---
name: clean-commit-gate
description: >
  Pre-commit quality gate that catches AI-generated bloat, unfocused changes, dead code, debug artifacts,
  and poor commit messages before they enter the repository. Use this skill before committing, before staging,
  or when cleaning up a working tree. Triggers include: "clean up my changes", "review before commit",
  "prepare for commit", "stage my changes", "clean commit", "split this commit", "what should I commit",
  "commit gate", "pre-commit review", or any request to ensure changes are minimal, focused, and clean
  before being committed. Also trigger when the user says things like "this diff is too big", "I need to
  split this up", "there's too much noise in here", or expresses frustration about messy git history.
  This skill is about hygiene at the commit level — for PR-level architectural review, use the
  thermonuclear-pr-review skill instead.
---

# Clean Commit Gate

A pre-commit quality gate that enforces focused, minimal, clean commits. The philosophy: every commit
should be a single logical change that a future reader can understand from its message alone. AI-assisted
coding tends to produce bloated diffs — this skill exists to counteract that.

## When to Run

Run this skill:
- Before `git add` / `git commit`
- After a coding session where an LLM generated significant code
- When `git diff` looks larger than expected
- When the user asks to clean up or prepare changes for commit

## Process

### Step 1: Assess the current state

Run these commands to understand what we're working with:

```bash
git status
git diff --stat          # unstaged changes
git diff --cached --stat # staged changes
```

Get the full diff for analysis:
```bash
git diff                 # unstaged
git diff --cached        # staged
```

If both staged and unstaged changes exist, analyze them separately.

### Step 2: Scan for clutter

Search the diff for each category of noise. Be aggressive — the goal is zero clutter.

**AI-generated bloat:**
- Unnecessary comments explaining obvious code ("// increment the counter")
- Overly verbose variable names that read like sentences
- Wrapper functions that add indirection without value
- Unnecessary type annotations where inference works
- Boilerplate that could be replaced by a simpler pattern
- "Just in case" error handling for conditions that can't occur
- Unnecessary abstractions — interfaces with one implementation, factories that build one thing
- Docstrings that restate the function signature in prose

**Dead code / debug artifacts:**
- `console.log`, `print()`, `debugger`, `pdb.set_trace()`
- Commented-out code blocks
- Unused imports
- Unused variables or functions
- TODO/FIXME/HACK comments that aren't actionable
- Leftover test data or mock values in production code
- `.only` or `.skip` on tests

**Style noise:**
- Gratuitous reformatting of lines the commit doesn't logically touch
- Whitespace-only changes mixed with real changes
- Import reordering that's unrelated to the actual change

For each finding, report:
- File and line number
- Category (bloat / dead code / style noise)
- Severity (must-fix / should-fix / nit)
- Suggested fix (delete, simplify, or move to a separate commit)

### Step 3: Check commit focus

A focused commit changes one thing. Evaluate whether the diff contains a single logical change or multiple:

**Signs of an unfocused diff:**
- Changes span unrelated modules or features
- The diff contains both a refactor and a feature addition
- Test changes don't correspond to the code changes
- Configuration changes are mixed with logic changes
- Bug fixes are bundled with unrelated cleanup

If the diff is unfocused, propose a split plan:

```
Proposed commit sequence:
1. "refactor: extract auth middleware into separate module" — files: auth.py, middleware.py
2. "feat: add rate limiting to API endpoints" — files: api.py, rate_limit.py, tests/
3. "chore: update dependencies" — files: requirements.txt, lock file
```

For each proposed commit, list exactly which files/hunks belong to it. If interactive staging (`git add -p`) would help, say so and describe which hunks to stage.

### Step 4: Draft commit message

Write a commit message following conventional commits format:

```
<type>(<scope>): <subject>

<body — what and why, not how>

<footer — breaking changes, issue refs>
```

Rules:
- **Subject line:** imperative mood, lowercase, no period, under 72 chars. It should complete the sentence "If applied, this commit will ___."
- **Type:** feat, fix, refactor, chore, docs, test, perf, style, ci
- **Scope:** the module/component affected (optional but preferred)
- **Body:** explain *why* this change exists, not *what* it does (the diff shows what). If the change is trivial, the body can be omitted.
- **No filler phrases:** "This commit updates..." or "Changes made to..." are noise. Start with the reason.

**Good examples:**
```
feat(dag): add cross-attention between child and parent nodes

Parent node embeddings are now accessible to children via cross-attention
during forward pass. This enables information flow from earlier tasks
without requiring explicit skip connections.

Resolves #42
```

```
fix(training): prevent gradient explosion in crystallization loss

The eigenvalue decomposition was producing NaN gradients when the
covariance matrix had near-zero eigenvalues. Added epsilon clamping
before the decomposition step.
```

**Bad examples:**
```
update code                          # what code? why?
fix bug in training loop             # which bug?
refactor: refactored the module      # tautology
feat: added new feature for users    # which feature? what does it do?
```

### Step 5: Final checklist

Before approving the commit, verify:

- [ ] No debug statements (`console.log`, `print`, `debugger`, `pdb`)
- [ ] No commented-out code
- [ ] No unused imports or variables
- [ ] No AI-generated filler comments
- [ ] No unnecessary abstractions or wrappers
- [ ] No gratuitous formatting changes
- [ ] Commit is a single logical change
- [ ] Commit message follows conventional commits
- [ ] Subject line is under 72 chars and uses imperative mood
- [ ] Tests (if any) correspond to the code change

## Strictness Levels

The user can request different strictness:

- **Standard** (default): catch obvious clutter, enforce focused commits, write good messages
- **Strict**: additionally flag any abstraction that doesn't clearly earn its place, any comment that doesn't add information beyond the code, any test that tests implementation rather than behavior
- **Paranoid**: additionally enforce that every function is under 30 lines, every file is under 300 lines, every commit touches at most 3 files (excluding tests), and the commit message body explains the reasoning behind every non-trivial decision

## Multi-commit workflow

If a session produced a large batch of changes, help the user create a clean commit sequence:

1. Analyze the full diff
2. Identify logical groupings
3. Propose a commit order (dependencies first, features last)
4. For each commit: list files, draft message, flag any clutter
5. Guide the user through staging and committing each one

The result should be a git log that reads like a story: each commit builds on the last, and a reader can understand the progression without looking at the code.
