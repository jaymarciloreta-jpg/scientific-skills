---
name: nasal-cavity-airflow
description: >
  Turn a patient head CT into a watertight nasal air-lumen geometry and a
  CFD-ready mesh for nasal airflow simulation. Use for any nasal-airflow geometry
  step: segmenting the nasal airway or valve from CT, cleaning a sinonasal STL,
  making it watertight, sealing nares to nasopharynx, removing off-path sinuses,
  splitting the lumen into OpenFOAM inlet/outlet/wall patches, diagnosing
  implausible patch areas, setting the area-weighted inlet flow split, or meshing
  the airway (snappyHexMesh, gmsh, cfMesh) with valve-throat refinement. Triggers
  on things like "segment the nasal airway", "make the airway STL watertight",
  "my inlet patch area is way too big", "extract OpenFOAM patches from this nasal
  mesh", or "mesh the nasal cavity for CFD", even if the tool is not named. Do NOT
  use for: structural FE / tube-law segmentation of the lateral wall; solver
  physics (turbulence model, BC values, divergence); V&V 40 or validation against
  measured data; or non-nasal anatomy (lung airway, liver).
---

# Nasal cavity airflow: CT to CFD-ready geometry

This skill encodes a working, reproducible pipeline for getting from a patient
head CT to a meshable nasal air lumen and an OpenFOAM-ready, patched, watertight
surface. It is built for nasal-airflow and nasal-valve collapse studies where
the throat cross-section drives the answer, so fidelity at the valve and an
honest, auditable chain matter more than speed.

The prime goal: a watertight air-lumen STL, sealed naris to nasopharynx, split
into clean inlet / outlet / wall patches with anatomically sane areas, meshed
finely enough at the valve that the throat cross-section is converged. If a step
is not moving toward that, stop and say so.

## The pipeline at a glance

```
CT (DICOM)
  -> de-identify (dcm2niix -> NIfTI)            # PHI never enters the project
  -> segment air lumen                          # Slicer or sandbox script
  -> clean to a single watertight lumen         # largest air island, re-surface
  -> trim + seal: nares inlet, nasopharynx outlet, remove off-path sinuses
  -> extract patches: wall / inletLeft / inletRight / outlet  (+ area report)
  -> mesh (snappyHexMesh / gmsh) with valve-throat refinement + BL prisms
  -> hand to the CFD case  (solver setup is out of scope for this skill)
```

Each step has a "good enough to proceed" check. Do not advance on a domain that
is not watertight or whose patch areas are anatomically implausible; every
downstream step inherits the error.

## Coordinate frame (assume RAS mm unless told otherwise)

For this project's geometry the frame is: `x` = left-right, `y` =
anterior-posterior with **low y = anterior (nares)** and **high y = posterior
(choanae / nasopharynx)**, `z` = superior-inferior with high z superior. Inlet
flow is +y (anterior to posterior). Left-vs-right cannot be read from geometry
alone without a fiducial, and it does not change the limit because the worse
side governs. Confirm the frame on any new scan before trusting the patch
classifier, which keys off `y` position and face normals.

## Step 1 - De-identify (do this first, always)

CT DICOM headers carry patient identifiers. Convert to NIfTI with `dcm2niix`,
which drops nearly all PHI and yields one small file, before the data leaves the
clinical system. If DICOM must be handed over, anonymize it first (Slicer has a
built-in anonymizer). Never place identifiable data in the project folder.

## Step 2 - Segment the air lumen

Two paths, same output (an STL of the nasal air lumen). Pick by how much manual
control is needed.

- **Sandbox / unattended** (no Slicer running): `scripts/segment_airway.py`
  loads NIfTI or DICOM, optionally resamples isotropic, thresholds air, keeps
  the largest non-border air component, light close + Gaussian, marching cubes,
  Laplacian smooth, writes STL. Best for a fast first pass.
- **Slicer-native / auditable**: `scripts/slicer_segment_airway.py` does the
  same chain with Slicer's own modules (ResampleScalarVolume CLI, Segment
  Editor Threshold / Islands / Smoothing, Segmentations export). Use it when you
  want a GUI-equivalent, reproducible result, or you want to drop into manual
  refinement in the same scene.

The single most important parameter is **resolution at the valve**, not the
threshold. The valve is a slit often only 1-3 voxels wide at native CT spacing;
resample to a fine isotropic spacing (start ~0.3 mm) so it is 4-5 voxels wide,
or the throat cross-section `A` is a discretization artifact. A 1 mm voxel pass
is fine for scoping but must be regenerated finer for the production geometry.

At the throat, the imaging physics fights you: partial-volume averaging blurs
the slit, mucus and secretions read as soft tissue and can falsely close the
lumen, and beam-hardening near bone and dental work corrupts local HU. These
make the throat both the most important and the most fragile feature, so inspect
it directly and measure the cross-section on a plane locally perpendicular to the
airway centerline, not on a raw axial slice (an oblique valve overstates the
area on axial). `references/segmentation.md` has the full list.

