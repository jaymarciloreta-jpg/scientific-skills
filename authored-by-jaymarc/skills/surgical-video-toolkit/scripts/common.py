"""Shared helpers for the surgical-video-toolkit scripts.

Timecode here is 29.97 fps NON-DROP frame (HH:MM:SS:FF, frames 0-29), which is
what the surgical capture systems (e.g. Karl Storz / generic 1080p29.97 grabbers)
produce and what Premiere expects on import. If your footage is a different rate,
pass --fps and everything downstream stays consistent.
"""
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
    dur = float(info["format"].get("duration", 0.0))
    width = int(v["width"]) if v else 0
    height = int(v["height"]) if v else 0
    fps = DEFAULT_FPS
    if v and v.get("r_frame_rate") and v["r_frame_rate"] != "0/0":
        try:
            fps = Fraction(v["r_frame_rate"])
        except Exception:
            pass
    ctime = None
    for tags in (info["format"].get("tags", {}), (v or {}).get("tags", {})):
        if tags and tags.get("creation_time"):
            ctime = tags["creation_time"]
            break
    return {"duration": dur, "width": width, "height": height,
            "fps": fps, "creation_time": ctime}


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
