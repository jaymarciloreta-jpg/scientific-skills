#!/usr/bin/env python3
"""Prepare a local visual cut review, then apply explicit decisions to a KEEP list."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from fractions import Fraction

from common import read_manifest, write_keeps, run
from detect_deadtime import score_recording, classify, PROFILES


def fingerprint(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def merge(spans):
    result = []
    for start, end in sorted(spans):
        if result and start <= result[-1][1]:
            result[-1][1] = max(end, result[-1][1])
        else:
            result.append([start, end])
    return result


def subtract(start, end, cuts):
    result, cursor = [], start
    for a, b in merge(cuts):
        a, b = max(start, a), min(end, b)
        if b <= cursor or a >= end:
            continue
        if a > cursor:
            result.append((cursor, a))
        cursor = max(cursor, b)
    if cursor < end:
        result.append((cursor, end))
    return result


def candidates(scores, reasons, durations):
    out, i = [], 0
    while i < len(scores):
        if reasons[i] is None:
            i += 1; continue
        first, reason = scores[i], reasons[i]
        j = i + 1
        while (j < len(scores) and reasons[j] == reason
               and scores[j]['source_file'] == first['source_file']
               and scores[j]['src_sec'] == scores[j-1]['src_sec'] + 1):
            j += 1
        start, end = first['src_sec'], min(durations[first['source_file']], scores[j-1]['src_sec']+1)
        if end > start:
            out.append(dict(id=f"cut-{len(out)+1:05d}", file=first['source_file'],
                            start=start, end=end, reason=reason, action='keep'))
        i = j
    return out


def validate_protected(protected, durations):
    for p in protected:
        if p['file'] not in durations:
            raise ValueError('Protected interval has unknown clip ID')
        a, b = float(p['start']), float(p['end'])
        if not math.isfinite(a+b) or not 0 <= a < b <= durations[p['file']]:
            raise ValueError('Invalid protected interval')


def apply_decisions(session, decisions):
    if decisions.get('session_id') != session['session_id']:
        raise ValueError('Decisions belong to a different review session')
    edits = decisions.get('decisions', [])
    if len(edits) != len(session['candidates']) or len({e['id'] for e in edits}) != len(edits):
        raise ValueError('Decisions must contain each candidate exactly once')
    by_id = {c['id']: c for c in session['candidates']}
    cuts = {}
    for edit in edits:
        if edit['id'] not in by_id or edit['action'] not in {'keep','remove'}:
            raise ValueError('Unknown candidate or action')
        c = by_id[edit['id']]
        a, b = float(edit['start']), float(edit['end'])
        if not math.isfinite(a+b) or not c['start'] <= a < b <= c['end']:
            raise ValueError('Adjusted cut must remain inside its proposed interval')
        if edit['action'] == 'remove':
            # Cut inward to frame boundaries so rounding cannot eat protected context.
            fps = float(Fraction(session['fps']))
            a, b = math.ceil(a*fps)/fps, math.floor(b*fps)/fps
            protected = [(p['start'],p['end']) for p in session['protected'] if p['file']==c['file']]
            for left, right in subtract(a,b,protected):
                left, right = math.ceil(left*fps)/fps, math.floor(right*fps)/fps
                if right > left:
                    cuts.setdefault(c['file'], []).append((left,right))
    spans=[]
    for row in session['manifest']:
        spans.extend((row['file'], a, b) for a,b in subtract(0,float(row['duration_sec']),cuts.get(row['file'],[])))
    return spans


def prepare(args):
    rows = read_manifest(args.manifest)
    for row in rows:
        stat=Path(row["path"]).stat()
        row["source_size"]=stat.st_size;row["source_mtime_ns"]=stat.st_mtime_ns
    rates = {r['fps'] for r in rows}
    if len(rates)!=1:
        raise ValueError('Mixed frame rates: normalize media to one constant frame rate before review')
    if any(str(r.get('variable_rate','')).lower()=='true' for r in rows):
        raise ValueError('Potential variable frame rate: normalize before review')
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    if (out/'session.json').exists():
        raise ValueError('Review directory already has a session; choose a new directory')
    durations={r['file']:float(r['duration_sec']) for r in rows}
    protected=json.loads(Path(args.protect).read_text()) if args.protect else []
    validate_protected(protected,durations)
    scores=score_recording(rows,True)
    if not scores:raise ValueError('No frames decoded')
    reasons=classify(scores,PROFILES[args.profile],False)
    cs=candidates(scores,reasons,durations)
    session=dict(version=2,manifest=rows,fps=rows[0]['fps'],profile=args.profile,
                 protected=protected,candidates=cs)
    session['session_id']=fingerprint(session)
    media=out/'previews';media.mkdir(exist_ok=True)
    paths={r['file']:r['path'] for r in rows}
    for c in cs:
        mid=(c['start']+c['end'])/2
        preview_start=max(0,mid-4)
        preview_duration=min(8,durations[c['file']]-preview_start)
        run(['ffmpeg','-v','error','-n','-ss',str(mid),'-i',paths[c['file']],
             '-frames:v','1','-vf','scale=480:-2',str(media/(c['id']+'.jpg'))])
        run(['ffmpeg','-v','error','-n','-ss',str(preview_start),'-i',paths[c['file']],
             '-t',str(preview_duration),'-an','-vf','scale=640:-2',
             '-c:v','libx264','-preset','veryfast','-crf','26','-pix_fmt','yuv420p',
             '-movflags','+faststart',str(media/(c['id']+'.mp4'))])
        c['preview_start']=preview_start
    # Include preview positions in session identity so the saved payload is reproducible.
    session['session_id']=fingerprint({k:v for k,v in session.items() if k!='session_id'})
    (out/'session.json').write_text(json.dumps(session,indent=2))
    with (out/'scores.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(scores[0]));writer.writeheader();writer.writerows(scores)
    write_keeps([(r['file'],0,float(r['duration_sec'])) for r in rows],out/'KEEP_unreviewed.csv',Fraction(session['fps']))
    template=Path(__file__).with_name('review_template.html').read_text()
    (out/'review.html').write_text(template.replace('/*SESSION*/{}',json.dumps(session).replace('<','\\u003c')))
    print(f"Review {len(cs)} candidates in {out/'review.html'}. All footage stays kept until explicitly removed.")


def finalize(args):
    session=json.loads(Path(args.session).read_text()); decisions=json.loads(Path(args.decisions).read_text())
    for row in session['manifest']:
        stat=Path(row['path']).stat()
        if stat.st_size!=row['source_size'] or stat.st_mtime_ns!=row['source_mtime_ns']:
            raise ValueError('Source changed since review; prepare a new session')
    spans=apply_decisions(session,decisions)
    if not spans:raise ValueError('Review would remove all footage')
    out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
    for name in ['KEEP_reviewed.csv','review_audit.json']:
        if (out/name).exists():raise ValueError('Output exists; choose a new directory')
    write_keeps(spans,out/'KEEP_reviewed.csv',Fraction(session['fps']))
    audit=dict(session_id=session['session_id'],decisions=decisions['decisions'],
               protected=session['protected'],source_duration=sum(float(r['duration_sec']) for r in session['manifest']),
               kept_duration=sum(b-a for _,a,b in spans))
    (out/'review_audit.json').write_text(json.dumps(audit,indent=2))
    print(out/'KEEP_reviewed.csv')


def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='command',required=True)
    prep=sub.add_parser('prepare');prep.add_argument('--manifest',required=True);prep.add_argument('--outdir',required=True)
    prep.add_argument('--profile',choices=list(PROFILES),default='conservative');prep.add_argument('--protect',help='JSON list of {file,start,end} in source seconds')
    final=sub.add_parser('finalize');final.add_argument('--session',required=True);final.add_argument('--decisions',required=True);final.add_argument('--outdir',required=True)
    args=ap.parse_args();(prepare if args.command=='prepare' else finalize)(args)

if __name__=='__main__':main()
