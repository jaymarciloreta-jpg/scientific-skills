# Segmentation reference

Detail behind Step 2-4 of the skill. Read this when tuning thresholds, fighting
holes in the surface, or deciding how to handle sinuses.

## Thresholds and why the threshold is a sensitivity parameter

Air in the lumen is strongly negative HU against soft tissue, so a Threshold
effect isolates it cleanly. A practical air window is roughly -1024 to -300 HU.
There is no exact per-patient threshold; use an automated method (Otsu, isodata)
as a reproducible starting point, then tune.

The reason to treat the threshold as a swept input rather than a fixed constant:
the CT segmentation threshold strongly drives lumen cross-sectional area,
pressure drop, flow rate, and airway resistance, while flow distribution and
surface area are comparatively insensitive. Since the throat cross-section is
exactly the quantity a nasal-valve collapse model keys on, the threshold
propagates directly into the result. One nasal CFD study found a value near
-800 HU best matched rhinomanometry. Record the threshold with every surface and
sweep it as part of validation.

## Valve resolution: the thing that actually controls quality

The nasal valve is a slit, often only 1-3 voxels wide at native CT spacing.
Thresholding air that thin leaves holes and a ragged collapse plane, and the
throat cross-section becomes a discretization artifact. The fix that matters
most: before segmenting, resample the master volume to a fine isotropic spacing
(start ~0.3 mm) so the narrowest gap you care about is 4-5 voxels wide. In
Slicer this is done by resampling the master volume (ResampleScalarVolume or
Crop Volume), or by raising the segmentation's internal labelmap oversampling.
Oversampling by 2x raises memory ~8x, so crop to the region of interest first.

A 1 mm voxel pass is acceptable for scoping (orientation checks, rough volume,
domain layout) but must be regenerated finer for the production geometry.

## Imaging physics at the throat (the fragile part)

The throat is the most important feature and the most fragile to capture,
because several CT effects bite hardest exactly where the lumen is thinnest.
Inspect the valve region slice by slice and treat these deliberately:

- **Partial-volume averaging.** Where the airway is thin, each voxel is a blend
  of air and mucosa, so its HU sits between the two and the threshold alone
  decides whether it is air. This is precisely where threshold choice moves the
  minimum area the most. Finer isotropic voxels and the threshold sweep are the
  mitigations.
- **Mucus, secretions, crusting.** These have soft-tissue-like HU and get
  excluded from the air column, falsely narrowing or closing the valve. For a
  collapse limit, an accidental pre-closure makes the model non-conservative in
  confusing ways. Decide whether a closure is real anatomy or a mucus plug, and
  prefer a clean, decongested scan.
- **Beam-hardening and metal/streak artifact.** Dental work, packing, or dense
  bone near the piriform aperture throw local HU off right where you need it.
  Inspect that region specifically.
- **Leaks and bridges.** A too-permissive threshold lets air leak through thin
  bony walls into sinuses or the contralateral side, or bridge a near-contact at
  the valve, fusing structures that should be separate. Always keep only the
  connected airway component you intend and verify the valve is neither
  artificially fused nor split.

## Measuring the cross-section, and not destroying it

- **Use a centerline-perpendicular plane.** Throat area depends on the plane you
  slice it on. The valve is oblique, so a raw axial slice overstates the true
  minimum area. Measure cross-sections on planes locally perpendicular to the
  airway centerline.
- **Smoothing erodes the choke.** Aggressive surface smoothing rounds off and
  widens the narrowest slit, the opposite of what a choke-point model needs. Use
  minimal, controlled smoothing and re-measure the minimum cross-section before
  and after to quantify how much the smoothing changed it.
- **Left and right stay separate.** The flow split between the two valves is the
  governing configuration variable and the limit comes from the worse side, so
  do not let the two air columns merge or get smoothed together.

## Holes in the surface

Holes almost always mean the structure is under-resolved, not that the threshold
is wrong. In order of effectiveness: increase resolution (above); apply a small
median or morphological-closing smoothing in the Segment Editor; only then
hand-fill residual holes with Paint. Binary-labelmap thresholding loses
sub-voxel surface precision relative to a direct grayscale iso-surface, but
post-smoothing compensates; if maximum throat fidelity is needed, use a
fractional labelmap or keep oversampling high rather than smoothing hard.

## Keep the lumen, not the tissue

The exported STL is the air lumen (negative space) that the solver fills. Keep
the largest connected air component to drop speckle and the big exterior-air
blob, then confirm the surface is watertight before going further.

The structural lateral wall (membranous segment, cartilage frame) for an FE / FSI
tube law is a separate, harder segmentation because CT shows cartilage poorly.
Do it in the FE stage; it does not block the lumen STL.

## The sinus trap (most common cause of bad geometry)

Paranasal sinuses are frequently broadly connected to the nasal cavity, not
joined by thin ostia, so a 2 mm erosion will not split them off and automatic
pruning is unreliable. Consequences and options:

- A planar inlet/outlet cut through retained sinuses slices the wide cavities
  and inflates patch areas (observed: inlet ~6 cm2, outlet ~25 cm2 versus real
  naris ~1-1.6 cm2 and nasopharynx a few cm2).
- For a scoping run, keep the sinuses as dead-end cavities; through-flow is
  negligible, the only cost is mesh size.
- For the formal record and a true valve minimal cross-section, paint the
  sinuses out in Slicer and cut the oral cavity at the velopharynx, then
  re-export. All downstream steps then run cleanly.

If patch areas come out implausible, suspect attached sinuses before anything
else.

## Manual refinement in Slicer

After an automated first pass, refine in Segment Editor: Threshold to seed,
Islands to keep the airway, Scissors to cut flat inlet (nares) and outlet
(nasopharynx / plenum) planes, Paint / Erase to remove off-path sinus pockets.
Save the scene (.mrb) so the refinement is reproducible and auditable.

## The two scripts

- `segment_airway.py` (sandbox): scipy / skimage / trimesh, no Slicer needed.
  Auto-threshold, largest non-border component, marching cubes, Laplacian
  smooth. Flags: `--air-hu`, `--iso`, `--seed Z Y X`, `--keep-largest`. Best for
  an unattended first pass and for running where Slicer is not installed.
- `slicer_segment_airway.py` (Slicer-native): GUI-equivalent, reproducible,
  drops into manual refinement in the same scene. Flags: `--input`, `--out`,
  `--iso`, `--air-hu-min`, `--air-hu-max`, `--keep-largest`, `--median-mm`,
  `--closing-mm`, `--save-scene`. Run headless with
  `Slicer --no-main-window --python-script slicer_segment_airway.py -- ...`.
