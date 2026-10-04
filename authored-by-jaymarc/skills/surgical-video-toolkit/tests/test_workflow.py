import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from align_chunks import collect, parse_time
from common import write_keeps, read_keeps, probe_basics
from review_cuts import apply_decisions, candidates
from extract_markers import timeline_spans, parse_ts, render_spans
from build_timeline import validate, write_xml

class Workflow(unittest.TestCase):
    def test_same_name_different_contents(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for folder in ['a','b','c']:(p/folder).mkdir()
            (p/'a/clip.mp4').write_bytes(b'one');(p/'b/clip.mp4').write_bytes(b'two');(p/'c/copy.mp4').write_bytes(b'one')
            result=collect([p/'a',p/'b',p/'c']);self.assertEqual(len(result),2)
            self.assertEqual(len(set(result)),2)
    def test_timezone_comparable(self):
        self.assertEqual(parse_time('2025-01-01T12:00:00Z'),parse_time('2025-01-01T07:00:00-0500'))
    def test_protected_and_adjusted_removal(self):
        session={'session_id':'x','fps':'25','manifest':[{'file':'a','duration_sec':10}],
                 'candidates':[{'id':'1','file':'a','start':0,'end':10}], 'protected':[{'file':'a','start':4,'end':6}]}
        decisions={'session_id':'x','decisions':[{'id':'1','action':'remove','start':2,'end':8}]}
        self.assertEqual(apply_decisions(session,decisions),[('a',0,2),('a',4,6),('a',8,10)])
        decisions['decisions'][0]['action']='keep'
        self.assertEqual(apply_decisions(session,decisions),[('a',0,10)])
        decisions['session_id']='other'
        with self.assertRaises(ValueError):apply_decisions(session,decisions)
    def test_nan_and_missing_decisions(self):
        s={'session_id':'x','candidates':[{'id':'1','file':'a','start':0,'end':10}]}
        for decisions in [[],[{'id':'1','action':'remove','start':float('nan'),'end':2}]]:
            with self.assertRaises(ValueError):apply_decisions(s,{'session_id':'x','decisions':decisions})
    def test_timeline_crosses_cuts_and_files(self):
        keeps=[{'source_file':'a','src_in_sec':0,'duration_sec':2},{'source_file':'a','src_in_sec':10,'duration_sec':2},{'source_file':'b','src_in_sec':5,'duration_sec':3}]
        self.assertEqual(timeline_spans(1,4,keeps),[('a',1,1),('a',10,2),('b',5,1)])
        self.assertEqual(timeline_spans(2,1,keeps),[('a',10,1)])
        with self.assertRaises(ValueError):timeline_spans(7,1,keeps)
    def test_fractional_candidate_tail(self):
        rows=[{'source_file':'a','src_sec':0},{'source_file':'a','src_sec':1},{'source_file':'b','src_sec':0}]
        cs=candidates(rows,['idle']*3,{'a':1.3,'b':.5})
        self.assertEqual([(x['start'],x['end']) for x in cs],[(0,1.3),(0,.5)])
    def test_xml_escape_rate_dimensions_audio(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);source=p/'A & "B".mp4';source.touch();out=p/'edit.xml'
            keeps=[dict(source_file='a',src_in_sec=1,src_out_sec=2,duration_sec=1)]
            info={'a':dict(duration=4,fps=Fraction(25),width=640,height=360,audio_channels=2,audio_rate=48000)}
            write_xml(keeps,{'a':str(source)},out,'A & "B"',info,Fraction(25));root=ET.parse(out)
            self.assertEqual(root.findtext('.//sequence/name'),'A & "B"')
            self.assertEqual(root.findtext('.//sequence/media/video/format/samplecharacteristics/width'),'640')
            self.assertEqual(len(root.findall('.//sequence/media/audio/track/clipitem')),2)
            self.assertEqual(root.findtext('.//sequence/media/video/track/clipitem/in'),'25')
    def test_keep_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'keep.csv';write_keeps([('a',0,1),('a',.5,2)],p,Fraction(25))
            with self.assertRaises(ValueError):read_keeps(p)
    def test_timestamps(self):
        self.assertEqual(parse_ts('1:02:03.5'),3723.5)
        for bad in ['-1','nan','1:80','1:2:3:4']:
            with self.assertRaises(ValueError):parse_ts(bad)

class MediaIntegration(unittest.TestCase):
    def test_synthetic_highlight_excludes_removed_red_frames(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);source=p/'source.mp4'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=blue:s=160x90:r=25:d=1','-f','lavfi','-i','color=red:s=160x90:r=25:d=1','-f','lavfi','-i','color=green:s=160x90:r=25:d=1','-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=3','-filter_complex','[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]','-map','[v]','-map','3:a','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(source)],check=True)
            keeps=[dict(source_file='a',src_in_sec=0,src_out_sec=1,duration_sec=1),dict(source_file='a',src_in_sec=2,src_out_sec=3,duration_sec=1)]
            out=p/'highlight.mp4';render_spans(timeline_spans(.5,1,keeps),{'a':str(source)},out,width=160,height=90)
            b=probe_basics(out);self.assertAlmostEqual(b['duration'],1,delta=.12);self.assertEqual(b['audio_channels'],2)
            raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(out),'-vf','scale=1:1','-pix_fmt','rgb24','-f','rawvideo','-'])
            pixels=list(zip(raw[0::3],raw[1::3],raw[2::3]))
            self.assertFalse(any(r>100 and r>g*1.5 and r>b*1.5 for r,g,b in pixels))
            with self.assertRaises(ValueError):render_spans([('a',0,1)],{'a':str(source)},out)

if __name__=='__main__':unittest.main()
