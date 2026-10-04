# Surgical editing guide for residents

## What to ask the assistant

“Use surgical-video-toolkit to prepare a review of this recording. Keep all
footage until I approve cuts. Protect these important intervals: …”

1. **Locate the recording.** Work with copies in your approved local workspace.
   The tools do not modify source videos. Output previews contain the source
   imagery, so handle them like the original recording.
2. **Check recording order.** Confirm the manifest lists all chunks in the correct
   order. Files with identical names are not assumed to be duplicates.
3. **Protect important moments.** Identify source intervals that must remain.
   The assistant translates your timestamps into the protected-interval file.
4. **Open the review page.** Each proposed cut has a thumbnail, a short silent
   preview, and Keep/Remove controls. The default is Keep. Steady scope views,
   pauses, darkness, or bright corners do not establish that footage is expendable.
5. **Review proposed removals.** Inspect the full original interval when the short
   preview is insufficient. Adjust the proposed cut start/end to preserve context.
6. **Save decisions.** Click Download decisions, then Save decisions.json. A JSON
   copy option is available if downloads are blocked. The assistant applies this
   file to the matching review session and creates the reviewed cut list.
7. **Import the `.xml` into Premiere.** It is Final Cut Pro 7 XML, not `.fcpxml`.
   Check relinking, audio synchronization, and the first/last frame of every cut.
   Do not assume a structurally valid XML has passed a Premiere import test.
8. **Finish the teaching edit.** Refine pacing, add explanatory annotations, and
   export. Ask for a teaching highlight by its position on the reviewed timeline;
   the extraction script respects intervening cuts.

## Useful requests

- “Keep this steady anatomical view even though there is little motion.”
- “Protect seconds 125–148 in this source clip.”
- “Shorten this proposed removal; keep the two seconds before the action.”
- “Extract 20 seconds centered on 4:30 in the reviewed timeline.”

The current version proposes candidate cuts using image brightness and motion.
It does not recognize surgical phases, complications, landmarks, or clinical
importance. Automated teaching annotations and adaptive learning are future work.
