# Episode production template

## Protagonist card

- Name and role:
- Opening question (about 22 Chinese characters or fewer):
- Identity card shown during the question:
- First-person handoff immediately after the question:
- First-person voice:
- Immediate desire:
- Decision made:
- Fixed obligation or constraint:
- Visible stake:
- Opening contradiction and measurable stake:

## Timecoded beats

For every beat record:

| Time | Story event | Spoken line | Character action | Prop / visual change | Entry keyframe | Peak keyframe | Exit/consequence keyframe | Concept function | Evidence | Caption card |
|---|---|---|---|---|---|---|---|

Keep `Caption card` to one physical line. One beat may use several consecutive caption cards.

## Detailed shot list

For every shot record:

`shot | time/frame | framing | character action | foreground/background | prop state | camera/motion | caption emphasis | sound cue | new story information`

For each shot also record:

`keyframe asset ids | entry direction | entry frame | action peak frame | exit/consequence frame`

- Target roughly 18–24 meaningful shots per minute.
- Opening 15 seconds: at least five distinct visual beats.
- No unchanged composition longer than four seconds, except one deliberate reveal or ending hold capped at five seconds.
- A text-only swap on the same frozen composition does not count as a new shot.
- Each important event, cost, choice, consequence, and causal detail gets a dedicated visual beat.
- Each meaningful shot has 2–3 planned keyframe placements. Static holds use one keyframe only when no action, emotion, or prop state changes.

## Historical/evidence extension

For a historical, institutional, or historical-economy episode, create two additional tables.

Evidence ledger:

`beat | factual claim | evidence status | source | period/date | evidence object | uncertainty note | reconstruction label`

Layer-action map:

`shot | spoken clause | protagonist | one decisive object | one main action | background layer | character layer | prop before/after layer | foreground layer | entry order/direction | result lock frame`

Rules:

- Use only `史料确认`, `学界推断`, `艺术化重现`, or `存在争议` as evidence status values.
- Give every shot one primary action. Split a shot when it contains multiple independent actions that cannot be read instantly.
- Use maps as story actions: reveal a route, move a boundary, extinguish a city, cut a supply line, or connect a person to a place. Do not use a static map as decorative background.
- Add exact Chinese labels in ChatCut, not inside generated artwork.
- Do not create image-to-video prompts. Translate the layer-action map directly into ChatCut motion.

## Required beat labels

- Question hook
- Setup
- Decision
- Hidden obligation
- Escalation 1
- Escalation 2
- Reversal
- Concept reveal
- Three-detail mapping
- Resolution

## Production pack

- Verified topic note and source list
- Protagonist card
- Beat sheet
- Final narration
- Scene-level TTS map with actual durations
- Original character and background prompts/assets
- Caption JSON
- Preview frames
- Final MP4 and verification report
- 3:4 cover (1080×1440)
- 4:3 cover (1440×1080), independently recomposed
- Publishing copy with cover headline, video title, and video description
