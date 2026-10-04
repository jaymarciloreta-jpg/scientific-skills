"""
create_sinus_roi.py — Slicer-native automation of the NINS protocol
"Create ROI" step: import a head CT, apply a volume-rendering preset, and
draft a "Sinus_ROI" markup box around the paranasal sinuses.

This file is meant to run INSIDE 3D Slicer's own Python environment - either
pasted into Slicer's Python Interactor, run via
`exec(open(path).read())` from that console, or sent as the `command` to a
running slicer-mcp-server's `execute_python` tool. It will not run in a
plain Python interpreter: it imports `slicer`, `vtk`, and `DICOMLib`, which
only exist inside a live Slicer session.

Typical use:

    exec(open('/absolute/path/to/create_sinus_roi.py').read())
    main(dicom_dir='/absolute/path/to/dicom_folder')

Or, if a CT is already loaded in the scene:

    exec(open('/absolute/path/to/create_sinus_roi.py').read())
    main()

See the accompanying SKILL.md for the reasoning behind each step and for
what to do when the automatic sinus-region guess picks the wrong air
pocket (pass `sinus_bounds_ras` to override it).
"""

import slicer
import vtk


def _ensure_scipy():
    """scipy isn't always present in Slicer's bundled Python; install it
    into Slicer's environment (not system Python) if missing."""
    try:
        import scipy  # noqa: F401
    except ImportError:
        slicer.util.pip_install("scipy")


def import_dicom_directory(dicom_dir):
    """Import every DICOM series found under dicom_dir and load them all as
    scalar volumes, the scripted equivalent of File -> Add Data -> choose
    directory. Returns the list of loaded volume node IDs."""
    from DICOMLib import DICOMUtils

    loaded_node_ids = []
    with DICOMUtils.TemporaryDICOMDatabase() as db:
        DICOMUtils.importDicom(dicom_dir, db)
        for patient_uid in db.patients():
            loaded_node_ids.extend(DICOMUtils.loadPatientByUID(patient_uid))
    return loaded_node_ids


