#!/usr/bin/env python3
"""Export a reviewed KEEP CSV as Final Cut Pro 7 XML (.xml) for Premiere.

FCPXML is not Premiere's native interchange format. This exporter uses xmeml v5.
A video-only CMX3600 EDL is supplied as a fallback; XML includes mono/stereo audio.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import xml.etree.ElementTree as ET
from common import read_keeps, read_manifest, probe_basics, sec_to_tc


def tag(parent, name, value=None, **attrs):
    node=ET.SubElement(parent,name,attrs)
    if value is not None:node.text=str(value)
    return node


def rate(parent, fps):
    node=tag(parent,'rate');tag(node,'timebase',round(float(fps)))
    tag(node,'ntsc','TRUE' if fps.denominator==1001 else 'FALSE')


def validate(keeps, paths):
    info={}
    for k in keeps:
        fn=k['source_file']
        if fn not in paths:raise ValueError(f'Unknown source ID: {fn}')
        if fn not in info:info[fn]=probe_basics(paths[fn])
        b=info[fn]
        if float(k['src_out_sec']) > b['duration']+1/float(b['fps']):raise ValueError('Cut exceeds source duration')
        if b['variable_rate']:raise ValueError('Potential variable frame rate: normalize before export')
        if b['audio_channels']>2:raise ValueError('Only mono/stereo audio is supported; normalize multichannel audio first')
    formats={(b['fps'],b['width'],b['height']) for b in info.values()}
    if len(formats)!=1:raise ValueError('Mixed frame rates or dimensions: normalize before export')
    fps=next(iter(info.values()))['fps']
    if fps not in {Fraction(x) for x in ('24','25','30','50','60','24000/1001','30000/1001','60000/1001')}:
        raise ValueError(f'Unsupported interchange frame rate: {fps}')
    return info,fps


def write_xml(keeps,paths,out,title,info,fps):
    frames=lambda seconds:round(float(seconds)*float(fps))
    durations=[frames(k['src_out_sec'])-frames(k['src_in_sec']) for k in keeps]
    if any(d<=0 for d in durations):raise ValueError('Sub-frame or empty cut')
    first=next(iter(info.values()));root=ET.Element('xmeml',version='5')
    seq=tag(root,'sequence',id='sequence-1');tag(seq,'name',title);tag(seq,'duration',sum(durations));rate(seq,fps)
    media=tag(seq,'media');video=tag(media,'video');fmt=tag(video,'format');sample=tag(fmt,'samplecharacteristics')
    rate(sample,fps)
    for name,val in [('width',first['width']),('height',first['height']),('anamorphic','FALSE'),('pixelaspectratio','square'),('fielddominance','none')]:tag(sample,name,val)
    vtrack=tag(video,'track');audio=tag(media,'audio');tag(audio,'numOutputChannels',2)
    afmt=tag(audio,'format');asc=tag(afmt,'samplecharacteristics');tag(asc,'depth',16);tag(asc,'samplerate',48000)
    atracks=[tag(audio,'track') for _ in range(2)];acount=[0,0];offset=0;defined=set()
    asset_ids={name:f'file-{i}' for i,name in enumerate(info,1)}
    for i,(k,duration) in enumerate(zip(keeps,durations),1):
        fn=k['source_file'];b=info[fn];channels=b['audio_channels']
        links=[(f'v-{i}','video',1,i)]
        for channel in range(channels):
            acount[channel]+=1;links.append((f'a-{i}-{channel+1}','audio',channel+1,acount[channel]))
        for clip_id,kind,trackindex,clipindex in links:
            parent=vtrack if kind=='video' else atracks[trackindex-1]
            clip=tag(parent,'clipitem',id=clip_id);tag(clip,'name',Path(paths[fn]).name)
            tag(clip,'enabled','TRUE');tag(clip,'duration',frames(b['duration']));rate(clip,fps)
            for name,val in [('start',offset),('end',offset+duration),('in',frames(k['src_in_sec'])),('out',frames(k['src_out_sec']))]:tag(clip,name,val)
            file=tag(clip,'file',id=asset_ids[fn])
            if fn not in defined:
                defined.add(fn);tag(file,'name',Path(paths[fn]).name);tag(file,'pathurl',Path(paths[fn]).resolve().as_uri());rate(file,fps)
                tag(file,'duration',frames(b['duration']));tc=tag(file,'timecode');rate(tc,fps);tag(tc,'string','00:00:00:00');tag(tc,'frame',0);tag(tc,'displayformat','NDF')
                fm=tag(file,'media');fv=tag(fm,'video');sc=tag(fv,'samplecharacteristics');rate(sc,fps)
                for name,val in [('width',b['width']),('height',b['height']),('pixelaspectratio','square'),('fielddominance','none')]:tag(sc,name,val)
                if channels:
                    fa=tag(fm,'audio');tag(fa,'channelcount',channels);sc=tag(fa,'samplecharacteristics');tag(sc,'depth',16);tag(sc,'samplerate',b['audio_rate'])
            source=tag(clip,'sourcetrack');tag(source,'mediatype',kind);tag(source,'trackindex',trackindex if kind=='audio' else 1)
            for linked_id,linked_kind,linked_track,linked_index in links:
                link=tag(clip,'link');tag(link,'linkclipref',linked_id);tag(link,'mediatype',linked_kind);tag(link,'trackindex',linked_track);tag(link,'clipindex',linked_index)
        offset+=duration
    ET.indent(root)
    ET.ElementTree(root).write(out,encoding='utf-8',xml_declaration=True)
    ET.parse(out)


def write_edl(keeps,out,title,fps):
    if len(keeps)>999:raise ValueError('CMX3600 EDL supports at most 999 events here')
    lines=[f'TITLE: {title.replace(chr(10), " ")}', 'FCM: NON-DROP FRAME'];tl=0
    for i,k in enumerate(keeps,1):
        start,end=round(float(k['src_in_sec'])*fps),round(float(k['src_out_sec'])*fps)
        duration=end-start
        lines.append(f'{i:03d}  AX       V     C        {sec_to_tc(start/fps,fps)} {sec_to_tc(end/fps,fps)} {sec_to_tc(tl/fps,fps)} {sec_to_tc((tl+duration)/fps,fps)}')
        lines.append('* FROM CLIP NAME: '+k['source_file'].replace('\n',' '));tl+=duration
    Path(out).write_text('\n'.join(lines)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--keep',required=True);ap.add_argument('--manifest',required=True)
    ap.add_argument('--outdir',required=True);ap.add_argument('--name',default='surgical_ROUGH_CUT');ap.add_argument('--title',default='Reviewed surgical rough cut')
    args=ap.parse_args()
    if Path(args.name).name!=args.name:raise ValueError('Name must be a filename prefix')
    keeps=read_keeps(args.keep);paths={r['file']:r['path'] for r in read_manifest(args.manifest)};info,fps=validate(keeps,paths)
    out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True);xml=out/(args.name+'.xml');edl=out/(args.name+'.edl')
    if xml.exists() or edl.exists():raise ValueError('Output already exists; choose a new name')
    write_xml(keeps,paths,xml,args.title,info,fps)
    if len(keeps)<=999:write_edl(keeps,edl,args.title,fps)
    print(f'Wrote {xml}. Verify media relinking, audio, and cut boundaries in Premiere.')

if __name__=='__main__':main()
