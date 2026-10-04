---
name: cross-field-synthesis
description: >
  Translate research concepts across disciplinary boundaries and find analogous formalisms, methods, or
  results in other fields. Use this skill when the user is working at the intersection of fields and
  wants to find connections, when they ask "how would a [field X] researcher think about this",
  "is there an analogue of X in Y", "what's the [field] equivalent of", "bridge these two areas",
  "find related work outside my field", or when they want to translate their method's language into
  another community's vocabulary. Also trigger when the user is exploring a new application domain
  for their existing method and wants to understand how that domain frames similar problems.
  This is especially valuable for interdisciplinary work where the same concept has different names
  and formalizations across communities.
---

# Cross-Field Synthesis

Find conceptual bridges between fields by translating ideas, identifying analogous formalisms, and surfacing relevant work from adjacent communities. Output goes to the Obsidian vault.

## Input

The user provides:
1. **A concept or method** from their primary field
2. **A target field** (or fields) to search for analogues
3. Optionally: **why** they're looking (application, theoretical grounding, or just curiosity)

If the target field isn't specified, infer promising directions from the concept itself and suggest 2-3 candidate fields before proceeding.

## Execution

**Create tasks before starting.** Decompose into explicit tasks (e.g., "Formalize source
concept", "Search target field for analogues", "Map formalisms between fields", "Search
vault for related notes", "Write synthesis note"). Execute one at a time, marking each
complete. Synthesis is the most open-ended skill — tasks prevent losing focus when an
interesting but tangential connection appears.

## Synthesis Process

### Step 1: Formalize the source concept

Describe the concept in field-neutral language. Strip jargon and identify the core mathematical/structural/functional properties:
- What problem does it solve?
- What are its key structural properties (symmetry, compositionality, locality, hierarchy, etc.)?
- What constraints does it operate under?
- What are its failure modes?

This abstraction is what enables cross-field matching — two concepts that look different in domain-specific notation may be structurally identical.

### Step 2: Search for analogues

For each target field, search for:
- **Same structure, different name**: concepts that solve the same abstract problem (e.g., attention in ML ↔ gating in neuroscience ↔ routing in telecommunications)
- **Same name, different meaning**: terms shared across fields that mean subtly different things (dangerous false friends)
- **Solved problems**: has the target field already solved a version of your problem? Under what assumptions?
- **Established formalisms**: does the target field have a mature mathematical framework for this kind of thing?

Use web search extensively. Search with target-field-specific vocabulary, not your source field's terms. For example, if translating "modular neural networks" into neuroscience, search for "cortical columns", "functional specialization", "brain modularity" — not "modular networks neuroscience".

### Step 3: Build the translation table

Create a mapping between the source and target field's vocabulary:

| Source Field | Target Field | Notes |
|-------------|-------------|-------|
| attention mechanism | selective gating | similar function, different implementation |
| loss landscape | energy landscape | same math, statistical mechanics literature is deeper |
| ... | ... | ... |

Flag where the analogy breaks down — partial analogues are more useful when you know their limits.

### Step 4: Formalize the quantitative link

This is the critical step that separates useful synthesis from hand-wavy analogy. For each analogue,
push as far as possible toward a formal, quantitative connection:

**Level 1 — Shared mathematical structure:**
Can you write down the equations from both fields and show they're the same (or related by a known
transformation)? For example: "The softmax attention weight α_i = exp(q·k_i) / Σ_j exp(q·k_j) is
formally identical to the Boltzmann distribution P(s_i) = exp(-E_i/kT) / Z with temperature T=1
and energy E_i = -q·k_i." If this is possible, do it explicitly with equations.

**Level 2 — Quantitative correspondence:**
If the equations aren't identical, can you establish a quantitative mapping? For example: "The
eigenvalue spectrum of the network's Hessian at convergence follows a Marchenko-Pastur distribution
with aspect ratio γ = N/p, matching the prediction from random matrix theory for matrices with i.i.d.
entries." State the mapping, its assumptions, and where the correspondence is expected to break.

