---
name: hypothesis-stress-test
description: >
  Systematically stress-test a research hypothesis by generating counterarguments, identifying confounds,
  finding contradictory evidence, and surfacing related work. Use this skill whenever the user wants to
  pressure-test an idea, check if a hypothesis holds up, find holes in an argument, play devil's advocate
  on a research claim, or validate a proposed mechanism before committing to experiments. Triggers include:
  "stress test this", "what could go wrong with", "find holes in", "devil's advocate", "what am I missing",
  "counterarguments to", "is this hypothesis sound", "poke holes in this idea", "what confounds might exist",
  or any request to critically evaluate a proposed research direction. Also trigger when the user describes
  an experimental result and asks whether it's convincing or if alternative explanations exist.
---

# Hypothesis Stress-Test

Rigorously critique a research hypothesis and write a structured assessment to the Obsidian vault.

## Critical Stance

Approach every hypothesis as a hostile reviewer would. The user's understanding of their problem only
deepens when they're forced to defend claims against serious attack. A hypothesis that survives this
process is worth pursuing; one that doesn't was going to waste months of their time.

Do not treat the user's hypothesis as probably correct. Treat it as probably wrong until the evidence
forces you to upgrade. Most hypotheses in research are wrong — that's base rate, not pessimism.

When generating counterarguments, aim to produce at least one that genuinely worries the user — one
they hadn't considered and can't immediately dismiss. If every counter is something they already knew
about, you weren't critical enough.

If the hypothesis is vague, don't charitably fill in the gaps — point out the vagueness as a problem.
A hypothesis that can't be stated precisely enough to be falsified isn't a hypothesis, it's a hunch.
Force the user to sharpen it before you proceed. "I think X might cause Y somehow" is not ready for
stress-testing; it's ready for formalization.

## Input

The user provides a hypothesis — this could be:
- A formal statement ("X causes Y because Z")
- An informal intuition ("I think the backbone effect is because task 0 owns the only trained CNN")
- An experimental result they want alternative explanations for
- A proposed mechanism they're considering building on

If the hypothesis is vague, push back immediately: "This isn't precise enough to test. Which specific
part of X do you think causes which specific measurable change in Y, and through what mechanism?"
Don't proceed until there's a falsifiable claim on the table.

## Execution

**Create tasks before starting.** Decompose into explicit tasks (e.g., "Formalize claim
and assumptions", "Generate counterarguments", "Search for contradictory evidence",
"Assess robustness", "Write vault note"). Execute one at a time, marking each complete.
Include a verification task to confirm the gate record is consistent with the robustness
rating.

## Stress-Test Process

### Step 1: Formalize the hypothesis

Restate the hypothesis in a precise, falsifiable form. Identify:
- **The claim**: what specifically is being asserted
- **The mechanism**: the proposed causal chain
- **Key assumptions**: what must be true for the hypothesis to hold
- **Scope**: what domain/conditions this applies to

Present this back to the user for confirmation before proceeding.

### Step 2: Generate counterarguments

Produce 3-5 substantive counterarguments, each with:
- **The counter-claim**: what alternative explanation or objection exists
- **Why it's plausible**: evidence or reasoning supporting the counter
- **How to distinguish**: what experiment or observation would differentiate between the hypothesis and this alternative
- **Severity**: how damaging this counter is if true (fatal / serious / minor)

Prioritize non-obvious counters. "You need more data" is rarely useful. Think about:
- Alternative causal mechanisms that produce the same observations
- Confounding variables the user may not have controlled for
- Edge cases where the hypothesis breaks down
- Known results from adjacent fields that contradict the mechanism
- Selection biases or measurement artifacts

### Step 3: Search for contradictory evidence

Use web search to find:
- Papers that report conflicting results
- Known failure modes of the proposed mechanism
- Established results that constrain the hypothesis

For each piece of evidence found, assess whether it's a genuine contradiction or merely a different experimental context.

### Step 4: Search the vault for context

Read existing vault notes (especially `Papers/`, `Hypotheses/`, `Experiments/`) for:
- Prior stress-tests on related hypotheses
- Papers that bear on this claim
- Experimental results that provide evidence for or against

Cross-link with `[[wikilinks]]`.

### Step 5: Assess overall robustness

**Do not self-grade when running inside the research-loop pipeline.** The agent that generated
the critiques must not also judge survival — route the verdict through `/autoresearch:reason`
(hypothesis + critiques as opposing positions, blind judges). Standalone interactive use may
rate directly, but flag that the rating is self-graded.

Rate the hypothesis:
- **Robust** — survives stress-testing with minor caveats; counterarguments exist but are addressable
- **Promising but fragile** — plausible but has serious unaddressed confounds; needs specific experiments to firm up
- **Weak** — multiple strong counterarguments with no clear way to distinguish; reconsider before investing effort
- **Underdetermined** — not enough information to assess; specify what additional data would resolve this

### Step 6: Suggest experiments

For each counterargument rated "serious" or higher, propose a concrete experiment or analysis that would resolve the ambiguity. Be specific about:
- What to measure
- What outcome would support vs. refute the hypothesis
- How expensive/difficult this would be

## Output Format

Read `references/vault-conventions.md` from the paper-triage skill for folder structure and frontmatter conventions.
Follow `references/writing-guide.md` for prose clarity — especially in counterarguments and the robustness assessment.

If the hypothesis being stress-tested has a known `direction:`, write to
`<vault>/Hypotheses/<project>/<direction>/<short-description>.md`. Otherwise write to
`<vault>/Hypotheses/<project>/<short-description>.md`.

Create the `<project>` (and `<direction>`, if applicable) subdirectory if it does not exist.

```markdown
---
type: hypothesis
project: "<project>"
status: draft
domain: ["<tag1>", "<tag2>"]
created: <today>
sources: ["<any URLs found>"]
related: ["[[linked-notes]]"]
parents: ["[[parent-note-slug]]"]
produced_by: "hypothesis-stress-test"
parent_types: ["<type-of-parent>"]
robustness: robust | promising-but-fragile | weak | underdetermined
gate_verdict: accepted | rejected | inconclusive   # robust/promising-but-fragile → accepted; weak → rejected; underdetermined → inconclusive
gate_metric: "categorical robustness rating (blind-judged when in pipeline)"
gate_threshold: "robust or promising-but-fragile to proceed"
gate_value: "<the rating>"
---

# Hypothesis: <one-line statement>

## Formalized Claim

<precise, falsifiable statement>

**Mechanism:** <proposed causal chain>
**Key assumptions:** <what must hold>
**Scope:** <conditions/domain>

## Counterarguments

### 1. <Counter title> [severity: fatal|serious|minor]

<counter-claim and why it's plausible>

**Distinguishing test:** <how to tell which is right>

### 2. ...

## Contradictory Evidence

<findings from literature search, with citations>

## Robustness Assessment

**Rating:** <robust | promising-but-fragile | weak | underdetermined>

<synthesis paragraph explaining the overall assessment>

## Suggested Experiments

<specific experiments to resolve key ambiguities>

## Related Notes

<cross-links to vault content>
```

## After Writing

Summarize the assessment concisely. Highlight the most dangerous counterargument and the cheapest experiment that would resolve the biggest uncertainty.