def pick_best_ct_volume(volume_node_name=None):
    """Pick the scalar volume most likely to be the primary axial
    acquisition rather than a scanner-generated derived/reformatted series.

    If volume_node_name is given, that exact node is used instead of the
    heuristic - use this when the auto-pick grabs the wrong series.
    """
    if volume_node_name:
        node = slicer.util.getNode(volume_node_name)
        return node

    candidates = list(slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode"))
    if not candidates:
        raise RuntimeError(
            "No scalar volumes are loaded. Pass dicom_dir=... to import a "
            "series first, or load one in Slicer before calling main()."
        )

    # Prefer series whose auto-generated name doesn't flag them as a
    # scanner-derived reformat (seen in practice as "... DERIVED-PRIMARY-
    # AXIAL..." in the node name); among the rest, the original acquisition
    # is usually the one with the most slices.
    non_derived = [n for n in candidates if "DERIVED" not in n.GetName().upper()]
    pool = non_derived if non_derived else candidates

    def slice_count(node):
        image_data = node.GetImageData()
        return image_data.GetDimensions()[2] if image_data else 0

    pool.sort(key=slice_count, reverse=True)
    return pool[0]


def apply_volume_rendering(volume_node, preset_name="CT-Chest-Contrast-Enhanced"):
    """Turn on volume rendering for volume_node and copy in a named preset.
    Returns the display node."""
    vr_logic = slicer.modules.volumerendering.logic()
    display_node = vr_logic.CreateDefaultVolumeRenderingNodes(volume_node)
    display_node.SetVisibility(True)

    preset_node = vr_logic.GetPresetByName(preset_name)
    if preset_node:
        display_node.GetVolumePropertyNode().Copy(preset_node)
    else:
        print(
            f"[create_sinus_roi] Preset '{preset_name}' not found - leaving "
            f"the default preset in place. Check the exact name in the "
            f"Volume Rendering module's Preset dropdown."
        )
    return display_node


def compute_sinus_roi_bounds(
    volume_node,
    air_hi=-300,
    min_component_voxels=30,
    n_sinus_components=8,
    margin_mm=8,
):
    """Heuristic paranasal-sinus bounding box, in RAS mm, as
    (center_ras, half_size_mm).

    Method: threshold air-range voxels, label connected components, drop any
    touching the volume border (external/room air), assume the single
    largest remaining internal air component is the main nasal/
    nasopharyngeal airway, and take the bounding box of the next-largest
    handful of components as the draft sinus region. This is a first-draft
    bounding box, not a segmentation - always confirm it visually in Slicer
    afterward (see SKILL.md).
    """
    _ensure_scipy()
    import numpy as np
    from scipy import ndimage

    # arrayFromVolume returns axes in (k, j, i) order = (slice, row, col).
    arr = slicer.util.arrayFromVolume(volume_node)
    air_mask = arr < air_hi

    labeled, n_labels = ndimage.label(air_mask)
    if n_labels == 0:
        raise RuntimeError(
            "No air-range voxels found in this volume - is it a head CT, "
            "and are the HU values intact (not rescaled/clipped)?"
        )

    border_mask = np.zeros_like(air_mask)
    border_mask[0, :, :] = border_mask[-1, :, :] = True
    border_mask[:, 0, :] = border_mask[:, -1, :] = True
    border_mask[:, :, 0] = border_mask[:, :, -1] = True
    border_labels = set(np.unique(labeled[border_mask])) - {0}

    sizes = ndimage.sum(np.ones_like(labeled), labeled, index=range(1, n_labels + 1))
    candidates = [
        (label, sizes[label - 1])
        for label in range(1, n_labels + 1)
        if label not in border_labels and sizes[label - 1] >= min_component_voxels
    ]
    candidates.sort(key=lambda pair: -pair[1])

    if not candidates:
        raise RuntimeError(
            "No internal air-filled components survived filtering. Try "
            "lowering min_component_voxels, or check this is a head CT with "
            "the nasal passages and sinuses in the field of view."
        )

    # Drop the single biggest component (assumed = main airway) if there's
    # more than one candidate; otherwise fall back to using it anyway rather
    # than returning nothing.
    sinus_labels = [label for label, _ in candidates[1 : 1 + n_sinus_components]]
    if not sinus_labels:
        sinus_labels = [candidates[0][0]]

    sinus_mask = np.isin(labeled, sinus_labels)
    kji_coords = np.argwhere(sinus_mask)
    if kji_coords.size == 0:
        raise RuntimeError("Sinus component selection produced an empty mask.")

    k_min, j_min, i_min = kji_coords.min(axis=0)
    k_max, j_max, i_max = kji_coords.max(axis=0)

    ijk_to_ras = vtk.vtkMatrix4x4()
    volume_node.GetIJKToRASMatrix(ijk_to_ras)

    corners_ras = []
    for i in (i_min, i_max):
        for j in (j_min, j_max):
            for k in (k_min, k_max):
                ras = ijk_to_ras.MultiplyPoint((float(i), float(j), float(k), 1.0))
                corners_ras.append(ras[:3])
    corners_ras = np.array(corners_ras)

    ras_min = corners_ras.min(axis=0) - margin_mm
    ras_max = corners_ras.max(axis=0) + margin_mm
    center = (ras_min + ras_max) / 2.0
    half_size = (ras_max - ras_min) / 2.0
    return tuple(center), tuple(half_size)


def create_or_update_roi(center, half_size, name="Sinus_ROI"):
    """Create (or move, if it already exists) a Markups ROI node at the
    given RAS center with the given RAS half-size. Returns the ROI node."""
    existing = slicer.mrmlScene.GetFirstNodeByName(name)
    roi_node = existing if existing and existing.IsA("vtkMRMLMarkupsROINode") else None
    if roi_node is None:
        roi_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode")
        roi_node.SetName(name)

    roi_node.SetXYZ(*center)
    roi_node.SetRadiusXYZ(*half_size)
    return roi_node


def attach_roi_to_cropping(display_node, roi_node):
    """Wire the ROI into the volume-rendering display node's crop box, same
    end state as ticking "Crop: Enable" with that ROI selected in the GUI."""
    display_node.SetAndObserveROINodeID(roi_node.GetID())
    display_node.SetCroppingEnabled(True)


def main(
    dicom_dir=None,
    volume_node_name=None,
    preset_name="CT-Chest-Contrast-Enhanced",
    roi_name="Sinus_ROI",
    margin_mm=8,
    sinus_bounds_ras=None,
):
    """Run the full pipeline: optional DICOM import, series pick, volume
    rendering, draft sinus ROI, crop wiring.

    sinus_bounds_ras: optional manual override, a 6-tuple
        (r_min, r_max, a_min, a_max, s_min, s_max) in RAS mm. Pass this to
        skip the automatic air-threshold heuristic entirely, e.g. once
        you've read off good numbers from a first run's confirmed ROI.
    """
    if dicom_dir:
        import_dicom_directory(dicom_dir)

    volume_node = pick_best_ct_volume(volume_node_name=volume_node_name)
    print(f"[create_sinus_roi] Using volume: {volume_node.GetName()}")

    display_node = apply_volume_rendering(volume_node, preset_name=preset_name)

    if sinus_bounds_ras:
        r_min, r_max, a_min, a_max, s_min, s_max = sinus_bounds_ras
        center = ((r_min + r_max) / 2, (a_min + a_max) / 2, (s_min + s_max) / 2)
        half_size = ((r_max - r_min) / 2, (a_max - a_min) / 2, (s_max - s_min) / 2)
    else:
        center, half_size = compute_sinus_roi_bounds(volume_node, margin_mm=margin_mm)

    roi_node = create_or_update_roi(center, half_size, name=roi_name)
    attach_roi_to_cropping(display_node, roi_node)

    print(
        f"[create_sinus_roi] '{roi_name}' drafted at center={center}, "
        f"half_size={half_size} (RAS mm). Confirm it captures the paranasal "
        f"sinuses in the slice views / 3D view, and nudge its handles if not."
    )
    return volume_node, display_node, roi_node


if __name__ == "__main__":
    # Convenience for pasting the whole file at once and running with
    # defaults against whatever's already loaded in the scene.
    main()
