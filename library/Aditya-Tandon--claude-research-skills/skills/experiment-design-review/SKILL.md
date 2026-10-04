---
name: experiment-design-review
description: >
  Review and strengthen an experimental design by suggesting ablations, identifying missing controls,
  recommending metrics, and flagging methodological issues. Use this skill whenever the user describes
  an experiment they're planning and wants feedback on the design. Triggers include: "review my experiment",
  "what ablations should I run", "am I missing any controls", "is this experimental setup sound",
  "what metrics should I use", "help me design this experiment", "what should I control for",
  "review my methodology", or any request to improve or validate an experimental plan before running it.
  Also trigger when the user describes results and asks whether the experimental design was sufficient
  to support the conclusions drawn.
---

# Experiment Design Review

Review a proposed experiment and produce a structured critique with concrete suggestions for ablations, controls, and metrics. Output goes to the Obsidian vault.

## Input

The user describes an experimental setup. This could range from:
- A detailed protocol with baselines, metrics, and hyperparameters
- A rough sketch ("I want to test whether X improves Y by swapping Z")
- A completed experiment where they want a post-hoc design review

Extract or ask for:
1. **Research question** — what are you trying to show?
2. **Independent variable(s)** — what are you changing?
3. **Dependent variable(s)** — what are you measuring?
4. **Proposed setup** — model, dataset, training protocol, evaluation procedure
5. **Current baselines** — what comparisons are planned?
6. **Compute/time budget** — how many experiments can you realistically run?

The budget question matters — suggesting 50 ablations to someone with 1 GPU for a week wastes everyone's time. Tailor suggestions to what's feasible.

## Execution

**Create tasks before starting.** Decompose into explicit tasks (e.g., "Check vault for prior
attempts", "Identify core claim", "Audit controls", "Design ablations", "Review metrics",
"Check known pitfalls", "Write vault note"). Execute one at a time, marking each complete.
Include a verification task to confirm the reproducibility checklist is filled in.

## Review Process

### Step 0: Check the vault — has this already been tried?

**Before designing anything, search the vault for prior attempts at the same experiment or gate.**
Rejected/validated artifacts constrain the search space — re-running a settled question wastes
compute, and building on a prior result is almost always the right move. Grep by project, then by
the experiment's key terms and its metric:

```bash
grep -rl 'project: "<project>"' <vault>/ | xargs grep -lEi '<experiment keywords / metric>' 2>/dev/null
grep -rl 'status: refuted' <vault>/ | xargs grep -l 'project: "<project>"' 2>/dev/null   # already-refuted list
```

For each hit, read its `gate_verdict` + `gate_value`. Then decide, explicitly:
- **Already answered (validated or refuted):** do **not** re-run. Cite the note; either build the
  next increment on it or, if you believe it's wrong, design a *targeted* re-test that says why.
- **Partially done / different regime:** design the delta only; set the prior note as a `parent`.
- **Superseded premise:** if a newer result re-baselined the assumption this experiment rests on
  (e.g. a driver/hardware change), design against the *current* baseline, not the stale one.

State what you found (or "no prior attempt in the vault") in the experiment note. This mirrors the
refuted-list check `idea-bouncer` runs at direction-generation — apply it here too.

### Step 1: Identify the core claim

What conclusion does the user want to draw from this experiment? State it explicitly — this anchors everything else. A well-designed experiment is one where a positive result convincingly supports the claim and a negative result is informative.

### Step 2: Check controls

For each independent variable, verify:
- **Isolation**: does the experiment change exactly one thing? If multiple things change simultaneously, the result is uninterpretable
- **Fair comparison**: are baselines given the same compute budget, data, hyperparameter tuning effort?
- **Null hypothesis**: what would a "no effect" result look like? Is it distinguishable from a bug?

Flag missing controls. Common ones researchers forget:
- Random seed variance (run N>1 seeds)
- Hyperparameter sensitivity (did you tune the baseline as carefully as your method?)
- Dataset splits (are train/val/test truly independent?)
- Compute-matched baselines (your method uses 2x parameters — is the improvement from the method or the capacity?)

**Confound inventory (feeds the Stage 5 gate design checklist):** List everything that
differs between experimental arms in a table: variable, value per arm, and whether it's
the variable under test, pinned (same in both arms), or free (differs but not under test).
If more than one variable is free, the comparison cannot attribute the result. This table
is carried forward to Stage 5's gate design checklist clause 3.

### Step 3: Suggest ablations

Ablations should isolate the contribution of each component. For each proposed ablation:
- **What it tests**: which design choice does this validate?
- **Setup**: what exactly to change
- **Expected outcome if the component matters**: what should happen
- **Expected outcome if it doesn't**: what that would imply
- **Priority**: must-have / nice-to-have / only-if-time

Order ablations by information value per compute cost. The best ablation is cheap and resolves a big ambiguity.

### Step 3.5: VoI discriminant analysis (when multiple hypotheses compete)

**When multiple competing hypotheses exist for the same project/direction**, the most valuable
experiment is the one that discriminates between them — not one that confirms any single
hypothesis in isolation. This step is inspired by Murphy 2608.09696's Value-of-Information
criterion: ξ* = argmax_ξ Var_{p(M|D)}[E(y*|M, do(ξ))].

**Procedure:**

1. Check the vault for sibling hypotheses sharing the same `direction:` or `project:`:
   ```bash
   grep -rl 'direction: "<direction>"' <vault>/Hypotheses/<project>/ 2>/dev/null
   ```
2. For each pair of surviving hypotheses, identify the **divergence point** — the experimental
   condition where they make *different* quantitative predictions. If both hypotheses predict
   the same outcome for every feasible experiment, they are empirically indistinguishable and
   should be merged or distinguished on parsimony grounds (see Occam penalty in research-loop
   Stage 5).
