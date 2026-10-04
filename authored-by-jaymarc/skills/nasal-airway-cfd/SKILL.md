---
name: nasal-airway-cfd
description: >-
  Build a CFD-ready nasal airway flow domain from a head/sinus CT. Use this
  whenever the user wants to segment the nasal cavity / nasopharynx airway from
  DICOM or NRRD scans, screen a cohort of CT scans for a usable subject, turn a
  CT into an airway STL for CFD/CFX/Fluent/OpenFOAM, extract a sinonasal flow
  domain, or define nostril inlets and a nasopharyngeal outlet. Triggers on
  "nasal airway", "sinonasal segmentation", "airway STL from CT", "nasal CFD
  geometry", "segment the nose for CFD", "nasopharynx outlet", "pick a scan from
  this DICOM folder", or any mention of turning sinus/head CT data into a
  watertight airway surface for simulation. Drives 3D Slicer through the
  `slicer` MCP (mcp-slicer). Prefer this skill over hand-rolling VTK every time
  the task is nasal-airway geometry prep.
---

# Nasal Airway CFD Geometry

Produce a watertight, correctly-oriented STL of the nasal airway + nasopharynx
that a CFD mesher can use directly, starting from a head/sinus CT. The domain
has **two inlets (left + right nostrils)** and **one outlet (nasopharynx, on the
hard-palate axial plane)**; paranasal sinuses and the oral cavity are excluded.

This skill operates **3D Slicer** through the `slicer` MCP. Three tools matter:
`execute_python_code` (runs Python *inside* Slicer — numpy and scipy are
available there), `capture_screenshot`, and `list_nodes`. Slicer must be open
with its Web Server module running.

## Why segment from the source CT (not a pre-made STL)

A cleaned/smoothed STL is almost always a dead end for this task: it carries
**no patient orientation**, its nostril/choanal **openings have been sealed
over**, and the **oral cavity is often fused in** — so every inlet/outlet cut
becomes a blind guess. The source CT fixes all three: orientation is built in
(axial = true horizontal, so the hard palate is a real axial plane), the
openings are real air boundaries, and air is directly threshold-segmentable. If
the user hands you an STL, steer them to the CT.

## Workflow

Work through these stages in order. Each stage's concrete Slicer-Python is in
`references/slicer-snippets.md` — read it before running a stage and adapt the
parameters; don't retype VTK from memory. Show the user a screenshot at the end
of each visual stage and confirm before proceeding — placement judgments
(which scan, where the inlet/outlet planes go) are theirs to make.

### 1. Survey the cohort
List the candidate volumes and rank by resolution. Skip derived series
(`DERIVED`, `MIP` in the name), scouts (3rd dim < ~40), and thick-slice series.
Prefer thin slices (≤0.6 mm) and fine in-plane spacing. NRRD headers are plain
ASCII — you can parse `sizes` and `space directions` without loading. See
`references/screening.md`.

### 2. Screen & select a usable scan
This is an ENT/sinus-practice kind of dataset — **pathology is common**, so a
high-resolution scan is not automatically usable. Screen each candidate against
three criteria and get the user's clinical sign-off:

- **Straight septum** — no severe deviation (asymmetric/obstructed passages)
- **No mass/tumor** — sinuses aerated (black), skull base unremarkable
- **Nose in FOV** — anterior nasal structures/nostrils not cropped by the scan

The decisive view is an **axial slice at the maxillary-sinus level**, zoomed on
the nasal cavity (shows septum + both passages + nose coverage at once). To land
on that level reliably, use the **bilateral maxillary-sinus detector** (snippet
in references) — naive "most air" detectors get fooled by the frontal sinus and
mastoid air cells. Capture, present, and let the user confirm or pick another.

### 3. Threshold air & create the segmentation
Air mask = HU in **[-1024, -350]**. Build a visible segmentation so the user can
see what's captured. The whole air space is one connected blob (nasal connects
to outside through the nostrils, and to the pharynx/mouth) — that's expected;
the next stage bounds it.

### 4. Bound the domain with an ROI
Add an interactive `vtkMRMLMarkupsROINode` over the sinonasal region. **Its
faces are the CFD boundaries:** the anterior face sits just behind the nostril
tips (→ the two nostril inlets), the inferior face at the hard-palate level
(→ the nasopharyngeal outlet), the posterior face behind the nasopharynx, and
the lateral/superior faces enclose the nasal cavity. Let the user drag the
faces — this is the key anatomical decision. Anchor the initial box on the
enclosed-air extent.

