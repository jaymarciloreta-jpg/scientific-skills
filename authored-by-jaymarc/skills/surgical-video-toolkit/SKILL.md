---
name: surgical-video-toolkit
description: >-
  Edit long surgical / endoscopic recordings (sinus, skull base, ENT, laparoscopic,
  arthroscopic, any scope or OR camera) into a Premiere-ready edit. Use whenever
  someone wants to turn raw OR footage into something watchable or teachable: stitch
  the auto-split chunks into one continuous recording in the right order,
  automatically cut dead time (scope out of the patient, standby/black screens, long
  idle stretches), generate a Premiere FCPXML/EDL timeline of just the good footage,
  or pull short fixed-length highlight/"marker" clips. Triggers on "edit this surgery
  video", "remove the dead time", "cut where the scope is out", "make a rough cut of
  the case", "stitch these OR chunks together", "make a Premiere timeline from this
  endoscopy", "pull highlight clips from the case", or any multi-hour OR/scope
  recording that needs trimming. Drivable in plain English by attendings and
  residents. Not for consumer/vlog video, photo editing, audio cleanup, or plain
  resize/compress. Source files are never modified.
---

# Surgical Video Toolkit

Turn raw operating-room footage into an edit. The heavy, mind-numbing part of
editing a surgical case is not the creative cutting — it is wading through hours of
the scope sitting on the tray, black standby screens, and slow idle stretches to
find the surgery. This skill automates that triage and hands a human a clean
Premiere timeline (or short clips) to finish from.

It is built to be **non-destructive and transparent**: it only ever reads the
footage and writes small text/CSV files. Every cut it proposes is listed in a CSV a
human can audit, and every threshold is a knob you can turn. Think of it as a fast,
tireless first-assist for the edit — not a black box.

## The four modules (and when to use each)

1. **Align** (`scripts/align_chunks.py`) — discover the chunks and order them.
   Capture boxes auto-split a long case into many sequential MP4s and sometimes
   copy the whole recording into several folders. Use this first, always. It
   de-duplicates identical copies and orders chunks by their embedded recording
   time (filenames lie about order). Output: `manifest.csv`.

2. **Detect dead time** (`scripts/detect_deadtime.py`) — score every second and
   decide keep vs. cut. Use when the goal is "remove the boring/empty parts."
   Output: `*_KEEP_segments.csv`, `*_REMOVED_regions.csv`, `*_per_second.csv`.

3. **Build timeline** (`scripts/build_timeline.py`) — turn the KEEP list into a
   Premiere-importable `.fcpxml` (primary) and `.edl` (backup). Use right after
   detection. This is the deliverable the editor opens in Premiere.

4. **Extract markers** (`scripts/extract_markers.py`) — cut short, flat,
   shareable highlight clips (default 30 s, H.264+AAC 1080p). Use for teaching
   clips / conference reels, independent of the rough cut. Markers can be given as
   "file + time" or as positions on the dead-time-removed timeline.

You do not have to run all four. "Just pull two 30-second clips" → module 4 only
(with module 1 for paths). "Make a rough cut" → modules 1→2→3.

## Standard workflow (the rough cut)

Run from the `scripts/` directory. `ffmpeg`, `ffprobe`, Python 3, and `numpy` must
be available.

```bash
# 1. Align: point at the folder(s) holding the recording. Multiple folders that are
#    copies of each other are fine — it keeps one.
python align_chunks.py "/path/to/CASE_folder" -o OUT/manifest.csv

# 2. Detect dead time. --profile balanced is the sane default.
python detect_deadtime.py --manifest OUT/manifest.csv --outdir OUT \
    --name CASE --profile balanced

# 3. Build the Premiere timeline from the kept segments.
python build_timeline.py --keep OUT/CASE_KEEP_segments.csv --manifest OUT/manifest.csv \
    --outdir OUT --name CASE_ROUGH_CUT --title "CASE - dead-time removed"
```

Then hand off the `.fcpxml` (see `references/premiere_handoff.md`). Always also
write a short `README_edit.md` next to the outputs summarizing what was kept,
removed, and why — surgeons want that transparency before they trust the cut. There
is a template at the end of `references/premiere_handoff.md`.

## Marker / highlight clips

```bash
# Source-relative: "in this chunk, starting at 12:30"
python extract_markers.py --outdir OUT/markers --length 30 \
    --manifest OUT/manifest.csv --at Ch1_004_CH002_V.MP4=12:30

# Timeline-relative: a spot you noted while scrubbing the rough cut
python extract_markers.py --outdir OUT/markers --length 30 --center \
    --keep OUT/CASE_KEEP_segments.csv --manifest OUT/manifest.csv \
    --timeline-at 45:10 --prefix Sinus
```

## How detection actually works (so you can defend the cuts)

The recording is sampled once per second into a tiny grayscale frame, then scored:

- **Scope-out** → bright frame **corners**. An endoscope paints a black circular
  mask with dark corners; when the scope leaves the body the corners light up.
- **No-signal** → near-black **whole frame** (standby screen, capped scope, blackout).
- **Idle** → low frame-to-frame **motion** sustained long enough (brief pauses are
  kept so the result doesn't feel jump-cut).

A second is kept only if it is in-body, has signal, and isn't part of a long idle
run. Kept regions get short handles (0.5 s) so cuts don't slam onto motion, and
slivers shorter than 1 s are dropped. Spot-check the boundaries against the actual
footage before trusting a new case — render a couple of marker clips at cut/keep
edges, or read `*_per_second.csv`. Full threshold reference and tuning advice:
`references/tuning.md`.

## Guardrails worth keeping in mind

- **Never treat duplicate folders as camera angles.** If folders are byte-identical
  copies, they are one recording; `align_chunks.py` handles this, but if asked to
  "sync the three angles," confirm whether they are truly different angles first.
- **Confirm the profile with the surgeon.** "Balanced" removes obvious dead time
  with safe handles. For grand-rounds teaching, `conservative` is safer; for a quick
  social cut, `aggressive`. When in doubt, default to balanced and offer to
  regenerate — re-running detection is cheap.
- **Keep it non-destructive.** Outputs are an edit list, not a re-render. Only
  `extract_markers.py` writes new video, and it writes new files alongside, never
  over the source.
- If a surgeon wants a single flat trimmed MP4 instead of a Premiere timeline, that
  is a reasonable follow-up (concatenate the KEEP segments with ffmpeg) — offer it,
  but the timeline is the default because it leaves the human in control.

## Reference files

- `RESIDENT_GUIDE.md` — plain-English, step-by-step guide written for residents to
  drive this whole workflow from Claude + Premiere. This is the wiki-facing doc.
- `references/premiere_handoff.md` — importing the FCPXML/EDL, relinking media,
  fine-tuning, exporting, plus a README_edit template.
- `references/tuning.md` — every threshold, the three profiles, and how to make a
  cut tighter or looser.
