# Editing Surgical Videos with Claude + Premiere — Resident Guide

A practical guide to turning a raw, multi-hour OR recording into a watchable edit or
a set of teaching clips, without spending your weekend scrubbing through black
screens. You drive it in plain English; Claude does the tedious triage; you finish
the storytelling in Premiere.

You do **not** need to know how to code. Every step below is something you ask Claude
for in normal language. The exact commands are included only so you understand what
is happening under the hood.

---

## 1. The mental model (read this once)

A surgical recording off the capture box is messy in predictable ways:

- It's **split into many short MP4 files** (often ~15 minutes each) because the box
  auto-chunks long recordings.
- The chunks are sometimes **copied into several folders** that look like different
  camera angles but are actually identical copies.
- Most of the runtime is **dead time**: the scope sitting out of the patient, the
  blue/black standby screen, and long idle stretches where nothing is happening.

The job splits cleanly into two halves, and that's the whole point of this workflow:

> **Claude** does the mechanical, high-volume work — putting the chunks in order and
> finding/removing the dead time. **Premiere** is where *you* do the judgment work —
> trimming for story, adding titles, and exporting.

Claude works **non-destructively**. It reads your footage and produces a small
"edit list" — a file that says *"play this clip from 10:32 to 11:38, then this one…"*
Your original videos are never changed. You import that edit list into Premiere and a
finished timeline appears, ready to refine.

There are three things you can ask for:

1. **A rough cut** — the whole case with dead time removed, as a Premiere timeline.
2. **Highlight / "marker" clips** — short fixed-length clips (e.g. 30 s) of specific
   moments, as flat MP4s you can drop into a talk.
3. **Both.**

---

## 2. Before you start

- Get the case footage onto your computer (or a connected Dropbox/drive folder).
  Note the folder path.
- Have **Adobe Premiere Pro** installed for the finishing step.
- Open Claude in **Cowork mode** and give it access to the folder with the footage.
  (Cowork is the desktop mode where Claude can see your files and run the tools.)

That's it. You don't install anything else — the video tools Claude needs run inside
its sandbox.

---

## 3. Making a rough cut (the common case)

### Step 1 — Point Claude at the footage

Just describe what you have. For example:

> "I have a sinus case recording in the folder `Medina_DamianGabriel__20260423`.
> It's split into a bunch of MP4 chunks. Please stitch them into the right order and
> make a rough cut with the dead time removed, ready for Premiere."

Claude will first **align** the chunks — figuring out the true chronological order
from each file's embedded recording time (not the filename, which often lies). If
there are duplicate folders, it keeps one and ignores the copies. It'll tell you the
total runtime so you can sanity-check (e.g. "5 h 47 m across 24 chunks").

### Step 2 — Let it find the dead time

Claude samples the footage once per second and scores three things:

- **Scope-out** — when the scope leaves the patient, the dark circular edges of the
  endoscope image disappear and the corners of the frame go bright. That's how it
  knows the scope is out.
- **No-signal** — near-black frames: the standby screen, a capped scope, a blackout.
- **Idle** — the scope is inside but nothing is moving for a while. Brief pauses are
  kept so the video doesn't feel chopped; only longer dead stretches are cut.

It then writes a couple of spreadsheets you can actually read:

- a **KEEP** list (every segment it's keeping, with timecodes), and
- a **REMOVED** list (every cut, with the reason — scope-out, no-signal, or idle).

This transparency matters: when an attending asks "what did you cut and why," the
answer is right there in the REMOVED spreadsheet.

### Step 3 — Choose how aggressive to be

Claude defaults to a **balanced** trim: clear dead time gone, with a half-second of
padding around every cut so nothing slams. You can ask for:

- **Conservative** — only obvious long dead time goes. Best for grand rounds or
  anything that needs to be defensible.
- **Aggressive** — trims harder for a snappy social/sizzle cut.
- **"Keep the lens-on-tissue moments"** — if it cut the red-out moments where you had
  the scope right on the mucosa, just say so and it keeps those.

Re-running is cheap (a few minutes for a multi-hour case), so iterate freely:

> "That's close, but it cut a few spots where the field was just bright and bloody —
> can you be less aggressive about scope-out and regenerate?"

### Step 4 — Get the Premiere timeline

Claude builds two files describing the same cut:

- **`..._ROUGH_CUT.fcpxml`** — import this into Premiere.
- **`..._ROUGH_CUT.edl`** — a backup, in case FCPXML import acts up.

It'll also write a short **README_edit** summarizing what was kept and removed.

### Step 5 — Finish in Premiere

1. **File → Import** and choose the `..._ROUGH_CUT.fcpxml`.
2. Premiere builds a sequence with every kept clip already laid end to end in order.
3. If it asks to **relink media**, point it at the case folder. (If there are
   identical duplicate folders, any one works.)
4. Each clip is named `<source> cutNNN`, so you can trace any clip back to the raw
   footage.
5. Now do the human part: trim for story, drop steps that don't teach anything, add
   titles for each surgical step, and add a de-identified slate if it's leaving the
   institution.
6. **File → Export → Media** when you're happy (H.264, "Match Source" for full
   quality, or a smaller preset for a quick review copy).

