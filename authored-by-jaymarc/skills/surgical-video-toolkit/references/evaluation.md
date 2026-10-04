# Evaluation protocol

The automated tests use generated color clips and tones. No performance claims
on surgical footage can be made from these tests.

For a first retrospective evaluation, select several authorized, de-identified
recordings spanning different scopes, recording layouts, and lighting conditions.
Keep evaluation cases separate from cases used to tune thresholds. Have the
surgeon mark important source intervals before reviewing the proposed cuts.
Retain those labels separately; do not automatically feed them into the protected
list when measuring unassisted candidate quality, which would inflate retention.

Record source ID, start/end seconds, label (important/dead-time/uncertain), reviewer,
and rationale. For disputed intervals, obtain adjudication or report uncertainty.

Measure:

- Important seconds removed / total labeled important seconds (primary).
- Important-event intervals touched by any removal.
- Fraction of proposed removals rejected or narrowed by the reviewer.
- Review time plus final editing time, compared with the same manual task.
- Final reduction in recording duration (secondary).
- Import success, missing media, audio drift, and boundary errors in Premiere.

Report case-level results and failure examples, not only pooled averages. Freeze
thresholds and software revision before evaluating the held-out recordings.
Define acceptable retention and usability criteria with the clinical owner before
running the evaluation. The tool does not determine those clinical criteria.
