---
name: research-loop
description: "Orchestrate a full research investigation from question to vault-persisted results. Two modes: 'immersive' (user in the loop at every decision gate, builds deep understanding) and 'autonomous' (agents execute independently, user reviews final results). Triggers: \"research this\", \"investigate\", \"start a research loop\", \"explore this question\", \"run the research pipeline\", or any request to systematically investigate a research question with hypothesis testing and vault integration. Also activates on \"immersive mode\" or \"autonomous mode\" when paired with a research goal."
version: 2.1.0
---

# Research Loop — Orchestrated Investigation Pipeline

A full research pipeline that chains your research skills and autoresearch into a coherent
investigation workflow. Two modes control how much you're in the loop.

Grounded in the categorical discovery framework (Wang & Buehler 2026): typed artifact provenance,
formal gate records, search/discovery distinction, and evidence transport on pivots.

## Session Usage Safety

**Primary rule: checkpoint at every stage boundary, unconditionally.** At the end of each
pipeline stage, write/update a `type: checkpoint` note (produced_by: `research-loop-checkpoint`)
recording: current stage, what's done, what remains, git branch + worktree path, and any
unpersisted intermediate results. This is cheap (~10 lines) and makes every stage boundary a
resume point. Agents cannot reliably introspect their own context usage, so do not rely on
usage estimation as the main safety mechanism.

**Emergency fallback:** if an agent does estimate it is near its context/session limit
mid-stage, it MUST additionally:

1. **Commit or stash all current work** — `git stash` or `git commit -m "WIP: <stage> checkpoint"`
2. **Write a checkpoint note** (`type: checkpoint`, `status: draft`) as above
3. **Stop cleanly** — do not attempt to start a new stage or iteration

This prevents mid-task interruption where work is lost because the agent ran out of
context window or API usage. A half-finished experiment with no checkpoint is worse
than a stopped experiment with a clear resume point.

**For autonomous agents launched via `claude -p`:** Each agent should include this
preamble in its prompt:

```
SAFETY: Write a type: checkpoint note to .vault/ at every stage boundary
(stage, done, remaining, branch, worktree). If you believe you are near your
context or session limit mid-stage, stop immediately: commit or stash all code
changes, update the checkpoint note, and exit cleanly. Do not start new
iterations you cannot finish.
```

## Task-Based Execution (mandatory)

**Before starting any work, decompose the current scope into explicit tasks and create them.**
Do not list what needs to be done in prose and then start working — create tasks first, then
execute them one at a time, marking each complete before starting the next.

**Why:** Agents on long research work drift. They start investigating X, encounter Y, follow
it, and lose the thread. A task list anchors focus. It also enables resumption — if context
runs out, the task list shows what's done vs remaining.

**Rules:**

1. **Create tasks before executing.** At each pipeline stage, decompose the stage into 2–6
   concrete tasks (e.g., "Search vault for prior work on X", "Formalize H₀/H₁ for Y",
   "Write stress-test note to vault"). Create all of them, then start the first one.
2. **One task at a time.** Mark a task `in_progress` before starting it. Mark it `completed`
   when done. Do not work on multiple tasks simultaneously.
3. **Tasks may be revised.** If mid-execution you learn something that changes the plan,
   update or replace pending tasks — but do so explicitly. Add a brief note on why the plan
   changed. Never silently abandon a task.
4. **Stage-level tasks, not micro-tasks.** "Run partial correlation analysis" is a good task.
   "Open file X" is not. Each task should represent a meaningful unit of research progress.
5. **Verification task at the end.** Every stage's task list should end with a verification
   step: cross-check results, confirm vault notes were written, validate gate records.

**For autonomous agents (`claude -p`):** Include this in the agent prompt:

```
EXECUTION: Decompose your work into explicit tasks before starting. Create each task,
execute them one at a time (mark in_progress → completed), and include a final
verification task. If the plan changes mid-execution, update pending tasks explicitly
with a reason. Do not work without an active task.
```

**For immersive sessions:** The orchestrating agent (you) should maintain the task list.
Present it to the user at stage boundaries so they can see progress and redirect if needed.

## Pipeline State & Resumability

The pipeline is **not** one long prompt chain. The checkpoint note is the source of truth,
and any session (on any machine) can resume from it. One live checkpoint note per direction:
`Hypotheses/<project>/<direction>/checkpoint.md`, updated at every stage boundary.

**Checkpoint frontmatter (machine-readable — the driver script parses these):**

```yaml
type: checkpoint
project: "<project>"
direction: "<direction-slug>"
status: draft            # set to archived when the direction concludes
stage: "6a"              # last completed stage
next_action: "evaluate gate for h2 in ../h2-worktree"   # imperative, self-contained
worktree: "../h2-worktree"
branch: "experiment/20260707/h2"
machine: "my-hpc-cluster"  # where the worktree/job lives (hostname or alias)
job_id: "48211937"       # scheduler job id, if execution was submitted to a queue
job_scheduler: slurm     # slurm | pbs | none
resume_after: ""         # optional ISO timestamp hint
```

**Resuming:** `scripts/research-loop-driver.sh <project>` finds the live checkpoint,
checks any pending scheduler job (squeue/qstat), and either reports "still queued/running"
or dispatches `next_action` via `claude -p`. Run it manually, from cron, or after login on
any machine that has the vault synced. Because the vault is git-synced across machines, a
checkpoint written on the HPC is resumable from the laptop and vice versa — but only the
machine named in `machine:` can touch that worktree.

**Long-running cluster jobs:** the execution stage on an HPC must submit (sbatch/qsub),
write `job_id` + `job_scheduler` into the checkpoint, sync the vault, and **exit** — never
babysit a queue inside an agent session. The driver picks up when the job finishes.

## Stage-Local Metrics (no single global metric)

Real investigations — physics especially — do not optimize one metric end-to-end. The
pipeline therefore treats metrics as **stage-local and hypothesis-local**:

- Each hypothesis pre-registers its **own** Metric + gate at Stage 5. Different hypotheses
  in the same direction may gate on completely different quantities (a trigger efficiency,
  then a background rejection, then a significance).
- **Plateau detection (Stage 6.5) is per metric-thread**, never across metrics: the
  prequential structure estimate is only meaningful within a single metric's trace. When
  the metric changes between stages, start a fresh trace; do not concatenate.
- **Changing metrics is normal progress, not a regime transition.** Moving from "does the
  preselection work" to "what is the expected significance" is the same schema with a new
  gate. It becomes a regime transition only when artifact *types* or *operations* change
  (new kinds of evidence, new analysis morphisms) — that's when the Kan audit fires.
- Each result note records which metric governed it (`gate_metric`), so the direction's
  history is a sequence of gated claims, not one metric curve.

## Provenance & Gate Requirements

**Every vault note produced by this pipeline MUST include typed provenance fields:**

```yaml
parents: ["[[parent-note-slug]]"]
produced_by: "<skill-name>"
parent_types: ["<type1>", "<type2>"]
```

**Every hypothesis evaluation or experiment result MUST include gate record fields:**

```yaml
gate_verdict: accepted | rejected | inconclusive
gate_metric: "<what was measured>"
gate_threshold: "<pre-registered decision rule>"
gate_value: "<observed value>"
```

See `vault-conventions.md` for the full schema registry and field semantics.

## Modes

### Immersive Mode (default for Cowork and interactive sessions)

You're a thinking partner, not a task runner. The user builds understanding at every step.

**Behaviour:**
- Present findings conversationally, not as reports
- At each decision gate: show the data, explain trade-offs, ask what the user thinks *before* offering your recommendation
- Push back on the user's intuitions when the data disagrees — this is where learning happens
- Never auto-advance past a gate. The user says "continue" or redirects
- Use `AskUserQuestion` at decision gates with concrete options informed by the analysis so far
- Write intermediate findings to vault as `status: draft`, upgrade to `reviewed` after user confirms

**Decision gates (user must explicitly approve):**
1. After direction generation → which direction(s) to pursue?
2. After stress-test → does the hypothesis survive? Pivot or proceed?
3. After experiment design → are the ablations/controls right?
4. After each execution result → interpret together before moving on
5. After synthesis → what did we learn? What's next?
6. **NEW:** After plateau detection → search exhausted? Regime transition needed?

### Autonomous Mode (for Claude Code CLI, overnight runs, batch processing)

Agents execute independently. User reviews final results.

**Behaviour:**
- Use autoresearch configs for execution (Goal/Scope/Metric/Direction/Verify)
- Fan out parallel hypotheses via `claude -p`
- Write results directly to vault as `status: draft`
- Only surface final summary and decision points that genuinely need human input
- Use autoresearch's mechanical verification and auto-rollback

**Autonomous decision rules (pre-registered, no human needed):**
- Direction selection: pick highest information-value-per-effort
- Hypothesis survival: pre-registered p-value and effect size thresholds
- Experiment execution: autoresearch loop with mechanical metric
- Convergence: stop when all hypotheses resolved or compute budget exhausted
- **NEW:** Plateau → regime transition: if 3+ iterations show no metric improvement AND no new artifact types emerging, flag for human review

