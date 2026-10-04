---
name: science-video-director
description: Create, adapt, and render 16:9 Chinese story-led explainer videos using an original protagonist, matte Q-chibi paper-theatre layers, ChatCut or Remotion, synchronized narration/captions/sound, reusable assets, covers, and verified final exports. Use for 科普视频、经济学/心理学/社会学/医学/科技/历史讲解、热点故事化、动漫叙事、分镜、配音、字幕、封面或成片任务。
---

# Character Story Explainer Director

## Goal

Deliver an understandable, immersive, locally editable Chinese explainer in which one original character experiences the mechanism before the formal concept is named. Preserve story clarity, causal depth, visual alignment, audio sync, publishing assets, and final-file verification while using the fewest useful context and generation loops.

## Context loading

Read [references/run-router.md](references/run-router.md) first. Load only the references assigned to the current phase; a full episode still loads them sequentially rather than all at once. Do not reread completed phase artifacts when `production-state.json` contains their approved decisions.

For Remotion implementation, load the installed `remotion-best-practices` skill only when entering implementation. Explicit user instructions override defaults below.

## Success contract

The task is complete only when all applicable conditions pass:

1. Format is 16:9, 1920×1080, 30fps unless the user explicitly changes it.
2. A new episode first presents three meaningfully different compact script options. Only the selected option becomes a full narration, and no paid generation, TTS, music, or editing begins until the user explicitly approves that final narration.
3. After narration approval, the director locks a treatment, clause-level edit decision list, continuity plan, asset resolution, generation budget, caption-motion map, and sound cue sheet. The editor executes this lock instead of inventing the story while cutting.
4. The first five seconds ask one concrete contradiction question, show the protagonist's name and identity, then enter the character's first-person story.
5. The story advances through event, cost, choice, consequence, reversal, concept reveal, three mappings, and resolution. No section survives only to repeat earlier information.
6. Characters and worlds are original. The default visual is matte hand-painted Q-chibi paper theatre with transparent performance poses and independently animated scene, prop, foreground, relation, and result layers.
7. Every spoken action, decisive object, number, relationship, and consequence appears only when the corresponding narration reaches it; no early data or conclusion leak.
8. The asset manifest has no unapproved, blank, generic, repeated-pose, or narration-mismatched placeholder. Reuse approved shared assets before generating a documented gap.
9. Captions are physically one line. Emphasis replaces the base card, and visible text contains no raw escape tokens.
10. Narration, captions, character action, emphasis motion, and sound peaks are aligned to measured audio timing. The audio mix includes narration, subordinate music, useful ambience, and sparse motivated effects.
11. ChatCut remains the editable master. Do not use Seedance or another image-to-video model.
12. The actual downloaded MP4 passes fps, frame-count, audio/video-duration, subtitle, shot, layout, and audible-volume checks.
13. Each episode includes independently composed 3:4 and 4:3 covers, a title, and a factual story-led description ending with 4–8 relevant hashtags.

## Authorization

- For answer, review, diagnosis, or plan requests, inspect the necessary material and report; do not implement unrelated changes.
- For build, change, fix, or render requests, make in-scope local changes and run relevant non-destructive checks without pausing.
- Ask before external publishing, paid generation not already authorized by the request, destructive changes, or material scope expansion.

## Production flow

### 1. Orient

- Classify the current phase with the router.
- Read supplied artifacts completely only when they are primary evidence for this phase.
- Reuse the episode's `production-state.json`; if absent, create it from the template and record only approved decisions, source pointers, blockers, and output paths.
- For current, financial, medical, legal, disputed, or historical claims, retrieve current primary evidence and keep a local source note.

Stop when the topic, lens, protagonist role, factual risk, current phase, required outputs, and missing evidence are explicit.

### 2. Select and approve the script

- Read `script-selection-and-director-lock.md`.
- Present three distinct compact treatments; after selection, expand only that one into the complete narration.
- Record the selected option and explicit approval. Before approval, do not generate assets, audio, covers, or a timeline.

Stop when the user has explicitly approved the complete final narration.

### 3. Build the locked story

- Lock the short contradiction question, protagonist identity card, immediate first-person handoff, desire, irreversible pressure, and measurable stake.
- Build a causal ladder. Every beat must add an event, cost, choice, consequence, or reinterpretation.
- Let viewers feel the mechanism before naming it. Keep roughly 65–75% of narration on lived events and 25–35% on naming, mechanism, caveat, and takeaway.
- Make abstract claims visible through actions and evidence-bearing objects.

Stop when the beat sheet contains the reversal, delayed concept reveal, three story mappings, resolution, and no synonymous filler.

### 4. Lock the director plan

- Create the director treatment and clause-level edit decision list defined in the reference.
- Lock continuity, actions, props, reveal order, sound/caption anchors, assets, and generation budget.
- Record the approved narration SHA-256 and set `directorLock.status` to `approved`.
- A post-lock narration or thesis change marks downstream phases stale and returns the affected section to the director.

Stop when every clause has an executable visual action and preflight has no placeholder, early reveal, continuity break, or unbudgeted generation.

