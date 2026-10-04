import concurrent.futures, subprocess, pathlib, json, urllib.request, datetime, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
REPOS='''K-Dense-AI/scientific-agent-skills
ultralytics/skills
roboflow/computer-vision-skills
mist-medical/skills
NVIDIA-Medtech/medical-AI-skills
AminAlam/meddev-agent-skills
lukeoishi/engineering-agent-skills
jmwright/cadquery-llm-skill
flowful-ai/cad-skill
znlgis/opengis-skills
luckiday/vibe-hardware
IxTechCrypto/kicad-skills
sabas0ba/kicad_skills
dropio12/cherry-hardware-agent
Aditya-Tandon/claude-research-skills
zi-yue-1129/research-lab-skills
alirezarezvani/claude-skills
mindrally/skills
huggingface/skills
obra/superpowers
ArthurTorres11/opencode-setup
abwoo/nih-skill
wasserth/TotalSegmentator
pieper/slicer-skill
medmcp/medmcp-totalsegmentator
test1card/femis-skill
CUHK-AIM-Group/NeuroDiscovery
Bardli/ml-experiment-workflow
VeryMath/AI4Math-Computational-Mathematics
Cai-aa/CAE-Agent-Hub
remotion-dev/skills
heygen-com/hyperframes
phamthanhnghia/remotion-agent-skills
kissawang9-ai/science-video-director
anthropics/skills
elevenlabs/skills
runwayml/skills
'''.split()
def collect(repo):
    dest=ROOT/'sources'/repo.replace('/','--')
    entry={'repo':repo,'url':'https://github.com/'+repo,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        req=urllib.request.Request('https://api.github.com/repos/'+repo,headers={'User-Agent':'Skill-Catalog'})
        with urllib.request.urlopen(req,timeout=25) as f: meta=json.load(f)
        entry.update({k:meta.get(k) for k in ['full_name','stargazers_count','forks_count','pushed_at','archived','default_branch','description']})
        entry['license']=(meta.get('license') or {}).get('spdx_id','Unknown')
    except Exception as e:
        entry['metadata_error']=str(e)
        fallback=subprocess.run(['gh','api','repos/'+repo],capture_output=True,text=True) if shutil.which('gh') else None
        if fallback and fallback.returncode==0:
            meta=json.loads(fallback.stdout)
            entry.update({k:meta.get(k) for k in ['full_name','stargazers_count','forks_count','pushed_at','archived','default_branch','description']})
            entry['license']=(meta.get('license') or {}).get('spdx_id','Unknown')
            entry.pop('metadata_error',None)
    try:
        if not (dest/'.git').exists():
            p=subprocess.run(['git','-c','filter.lfs.required=false','-c','filter.lfs.smudge=','-c','filter.lfs.process=','clone','--depth','1','--quiet','https://github.com/'+repo+'.git',str(dest)],capture_output=True,text=True,timeout=180)
            if p.returncode: raise RuntimeError(p.stderr[:400])
        entry['commit']=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()
        entry['skill_files']=len(list(dest.rglob('SKILL.md')))
    except Exception as e: entry['clone_error']=str(e)
    return entry
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results=[]
    for row in pool.map(collect,REPOS):
        results.append(row); print(row['repo'],row.get('skill_files'),row.get('clone_error',''),flush=True)
(ROOT/'catalog'/'repositories.json').write_text(json.dumps(results,indent=2))
