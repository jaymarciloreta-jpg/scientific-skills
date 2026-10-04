---
name: thermonuclear-pr-review
description: >
  Extremely thorough PR review that checks diffs against the full codebase for structural regressions,
  missed simplifications, architectural drift, and maintainability problems. Inspired by Cursor's
  thermonuclear code quality review but adapted for Claude Code with deeper codebase context awareness.
  Use this skill for: "review this PR", "review my branch", "code review", "check my changes",
  "is this ready to merge", "thermonuclear review", "deep review", "harsh review", "strict code review",
  or any request to thoroughly evaluate code changes before merging. Also trigger when the user asks
  "what's wrong with this code" or "how can I improve this" about a branch or set of changes.
  This skill is for PR-level architectural review. For pre-commit hygiene, use clean-commit-gate instead.
---

# Thermonuclear PR Review

An aggressively thorough code review that treats every PR as a chance to make the codebase better, not
just "not worse." The bar for approval is high: the code should feel inevitable in hindsight.

This review operates on two levels simultaneously: the diff (what changed) and the codebase (how those
changes interact with everything else). Most reviews only do the first. This one does both.

## Process

### Step 1: Gather context

```bash
# What branch are we reviewing?
git branch --show-current
git log --oneline main..HEAD    # commits on this branch

# Full diff against main
git diff main...HEAD

# Stats
git diff main...HEAD --stat
git diff main...HEAD --numstat
```

Read the diff carefully. Before forming opinions, understand *what* changed and *why* (from commit
messages, PR description, or ask the user).

### Step 2: Structural review (the thermonuclear part)

This is the core of the review. For every meaningful change in the diff, evaluate against these standards.
Do not merely identify local cleanup opportunities — actively search for "code judo" moves: restructurings
that preserve behavior while making the implementation dramatically simpler.

**2a. Complexity assessment**

For each file touched by the PR:
- Read the full file (not just the diff hunks) to understand the context
- Check if the PR increased or decreased the file's complexity
- If a file crosses 500 lines due to this PR, flag it as a decomposition candidate
- Count the number of conditionals added vs. removed. Net positive = suspicious.

Questions to ask:
- Is there a way to reframe this change so whole branches, helpers, or layers disappear?
- Did this PR add branching complexity where a better abstraction would eliminate it?
- Are there repeated conditionals that signal a missing model?
- Can any of the new code be deleted by using an existing pattern in the codebase differently?

**2b. Abstraction quality**

- Does every new abstraction (class, function, module, interface) earn its existence?
- Flag thin wrappers, identity abstractions, or pass-through helpers that add indirection without buying clarity
- Flag generic mechanisms that hide simple data-shape assumptions
- Check if new helpers duplicate existing utilities elsewhere in the codebase (grep for similar function names and patterns)

**2c. Boundary cleanliness**

- Did feature-specific logic leak into shared paths?
- Did implementation details leak through API boundaries?
- Are type boundaries clear, or does the PR introduce casts, `any`, `Optional` proliferation, or loosely-shaped dicts/objects?
- Is the logic in the canonical layer, or is it drifting into the wrong module?

**2d. Spaghetti detection**

Flag aggressively:
- New ad-hoc conditionals inserted into unrelated flows
- One-off booleans or flags that complicate existing control flow
- Special-case handling in the middle of an already busy function
- "Temporary" branching that will become permanent debt
- Scattered feature checks across shared code (should be behind a dedicated abstraction)

### Step 3: Codebase context check

This is what elevates the review beyond diff-only analysis. For each significant change:

```bash
# Check how this module is used elsewhere
grep -r "import.*<module>" --include="*.py" --include="*.ts" .
grep -r "<function_name>" --include="*.py" --include="*.ts" .

# Check for similar patterns already in the codebase
# (prevents reinventing existing utilities)
grep -r "<pattern>" .

# Check test coverage
find . -name "*test*" -path "*<module>*"
```

Questions:
- Does this change break any implicit contracts with other modules?
- Are callers of the changed code updated? Are there callers the PR author missed?
- Does the codebase already have a canonical way to do what this PR is doing?
- Will this change force awkward adaptations in downstream code?

### Step 4: Maintainability deep dive

Think 6 months ahead. A future developer (possibly the same person) will encounter this code.

- Can someone understand this code without reading the PR description?
- If the original author left the project, could someone else modify this safely?
- Are the names accurate and specific? (Not `data`, `result`, `handler`, `manager`, `utils`)
- Is the control flow traceable without a debugger?
- Are error cases handled explicitly, or do they fall through silently?

### Step 5: Test assessment

- Do the tests test behavior or implementation? (Implementation tests are brittle and should be flagged)
- Are edge cases covered? What inputs could break this?
- Are there tests for the failure/error paths, not just the happy path?
- If there are no tests for new functionality, that's a blocker.

### Step 6: Performance and correctness (where applicable)

Not every PR needs this, but flag when you see:
- O(n²) or worse algorithms on potentially large inputs
- Unnecessary sequential work that could be parallel
- Race conditions in concurrent code
- Missing transaction boundaries or non-atomic state updates
- Resource leaks (unclosed files, connections, subscriptions)

## Output Format

Structure the review as:

```markdown
## PR Review: <branch-name>

**Verdict:** Approve / Request Changes / Needs Discussion
**Severity:** <number> critical | <number> major | <number> minor findings

### Critical (must fix before merge)

#### 1. <Finding title>
**File:** `path/to/file.py:42-58`
**Category:** spaghetti growth | abstraction debt | boundary leak | ...
**Issue:** <what's wrong and why it matters>
**Suggestion:** <specific fix, not just "improve this">

### Major (strongly recommended)

#### 2. ...

### Minor (would improve the PR)

#### 3. ...

### Positive observations

<things the PR does well — acknowledge good work>

### Summary

<2-3 sentence overall assessment. What's the main thing to address?>
```

## Approval Bar

Do NOT approve merely because behavior seems correct. The bar is:

- No structural regression — the codebase should not be harder to work with after this PR
- No missed code-judo moves — if there's a visible path to making this dramatically simpler, it should be taken
- No unjustified file-size explosion
- No spaghetti growth from special-case branching
- No unnecessary abstractions or indirection
- No architectural boundary leaks
- No duplicated utilities when canonical helpers exist
- No missing tests for new behavior
- Commit history is clean (single logical change per commit, good messages)

These are presumptive blockers. The author can justify exceptions, but the default is to push back.

## Review Tone

Be direct and demanding about quality, but not hostile. The goal is to make the code better, not to
make the author feel bad. Frame feedback as opportunities:

Good:
- "There's a code-judo move here — if we reframe X as Y, these three conditionals disappear entirely."
- "This works, but it makes the surrounding code harder to follow. Can we restructure to keep the behavior and simplify the flow?"
- "This abstraction isn't earning its keep yet. Can we inline it and see if that's clearer?"

Bad:
- "This is bad code."
- "Why would you do it this way?"
- "This is wrong." (without explaining what to do instead)

## Integration with clean-commit-gate

If the commit history itself is messy (unfocused commits, poor messages, debug artifacts), note it in the
review but focus the review on the cumulative diff. Suggest the author run the clean-commit-gate skill
to clean up the history before re-requesting review.