If the FCPXML ever refuses to import on your Premiere version, import the `.edl`
instead — same cuts.

---

## 4. Making highlight / marker clips

When you just want short clips for a talk or a tweet — not the whole case — ask for
markers. Two ways to tell Claude where:

**By where it is in the footage:**

> "Pull a 30-second clip starting at 12:30 in chunk `Ch1_004_CH002_V.MP4`, and
> another at 21:05."

**By where it is in the rough cut** (handy if you noted timestamps while watching the
rough cut):

> "From the rough cut, grab 20-second clips centered on 45:10 and 1:12:40."

These come out as clean, standalone **MP4 files** (1080p, H.264 + audio) that play
anywhere — PowerPoint, Keynote, email, upload. They're separate from the rough cut,
so you can ask for them on their own.

---

## 5. Phrasebook — what to actually type

| You want… | Say something like… |
|-----------|---------------------|
| The whole workflow | "Stitch these OR chunks in order and make a Premiere rough cut with dead time removed." |
| A gentler cut | "Use the conservative profile — only cut obvious long dead time." |
| A tighter cut | "Trim it harder, this is for a 2-minute social clip." |
| Keep red-out moments | "Don't cut the spots where the lens is pressed against tissue." |
| Just clips | "Pull three 30-second highlight clips at these timestamps: …" |
| Understand a cut | "Why did you remove the section around 1:05:00?" (it'll cite the REMOVED list) |
| A flat trimmed file | "Instead of a timeline, give me one trimmed MP4 of just the kept footage." |

---

## 6. Good habits

- **Spot-check before you trust it.** On a new *type* of case, ask Claude to render a
  couple of clips right at its cut/keep boundaries and eyeball them. Kept bits should
  show real surgery; cut bits should be genuinely empty.
- **Keep the surgeon in the loop on the profile.** Balanced is a safe default, but
  confirm before a high-stakes use.
- **De-identify before anything leaves the building.** Surgical video can be PHI —
  check for name overlays, the standby screen, and the slate, and follow the media-
  release policy.
- **Originals are safe.** Nothing in this workflow edits your source files. The worst
  case of a bad cut is re-running it.

---

## 7. What's happening under the hood (optional)

For the curious — the same steps as terminal commands. Claude runs these for you; you
never have to. They live in the `scripts/` folder of the toolkit.

```bash
# order the chunks
python align_chunks.py "/path/to/CASE_folder" -o OUT/manifest.csv

# find and remove dead time
python detect_deadtime.py --manifest OUT/manifest.csv --outdir OUT \
    --name CASE --profile balanced

# build the Premiere timeline
python build_timeline.py --keep OUT/CASE_KEEP_segments.csv --manifest OUT/manifest.csv \
    --outdir OUT --name CASE_ROUGH_CUT --title "CASE - dead-time removed"

# (optional) pull a highlight clip
python extract_markers.py --outdir OUT/markers --length 30 \
    --manifest OUT/manifest.csv --at Ch1_004_CH002_V.MP4=12:30
```

Deeper detail lives in `references/tuning.md` (how the thresholds work) and
`references/premiere_handoff.md` (Premiere import/export specifics).

---

*Questions or a case that behaves oddly? Bring the footage path and what looked wrong
to Claude — "the cut kept too much black at the start," "it split one step into three
clips" — and iterate. The tools are made to be re-run.*
