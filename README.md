# Physician–Scientist Skills

A collected agent-skill library for **computer vision, medical imaging and autosegmentation, scientific ideation, device development, and video/content creation**. Medical and general hardware workflows receive equal priority.

Collected **2026-10-04**: **473 indexed skills** from **37 source repositories**, with **397 cataloged skills copied locally** where a permissive repository license and license file were identified. The separately selected scientific-brainstorming version is also preserved.

## Browse

- [Full catalog](catalog/CATALOG.md) — browse directly on GitHub.
- [Searchable catalog](catalog/index.html) — download/open locally for search and category filters; GitHub displays HTML source rather than running it.
- [CSV inventory](catalog/skills.csv) and [JSON inventory](catalog/skills.json).
- [Recommended starting sets](START_HERE.md).
- [Physician/scientist content workflows](PHYSICIAN_CONTENT.md).
- [Repository metadata and pinned revisions](catalog/repositories.json).

## Your authored skills

[Skills by Jaymarc Iloreta](authored-by-jaymarc/README.md) contains four original workflows for surgical video editing, Slicer sinus ROI, and nasal-airway geometry, plus a separately attributed Slicer adaptation.

## First skill added

[Scientific brainstorming](skills/scientific-brainstorming/SKILL.md) is the exact version you selected, with [SCAMPER, Six Thinking Hats, morphological analysis, TRIZ, and biomimicry reference methods](skills/scientific-brainstorming/references/brainstorming_methods.md). Its original files are unchanged; provenance and a license were added separately.

## Coverage

| Topic | Indexed entries |
|---|---:|
| CAD, simulation & hardware | 144 |
| Video, audio & physician content | 88 |
| Computer vision & ML | 57 |
| Medical imaging & segmentation | 34 |
| Scientific ideation & research | 60 |
| Iteration & reproducibility | 52 |
| Medical device quality & validation | 73 |

Skills may appear in multiple categories. Repeated placements of the same named skill within a repository are collapsed, with alternative paths recorded. Different implementations from different repositories remain separate.

## Layout and use

`skills/` holds explicitly selected versions. `library/<owner>--<repo>/` holds namespaced upstream skill folders with their accompanying files and licenses. `catalog/` links each skill to its exact Git commit and records a content hash, licensing, popularity, and local availability. `sources/` contains local upstream checkouts and is excluded from Git.

To use a collected skill, open its `SKILL.md` and accompanying references in your agent, or copy the complete skill directory into the agent's skill location. Review its dependencies first: some require a specific application, MCP server, GPU, API account, or files elsewhere in the upstream repository. A collected folder is not a tested installation. Skills are not globally activated by this repository.

The inventory compares names and content against the two local skill roots available during collection. “Same-name installed” does not establish equivalence or mean an update has been applied. Directory install counts are included only when observed in saved CLI search output; missing counts are not zero.

## Provenance and licensing

Third-party material retains its original license and attribution; this repository does not relicense it. Skills with unknown, custom, noncommercial, or copyleft repository licensing are cataloged as source links only in this initial collection. This is a collection policy, not a claim that those licenses prohibit use. Runtime software, models, services, and weights can have licenses separate from a skill's text.

Source existence and metadata were checked, but **the skills have not been execution-tested or clinically validated**. Repository popularity is only an adoption signal. Regulatory skills are supporting references whose statements must be checked against current authoritative requirements.

## Rebuilding

`python3 scripts/collect.py` retrieves the listed source repositories into `sources/` and records the existing checkout revision. It reuses existing checkouts; it does not silently update them. Then run `python3 scripts/build_catalog.py` and `python3 scripts/render_catalog.py`. The builder uses explicit topic filters; it is a broad discovery catalog, not an exhaustive list of every GitHub skill.

Collection scripts read upstream content as data and do not run upstream setup scripts or models. The checked-in snapshot and commit metadata make the current collection reproducible. Review local changes before refreshing or publishing a new snapshot.
