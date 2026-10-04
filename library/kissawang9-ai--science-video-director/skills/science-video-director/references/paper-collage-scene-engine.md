# Q-chibi paper-theatre scene engine

Use this as the default visual-production layer beneath the story-led explainer workflow. It adapts paper-collage craft and deterministic layer animation to character-led science videos. It does not turn the episode into a product advertisement.

## 1. Visual lock

- Preserve the recurring protagonist as matte, soft hand-painted Q-chibi 2D art.
- Build the paper field from fine uncoated fiber grain with no glossy gradient.
- Use layered paper-cut scenery and props with slightly irregular clean edges, an optional 2–4px warm-white keyline, and soft 6–10px shadows at about 25–35% opacity.
- Use fine halftone or risograph texture on documents, screens, crowds, money, charts, and mechanism objects. Keep faces and skin softly painted.
- Keep one dominant focal point and enough negative space for the single-line caption lane.
- Do not burn long Chinese text into generated images. Add exact titles, labels, numbers, and captions as editable ChatCut text or Motion Graphic layers.

Lock one finished style-anchor frame before generating the batch. It fixes character proportions, paper grain, edges, shadow direction, palette, foreground depth, and emotional tone.

## 2. Storyboard masters and quota saving

Contact-sheet generation is allowed and preferred when it saves image quota.

For every cell, specify:

- scene id and narrative clause;
- character identity, pose, expression, and entrance direction;
- decisive prop before/after state;
- visible consequence;
- camera scale and dominant focal point;
- reusable environment and foreground layer.

Use the approved style anchor and recurring-character reference in every master generation. Reject cells with duplicated actions, blank panels, malformed hands, missing props, incorrect emotions, style drift, or unrelated decoration. Crop accepted cells into independent 1920×1080 files and inspect the crops at full size.

### Grayscale-to-color quota rule

- Generate one approved full-color 16:9 master for a shot, then derive its grayscale state locally in ChatCut or Remotion by desaturation. Do not call an image model again for a grayscale duplicate.
- Preserve the 1920×1080 landscape composition even when the reference uses a vertical or square canvas. Do not inherit oversized white card margins or a listicle layout.
- Use this reveal only when the color change carries a new choice, consequence, mechanism, or understanding. Keep the first-person protagonist story as the structural spine.

For an eligible reveal, animate in this order:

1. Let the grayscale paper field and environment settle.
2. Slide in the grayscale protagonist or decisive prop with a motivated direction.
3. Restore color first to the decisive object, warning, bill, clue, or mechanism.
4. Spread color to the protagonist and visible consequence.
5. Hold the clean full-color result for about 0.4–1.0 seconds.

Keep the series color semantics stable: use red for conflict, loss, warning, or reversal; yellow for mechanism, insight, or resolution; restore natural color for the protagonist's lived reality. Change another meaningful visual element within 2–4 seconds so the reveal never becomes one static card held for an entire paragraph.

## 3. Minimum useful layer plan

Use only layers that carry story information:

1. paper field;
2. recurring environment or stage;
3. protagonist entry state;
4. protagonist action/emotion peak state;
5. protagonist exit or consequence state;
6. decisive prop before/after state;
7. foreground occlusion or pressure layer;
8. optional exact-text overlay.

Group tightly connected objects instead of creating tiny fragments with visible seams. Preserve existing shadows inside cutout padding. Never crop through adjacent dark objects.

## 4. Motion grammar

- Use a hybrid cadence: character body travel uses a smooth 10–18 frame ease, while props, evidence objects, arrows, labels, and result layers use 6–10 visible stop-motion steps.
- Use left/right entrances for arrivals, pursuit, confrontation, or information flow.
- Use top-down drops for notices, interruption, pressure, bills, or sudden consequences.
- Use bottom-up entrances for decisions, realization, recovery, or concept reveal.
- Let base/environment layers settle first, then protagonist, then decisive prop, then exact label.
- Use 8–14 frames at 30fps for the main entrance and a restrained 3–6% settle.
- Hold a clean finished-frame lock for about 0.4–1.0 seconds when the narration permits.
- Vary framing and layers, not random motion. Reject perpetual breathing, endless drift, morphing edges, rapid template transitions, or whole-frame-only sliding when internal action is required.

Inspect an early assembly frame, the action peak, and the final lock frame for every scene.

## 5. Transparent character cutout anime performance

The default character presentation is no longer a person baked into one flattened scene. When a character carries the current clause, separate that character from the environment and animate the cutout as an independent performance layer.