### 5. Extract the airway (enclosed-air ∩ ROI)
Take **enclosed air** (per-slice, drop border-connected external air) intersect
with the ROI, label, keep the largest component. This is automatic and robust —
see the "Critical" note in `references/slicer-snippets.md`. Result is the nasal
cavity + nasopharynx + paranasal sinuses, no external leak. Sanity-check the
volume (≈40–70 cm³ with sinuses).

### 5b. Exclude the paranasal sinuses — manual, not morphological
This is the one genuinely manual step. The sinuses (maxillary, ethmoid,
sphenoid) join the nasal cavity through **thin ostia (~1–3 mm)**, while the
nasopharynx joins through the **wide choanae (~2–3 cm)**.

**Do NOT rely on morphological opening** (erode-keep-dilate) to snap the ostia.
It's too blunt: it also pinches the nasal valve, meatuses, and choanae, gnarls
the turbinate surface, and silently drops real passages (tested — erode=2 split
off a real 13 cm³ chunk; erode=3 shattered the airway). The surface it produces
is unusable for CFD.

**Manual Scissors is also fragile** — a stray Fill/closed-surface round-trip can
silently turn the whole segment into a filled block (it reads back as a constant
cross-section ~300+ cm³). If a segment volume jumps like that, discard it and
re-extract from enclosed∩ROI.

**What works: marker-controlled watershed** (scipy `ndimage.watershed_ift` —
skimage is usually absent in Slicer). Seed the keep-region and each sinus, let
the watershed cut at the narrow necks (ostia), keep the keep-region:

- Compute `edt = distance_transform_edt(airway, sampling=spacing)`.
- KEEP seeds (label 1): a few points down the central nasal channel + the
  nasopharynx. **To keep a sinus the user wants retained (e.g. ethmoid), drop a
  keep-seed inside it** — otherwise a nearby remove-seed will claim it.
- REMOVE seeds (labels 2,3,…): one per sinus, at its highest-EDT (deepest)
  voxel. **Maxillary auto-seeds reliably** (clearly lateral: `|i-mid_i|>26`).
  **Sphenoid**: posterior + superior + central. **Ethmoid does NOT auto-seed
  reliably** — it's a thin honeycomb contiguous with the upper nasal cavity near
  the midline; an auto "ethmoid" seed routinely lands in the nasal cavity and
  steals 40+ cm³. Either keep it, or have the user click it (and accept it's
  many cells).
- `img=(edt.max()-edt)` scaled to uint8 (necks + exterior become high-cost
  barriers, so flooding stays in the airway and splits at ostia); run
  `watershed_ift(img, markers)`; `keep = (ws==1) & airway`.
- **Always report per-label volumes** as a sanity check: a sinus seed claiming
  >10–15 cm³ means it grabbed nasal cavity — reposition it. Maxillary ≈ 6–8 cm³
  each, sphenoid ≈ 1–7 cm³.

Click-seeding hazard: points placed in slice views can land off-target (outside
the airway, e.g. in the 3D background) — those markers fall outside the mask and
silently do nothing. Verify seed RAS coords are inside the head before trusting
them; prefer auto-placement where the anatomy is unambiguous (maxillary).

If the user insists on Scissors instead: Segment Editor → Scissors, Erase-inside,
thin stroke across each ostium, then Islands → keep the nasal island.

If the user is fine keeping the sinuses (some CFD studies do — they're
near-stagnant), skip this; just warn that dead-end pockets complicate meshing
and convergence.

### 6. Outlet, smooth & export
**Outlet:** make a flat axial cut at the nasopharynx for a single clean outlet
patch (the device-seal interface in suction-device studies). Two subtleties:
(1) the enclosed-air airway stops *above* the ROI floor (enclosed air ends where
the nasopharynx opens to the oropharynx) — find the true `S_min` of the mask.
(2) The **hard-palate level is the choanae**, where the nasopharynx splits into
the two posterior nasal apertures → a cut there gives 2-3 openings, not one. The
**unified single nasopharynx** opening is a mm or two *lower*, right at the
bottom of the enclosed air. Scan axial loop-count from the bottom up: the level
with **1 loop** is the true single outlet; cut there. You generally *can't*
extend below it without pulling in the oropharynx/mouth.

