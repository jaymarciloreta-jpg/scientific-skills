#!/usr/bin/env python3
"""
detect_deadtime.py — find the dead time in an endoscopic recording.

What "dead time" means here, and how each kind is detected
----------------------------------------------------------
The script samples the footage once per second (cheap, plenty for this), shrinks
each sample to a tiny grayscale frame, and scores three signals:

  * SCOPE-OUT  — when the scope leaves the nostril the black circular endoscope
    mask disappears and the frame CORNERS go bright. In-nose footage has dark
    corners; scope-out footage has bright corners. So we measure corner brightness.

  * NO-SIGNAL  — capture standby / capped scope / blackout frames are nearly
    black across the WHOLE frame. So we measure overall brightness.

  * IDLE       — the scope is in the nose but nothing is happening. We measure
    frame-to-frame change (motion). A run of low-motion seconds that lasts long
    enough is idle; brief pauses are kept so the edit doesn't feel chopped.

A second is KEPT only if it is in-nose AND has signal AND is not part of a long
idle run. Kept regions are then padded with short handles (so cuts don't land
hard on motion) and tiny slivers are dropped.

This is a transparent, inspectable heuristic — not a neural net. Every threshold
is a flag you can tune (see references/tuning.md), and the output CSVs let a human
verify every cut. Source files are never modified.

Usage
-----
  python detect_deadtime.py --manifest manifest.csv --outdir OUT [--profile balanced]
  python detect_deadtime.py --manifest manifest.csv --outdir OUT \
      --profile aggressive --keep-redout

Outputs (in OUT/):
  <name>_KEEP_segments.csv     every kept segment (source file, in/out TC, duration)
  <name>_REMOVED_regions.csv   every removed region with its reason
  <name>_per_second.csv        raw per-second scores (for tuning / auditing)
"""
import argparse
import csv
import os
import subprocess
import sys
from fractions import Fraction

import numpy as np

from common import sec_to_tc, sec_to_clock

# Sampling frame size. Small = fast; 64x64 keeps corner/motion signal intact.
GRID = 64
CORNER = 12  # corner patch size in the shrunk frame

PROFILES = {
    # min_idle_sec: shortest low-motion run that counts as idle (longer => keeps more)
    # motion_thresh: per-second mean abs frame delta below which a second is "low motion"
    "conservative": {"min_idle_sec": 12.0, "motion_thresh": 1.2},
    "balanced":     {"min_idle_sec": 5.0,  "motion_thresh": 2.0},
    "aggressive":   {"min_idle_sec": 3.0,  "motion_thresh": 3.0},
}

# Brightness thresholds (0-255 on the shrunk grayscale frame).
CORNER_BRIGHT = 55.0   # corners brighter than this => scope is out of the nose
FRAME_DARK = 16.0      # whole frame darker than this => no signal / standby / blackout
HANDLE_SEC = 0.5       # padding kept on each side of a cut
MIN_KEEP_SEC = 1.0     # drop kept slivers shorter than this


def sample_frames(path):
    """Yield one (sec_index, frame) per second as a GRID x GRID uint8 array."""
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(path),
        "-vf", f"fps=1,scale={GRID}:{GRID},format=gray",
        "-f", "rawvideo", "-",
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = GRID * GRID
    i = 0
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield i, np.frombuffer(buf, dtype=np.uint8).reshape(GRID, GRID).astype(np.float32)
        i += 1
    p.stdout.close()
    p.wait()


