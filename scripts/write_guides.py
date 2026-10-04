from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]; rows=json.loads((root/'catalog/skills.json').read_text())
def link(repo,name):
 r=next((r for r in rows if r['repository']==repo and r['name']==name),None)
 if not r: raise ValueError((repo,name))
 return f'[{name}]({r["local_path"] or r["url"]})'
k='K-Dense-AI/scientific-agent-skills';h='heygen-com/hyperframes'
groups=[('Scientific ideation and research',k,['scientific-brainstorming','hypothesis-generation','experimental-design','scientific-critical-thinking','literature-review','citation-management','statistical-power']),('General computer vision','roboflow/computer-vision-skills',[]),('Medical image preparation and segmentation','NVIDIA-Medtech/medical-AI-skills',['dicom-series-preflight','dicom-series-to-volume','nv-segment-ct','nv-segment-ct-finetune','medtech-model-evidence-export']),('Device concept, CAD and simulation',k,['lab-hardware-cad','pymoo','fluidsim','openpiv','uncertainty-and-units']),('Scientific communication',k,['scientific-writing','scientific-schematics','scientific-visualization','scientific-slides','infographics']),('Video production',h,['hyperframes','faceless-explainer','embedded-captions','slideshow','product-launch-video'])]
text='# Start here\n\nThese starting sets are selected for topical fit and identifiable upstream sources. They are recommendations for evaluation, not a claim of tested interoperability. Small specialist repositories are marked early/niche in the catalog.\n\n'
for title,repo,names in groups:
 if not names:names=[r['name'] for r in rows if r['repository']==repo and any(x in r['name'] for x in ['data-management','training','inference','evaluation'])]
 text+='## '+title+'\n\n'+', '.join(link(repo,n) for n in names)+'.\n\n'
text+='''## Complementary specialist collections

- [MIST](https://github.com/mist-medical/skills): `mist-expert` and `misfit-expert` were present in the pinned checkout. The web README mentioned an autoresearch skill that was not present; it is not counted.
- [TotalSegmentator](https://github.com/wasserth/TotalSegmentator/tree/master/skills): upstream workflow for anatomy segmentation; requires its actual runtime/MCP setup.
- [3D Slicer](https://github.com/pieper/slicer-skill): programming and medical imaging workflows, with companion integration tooling.
- [Hugging Face](https://github.com/huggingface/skills): vision training and experiment tracking.
- [Ultralytics](https://github.com/ultralytics/skills): YOLO dataset, training, tuning, inference, and export workflows; source links retained under this collection's licensing policy.
- [Medical device development](https://github.com/AminAlam/meddev-agent-skills): requirements, risk, traceability, embedded software, verification, and change control. Review regulatory currency for each use.
- [Vibe Hardware](https://github.com/luckiday/vibe-hardware): coordinated firmware, PCB, industrial design, CAD, and product manifests; early-stage community source.
- [CAE Agent Hub](https://github.com/Cai-aa/CAE-Agent-Hub): Abaqus analysis workflows. Commercial solver access is separate.
- [Remotion](https://github.com/remotion-dev/skills): programmatic video and captions; source-linked, with runtime licensing separate.
- [ElevenLabs](https://github.com/elevenlabs/skills): narration, transcription, audio cleanup, and related media skills. API account and usage charges are separate.

## Practical iteration loops

**Imaging:** define target structures → inspect modality and geometry → establish a baseline → review masks visually → measure errors on held-out cases → change one component → preserve configuration and results.

**Device development:** capture need and interfaces → brainstorm alternatives → select testable design hypotheses → build parametric CAD → simulate relevant behavior → prototype → bench test → record failures and revise.

**Research communication:** gather source evidence → build a claim/source table → write for the audience → generate figures or slides → assemble narration and video → check claims, numbers, labels, and captions → publish the reviewed output.

## Gaps to develop next

The library has useful building blocks, but this collection does not establish a complete, validated end-to-end skill for surgical-video de-identification/editing, anatomy-specific endoscopic video segmentation, CT-to-device-fit evaluation, or evidence-grounded patient education. Your [authored surgical-video and airway/Slicer skills](authored-by-jaymarc/README.md) are included separately, with their scripts, references, and authorship records. Their runtime behavior has not been validated by this collection. Dedicated nnU-Net/MedSAM training skills also merit further targeted collection; supporting software repositories should not be counted as agent skills without an actual skill entry point.
'''
(root/'START_HERE.md').write_text(text)
text='# Physician/scientist video and content workflows\n\nYour own [surgical-video-toolkit](authored-by-jaymarc/skills/surgical-video-toolkit/SKILL.md) is the starting point for long surgical recordings, dead-time removal, Premiere timelines, and teaching clips. See its [resident guide](authored-by-jaymarc/skills/surgical-video-toolkit/RESIDENT_GUIDE.md).\n\n'
text+='Compose content workflows from research, visualization, and production skills. General video generation alone does not provide evidence checking or medical accuracy.\n\n'
text+='| Intended output | Suggested skills |\n|---|---|\n'
for output,items in [
 ('Paper-to-video research explainer',[(k,'literature-review'),(k,'citation-management'),(k,'scientific-schematics'),(h,'faceless-explainer')]),
 ('Grand rounds or conference teaching',[(k,'scientific-slides'),(k,'scientific-visualization'),(h,'slideshow')]),
 ('Captioned surgical teaching footage',[(h,'embedded-captions'),('elevenlabs/skills','speech-to-text')]),
 ('Narrated patient education',[(k,'research-lookup'),('elevenlabs/skills','text-to-speech'),(h,'faceless-explainer')]),
 ('Device concept or prototype demonstration',[(k,'lab-hardware-cad'),(h,'product-launch-video')]),
 ('Research graphics and social summaries',[(k,'infographics'),(k,'scientific-schematics'),(h,'general-video')]),
 ('Illustrative generated footage',[('runwayml/skills','rw-generate-video'),('runwayml/skills','rw-generate-image')])]:
 text+='| '+output+' | '+', '.join(link(repo,n) for repo,n in items)+' |\n'
text+='''
## A reusable production brief

- Audience: patients, trainees, physician peers, scientists, or device stakeholders.
- Purpose: the one thing the viewer should understand or do after watching.
- Evidence: supplied papers, figures, data, and a claim-to-source list.
- Format: length, aspect ratio, narration, caption language, and destination.
- Visual source: actual footage/data, schematic animation, or explicitly illustrative generated media.
- Review: check scientific claims and citations, anatomy, numerical labels, drug/device names, medical terminology in captions, and the distinction between observed data and illustrations.

For real patient images and surgical footage, establish permission and remove identifiers before sharing with external media services. Check the finished video frame by frame where annotations or transformations could alter scientific meaning. This workflow is a proposed composition of skills, not an execution-tested clinical content system.

The saved catalog identifies the exact source revisions. Current APIs, costs, model availability, and model/runtime licenses must be checked when producing media.
'''
(root/'PHYSICIAN_CONTENT.md').write_text(text)
