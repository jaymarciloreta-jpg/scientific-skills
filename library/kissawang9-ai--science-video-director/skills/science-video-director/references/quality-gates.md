# Quality gates

## Story

- A named protagonist appears within five seconds.
- The first five seconds contain a direct spoken question built from a concrete contradiction and stake.
- The protagonist and a name/identity card are visible during the opening question.
- The question is about 22 Chinese characters or fewer, sounds natural at the selected voice speed, and leaves the answer unresolved.
- The opening does not begin with a greeting, `你知道吗`, a definition, a topic announcement, or the protagonist explaining background.
- Immediately after the question, the narration hands off to the protagonist's first-person experience.
- The protagonist makes a decision; events do not merely happen around them.
- At least two consequences escalate before the formal concept is named.
- The concept reveal maps at least three earlier story details back to the mechanism.
- Story occupies roughly 65–75% of narration.
- The ending resolves the opening contradiction.
- No default runtime cap was used to cut a necessary causal beat; any fixed duration comes from an explicit user request.
- Every beat adds a new event, cost, decision, consequence, or reinterpretation; no passage survives only as recap or synonymous explanation.
- Escalation forms a causal ladder instead of a flat hardship list: later beats change the stake, the mechanism, or the meaning of an earlier beat.
- A viewer can retell the chain as `人物想要什么 → 做了什么 → 什么没有随表象改变 → 代价如何扩散 → 概念为什么能解释它`.

## Originality and evidence

- Characters, names, voices, worlds, art, and shot compositions are original or licensed.
- A reference video's mechanism may be transferred; its recognizable expression may not be copied.
- Current or high-stakes claims use primary, current sources.
- Numbers include units, dates, and comparison bases.
- Generated reconstructions are labeled when viewers could mistake them for records.
- Historical episodes include an evidence ledger; every factual beat is marked `史料确认`, `学界推断`, `艺术化重现`, or `存在争议`.
- Period, clothing, money, map boundaries, documents, tools, architecture, titles, and writing systems are internally consistent or explicitly identified as schematic.
- Original editorial historical collage may use transferable map-and-document grammar, but it does not copy Vox branding, fonts, color systems, signature layouts, or shot compositions.

## Visual

- 1920×1080, 16:9 by default; safe areas pass.
- One approved style-anchor frame locks protagonist proportions, paper field, grain, edge treatment, shadows, palette, and depth before batch scene generation.
- Storyboard masters pass a contact-sheet continuity review, and every accepted cell is cropped into an inspected independent 1920×1080 asset before placement.
- One protagonist remains visually identifiable throughout.
- Character skin and clothing read as matte hand-drawn surfaces, with varied line weight, subtle pigment texture, and believable fabric folds.
- No character has glossy plastic highlights, airbrushed skin, toy-like 3D volume, or generic vector-stock smoothness.
- Every 2–4 seconds changes character state, prop state, camera emphasis, or causal annotation.
- Shot count is proportional to story density: roughly 18–24 meaningful shots per minute, with every important event, cost, choice, and causal detail receiving its own visual beat.
- The first 15 seconds contain at least five distinct visual beats and show the concrete loss before background explanation.
- No unchanged composition holds longer than four seconds, except one deliberate reveal or ending hold of at most five seconds.
- A caption, label, or number changing over an otherwise frozen scene does not by itself count as a new shot.
- No more than two consecutive shots reuse the same camera scale, character pose, and prop state.
- The episode has a keyframe asset plan, and every meaningful shot maps to its entry, action peak, and exit/consequence assets where applicable.
- No finished episode relies on one character still for the full story. Shock, decision, physical action, pressure, loss, explanation, and resolution use distinct approved Q-chibi poses.
- Character slide-in, drop-in, and pop-up motions connect generated pose states; they never substitute for missing action keyframes.
- Every character-led clause uses an independent transparent character layer unless a fully integrated scene is editorially necessary. A character baked into every full-frame storyboard crop is not the default.
- Every major character beat has at least entry/orientation, action peak, and reaction/consequence states. Pose changes keep the face and floor anchor stable and transition over 4–8 frames without a visible body jump.
- Character body travel uses a smooth 10–18 frame ease and restrained settle; paper props, evidence objects, arrows, labels, and consequences use the separate 6–10 step paper cadence.
- In multi-person relationship scenes, people appear first, relationship lines second, and evidence/result objects third. Each element begins on its exact spoken anchor; zero relationship, number, document, or conclusion layers leak into the preceding clause.
- Where a scene contains internal action, at least two story-bearing layers move independently. A single flattened full-frame pan/zoom does not pass as paper-theatre animation.
- Layer entrances use motivated directions, a restrained 6–10 step stop-motion cadence, and a clean final lock frame. Random drift, perpetual breathing, visible crop seams, and morphing paper edges fail.
- Every final shot passes the clause-to-image test: a viewer watching without sound can identify who is doing what, to which object/person, and what changed.
- Every multi-panel composition has complete and distinct panel content. Zero blank screens, decorative placeholders, duplicated filler panels, or panels unrelated to the current spoken clause.
- Every action verb in the narration is represented by a matching pose or complete scene asset. Reusing the same pose for different verbs fails the gate even when the background or caption changes.
- The scene asset manifest has zero `missing`, `placeholder`, `generic`, or `mismatch` rows before final timeline assembly.
- Every abstract noun that matters has a visible object or consequence.
- Every historical shot has one decisive evidence object, one main action, and one readable result. Decorative relic piles and unrelated period props fail.
- Historical maps perform a visible causal action and return the viewer to the protagonist's consequence; static map wallpaper fails.
- No scene is primarily a dashboard, slide, or wall of text.
- Each caption card renders on exactly one line with no newline characters.
- Ordinary captions and animated emphasis captions never duplicate the same spoken phrase on two simultaneous lines; the emphasis treatment replaces the base card for that phrase.
- Each spoken clause has at most one dominant emphasized word group, and the highlight color communicates a stable meaning rather than decoration.
- Major beats use semantic caption motion: scale/impact for weight, slide/whoosh for movement, separation for divergence, counter/tick for quantities, and restrained glow for a concept reveal.
- Captions never cover faces, key props, or platform controls.
- No title, card, label, chart, caption, or prop text visibly contains raw escape tokens such as `\\n`, `/n`, `\\r`, or `\\t`.
- Intended multi-line non-caption text uses explicit line arrays or React elements, never escape text inside a JSX quoted attribute.