**Level 3 — Testable prediction from the analogy:**
Even if the formal link is partial, the analogy should generate a quantitative prediction that can
be tested in the source field. State this as a hypothesis test:
- H₀: the analogy is superficial and does not predict behavior in the source domain
- H₁: the target field's theory predicts [specific quantitative outcome] in the source domain
- Test: [specific experiment or analysis]
- Expected effect: [what the target field's theory would predict, with numbers if possible]

**Level 4 — Qualitative only (last resort):**
If no quantitative link can be established, explain precisely why. "The analogy is suggestive but
the source domain violates [specific assumption X] required by the target field's formalism, so the
quantitative predictions don't carry over." This is an honest answer, but it limits the analogy's
usefulness — say so explicitly.

Never present a qualitative analogy as if it were a formal connection. The whole point of
cross-field synthesis is to import *rigorous* results, not vibes.

### Step 5: Assess transfer potential

For each analogue found, evaluate:
- **Strength of analogy**: Which formalization level (1-4) did you achieve? Be honest.
- **What transfers**: Which techniques, theorems, or insights from the target field could apply? For quantitative links (levels 1-2), state the specific theorem and its conditions.
- **What doesn't transfer**: Where the analogy breaks. Which assumptions of the target field's theory are violated in the source domain?
- **Maturity gap**: Is the target field more or less mature on this topic? (e.g., statistical mechanics has much deeper theory of phase transitions than ML does)

### Step 5: Search vault for connections

Check existing vault notes for:
- Papers from the target field already in the vault
- Hypotheses that touch on cross-field connections
- Prior synthesis notes

### Step 6: Extract actionable insights

Don't just map concepts — identify:
- **Theorems or results to import**: specific mathematical results from the target field that apply
- **Methods to try**: techniques from the target field that could be adapted
- **Language to use**: vocabulary that would make the work legible to the target community (important for interdisciplinary papers/talks)
- **People to read**: key researchers at the intersection

## Output Format

Read `references/vault-conventions.md` from the paper-triage skill for conventions.
Follow `references/writing-guide.md` for prose clarity — synthesis notes are the most prose-heavy artifact type.

Write to `<vault>/Synthesis/<project>/<concept>-in-<field>.md`:

Create the `<project>` subdirectory if it does not exist.

```markdown
---
type: synthesis
project: "<project>"
status: draft
domain: ["<source-field>", "<target-field>"]
created: <today>
sources: ["<URLs found>"]
related: ["[[linked-notes]]"]
parents: ["[[parent-note-slug]]"]
produced_by: "cross-field-synthesis"
parent_types: ["<type-of-parent>"]
---

# <Source Concept> through the lens of <Target Field>

## Source Concept (field-neutral)

<abstract description stripped of jargon>

## Translation Table

| <Source Field> | <Target Field> | Formalization Level | Notes |
|---------------|---------------|---------------------|-------|
| ... | ... | 1 (shared math) / 2 (quantitative) / 3 (testable prediction) / 4 (qualitative only) | ... |

## Formal Connections

### <Analogue 1>

**Formalization level:** <1-4>

**Quantitative link:**
<equations, mappings, or explicit statement of why no quantitative link exists>

**Testable prediction:**
- H₀: <null>
- H₁: <what the target field's theory predicts>
- Test: <specific experiment>
- Expected effect: <quantitative prediction>

**Relevant work:** <citations>

### <Analogue 2> ...

## What Transfers

<specific techniques, theorems, or frameworks that could apply>

## Where the Analogy Breaks

<limits of the mapping — important for avoiding false imports>

## Actionable Next Steps

<concrete things to read, try, or investigate>

## Key Researchers

<people working at this intersection>
```

## After Writing

Highlight the single most promising analogue and why. If a target-field formalism is more mature than the source field's approach, flag that explicitly — it often means there's a shortcut available.
