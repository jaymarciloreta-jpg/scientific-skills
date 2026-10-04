---
name: agent-hypothesis-gen
description: >
  Generate testable hypotheses and design automated validation plans for goals that will be executed by
  Claude Code CLI agents. Use this skill when the user wants to set up an autonomous research or
  engineering task where an agent will explore, test, and validate ideas without constant human supervision.
  Triggers include: "generate hypotheses for", "set up an agent to test", "automate this investigation",
  "what should an agent try", "design a test plan for an agent", "autonomous experiment",
  "have an agent figure out", "agent-driven research", or any request to decompose a research or
  engineering goal into hypotheses that a Claude Code agent can independently test and report on.
  Also trigger when the user wants to create a systematic exploration loop: generate candidates →
  test → evaluate → refine.
---

# Agent Hypothesis Generation

Generate structured hypotheses and validation plans designed to be executed by Claude Code CLI agents (`claude -p`). Output goes to the Obsidian vault and produces ready-to-use agent prompts.

## Input

The user provides a **goal** — a research question, engineering problem, or exploration task they want to partially automate. Examples:
- "Find the best learning rate schedule for my model"
- "Figure out why validation loss plateaus after epoch 30"
- "Explore which graph construction methods work best for this dataset"
- "Survey what caching strategies exist for our API layer"

Also accept: a high-level direction where the user wants help decomposing into testable sub-questions.

## Execution

