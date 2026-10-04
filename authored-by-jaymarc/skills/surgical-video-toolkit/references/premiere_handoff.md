# Premiere handoff

The toolkit produces an **edit list**, not a rendered video. You finish the edit in
Premiere. Here is how to get from the generated files to a working timeline and out
to a final file.

## What the files are

- `*_ROUGH_CUT.fcpxml` — **import this.** Premiere builds a sequence with every kept
  clip already laid end to end, in order. Carries media references so Premiere can
  relink automatically.
- `*_ROUGH_CUT.edl` — backup with the identical cut list. If FCPXML import misbehaves
  on a given Premiere version, import the EDL instead; it relinks by clip name.
- `*_KEEP_segments.csv` — every kept segment (source file, in/out timecode, duration).
- `*_REMOVED_regions.csv` — every removed region with its reason, for transparency.

## Importing the FCPXML

1. In Premiere: **File → Import** and choose `*_ROUGH_CUT.fcpxml`.
2. Premiere creates a sequence named from the title you passed (e.g. *"CASE -
   dead-time removed"*) with all kept clips in order.
3. If it asks to **relink media**, point it at the source folder. If the recording
   was copied into several identical folders, any one of them works — Premiere
   relinks the rest by filename.
4. Each clip is named `<source> cutNNN`, so you can always trace a clip back to where
   it came from in the raw footage.

## If FCPXML import fails

Use the EDL: **File → Import** → `*_ROUGH_CUT.edl`. When prompted, choose the source
footage to relink against. Same cuts, same order.

## Fine-tuning (this is where the human earns their keep)

- Scrub the sequence. The automation removes dead time; it does **not** make
  storytelling decisions. Trim clip heads/tails, reorder, and drop steps that aren't
  teaching anything.
- Add titles/lower-thirds for each surgical step, and a patient-de-identified slate
  at the top if the video leaves the institution.
- If you want chapter markers, the boundaries in `*_KEEP_segments.csv` are a good
  starting list.

## Exporting

- **File → Export → Media**, H.264, "Match Source" for a faithful 1080p29.97 export,
  or a smaller preset for a review proxy / upload.
- For conference or social, consider exporting selects as separate clips (or use the
  marker-clip module) rather than one long file.

## De-identification reminder

Surgical video can be PHI. Before anything leaves the institution, confirm there is
no patient identifier on the capture (name overlays, the standby screen, the slate)
and follow your institution's media-release policy.

---

## README_edit template

Write this next to the outputs so the surgeon can trust the cut at a glance. Fill in
the bracketed numbers from the detection summary and CSVs.

```markdown
# [Case] — automated rough cut

Removes scope-out, no-signal, and idle footage from the full recording and hands you
a Premiere-ready timeline. Your source files are untouched.

## The result
- Kept: [X] min across [N] segments
- Removed: [Y] min ([Z]%) — scope-out [a] min, no-signal [b] min, idle [c] min
- Trimming profile: [balanced] — 0.5 s handles around every cut.

## How to use it in Premiere
1. File → Import → `[Case]_ROUGH_CUT.fcpxml`.
2. Premiere builds the sequence with all kept clips in order.
3. If asked to relink, point at the source folder.
4. Each clip is named `<source> cutNNN` so you can trace it back.
Backup: import `[Case]_ROUGH_CUT.edl` if FCPXML misbehaves.

## How the cuts were decided
Every second was scored on three signals: scope-out (bright corners), no-signal
(near-black frame), and idle (low motion ≥ [min idle] s). Spot-checked at cut/keep
boundaries.

## Files
- `[Case]_ROUGH_CUT.fcpxml` — the timeline (import this).
- `[Case]_ROUGH_CUT.edl` — backup cut list.
- `[Case]_KEEP_segments.csv` — every kept segment.
- `[Case]_REMOVED_regions.csv` — every removed region + reason.

## Tuning
Want it tighter or looser? Re-run detection with a different profile or
`--keep-redout`. See references/tuning.md.
```