## Pipeline Stages

### Stage 0: Probe (optional, recommended for new domains)

**Purpose:** Surface hidden assumptions before committing to a direction.

- Immersive: Interactive `/autoresearch:probe` — you answer persona questions
- Autonomous: `/autoresearch:probe --mode autonomous`

**Output:** Constraint set, assumption ledger, refined goal statement.

**Vault output:** `<vault>/Hypotheses/<project>/<goal-slug>-probe.md` with `type: probe`
**Provenance:** `produced_by: "autoresearch-probe"`, `parents: []`, `parent_types: []`

### Stage 0.5: Literature Grounding (required before direction generation)

**Skill:** `paper-triage`

**Purpose:** Ground the investigation in prior work before generating directions. Vault
conventions *require* literature grounding for hypothesis, experiment, and result notes —
this stage is where it happens, not as an afterthought.

- Search for the 3-5 most relevant works: (i) the standard method, (ii) accepted validation
  targets/numbers, (iii) known pitfalls.
- Triage each into `Papers/<project>/` via paper-triage (one note per paper, with a
  "why it matters for us" section).
- Immersive: present the landscape — "here's what exists, here's the gap".
- Autonomous: triage, then proceed; papers feed Stage 1 as parents.

**Vault output:** `Papers/<project>/<author-year-short-title>.md` per paper
**Provenance:** `produced_by: "paper-triage"`, `parents: []`, `parent_types: []`

### Stage 1: Direction Generation

**Skill:** `idea-bouncer` (Mode 1: Research Directions)

**Purpose:** Generate 4-6 candidate research directions with formalised hypothesis tests.

- Immersive: Present directions with H₀/H₁, trade-offs, scout experiments. User picks.
- Autonomous: Rank by information-value-per-effort, pick top 1-2.

**Decision gate (immersive):** "Here are 4 directions. Which do you want to pursue, and why?"

**Direction rejection logging (REQUIRED at this gate).** When the user selects directions,
log the ones they rejected with their reasons to the direction rejection log
(`<vault>/Hypotheses/<project>/<project>-direction-rejections.md`). Ask: "You didn't pick
[X] — what made it uninteresting?" This taste signal constrains future direction generation
more precisely than gate rejections. See idea-bouncer Output section for format.

**Vault output:** `<vault>/Hypotheses/<project>/<direction-slug>/hypothesis.md` (create the
`<direction-slug>` subfolder here — this is where the direction is born) with `status: draft`,
`direction: <direction-slug>` (this slug propagates to all downstream artifacts of this thread)
**Provenance:** `produced_by: "idea-bouncer"`, `parents:` the Stage 0.5 paper notes and any
probe/prior notes that informed the directions, `parent_types:` their types.

### Stage 2: Stress Test

**Skill:** `hypothesis-stress-test`

**Purpose:** Attack the chosen direction(s) — counterarguments, confounds, contradictory evidence.

- Immersive: Present each critique. User responds. Model pushes back. Iterate until the
  hypothesis either collapses or hardens. This is where understanding deepens most.
- Autonomous: Single-pass stress test, then **blind-judged verdict** (see below).

**Verdict must not be self-graded.** The agent that generates critiques must not also judge
whether the hypothesis survived them — same-agent grading rationalises its own attacks away
(the categorical framework's V_b gate must be independent of the proposer; cf. Builder/Breaker's
6.4% acceptance rate). Route the survival verdict through `/autoresearch:reason`: the hypothesis
+ critiques go in as opposing positions, blind judges converge on a verdict.

