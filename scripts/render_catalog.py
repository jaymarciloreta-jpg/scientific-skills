from pathlib import Path
import json,html,collections
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'catalog/skills.json').read_text()); summary=json.loads((root/'catalog/summary.json').read_text())
data=json.dumps(rows,ensure_ascii=False).replace('<','\\u003c')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Physician–Scientist Skill Library</title>
<style>body{font:16px/1.55 system-ui,sans-serif;margin:0;background:#f3f5f6;color:#142d37}main{max-width:1200px;margin:auto;padding:36px 24px}h1{font-size:38px;line-height:1.15;margin:12px 0}p{max-width:860px}input,select{padding:12px;border:1px solid #aebfc6;border-radius:7px;font:inherit;background:white}input{min-width:300px;flex:1}.filters{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0 12px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}.card{background:white;border:1px solid #d8e0e3;padding:20px;border-radius:10px}.card h2{font-size:19px;overflow-wrap:anywhere;margin:0 0 8px}.tag{font-size:12px;display:inline-block;background:#e5f0ed;padding:3px 7px;margin:2px;border-radius:4px}.meta{font-size:13px;color:#536b74}.card p{font-size:14px}.links{display:flex;gap:15px}a{color:#066675}#count{font-weight:600;margin-bottom:18px}</style>
<main><div class="meta">RESEARCH · ENGINEERING · COMMUNICATION</div><h1>Physician–Scientist Skill Library</h1><p>Agent skills for medical and general computer vision, segmentation, scientific ideation, device development, and video/content creation. Indexed from source on October 4, 2026; execution has not been tested.</p><div class="filters"><input id="search" aria-label="Search skills" placeholder="Search skill, tool, topic, or repository…"><select id="category" aria-label="Category"><option value="">All categories</option></select><select id="copy" aria-label="Collection status"><option value="">All entries</option><option value="yes">Collected locally</option><option value="no">Source links only</option></select></div><div id="count" aria-live="polite"></div><div id="grid" class="grid"></div></main><script>const rows=DATA;
const search=document.querySelector('#search'),cat=document.querySelector('#category'),copy=document.querySelector('#copy'),grid=document.querySelector('#grid');
for(const category of [...new Set(rows.flatMap(r=>r.categories))].sort()){const o=document.createElement('option');o.value=category;o.textContent=category;cat.append(o)}
function text(tag,value,cls){const e=document.createElement(tag);e.textContent=value;if(cls)e.className=cls;return e}
function render(){const q=search.value.toLowerCase();const found=rows.filter(r=>(!cat.value||r.categories.includes(cat.value))&&(!copy.value||r.collected===(copy.value==='yes'))&&[r.name,r.description,r.repository,...r.categories].join(' ').toLowerCase().includes(q));document.querySelector('#count').textContent=found.length+' skills · '+found.filter(r=>r.collected).length+' collected';grid.replaceChildren();for(const r of found){const card=text('article','','card');card.append(text('h2',r.name));for(const c of r.categories)card.append(text('span',c,'tag'));card.append(text('p',r.description||'Open the source skill for its workflow.'));card.append(text('div',r.repository+' · '+(r.stars??'Unknown')+' stars · '+r.license,'meta'));card.append(text('div',r.maturity+' · '+r.directory_installs+' directory installs','meta'));card.append(text('div',r.installed_status,'meta'));const links=text('p','','links');const source=text('a','Pinned source');source.href=r.url;source.target='_blank';source.rel='noopener';links.append(source);if(r.collected){const local=text('a','Local skill');local.href='../'+r.local_path;links.append(local)}card.append(links);grid.append(card)}}for(const el of [search,cat,copy])el.addEventListener('input',render);render();</script></html>'''.replace('DATA',data)
(root/'catalog/index.html').write_text(page)
readme=f'''# Physician–Scientist Skills

A collected agent-skill library for **computer vision, medical imaging and autosegmentation, scientific ideation, device development, and video/content creation**. Medical and general hardware workflows receive equal priority.

Collected **2026-10-04**: **{summary['indexed_skills']} indexed skills** from **{summary['repositories']} source repositories**, with **{summary['collected_skills']} cataloged skills copied locally** where a permissive repository license and license file were identified. The separately selected scientific-brainstorming version is also preserved.

## Browse

- [Full catalog](catalog/CATALOG.md) — browse directly on GitHub.
- [Searchable catalog](catalog/index.html) — download/open locally for search and category filters; GitHub displays HTML source rather than running it.
- [CSV inventory](catalog/skills.csv) and [JSON inventory](catalog/skills.json).
- [Recommended starting sets](START_HERE.md).
- [Physician/scientist content workflows](PHYSICIAN_CONTENT.md).
- [Repository metadata and pinned revisions](catalog/repositories.json).

## Your authored skills

[Skills by Jaymarc Iloreta](authored-by-jaymarc/README.md) contains four original workflows for surgical video editing, Slicer sinus ROI, and nasal-airway geometry, plus a separately attributed Slicer adaptation.

## First skill added

[Scientific brainstorming](skills/scientific-brainstorming/SKILL.md) is the exact version you selected, with [SCAMPER, Six Thinking Hats, morphological analysis, TRIZ, and biomimicry reference methods](skills/scientific-brainstorming/references/brainstorming_methods.md). Its original files are unchanged; provenance and a license were added separately.

## Coverage

| Topic | Indexed entries |
|---|---:|
'''+''.join(f'| {k} | {v} |\n' for k,v in summary['categories'].items())+'''
Skills may appear in multiple categories. Repeated placements of the same named skill within a repository are collapsed, with alternative paths recorded. Different implementations from different repositories remain separate.

## Layout and use

`skills/` holds explicitly selected versions. `library/<owner>--<repo>/` holds namespaced upstream skill folders with their accompanying files and licenses. `catalog/` links each skill to its exact Git commit and records a content hash, licensing, popularity, and local availability. `sources/` contains local upstream checkouts and is excluded from Git.

To use a collected skill, open its `SKILL.md` and accompanying references in your agent, or copy the complete skill directory into the agent's skill location. Review its dependencies first: some require a specific application, MCP server, GPU, API account, or files elsewhere in the upstream repository. A collected folder is not a tested installation. Skills are not globally activated by this repository.

The inventory compares names and content against the two local skill roots available during collection. “Same-name installed” does not establish equivalence or mean an update has been applied. Directory install counts are included only when observed in saved CLI search output; missing counts are not zero.

## Provenance and licensing

Third-party material retains its original license and attribution; this repository does not relicense it. Skills with unknown, custom, noncommercial, or copyleft repository licensing are cataloged as source links only in this initial collection. This is a collection policy, not a claim that those licenses prohibit use. Runtime software, models, services, and weights can have licenses separate from a skill's text.

Source existence and metadata were checked, but **the skills have not been execution-tested or clinically validated**. Repository popularity is only an adoption signal. Regulatory skills are supporting references whose statements must be checked against current authoritative requirements.

## Rebuilding

`python3 scripts/collect.py` retrieves the listed source repositories into `sources/` and records the existing checkout revision. It reuses existing checkouts; it does not silently update them. Then run `python3 scripts/build_catalog.py` and `python3 scripts/render_catalog.py`. The builder uses explicit topic filters; it is a broad discovery catalog, not an exhaustive list of every GitHub skill.

Collection scripts read upstream content as data and do not run upstream setup scripts or models. The checked-in snapshot and commit metadata make the current collection reproducible. Review local changes before refreshing or publishing a new snapshot.
'''
(root/'README.md').write_text(readme)
