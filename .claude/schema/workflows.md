# Workflow Reference

<!-- CONFIGURABLE: The section headers below use Chinese（中文）by default (摘要, 核心观点, etc.).
     If your wiki uses a different language, translate these headers consistently across all files. -->

## Ingest Workflow

Triggered by: *"ingest <file>"* or `/wiki-ingest`

**Before starting: Read `.claude/schema/card-types.md` and `.claude/schema/page-format.md`**

**Supported formats:** Markdown (`.md`) ingested directly. Non-markdown files (`.pdf`, `.docx`, `.pptx`, `.xlsx`, `.html`, `.txt`, `.csv`, `.json`, `.xml`, `.rst`, `.rtf`, `.epub`, `.ipynb`, `.yaml`, `.yml`, `.tsv`, `.wav`, `.mp3`) auto-converted to markdown via [markitdown](https://github.com/microsoft/markitdown) before ingestion. Use `--no-convert` to skip auto-conversion.

### Steps (in order)

1. Read the source document fully using the Read tool (auto-convert if non-markdown)
2. Read `wiki/index.md` and `wiki/overview.md` for current wiki context
3. Write `wiki/sources/<slug>.md` — use the Source Page Format below
4. Update `wiki/index.md` — add entry under Sources section
5. Update `wiki/overview.md` — revise synthesis if warranted
6. **Check for existing pages that will be updated** — for each entity/concept/atom that this new source will add information to, check if a wiki page already exists. If yes, **archive it first** before modifying:
   1. Copy the current page to `wiki/archive/{Name}-V{N}.md` (N = next version number; start at V1, increment for each update)
   2. Add `archived: true` to the archived file's YAML frontmatter
   3. Add the archived version to the current page's `revisions` list (e.g., `revisions: ["[[CognitiveDebt-V1]]"]`)
   4. Then proceed to update the current page per steps 7-8 below
7. **Cross-reference scan** — before writing any new cards, search the existing wiki for terms/concepts/entities that overlap with key terms from the source. Use `grep -rl "term\|alias" wiki/concepts/ wiki/entities/` for each major concept. For each match found:
   - Read the existing card to understand its claims and boundaries
   - Decide the relationship type: #backs / #challenges / #extends / #applies
   - Note these candidates for use in new cards' `## 关联` sections
   - Pay special attention to **potential contradictions** (#challenges candidates): does the new source disagree with an existing card on any claim?
8. **Top-down extraction framework** — before writing any cards, run this extraction template in priority order:
   1. **Core insight定位**: Identify the source's core insight (5 detection patterns in card-types.md). A book/chapter's central claim is the biggest insight card.
   2. **Evidence tracing**: What key evidence supports the core insight? Each piece maps to a term/concept → terminology card
   3. **Person tracking**: Who proposed each piece of evidence/concept? → person card (if existing, update academic lineage)
   4. **Quote capture**: Find the most striking original quotes → quote cards
   5. **Action extraction**: What methods can guide your own actions? → action cards
   6. **Free notes**: Any personal reflections or uncategorized content? → basic cards
   - **Timeline**: Record where this view sits in academic history — who proposed first, who revised, who opposed, who inherited
   - This top-down template complements the subsequent bottom-up scan: establish the core skeleton first, then fill gaps
9. Update/create entity pages — choose `card_type: person` or `event` based on content, use the corresponding Card Type template. **For updates: merge new facts into existing sections, preserve all existing details, append the new source as a new `- "[[...]]"` item to the `sources` YAML list, update `updated` date.**
10. **Person lineage tracing** — for each person mentioned in the source, trace their academic genealogy:
    - Who is this person's **teacher/influencer**? → #extends
    - Who are this person's **collaborators**? → #backs
    - Who are this person's **debate opponents**? → #challenges
    - What **school/institution/journal** are they affiliated with? → #backs
    - Check if these related people/schools/institutions have existing wiki pages; if a person is referenced in 2+ sources but has no card, flag for creation
    - Write the results into the person card's `## 学术脉络` section
11. Update/create concept pages — **scan for insight candidates first** (see 5 detection patterns in card-types.md), then extract terminology, action, schema, basic, index-card cards. **Same archive-before-update rule as step 6. When writing `## 关联` sections, use the cross-reference results from step 7 to establish at least one cross-source link per card.**
12. Extract notable quotes and new words → create atom pages (only when the source contains genuinely striking quotes or domain-specific terms worth independent tracking)
13. **Check card extraction density** — verify the extraction is thorough enough (see Card Extraction Guidelines in card-types.md)
14. **Alias deduplication** — when a new source refers to an existing concept/entity by a different name, do NOT create a new page; instead add the variant to the existing page's `aliases` list and update its `sources` YAML list
15. **Merge conflicts** — when updating a page with information from a new source that contradicts existing claims, mark with a conflict callout:
    ```
    > [!conflict] Source disagreement
    > [[source-a]] claims X, while [[source-b]] claims Y.
    ```
16. Flag any contradictions with existing wiki content
17. Prepend to `wiki/log.md` (newest first, reverse chronological) — use `## [YYYY-MM-DD] ingest | <Title>` header, then list new pages using `[[wikilink]]` format (not backtick paths), and summarize cross-source connections. For archived pages, note the archive version.
18. **Post-ingest validation** — check for broken `[[wikilinks]]`, verify all new pages are in `index.md`, print a change summary including any archived versions

### Source Page Format

```markdown
---
title: "Source Title"
type: "[[source]]"
tags: []
date: YYYY-MM-DD
source_file: raw/...
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Source Title

<!-- CONFIGURABLE: Translate section headers below to your wiki's language -->

## 摘要
2–4 sentence summary.

## 核心观点
- Claim 1
- Claim 2

## 关键引用
> "Quote here" — context

## 关联
- [[EntityName]] — #extends how they relate
- [[ConceptName]] — #backs how it connects

## 矛盾
- Contradicts [[OtherPage]] on: ...

## 源文件
[[raw-filename]]
```

### Domain-Specific Templates

#### Diary / Journal Template
```markdown
---
title: "YYYY-MM-DD Diary"
type: "[[source]]"
tags: [diary]
date: YYYY-MM-DD
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# YYYY-MM-DD Diary

## 事件概要
## 关键决策
## 精力与情绪
## 关联
## 转变与矛盾
```

#### Meeting Notes Template
```markdown
---
title: "Meeting Title"
type: "[[source]]"
tags: [meeting]
date: YYYY-MM-DD
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Meeting Title

## 目标
## 主要讨论
## 决议
## 待办事项
```

---

## Query Workflow

Triggered by: *"query: <question>"* or `/wiki-query`

1. Read `wiki/index.md` to identify relevant pages
2. Read those pages with the Read tool
3. Synthesize an answer with inline citations as `[[PageName]]` wikilinks
4. Ask the user if they want the answer saved as `wiki/query/<slug>.md` using the Query Page Format below

### Query Page Format

```markdown
---
title: "Query: Brief Title"
type: "[[query]]"
tags: []
sources:
  - "[[source1]]"
  - "[[source2]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Query: Brief Title

## 问题
The original question asked by the user

## 回答
Synthesized answer based on the knowledge base, using [[PageName]] format inline citations

## 参考卡片
- [[CardName1]] — brief description of relevance
- [[CardName2]] — brief description of relevance
```

Self-validation: Question must not be empty; Answer must include at least one `[[wikilink]]` citation; At least 2 reference cards.

<!-- CONFIGURABLE: Translate section headers (问题, 回答, 参考卡片) to your wiki's language -->

---

## Synthesis Workflow

Triggered by: *"synthesize [[PageName]]"* or *"synthesize '主题' from [[Card1]], [[Card2]]"* or `/wiki-synthesis`

Two modes:
- **Mode 1 (from a card)**: `synthesize [[SomeCard]]` — AI auto-collects all related cards
- **Mode 2 (from a selection)**: `synthesize "theme" from [[Card1]], [[Card2]], [[Card3]]` — user provides theme + card list

### Mode 1 Steps (from a seed card)

1. Read the seed card, extract `title`, `aliases`, all `[[wikilinks]]` in body and frontmatter
2. Grep across `wiki/` (excluding `archive/`, `types/`) for the seed card's title, aliases, and page name appearing in other cards' body text, `sources`, or `## 关联` sections
3. Read all discovered related cards
4. **Choose dimensions** — AI selects the most fitting grouping angle from: Timeline / Theme Classification / Geography / Person Network / Causal Chain / Debate & Contrast / Methodology Schools / or another angle that better fits the data. State the chosen dimension and reasoning.
5. **Group into 4±3 groups** (aligned with working memory capacity). Each group gets a descriptive name.
6. **Extract fact sentences** — for each card in each group, extract 2-5 key fact sentences **verbatim** from the card's fields. No rewriting, no paraphrasing. Each fact ends with `— [[CardName]]`.
7. Generate a synthesis title
8. Write to `wiki/syntheses/<slug>.md` using the Synthesis Page Format
9. Update `wiki/index.md` — add entry under Syntheses section
10. Prepend to `wiki/log.md` (newest first): `## [YYYY-MM-DD] synthesis | <Title>`

### Mode 2 Steps (from user selection)

1. Read all user-specified cards
2. Continue from Mode 1 Step 4 (skip auto-collection), using the user-provided theme as the synthesis title seed

### Synthesis Page Format

```markdown
---
title: "Synthesis Title"
type: "[[synthesis]]"
tags: []
sources:
  - "[[source1]]"
  - "[[source2]]"
seed: "[[SeedCard]]"
scope:
  - "[[Card1]]"
  - "[[Card2]]"
  - "[[Card3]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
revisions: []
---

# Synthesis Title

## 维度

**Seed**: [[SeedCard]] (Mode 1) / User-specified theme (Mode 2)
**Cards included**: N (entity: X, concept: Y, atom: Z)
**Grouping dimension**: Chosen dimension with one-sentence rationale

## 分组

### Group 1: Group Name

> Group overview (1-2 sentences)

- Fact sentence 1 — [[CardName1]]
- Fact sentence 2 — [[CardName1]]

### Group 2: Group Name

> Group overview

- Fact sentence 1 — [[CardName2]]

## 原卡链接

- [[Card1]] — brief note
- [[Card2]] — brief note
```

### Fact Sentence Rules

- **Verbatim**: every fact sentence is copied word-for-word from a field in the source card. No rewriting, no rhetorical polish.
- **Attributed**: every fact sentence ends with `— [[CardName]]` linking back to the source card.
- **Volume**: 2-5 fact sentences per card, selecting the most essential points.
- **Language**: preserve the original language of the card field.

### Version Mechanism

Synthesis pages follow the same versioning rules as other wiki pages:
- Re-running a synthesis after new cards are added triggers the version merge workflow (Ingest step 6)
- Old version archived to `wiki/archive/{Name}-V{N}.md`, new version merges old + new cards

<!-- CONFIGURABLE: Translate section headers (维度, 分组, 原卡链接) to your wiki's language -->

---

## Lint Workflow

Triggered by: *"lint the wiki"* or `/wiki-lint`

Use Grep and Read tools to check for:
- **Orphan pages** — wiki pages with no inbound `[[links]]` from other pages (exclude `wiki/archive/` and `wiki/types/`)
- **Broken links** — `[[WikiLinks]]` pointing to pages that don't exist (exclude links in `wiki/archive/`)
- **Contradictions** — claims that conflict across pages
- **Stale summaries** — pages not updated after newer sources
- **Missing entity pages** — entities mentioned in 3+ pages but lacking their own page
- **Data gaps** — questions the wiki can't answer; suggest new sources

Output a lint report and ask if the user wants it saved to `wiki/lint-report.md`.

---

## Health Workflow

Triggered by: *"health"* or `/wiki-health`

Run: `python tools/health.py` (or `python tools/health.py --json` for machine-readable output)

Fast structural integrity checks — **zero LLM calls**, safe to run every session:
- **Empty / stub files** — pages with no content beyond frontmatter
- **Index sync** — `wiki/index.md` entries vs actual files on disk (exclude `wiki/archive/`)
- **Log coverage** — source pages missing a corresponding `ingest` entry in `wiki/log.md`

Output a health report. Use `--save` to write to `wiki/health-report.md`.

### Health vs Lint Boundary

| Dimension | `health` | `lint` |
|---|---|---|
| **Scope** | Structural integrity | Content quality |
| **LLM calls** | Zero | Yes (semantic analysis) |
| **Cost** | Free | Tokens |
| **Frequency** | Every session, before other work | Every 10-15 ingests |
| **Checks** | Empty files, index sync, log sync | Orphans, broken links, contradictions, gaps |
| **Tool** | `tools/health.py` | `tools/lint.py` |
| **Run order** | First (pre-flight) | After health passes |

> Run `health` first — linting an empty file wastes tokens.

---

## Graph Workflow

Triggered by: *"build the knowledge graph"* or `/wiki-graph`

When the user asks to build the graph, run `tools/build_graph.py` which:
- Pass 1: Parses all `[[wikilinks]]` → deterministic `EXTRACTED` edges
- Pass 2: Infers implicit relationships → `INFERRED` edges with confidence scores
- Runs Louvain community detection
- Outputs `graph/graph.json` + `graph/graph.html`
- **Excludes** `wiki/archive/` and `wiki/types/` — archived versions and type definitions are not graph nodes

If the user doesn't have Python/dependencies set up, instead generate the graph data manually:
1. Use Grep to find all `[[wikilinks]]` across wiki pages (**excluding** `wiki/archive/` and `wiki/types/`)
2. Build a node/edge list
3. Write `graph/graph.json` directly
4. Write `graph/graph.html` using the vis.js template