### Required character states

For every major character beat, prepare at least:

1. entry or orientation state;
2. action/emotion peak state;
3. reaction, consequence, or exit state.

Add a fourth explanatory/pointing state when the character introduces evidence. When an action depends on a hand-held object, handoff, pointing arm, falling object, phone, document, money, or tool, provide a separate prop/arm layer or a complete matching pose. A neutral standing cutout cannot represent unrelated verbs.

Keep all states on one identity lock: identical face geometry, apparent age, hairstyle, costume details, body scale, and foot/floor anchor. Reusable character PNGs use a transparent or removable flat background with no baked floor shadow; add the contact shadow as a separate editable layer.

### Anime motion grammar

- Bring a character in over 10–18 frames with translation, 0.94–1.00 scale recovery, opacity reveal, and one restrained 3–6% settle. This is smoother than the stepped paper-prop cadence.
- Change poses with a 4–8 frame match-move or crossfade while keeping the face and foot anchor stable. Do not hard-cut between misaligned bodies.
- Trigger head, upper-body, arm, or prop motion only on the matching spoken action or emotional turn. Do not run perpetual breathing, blinking, bobbing, or random drift.
- Use 1–3% background parallax and an independently moving foreground occlusion when a close shot needs depth. The character remains the dominant focal point.
- For relationship diagrams, place people first, draw the relationship line second, then reveal the document, money, house, test result, or other consequence. Preserve spatial identity so the same person does not jump sides without a motivated transition.
- For scene replacement, allow the outgoing relationship diagram to dim while the incoming full scene grows from the same spatial anchor. This creates continuity without a generic full-screen wipe.

### Clause timing lock

The cutout pose, relation line, evidence object, data label, and consequence must enter at the word-level narration anchor that names them. A relation, number, identity, or conclusion appearing during the previous clause is a hard failure even if the caption timing is correct.

Inspect three frames for every character scene: one frame immediately before entry, the action/pose peak, and the final clean lock. The pre-entry frame must contain no leaked character, relation, data, or conclusion layer.

## 6. ChatCut assembly

Keep ChatCut as the editable master timeline.

Preferred order:

1. Generate and approve independent scene assets.
2. Build one editable scene item per meaningful scene or short chapter.
3. Place the measured ChatCut narration first.
4. Derive scene start/end seconds from the narration waveform.
5. Add layered scene motion, single-line captions, ambience, music, and sparse SFX.
6. Verify representative frames and then export the reviewed timeline id.

Local layered animation may produce individual scene MP4s for import when exact segmentation is more reliable outside ChatCut. Do not flatten the entire episode locally as the primary master.

Avoid one multi-minute Motion Graphic that switches every image from a hard-coded frame array. Separate scene items are easier to retime, inspect, and replace.

## 7. Frame-rate-safe timing

Editorial anchors may be written as 30fps frames, but runtime logic must be time based.

```jsx
const frame = useCurrentFrame();
const {fps} = useVideoConfig();
const timeSeconds = frame / fps;
const startSeconds = anchorFrame30 / 30;
const startFrame = Math.round(startSeconds * fps);
```

Compare `timeSeconds` with second-based scene boundaries, or compare `frame` with `startFrame`. Never compare runtime `frame` directly with a raw 30fps anchor when export fps can change.

The default and delivery rate remains 30fps. Frame-rate-safe code is a resilience requirement, not permission to export arbitrary rates without verification.

## 8. Final validation

- Confirm the export job uses the reviewed timeline id.
- Export H.264/AAC at 1920×1080 and 30fps.
- Run `node scripts/verify-render-sync.mjs <downloaded.mp4> 30`.
- Reject missing audio/video streams, fps mismatch, inconsistent frame count, or excessive audio/video duration delta.
- Extract the opening, one middle frame per scene, reversal, mechanism, and ending into a contact sheet.
- Compare downloaded-file frames with the same timeline moments. The editor preview alone is not final proof.

## Boundaries retained from this project

- First-person protagonist story remains the narrative spine.
- Formal concepts still appear after the decisive reversal.
- Voice remains the user-confirmed ChatCut preset.
- Captions remain editable and single-line.
- Covers retain the established near-black series design and are not automatically converted to paper collage.

This module is adapted from the MIT-licensed production ideas in `Jane-xiaoer/paper-collage-ad-codex`, especially its visual lock, layered paper animation, scene-level rendering, and stream-level quality control. The advertising-specific product promise, brand CTA, mandatory voice cloning, and local flattened master are intentionally excluded.
