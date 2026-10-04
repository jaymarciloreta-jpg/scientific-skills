---
name: paper-triage
description: >
  Structured extraction and triage of academic papers into an Obsidian vault. Use this skill whenever the user
  wants to process a research paper — whether from a PDF upload, an arXiv URL, a Semantic Scholar link, or pasted
  abstract text. Triggers include: "read this paper", "summarize this paper", "extract from this PDF",
  "add this to my vault", "triage this paper", "what does this paper claim", or any request to systematically
  pull out claims, methods, baselines, limitations, or contributions from academic literature. Also trigger when
  the user provides a batch of papers to process. This skill writes structured Obsidian notes — if the user just
  wants a quick chat summary without vault integration, you can handle that without the skill.
---

# Paper Triage & Extraction

Extract structured information from academic papers and write Obsidian-compatible notes to the user's vault.

## Inputs (accept any of these)

1. **PDF file** — uploaded or at a file path. Use the `pdf` skill to extract text.
2. **URL** — arXiv, Semantic Scholar, OpenReview, or direct PDF links. Fetch and extract.
3. **Pasted text** — abstract, full text, or partial content in the conversation.
4. **Batch** — multiple papers at once. Process each and create separate notes.

## Execution

**Create tasks before starting.** Decompose the work into explicit tasks (e.g., "Extract
text from PDF", "Pull structured fields", "Search vault for related notes", "Write vault
note"). Execute one at a time, marking each complete. For batch processing, create one
task per paper plus a final cross-linking task.

## Extraction Process

### Step 1: Get the full text

**Rule: always read the full paper.** Abstracts omit methodology details, negative results,
limitations, and caveats that are critical for accurate triage. Only fall back to abstract-only
when the full text is genuinely unavailable (paywalled, no PDF, fetch fails). If you proceed
from the abstract alone, you MUST add `coverage: abstract-only` to the frontmatter and flag
it in the note body: `> ⚠ This note was triaged from the abstract only. Full-text review pending.`

- For PDFs: use the pdf skill's extraction pipeline — read all pages
- For arXiv URLs (e.g., `arxiv.org/abs/XXXX.XXXXX`): download the PDF version and extract full text. Do not stop at the abstract page
- For other URLs: fetch the page content. If it is abstract-only, attempt to locate and download the full PDF (check for PDF links, DOI resolvers, or open-access mirrors)
- For pasted text: use directly; if it is clearly only an abstract, ask the user for the full paper before proceeding

### Step 2: Extract structured fields

Pull out the following (leave blank if not found, don't hallucinate):

| Field | What to extract |
|-------|----------------|
| **Title** | Full paper title |
| **Authors** | Author list |
| **Year** | Publication year |
| **Venue** | Conference/journal if identifiable |
| **Core claim** | The paper's central thesis in 1-2 sentences — what they claim to show |
| **Method** | How they achieve/demonstrate the claim (architecture, algorithm, approach) |
| **Key results** | Quantitative results: metrics, datasets, numbers. Be specific. |
| **Baselines** | What they compare against |
| **Limitations** | Stated or apparent limitations, failure modes, scope constraints |
| **Relevance** | How this connects to the user's current project (if a project context is available from the vault) |
| **Open questions** | What the paper leaves unresolved or what follow-up work it suggests |
| **Citation** | Full reference in BibTeX and APA format. Extract from the paper metadata, DOI lookup, or Semantic Scholar. If unavailable, construct from extracted fields (authors, title, year, venue). |

### Step 3: Assess relevance (if project context available)

Read the vault's `Projects/` folder and any notes matching the user's current project. Score relevance:
- **High** — directly addresses a component of the user's work
- **Medium** — related technique or adjacent problem
- **Low** — tangentially related, good for background
- **Not relevant** — file under general reading

### Step 4: Verify references (CoE I3)

**Rule: every citation must resolve to a real publication.** Agent-generated literature grounding
can hallucinate plausible-looking references — titles that sound right but don't exist. Verification
catches this before a fabricated citation propagates through the provenance graph.

For each citation extracted in Step 2:

1. **Query Semantic Scholar** (preferred) or arXiv API by title + first author:
   ```python
   import urllib.parse, json, urllib.request
   query = urllib.parse.quote(f"{first_author} {title_fragment}")
   url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=3&fields=title,authors,year,externalIds"
   resp = json.loads(urllib.request.urlopen(url).read())
   ```
2. **Match criteria:** title similarity > 80% (fuzzy match) AND at least one author surname matches
   AND year matches within ±1. Near-misses (real DOI attached to wrong description) count as
   unverified — flag them explicitly.
3. **For arXiv papers:** also verify the arXiv ID resolves: `https://arxiv.org/abs/<id>` returns 200.
4. **Record in frontmatter:**
   - `citations_verified: <N>` — number that resolved successfully
   - `citations_unverified: <N>` — number that could not be resolved
   - `citations_total: <N>` — total extracted
5. **Flag unverified citations** in the note body:
   `> ⚠ Unverified citation: <citation>. Could not resolve via Semantic Scholar or arXiv.`

If >20% of citations are unverified, add a warning at the top of the note:
`> ⚠ High unverified citation rate (<N>/<total>). Treat literature claims with caution.`

**When to skip:** If the paper was uploaded as a PDF by the user (not agent-retrieved), verification
is still recommended but failures are less concerning — the paper itself is real, only its bibliography
entries are being checked. For agent-retrieved papers (URL-based triage), verification is mandatory.

### Step 5: Search for related vault notes

Before writing, grep the vault for:
- Papers by the same authors
- Papers on the same method or dataset
- Hypotheses or experiments that cite similar concepts

Add these as `[[wikilinks]]` in the `related` frontmatter.

## Output Format

Read `references/vault-conventions.md` for folder structure and frontmatter conventions.
Follow `references/writing-guide.md` for prose clarity in narrative sections (Core Claim, Method, Limitations, Relevance).

Write to `<vault>/Papers/<project>/<first-author-year-short-title>.md`:

Create the `<project>` subdirectory if it does not exist. Use the `project:` frontmatter value as the directory name.

```markdown
---
type: paper
project: "<inferred-or-asked>"
status: draft
domain: ["<tag1>", "<tag2>"]
created: <today>
sources: ["<URL or DOI>"]
related: ["[[other-note]]"]
parents: []
produced_by: "paper-triage"
parent_types: []
relevance: high | medium | low
coverage: full | abstract-only
citations_verified: <N>
citations_unverified: <N>
citations_total: <N>
---

# <Paper Title>

**Authors:** <author list>
**Year:** <year> | **Venue:** <venue>

## Citation

**BibTeX:**
```bibtex
@article{<key>,
  title={<title>},
  author={<authors>},
  journal={<venue>},
  year={<year>},
  doi={<DOI if available>}
}
```

**APA:** <authors> (<year>). <title>. *<venue>*. <DOI URL if available>

## Core Claim

<1-2 sentences>

## Method

<concise description of approach>

## Key Results

<specific quantitative results, formatted as a table if multiple>

## Baselines

<what they compared against>

## Limitations

<stated + apparent limitations>

## Relevance to [[<Project>]]

<how this connects to current work — skip if no project context>

## Open Questions

<unresolved questions, follow-up directions>

## Raw Notes

<any additional observations, quotes, or context>
```

## Batch Processing

When given multiple papers, process each independently but cross-link them:
1. Extract all papers
2. After all are extracted, add cross-references between them where relevant
3. Present a summary table: title, relevance score, one-line takeaway

## After Writing

Tell the user:
- Where the note was saved
- The relevance assessment (if applicable)
- Any existing vault notes that connect to this paper
- Suggest follow-up: "Want me to stress-test any of the claims?" or "Should I check for related work?"