## Audio and sync

- The user-confirmed voice preset is used consistently.
- Each TTS clip fits its mapped visual window by actual measured duration.
- Narration is audible, unclipped, and intelligible; music stays subordinate.
- Finished episodes include intentional sound design where appropriate: narration, subordinate music, environment/foley, and sparse emphasis SFX. Narration-only delivery requires an explicit creative reason.
- Each SFX is justified by a visible action, transition, prop change, or emphasized word; no effect is added merely to keep the track busy.
- Important SFX transients land within about two frames of the matching motion or spoken stress at 30fps.
- Intentional silence remains available before reversals, concept reveals, or final lines; the mix does not become continuous noise.
- The final true peak remains safely below clipping; do not copy a reference mix that peaks at or near 0 dBFS.
- Spoken line, caption card, character action, and prop state agree at every scene boundary.

## Technical

- Type checking passes.
- Opening preview confirms the full question finishes within five seconds and the identity card is already visible.
- Opening, reversal, mechanism, and ending stills pass full-size inspection.
- Full H.264 MP4 render succeeds unless another format was requested.
- The exported timeline id matches the reviewed active timeline id.
- Motion Graphic timing is fps-aware: scene boundaries are stored as seconds or scaled from 30fps editorial anchors using the active runtime fps.
- The project contains no Seedance or other image-to-video generation jobs or clips. Motion comes from approved still/keyframe assets and deterministic ChatCut layer animation.
- The final export uses 30fps unless the user explicitly requests another rate and every time-bearing component has passed an fps-independence check.
- `ffprobe` confirms resolution, frame rate, stream-level duration, video frame count, and expected audio stream on the actual downloaded MP4.
- Video frame count is consistent with `video duration × fps`, and audio/video stream durations differ by no more than the verifier tolerance.
- `node scripts/verify-render-sync.mjs <downloaded.mp4> 30` passes. A 60fps file produced from a 30fps timeline is a hard failure, even when the editor preview is correct.
- Caption validation reports zero multiline cards.
- Visible-text escape validation reports zero forbidden tokens across runtime source and JSON files.
- Final sync check passes every narration-backed scene.
- `caption-motion-map.md` and `sound-cue-sheet.md` exist and match the rendered timeline.

## Publishing pack

- Both `cover-3x4.png` (1080×1440) and `cover-4x3.png` (1440×1080) exist.
- The two ratios share one visual identity but use ratio-specific composition, not a blind crop.
- The cover contains one dominant headline beginning with the truthful discipline lens for that episode.
- The headline is readable at thumbnail size and does not cover the protagonist's face or decisive prop.
- Chinese wording, punctuation, and title prefix are exact.
- The video title states the topic and contradiction without making a false promise.
- The description contains the story hook, explained concept, factual boundary, and source note.
- Finance or investment topics include a clear `不构成投资建议` boundary.
- Cover artwork was generated with ChatCut `gpt-image-2`, not captured from the video.
- The description ends with 4–8 relevant `#话题标签`.
- Cover background is near-black textured and visually quiet.
- Cover hierarchy is white setup → red contradiction → original character/prop → yellow concept.
- The cover uses one dominant original character, not a recognizable franchise character.
