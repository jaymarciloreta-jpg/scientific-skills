# Tuning the dead-time detection

Every cut comes from a handful of thresholds. They live at the top of
`scripts/detect_deadtime.py`. You rarely need to touch the code — pick a profile
and, if needed, override a couple of flags. This file explains what each knob does
and how to react to common complaints.

## The three profiles

Set with `--profile`. They differ only in how eagerly idle footage is cut:

| Profile        | min idle run | motion threshold | Use it when… |
|----------------|--------------|------------------|--------------|
| `conservative` | 12 s         | 1.2              | Grand rounds / medico-legal; only obvious long dead time should go. |
| `balanced`     | 5 s          | 2.0              | Default. Clear dead time removed, surgery flow intact. |
| `aggressive`   | 3 s          | 3.0              | Quick social / sizzle cut; tolerate a snappier feel. |

- **min idle run**: the shortest stretch of low motion that counts as idle. Larger
  = more pauses survive.
- **motion threshold**: mean per-second pixel change below which a second is "low
  motion." Higher = more seconds look idle.

## The brightness thresholds (constants in the script)

These are the same across profiles because they reflect the optics, not taste:

- `CORNER_BRIGHT = 55` — corners brighter than this ⇒ **scope-out**. The single most
  important knob. If in-body footage with a bright field is being cut as scope-out,
  raise it (e.g. 70). If scope-out footage is sneaking through, lower it (e.g. 45).
- `FRAME_DARK = 16` — whole frame darker than this ⇒ **no-signal**. Raise slightly if
  dim-but-real surgery is being dropped; lower if standby screens survive.
- `HANDLE_SEC = 0.5` — padding kept on each side of every cut so it doesn't land hard
  on motion. Raise to 1.0 for a gentler feel.
- `MIN_KEEP_SEC = 1.0` — kept segments shorter than this are dropped as slivers.

## Flags you can pass without editing code

- `--profile {conservative,balanced,aggressive}`
- `--keep-redout` — keeps short dark spans (≤4 s) that are likely the lens pressed
  against mucosa ("red-out") rather than true dead time. Use when a surgeon says
  "you cut the moments where I was right on the tissue."
- `--fps` — override frame rate (default 29.97 non-drop). Set if the capture is 25 or
  59.94, so timecodes line up in Premiere.

## Reacting to feedback

| Complaint | Fix |
|-----------|-----|
| "It cut real surgery where the field was bright." | Raise `CORNER_BRIGHT` (e.g. 70). |
| "Scope-out footage made it into the cut." | Lower `CORNER_BRIGHT` (e.g. 45). |
| "Too choppy / too many micro-cuts." | Use `conservative`, or raise `HANDLE_SEC` and `MIN_KEEP_SEC`. |
| "Still too long, trim harder." | Use `aggressive`, or lower `min_idle` / raise motion threshold. |
| "You cut the lens-on-tissue moments." | Add `--keep-redout`. |
| "Timecodes are off in Premiere." | Pass the correct `--fps`. |

## Verifying a cut before you trust it

Detection is a heuristic, so confirm it on each new kind of case:

1. Open `*_per_second.csv` and skim the `reason`/score columns around a few
   transitions.
2. Or render marker clips at a couple of cut **and** keep boundaries
   (`extract_markers.py --timeline-at ...`) and eyeball them: every kept sample
   should show active surgery, every cut sample should be genuinely low-value.

Re-running detection is cheap (a multi-hour case scans in a few minutes), so iterate
freely rather than agonizing over the first pass.
