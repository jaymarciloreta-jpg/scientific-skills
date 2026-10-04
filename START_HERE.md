# Start here

These starting sets are selected for topical fit and identifiable upstream sources. They are recommendations for evaluation, not a claim of tested interoperability. Small specialist repositories are marked early/niche in the catalog.

## Scientific ideation and research

[scientific-brainstorming](library/K-Dense-AI--scientific-agent-skills/skills/scientific-brainstorming/SKILL.md), [hypothesis-generation](library/K-Dense-AI--scientific-agent-skills/skills/hypothesis-generation/SKILL.md), [experimental-design](library/K-Dense-AI--scientific-agent-skills/skills/experimental-design/SKILL.md), [scientific-critical-thinking](library/K-Dense-AI--scientific-agent-skills/skills/scientific-critical-thinking/SKILL.md), [literature-review](library/K-Dense-AI--scientific-agent-skills/skills/literature-review/SKILL.md), [citation-management](library/K-Dense-AI--scientific-agent-skills/skills/citation-management/SKILL.md), [statistical-power](library/K-Dense-AI--scientific-agent-skills/skills/statistical-power/SKILL.md).

## General computer vision

[roboflow-data-management](library/roboflow--computer-vision-skills/skills/roboflow-data-management/SKILL.md), [roboflow-inference](library/roboflow--computer-vision-skills/skills/roboflow-inference/SKILL.md), [roboflow-training-and-evaluation](library/roboflow--computer-vision-skills/skills/roboflow-training-and-evaluation/SKILL.md).

## Medical image preparation and segmentation

[dicom-series-preflight](library/NVIDIA-Medtech--medical-AI-skills/skills/dicom-series-preflight/SKILL.md), [dicom-series-to-volume](library/NVIDIA-Medtech--medical-AI-skills/skills/dicom-series-to-volume/SKILL.md), [nv-segment-ct](library/NVIDIA-Medtech--medical-AI-skills/skills/nv-segment-ct/SKILL.md), [nv-segment-ct-finetune](library/NVIDIA-Medtech--medical-AI-skills/skills/nv-segment-ct-finetune/SKILL.md), [medtech-model-evidence-export](library/NVIDIA-Medtech--medical-AI-skills/skills/medtech-model-evidence-export/SKILL.md).

## Device concept, CAD and simulation

[lab-hardware-cad](library/K-Dense-AI--scientific-agent-skills/skills/lab-hardware-cad/SKILL.md), [pymoo](library/K-Dense-AI--scientific-agent-skills/skills/pymoo/SKILL.md), [fluidsim](library/K-Dense-AI--scientific-agent-skills/skills/fluidsim/SKILL.md), [openpiv](library/K-Dense-AI--scientific-agent-skills/skills/openpiv/SKILL.md), [uncertainty-and-units](library/K-Dense-AI--scientific-agent-skills/skills/uncertainty-and-units/SKILL.md).

## Scientific communication

[scientific-writing](library/K-Dense-AI--scientific-agent-skills/skills/scientific-writing/SKILL.md), [scientific-schematics](library/K-Dense-AI--scientific-agent-skills/skills/scientific-schematics/SKILL.md), [scientific-visualization](library/K-Dense-AI--scientific-agent-skills/skills/scientific-visualization/SKILL.md), [scientific-slides](library/K-Dense-AI--scientific-agent-skills/skills/scientific-slides/SKILL.md), [infographics](library/K-Dense-AI--scientific-agent-skills/skills/infographics/SKILL.md).

## Video production

[hyperframes](library/heygen-com--hyperframes/skills/hyperframes/SKILL.md), [faceless-explainer](library/heygen-com--hyperframes/skills/faceless-explainer/SKILL.md), [embedded-captions](library/heygen-com--hyperframes/skills/embedded-captions/SKILL.md), [slideshow](library/heygen-com--hyperframes/skills/slideshow/SKILL.md), [product-launch-video](library/heygen-com--hyperframes/skills/product-launch-video/SKILL.md).

## Complementary specialist collections

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
