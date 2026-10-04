#!/usr/bin/env python3
"""
Automated first-pass nasal AIR-LUMEN segmentation -> STL for the
CFD pharyvac suction project.  Exploratory first pass; expect manual
refinement of the domain (naris->nasopharynx, sinus removal, plenum seal).

Usage:
  python3 segment_airway.py INPUT [--out nasal_lumen.stl] [--air-hu -300]
                                  [--seed Z Y X] [--keep-largest] [--iso 0.3]

INPUT may be:
  - a NIfTI file (.nii / .nii.gz)
  - a directory of DICOM (.dcm) slices

Pipeline:
  1. Load volume + voxel spacing (mm).
  2. (optional) resample to isotropic.
  3. Threshold air (HU below --air-hu).
  4. Keep the nasal airway via connected components (largest, or seeded).
  5. Light morphological close + Gaussian smooth of the mask.
  6. Marching cubes -> triangle surface -> Laplacian smooth -> STL (mm).
Reports voxel size, air volume, and triangle count so geometry quality
can be judged before meshing.
"""
import argparse, os, sys
import numpy as np

def load_volume(path):
    if os.path.isdir(path):
        import pydicom
        files = [os.path.join(path, f) for f in os.listdir(path)
                 if f.lower().endswith(".dcm")]
        if not files:
            sys.exit("No .dcm files in directory.")
        sl = [pydicom.dcmread(f) for f in files]
        sl.sort(key=lambda d: float(getattr(d, "ImagePositionPatient", [0,0,0])[2]))
        vol = np.stack([s.pixel_array.astype(np.float32) for s in sl])
        slope = float(getattr(sl[0], "RescaleSlope", 1))
        inter = float(getattr(sl[0], "RescaleIntercept", 0))
        vol = vol*slope + inter   # -> Hounsfield units
        py, px = map(float, sl[0].PixelSpacing)
        dz = abs(float(sl[1].ImagePositionPatient[2]) - float(sl[0].ImagePositionPatient[2])) \
             if len(sl) > 1 else float(getattr(sl[0], "SliceThickness", 1))
        spacing = np.array([dz, py, px])   # mm, (z,y,x)
    else:
        import nibabel as nib
        img = nib.load(path)
        vol = np.asarray(img.dataobj).astype(np.float32)
        vol = np.transpose(vol, (2,1,0))   # -> (z,y,x)
        zoom = img.header.get_zooms()[:3]
        spacing = np.array([zoom[2], zoom[1], zoom[0]], dtype=float)
    return vol, spacing

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out", default="nasal_lumen.stl")
    ap.add_argument("--air-hu", type=float, default=-300.0,
                    help="voxels below this HU are air (default -300)")
    ap.add_argument("--seed", type=int, nargs=3, default=None,
                    metavar=("Z","Y","X"), help="seed voxel inside the nasal airway")
    ap.add_argument("--keep-largest", action="store_true",
                    help="keep largest air component (use if no seed)")
    ap.add_argument("--iso", type=float, default=None,
                    help="resample to this isotropic spacing in mm (e.g. 0.3)")
    a = ap.parse_args()

    from scipy import ndimage as ndi
    from skimage import measure
    import trimesh

    vol, spacing = load_volume(a.input)
    print(f"[load] volume {vol.shape}  spacing(z,y,x)={spacing} mm  "
          f"HU range [{vol.min():.0f},{vol.max():.0f}]")

    if a.iso:
        factors = spacing / a.iso
        vol = ndi.zoom(vol, factors, order=1)
        spacing = np.array([a.iso, a.iso, a.iso])
        print(f"[iso ] resampled to {vol.shape} at {a.iso} mm isotropic")

    air = vol < a.air_hu
    air = ndi.binary_opening(air, iterations=1)   # de-speckle
    print(f"[air ] {air.sum()} air voxels ({air.mean()*100:.1f}% of volume)")

    lbl, n = ndi.label(air)
    print(f"[cc  ] {n} air components")
    if a.seed:
        z,y,x = a.seed
        target = lbl[z,y,x]
        if target == 0:
            sys.exit(f"Seed {a.seed} is not in air; pick a voxel inside the airway.")
        mask = lbl == target
    else:
        # default: largest INTERIOR component (exclude the big exterior-air blob
        # by ignoring any component touching the volume border)
        border_ids = set(np.unique(np.concatenate([
            lbl[0].ravel(), lbl[-1].ravel(), lbl[:,0].ravel(), lbl[:,-1].ravel(),
            lbl[:,:,0].ravel(), lbl[:,:,-1].ravel()])))
        sizes = ndi.sum(np.ones_like(lbl), lbl, index=range(1, n+1))
        ranked = sorted(range(1, n+1), key=lambda i: sizes[i-1], reverse=True)
        pick = next((i for i in ranked if i not in border_ids), ranked[0]) \
               if not a.keep_largest else ranked[0]
        mask = lbl == pick
        print(f"[cc  ] kept component {pick} ({int(mask.sum())} voxels)"
              + ("" if a.keep_largest else "  [largest non-border]"))

    mask = ndi.binary_closing(mask, iterations=2)
    maskf = ndi.gaussian_filter(mask.astype(np.float32), sigma=0.6)

    verts, faces, normals, _ = measure.marching_cubes(maskf, level=0.5, spacing=tuple(spacing))
    mesh = trimesh.Trimesh(vertices=verts[:, ::-1], faces=faces)  # -> (x,y,z) mm
    trimesh.smoothing.filter_laplacian(mesh, iterations=8)
    mesh.remove_degenerate_faces(); mesh.remove_unreferenced_vertices()

    mesh.export(a.out)
    bb = mesh.bounds
    print(f"[mesh] {len(mesh.faces)} triangles, watertight={mesh.is_watertight}")
    print(f"[mesh] bbox mm: {np.round(bb[1]-bb[0],1)}")
    print(f"[out ] wrote {a.out}")
    print("Next: review slice overlays + 3D surface, trim to naris->nasopharynx, "
          "then mesh for CFD.")

if __name__ == "__main__":
    main()