**Gate mapping (pre-registered, computable from the skill's actual output):** the
hypothesis-stress-test skill emits a categorical `robustness:` rating. Map it directly:

| robustness | gate_verdict | action |
|---|---|---|
| `robust` | accepted | proceed |
| `promising-but-fragile` | accepted | proceed, carry the listed confounds into Stage 4 as required controls |
| `weak` | rejected | pivot or reformulate |
| `underdetermined` | inconclusive | autonomous: flag for human; immersive: gather the missing info |

**Reviewer fixes enter as hypotheses, not patches.** When the stress test (or any reviewer)
proposes a correction or improvement to the hypothesis, that suggestion must enter the
pipeline as a testable claim — not be adopted as a patch. The concern may be wrong: test it.
If the correction is vindicated, adopt it with evidence. If it's refuted, the original
stands stronger for having survived the challenge. Suggestions from a reviewer should enter
as hypotheses, not patches.

**Decision gate (immersive):** "The hypothesis survived these attacks but has these weaknesses.
Do you want to proceed, modify the hypothesis, or pivot?"

**Vault output:** a **new child note** at `<vault>/Hypotheses/<project>/<direction-slug>/stress-test.md`
— never mutate the original hypothesis note in place (append-only/supersession semantics; in-place
mutation destroys the pre-test state and breaks endofunctoriality). Set the original note to
`status: archived` with `superseded_by: ["[[<project>/<direction-slug>/stress-test]]"]` (path-qualify
the wikilink: `hypothesis.md`/`stress-test.md` are the same filename in every direction folder, so
a bare `[[stress-test]]` is ambiguous across the vault). Child note carries the stress-test results,
robustness rating, and gate record:
```yaml
gate_verdict: accepted | rejected | inconclusive   # from the mapping table above
gate_metric: "categorical robustness rating (blind-judged via /autoresearch:reason)"
gate_threshold: "robust or promising-but-fragile to proceed"
gate_value: "<the rating>"
```
**Provenance:** `produced_by: "hypothesis-stress-test"`, `parents: ["[[<project>/<direction-slug>/hypothesis]]"]`, `parent_types: ["hypothesis"]`

### Stage 3: Cross-Field Synthesis (optional, when relevant)

**Skill:** `cross-field-synthesis`

**Purpose:** Find analogous formalisms, methods, or results in other fields.

- Immersive: "Here's how [other field] thinks about this problem. Does this framing help?"
- Autonomous: Write synthesis note, link to hypothesis.

**Vault output:** `<vault>/Synthesis/<project>/<concept-bridge>.md`
**Provenance:** `produced_by: "cross-field-synthesis"`, `parents:` the hypothesis/paper notes being bridged, `parent_types:` their types.

### Stage 4: Experiment Design

**Skill:** `experiment-design-review`

**Purpose:** Design ablations, identify controls, recommend metrics, flag pitfalls.

**VoI prioritization (REQUIRED when multiple hypotheses survive Stage 2).** Before designing
individual experiments, check whether multiple hypotheses survived the stress test for the
same direction. If so, identify experimental conditions where their predictions *diverge*
quantitatively. Prioritize experiments at those divergence points — one discriminative
experiment is worth more than two confirmatory ones, because it eliminates a hypothesis
rather than accumulating evidence for one.

Formally (Murphy 2608.09696, Eq. 4-5): the optimal experiment maximizes between-hypothesis
variance of the predicted outcome:

```
ξ* = argmax_ξ Var_{p(M|D)}[ E(y* | M, do(ξ)) ]
```

In practice, this means: for each candidate experiment, ask each surviving hypothesis to
predict the outcome. If they all agree, the experiment has zero VoI for model selection —
deprioritize it unless it serves a separate purpose (establishing a baseline, validating
an assumption). If they disagree, that experiment discriminates. Design it first.

If all hypotheses make the same prediction for every feasible experiment, they are
empirically indistinguishable under current capabilities — compare on parsimony (fewer
parameters / assumptions wins; see Occam penalty at Stage 5).

- Immersive: Present the VoI table from `experiment-design-review` Step 3.5. Ask: "These
  hypotheses disagree most at [X]. Should we design the experiment to target that divergence?"
- Autonomous: Automatically prioritize discriminative experiments; design confirmatory ones
  only for the surviving winner after discrimination.

**Decision gate (immersive):** "Here's the experiment plan. Are these the right ablations? What's missing?"

**Vault output:** `<vault>/Experiments/<project>/<direction-slug>/<experiment-slug>.md`
**Provenance:** `produced_by: "experiment-design-review"`, `parents: ["[[<project>/<direction-slug>/hypothesis]]"]`, `parent_types: ["hypothesis"]`

### Stage 5: Hypothesis Decomposition & Execution Config

**Skill:** `agent-hypothesis-gen`

**Purpose:** Break the experiment into independently testable sub-hypotheses with execution plans.

- Immersive: Present decomposition. User validates H₀/H₁ formulations and decision rules.
- Autonomous: Generate autoresearch configs directly.

**Blind branch pre-registration (default format).** When pre-registering a gate, declare
the possible outcomes without predicting which will occur. The format to default to is
outcome branches with no prediction offered — e.g., MINIMUM-REAL / MONOTONE / ANOMALOUS /
INCONCLUSIVE. This makes the "surprising" branch as reportable as the expected one. If you
predict an outcome, state the prediction explicitly and separately from the decision rule;
the rule must be symmetric (same action regardless of which branch fires).

**Output format depends on mode:**

**Immersive output:** Standard agent prompts (user runs or reviews each)

**Autonomous output:** Autoresearch-compatible configs:

```yaml
# Auto-generated autoresearch config for H1
Goal: <hypothesis H₁ statement>
Scope: <files/scripts involved>
Metric: <test statistic command that outputs a number>
Direction: <higher_is_better | lower_is_better>
Verify: <command to run>
Guard: <regression check, e.g., existing tests must still pass>
Iterations: <estimated iterations>
# Pre-registered gate — evaluated mechanically by run-hypothesis.sh, NOT by the agent:
GATE_CMD: <command printing the final test statistic (may differ from Metric, e.g. p-value)>
GATE_OP: <gt | lt>
GATE_THRESH: <pre-registered threshold from the hypothesis decision rule>
```

#### Gate Design Checklist (mandatory before execution)

Every pre-registered gate must pass this checklist before the experiment launches.
The checklist exists because the pipeline already records failures well — the weakness
is upstream, at design time. Failures cluster into four classes, each with a cheap
preventative encoded below.

**1. Sensitivity clause — can the gate see the defect it exists to exclude?**

State, before running: *what would this gate report if the defect were present?*
If you can't answer, the gate isn't specified. Where feasible, run the gate once
against a deliberately broken arm (a matched-arm A/B). A gate that passes on both
broken and correct code is not a gate — it's an identity.

```yaml
# In the hypothesis/experiment note:
gate_sensitivity: "Tested: injecting <defect> produces gate_value = <X>, which
  <crosses/does not cross> the threshold. The gate discriminates."
# OR:
gate_sensitivity: "Not tested — <justification why a broken-arm test is infeasible>"
```

**2. Reference-through-the-same-pipeline — is the reference value comparable?**

Any gate quoting agreement with a known answer must quote *two* numbers: deviation
from the ideal/textbook value, AND deviation from that value pushed through the
identical estimator on the identical grid/ladder/pipeline. Only the second is
attributable to the code. The first mixes physics (finite-size effects, truncation,
approximation) with solver error and cannot indict either.

```yaml
gate_reference_raw: "<deviation from ideal>"
gate_reference_pipeline: "<deviation from ideal-through-same-pipeline>"
# The gate threshold applies to gate_reference_pipeline, not gate_reference_raw.
```

**3. Confound inventory — what else differs between arms?**

List everything that differs between the experimental arms. Name the variable
under test. Declare which confounds are pinned (same value in both arms) and
which are free. If more than one variable is free, the comparison cannot attribute
the result to any single cause.

```markdown
## Confound Inventory
| Variable | Arm A | Arm B | Status |
|----------|-------|-------|--------|
| Backend  | GPU   | CPU   | **under test** |
| Stopping rule | fixed sweeps | convergence | ⚠ FREE — must pin |
| Bond dimension | 64 | 64 | pinned |
| Initial state | random seed 42 | random seed 42 | pinned |
```

**4. Power check — can the experiment detect the effect?**

Before running, estimate: what is the largest effect *available* (the oracle
ceiling), and what is the noise floor? If the noise exceeds the maximum possible
effect, the experiment is underpowered by construction. State:

```yaml
gate_power: "oracle ceiling: <X>, noise floor: <Y>, ratio: <X/Y>"
# If X/Y < 3, the experiment likely cannot produce a conclusive result.
# Consider: more samples, tighter controls, or a different metric.
```

**5. Gate the null — does the control have its own validity criterion?**

A control ("the floor is X") needs evidence that X is the floor and not an
artefact of the analysis. State the null's validity check:

```yaml
gate_null_check: "<how we know the null/baseline is valid>"
# e.g., "Baseline verified against exact solution on L=4 lattice (Table 2)"
# BAD: "Baseline is whatever the code outputs with default settings"
```

**6. Sign-of-bias check — can the estimator's error flatter the result?**

Ask whether the estimator's systematic error can change sign across the
parameter range. An estimator that fails *flatteringly* (biased toward the
desired answer) makes agreement with theory uninformative — success carries no
information because failure was structurally impossible. State:

```yaml
gate_bias_direction: "Estimator bias is <toward/away from/sign-changing relative to>
  the target. <Justification>."
# If bias is toward the target: the gate must use a tighter threshold or a
# bias-corrected estimator. Agreement alone is not evidence.
```

**7. Minimum-sample clause — is n sufficient for the statistic?**

For any gate using a median, mean, or comparison statistic: state the minimum
n required for the statistic to be meaningful. A 2-of-15 median with a bootstrap
band spanning a factor of four is not a basis for a KILL verdict.

```yaml
gate_min_n: <N>
gate_n_justification: "<why this n is sufficient — power analysis, bootstrap, prior>"
```

**8. Instrument the guards — are safety margins computed or claimed?**

Any safety margin (Nyquist, convergence tolerance, numerical precision) must be
*computed and printed per run*, not asserted in a docstring. If a guard margin was
claimed at design time, add a runtime check that prints the actual value:

```bash
# In the run script, not just in documentation:
echo "GUARD: Nyquist margin = $(python compute_nyquist.py) (required > 0.125)"
```

#### Occam Penalty (mandatory when comparing competing hypotheses)

When multiple hypotheses pass their individual gates, prefer the simpler one unless the
complex model provides *substantially* better fit. Pre-register what "substantially" means
before running (e.g., "H_complex must beat H_simple by at least 2σ / 5% relative / BIC
difference > 10").

**Quantitative evaluation (use when hypotheses are parametric models):**

Compute the Bayesian Information Criterion for each:

```
BIC_m = k_m · ln(n) − 2 · ln(L̂_m)
```

where k_m = number of free parameters, n = number of data points, L̂_m = maximized
likelihood. Lower BIC is better — the k·ln(n) term is the Occam penalty. A complex model
that barely passes the gate should lose to a simpler model that also passes, because BIC
penalizes the extra parameters unless the data truly needs them.

| Hypothesis | k (params) | ln(L̂) | BIC | Gate verdict | Occam rank |
|------------|-----------|--------|-----|-------------|------------|
| H_simple   | ...       | ...    | ... | ...         | ...        |
| H_complex  | ...       | ...    | ... | ...         | ...        |

**ΔBIC interpretation (Kass & Raftery 1995):**
- |ΔBIC| < 2: negligible evidence — prefer the simpler model
- 2 ≤ |ΔBIC| < 6: positive evidence for the lower-BIC model
- 6 ≤ |ΔBIC| < 10: strong evidence
- |ΔBIC| ≥ 10: very strong evidence

**When BIC is not applicable** (non-parametric models, qualitative hypotheses, or when
likelihood is intractable): state this explicitly and compare on structural complexity
instead — number of assumptions, number of free choices, number of mechanisms invoked.
The principle remains: among hypotheses that pass the gate, simpler wins by default.

**Record in result note:** `model_complexity: "<description of DOF / parameter count /
structural assumptions>"`. When BIC is computed, also record `bic_value: <number>`.

**Checklist gate:** In autonomous mode, the agent must emit a one-paragraph
"gate design summary" confirming that clauses 1-8 are addressed (or explaining
why a clause is inapplicable) before proceeding to execution. In immersive mode,
present the checklist to the user for review.

Also emit a shell execution plan using **git worktrees** for isolation:

```bash
# --- Setup: create worktrees for parallel hypotheses ---
MAIN_BRANCH=$(git branch --show-current)
EXPERIMENT_BASE="experiment/$(date +%Y%m%d)"

git worktree add ../h1-worktree -b "${EXPERIMENT_BASE}/h1" 2>/dev/null
git worktree add ../h2-worktree -b "${EXPERIMENT_BASE}/h2" 2>/dev/null
git worktree add ../h3-worktree -b "${EXPERIMENT_BASE}/h3" 2>/dev/null

# --- Phase 1: Independent hypotheses (parallel, isolated worktrees) ---
(cd ../h1-worktree && claude -p "/autoresearch
Goal: <H1 goal>
Scope: <H1 scope>
Metric: <H1 metric>
Direction: <H1 direction>
Verify: <H1 verify>
Iterations: 10") &

(cd ../h2-worktree && claude -p "/autoresearch
Goal: <H2 goal>
...") &

(cd ../h3-worktree && claude -p "/autoresearch
Goal: <H3 goal>
...") &
wait

# --- Phase 2: For each worktree, run the post-execution pipeline ---
# (see Stage 6 below for the full sequence per hypothesis)
```

**Why worktrees:** Each hypothesis runs in a fully isolated copy of the repo on its own
git branch. No merge conflicts between parallel experiments. Failed hypotheses can be
discarded cleanly (just remove the worktree). Successful ones become PRs.

**Provenance:** `produced_by: "agent-hypothesis-gen"`, `parents: ["[[experiment-note]]"]`, `parent_types: ["experiment"]`

### Stage 5.5: Retro-Registration (for exploratory work that became load-bearing)

Exploratory work often grows into a decisive result without ever being pre-registered.
This is fine for exploration — the problem is when an unregistered result becomes the
basis for a conclusion.

**Rule:** Once it becomes clear that an exploratory finding is load-bearing (it will
ground a gate verdict, enter a comparison, or support a claim in a synthesis note),
that finding must be retro-registered *before its decisive run*:

1. Write a one-paragraph registration: the question, the metric, the decision rule,
   and the gate design checklist items (at minimum: sensitivity, confound inventory,
   power check).
2. Add it to the experiment or hypothesis note as a "Retro-registration" section,
   timestamped.
3. Then run the decisive experiment against the registered rule.

This closes most of the gap between exploration and rigor without adding ceremony to
genuine exploration. The moment a question turns from "curious" to "load-bearing" is
the moment it needs a written decision rule.

**In the vault note:** Result notes from retro-registered experiments should include
`registration: retro` in frontmatter (vs the default `registration: pre` for
properly pre-registered work). This is disclosure, not a penalty — retro-registered
results with proper gates are valid evidence.

### Stage 6: Execution (Git-Integrated)

Each hypothesis executes in its own git worktree. After execution, the pipeline
diverges based on outcome:

```
hypothesis execution (in worktree)
        │
        ├─ SPEC VIOLATION (spec_violation: flagged)
        │   → reject without evaluating gate
        │   → log to vault with spec_violation_detail
        │   → preserve branch under refs/experiments/
        │   → do not retry (same metric invites same exploit)
        │
        ├─ REJECTED (gate_verdict: rejected)
        │   → log to vault with gate record
        │   → remove worktree + branch
        │   → no code changes survive
        │
        ├─ INCONCLUSIVE (gate_verdict: inconclusive)
        │   → log to vault with gate record
        │   → keep worktree for manual inspection
        │   → flag for human review
        │
        └─ ACCEPTED (gate_verdict: accepted)
            → clean-commit-gate (split into focused commits)
            → push branch + open PR
            → thermonuclear-pr-review (separate agent)
            → human merge approval
            → log to vault with gate record + PR link
```

#### 6a: Run the hypothesis

- Immersive: Run step-by-step in a worktree. After each result, discuss interpretation.
  Use `/autoresearch:reason` for ambiguous results.
- Autonomous: Launch autoresearch loop in the worktree. Results logged to TSV + vault.

#### 6a.5: Specification Violation Check (CoE I2)

**Purpose:** Detect code that earns its metric by gaming the evaluation rather than
solving the problem. The paper (Meng et al. 2026) shows spec violation risk scales
with iteration count — at high budgets, 50–70% of nodes converge on exploits for
some tasks. This check prevents gaming-derived results from passing the gate and
entering the provenance graph as accepted evidence.

**When to run:** After execution completes (6a) and before gate evaluation (6b).
Skip only if execution crashed/interrupted (the crash handler at step 4 of
`run-hypothesis.sh` already exits early).

**The check has two layers — mechanical first, then LLM judgment:**

**Layer 1: Mechanical (always runs, zero LLM cost):**

```bash
DIFF=$(git diff "$MAIN_BRANCH"..."$BRANCH" -- . ':!*.md' ':!*.txt')

# Q1a: Did the agent modify the metric/evaluation script itself?
METRIC_SCRIPT=$(echo "$GATE_CMD" | grep -oP '[\w/.-]+\.py' | head -1)
if [ -n "$METRIC_SCRIPT" ] && echo "$DIFF" | grep -q "^+++ b/${METRIC_SCRIPT}"; then
    echo "I2_FLAGGED: agent modified the metric script ${METRIC_SCRIPT}"
    SPEC_VIOLATION="flagged"
    SPEC_DETAIL="Evaluator manipulation: diff touches the metric script"
fi

# Q1b: Did the agent import the evaluation script as a library?
if echo "$DIFF" | grep -qP '^\+.*import.*\b('"$(basename "$METRIC_SCRIPT" .py)"')\b'; then
    echo "I2_FLAGGED: agent imports the metric script"
    SPEC_VIOLATION="flagged"
    SPEC_DETAIL="Evaluator manipulation: code imports the metric module"
fi
```

If Layer 1 flags a violation, skip Layer 2 — the evidence is deterministic.

**Layer 2: LLM judgment (runs if Layer 1 is clean, autonomous mode only):**

A fresh agent reads the diff, the metric command, and the hypothesis spec, then
answers two questions:

- **Q2 (specification circumvention):** Does the diff achieve the metric by violating
  constraints in the hypothesis or experiment note? Look for: hardcoded expected
  outputs, trivial/degenerate solutions (identity functions, zero tensors, constants),
  test-set structure exploitation (memorized indices, data leakage), or results that
  are technically correct but scientifically vacuous.

- **Q3 (scope integrity):** Does the diff modify files outside the declared `Scope`
  from the autoresearch config? This is a warning, not a hard violation — the agent
  may have legitimately needed to touch adjacent code.

Run K=3 independent LLM calls. Majority vote per question.

```bash
# Layer 2 (autonomous mode only — immersive mode presents the diff to the user instead)
if [ "$MODE" = "autonomous" ] && [ "$SPEC_VIOLATION" != "flagged" ]; then
    VERDICTS=""
    for i in 1 2 3; do
        V=$(claude -p "You are an I2 specification violation auditor.

HYPOTHESIS: $(head -5 "$PROMPT_FILE")
METRIC COMMAND: $GATE_CMD
SCOPE: $SCOPE
DIFF:
$(echo "$DIFF" | head -500)

Q2: Does this diff achieve the metric by circumventing the hypothesis constraints?
    Look for: hardcoded outputs, degenerate solutions, data leakage, evaluation gaming.
Q3: Does the diff modify files outside the declared Scope?

Reply EXACTLY with one line: Q2=clean|flagged Q3=clean|warning
No explanation." 2>/dev/null | tail -1)
        VERDICTS="$VERDICTS $V"
    done
    # Majority vote: flagged if >=2/3 say flagged on Q2
    Q2_FLAGS=$(echo "$VERDICTS" | grep -o 'Q2=flagged' | wc -l)
    if [ "$Q2_FLAGS" -ge 2 ]; then
        SPEC_VIOLATION="flagged"
        SPEC_DETAIL="Specification circumvention (LLM majority vote: ${Q2_FLAGS}/3)"
    fi
    Q3_WARNS=$(echo "$VERDICTS" | grep -o 'Q3=warning' | wc -l)
    if [ "$Q3_WARNS" -ge 2 ]; then
        SPEC_WARNING="scope-creep"
    fi
fi
```

**On violation (`spec_violation: flagged`):**
- Do NOT evaluate the gate. A spec-violating result is not evidence.
- Set `gate_verdict: rejected`, `gate_metric: "I2 specification violation"`.
- Preserve the branch under `refs/experiments/` — the violation itself is evidence
  of what the optimizer converges to under pressure, useful for redesigning metrics.
- In autonomous mode: continue to next hypothesis. Do not retry with the same metric.
- In immersive mode: present the violation to the user — they may want to redesign
  the metric or tighten the scope.

**On warning (`spec_warning: scope-creep`):**
- Proceed to gate evaluation normally.
- Record `spec_violation: warning` and `spec_violation_detail` in the result note.
- The thermonuclear-pr-review (6d, Step 3) will independently catch scope issues.

**On clean:**
- Record `spec_violation: clean` in the result note. Proceed to 6b.

#### 6b: Evaluate gate verdict

Apply the pre-registered decision rule from Stage 5. Classify as accepted/rejected/inconclusive.

#### 6c: On REJECTION — preserve, vault log, then cleanup

**Never delete unreferenced commits.** The vault note records `code_commit` — if the branch
is deleted without pushing, that commit gets garbage-collected and the code-provenance
guarantee (`git checkout <commit> && <run_command>`) silently breaks. Rejected results are
only evidence if they stay reproducible.

```bash
# 1. Preserve the rejected branch under refs/experiments/ (out of the normal branch namespace)
git push origin "${EXPERIMENT_BASE}/h1:refs/experiments/${EXPERIMENT_BASE}/h1"
# 2. Write vault note with gate record (status: refuted, code_commit now permanently resolvable)
# 3. Clean up the local workspace:
cd ..
git worktree remove h1-worktree --force
git branch -D "${EXPERIMENT_BASE}/h1"   # -D: rejected branches are unmerged by definition
```

The vault note preserves what was tried and why it failed; `refs/experiments/` preserves
the exact code state. Local worktree and branch are removed — the workspace stays clean
without destroying evidence.

#### 6d: On ACCEPTANCE — commit gate + PR + review

This is the code quality pipeline. Three agents, three concerns:

**Step 1: Clean Commit Gate** (same agent that ran the experiment)

```bash
cd ../h1-worktree
# Invoke clean-commit-gate skill:
# - Scans diff for AI bloat, debug artifacts, dead code
# - Splits changes into focused, logical commits
# - Writes clear commit messages referencing the hypothesis
# Each commit message should reference the hypothesis note:
#   "feat: add mode-conditioned compliance term (ref: crystallization-partial-correlation)"
```

The agent that ran the experiment knows the intent behind each change, so it's best
positioned to write meaningful commit messages and split the diff logically.

**Repo policy — one setup handles solo and collaborative repos.** Set `collab: true` in the
project's MOC note (`Projects/<project>.md`) for repos with collaborators; absent/false = solo.
The pipeline is identical up to the review step, then branches:

| | solo repo | collab repo |
|---|---|---|
| Unit of record | vault note + pushed branch | same |
| Review | thermonuclear review → `code-review` vault note | same, **plus** PR (humans need the PR surface) |
| PR | optional (merge-queue drains it if you want the history) | required — driver drains the queue into real PRs |
| Merge | you merge locally after reading the review note | via PR, respecting the repo's branch protection/CI |
| Gate records | vault only | vault is still canonical; PR links back to the note |

The vault stays the single source of truth in both cases — the PR is a *view* for collaborators,
never the record. This means collaborators who don't use your vault still get a normal
GitHub workflow, and you never maintain two pipelines.

**Step 2: Push + queue for review (PR is optional, not the unit of record)**

The **vault note + pushed branch** are the durable record; the PR is just one review
surface. This matters for multi-machine work (HPC nodes without `gh`, air-gapped
compute nodes, laptop + servers in parallel):

```bash
cd ../h1-worktree
git push -u origin "${EXPERIMENT_BASE}/h1"    # push always — this is the non-negotiable step

if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
  gh pr create \
    --title "experiment: <hypothesis-slug>" \
    --body "## Hypothesis\n<H₁ statement>\n\n## Result\n<gate verdict + metric>\n\n## Vault Note\n[[<hypothesis-note>]]" \
    --base "$MAIN_BRANCH"
else
  # No gh on this machine (HPC login node etc.): add to the vault merge queue instead.
  # Append to Hypotheses/<project>/<direction>/merge-queue.md (status: needs-review):
  #   | branch | machine | gate verdict | vault note | PR |
  #   | ${EXPERIMENT_BASE}/h1 | my-hpc-cluster | accepted | [[<note>]] | pending |
  echo "queued for PR: ${EXPERIMENT_BASE}/h1 (create in batch from laptop later)"
fi
```

PR description (whenever it is created) must include: the hypothesis tested, the gate
verdict with metric values, and a wikilink to the vault note. Since the branch is already
pushed, `gh pr create --head <branch>` works later from **any** machine — batch-create PRs
from the laptop for everything in the merge queue. Step 3 (thermonuclear review) does not
need a PR either: it can review `git diff main...<branch>` directly and write its verdict
as a `code-review` vault note; attach it to the PR when one exists.

**Step 3: Thermonuclear PR Review** (SEPARATE agent — must not be the same agent that wrote the code)

```bash
# Launch a fresh agent to review the PR independently:
claude -p "Review the PR on branch ${EXPERIMENT_BASE}/h1.
Use the thermonuclear-pr-review skill.
Check diffs against the full codebase.
Write your review as a PR comment.
If the code has structural issues, request changes.
If it's clean, approve with notes."
```

**Critical:** The reviewing agent must be separate from the authoring agent. Same-agent
review is theatre — the agent will rationalise its own choices. Use `claude -p` to
spawn a fresh agent with no memory of the implementation decisions.

**Step 4: Human Merge Approval**

The PR sits open until a human reviews and merges. The agent does NOT merge.
In immersive mode, prompt the user: "PR #X is open and has been reviewed by an agent.
Please review and merge when ready."

In autonomous mode, the pipeline continues to the next hypothesis without waiting
for merge. The PRs accumulate for batch human review.

#### 6e: Worktree cleanup (after merge or rejection)

```bash
# After PR is merged (or rejected by human):
git worktree remove ../h1-worktree
# Branch is deleted by GitHub on merge, or manually:
git branch -d "${EXPERIMENT_BASE}/h1"
```

#### Autonomous execution template (full sequence per hypothesis)

Key design decisions (do not regress these):
- **handoff.json is the source of truth**, not TSV regexing. Every autoresearch run writes
  `handoff.json` with `status` (COMPLETE|USER_INTERRUPT|BOUNDED|ERROR) and `results_tsv` path.
- **Kept/discarded are read from the TSV status column** (column 8; values `keep`/`discard`/`crash`),
  skipping the `#` header, column-header row, and iteration-0 baseline.
- **gate_verdict comes from the pre-registered decision rule**, evaluated mechanically —
  never from "did the optimizer keep something".
- **The executing agent writes its own result note** (it has the context); this script only
  validates that the note exists and is complete. No context-free agent narrates a TSV it
  never saw generated.
- **Crashes get a status record** (`gate_verdict: inconclusive`), not silence.
- **Rejected work is preserved** under `refs/experiments/` before any cleanup.

```bash
#!/usr/bin/env bash
# run-hypothesis.sh <worktree-path> <branch-name> <prompt-file> <vault-note-slug> <project-slug> <direction-slug>
# Requires the hypothesis config to define:
#   GATE_CMD    — command printing the test statistic (a number)
#   GATE_OP     — comparison operator: gt | lt
#   GATE_THRESH — pre-registered threshold
set -euo pipefail

WORKTREE="$1"; BRANCH="$2"; PROMPT_FILE="$3"; VAULT_NOTE="$4"
PROJECT="${5:?project slug required}"; DIRECTION="${6:?direction slug required}"
MAIN_BRANCH=$(git branch --show-current)
RESULT_NOTE=".vault/Hypotheses/${PROJECT}/${DIRECTION}/${VAULT_NOTE}-result.md"

cd "$WORKTREE"
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")

# 1. Execute. The prompt file (from agent-hypothesis-gen) instructs the agent to:
#    run the autoresearch loop, evaluate the decision rule, and WRITE ITS OWN result
#    note to ${RESULT_NOTE} with full provenance + gate record before exiting.
claude -p "$(cat "$PROMPT_FILE")"

# 2. Read execution status from handoff.json (source of truth, never regex TSVs for status)
HANDOFF=$(ls -t autoresearch/*/handoff.json 2>/dev/null | head -1)
STATUS=$(jq -r '.status // "ERROR"' "$HANDOFF" 2>/dev/null || echo "ERROR")
TSV=$(jq -r '.results_tsv // empty' "$HANDOFF" 2>/dev/null || true)

# 3. Iteration counts from the TSV status column (col 8: keep|discard|crash),
#    skipping '#' header, column-header row, and iteration-0 baseline
if [ -n "$TSV" ] && [ -f "$TSV" ]; then
    read -r TOTAL KEPT DISCARDED CRASHED <<< "$(awk -F'\t' \
        '!/^#/ && $1!="iteration" && $1!="0" {t++; if($8=="keep")k++; else if($8=="discard")d++; else if($8=="crash")c++}
         END {printf "%d %d %d %d", t, k, d, c}' "$TSV")"
else
    TOTAL=0; KEPT=0; DISCARDED=0; CRASHED=0
fi

# 4. Crash/interrupt => status record with inconclusive verdict, keep worktree for inspection
if [ "$STATUS" != "COMPLETE" ] && [ "$STATUS" != "BOUNDED" ]; then
    echo "INCONCLUSIVE: handoff status=$STATUS — keeping worktree for manual inspection"
    git add -A && git commit -m "WIP: checkpoint after ${STATUS}" --no-verify || true
    git push origin "${BRANCH}:refs/experiments/${BRANCH}"
    [ -f "$RESULT_NOTE" ] || claude -p "The experiment for ${VAULT_NOTE} ended with status ${STATUS}
    before writing its result note. Write ${RESULT_NOTE} now: type: result, status: needs-review,
    gate_verdict: inconclusive, direction: '${DIRECTION}', code_repo: '${REPO_NAME}',
    code_branch: '${BRANCH}', code_commit: '$(git rev-parse --short HEAD)',
    parents: ['[[${VAULT_NOTE}]]'], produced_by: 'autoresearch-execution',
    parent_types: ['agent-hypothesis']. State that execution did not complete and why, from
    the logs in autoresearch/."
    exit 0
fi

# 4.5 I2 Specification Violation Check (CoE I2) — before gate evaluation
SPEC_VIOLATION="clean"; SPEC_DETAIL=""; SPEC_WARNING=""
METRIC_SCRIPT=$(echo "$GATE_CMD" | grep -oP '[\w/.-]+\.py' | head -1)
DIFF=$(git diff "$MAIN_BRANCH"..."$BRANCH" -- . ':!*.md' ':!*.txt')

# Layer 1: mechanical — did the agent touch or import the metric script?
if [ -n "$METRIC_SCRIPT" ] && echo "$DIFF" | grep -q "^+++ b/${METRIC_SCRIPT}"; then
    SPEC_VIOLATION="flagged"; SPEC_DETAIL="Evaluator manipulation: diff modifies ${METRIC_SCRIPT}"
elif [ -n "$METRIC_SCRIPT" ] && echo "$DIFF" | grep -qP '^\+.*import.*\b'"$(basename "$METRIC_SCRIPT" .py)"'\b'; then
    SPEC_VIOLATION="flagged"; SPEC_DETAIL="Evaluator manipulation: code imports ${METRIC_SCRIPT}"
fi

# Layer 2: LLM judgment (autonomous mode, Layer 1 clean, diff non-trivial)
if [ "$SPEC_VIOLATION" = "clean" ] && [ "$(echo "$DIFF" | wc -l)" -gt 5 ]; then
    Q2_FLAGS=0
    for _i in 1 2 3; do
        V=$(claude -p "You are an I2 specification violation auditor.
HYPOTHESIS: $(head -5 "$PROMPT_FILE")
METRIC COMMAND: $GATE_CMD
DIFF (first 500 lines):
$(echo "$DIFF" | head -500)

Q2: Does this diff achieve the metric by circumventing the hypothesis constraints?
    (hardcoded outputs, degenerate solutions, data leakage, evaluation gaming)
Q3: Does the diff modify files outside expected scope?

Reply EXACTLY: Q2=clean|flagged Q3=clean|warning" 2>/dev/null | tail -1)
        echo "$V" | grep -q 'Q2=flagged' && Q2_FLAGS=$((Q2_FLAGS + 1))
        echo "$V" | grep -q 'Q3=warning' && SPEC_WARNING="scope-creep"
    done
    [ "$Q2_FLAGS" -ge 2 ] && { SPEC_VIOLATION="flagged"; SPEC_DETAIL="Specification circumvention (LLM ${Q2_FLAGS}/3)"; }
fi

echo "I2: spec_violation=${SPEC_VIOLATION} detail=${SPEC_DETAIL} warning=${SPEC_WARNING}"

# I2 FLAGGED => reject without evaluating gate, preserve evidence
if [ "$SPEC_VIOLATION" = "flagged" ]; then
    echo "I2_REJECTED: ${SPEC_DETAIL}"
    git push origin "${BRANCH}:refs/experiments/${BRANCH}"
    [ -f "$RESULT_NOTE" ] || claude -p "The experiment for ${VAULT_NOTE} was rejected by the I2
    specification violation check: ${SPEC_DETAIL}. Write ${RESULT_NOTE} now: type: result,
    status: refuted, gate_verdict: rejected, gate_metric: 'I2 specification violation',
    gate_threshold: 'no evaluator manipulation or specification circumvention',
    gate_value: '${SPEC_DETAIL}', spec_violation: flagged,
    spec_violation_detail: '${SPEC_DETAIL}', direction: '${DIRECTION}',
    code_repo: '${REPO_NAME}', code_branch: '${BRANCH}',
    code_commit: '$(git rev-parse --short HEAD)',
    parents: ['[[${VAULT_NOTE}]]'], produced_by: 'autoresearch-execution',
    parent_types: ['agent-hypothesis']. Explain the violation and why retrying with
    the same metric is not advisable."
    cd .. && git worktree remove "$WORKTREE" --force
    git branch -D "$BRANCH"
    exit 0
fi

# 5. Evaluate the PRE-REGISTERED decision rule mechanically (this — not kept-count — is the gate)
GATE_VALUE=$(eval "$GATE_CMD")
case "$GATE_OP" in
    gt) PASS=$(awk -v v="$GATE_VALUE" -v t="$GATE_THRESH" 'BEGIN{print (v>t)?1:0}') ;;
    lt) PASS=$(awk -v v="$GATE_VALUE" -v t="$GATE_THRESH" 'BEGIN{print (v<t)?1:0}') ;;
    *)  echo "ERROR: bad GATE_OP"; exit 1 ;;
esac
echo "GATE: value=${GATE_VALUE} op=${GATE_OP} threshold=${GATE_THRESH} => $([ "$PASS" = 1 ] && echo accepted || echo rejected)"
echo "DIAGNOSTIC: iterations=${TOTAL} kept=${KEPT} discarded=${DISCARDED} crashed=${CRASHED}"

# 6. Validate the agent wrote its result note with the required fields
for field in gate_verdict code_commit run_command produced_by direction; do
    grep -q "^${field}:" "$RESULT_NOTE" || { echo "ERROR: ${RESULT_NOTE} missing ${field}"; exit 1; }
done
NOTE_VERDICT=$(grep '^gate_verdict:' "$RESULT_NOTE" | awk '{print $2}')
EXPECTED=$([ "$PASS" = 1 ] && echo accepted || echo rejected)
[ "$NOTE_VERDICT" = "$EXPECTED" ] || { echo "ERROR: note verdict '${NOTE_VERDICT}' != computed '${EXPECTED}'"; exit 1; }

# 7. REJECTED => preserve, then clean up
if [ "$PASS" != 1 ]; then
    git push origin "${BRANCH}:refs/experiments/${BRANCH}"   # code_commit stays resolvable forever
    cd .. && git worktree remove "$WORKTREE" --force
    git branch -D "$BRANCH"
    echo "REJECTED: evidence preserved at refs/experiments/${BRANCH}, vault note written"
    exit 0
fi

# 8. ACCEPTED => clean commits (same agent context), push, PR against the real base branch
claude -p "Run the clean-commit-gate skill on the current changes in $(pwd).
Split into focused commits referencing hypothesis ${VAULT_NOTE}.
Commit plotting scripts alongside generated figures.
Do NOT commit debug artifacts, notebooks with output cells, or __pycache__."

FINAL_COMMIT=$(git rev-parse --short HEAD)
git push -u origin "$BRANCH"

if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh pr create \
        --title "experiment: ${VAULT_NOTE}" \
        --body "## Hypothesis
See vault note: [[${VAULT_NOTE}]]

## Gate
value=${GATE_VALUE} ${GATE_OP} ${GATE_THRESH} => accepted
Iterations: ${TOTAL} (kept ${KEPT} / discarded ${DISCARDED} / crashed ${CRASHED})
Commit: ${FINAL_COMMIT}" \
        --base "$MAIN_BRANCH"
    PR_URL=$(gh pr view "$BRANCH" --json url -q '.url')
else
    # No gh on this machine: queue for batch PR creation from the laptop
    QUEUE=".vault/Hypotheses/${PROJECT}/${DIRECTION}/merge-queue.md"
    GH_REPO=$(git remote get-url origin | sed -E 's#(git@|https?://)([^:/]+)[:/]##; s#\.git$##')
    [ -f "$QUEUE" ] || printf -- '---\ntype: checkpoint\nproject: "%s"\ndirection: "%s"\nstatus: needs-review\ngh_repo: "%s"\nproduced_by: "research-loop-checkpoint"\nparents: []\nparent_types: []\ncreated: %s\n---\n\n# Merge Queue: %s\n\n| branch | machine | verdict | vault note | PR |\n|---|---|---|---|---|\n' "$PROJECT" "$DIRECTION" "$GH_REPO" "$(date +%Y-%m-%d)" "$DIRECTION" > "$QUEUE"
    printf '| %s | %s | accepted | [[%s-result]] | pending |\n' "$BRANCH" "$(hostname -s)" "$VAULT_NOTE" >> "$QUEUE"
    PR_URL="(queued: research-loop-driver.sh drains this automatically on any gh-authenticated machine)"
fi

# 9. Independent review (SEPARATE fresh agent — never the author). Works without a PR:
claude -p "Review the changes on branch ${BRANCH} (git diff ${MAIN_BRANCH}...${BRANCH})
using the thermonuclear-pr-review skill. Check that plotting code is reproducible and
figures match the claimed results. Write your verdict as a code-review vault note in
.vault/Experiments/${PROJECT}/${DIRECTION}/; if a PR exists for this branch, also post it as a PR comment."

# 10. Patch the result note with the final (post-clean-commit-gate) commit, I2 verdict, + PR link
sed -i.bak "s/^code_commit:.*/code_commit: \"${FINAL_COMMIT}\"/" "$RESULT_NOTE" && rm -f "${RESULT_NOTE}.bak"
grep -q '^spec_violation:' "$RESULT_NOTE" || sed -i.bak "/^gate_value:/a\\
spec_violation: ${SPEC_VIOLATION}\\
spec_violation_detail: \"${SPEC_DETAIL:-none}\"" "$RESULT_NOTE" && rm -f "${RESULT_NOTE}.bak"
grep -qF "$PR_URL" "$RESULT_NOTE" || printf '\n**PR:** %s\n' "$PR_URL" >> "$RESULT_NOTE"

echo "DONE: ${PR_URL}, awaiting human merge."
```

#### Discovery-Design Reinforcement (REQUIRED after each validated result)

After a result is validated (gate_verdict: accepted), ask two questions before proceeding:

1. **What predictions does this validated mechanism sharpen?** Identifying a mechanism
   improves predictions for related quantities. List what's now more precisely predicted
   than before this result. These sharpened predictions are inputs for the next VoI
   computation (Stage 4) — they change which experiments are most discriminative.

2. **What subtler residuals are now detectable?** Each validated result raises the
   resolution of the investigation. Patterns that were previously below the noise floor
   (swamped by the now-explained effect) may become visible. List these exposed residuals.
   They feed directly into the next iteration's direction generation (idea-bouncer's
   residual-first framing).

This makes the loop *telescopic* (Murphy 2608.09696's "discovery-design reinforcement"):
each validated result → sharpened predictions → better experiment design → subtler
residuals exposed → next discovery. The loop's resolution increases monotonically.

**Record in result note:**
```yaml
sharpened_predictions: ["<what this result makes more precise>"]
exposed_residuals: ["<what subtler patterns are now detectable>"]
```

**Immersive:** Present these to the user: "Now that we've established [X], these
predictions are sharper: [...]. And these patterns might now be visible: [...].
Should we chase any of these?"
**Autonomous:** Record in the result note; the next iteration's idea-bouncer will
pick them up via the residual scan in Step 1.5.

**Decision gate (immersive):** After each result: "Here's what we found. What does this mean
for the bigger question? The code changes are on branch X — here's the diff summary."

### Stage 6.5: M-Open Predictive Check, Plateau Detection & Regime Classification

**Purpose:** Distinguish search exhaustion from discovery opportunity, and detect when
the model class itself is structurally inadequate.

#### M-Open Predictive Check (run BEFORE plateau classification)

Inspired by Murphy 2608.09696's M-open mechanism: after each validated result, check
whether the best current model is structurally adequate — not just whether the metric
is still improving. A model can plateau because it's correct (noise floor reached) or
because it's *wrong in a way the metric can't see*.

**Procedure:**

1. At Stage 5, pre-register a residual threshold τ_r alongside the gate threshold.
   τ_r answers: "How wrong can the best model be on new data before we conclude the
   model *class* (not just the parameters) is inadequate?"

2. After each validated result, compute residuals of the best model on held-out or
   new data:
   ```bash
   # Run the best model on held-out data and compute residual
   RESIDUAL=$(python compute_residual.py --model best --data held_out)
   echo "M-OPEN CHECK: residual=${RESIDUAL}, threshold=${TAU_R}"
   ```

3. **Classify:**

   | Condition | Interpretation | Action |
   |-----------|---------------|--------|
   | residual ≤ τ_r | Model class is adequate | Continue refining parameters within it |
   | residual > τ_r | Model class is structurally wrong | Trigger hypothesis-space expansion |

4. **On expansion trigger:** Loop back to Stage 1 (idea-bouncer) with the residual
   pattern as input. Specifically, pass the residuals to the **residual-first framing**
   in Step 2: "The best current model fails to explain [these patterns]. What mechanism
   could produce these specific failures?" This is residual-conditioned hypothesis
   proposal — the most informative input for direction generation.

5. **Record in the result note:**
   ```yaml
   m_open_residual: "<observed residual on held-out data>"
   m_open_threshold: "<pre-registered τ_r>"
   m_open_verdict: adequate | expand
   ```

**When τ_r is hard to set a priori:** Use the noise floor as a lower bound. If your
measurement has noise level σ, then τ_r < σ is meaningless (you can't distinguish model
error from noise). A reasonable default: τ_r = 3σ (the model must explain the data to
within 3× the noise level).

**Relationship to plateau detection:** The M-open check is *complementary*, not a
replacement. Plateau detection asks "is the optimizer still finding improvements?" —
M-open asks "is the model class capable of capturing the truth?" A model can plateau
because it's found the best parameters (adequate, plateau = convergence) or because
no parameters in this class can fit the data (expand, plateau = structural inadequacy).

#### Plateau Detection (existing signals)

After execution, before synthesis, classify the state of the investigation:

**Signals to check (mechanical first, judgment second):**
1. **Prequential structure estimate** (see vault-conventions.md, Regime Tracking): compute
   `S_hat` and `dS_last_k` from the results TSV metric trace. `dS_last_k < ε` = the loop is
   fitting noise, not extracting structure. This is the primary plateau signal — pre-registered
   k and ε, no vibes.
2. Are new artifact types or operations emerging? Mechanical check: `grep -h '^type:' <vault>/*/<project>/*.md | sort -u` — compare against the set at the last checkpoint.
3. Has the autoresearch loop hit its plateau detector?
4. Are the remaining hypotheses all failing with similar failure modes?
5. **M-open verdict from above:** if `m_open_verdict: expand`, this overrides plateau
   classification — even if the metric is still improving, the model class is wrong.

**Classification:**

| Signal Pattern | Regime Status | Action |
|---------------|--------------|--------|
| Metric improving, artifacts growing | **Active search** | Continue to next iteration |
| Metric improving, same artifact types | **Routine search** | Continue, but note convergence |
| Metric plateaued, new types emerging | **Discovery in progress** | Document the regime transition explicitly |
| Metric plateaued, same types, some hypotheses pass | **Partial convergence** | Synthesize what worked, design follow-up |
| Metric plateaued, all hypotheses failing | **Regime exhaustion** | The current framework can't reach the answer |

**On regime exhaustion (immersive):**
Present to user: "We've exhausted what can be found within the current framework. The schema
(types: X, Y, Z; operations: A, B, C) doesn't seem to contain the answer. Options:
1. Add new artifact types (what new kinds of evidence would help?)
2. Add new operations (what new analysis methods could we try?)
3. Reframe the question entirely (is the hypothesis even asking the right thing?)
4. Accept current results as the best available answer."

**On regime exhaustion (autonomous):**
Write a regime-exhaustion note to vault with `status: needs-review` and `gate_verdict: inconclusive`,
and stop. Do NOT continue iterating — that's wasted compute.

### Stage 6.75: Kan-Transport Audit (on direction pivots) (NEW)

**Purpose:** When changing research direction, systematically audit what old evidence carries forward.

**Trigger:** User decides to pivot at any decision gate, OR regime exhaustion leads to reframing.

**Process:**

1. **List all artifacts** from the direction being pivoted away from (per-direction, not
   per-project — that's what the `direction:` field exists for):
   ```bash
   grep -rl 'direction: "<old-direction-slug>"' <vault>/
   ```

2. **For each artifact, classify transportability:**

   | Classification | Meaning | Action |
   |---------------|---------|--------|
   | **Transportable** | Valid under new framing as-is | Add `related` link to new direction notes |
   | **Reinterpretable** | Valid but needs re-framing | Create new note with `parents:` → old note |
   | **Inapplicable** | No mapping to new direction (Kan obstruction) | Note in audit; don't discard |
   | **Contradictory** | Actively conflicts with new direction | Critical — must be addressed explicitly |

3. **Identify forced residuals** — what the new direction needs that has no old-direction analogue.
   These represent genuinely new work required (the Kan obstruction: transport yields ∅).

3.5. **Re-run gates on transported evidence** (Definition 6, condition 3): for every
   transportable/reinterpretable artifact carrying a `gate_verdict`, re-run its gate command
   under the new framing (or justify in writing why the verdict still holds if not mechanically
   re-runnable). Gate fails after transport → reclassify as **contradictory**. A transition
   where old commitments stop being accepted is not a verified transition.

4. **Compute audit summary statistics:**
   - `total_artifacts`: number of artifacts audited
   - `transportable_count`: artifacts valid as-is in new framing
   - `reinterpretable_count`: valid but need re-framing
   - `inapplicable_count`: no mapping (Kan obstruction)
   - `contradictory_count`: actively conflicts with new direction
   - `transportable_fraction`: (transportable + reinterpretable) / total
   - `contradiction_fraction`: contradictory / total

5. **Write audit note:**
   ```yaml
   type: synthesis
   produced_by: "research-loop-audit"
   parents: ["[[old-direction-note]]", "[[new-direction-note]]"]
   parent_types: ["hypothesis", "hypothesis"]
   ```
   Content: what transported, what didn't, gate re-run outcomes, what's needed, estimated
   cost of the pivot, and the summary statistics above.

6. **Update the Regime Log** (`Projects/<project>-regimes.md`): append the transition,
   increment the regime counter. All subsequent notes stamp the new `regime:` value.

**Autonomous escalation thresholds (async human-in-the-loop):**

The agent runs the full audit mechanically — it never waits for a human to classify
each artifact. But after computing summary statistics, it checks two pre-registered
escalation thresholds before continuing:

| Condition | Meaning | Action |
|-----------|---------|--------|
| `contradiction_fraction > 0.3` | >30% of old work actively conflicts with new direction | **STOP.** Set audit note `status: needs-review`. Print summary. Wait for human. |
| `transportable_fraction < 0.5` | <50% of prior work carries forward | **STOP.** Set audit note `status: needs-review`. Print summary. Wait for human. |
| Neither triggered | Pivot is low-risk; most evidence transports | Continue to Stage 7 autonomously. Audit note gets `status: draft`. |

**Why these thresholds:** A high contradiction fraction means the new direction
doesn't just ignore old evidence — it *contradicts* it. The human needs to decide
whether the old evidence was wrong, whether the new framing is wrong, or whether
both can coexist under a broader theory. A low transportable fraction means most
prior work is wasted, which is expensive — the human should confirm the pivot is
worth the cost before the agent commits compute to the new direction.

**Immersive mode:** Always presents the full audit interactively regardless of thresholds.
The thresholds only matter in autonomous mode, where the agent would otherwise
silently pivot and continue.

**Overriding thresholds:** Project-level overrides can adjust these in a local copy of
this SKILL.md. E.g., for exploratory early-stage work where pivots are cheap, set
`contradiction_threshold: 0.5` and `transportable_threshold: 0.3`.

### Stage 7: Vault Write, Claim Verification & Synthesis

**Purpose:** Persist everything to the your vault, then verify that what's
written faithfully reflects what happened.

- Write/update hypothesis notes with final results and `status: validated | refuted | inconclusive`
- **Include gate records on ALL evaluated hypotheses** — including rejections
- Cross-link with related notes using `[[wikilinks]]`
- **Ensure all notes have typed provenance** (parents, produced_by, parent_types)
- **Prose style:** all vault notes can adopt the principles in `Methodology/writing-guide.md`
  (verdict-first headlines, honest-ledger sections, numbers carried in prose) — read it once
  per loop before writing the result note
- **Run claim verification** (see below)
- Write a project-level summary note if this was a multi-hypothesis investigation
- Run `vault-sync.sh` to commit and push
- **Remove your git worktree(s) after the final push:** `git worktree remove <path>` for every
  worktree this loop created (vault- and code-side). A worktree whose branch is pushed holds
  nothing; a worktree left behind becomes a stale registration that pins local branches and
  blocks `git checkout` for others. If `remove`
  refuses because the tree is dirty, rescue or commit the content first — never leave it
  silently, and never `--force` over unrescued data.

#### 7a: Claim Verification (CoE post-hoc audit)

**Purpose:** Catch drift between what happened and what the note says happened. Gate
records verify the *metric*; claim verification audits the *prose*. A note can pass its
gate while still misrepresenting the method, overstating effect sizes, or citing numbers
not present in the data.

**Run this on every `result` note before setting `status` to anything other than `draft`.**

**Numerical claim check (I1-equivalent):**

For each quantitative claim in the result note (metric values, improvements, iteration
counts, effect sizes):

1. Extract the claimed number and its context from the note prose.
2. Locate the source: the TSV results file, execution log, or gate record field.
3. Verify the number matches within rounding tolerance (0.1% relative or 0.01 absolute).
4. Flag mismatches as `> ⚠ Claim mismatch: note says X, source shows Y.`

```bash
# Quick mechanical check: does the gate_value in frontmatter match the TSV?
NOTE_VALUE=$(grep '^gate_value:' "$RESULT_NOTE" | sed 's/.*"\(.*\)"/\1/')
TSV_VALUE=$(tail -1 "$TSV" | awk -F'\t' '{print $4}')
# Compare — flag if they diverge
```

**Method-code alignment check (I4-equivalent):**

Read the "Method" or "Key Changes" section of the result note. For each methodological
claim (algorithm used, architecture change, hyperparameter choice):

1. Verify the claim against the actual code at `code_commit`.
2. Acceptable simplification (omitting implementation details) is fine.
3. Flag cases where the note describes something the code doesn't do:
   `> ⚠ Method-code misalignment: note describes X, but code at <commit> does Y.`

**For autonomous agents:** Include this in the agent prompt:

```
CLAIM VERIFICATION (mandatory before finalising result notes):
After writing each result note, re-read it and cross-check:
1. Every number against the results TSV or execution log
2. Every method description against the code at the recorded commit
Flag any mismatch with ⚠ inline. Do not silently correct — flag first,
then fix with the correction visible.
```

**Record in frontmatter:** Add `claims_verified: true | false` to result notes after
running the check. A note with `claims_verified: false` should have `status: needs-review`.

**Immersive:** Present mismatches to user — "the note says X but the data shows Y,
which is correct?"
**Autonomous:** Auto-flag, set `status: needs-review` if any mismatch found, auto-sync.

## How to Invoke

### In Claude Code (terminal):

```bash
# Immersive mode (default in interactive sessions)
claude
> Start a research loop on: <your question>

# Autonomous mode
claude -p "Run an autonomous research loop on: <your question>.
Mode: autonomous. Write results to .vault/"

# Explicit mode selection
> Research this in immersive mode: <question>
> Research this autonomously: <question>
```

### In Cowork:

Immersive mode is the default. Just describe what you want to investigate.

### Mode detection heuristic:

- Interactive Claude Code session or Cowork → default immersive
- `claude -p` (non-interactive) → default autonomous
- User says "run overnight" / "autonomous" / "batch" → autonomous
- User says "walk me through" / "immersive" / "let's think about" → immersive

## Vault Integration

All output goes to the your vault (`.vault/` symlink or absolute path).
Follow vault conventions for frontmatter, naming, AND typed provenance.

Before writing any note:
1. `grep` the vault for the project slug and key terms
2. Check for existing notes on this topic
3. Link new notes to existing ones via `related:` frontmatter and inline `[[wikilinks]]`
4. Set `parents:` to the specific notes that produced this one
5. Set `produced_by:` to the skill that generated this note
6. Validate that the `parent_types → type` via `produced_by` is a valid morphism in the schema registry

After completion:
1. Run `vault-sync.sh` (or remind user to run it)
2. Suggest Dataview queries the user can run in Obsidian to explore the results

## Autoresearch Integration

This skill chains with autoresearch at Stage 5-6:

- `agent-hypothesis-gen` can emit autoresearch configs instead of raw `claude -p` prompts
- The autoresearch loop handles execution with mechanical verification and rollback
- Results from autoresearch's TSV logs get parsed and written to vault notes
- `/autoresearch:reason` is used in immersive mode for ambiguous results
- `/autoresearch:predict` can be inserted before Stage 4 for multi-persona experiment review

### Post-autoresearch vault hook

After any autoresearch loop completes, parse the results TSV and write a structured vault note.
Follow `Methodology/writing-guide.md` for prose clarity in the Results Summary and interpretation sections.

```markdown
---
type: result
project: "<project>"
direction: "<direction-slug>"
regime: "<project>/<n>"
status: draft
domain: ["<tags>"]
created: <today>
sources: ["autoresearch loop <timestamp>"]
related: ["[[parent-hypothesis-note]]"]
parents: ["[[parent-hypothesis-note]]"]
produced_by: "autoresearch-execution"
parent_types: ["agent-hypothesis"]
gate_verdict: <accepted | rejected | inconclusive>
gate_metric: "<the autoresearch metric>"
gate_threshold: "<pre-registered decision rule from hypothesis>"
gate_value: "<final metric value>"
registration: pre | retro
gate_sensitivity: "<broken-arm test result or justification for omission>"
gate_power: "<oracle ceiling vs noise floor>"
model_complexity: "<DOF / parameter count / structural assumptions>"
bic_value: "<BIC score, if computed>"
m_open_residual: "<observed residual on held-out data>"
m_open_threshold: "<pre-registered τ_r>"
m_open_verdict: adequate | expand
voi_discriminant: "<which competing hypotheses this experiment discriminated, or 'N/A'>"
sharpened_predictions: ["<what this result makes more precise>"]
exposed_residuals: ["<what subtler patterns are now detectable>"]
---

# Autoresearch Result: <goal>

## Configuration
- Goal: <goal>
- Metric: <metric>
- Iterations: <N run> / <N planned>
- Duration: <time>

## Results Summary
- Baseline: <initial metric value>
- Final: <best metric value>
- Improvement: <delta> (<direction>)
- Kept: <N> / Discarded: <N> / Crashed: <N>

## Key Changes (kept iterations)
<parsed from TSV — what changes improved the metric>

## Decision
<reject/fail-to-reject H₀ based on pre-registered criteria>

## Next Steps
<suggested follow-up based on results>
```

## Chaining with Autoresearch Subcommands

These autoresearch subcommands slot into the pipeline:

| Stage | Autoresearch subcommand | When to use |
|-------|------------------------|-------------|
| 0 | `/autoresearch:probe` | Surface hidden assumptions before starting |
| 2 | `/autoresearch:reason` | Multi-round adversarial refinement of hypothesis |
| 4 | `/autoresearch:predict` | Multi-persona review of experiment design |
| 5-6 | `/autoresearch` (core loop) | Mechanical execution with verification |
| 6 | `/autoresearch:reason` | Resolve ambiguous results via blind judging |
| 6.5 | (built-in) | Plateau detection and regime classification |
| 6.75 | (built-in) | Kan-transport audit on direction pivots |
| 7 | `/autoresearch:learn` | Auto-generate documentation from results |