### 5. Resolve visual assets

- Read `asset-library/cast.json`, create `episode-assets.json`, then run:

  ```bash
  npm run assets:resolve -- --input <episode-assets.json>
  ```

- Obey `reuse`, `adapt`, and `generate`. A missing action, emotion, or hand-object interaction is a real gap; a neutral pose is not a substitute.
- Lock one representative style anchor before batch generation. Contact-sheet masters are allowed only when every cell has a scene id, action, emotion, prop state, and consequence.
- For each story-bearing action, prepare entry, action/emotion peak, and reaction/result states. Separate characters, decisive props, relations, foreground, and results.
- Use grayscale-to-color as a causal reveal: derive grayscale from one approved color master, color the decisive object first, then the protagonist and consequence.

Stop before editing if the manifest contains a placeholder, wrong action, blank panel, repeated substitute pose, or early-reveal asset.

### 6. Direct motion, captions, and sound

- Use 10–18 frame eased character travel, 4–8 frame pose swaps, restrained 3–6% settle, and 6–10 step paper-prop/evidence motion. Animate only when narration or emotion motivates it.
- Keep one dominant focal point and change one meaningful visual element every 2–4 seconds. Target story density rather than arbitrary cuts; important events and consequences need separate beats.
- Generate narration with the confirmed ChatCut voice; project default is `yuanboxiaoshu`. Retiming follows measured audio duration.
- Build one-line captions from final narration. Use white for ordinary story information, red for conflict/loss/reversal, and yellow for mechanism/resolution.
- Produce a caption-motion map and sound cue sheet before final rendering.

Stop when word timing, caption onset, character action, visual emphasis, and SFX transients agree at every key point.

### 7. Implement

- Keep scenes separate and data outside JSX when practical. Use seconds as source timing; convert 30fps anchors with `Math.round(anchorFrame30 * fps / 30)`.
- In Remotion use `useCurrentFrame()`, `interpolate()`, `spring()`, and `Sequence`, never CSS animation timing.
- Use ChatCut as the editable timeline. Import local layered renders as scene assets only when needed; never flatten the whole episode as the only master.
- Execute the locked edit decision list. The editor may tune technical timing, easing, crop, volume, and safe areas, but may not rewrite, reorder, reveal early, or invent substitute scenes.
- Render representative hook, reversal, mechanism, and ending frames before a full export.

Stop when representative frames show full-frame coverage, correct focal hierarchy, no clipping/black half-screen, no baked escape tokens, and no narration mismatch.

### 8. Verify

- Load [references/quality-gates.md](references/quality-gates.md) now, not at task start.
- Run the most relevant available checks: asset validation, text escape validation, type/build checks, representative stills, full render/export, `ffprobe`, audible-volume inspection, caption validation, and:

  ```bash
  node scripts/verify-render-sync.mjs <downloaded.mp4> 30
  npm run workflow:validate
  ```

- Inspect the actual downloaded MP4 rather than relying on the editor preview.

Stop only when applicable checks pass or the final report names the exact failed check and blocker.

### 9. Publish pack

- Load the cover and publishing references only for this phase.
- Compose 1080×1440 and 1440×1080 covers independently with ChatCut `gpt-image-2`; do not crop one ratio from the other and do not use video screenshots.
- Use `学科：现象` in white, the contradiction in red, and the core concept in yellow on the series' dark textured background with one original character or decisive prop.
- Inspect exact Chinese text, full-size layout, and thumbnail readability.
- Write one title and one factual story-led description with 4–8 hashtags.

## Efficiency rules

- Use [../../workflow/gpt-5.6-efficiency-policy.md](../../workflow/gpt-5.6-efficiency-policy.md) only when auditing model choice, reasoning, caching, token use, or prompt architecture; it is not required for ordinary episode phases.
- State each durable rule once. Point to an approved local artifact instead of pasting its full content into later prompts.
- Keep the stable project contract as the prompt prefix and append only current phase state, selected evidence, missing fields, and required output.
- Use `npm run video:context -- --episode <dir> --phase <phase>` to create the smallest phase context when a `production-state.json` exists.
- Use only phase-relevant tools. Parallelize independent reads; keep dependent decisions sequential.
- Prefer deterministic scripts for indexing, filtering, deduplication, timing checks, and validation. Keep narrative, visual, factual, and approval judgment visible to the model.
- Do not minimize calls, context, reasoning, or outputs at the expense of evidence, story causality, action coverage, sync, or final-file checks.
- After each result ask whether the phase success and stop conditions are met. If yes, advance; if not, retrieve or fix only the smallest missing requirement.

## Delivery

Save the production state, sources, protagonist card, beat sheet, narration, shot list, asset manifest and resolution report, caption JSON, caption-motion map, sound cue sheet, editable project, preview frames, downloaded verified MP4, both covers, title, and description locally as applicable.

Lead the final response with completion status. Include essential evidence, failed or skipped checks, voice preset, render specification, shot/sync result, and clickable local paths. Omit routine tool narration and repeated artifact contents.
