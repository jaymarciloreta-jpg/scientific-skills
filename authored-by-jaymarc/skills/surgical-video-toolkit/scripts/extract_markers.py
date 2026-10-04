#!/usr/bin/env python3
"""
extract_markers.py — cut short, shareable highlight clips ("marker clips").

Use this for teaching clips, conference reels, or "look at this step" moments:
fixed-length clips (default 30 s) pulled at chosen timestamps and re-encoded to a
clean, universally-playable H.264 + AAC MP4 at 1080p. Unlike the rough-cut
timeline (which is a non-destructive edit list), these are flat video files you
can drop into Keynote/PowerPoint, email, or upload.

Two ways to say WHERE to cut:
  * --at: source-relative — "in file X, starting at MM:SS". Best when you already
    know the clip is in a specific chunk.
  * --timeline-at with --keep: timeline-relative — a position in the dead-time-
    removed cut. The script maps it back to the right source file and offset using
    the KEEP_segments.csv, so the timestamps you read off the rough cut just work.

Timestamps accept SS, MM:SS, or HH:MM:SS. By default a marker is the START of the
clip; use --center to treat it as the midpoint instead.

Usage
-----
  # source-relative, two clips, default 30 s, into ./markers
  python extract_markers.py --outdir markers \
      --at Ch1_004_CH002_V.MP4=12:30 --at Ch1_004_CH002_V.MP4=21:05 \
      --manifest manifest.csv

  # timeline-relative against the rough cut, 20 s clips centered on the marker
  python extract_markers.py --outdir markers --length 20 --center \
      --keep Medina_sinus_KEEP_segments.csv --manifest manifest.csv \
      --timeline-at 45:10 --timeline-at 1:12:40 --prefix Sinus
"""
import argparse
import csv
import os
import sys

from common import run, sec_to_clock


def parse_ts(s):
    parts = [float(x) for x in str(s).split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, sec = parts[-3], parts[-2], parts[-1]
    return h * 3600 + m * 60 + sec


def load_paths(manifest):
    paths = {}
    if manifest and os.path.exists(manifest):
        with open(manifest) as f:
            for r in csv.DictReader(f):
                paths[r["file"]] = r["path"]
    return paths


def timeline_to_source(tl_sec, keep_csv):
    """Map a timeline position to (source_file, source_sec) via KEEP segments."""
    with open(keep_csv) as f:
        keeps = list(csv.DictReader(f))
    acc = 0.0
    for k in keeps:
        d = float(k["duration_sec"])
        if tl_sec <= acc + d:
            return k["source_file"], float(k["src_in_sec"]) + (tl_sec - acc)
        acc += d
    last = keeps[-1]
    return last["source_file"], float(last["src_out_sec"])


def extract(src_path, start, length, out_path):
    start = max(0.0, start)
    # -ss before -i for a fast seek, re-encode for a clean keyframe-accurate clip.
    cmd = [
        "ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", str(src_path),
        "-t", f"{length:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out_path),
    ]
    run(cmd)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--length", type=float, default=30.0, help="clip length in seconds")
    ap.add_argument("--center", action="store_true",
                    help="treat each timestamp as the clip midpoint, not its start")
    ap.add_argument("--prefix", default="Marker", help="output filename prefix")
    ap.add_argument("--manifest", help="manifest.csv for resolving source paths")
    ap.add_argument("--keep", help="KEEP_segments.csv (needed for --timeline-at)")
    ap.add_argument("--at", action="append", default=[],
                    help="source-relative marker FILE=TIMESTAMP (repeatable)")
    ap.add_argument("--timeline-at", action="append", default=[],
                    help="timeline-relative marker TIMESTAMP (repeatable, needs --keep)")
    args = ap.parse_args()

    paths = load_paths(args.manifest)
    os.makedirs(args.outdir, exist_ok=True)
    jobs = []  # (source_file, start_sec)

    for spec in args.at:
        if "=" not in spec:
            sys.exit(f"--at expects FILE=TIMESTAMP, got: {spec}")
        fn, ts = spec.split("=", 1)
        jobs.append((fn, parse_ts(ts)))

    for ts in args.timeline_at:
        if not args.keep:
            sys.exit("--timeline-at requires --keep KEEP_segments.csv")
        fn, src_sec = timeline_to_source(parse_ts(ts), args.keep)
        jobs.append((fn, src_sec))

    if not jobs:
        sys.exit("No markers given. Use --at or --timeline-at.")

    n = 0
    for i, (fn, start) in enumerate(jobs, 1):
        if args.center:
            start -= args.length / 2.0
        src = paths.get(fn, fn)
        if not os.path.exists(src):
            print(f"  ! source not found, skipping: {fn}", file=sys.stderr)
            continue
        out = os.path.join(args.outdir,
                           f"{args.prefix}_{i:02d}_{int(args.length)}s.mp4")
        print(f"  clip {i}: {fn} @ {sec_to_clock(max(0,start))} -> {os.path.basename(out)}")
        extract(src, start, args.length, out)
        n += 1
    print(f"\nWrote {n} marker clip(s) to {args.outdir}")


if __name__ == "__main__":
    main()
