# Script selection and director lock

This phase prevents expensive visual rework. It separates creative choice, final narration approval, directing, and editing.

## Gate A: script options

For one researched topic, present three compact but meaningfully different script treatments. Each option must include:

- option id and working title;
- opening contradiction question;
- protagonist name, identity, immediate desire, and measurable stake;
- first-person causal chain;
- reversal and delayed concept reveal;
- three mappings and the ending resolution;
- estimated narration range and likely new-asset burden.

The options must differ in protagonist situation, dramatic engine, or explanatory lens—not merely wording. Do not write three long full narrations, generate assets, create TTS, or start a timeline at this stage.

Record the user's selected option id in `production-state.json`. Expand only that option into the full narration. Show the complete narration for approval and record `finalNarrationApproved: true` only after explicit user confirmation.

## Gate B: director preparation

After final narration approval, create:

1. `director-treatment.md`: emotional curve, visual thesis, continuity of space/time, palette progression, focal hierarchy, grayscale-to-color reveal, transition discipline, and sound strategy.
2. `edit-decision-list.md`: every narration clause mapped to scene, shot, character action, decisive prop, entry/peak/result state, motion direction, caption emphasis, SFX, and exact reveal order.
3. `episode-assets.json` plus the resolution report: reuse and adapt approved assets before generation; list only genuine gaps.
4. `generation-budget.md`: planned character sheet, environment sheet, two independent covers, TTS, music, correction reserve, and full-export count.
5. Measured narration timing, caption-motion map, and sound cue sheet.

The director must rehearse the complete episode on paper before editing. Check:

- every spoken verb has a matching action state;
- every number, relationship, object, and consequence appears on its spoken anchor;
- each shot has one dominant focal point and one new story function;
- locations, screen direction, character floor anchors, and prop states remain continuous;
- the first 15 seconds, reversal, concept reveal, and ending have distinct visual beats;
- all required assets exist or fit the approved generation budget;
- no placeholder, early reveal, repeated substitute pose, or unexplained visual cut remains.

Record the approved narration SHA-256 and set `directorLock.status` to `approved`. Editing is blocked until this gate passes.

## Gate C: editor execution

The editor executes the locked `edit-decision-list.md`. The editor may adjust technical timing, easing, crop, volume, and safe-area placement, but may not:

- rewrite or reorder narration;
- reveal data, concepts, or results early;
- invent unplanned scenes or substitute unrelated poses;
- add decorative cuts that change focal hierarchy;
- regenerate assets merely to solve an avoidable timeline problem.

If the locked plan cannot be executed, stop at the exact failed beat and return it to the director phase. Do not patch around it with random imagery.

## Change control

Any post-approval change to narration, protagonist, factual thesis, reversal, concept, or timing invalidates the director lock and marks assets, captions-audio, implementation, and QA as `stale`. Re-lock the smallest affected section before editing resumes.

The workflow may advance without further user interruption when the approved narration is unchanged and the director package passes. New paid generation beyond the recorded budget still requires authorization.