**Create tasks before starting.** Decompose into explicit tasks (e.g., "Decompose goal
into hypotheses", "Design agent workflow for each", "Write agent prompts", "Design
orchestration plan", "Search vault for context", "Write vault note"). Execute one at a
time, marking each complete. Include a verification task to confirm all agent prompts
contain the code provenance and clean-commit-gate instructions.

## Process

### Step 1: Decompose the goal into hypotheses

Break the goal into 3-7 specific, testable hypotheses. Each hypothesis must be formalized as a
proper statistical or empirical test — not a vague direction.

Requirements for each hypothesis:
- **Falsifiable**: there's a concrete observation that would refute it
- **Quantitative**: the pass/fail criterion is a number, not a judgment call
- **Independently testable**: an agent can evaluate it without results from other hypotheses
- **Scoped**: completable in a single agent session (minutes to hours, not days)
- **Ordered by information value**: test the hypothesis that most constrains the search space first

For each hypothesis, specify:
- **H₀** (null): the boring/default explanation, stated precisely
- **H₁** (alternative): the interesting claim, stated precisely
- **Test statistic / metric**: what exactly to measure (e.g., "accuracy gap between modular and
  monolithic on CIFAR-10-C averaged over 5 seeds", not "whether it works better")
- **Decision rule**: a pre-registered threshold. "Reject H₀ if mean accuracy gap > 2pp with p < 0.05
  on a paired t-test across seeds." The agent must compute this, not eyeball it.
- **Expected effect size**: what magnitude of effect would be scientifically meaningful vs. noise?
  If you can't estimate this, that's a sign you need a pilot study first — say so.
- **Dependencies**: does this depend on another hypothesis's result?
- **Estimated cost**: rough compute/time estimate

If a hypothesis genuinely cannot be quantified (rare for anything an agent can test), explain why
and propose the closest quantitative proxy. "Does the code feel cleaner" is never acceptable —
"Does cyclomatic complexity decrease by >10%?" is.

### Step 2: Design the agent workflow

For each hypothesis, determine the execution pattern:

**Pattern A: Run-and-report** — agent runs a script/experiment, collects results, writes a summary.
Best for: benchmarking, parameter sweeps, data analysis.

**Pattern B: Search-and-synthesize** — agent searches docs/code/web, extracts relevant information, produces a structured summary.
Best for: literature surveys, codebase analysis, API evaluation.

**Pattern C: Build-and-test** — agent implements a small prototype, runs tests, reports what works.
Best for: comparing approaches, validating feasibility, testing edge cases.

**Pattern D: Iterative refinement** — agent tries an approach, evaluates, adjusts, repeats for N iterations.
Best for: optimization, prompt engineering, configuration tuning.

### Step 3: Write agent prompts

For each hypothesis, produce a ready-to-use prompt for `claude -p`. The prompt should:

1. **State the goal clearly** — what to investigate and why
2. **Specify the methodology** — what steps to take
3. **Define success criteria** — how to evaluate results
4. **Set output format** — where and how to write results (markdown file with structured sections)
5. **Include guardrails** — time/compute limits, scope boundaries, when to stop

The prompt should be self-contained — the agent won't have conversational context.

Template:
```
You are investigating: <hypothesis>

H₀: <null hypothesis — stated precisely>
H₁: <alternative hypothesis — stated precisely>
Test statistic: <what to measure, exactly>
Decision rule: <pre-registered threshold, e.g., "reject H₀ if X > Y with p < 0.05">
Expected effect size: <what magnitude would be meaningful>

Context: <brief background on why this matters>

Methodology:
1. <step 1>
2. <step 2>
...

Write your results to: <output-path>

Use this structure for your report:
- H₀: <restate null>
- H₁: <restate alternative>
- Method: <what you actually did — deviations from plan must be flagged>
- Raw measurements: <all numbers, not just summaries>
- Test statistic value: <computed value>
- p-value or confidence interval: <if applicable>
- Effect size: <observed vs. expected>
- Decision: reject H₀ | fail to reject H₀ | inconclusive (with reason)
- Caveats: <what could invalidate this result — small N, violated assumptions, etc.>
- Suggested follow-up: <what to test next based on results>

Code provenance (REQUIRED — fill in before writing the vault note):
- code_commit: <git rev-parse --short HEAD>
- code_repo: <repo name>
- code_branch: <current branch>
- run_command: <exact command you used>
- plots: <list of figure paths relative to repo root>

After completing the experiment:
1. Commit all code changes AND plotting scripts AND generated figures
2. Run clean-commit-gate to ensure commits are focused and clean
3. Write the result vault note with ALL code provenance fields populated

Constraints:
- Time limit: <minutes>
- Do not modify production code on main — work on your experiment branch
- Commit plotting code alongside figures — never commit figures without their generating script
- If results are inconclusive after <N> attempts, stop and report what you found
```

### Step 4: Design the orchestration plan

Specify how the hypotheses connect:
- **Parallel group**: hypotheses that can run simultaneously
- **Sequential chains**: hypotheses where the next depends on the previous result
- **Decision points**: where a human should review before proceeding
- **Convergence criteria**: when to stop the exploration

Provide a shell script or execution plan the user can run:

```bash
# Phase 1: Independent hypotheses (parallel)
claude -p "$(cat hypothesis-1-prompt.md)" --output-dir results/h1 &
claude -p "$(cat hypothesis-2-prompt.md)" --output-dir results/h2 &
wait

# Phase 2: Review results, then conditional hypotheses
# ... (depends on Phase 1 outcomes)
```

### Step 5: Search vault for context

Check existing vault notes for:
- Prior hypotheses on this topic
- Experiment results that inform the search space
- Papers with relevant techniques

Feed relevant context into agent prompts where it would help.

## Output Format

Read `references/vault-conventions.md` from the paper-triage skill for conventions.

If the goal has a known `direction:` (from the parent hypothesis/experiment note or session
context), write to `<vault>/Agent-Hypotheses/<project>/<direction>/<goal-slug>.md`. Otherwise
write to `<vault>/Agent-Hypotheses/<project>/<goal-slug>.md`.

Create the `<project>` (and `<direction>`, if applicable) subdirectory if it does not exist.

```markdown
---
type: agent-hypothesis
project: "<project>"
status: draft
domain: ["<tag1>", "<tag2>"]
created: <today>
sources: []
related: ["[[linked-notes]]"]
parents: ["[[parent-note-slug]]"]
produced_by: "agent-hypothesis-gen"
parent_types: ["<type-of-parent>"]
---

# Agent Investigation: <goal>

## Goal

<what we're trying to learn or achieve>

## Hypotheses

### H1: <statement>
- **Test:** <what the agent does>
- **Pass:** <what supports this>
- **Fail:** <what refutes this>
- **Pattern:** run-and-report | search-and-synthesize | build-and-test | iterative-refinement
- **Est. time:** <minutes>

### H2: ...

## Execution Plan

```
<dependency graph or execution order>
```

## Decision Points

<where human review is needed before continuing>

## Agent Prompts

Saved to: `<vault>/Agent-Hypotheses/<goal-slug>/` as individual `.md` files per hypothesis.
```

Also write each agent prompt as a separate file: `<vault>/Agent-Hypotheses/<goal-slug>/h1-prompt.md`, etc.

## After Writing

Summarize: how many hypotheses, estimated total time, which can run in parallel, and where human checkpoints are. Ask if the user wants to adjust scope or priorities before launching agents.