**Smoothing — smooth the SURFACE, not the labelmap.** Labelmap smoothing
(Slicer "Smoothing factor" > ~0.1) severs the thin ethmoid/turbinate walls and
shatters the result into *hundreds* of shells (seen: 599 components). Instead:
set Smoothing factor "0", generate the closed surface, then on the polydata run
`vtkWindowedSincPolyDataFilter` (PassBand 0.1, ~20 iters, FeatureEdgeSmoothing
off, BoundarySmoothing off) — topology-preserving, removes stair-steps, keeps
turbinates. Marching cubes still emits tiny speckle shells, so
`vtkPolyDataConnectivityFilter` → **largest region** to get one clean body
(verify visually it didn't drop a wanted structure like the ethmoid — compare
volumes). Export STL via `saveNode(model, path)`; the model keeps RAS
orientation. Name with patient + date, save to the project geometry folder.

**Patches:** the exported surface is closed/watertight — inlet (2 nostrils) and
outlet are flat *faces* of it, which a mesher tags by region/normal. For
OpenFOAM/snappyHexMesh, optionally export separate `wall.stl` / `inlet.stl` /
`outlet.stl` instead (split by the cut-plane normals).

### 7. QC the result
Confirm **watertight** (0 boundary + 0 non-manifold edges) and **1 connected
component**; report **inlet/outlet areas + hydraulic diameters** (`Dh≈2√(A/π)`)
the user needs for CFD BCs, plus **triangle quality** (no slivers).

**Volume mismatch is usually benign.** A surface (mass-properties) volume ~15%
above the voxel-count volume (seen: 51.6 → 59.9 cm³) is the **marching-cubes
half-voxel offset** spread over a high surface-area, convoluted structure
(area × ~½-voxel ≈ the gap) — NOT self-intersection. It's the same before and
after smoothing. Don't chase it.

**The real meshing concern is genus (topological handles).** Kept ethmoid +
turbinates give a high-genus surface (seen: genus ≈ 118). Light morphological
closing barely helps (1-voxel: 118→115) because the tunnels are *real anatomy*,
not noise; aggressive closing (2-voxel: →37) only works by filling real airway
gaps (+13% volume) — a fidelity-vs-meshability tradeoff to put to the user. The
surface itself can be watertight/manifold/sliver-free and still be genus-100+;
it IS meshable, but the ethmoid/turbinate region needs fine local cells and
boundary-layer generation may struggle in the narrowest gaps. Also **decimate**
a 400k+ triangle surface to ~100–200k (topology-preserving) for CFD.

## Gotchas (learned the hard way)

- **`FitSliceToAll()` resets the slice offset to the volume center.** Always set
  the slice offset *after* calling Fit, or your carefully-computed nasal level
  silently jumps back to mid-FOV (usually the brain).
- **The dedicated `capture_screenshot` "slice" mode uses its own offset
  convention** (relative, not RAS). To screenshot a specific anatomical level,
  set the slice offsets in Python and capture `view_type="application"`
  (four-up) — that reflects the real slice-node positions.
- **Don't find the nasal level by "most air."** Frontal sinus and mastoid air
  cells are enclosed midline/paired air and will hijack the search. Use the
  bilateral maxillary-sinus fingerprint instead.
- **An STL has no orientation; a CT/NRRD does.** Never infer "which way is up"
  statistically if you can segment from the oriented source.
- **numpy + scipy run inside Slicer's Python** — use `slicer.util.arrayFromVolume`
  (returns a (Z,Y,X) view) and `scipy.ndimage.label` for connectivity. Call
  `arrayFromVolumeModified` after writing back.
- **`vtkMRMLScalarVolumeNode` is not a labelmap.** To import a binary mask into a
  segmentation, make a `vtkMRMLLabelMapVolumeNode` (e.g. via
  `volumes.logic().CreateAndAddLabelVolume`), not a cloned scalar volume.

### 8. OpenFOAM mesh + solve
Export split surface STLs (`wall`, `inletLeft`, `inletRight`, `outlet`) after the
user confirms seal/outlet placement. Run the Docker pipeline in
`~/Projects/nasal-airway-openfoam` — see `references/openfoam-pipeline.md`.

## References
- `references/slicer-snippets.md` — tested Slicer-Python for every stage.
- `references/screening.md` — cohort ranking + scan-selection criteria and the
  maxillary-level detector.
- `references/openfoam-pipeline.md` — snappyHexMesh case setup, BCs, post-process.