3. Compute a VoI table:

   | Hypothesis pair | Divergence point | Predicted outcome (H_A) | Predicted outcome (H_B) | Discriminative experiment |
   |-----------------|------------------|-------------------------|-------------------------|---------------------------|
   | ... | ... | ... | ... | ... |

4. **Prioritize discriminative experiments over confirmatory ones.** One experiment that
   distinguishes H_A from H_B is worth more than two experiments that confirm H_A and H_B
   independently, because it eliminates a hypothesis rather than accumulating evidence for
   one. If an ablation from Step 3 happens to sit at a divergence point, promote it to
   critical priority.
5. If no divergence points exist for feasible experiments, state this explicitly — the
   hypotheses are empirically equivalent under current capabilities and should be compared
   on complexity (fewer parameters / assumptions wins).

**When only one hypothesis exists,** skip this step and note `voi_discriminant: "N/A — single
hypothesis"` in the output.

### Step 4: Review metrics

Check whether the proposed metrics actually measure what the user cares about:
- Are they standard in the field? (If not, justify why a non-standard metric is better)
- Do they capture all dimensions of the claim? (e.g., accuracy alone doesn't capture efficiency)
- Are they sensitive enough to detect the expected effect size?
- Would a hostile reviewer accept these metrics?

Suggest additional metrics if gaps exist. Common omissions:
- Efficiency metrics (FLOPs, wall-clock time, memory)
- Statistical significance (confidence intervals, not just point estimates)
- Qualitative analysis (error cases, failure modes)
- Scaling behavior (does the effect hold at different scales?)

### Step 5: Check for known pitfalls (and ground the design in the literature)

Search web and vault for:
- Known issues with the proposed evaluation methodology
- Papers that tried similar experiments and found unexpected confounds
- Standard practices in the field that the design deviates from
- **The standard method and the accepted validation targets/numbers** for this problem

**Sufficiency-checked proxy metrics (for expensive computations).** When the experiment
involves HPC runs, large-scale training, long simulations, or any computation where the
full evaluation is expensive enough to limit the number of runs: flag whether a cheap proxy
metric could substitute for the full computation. If a proxy is proposed or already in use,
require a sufficiency protocol (inspired by MDA's SBI sufficiency checks, Murphy 2608.09696):
- Run the full (gold-standard) computation on K spot-check cases (K ≥ 3, ideally 5-10).
- Compute the proxy metric on the same cases.
- Pre-register the acceptable divergence threshold: |proxy - gold| < ε for what ε?
- If divergence exceeds ε on any spot-check, the proxy is invalid for this regime — fall
  back to the full computation or find a better proxy.
- Record: `proxy_metric: "<cheap estimator>"`, `sufficiency_check: "K=<N> spot-checks,
  ε=<threshold>, max observed divergence=<value>"`.

**Ground the plan in the literature (required — see `references/vault-conventions.md` → "Literature Grounding"):** cite the relevant prior work inline where it informs the design (method, controls, validation targets, pitfalls), and **add each cited paper to the vault** as a `type: paper` note under `Papers/<project>/` with a "why it matters for us" line. Link them from the experiment note via `related`. If a proper review is warranted, run one (or spawn a subagent) and persist its key references as paper notes.

### Step 6: Synthesize recommendations

Prioritize recommendations by impact and cost. Group into:
- **Critical** — the experiment can't support the claim without this
- **Important** — significantly strengthens the evidence
- **Nice to have** — improves completeness but not essential

## Output Format

Read `references/vault-conventions.md` from the paper-triage skill for conventions.
Follow `references/writing-guide.md` for prose clarity in the Controls Assessment and Known Pitfalls sections.

If the experiment has a known `direction:` (from the hypothesis it tests, or session context),
write to `<vault>/Experiments/<project>/<direction>/<experiment-name>.md`. Otherwise write to
`<vault>/Experiments/<project>/<experiment-name>.md`.

Create the `<project>` (and `<direction>`, if applicable) subdirectory if it does not exist.

```markdown
---
type: experiment
project: "<project>"
status: draft
domain: ["<tag1>", "<tag2>"]
created: <today>
sources: []
related: ["[[linked-notes]]"]
parents: ["[[parent-note-slug]]"]
produced_by: "experiment-design-review"
parent_types: ["<type-of-parent>"]
voi_discriminant: "<which competing hypotheses this experiment discriminates, or 'N/A — single hypothesis'>"
proxy_metric: "<cheap estimator used, if any, or 'none'>"
sufficiency_check: "<K spot-checks, ε threshold, max observed divergence, or 'N/A'>"
---

# Experiment: <name>

## Research Question

<what this experiment aims to show>

## Proposed Setup

<summary of the user's design>

## Design Review

### Controls Assessment

<what's well-controlled, what's missing>

### Recommended Ablations

| Priority | Ablation | Tests | Expected outcome |
|----------|----------|-------|-----------------|
| Critical | ... | ... | ... |
| Important | ... | ... | ... |
| Nice to have | ... | ... | ... |

### Metrics Review

<current metrics assessment + suggested additions>

### Known Pitfalls

<relevant issues from literature>

## Reproducibility Requirements

- [ ] All code committed to a feature branch before running
- [ ] Run command documented (exact flags, seeds, configs)
- [ ] Plotting scripts committed alongside generated figures
- [ ] Results written to a separate `result` note with code provenance fields:
      `code_commit`, `code_repo`, `code_branch`, `run_command`, `plots`
- [ ] Changes pass clean-commit-gate before PR submission

## Experiment Checklist

- [ ] <each concrete action item>

## Related Notes

<cross-links>
```

## After Writing

Give a concise summary: the biggest gap in the current design, the single most valuable ablation, and whether the design can support the intended claim as-is.
