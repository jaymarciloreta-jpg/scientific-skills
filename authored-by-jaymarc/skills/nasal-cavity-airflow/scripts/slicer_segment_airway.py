#!/usr/bin/env python-real
"""
slicer_segment_airway.py - rerun-ready nasal AIR-LUMEN segmentation in 3D Slicer.

This is the Slicer-native counterpart to the sandbox script segment_airway.py.
It uses Slicer's own modules (ResampleScalarVolume CLI, Segment Editor effects,
Segmentations export) so the result matches what you would get clicking through
the GUI, and so the whole chain is reproducible from one command for the
V&V 40 record.

Pipeline (cheap and conservative first, fidelity where it matters):
  1. Load the CT volume (NIfTI or a DICOM directory).
  2. Resample to a fine ISOTROPIC spacing. The nasal valve is a slit only 1-3
     voxels wide at native CT spacing; thresholding such thin air leaves holes
     and a ragged collapse plane. Oversampling so the valve is ~4-5 voxels wide
     is what makes the throat cross-section A(P_tm) a real measurement rather
     than a discretization artifact.
  3. Threshold air with the Segment Editor Threshold effect.
  4. Keep the largest island (the connected nasal airway), dropping speckle and
     disconnected exterior-air blobs.
  5. Smooth (median + closing) to remove voxel staircase without eroding the
     throat.
  6. Export a watertight STL of the air lumen in mm (RAS), ready for patch
     extraction and meshing.

WHY a separate script from segment_airway.py: the sandbox version (scipy /
skimage / trimesh) is great for an unattended first pass with no Slicer running.
This version is for when you want Slicer's surface nets / smoothing and an
auditable, GUI-equivalent result, or you want to drop straight into manual
refinement (painting out sinuses, cutting the velopharynx) in the same scene.

USAGE
  Headless (recommended for reruns):
    Slicer --no-splash --no-main-window --python-script slicer_segment_airway.py -- \
        --input  /path/to/ct.nii.gz \
        --out    /path/to/nasal_lumen.stl \
        --iso    0.3 \
        --air-hu-min -1024 --air-hu-max -300 \
        --keep-largest

  Interactive (paste into the Slicer Python console, edit ARGS first):
    Set RUN_INLINE_ARGS below, then exec(open('slicer_segment_airway.py').read())

NOTES
  - Air threshold default [-1024, -300] HU is a starting point, not gospel.
    The CT segmentation threshold strongly drives lumen cross-sectional area,
    pressure drop, and resistance (less so flow split), so treat it as a
    sensitivity parameter in validation, not a fixed constant. A value near
    -800 HU has been reported to best match rhinomanometry; sweep it.
  - This produces the FLUID domain (air lumen). The structural lateral wall is
    a separate segmentation handled in the FE stage (CT shows cartilage poorly).
  - After export, run extract_openfoam_patches.py to split wall/inlet/outlet,
    and confirm the inlet area is anatomically sane (a naris is ~1-1.6 cm2).
    Inflated patch areas usually mean sinuses are still attached and a planar
    cut is slicing through them; paint them out first.
"""

import os
import sys

# Inline args for console use; ignored when run with "-- ..." on the CLI.
RUN_INLINE_ARGS = None
# Example:
# RUN_INLINE_ARGS = ["--input", "geometry/ct_raw/ct.nii.gz",
#                    "--out", "geometry/nasal_lumen.stl", "--iso", "0.3"]


def parse_args(argv):
    import argparse
    ap = argparse.ArgumentParser(description="Slicer nasal air-lumen segmentation")
    ap.add_argument("--input", required=True,
                    help="CT volume: NIfTI file or a DICOM directory")
    ap.add_argument("--out", default="nasal_lumen.stl",
                    help="output STL path (mm, RAS)")
    ap.add_argument("--iso", type=float, default=0.3,
                    help="isotropic resample spacing in mm (default 0.3; use "
                         "<= native to oversample the valve)")
    ap.add_argument("--air-hu-min", type=float, default=-1024.0,
                    help="lower air threshold in HU (default -1024)")
    ap.add_argument("--air-hu-max", type=float, default=-300.0,
                    help="upper air threshold in HU (default -300; sweep this)")
    ap.add_argument("--keep-largest", action="store_true",
                    help="keep only the largest island (the nasal airway)")
    ap.add_argument("--median-mm", type=float, default=0.0,
                    help="median smoothing kernel in mm (0 disables)")
    ap.add_argument("--closing-mm", type=float, default=0.0,
                    help="morphological closing kernel in mm (0 disables)")
    ap.add_argument("--save-scene", default=None,
                    help="optional .mrb path to save the full Slicer scene for audit")
    return ap.parse_args(argv)


def log(msg):
    print("[slicer-seg] " + msg)
    try:
        import slicer
        slicer.app.processEvents()
    except Exception:
        pass


def load_ct(path):
    import slicer
    if os.path.isdir(path):
        # DICOM directory: import into the temporary DICOM database, load series.
        from DICOMLib import DICOMUtils
        loaded = []
        with DICOMUtils.TemporaryDICOMDatabase() as db:
            DICOMUtils.importDicom(path, db)
            for patientUID in db.patients():
                loaded += DICOMUtils.loadPatientByUID(patientUID)
        if not loaded:
            raise RuntimeError("No DICOM series loaded from " + path)
        volumeNode = slicer.util.getNode(loaded[0])
    else:
        volumeNode = slicer.util.loadVolume(path)
    return volumeNode


