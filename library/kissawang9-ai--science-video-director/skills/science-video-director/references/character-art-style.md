# Character art style

Use this treatment for every recurring protagonist and supporting character.

## Series default: soft Q-chibi

- Every recurring and one-off character uses the same soft hand-painted Q-chibi system shown in the project reference `assets/style-references/q-chibi-character-collage.png`.
- Head-to-body ratio stays around 1:2.8 to 1:3.5. The head is large, the torso and limbs are compact, and the silhouette remains readable at small size.
- Use a rounded face, large expressive eyes, small nose and mouth, visible blush, soft cheeks, and lively hair clumps.
- Preserve the character's real story age through hairstyle, clothing, posture, props, and facial intent; do not turn every adult into a child.
- Render as a polished 2D storybook illustration: soft watercolor/gouache shading, fine hand-drawn edges, gentle paper texture, and detailed clothing folds.
- Keep skin and fabric matte. Soft volume is allowed, but glossy toy highlights, plastic skin, vinyl-figure surfaces, and hard 3D rendering are forbidden.
- Hands must remain coherent and readable. Simplify fingers only in a deliberate Q-chibi manner.
- Use one dominant expression and one clear action per pose.

## Paper-theatre integration

- Keep the protagonist as a hand-painted Q-chibi illustration; do not convert the face or skin into coarse newspaper halftone.
- Give clothing and hair a fine matte pigment texture. Reserve stronger paper grain, cut edges, white keylines, and halftone dots for scenery, props, shadows, screens, documents, crowds, and mechanism visualizations.
- When a character is used as a movable cutout, preserve a subtle irregular paper edge and a soft low-opacity contact shadow without turning the person into a cardboard puppet.
- Build emotion through approved pose and expression changes. Paper-layer translation supports the performance but never replaces the action/peak/consequence character states.

## Motion-entry lock

- Important characters never simply appear. They enter with a motivated directional movement.
- Use left/right slide-in for arrivals, pursuit, confrontation, and information entering the story.
- Use top-down drop with a short settle for interruptions, notices, pressure, or sudden consequences.
- Use bottom-up pop/slide for realization, comeback, decision, or concept reveal.
- Entrance lasts about 8–14 frames at 30fps and ends with a restrained 3–6% overshoot.
- Do not alternate directions randomly. Direction must match spatial continuity and narrative cause.

## Identity lock

For a recurring character, preserve:

- face shape, eye spacing, eyebrow shape, nose, hairstyle, apparent age, Q-chibi head/body ratio, and body proportions;
- signature clothing colors, collar, pockets, buttons, belt, trousers, and shoes;
- the episode's chosen prop and pose intent.

Change pose, expression, and prop without redesigning the person.

## Avoid

- plastic skin, waxy face, glossy jacket, specular rim lighting, and airbrushed gradients;
- 3D render, toy figure, game-character render, vinyl figure, or Pixar-like volume;
- perfectly uniform vector outlines and stock-illustration smoothness;
- excessive beauty retouching, glassy eyes, wet lips, or porcelain skin;
- cinematic background lighting baked into a reusable character cutout.

## Asset generation

- Generate with `gpt-image-2` using the approved character reference.
- For reusable cutouts, use a perfectly flat removable chroma-key background with no floor, shadow, gradient, or reflection.
- Generate one representative style-lock pose first. After approval, derive the full pose set from that upgraded reference.
- For each story chapter, create a compact performance set rather than one repeated full-body still: entry/orientation, action peak, reaction/consequence, and optional pointing/explaining pose.
- Keep the same crop scale and foot/floor anchor across pose variants so ChatCut can use a 4–8 frame match-move or crossfade without the body visibly jumping.
- When the narration names a hand action or manipulated object, generate the matching arm/hand/prop state or provide the prop as a separate transparent layer. Do not fake a handoff, drop, strike, signature, phone action, or pointing gesture with a neutral pose.
- Keep reusable contact shadows separate from the person PNG. This lets the shadow settle independently when the character slides or scales into a scene.
- Use `assets/style-references/q-chibi-character-collage.png` only as a general style and proportion reference. Do not reproduce any exact person, outfit, pose, watermark, or composition from the collage.
- Never overwrite the previous generation until the upgraded identity and transparency pass inspection.

## Approval checks

- At 100% size, paper/pigment texture is visible but not noisy.
- Skin and clothing remain matte; no white plastic hotspots.
- Hands, fingers, face, and prop are anatomically coherent.
- The silhouette stays readable against both light and dark video backgrounds.
- The character still looks like the same named protagonist across all poses.
