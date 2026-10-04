"""Shared helpers for the surgical-video-toolkit scripts.

Timecode here is 29.97 fps NON-DROP frame (HH:MM:SS:FF, frames 0-29), which is
what the surgical capture systems (e.g. Karl Storz / generic 1080p29.97 grabbers)
produce and what Premiere expects on import. If your footage is a different rate,
pass --fps and everything downstream stays consistent.
"""
import csv
import math
from pathlib import Path
import json
import subprocess
from fractions import Fraction

DEFAULT_FPS = Fraction(30000, 1001)  # 29.97 non-drop


def run(cmd):
    """Run a command, return stdout text. Raises on failure with stderr shown."""
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd))}\n{p.stderr[:2000]}")
    return p.stdout


def ffprobe_json(path):
    out = run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(path),
    ])
    return json.loads(out)


def probe_basics(path):
    """Return dict with duration (s), width, height, fps (Fraction), creation_time (str|None)."""
    info = ffprobe_json(path)
    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), None)
    if not v:
        raise ValueError(f"No video stream: {path}")
    dur = float(info["format"].get("duration", 0.0))
    if not math.isfinite(dur) or dur <= 0:
        raise ValueError(f"Invalid video duration: {path}")
    width = int(v["width"]) if v else 0
    height = int(v["height"]) if v else 0
    fps = DEFAULT_FPS
    if v and v.get("r_frame_rate") and v["r_frame_rate"] != "0/0":
        try:
            fps = Fraction(v["r_frame_rate"])
        except Exception:
            pass
    if fps <= 0:
        raise ValueError(f"Invalid frame rate: {path}")
    avg = Fraction(v.get("avg_frame_rate") or "0/1")
    variable_rate = avg > 0 and abs(float(avg - fps)) > 0.01
    audio = next((s for s in info["streams"] if s.get("codec_type") == "audio"), {})
    ctime = None
    for tags in (info["format"].get("tags", {}), (v or {}).get("tags", {})):
        if tags and tags.get("creation_time"):
            ctime = tags["creation_time"]
            break
    return {"duration": dur, "width": width, "height": height,
            "fps": fps, "creation_time": ctime, "variable_rate": variable_rate,
            "audio_channels": int(audio.get("channels", 0)),
            "audio_rate": int(audio.get("sample_rate", 48000))}


def sec_to_tc(seconds, fps=DEFAULT_FPS):
    """Seconds -> HH:MM:SS:FF non-drop timecode string."""
    fps = Fraction(fps)
    fps_int = int(round(float(fps)))  # 30 for 29.97
    total_frames = int(round(seconds * fps))
    f = total_frames % fps_int
    total_s = total_frames // fps_int
    s = total_s % 60
    m = (total_s // 60) % 60
    h = total_s // 3600
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


def sec_to_clock(seconds):
    """Seconds -> H:MM:SS for human-readable summaries."""
    s = int(round(seconds))
    return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def fcpxml_time(seconds, fps=DEFAULT_FPS):
    """Seconds -> FCPXML rational time string like '26996970/30000s'."""
    fps = Fraction(fps)
    num = int(round(seconds * fps)) * fps.denominator
    den = fps.numerator
    return f"{num}/{den}s"


def read_manifest(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("Empty manifest")
    ids = [r["file"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Ambiguous manifest IDs; regenerate with align_chunks.py")
    for r in rows:
        duration=float(r["duration_sec"])
        if not math.isfinite(duration) or duration <= 0 or Fraction(r["fps"]) <= 0:
            raise ValueError("Invalid manifest duration or frame rate")
        r["path"] = str(Path(r["path"]).resolve())
        if not Path(r["path"]).is_file():
            raise ValueError(f"Missing source: {r['path']}")
    return rows


def read_keeps(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("Empty KEEP list")
    previous = {}
    for r in rows:
        start, end = float(r["src_in_sec"]), float(r["src_out_sec"])
        duration = float(r["duration_sec"])
        if not all(math.isfinite(x) for x in (start, end, duration)) or start < 0 or end <= start:
            raise ValueError("Invalid KEEP interval")
        if abs(end-start-duration) > .001:
            raise ValueError("KEEP duration disagrees with source interval")
        if start < previous.get(r["source_file"], 0)-1e-6:
            raise ValueError("Overlapping or out-of-order KEEP intervals")
        previous[r["source_file"]] = end
    return rows


def write_keeps(spans, path, fps):
    rows, offset = [], 0.0
    for file, start, end in spans:
        start = round(start*float(fps))/float(fps)
        end = round(end*float(fps))/float(fps)
        if end <= start:
            continue
        rows.append(dict(segment=len(rows)+1, source_file=file,
                         src_in_sec=round(start, 9), src_out_sec=round(end, 9),
                         duration_sec=round(end-start, 9), src_in_tc=sec_to_tc(start,fps),
                         src_out_tc=sec_to_tc(end,fps), timeline_in_tc=sec_to_tc(offset,fps)))
        offset += end-start
    with open(path, "w", newline="") as f:
        cols = ["segment","source_file","src_in_sec","src_out_sec","duration_sec",
                "src_in_tc","src_out_tc","timeline_in_tc"]
        writer = csv.DictWriter(f, fieldnames=cols); writer.writeheader(); writer.writerows(rows)
    return rows
