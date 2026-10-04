---
name: surgical-video-toolkit
description: >-
  Prepare surgeon-reviewed edits of long surgical or endoscopic recordings.
  Deduplicate and order recording chunks, propose dead-time intervals for visual
  review, protect important moments, export a reviewed Premiere XML timeline with
  audio, and extract teaching highlights across edits. Use for OR footage,
  surgical teaching clips, endoscopy rough cuts, and Premiere handoff. Preserve
  uncertain footage; no automatic clinical-importance classification.
metadata:
  version: "2.0.0"
  author: Jaymarc Iloreta
---

# Surgical Video Toolkit · 2.0

Turn long surgical recordings into an auditable, surgeon-reviewed edit. Keep all
footage by default. Bright corners, darkness, and low motion are **candidate
signals**, not proof that a moment is unimportant. Source videos are never edited.

## Requirements and boundaries

Python 3.9+, NumPy, FFmpeg, and ffprobe; a browser for local review; Premiere for
final import verification. Work locally. No cloud service, credentials, model
weights, or network access is needed for processing. Preview clips contain actual
source imagery: store output in the approved case workspace, outside this public
skill repository. The included tests use synthetic media only.

This release handles one chronological recording with constant frame rate,
consistent dimensions, and mono/stereo audio. Reject mixed formats, suspected VFR,
or multichannel audio at export with a clear normalization instruction. This is
not multi-camera synchronization, clinical event recognition, or validated
clinical decision software. Heuristic VFR screening is not exhaustive; normalize
known VFR sources before use.

## Workflow

Run the following from `scripts/`, using absolute paths to source and output.
Create a fresh output directory for each review/export revision.

### 1. Align and verify the manifest

```bash
python3 align_chunks.py /path/to/recording -o /path/to/CASE/manifest.csv
```

Files are SHA-256 hashed; only byte-identical copies are deduplicated. Different
videos with the same filename remain distinct. `file` is now a stable clip ID;
`original_file` preserves the original basename. All later inputs use clip IDs.

Inspect the manifest and confirm chronology. Recording timestamps and file
modification times can be unreliable. For an explicit order, supply `--order
/path/to/order.txt`, one absolute source path per line, listing every deduplicated
source once. Copies of one recording are not separate camera angles.

### 2. Protect important moments and prepare review

Optional protected intervals use source seconds and manifest clip IDs:

```json
[{"file":"clip--0123456789abcdef.mp4","start":30,"end":45}]
```

```bash
python3 review_cuts.py prepare --manifest /path/to/CASE/manifest.csv \
  --outdir /path/to/CASE/review --profile conservative \
  --protect /path/to/CASE/protected.json
```

Omit `--protect` when there are no protected intervals. Profiles change which
intervals are proposed; **none authorize automatic removal**. Review outputs:

- `review.html`: local interactive Keep/Remove controls with adjustable bounds.
- `previews/`: thumbnails and short silent previews near candidate midpoints.
- `session.json`: manifest, candidate intervals, protected spans, source metadata,
  and a session ID binding the decisions to this review.
- `scores.csv`: per-second heuristic measurements.
- `KEEP_unreviewed.csv`: all footage retained, not an approved edit.

Open `review.html` in a browser. If local media loading is restricted, serve just
that output folder using `python3 -m http.server 8768 --bind 127.0.0.1 --directory
/path/to/CASE/review` and open `http://127.0.0.1:8768/review.html` locally.
Do not bind the review server to all network interfaces.

### 3. Review and apply decisions

Each proposal defaults to **Keep**. Choose Remove only after checking the content;
narrow its start/end when needed. Previews cover at most eight seconds and are
not a substitute for inspecting a long proposed interval in the source player.
Protected moments stay kept even when an overlapping proposal is removed.
Browser draft decisions persist locally when localStorage is available; download
is the durable handoff. Click **Download decisions**, then **Save decisions.json**,
or copy the displayed JSON if browser downloads are unavailable.

```bash
python3 review_cuts.py finalize --session /path/to/CASE/review/session.json \
  --decisions /path/to/decisions.json --outdir /path/to/CASE/approved
```

The finalizer rejects wrong-session, missing, duplicate, out-of-bounds, and invalid
decisions, and source size/modification changes. It emits `KEEP_reviewed.csv` and
`review_audit.json`. These checks detect common mistakes, not malicious tampering.

### 4. Export the reviewed timeline

```bash
python3 build_timeline.py --manifest /path/to/CASE/manifest.csv \
  --keep /path/to/CASE/approved/KEEP_reviewed.csv \
  --outdir /path/to/CASE/export --title "Reviewed surgical teaching edit"
```

Deliver **`.xml` (Final Cut Pro 7 / xmeml)** for Premiere, with source frame rate,
dimensions, escaped paths, and linked mono/stereo audio. The `.edl` fallback is
video-only and is emitted for up to 999 events; relinking may be manual.
**Do not describe `.fcpxml` as directly importable in Premiere.** See
[Premiere handoff](references/premiere_handoff.md).

### 5. Extract teaching highlights

```bash
python3 extract_markers.py --manifest /path/to/CASE/manifest.csv \
  --keep /path/to/CASE/approved/KEEP_reviewed.csv --timeline-at 1:20 \
  --length 30 --outdir /path/to/CASE/highlights
```

Use `--center` for a marker-centered clip, or `--at CLIP_ID=12:30` for a source
marker. Reviewed-timeline highlights assemble every selected KEEP interval,
including transitions across files. They never simply seek into the original and
continue through removed sections. Outputs are H.264 1080p MP4 with stereo AAC
when selected sources have audio. Silent segments receive silence when needed;
wholly silent selections remain silent. Clips at the end are shortened to the
available media. Existing files are not overwritten.

## Validation and iteration

Run `python3 -m unittest discover -s tests -v` from this skill folder.
Synthetic tests check duplicate handling, protected spans, review decisions,
XML escaping/audio/timing, and cross-cut highlight content. The software has not
been validated on surgical cases or through an actual Premiere import in this
release. Use [the evaluation protocol](references/evaluation.md) for the next
stage; prioritize important-footage retention over compression ratio.

The legacy `detect_deadtime.py` now retains footage by default. Its explicit
`--auto-cut` option is for legacy heuristic experiments; do not use it as the
standard surgeon-reviewed workflow. Prefer the reviewed KEEP CSV throughout.
