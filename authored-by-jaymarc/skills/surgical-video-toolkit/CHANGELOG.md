# Changelog

## 2.0.0 — 2026-10-04

- Content-hash deduplication retains different recordings with identical names;
  manifest clip IDs are stable and original names are recorded separately.
- Explicit order-file support and timezone-consistent recording timestamps.
- Local visual review with thumbnails, short preview clips, Keep/Remove choices,
  adjustable cut bounds, saved browser drafts, and JSON decision export.
- All footage retained until a reviewer chooses removal; protected source moments
  override removal decisions. Source changes invalidate finalization.
- Reviewed cut lists and decision audit; validation rejects mismatched sessions,
  invalid ranges, and missing/duplicate decisions.
- Final Cut Pro 7 XML replaces the incorrect direct-Premiere FCPXML promise;
  actual source dimensions/rate, XML escaping, and linked mono/stereo audio.
- Highlight extraction composes the full selected edited interval across cuts
  and source files, retaining audio and refusing existing output files.
- Fresh resident guide, handoff instructions, tuning explanation, and evaluation
  protocol. Legacy detector retains footage unless `--auto-cut` is requested.

### Verification

Automated unit and synthetic-media integration tests plus a command-line
prepare → review decisions → finalize → XML export smoke test. Browser checks
covered default Keep, Remove selection, adjusted bounds, draft persistence, and
export-link generation. Tests use generated colors/tones, never surgical data.

No actual Premiere import or surgical-case performance evaluation has been run.
Mixed source formats and suspected variable frame rate require normalization;
only mono/stereo audio is supported by XML export. The VFR screen compares stream
rate metadata and does not establish full frame-timestamp constancy.

### Migration

Regenerate manifests: clip IDs now include content hashes. Use manifest IDs in
markers and protected interval files. The standard workflow is `review_cuts.py`
prepare/finalize; hand Premiere the resulting `.xml`, not `.fcpxml`. Do not mix
old filename-keyed cut lists with new manifests. Per-recording model calibration,
automatic teaching labels, and learning from feedback remain future work.