Read `references/segmentation.md` before tuning thresholds or chasing holes.

## Step 3 - Clean to one watertight lumen

The STL the solver fills is the **air lumen** (the negative space), not tissue.
Keep the largest connected air component to drop speckle and exterior-air blobs,
re-surface, and confirm `is_watertight`. A non-watertight lumen is not ready to
patch or mesh.

The **structural wall** for any FE / FSI tube law is a separate, harder
segmentation (CT shows cartilage poorly) and is handled in the FE stage. It does
not block the lumen STL.

## Step 4 - Trim and seal, and the sinus trap

Trim to naris-to-nasopharynx and seal the outlet plenum. The recurring trap in
sinonasal geometry: the paranasal sinuses are often broadly connected to the
cavity (not joined by thin ostia), so morphological erosion will not cleanly
split them. Two honest options:

- **Keep the sinuses** as dead-end cavities (negligible through-flow, only a
  mesh-size cost) for a scoping run.
- **Paint them out in Slicer** and cut the oral cavity at the velopharynx for
  the formal record and for a clean valve minimal cross-section.

This matters because a planar inlet/outlet cut through retained sinuses inflates
patch areas badly (seen: inlet ~6 cm2, outlet ~25 cm2 versus real naris
~1-1.6 cm2 and nasopharynx a few cm2). If patch areas come out implausible,
the sinuses are almost certainly still attached. Sinus removal is on the
critical path for clean patches and a real valve cross-section, not optional.

When areas look wrong, rule out two cheaper causes in the same pass before
re-segmenting. First, **units**: STL carries no unit, and OpenFOAM assumes
meters, so a millimeter STL read as meters inflates every area by 1e6 and every
length by 1e3. Check the surface bounding box reads as ~0.05-0.07 m head-scale
in meters, not tens of meters; if it does not, scale by 0.001 (see
`references/meshing-export.md`). A true units error scales all patches by the
same factor, so a uniform 1e6 blow-up points at units while a per-patch mismatch
(inlet 4x, outlet 10x) points at retained anatomy. Second, the **coordinate
frame**: the classifier keys off the `y` axis and face normals, so a scan in a
different orientation grabs the wrong faces even on clean geometry.

## Step 5 - Extract OpenFOAM patches

Run `scripts/extract_openfoam_patches.py <sealed.stl> <out_dir>`. It requires a
watertight input, classifies faces into `wall`, `inletLeft`, `inletRight`,
`outlet` by `y` position and normal direction, writes one STL per patch, and
emits `patch_report.json` with per-patch areas in cm2 and the lumen volume.

Acceptance check: inlet areas near 1-1.6 cm2 per naris, outlet a few cm2. If
not, go back to Step 4. The area report also feeds the area-weighted inlet flow
split in the CFD boundary conditions.

Read `references/meshing-export.md` for patch tolerances and the meshing setup.

## Step 6 - Mesh for CFD

Hand the patched surfaces to volume meshing. The reference setup uses OpenFOAM
`snappyHexMesh` (blockMesh background, snap, then `checkMesh`) run in Docker. The
mechanics that trip people: scale the surface to **meters** first (STL is
millimeters, OpenFOAM assumes meters), run `surfaceFeatures` to capture the
cap-to-wall feature edges so snap does not round them off, set `locationInMesh`
to a point you know is **inside the lumen**, and grow inflation layers on the
**wall only**, not on inlet or outlet. Resolve a boundary layer along the mucosa
at the valve, because the choke / flow criterion depends on the velocity at the
collapse plane, and refine the throat until the collapse-plane cross-section and
the derived critical flow stop changing. Mesh independence is demonstrated on the
throat cross-section and the critical flow, not on a global residual. See
`references/meshing-export.md`.

After `checkMesh` passes, the geometry stage is complete and the case is ready
for solver setup, which is outside this skill.

## Provenance (carry this on every artifact)

Tag every output with the geometry version, the source CT and its decongestion
state, the isotropic spacing, the air threshold used, and the date. A surface or
area with no recorded threshold and spacing cannot enter a credibility record,
because both materially change the result.

## Reference files

- `references/segmentation.md` - thresholds and the threshold-sensitivity
  caveat, valve resolution, hole-filling, sinus handling, the two script paths,
  and manual refinement in Slicer.
- `references/meshing-export.md` - patch classification tolerances, watertight
  repair, snappyHexMesh / gmsh setup, boundary layers, and the throat mesh-
  independence check.

## Scripts

- `scripts/slicer_segment_airway.py` - Slicer-native resample -> threshold ->
  islands -> smooth -> STL.
- `scripts/segment_airway.py` - sandbox (scipy/skimage/trimesh) first-pass
  segmentation, no Slicer needed.
- `scripts/extract_openfoam_patches.py` - split a sealed watertight STL into
  OpenFOAM patches with an area report.