def score_recording(manifest_rows, keep_redout):
    """Return list of per-second dicts across the whole timeline."""
    per_sec = []
    prev = None
    for r in manifest_rows:
        path = r["path"]
        dur = float(r["duration_sec"])
        t0 = float(r["timeline_start_sec"])
        print(f"  scanning {r['file']} ({sec_to_clock(dur)}) ...", file=sys.stderr)
        local_prev = prev
        count = 0
        for i, fr in sample_frames(path):
            if i >= int(dur) + 1:
                break
            corners = np.concatenate([
                fr[:CORNER, :CORNER].ravel(), fr[:CORNER, -CORNER:].ravel(),
                fr[-CORNER:, :CORNER].ravel(), fr[-CORNER:, -CORNER:].ravel(),
            ])
            corner_mean = float(corners.mean())
            frame_mean = float(fr.mean())
            motion = float(np.abs(fr - local_prev).mean()) if local_prev is not None else 99.0
            local_prev = fr

            scope_out = corner_mean > CORNER_BRIGHT
            no_signal = frame_mean < FRAME_DARK
            # "Red-out": lens pressed to mucosa — dark but reddish. On a grayscale
            # near-black frame we can't see hue, so we treat very-dark as no_signal
            # UNLESS --keep-redout, which keeps short dark spans (handled downstream).
            per_sec.append({
                "timeline_sec": round(t0 + i, 3),
                "source_file": r["file"], "src_sec": i,
                "corner_mean": round(corner_mean, 2),
                "frame_mean": round(frame_mean, 2),
                "motion": round(motion, 3),
                "scope_out": scope_out, "no_signal": no_signal,
            })
            count += 1
        prev = local_prev
    per_sec.sort(key=lambda d: d["timeline_sec"])
    return per_sec


def classify(per_sec, profile, keep_redout):
    """Mark each second keep/remove with a reason, applying idle-run logic."""
    mt = profile["motion_thresh"]
    min_idle = profile["min_idle_sec"]
    n = len(per_sec)
    reason = [None] * n  # None => keep

    for i, d in enumerate(per_sec):
        if d["scope_out"]:
            reason[i] = "scope-out"
        elif d["no_signal"]:
            reason[i] = "no-signal"

    # Idle: runs of low motion among still-kept seconds, lasting >= min_idle.
    i = 0
    while i < n:
        if reason[i] is None and per_sec[i]["motion"] < mt:
            j = i
            while j < n and reason[j] is None and per_sec[j]["motion"] < mt:
                j += 1
            if (j - i) >= min_idle:
                for k in range(i, j):
                    reason[k] = "idle"
            i = j
        else:
            i += 1

    if keep_redout:
        # Re-keep short no-signal/idle spans that are likely a lens-against-tissue
        # moment rather than true dead time (<= 4 s).
        i = 0
        while i < n:
            if reason[i] in ("no-signal", "idle"):
                j = i
                while j < n and reason[j] == reason[i]:
                    j += 1
                if (j - i) <= 4:
                    for k in range(i, j):
                        reason[k] = None
                i = j
            else:
                i += 1
    return reason


