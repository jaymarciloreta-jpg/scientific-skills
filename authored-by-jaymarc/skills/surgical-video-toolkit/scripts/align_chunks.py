#!/usr/bin/env python3
"""
align_chunks.py — discover the recording's chunks and put them in chronological order.

Why this exists
---------------
Long surgical recordings are auto-split by the capture box into many sequential
MP4 chunks (often ~15 min each). Sometimes the same recording is also copied into
several folders. Two traps to avoid:

  1. Duplicate folders are byte-for-byte COPIES, not camera angles. "Aligning" them
     means picking ONE copy and ignoring the rest — never laying them side by side.
  2. Filename order is not always chronological. A capture box may name the first
     short chunk "Ch1_001_V.MP4" and the next "Ch1_001_CH001_V.MP4", which sort the
     wrong way alphabetically. The reliable clock is the embedded recording time.

So this script de-duplicates by filename, orders chunks by embedded creation_time
(falling back to file mtime, then a natural filename sort), and writes a manifest
that every later step reads. The result is one continuous timeline in true order.

Usage
-----
  python align_chunks.py FOLDER [FOLDER ...] -o manifest.csv
  python align_chunks.py /path/to/recording_folder -o manifest.csv --json manifest.json

Output: manifest.csv with one row per chunk:
  index, file, path, duration_sec, timeline_start_sec, creation_time, order_basis
"""
import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime

from common import probe_basics, sec_to_clock

VIDEO_EXTS = {".mp4", ".mov", ".mxf", ".m4v", ".avi", ".mts", ".m2ts"}


def natural_key(name):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", name)]


def parse_time(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def collect(folders):
    """Gather video files, de-duplicating identical filenames across folders."""
    seen = {}
    for folder in folders:
        if not os.path.isdir(folder):
            print(f"  ! not a folder, skipping: {folder}", file=sys.stderr)
            continue
        for entry in sorted(os.listdir(folder)):
            ext = os.path.splitext(entry)[1].lower()
            if ext not in VIDEO_EXTS:
                continue
            if "_thumb" in entry.lower():
                continue
            if entry not in seen:  # first folder wins; later copies ignored
                seen[entry] = os.path.join(folder, entry)
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="+", help="one or more source folders")
    ap.add_argument("-o", "--out", default="manifest.csv", help="output manifest CSV")
    ap.add_argument("--json", help="optional JSON copy of the manifest")
    args = ap.parse_args()

    files = collect(args.folders)
    if not files:
        sys.exit("No video files found.")
    print(f"Found {len(files)} unique chunk(s) across {len(args.folders)} folder(s).")

    rows = []
    for name, path in files.items():
        b = probe_basics(path)
        ctime = parse_time(b["creation_time"])
        rows.append({
            "file": name, "path": path, "duration_sec": round(b["duration"], 3),
            "width": b["width"], "height": b["height"], "fps": str(b["fps"]),
            "creation_time": b["creation_time"] or "",
            "_ctime": ctime, "_mtime": os.path.getmtime(path),
        })

    # Order: embedded creation_time if every chunk has one, else mtime, else name.
    if all(r["_ctime"] for r in rows):
        rows.sort(key=lambda r: r["_ctime"]); basis = "creation_time"
    elif len({round(r["_mtime"]) for r in rows}) == len(rows):
        rows.sort(key=lambda r: r["_mtime"]); basis = "file_mtime"
    else:
        rows.sort(key=lambda r: natural_key(r["file"])); basis = "filename"
    print(f"Ordered chunks by: {basis}")

    t = 0.0
    for i, r in enumerate(rows, 1):
        r["index"] = i
        r["timeline_start_sec"] = round(t, 3)
        r["order_basis"] = basis
        t += r["duration_sec"]

    cols = ["index", "file", "path", "duration_sec", "width", "height", "fps",
            "timeline_start_sec", "creation_time", "order_basis"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    if args.json:
        with open(args.json, "w") as f:
            json.dump([{k: r[k] for k in cols} for r in rows], f, indent=2)

    print(f"\nTotal duration: {sec_to_clock(t)}  ({t/60:.1f} min)")
    print(f"Manifest written: {args.out}")


if __name__ == "__main__":
    main()
