---
name: slicer-sinus-roi
description: >
  Automates the "import CT, volume rendering, paranasal-sinus ROI" step of
  the NINS / SPG Anatomy Study protocol in 3D Slicer: load a head CT DICOM
  series, apply a CT volume-rendering preset, and auto-draft a "Sinus_ROI"
  markup box around the paranasal sinuses for the user to visually confirm or
  nudge. Use this whenever the user asks to "crop the volume and create an ROI
  of the sinuses in Slicer", "set up the sinus ROI for volume rendering",
  "run the Create ROI step of the protocol", or references cropping /
  ROI-ing a CT in 3D Slicer for this study, even if they don't name the script.
  Do NOT use for the nasal-airway CFD segmentation pipeline (that's the
  separate nasal-cavity-airflow skill) or for placing anatomical landmarks
  (that's a separate Landmark_Measurements step).
---

# Slicer sinus ROI setup

This skill packages the "Create ROI" step from the user's own NINS project
protocol (`03 Projects/NINS/00 Protocol & Setup/(C) Protocol` in their
Obsidian vault) as a single Slicer Python script, so the tedious first pass
- import the scan, turn on volume rendering, draw a box around the sinuses -
happens automatically, and the user only has to eyeball and nudge the result
instead of dragging it into place by hand every time.

## Why this exists

The recorded workflow this skill was built from did the same three things
twice: once by hand in 3D Slicer (Add Data -> pick the right series among
several "Unnamed Series" -> Volume Rendering -> drag an ROI box), and once by
typing "crop volume and create an ROI of the sinuses" to a Cursor agent that
was talking to Slicer's built-in Web Server module over HTTP. Both runs
converge on the same three outcomes, so this skill produces one script that
reaches them directly instead of re-clicking through the GUI or re-explaining
the task to an agent in prose each time.

## Important: this runs *in* Slicer, not in this session

Claude in this session (Cowork / cloud sandbox) cannot reach the user's local
3D Slicer instance or its Web Server (`http://localhost:<port>/...` is not
reachable from here, in the cloud or via the device bridge - it's the user's
own machine's loopback interface). So a Claude session encountering this
skill should **not** try to execute the script itself. Instead:

1. Hand the user (or paste into their existing tool) the script at
   `scripts/create_sinus_roi.py`, unmodified unless they've asked for a
   parameter change (preset name, margin, thresholds - see below).
2. Tell them how to run it, matching whichever path they're already using:
   - **Their existing Cursor + `slicer-mcp-server.py` pipeline** (this is
     what the recording showed): make sure Slicer's Web Server module is
     started (`Modules -> Web Server -> Start server`), then have Cursor's
     agent call the MCP server's `execute_python` tool with
     `exec(open('/absolute/path/to/create_sinus_roi.py').read()); main(dicom_dir=...)`.
     If the script needs to land on the Slicer host first, use the server's
     `/file` upload endpoint (see the `slicer` skill's MCP section) rather
     than pasting the whole file through `execute_python` - it's much faster.
   - **Directly in Slicer**, no Cursor needed: open
     `View -> Python Interactor` and run the same
     `exec(open(...).read()); main(...)` line there.
3. If neither Slicer nor Cursor is running, this skill can't complete the
   task on its own — say so, rather than guessing at a substitute. Computer
   use (screen control) is the other route that would let a future session
   drive Slicer's UI directly instead of running this script; mention it as
   an option if the user would rather have the exact recorded clicks
   automated than a script.

## What `main()` does

`scripts/create_sinus_roi.py` defines a single entry point:

```python
main(
    dicom_dir=None,             # a directory of DICOM files to import; pass
                                 # None to use the volume already loaded/active
                                 # in the scene instead of importing anything
    preset_name="CT-Chest-Contrast-Enhanced",
    roi_name="Sinus_ROI",
    margin_mm=8,                # padding added around the auto-detected
                                 # sinus air pockets
    sinus_bounds_ras=None,      # manual override: (rmin,rmax,amin,amax,smin,smax)
                                 # in RAS mm - use this if the auto heuristic
                                 # grabs the wrong air pocket (see below)
)
```

Steps, in order:

1. **Import (optional).** If `dicom_dir` is given, imports every series found
   there via `DICOMLib.DICOMUtils` and loads them all as scalar volumes -
   same as what "Add Data -> choose directory" does in the GUI. If
   `dicom_dir` is `None`, it works on whatever CT volume is already loaded.
2. **Pick the primary series.** When multiple volumes are present (the
   recording showed several "Unnamed Series", some tagged
   `DERIVED-PRIMARY-AXIAL...`), the script skips any node whose name contains
   `DERIVED` and picks the remaining one with the most slices - that's the
   original acquisition, not a scanner-generated reformat. If this picks the
   wrong series for a given scan, pass the node's name explicitly (see
   `volume_node_name` kwarg in the script) instead of relying on the
   heuristic.
3. **Volume rendering.** Creates the default volume-rendering display node,
   turns visibility on, and copies in the named preset (defaults to
   `CT-Chest-Contrast-Enhanced`, matching what was on screen in the
   recording - swap for any preset name Slicer lists in the Volume Rendering
   module's Preset dropdown).
4. **Draft the sinus ROI.** This is the part worth understanding rather than
   trusting blindly: true anatomical sinus segmentation needs an atlas or a
   trained model, which is out of scope here. Instead the script uses the
   same shortcut a person does when dragging the box by eye - air reads as a
   clear intensity band on CT (roughly -1024 to -300 HU) - and automates the
   *bounding box* part:
   - Threshold the whole volume for air-range voxels.
   - Label connected air components.
   - Drop any component touching the image border (that's the room/table air
     around the patient, not anatomy).
   - Assume the single largest remaining internal air component is the main
     nasal/nasopharyngeal airway (it's bigger and more contiguous than an
     isolated sinus cell - the same assumption the `nasal-cavity-airflow`
     skill's segmentation makes).
   - Take the bounding box of the next-largest handful of components (the
     maxillary/ethmoid/frontal/sphenoid air cells) as the draft sinus region,
     pad it by `margin_mm`, and convert to RAS using the volume's
     IJK-to-RAS matrix.
   This is a first draft, not a diagnosis-grade segmentation - the same
   "confirm the ROI accurately captures the paranasal sinuses" check the
   user's own protocol note calls for still applies. If a scan has unusual
   anatomy (prior sinus surgery, packed/opacified sinuses, pediatric anatomy)
   the heuristic can grab the wrong component; that's what `sinus_bounds_ras`
   is for - skip the heuristic and hand it exact bounds instead.
5. **Create/update the ROI node.** Names it `Sinus_ROI` (matching the
   protocol note), sets it to the computed center/size, enables cropping on
   the volume-rendering display node, and attaches the ROI so "Crop: Enable"
   and "Display ROI" in the Volume Rendering panel reflect it immediately -
   same end state as the manual drag in the recording.

## Adjusting after the fact

The script leaves a normal Markups ROI node in the scene, so anything after
it runs is just normal Slicer interaction: drag its handles in any slice or
3D view to correct it, or re-run `main()` with a tighter/looser `margin_mm`
or an explicit `sinus_bounds_ras` once you know the right numbers for this
scan.

## Reference

- `scripts/create_sinus_roi.py` - the full implementation.
- The `slicer` skill (search/reason over 3D Slicer source) has the
  authoritative API docs if the Slicer version in use changes the Markups
  ROI or Volume Rendering API - check
  `script_repository/markups.md` and `script_repository/webserver.md` there
  before changing this script's node API calls.
- The `nasal-cavity-airflow` skill documents the related but distinct task of
  segmenting the nasal *airway* (not the sinuses) into a CFD-ready mesh -
  useful background on why "biggest air component = main airway" is a safe
  assumption on this anatomy.
