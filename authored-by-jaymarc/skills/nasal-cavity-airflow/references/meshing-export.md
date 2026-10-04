# Meshing and export reference

Detail behind Step 5-6 of the skill. Read this when extracting patches or
setting up the volume mesh.

## Patch extraction

`extract_openfoam_patches.py <sealed.stl> <out_dir>` requires a watertight
input and classifies each face into `wall`, `inletLeft`, `inletRight`, `outlet`
using `y` position and face-normal direction:

- `inlet` = faces near `y_min` (anterior nares) with normal pointing -y.
- `outlet` = faces near `y_max` (posterior nasopharynx / plenum) with normal +y.
- left / right inlet split at the median `x` (or a supplied `--x-mid`).
- everything else is `wall`.

Tolerances: `--y-tol` (mm band around the inlet/outlet plane, default 2.0) and
`--n-tol` (normal-alignment cutoff, default 0.7). It writes one STL per patch
plus `patch_report.json` with per-patch areas in cm2, lumen volume in cm3, the
bounding box, and the y / x split values used.

This classifier assumes flat, cleanly cut inlet and outlet planes. If the cut is
oblique or the sinuses are attached, the bands will grab the wrong faces. Sanity
check against anatomy: a naris is ~1-1.6 cm2, the nasopharynx a few cm2. Bad
areas mean go back to trimming and sealing.

## Watertight repair

If the lumen is not watertight, do not patch it. Common fixes: re-run the
segmentation cleanup keeping the largest island and re-surfacing; fill holes
with the Hollow / Wrap Solidify tools in Slicer; or, as a last resort, a mesh
repair pass (fill small holes, remove degenerate faces, remove unreferenced
vertices). Re-confirm `is_watertight` after any repair.

## Inlet flow split

The CFD boundary condition uses an area-weighted split of the total flow across
inletLeft and inletRight, taken from the patch areas in `patch_report.json`.
Reference BC file shape:

```json
{
  "totalFlowRateLpm": 15.0,
  "inletLeftAreaMm2":  121.2,
  "inletRightAreaMm2":   5.9,
  "outletAreaMm2":      33.1
}
```

The left/right asymmetry is physiologically real and is a governing
configuration variable for collapse studies; report symmetric and asymmetric
splits and take the limit from the worse side.

## Units: scale to meters once, early

STL files carry no unit, and OpenFOAM solves in SI (meters), while segmentation
exports in millimeters. So OpenFOAM reads a 1 mm geometry as 1 m unless told
otherwise, inflating every length by 1000 and every area by 1e6, which wrecks
Reynolds number, wall shear, and every boundary-layer quantity. This is also a
prime suspect when patch areas look absurd: a units error scales all patches by
the same factor (a uniform 1e6 blow-up), whereas retained sinuses inflate
patches unevenly.

Confirm with the surface bounding box: a head-scale airway should read about
0.05 to 0.07 m tall in meters, not tens of meters. Scale once, before meshing,
and keep the whole case in meters:

```bash
surfaceTransformPoints -scale 0.001 in_mm.stl constant/triSurface/out_m.stl
# older syntax: surfaceTransformPoints -scale '(0.001 0.001 0.001)' in.stl out.stl
```

If you already meshed, `transformPoints -scale 0.001` scales the mesh. Do not
mix conventions; scale the surface and any background block consistently.

## Volume meshing (OpenFOAM snappyHexMesh, reference path)

Reference setup meshes in OpenFOAM via Docker:

```
new-case.sh   <name> <surfaces_dir> <bc.json>   # assemble case from template
run-mesh.sh   cases/<name>                       # blockMesh -> snappyHexMesh -> checkMesh
run-solve.sh  cases/<name>
postprocess.sh cases/<name>
```

`run-mesh.sh` runs a background `blockMesh`, then `snappyHexMesh -overwrite`,
then `checkMesh`. The case template carries `system/snappyHexMeshDict`,
`blockMeshDict`, `fvSchemes`, `fvSolution`, `controlDict`, and a RANS k-omega
field set (`0/U`, `k`, `omega`, `nut`, `p`) with `transportProperties` and
`turbulenceProperties`.

### snappyHexMesh mechanics that actually bite

- **Feature edges.** Run `surfaceFeatures` (older: `surfaceFeatureExtract`)
  against the surface so snap captures the cap-to-wall rims at the nares and
  outlet instead of rounding them off. Without this the inlet and outlet edges
  smear.
- **`locationInMesh`.** In `castellatedMeshControls`, set this to a point you
  know is inside the air lumen (for example mid nasal cavity). A point outside
  the lumen meshes the wrong region and is the most common cause of an empty or
  inverted mesh.
- **Patch naming.** Register the surfaces under `geometry` and give each a
  `patchInfo` in `refinementSurfaces` so `wall` comes out type `wall` and the
  inlet and outlet come out type `patch`.
- **Layers on the wall only.** Turn on `addLayers` for the `wall` region, not for
  inlet or outlet, and size the first cell to your target y+ for the regime.
- **Refinement region at the throat.** Add a `refinementRegions` box around the
  valve, since that is where the answer lives.

### Patch surface format options

The reference `extract_openfoam_patches.py` writes one STL per patch. snappy can
also read a single multi-solid named STL, where each `solid <name> ...
endsolid <name>` block becomes a named region you reference in
`snappyHexMeshDict`. Either works; per-file is simpler to inspect, multi-solid is
the more common snappy idiom.

Alternative mesher: gmsh from the patched surfaces, or cfMesh, if a body-fitted
prism layer is preferred over snappyHexMesh's added layers.

## Boundary layers and throat refinement

Resolve a boundary layer along the mucosa, especially at the valve throat,
because the choke / flow-limitation criterion depends on the velocity at the
collapse plane and on `u/c` there. Add a refinement region around the throat.

## Mesh independence (the check that counts)

Demonstrate convergence on the two quantities that feed the safety limit: the
collapse-plane lumen cross-section `A(P_tm)` and the resulting critical flow,
not a global residual. Refine until both change by less than the validation
tolerance and record the series. Note whether the most compliant material corner
needs its own near-apposition refinement. Cite the mesh version tag from every
case that uses it.
