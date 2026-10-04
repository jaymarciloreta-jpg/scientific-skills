# Kinetic captions and sound design

## What to transfer from subtitle-editing references

Treat text as a moving story object. The transferable mechanism is not a particular font, preset, color, or template. It is the synchronization of one spoken emphasis with one visual text action and one short sound cue.

The reference pattern is:

`plain setup → one key word takes visual control → motion lands on the spoken stress → a short SFX confirms the landing → the screen clears for the next idea`

Do not copy a reference video's avatar, exact layout, effect names, branding, or typography package.

## Two caption modes, never two caption lines

1. **Base mode:** one short clause in the fixed safe subtitle lane. Use high-contrast white text with a restrained outline or shadow.
2. **Emphasis mode:** for a decisive number, conflict word, reversal word, or concept term, replace the base card with one animated single-line composition. Do not keep the full base caption underneath it.

Split long speech into consecutive cards. Never shrink an entire sentence until it becomes hard to read, and never wrap a subtitle into two physical lines.

## Stable visual semantics

- White: identity, action, factual setup, and connective words.
- Red: loss, danger, contradiction, denial, reversal, or a broken rule.
- Yellow: mechanism, evidence, resolution, or the final concept.
- One spoken clause gets at most one dominant highlighted group, normally 1–5 Chinese characters.
- Size contrast should reveal hierarchy immediately. The important word may be larger, but connective words remain readable rather than becoming visual noise.

## Motion must explain meaning

- Weight, cost, or a hard conclusion: short scale overshoot and impact.
- Movement, departure, or transfer: directional slide and whoosh.
- Two values or obligations diverging: separate words or numbers in opposite directions.
- Repetition or multiplication: controlled duplication, then stop on one decisive total.
- Quantity or time: count, tick, flip, or progressive reveal.
- Notification or interruption: pop, stamp, or sudden vertical arrival.
- Concept reveal: restrained focus, glow, or underline after a brief quiet beat.
- Final line: minimal motion. Let the words hold rather than adding a flashy exit.

As a practical starting point at 30fps, keep the main entrance around 4–10 frames, allow a readable hold, and use a short clean exit. Retiming must follow the measured voice and the emotional beat, not a universal preset.

## Four-layer audio hierarchy

1. **Narration:** the intelligibility anchor. Use the user-confirmed voice and direct its performance by beat.
2. **Background music:** a low emotional bed with changes at escalation, reversal, and resolution. Duck it beneath speech.
3. **Ambience and foley:** establish the lived space, such as shop room tone, train rumble, door movement, paper, tape, footsteps, or a clock.
4. **Emphasis SFX:** sparse short cues for a key word, number, action, transition, or reveal.

Silence is a fifth tool. A short gap before the decisive reversal, concept name, or final sentence makes the next sound more powerful.

## Caption-to-sound mapping

| Caption or action | Suitable sound family | Purpose |
|---|---|---|
| Text types or appears in sequence | soft typing, tick, paper tap | confirms information arrival |
| Keyword scales or lands | pop, low impact, restrained hit | adds weight |
| Text or character slides | short whoosh | confirms direction |
| Number changes | click, counter, coin, clock tick | makes quantity tangible |
| Alert or refund appears | notification, stamp, UI pop | creates interruption |
| Glow or concept reveal | soft chime, shimmer, tonal lift | signals recognition |
| Door, train, packing, footsteps | matching foley and ambience | anchors the character in a real space |
| Reversal | brief riser followed by impact or silence | marks a change in meaning |

Use the ChatCut Sound Effects library before generating anything custom. Avoid stacking more than two attention-seeking SFX at one moment.

## Required planning artifacts

### `caption-motion-map.md`

Record:

`time/frame | spoken clause | emphasized word | caption mode | color meaning | animation | screen position`

### `sound-cue-sheet.md`

Record:

`time/frame | narration beat | visible action | cue type | asset/source | gain | fade | editorial purpose`

## Verification

- Watch once with sound off: the hierarchy and meaning of each emphasized word should still be clear.
- Listen once without looking: narration must remain intelligible and the sound arc should reveal escalation and release.
- Watch once at full mix: the spoken stress, caption motion, character/prop action, and SFX transient should land together.
- Inspect the waveform for unplanned long dead zones and for continuous overfilling.
- Measure the final mix and retain safe headroom below clipping.
