#!/usr/bin/env python3
"""Render source or reviewed-timeline highlights without restoring removed footage."""
import argparse
import math
from fractions import Fraction
from pathlib import Path
import tempfile
from common import run, probe_basics, read_manifest, read_keeps


def parse_ts(s):
    parts=str(s).split(':')
    if not 1<=len(parts)<=3:raise ValueError('Use SS, MM:SS, or HH:MM:SS')
    values=[float(x) for x in parts]
    if any(not math.isfinite(x) or x<0 for x in values) or any(x>=60 for x in values[1:]):raise ValueError('Invalid timestamp')
    result=0
    for x in values:result=result*60+x
    return result


def timeline_spans(start,length,keeps):
    total=sum(float(k['duration_sec']) for k in keeps)
    if not math.isfinite(start+length) or start<0 or length<=0 or start>=total:raise ValueError('Highlight is outside the timeline')
    end=min(start+length,total);offset=0;spans=[]
    for k in keeps:
        duration=float(k['duration_sec']);a=max(start,offset);b=min(end,offset+duration)
        if b>a:spans.append((k['source_file'],float(k['src_in_sec'])+a-offset,b-a))
        offset+=duration
    return spans


def render_spans(spans,paths,out,width=1920,height=1080):
    out=Path(out)
    if out.exists():raise ValueError('Output already exists')
    if any(out.resolve()==Path(p).resolve() for p in paths.values()):raise ValueError('Output cannot overwrite a source')
    info={fn:probe_basics(paths[fn]) for fn,_,_ in spans}
    fps=next(iter(info.values()))['fps']
    # Normalize segments to the first source's rate and a stereo 48 kHz audio track.
    # Silent sources get silence only when at least one selected source contains audio.
    has_audio=any(b['audio_channels'] for b in info.values())
    with tempfile.TemporaryDirectory(prefix='surgical-highlight-') as tmp:
        parts=[]
        for i,(fn,start,length) in enumerate(spans):
            b=info[fn]
            if start<0 or length<=0 or start+length>b['duration']+1/float(b['fps']):raise ValueError('Highlight exceeds source bounds')
            part=Path(tmp)/f'{i:05d}.mp4';parts.append(part)
            cmd=['ffmpeg','-v','error','-n','-ss',str(start),'-i',paths[fn]]
            if has_audio and not b['audio_channels']:cmd+=['-f','lavfi','-i','anullsrc=channel_layout=stereo:sample_rate=48000']
            cmd+=['-t',str(length),'-map','0:v:0','-vf',f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}',
                  '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p']
            if has_audio:cmd+=['-map','0:a:0' if b['audio_channels'] else '1:a:0','-c:a','aac','-ar','48000','-ac','2','-b:a','160k']
            else:cmd+=['-an']
            run(cmd+[str(part)])
        listing=Path(tmp)/'parts.txt';listing.write_text(''.join(f"file '{p.name}'\n" for p in parts))
        out.parent.mkdir(parents=True,exist_ok=True)
        run(['ffmpeg','-v','error','-n','-f','concat','-safe','1','-i',str(listing),'-c','copy','-movflags','+faststart',str(out)])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--outdir',required=True);ap.add_argument('--manifest',required=True)
    ap.add_argument('--keep');ap.add_argument('--length',type=float,default=30);ap.add_argument('--center',action='store_true');ap.add_argument('--prefix',default='Marker')
    ap.add_argument('--at',action='append',default=[]);ap.add_argument('--timeline-at',action='append',default=[])
    args=ap.parse_args()
    if not math.isfinite(args.length) or args.length<=0:raise ValueError('Length must be positive')
    if Path(args.prefix).name!=args.prefix:raise ValueError('Prefix must be a filename')
    rows=read_manifest(args.manifest);paths={r['file']:r['path'] for r in rows};jobs=[]
    for value in args.at:
        fn,t=value.split('=',1)
        if fn not in paths:raise ValueError('Use a clip ID from manifest.csv')
        t=parse_ts(t);duration=probe_basics(paths[fn])['duration']
        if t>=duration:raise ValueError('Marker outside source')
        start=max(0,t-args.length/2) if args.center else t
        jobs.append([(fn,start,min(args.length,duration-start))])
    for value in args.timeline_at:
        if not args.keep:raise ValueError('--timeline-at requires --keep')
        t=parse_ts(value);keeps=read_keeps(args.keep)
        if t>=sum(float(k['duration_sec']) for k in keeps):raise ValueError('Marker outside timeline')
        start=max(0,t-args.length/2) if args.center else t
        jobs.append(timeline_spans(start,args.length,keeps))
    if not jobs:raise ValueError('Supply --at or --timeline-at')
    for i,spans in enumerate(jobs,1):
        out=Path(args.outdir)/f'{args.prefix}_{i:02d}.mp4';render_spans(spans,paths,out);print(out)

if __name__=='__main__':main()