def resample_isotropic(volumeNode, iso_mm):
    """Resample to isotropic spacing using the ResampleScalarVolume CLI.

    Deterministic and GUI-equivalent, which is what we want for reproducibility.
    """
    import slicer
    outNode = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLScalarVolumeNode", volumeNode.GetName() + "_iso")
    params = {
        "InputVolume": volumeNode.GetID(),
        "OutputVolume": outNode.GetID(),
        "outputPixelSpacing": "%g,%g,%g" % (iso_mm, iso_mm, iso_mm),
        "interpolationType": "linear",
    }
    cliNode = slicer.cli.runSync(
        slicer.modules.resamplescalarvolume, None, params)
    if cliNode.GetStatusString() != "Completed":
        raise RuntimeError("ResampleScalarVolume failed: "
                           + cliNode.GetStatusString())
    slicer.mrmlScene.RemoveNode(cliNode)
    return outNode


def segment_air(volumeNode, args):
    import slicer
    import vtkSegmentationCorePython as vtkSegmentationCore  # noqa: F401

    segNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segNode.CreateDefaultDisplayNodes()
    segNode.SetReferenceImageGeometryParameterFromVolumeNode(volumeNode)
    segId = segNode.GetSegmentation().AddEmptySegment("airway")

    editor = slicer.qMRMLSegmentEditorWidget()
    editor.setMRMLScene(slicer.mrmlScene)
    editorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    editor.setMRMLSegmentEditorNode(editorNode)
    editor.setSegmentationNode(segNode)
    editor.setSourceVolumeNode(volumeNode)
    editor.setCurrentSegmentID(segId)

    # 1) Threshold air.
    editor.setActiveEffectByName("Threshold")
    eff = editor.activeEffect()
    eff.setParameter("MinimumThreshold", str(args.air_hu_min))
    eff.setParameter("MaximumThreshold", str(args.air_hu_max))
    eff.self().onApply()
    log("threshold applied [%g, %g] HU" % (args.air_hu_min, args.air_hu_max))

    # 2) Keep largest island (the connected nasal airway).
    if args.keep_largest:
        editor.setActiveEffectByName("Islands")
        eff = editor.activeEffect()
        eff.setParameter("Operation", "KEEP_LARGEST_ISLAND")
        eff.self().onApply()
        log("kept largest island")

    # 3) Smoothing - median then closing, both optional.
    if args.median_mm > 0:
        editor.setActiveEffectByName("Smoothing")
        eff = editor.activeEffect()
        eff.setParameter("SmoothingMethod", "MEDIAN")
        eff.setParameter("KernelSizeMm", str(args.median_mm))
        eff.self().onApply()
        log("median smoothing %g mm" % args.median_mm)
    if args.closing_mm > 0:
        editor.setActiveEffectByName("Smoothing")
        eff = editor.activeEffect()
        eff.setParameter("SmoothingMethod", "MORPHOLOGICAL_CLOSING")
        eff.setParameter("KernelSizeMm", str(args.closing_mm))
        eff.self().onApply()
        log("morphological closing %g mm" % args.closing_mm)

    # Clean up the transient editor node.
    slicer.mrmlScene.RemoveNode(editorNode)
    return segNode, segId


def export_stl(segNode, out_path):
    import slicer
    segNode.CreateClosedSurfaceRepresentation()
    folder = os.path.dirname(os.path.abspath(out_path)) or "."
    if not os.path.isdir(folder):
        os.makedirs(folder)
    # Export segments to model nodes, then save the model as STL.
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    exportFolderItemId = shNode.CreateFolderItem(
        shNode.GetSceneItemID(), "ExportModels")
    slicer.modules.segmentations.logic().ExportAllSegmentsToModels(
        segNode, exportFolderItemId)
    modelNodes = vtk_collection_to_list(shNode, exportFolderItemId)
    if not modelNodes:
        raise RuntimeError("No model produced from segmentation")
    slicer.util.saveNode(modelNodes[0], out_path)
    log("wrote STL " + out_path)


def vtk_collection_to_list(shNode, folderItemId):
    import vtk
    coll = vtk.vtkCollection()
    shNode.GetDataNodesInBranch(folderItemId, coll)
    return [coll.GetItemAsObject(i) for i in range(coll.GetNumberOfItems())]


def report(segNode, segId, volumeNode):
    import slicer
    try:
        import SegmentStatistics
        segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
        pn = segStatLogic.getParameterNode()
        pn.SetParameter("Segmentation", segNode.GetID())
        segStatLogic.computeStatistics()
        stats = segStatLogic.getStatistics()
        vol_cm3 = stats[segId, "LabelmapSegmentStatisticsPlugin.volume_cm3"]
        log("air-lumen volume = %.2f cm3" % vol_cm3)
    except Exception as exc:
        log("volume stat skipped: %s" % exc)


def main():
    import slicer  # noqa: F401
    if RUN_INLINE_ARGS is not None:
        argv = RUN_INLINE_ARGS
    else:
        # Slicer passes script args after the literal "--".
        argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    args = parse_args(argv)

    log("loading " + args.input)
    ct = load_ct(args.input)
    sp = ct.GetSpacing()
    log("native spacing (mm) = %.3f, %.3f, %.3f" % (sp[0], sp[1], sp[2]))

    work = ct
    if args.iso and args.iso > 0:
        work = resample_isotropic(ct, args.iso)
        log("resampled to %g mm isotropic" % args.iso)

    segNode, segId = segment_air(work, args)
    report(segNode, segId, work)
    export_stl(segNode, args.out)

    if args.save_scene:
        slicer.util.saveScene(args.save_scene)
        log("saved scene " + args.save_scene)

    log("done. Next: extract_openfoam_patches.py, then mesh. "
        "Sanity-check inlet area (~1-1.6 cm2 per naris).")


if __name__ == "__main__":
    main()
