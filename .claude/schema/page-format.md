# Page Format Reference

<!-- CONFIGURABLE: The card type names and domain tags in this file are the default preset
     (based on Yang Zhiping's Card Method / 卡片大法). To customize:
     1. Replace card_type names with your own
     2. Replace domain tags with your own taxonomy
     3. Translate section headers if your wiki uses a non-Chinese language
     4. Update type-to-directory mappings to match your wiki structure -->

## Frontmatter

Every wiki page uses this frontmatter:

```yaml
---
title: "Page Title"
aliases: []
type: "[[source|源文件]]" | "[[entity|实体]]" | "[[concept|概念]]" | "[[synthesis|综述]]" | "[[query|问答]]" | "[[atom|原子]]"
card_type: "[[person|人物卡]]" | "[[event|事件卡]]" | "[[terminology|术语卡]]" | "[[insight|新知卡]]" | "[[action|行动卡]]" | "[[schema|图示卡]]" | "[[basic|基础卡]]" | "[[index-card|索引卡]]" | "[[quote|金句卡]]" | "[[new-word|新词卡]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
revisions: []                 # archived versions, e.g. ["[[PageName-V1]]", "[[PageName-V2]]"]
score: 1-10                    # optional quality/insight rating, displayed as colored badge
---

# Page Title
```

- `type` determines the directory (`entities/`, `concepts/`, `atoms/`, etc.) — links to `wiki/types/` definition page
- `card_type` determines the template and self-validation rules — links to `wiki/types/` definition page
- `card_type` is required for entity, concept, and atom pages; omit for source and synthesis pages
- `aliases` lists alternative names for this page (e.g., translations, abbreviations, synonyms). Obsidian treats aliases as valid link targets — `[[alias]]` will resolve to this page. When ingesting new sources that reference an existing concept by a different name, add the variant to `aliases` instead of creating a duplicate page.
- **Bilingual titles**: If the `title` is in one language, include a translation in `aliases`. The browser build script detects the first alias containing characters from a different script and displays the title as `"Original (Translation)"` automatically.
- `sources` is a YAML list of `[[wikilink]]` entries pointing to source pages. Single source uses one list item; multiple sources use additional `- "..."` lines. Each update appends the new source to this list (no duplicates).
- `created` is the date the wiki page was first created; `updated` is the date of last modification
- `revisions` lists archived versions in `wiki/archive/` (e.g., `["[[CognitiveDebt-V1]]"]`). Placed in YAML so graph builders only scan body wikilinks, keeping archive nodes out of the knowledge graph. Omit this field on first creation. **Once the page is updated with information from a new source, `revisions` MUST contain the archived version reference.**
- Every page starts with `# Title` as the first line after frontmatter, matching the `title` field

Use `[[PageName|DisplayName]]` wikilinks to link to other wiki pages. The pipe alias renders display text while the link target remains the page name.

---

## Source Contributions (来源贡献)

When a card synthesizes content from multiple sources, add a `## 来源贡献` section to describe what each source contributed. This is especially useful for concept and synthesis cards built from 3+ sources.

```markdown
## 来源贡献
- [[paper-2025-gpt4-report|GPT-4 Technical Report]] — 提供了模型能力和评估基准数据
- [[article-anthropic-safety|Anthropic Safety Approach]] — #backs 提供了安全分类框架的具体案例
```

Format:
- `- [[SourcePage|Display]] — description of what this source contributed`
- Relationship tags (`#extends`, `#backs`, etc.) are optional but recommended when the contribution has a clear conceptual relationship
- Position: after the main body, before `## 关联`

---

## Connections Format (关联)

**Every entity, concept, and atom page MUST end with a `## 关联` section.** This is the knowledge graph's primary link layer — without it, pages become orphans.

In `## 关联` sections, each link must include a relationship tag:

```markdown
## 关联
- [[PageName|DisplayName]] — #extends builds on its foundation
- [[OtherPage|DisplayName]] — #challenges contradicts its core claim
```

### 4 Relationship Types

<!-- CONFIGURABLE: Rename these tags or adjust semantics for your domain -->

| Tag | Meaning | When to use |
|-----|---------|-------------|
| `#backs` | Supports | A provides evidence/categorization/component support for B's claims |
| `#challenges` | Challenges | A disagrees with or narrows the scope of B's claims |
| `#extends` | Extends | A builds on or is caused by B |
| `#applies` | Applies | A puts B's theory into practice |

### Decision Flow

```
A provides evidence / categorization / component support for B?        → #backs
A disagrees with or narrows B's scope?                                 → #challenges
A builds on / is caused by B?                                          → #extends
A puts B's theory into operational practice?                           → #applies
```

Rules:
- At least one `[[wikilink]]` per page
- Every link must carry exactly one of the 4 relationship tags listed above
- **Prefer #challenges over #extends when there is any tension** — the most common mistake is smoothing a mild conflict into a safe #extends
- Source pages use their own `## 关联` section (see Source Page Format in workflows.md)
- `## 关联` is always the **last** section in the page body

---

## Academic Lineage (学术脉络)

**Used only for person pages**, placed between `## 主要贡献` and `## 代表作`. A structured section tracking academic mentorship, collaboration, debate opponents, and affiliations (school/institution/journal).

### Three Relationship Categories

| Relation | Tag | Criteria |
|----------|-----|----------|
| Mentorship / Foundation | #extends | A inherits B's theoretical framework/academic tradition, or clear teacher-student/mentoring relationship |
| Collaboration | #backs | A co-authored with B, shared a lab, or belonged to the same school/institution |
| Debate | #challenges | A and B have open academic disputes on core claims or hold opposing positions |

### Format

```markdown
## 学术脉络

### 人物关系
- [[Brunswik|Egon Brunswik]] — #extends PhD advisor, inherited lens model
- [[West|Stephen West]] — #backs collaborator, co-authored RAM (1987)
- [[Kahneman|Daniel Kahneman]] — #challenges fundamental disagreement on nature of cognitive biases

### 学派与机构
- [[StanfordUniversity|Stanford University]] — #backs professor 1989-1995
- [[MaxPlanckInstitute|Max Planck Institute]] — #backs director since 1995
- Big Five school — #backs core member (plain text if no wiki page exists)
```

Rules:
- **Person relations** preferentially use `[[PageName|DisplayName]]` links to existing wiki person cards; people without pages use plain text and should be flagged for card creation
- **Schools & institutions** follow the same rule — link if a page exists, plain text otherwise

---

## Domain Tags (领域标签)

<!-- CONFIGURABLE: Replace this entire taxonomy with your own domain tags.
     The two-layer system (domain + sub-tag) is the reusable pattern. -->

Use a two-layer tagging system: **domain** (coarse filter) + **sub-tag** (fine filter). A page can have multiple domain and sub-tags.

```yaml
tags: [cognitive-science, behavior, emotion]
tags: [ai, ai-coding, cognitive-science, habit]
tags: [psychology, edu-psych, education]
```

### Default Domain → Sub-tag Reference

| Domain | Sub-tag | Coverage |
|--------|---------|----------|
| **cognitive-science** | `reading` | Cognitive reading |
| | `writing` | Cognitive writing |
| | `poetry` | Cognitive poetry |
| | `info-analysis` | Information analysis |
| | `decision` | Decision analysis |
| | `argumentation` | Argumentation analysis |
| | `habit` | Expert habits |
| | `behavior` | Behavioral analysis |
| | `advantage` | Life advantage theory |
| | `life-dev` | Life development |
| | `emotion` | Emotion情境论 |
| **psychology** | `edu-psych` | Educational psychology |
| | `money-psych` | Money psychology |
| | `family-training` | Family training |
| **education** | `edu-trend` | Education trends & policy |
| | `school-refusal` | School refusal |
| | `school-planning` | School planning |
| **ai** | `ai-product` | AI product |
| | `ai-coding` | AI coding |
| | `ai-model` | AI model development |
| | `ai-art` | AI art |
| | `ai-video` | AI video |
| **business** | `trade` | Trade |
| | `economy` | Economy |

### Special Source Tags

| Tag | Usage |
|-----|-------|
| `source:arxiv` | Academic paper from arXiv |
| `source:blog` | AI lab or industry blog post |
| `source:policy` | Government or think tank policy document |
| `source:report` | Industry or academic report |
| `source:news` | News article on developments |

**Tagging rules:**
- Always include at least one domain tag
- Add sub-tags for specificity; a page can have multiple sub-tags across domains
- When content spans domains (e.g., educational psychology), tag both: `[psychology, edu-psych, education]`
- New sub-tags may be created as needed, but always nest under an existing domain
- Source tags (e.g., `source:arxiv`) are optional but recommended for traceability
