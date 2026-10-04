"""Build a topical inventory and vendor permissively licensed skill directories.
No downloaded skill code is executed. Uses only Python's standard library.
"""
from pathlib import Path
import json,re,csv,hashlib,shutil,html,collections
ROOT=Path(__file__).resolve().parents[1]
repos=json.loads((ROOT/'catalog/repositories.json').read_text())
RULES={
'Computer vision & ML':r'vision|opencv|yolo|roboflow|deep-learning|pytorch|tensorflow|transformers|scikit-learn|shap|umap|automl|model|gpu|jax|trackio',
'Medical imaging & segmentation':r'segment|dicom|slicer|imaging|mist-expert|misfit|histolab|pathml|cellprofiler|omero|pacsomatic|bids|neuro|registration|nifti|nv-reason|nv-generate|medtech',
'Scientific ideation & research':r'brainstorm|hypothe|research|literature|citation|peer-review|critical-thinking|experimental|experiment|statistical|statistic|scholar|uncertainty|what-if|paper|pymc|statsmodels|science-video',
'CAD, simulation & hardware':r'cad|kicad|hardware|firmware|embedded|fpga|ros2|systemverilog|spice|pcb|vibe-|femis|abaqus|finite-element|simulat|fluidsim|openpiv|pymoo|pybamm|cantera|fictiv|mechanical|mesh|thermal|structural|manufactur|multiphysics|optimization',
'Medical device quality & validation':r'iso13485|iso-standards|risk-management|regulatory|quality-manager|quality-document|capa|fda-|mdr-|qms-|clinical-research',
'Video, audio & physician content':r'video|remotion|hyperframes|caption|overlay|slideshow|animation|gsap|lottie|waapi|animejs|faceless|voice|speech|sound|music|runway|scientific-writing|scientific-slides|scientific-schematics|scientific-visualization|infographic|poster|presentation|pptx|docx|canvas-design|content-creator|content-strategy|content-production|brand-guidelines|storytell',
'Iteration & reproducibility':r'writing-plans|executing-plans|systematic-debug|test-driven|verification-before|finishing-a-development|experiment|autoresearch|grade-iterate|decision-log|spec-driven|data-quality|data.*version|datalad|lamindb|nextflow|open-notebook|labarchive|protocolsio|benchmark|reproduc|least-squares'
}
WHOLE={
'ultralytics/skills':'Computer vision & ML','roboflow/computer-vision-skills':'Computer vision & ML',
'mist-medical/skills':'Medical imaging & segmentation','NVIDIA-Medtech/medical-AI-skills':'Medical imaging & segmentation',
'AminAlam/meddev-agent-skills':'Medical device quality & validation',
'lukeoishi/engineering-agent-skills':'CAD, simulation & hardware','jmwright/cadquery-llm-skill':'CAD, simulation & hardware','flowful-ai/cad-skill':'CAD, simulation & hardware','luckiday/vibe-hardware':'CAD, simulation & hardware','IxTechCrypto/kicad-skills':'CAD, simulation & hardware','sabas0ba/kicad_skills':'CAD, simulation & hardware','dropio12/cherry-hardware-agent':'CAD, simulation & hardware',
'Aditya-Tandon/claude-research-skills':'Scientific ideation & research','zi-yue-1129/research-lab-skills':'Iteration & reproducibility','test1card/femis-skill':'CAD, simulation & hardware','Cai-aa/CAE-Agent-Hub':'CAD, simulation & hardware','VeryMath/AI4Math-Computational-Mathematics':'Iteration & reproducibility',
'remotion-dev/skills':'Video, audio & physician content','phamthanhnghia/remotion-agent-skills':'Video, audio & physician content','elevenlabs/skills':'Video, audio & physician content','runwayml/skills':'Video, audio & physician content'}
def front(text,key):
    if not text.startswith('---'): return ''
    fm=text.split('---',2)[1]
    m=re.search(r'^'+re.escape(key)+r':\s*(.*)$',fm,re.M)
    if not m:return ''
    value=m.group(1).strip()
    if value in ('>','|','>-','|-',''):
        tail=fm[m.end():]; value=' '.join(x.strip() for x in re.split(r'\n(?=\S)',tail)[0].splitlines())
    return value.strip('"\'')
installed={}
for base in [Path('/Users/jaymarc/.agents/skills'),Path('/Users/jaymarc/.codex/skills')]:
    for p in base.glob('*/SKILL.md'):
        t=p.read_text(errors='replace'); installed.setdefault(front(t,'name') or p.parent.name,[]).append(hashlib.sha256(t.encode()).hexdigest())
