# Phase Context Router

Load only the current phase row. A full episode follows the table sequentially.

| Phase | Use when | Read now | Required output | Stop condition |
|---|---|---|---|---|
| `research` | 热点、事实、选题、学科框架 | `video-types.md`; primary sources | topic note, risk level, source note | central contradiction and evidence are sufficient |
| `script-options` | 同一选题给出多个文案方向供用户选择 | `story-engine.md`, `script-selection-and-director-lock.md` | three option cards, selected option id | user selects one option |
| `story` | 把选中的方向扩成最终文案并确认 | `story-engine.md`, `episode-template.md`, `script-selection-and-director-lock.md` | protagonist card, beat sheet, full narration, approval record | user explicitly approves final narration |
| `director-lock` | 文案确认后的导演预演、镜头与执行准备 | `script-selection-and-director-lock.md`, `episode-template.md` | director treatment, edit decision list, generation budget, narration hash | director package passes and is locked |
| `assets` | 人物、分镜母图、场景、道具 | `asset-reuse-system.md`, `character-art-style.md`, `paper-collage-scene-engine.md` | style anchor, `episode-assets.json`, reuse report, shot assets | no placeholders or action mismatches |
| `history` | 历史、制度、战争、历史经济社会 | `historical-editorial-mode.md` plus the active phase refs | evidence ledger, period-correct shot contract | every factual beat has status and evidence object |
| `captions-audio` | 配音、字幕、音效、音乐、同步 | `kinetic-captions-and-sound.md` | measured voice, captions, motion map, cue sheet | word/action/caption/SFX anchors agree |
| `implementation` | ChatCut、Remotion、剪辑、动效 | `paper-collage-scene-engine.md`; Remotion skill only if used | editable timeline, representative renders | visual alignment and timing proof pass |
| `qa` | 下载、验收、错位、黑屏、完播问题 | `quality-gates.md` | validation report, actual MP4 proof | all applicable gates pass or blockers are exact |
| `publishing` | 封面、标题、简介 | `cover-series-style.md`, `publishing-pack.md` | 3:4/4:3 covers, title, description | exact text and thumbnail checks pass |

## Routing rules

- A revision starts from the failed phase. Do not reload unrelated approved phases unless the change invalidates them.
- A new episode cannot skip `script-options`, final narration approval, or `director-lock`. No paid asset generation, TTS, music generation, or timeline editing begins before those gates.
- A reference video contributes only transferable mechanisms to the active phase.
- For large sources, keep paths and extracted decisions in `production-state.json`, not the full source.
- If a phase result changes the protagonist, factual thesis, narration, or timing, mark downstream phases stale in `production-state.json` and rerun only those phases.

## State handoff

Use one episode-local `production-state.json` as the compact handoff. Keep:

- episode id, topic, lens, current phase and phase status;
- three script option ids, selected option id, final narration approval and narration hash;
- director-lock status, treatment path, edit-decision-list path and generation budget;
- protagonist identity and locked visual anchor;
- approved hook, beat ids, verified claims and source paths;
- narration, timing, shot, asset, caption, sound, project, cover and final-export paths;
- blockers and the next smallest action.

Do not store long commentary, discarded variants, full tool output, or repeated rules in this file.
