# Publishing pack

Create this pack after the final video passes story, audio, subtitle, and technical QA.

## Required files

- `cover-3x4.png`: 1080×1440.
- `cover-4x3.png`: 1440×1080.
- `publishing-copy.md`: cover headline, video title, and video description.

Store the files inside the episode's local production folder.

## Cover headline

- Follow [cover-series-style.md](cover-series-style.md) as the fixed series cover system.
- Use a three-line combined headline: white `学科：现象`, red `反常问题`, yellow `核心概念`.
- Choose the truthful explanatory lens: `经济学：`, `心理学：`, `社会学：`, `医学：`, `科技：`, or another relevant field.
- Keep the white line to roughly 6–10 Chinese characters, the red line to 7–12, and the yellow concept to 2–6.
- Use concrete nouns and verbs. Avoid vague labels such as `深度解析`, `全面解读`, or `震惊`.
- Keep one dominant message. Do not turn the cover into a summary slide.

## Cover composition

- Use a near-black charcoal or dark woodgrain textured background with no detailed cinematic scene.
- Show one original protagonist with one decisive prop and one exaggerated, story-specific reaction.
- Keep the character isolated and readable, occupying roughly 30–45% of the cover height.
- Use the fixed visual order: white setup line, red contradiction line, central character/prop, yellow concept line.
- Preserve the episode's character design, colors, and world.
- Make 3:4 and 4:3 versions from the same visual identity, but recompose each ratio separately.
- Keep the protagonist's face, decisive prop, and full headline inside safe areas.
- Generate the complete cover artwork with ChatCut `gpt-image-2` (`img2`), including the requested Chinese headline.
- Do not use a screenshot or extracted video frame as the cover image.
- If the generated headline contains a wrong character, missing punctuation, duplicated words, or extra text, regenerate it rather than delivering it.
- Never include platform UI, view counts, hearts, progress bars, screenshots, logos, watermarks, or unrelated decorative text.
- Check both full-size and thumbnail previews.

## Video title

- Prefer 20–32 Chinese characters.
- State the topic, contradiction, and promised concept or payoff.
- The title may be slightly more explanatory than the cover.
- Do not overclaim, invent urgency, or promise investment returns.

## Video description

- Prefer 80–160 Chinese characters.
- Include the protagonist's opening problem, the concept revealed, and what the viewer will understand.
- Name the source institutions or link the local source note when factual claims are used.
- Label fictional scenes as fictional when viewers could mistake them for real events.
- Add `不构成投资建议` for finance and investment topics.
- End with 4–8 relevant `#话题标签`; the first tag should name the main content category, such as `#经济学`.

## Final check

- Confirm exact pixel dimensions.
- Confirm headline spelling and punctuation.
- Confirm the two covers are not simple crops of one layout.
- Confirm the title and description match the final video rather than an earlier draft.
- Confirm the description contains relevant `#话题标签`.