counts=collections.Counter(); rows=[]; seen={}; exclusions=[]
for repo in repos:
    slug=repo['repo']; base=ROOT/'sources'/slug.replace('/','--')
    if not repo.get('commit'):continue
    for file in sorted(base.rglob('SKILL.md'),key=lambda p:(len(p.parts),str(p))):
        rel=file.relative_to(base); parts=set(rel.parts)
        if file.is_symlink():continue
        if parts & {'tests','test','fixtures','evals','node_modules','.git','vendor','template','templates'}:continue
        if slug=='NVIDIA-Medtech/medical-AI-skills' and rel.parts[0]!='skills':continue
        if slug=='heygen-com/hyperframes' and rel.parts[0] in {'.agents','.claude'}:continue
        if slug=='elevenlabs/skills' and rel.parts[0]=='.agents':continue
        text=file.read_text(errors='replace'); name=front(text,'name') or file.parent.name
        if name in {'app-store-optimization','performance-optimization','marketing-skills','business-growth-skills','research-finance','market-research-reports','pkpd-modeling','runway-dev-characters','rw-check-org-details'}:continue
        if name.lower() in {'readme','template','sample-skill','skill-creator','agent-orchestration'}:continue
        cats=[k for k,v in RULES.items() if re.search(v,name,re.I)]
        if slug in WHOLE and WHOLE[slug] not in cats:cats.insert(0,WHOLE[slug])
        if slug=='znlgis/opengis-skills':
            if rel.parts[0] not in {'cad','3d','iot'}:continue
            cats=['CAD, simulation & hardware']
        if not cats:continue
        digest=hashlib.sha256(text.encode()).hexdigest()
        # Same skill name from the same source is one entry; hash tracks exact duplicates elsewhere.
        key=(slug,name)
        if key in seen:
            seen[key]['alternate_paths'].append(str(rel));continue
        licenses=list(base.glob('LICENSE*'))+list(base.glob('COPYING*'))
        declared=front(text,'license'); lic=repo.get('license','Unknown')
        permissive=lic in {'MIT','Apache-2.0','BSD-2-Clause','BSD-3-Clause','ISC'}
        local=ROOT/'library'/slug.replace('/','--')/rel.parent
        copied=False
        if permissive and licenses:
            def ignore(path,names):
                return [n for n in names if n in {'.git','node_modules','__pycache__','.DS_Store','.venv'} or (Path(path)/n).is_symlink()]
            # Preserve complete skill folder and its adjacent resources. Root-level skills retain repository context.
            shutil.copytree(file.parent,local,dirs_exist_ok=True,ignore=ignore)
            for licensefile in licenses:
                if licensefile.is_file():
                    dest=ROOT/'library'/slug.replace('/','--')/licensefile.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(licensefile,dest)
            copied=True
        status='same-name installed; different contents' if name in installed else 'not found in local skill roots'
        if digest in installed.get(name,[]):status='exact local match'
        row={'name':name,'categories':cats,'repository':slug,'description':front(text,'description')[:650],
             'source_path':str(rel),'url':f'https://github.com/{slug}/blob/{repo["commit"]}/{rel.as_posix()}',
             'commit':repo['commit'],'sha256':digest,'stars':repo.get('stargazers_count'),
             'license':lic,'skill_declared_license':declared,'pushed_at':repo.get('pushed_at'),
             'maturity':'Established repository' if (repo.get('stargazers_count') or 0)>=1000 else ('Community repository' if (repo.get('stargazers_count') or 0)>=100 else 'Early/niche; limited adoption evidence'),
             'installed_status':status,'collected':copied,'local_path':str((local/'SKILL.md').relative_to(ROOT)) if copied else '',
             'review':'Indexed from source; not execution-tested','alternate_paths':[]}
        rows.append(row);seen[key]=row
rows.sort(key=lambda r:(r['categories'][0],r['repository'],r['name']))
# Attach observed directory install counts where the CLI provided them; never infer missing counts.
installs={}
for f in (ROOT/'evidence').glob('skills-search-*.txt'):
    t=re.sub(r'\x1b\[[0-9;]*m','',f.read_text())
    for repo,name,count in re.findall(r'([\w.-]+/[\w.-]+)@([^\s]+)\s+([\d.,KM]+) installs',t): installs[(repo,name)]=count
for row in rows:row['directory_installs']=installs.get((row['repository'],row['name']),'Not observed')
(ROOT/'catalog/skills.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
with (ROOT/'catalog/skills.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader()
    for row in rows:writer.writerow({k:'; '.join(v) if isinstance(v,list) else v for k,v in row.items()})
lines=['# Skill catalog','','Collected 2026-10-04. Individual upstream skills are indexed by pinned commit. Descriptions are upstream metadata, not independently validated claims. Stars and directory installs are adoption signals, not proof of quality.','','| Skill | Categories | Source | Stars | License | Local copy |','|---|---|---|---:|---|---|']
for r in rows:lines.append(f'| [{r["name"]}]({r["url"]}) | {", ".join(r["categories"])} | {r["repository"]} | {r["stars"]} | {r["license"]} | {"Yes" if r["collected"] else "Link only"} |')
(ROOT/'catalog/CATALOG.md').write_text('\n'.join(lines)+'\n')
summary={'repositories':len(repos),'indexed_skills':len(rows),'collected_skills':sum(r['collected'] for r in rows),'unique_content_hashes':len(set(r['sha256'] for r in rows)),'categories':dict(collections.Counter(c for r in rows for c in r['categories'])),'local_matches':sum(r['installed_status']!='not found in local skill roots' for r in rows)}
(ROOT/'catalog/summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
# Attribution per source, outside skill content.
for repo in repos:
    dest=ROOT/'library'/repo['repo'].replace('/','--')
    if dest.exists(): (dest/'UPSTREAM.json').write_text(json.dumps(repo,indent=2))