def build_segments(per_sec, reason, manifest_rows, fps):
    """Turn the per-second keep mask into padded, merged KEEP segments + REMOVED regions."""
    n = len(per_sec)
    # Source duration lookup for clamping handles within a chunk.
    dur_by_file = {r["file"]: float(r["duration_sec"]) for r in manifest_rows}

    # Contiguous keep runs (by timeline second).
    keeps = []
    i = 0
    while i < n:
        if reason[i] is None:
            j = i
            while j < n and reason[j] is None:
                j += 1
            keeps.append((i, j - 1))  # inclusive second indices
            i = j
        else:
            i += 1

    # Convert to source-relative spans with handles, splitting if a run crosses files.
    segs = []
    for a, b in keeps:
        run = per_sec[a:b + 1]
        # split where the source file changes
        start = 0
        for idx in range(1, len(run) + 1):
            if idx == len(run) or run[idx]["source_file"] != run[start]["source_file"]:
                chunk = run[start:idx]
                f = chunk[0]["source_file"]
                s_in = chunk[0]["src_sec"] - HANDLE_SEC
                s_out = chunk[-1]["src_sec"] + 1 + HANDLE_SEC  # +1: second covers its span
                s_in = max(0.0, s_in)
                s_out = min(dur_by_file.get(f, s_out), s_out)
                if s_out - s_in >= MIN_KEEP_SEC:
                    segs.append({"source_file": f, "src_in": s_in, "src_out": s_out})
                start = idx

    # Assign timeline positions sequentially.
    tl = 0.0
    keep_rows = []
    for k, sg in enumerate(segs, 1):
        d = sg["src_out"] - sg["src_in"]
        keep_rows.append({
            "segment": k, "source_file": sg["source_file"],
            "src_in_tc": sec_to_tc(sg["src_in"], fps),
            "src_out_tc": sec_to_tc(sg["src_out"], fps),
            "src_in_sec": round(sg["src_in"], 2), "src_out_sec": round(sg["src_out"], 2),
            "duration_sec": round(d, 2), "timeline_in_tc": sec_to_tc(tl, fps),
        })
        tl += d

    # Removed regions: contiguous same-reason runs.
    removed = []
    i = 0
    while i < n:
        if reason[i] is not None:
            j = i
            while j < n and reason[j] == reason[i]:
                j += 1
            removed.append({
                "removed_start_sec": round(per_sec[i]["timeline_sec"], 1),
                "removed_end_sec": round(per_sec[j - 1]["timeline_sec"] + 1, 1),
                "duration_sec": round((j - i), 1),
                "reason": reason[i], "approx_source": per_sec[i]["source_file"],
            })
            i = j
        else:
            i += 1
    return keep_rows, removed, tl


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True, help="manifest.csv from align_chunks.py")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--name", default="surgical", help="prefix for output files")
    ap.add_argument("--profile", choices=list(PROFILES), default="balanced")
    ap.add_argument("--keep-redout", action="store_true",
                    help="keep short dark spans (lens against tissue) instead of cutting")
    ap.add_argument("--fps", default=None, help="override fps, e.g. 30000/1001 or 25")
    args = ap.parse_args()

    with open(args.manifest) as f:
        manifest_rows = list(csv.DictReader(f))
    if not manifest_rows:
        sys.exit("Empty manifest.")
    fps = Fraction(args.fps) if args.fps else Fraction(manifest_rows[0].get("fps") or "30000/1001")
    os.makedirs(args.outdir, exist_ok=True)

    print(f"Scoring {len(manifest_rows)} chunk(s), profile={args.profile} ...", file=sys.stderr)
    per_sec = score_recording(manifest_rows, args.keep_redout)
    reason = classify(per_sec, PROFILES[args.profile], args.keep_redout)
    keep_rows, removed, tl = build_segments(per_sec, reason, manifest_rows, fps)

    base = os.path.join(args.outdir, args.name)
    with open(base + "_per_second.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_sec[0].keys()))
        w.writeheader(); w.writerows(per_sec)
    with open(base + "_KEEP_segments.csv", "w", newline="") as f:
        cols = ["segment", "source_file", "src_in_tc", "src_out_tc",
                "src_in_sec", "src_out_sec", "duration_sec", "timeline_in_tc"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(keep_rows)
    with open(base + "_REMOVED_regions.csv", "w", newline="") as f:
        cols = ["removed_start_sec", "removed_end_sec", "duration_sec", "reason", "approx_source"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(removed)

    total = len(per_sec)
    removed_sec = sum(r["duration_sec"] for r in removed)
    by_reason = {}
    for r in removed:
        by_reason[r["reason"]] = by_reason.get(r["reason"], 0) + r["duration_sec"]
    print(f"\n  Sampled {total} s ({sec_to_clock(total)})")
    print(f"  KEPT  : {sec_to_clock(tl)} across {len(keep_rows)} segments")
    pct = (removed_sec / total * 100) if total else 0
    print(f"  REMOVED: {sec_to_clock(removed_sec)} ({pct:.0f}%) -> " +
          ", ".join(f"{k} {v/60:.1f}m" for k, v in sorted(by_reason.items())))
    print(f"  Wrote KEEP/REMOVED/per-second CSVs to {args.outdir}")


if __name__ == "__main__":
    main()
