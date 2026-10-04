# OpenFOAM pipeline reference

## Inputs from Slicer (Stage 6–7)

1. User confirms **seal/outlet plane** — single-loop nasopharyngeal opening at device interface.
2. Export four watertight patches (mm, RAS, decimated ~100–200k tris total on wall):
   - `wall.stl`, `inletLeft.stl`, `inletRight.stl`, `outlet.stl`
3. Record patch areas from QC → `bc/<case>.json`.

## Project commands

All commands run from `~/Projects/nasal-airway-openfoam` on the host; OpenFOAM runs inside Docker (`opencfd/openfoam-default:2312`).

| Step | Command | Output |
|------|---------|--------|
| Create case | `./scripts/new-case.sh <name> geometry/<name>/` | `cases/<name>/` |
| Mesh | `./scripts/run-mesh.sh cases/<name>` | `log.snappyHexMesh`, polyMesh |
| Solve | `./scripts/run-solve.sh cases/<name>` | `log.simpleFoam`, time dirs |
| Post | `./scripts/postprocess.sh cases/<name>` | patch integrals, `case.foam` |

## Boundary conditions

Default steady inspiratory flow:

- **inletLeft / inletRight:** `fixedValue` velocity, +Z direction (adjust in `0/U` if your RAS export differs)
- **outlet:** `fixedValue` pressure = 0 (gauge)
- **wall:** `noSlip`
- **outer:** background mesh patch — should be removed by snappy; if it remains, set `type empty` or refine `locationInMesh`

Flow split: `Q_left = Q_total × A_left / (A_left + A_right)`.

## snappyHexMesh tuning

| Issue | Knob |
|-------|------|
| Ethmoid genus / tiny tunnels | `resolveFeatureAngle 20–30`, local `(3 4)` refinement on wall |
| Memory | lower `maxGlobalCells` (e.g. 4e6) |
| Negative volume | move `locationInMesh` to center of nasal cavity (auto-set by `prepare_case.py`) |
| sliver cells | `minVol`, `maxNonOrtho` in `meshQualityControls` |

## Optional next steps

- Enable `addLayers true` for wall y+ control (hard in high-genus ethmoid).
- Switch to `pimpleFoam` for transient inhalation waveform.
- Map olfactory-plane samples with `postProcess -func surfaces`.
