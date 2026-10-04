#!/usr/bin/env python3
"""
build_timeline.py — turn a KEEP_segments.csv into a Premiere-ready timeline.

Produces two files that describe the SAME cut list:
  * .fcpxml — a sequence Premiere can import directly (File > Import). It carries
    real media references so Premiere can relink to the footage automatically.
  * .edl    — a CMX3600 edit decision list as a backup. Some Premiere versions
    choke on a given FCPXML; the EDL always imports and relinks by clip name.

Nothing is rendered or copied. These are tiny text files; the footage stays put.
The surgeon/editor reviews and fine-tunes in Premiere from here.

Usage
-----
  python build_timeline.py --keep KEEP_segments.csv --manifest manifest.csv \
      --outdir OUT --name Medina_sinus --title "Medina sinus - dead-time removed"
"""
import argparse
import csv
import os
from fractions import Fraction

from common import sec_to_tc, fcpxml_time, probe_basics


def load(keep_csv, manifest_csv):
    with open(keep_csv) as f:
        keeps = list(csv.DictReader(f))
    paths = {}
    if manifest_csv and os.path.exists(manifest_csv):
        with open(manifest_csv) as f:
            for r in csv.DictReader(f):
                paths[r["file"]] = r["path"]
    return keeps, paths


def write_edl(keeps, out, title, fps):
    lines = [f"TITLE: {title.upper()}", "FCM: NON-DROP FRAME"]
    tl = 0.0
    for i, k in enumerate(keeps, 1):
        d = float(k["duration_sec"])
        rec_in = sec_to_tc(tl, fps)
        rec_out = sec_to_tc(tl + d, fps)
        lines.append(f"{i:03d}  AX       V     C        "
                     f"{k['src_in_tc']} {k['src_out_tc']} {rec_in} {rec_out}")
        lines.append(f"* FROM CLIP NAME: {k['source_file']}")
        tl += d
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")


def write_fcpxml(keeps, paths, out, title, fps):
    # One asset per unique source file.
    files = []
    for k in keeps:
        if k["source_file"] not in files:
            files.append(k["source_file"])

    frame_dur = f"{fps.denominator}/{fps.numerator}s"  # e.g. 1001/30000s
    res = ['<?xml version="1.0" encoding="UTF-8"?>', "<!DOCTYPE fcpxml>",
           '<fcpxml version="1.8">', "  <resources>",
           f'    <format id="r1" name="FFVideoFormat1080p2997" '
           f'frameDuration="{frame_dur}" width="1920" height="1080"/>']
    asset_id = {}
    rid = 2
    for fn in files:
        path = paths.get(fn, fn)
        dur = "0s"
        if os.path.exists(path):
            b = probe_basics(path)
            dur = fcpxml_time(b["duration"], fps)
        asset_id[fn] = f"r{rid}"
        src = "file://" + os.path.abspath(path).replace(" ", "%20")
        res.append(f'    <asset id="r{rid}" name="{fn}" start="0s" hasVideo="1" '
                   f'format="r1" videoSources="1" duration="{dur}">')
        res.append(f'      <media-rep kind="original-media" src="{src}"/>')
        res.append("    </asset>")
        rid += 1
    res.append("  </resources>")

    # Spine of clips laid end to end.
    res += ["  <library>", "    <event name=\"%s\">" % title,
            f'      <project name="{title}">',
            f'        <sequence format="r1" tcStart="0s" tcFormat="NDF">',
            "          <spine>"]
    offset = 0.0
    for i, k in enumerate(keeps, 1):
        d = float(k["duration_sec"])
        start = float(k["src_in_sec"])
        res.append(
            f'            <asset-clip name="{k["source_file"]} cut{i:03d}" '
            f'ref="{asset_id[k["source_file"]]}" '
            f'offset="{fcpxml_time(offset, fps)}" '
            f'start="{fcpxml_time(start, fps)}" '
            f'duration="{fcpxml_time(d, fps)}" format="r1"/>')
        offset += d
    res += ["          </spine>", "        </sequence>", "      </project>",
            "    </event>", "  </library>", "</fcpxml>"]
    with open(out, "w") as f:
        f.write("\n".join(res) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keep", required=True, help="KEEP_segments.csv from detect_deadtime.py")
    ap.add_argument("--manifest", help="manifest.csv (for real media paths in FCPXML)")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--name", default="surgical_ROUGH_CUT", help="output filename prefix")
    ap.add_argument("--title", default="Surgical rough cut - dead-time removed")
    ap.add_argument("--fps", default=None)
    args = ap.parse_args()

    keeps, paths = load(args.keep, args.manifest)
    if not keeps:
        raise SystemExit("KEEP csv is empty.")
    fps = Fraction(args.fps) if args.fps else Fraction("30000/1001")
    os.makedirs(args.outdir, exist_ok=True)
    edl = os.path.join(args.outdir, args.name + ".edl")
    fcp = os.path.join(args.outdir, args.name + ".fcpxml")
    write_edl(keeps, edl, args.title, fps)
    write_fcpxml(keeps, paths, fcp, args.title, fps)
    total = sum(float(k["duration_sec"]) for k in keeps)
    print(f"Built timeline: {len(keeps)} clips, {total/60:.1f} min")
    print(f"  {fcp}")
    print(f"  {edl}")


if __name__ == "__main__":
    main()
