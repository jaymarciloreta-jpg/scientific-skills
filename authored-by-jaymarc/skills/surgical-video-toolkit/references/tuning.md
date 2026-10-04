# Detection and review tuning

The candidate detector samples once per second at 64×64 grayscale resolution.
It proposes scope-out when corner mean exceeds 55/255, no-signal when whole-frame
mean is below 16/255, and low-motion intervals from mean absolute frame difference.
These are uncalibrated heuristics, not clinical classifications. Circular borders
can persist outside the patient; cropping can remove them inside the patient.
Grayscale cannot distinguish red-out from black frames by hue.

| Profile | Minimum low-motion run | Motion threshold |
|---|---:|---:|
| conservative (default) | 12 s | 1.2 |
| balanced | 5 s | 2.0 |
| aggressive | 3 s | 3.0 |

Profiles affect proposals only in the review workflow. No proposal is removed
without an explicit Remove decision. Choose a profile, generate a fresh review,
and inspect representative proposals before continuing. Keep false positives.
Cut endpoints can be narrowed within the proposed interval; protected intervals
are subtracted from removals. Cuts are rounded inward to frame boundaries.

Per-recording learned calibration, color/blur classification, and learning from
review decisions are not implemented. Save decisions to support later evaluation.
The review audit reports the final retained duration after overlaps and protected
intervals; raw candidate durations must not be interpreted as the final removal.
