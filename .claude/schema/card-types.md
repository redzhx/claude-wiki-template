# Card Type Guide

<!-- CONFIGURABLE: This file defines 11 card types based on Yang Zhiping's Card Method (卡片大法).
     The card types, their names, templates, and validation rules are the DEFAULT PRESET.
     To customize for your own knowledge system:
     1. Rename/remove/add card types in the hierarchy below
     2. Adjust templates to match your domain
     3. Update the extraction guidelines with your own density targets
     4. Translate Chinese display names if using a non-Chinese wiki
     The structural pattern (type → template → self-validation → extraction priority) is reusable. -->

## Card Type Value Hierarchy

Cards are not equal in value. The priority order for extraction:

1. **insight (新知卡)** — **highest value**. Records cognitive framework shifts (已知→新知). Counter-intuitive knowledge is rarer and more durable than definitions or procedures.
2. **action (行动卡)** — actionable methods and techniques.
3. **terminology (术语卡)** — precise definitions of key concepts.
4. **schema (图示卡)** — frameworks where spatial/structural relationships are the core knowledge.
5. **person / event** — entities.
6. **quote / new-word** — atomic fragments.
7. **index-card** — structured lists and classifications.
8. **basic (基础卡)** — valuable knowledge that resists any fixed template; free-form but not a dumping ground.

**Hard rule**: Scan for insight candidates FIRST before extracting any other card type. If a dense informational source yields zero insights, you have almost certainly missed something — re-read the source looking for implicit reversals.

## Quick Reference: Source Text → Card Types

<!-- CONFIGURABLE: Adjust mapping to your domain's text types -->

| Text Type | Description | Primary Card Types |
|-----------|-------------|-------------------|
| General | Any text may contain | basic, action |
| Informational | Popular science, academic, argumentative | **insight (priority)**, terminology, person, schema, event |
| Narrative | Novel, biography, history, long-form journalism, personal essay, memoir | event, person, insight, action, quote |
| Aesthetic | Poetry, prose, literature | new-word, quote |

> Event cards are not limited to narrative texts. **Research experiments** (e.g., EEG studies) and **historical events** (e.g., the first proposal of a theory and its background) in informational texts also fit the event card template.

---

## Card Type Templates

### 1. Basic Card (基础卡) — `concepts/`

The basic card is the **anti-template** card type. Use it when knowledge is genuinely valuable but forcing it into a fixed template would distort the content.

**Content suitable for basic cards**:
- Cross-topic synthesis that can't be reduced to a single concept
- Multi-angle parallel expositions
- Complete records of dialogues/debates/refutations
- Value judgments and aesthetic commentary
- Character trait distillation and elaboration

**Two hard constraints**:
- Must have a `## 关联` section linking to other cards
- Body must have substantive content — cannot be a placeholder

```markdown
---
title: "Card Title"
aliases: []
type: "[[concept]]"
card_type: "[[basic]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Card Title

Free-form body. Organize naturally by content — headings, bold, lists, quotes, paragraphs,
whatever the content demands.

## 关联
- [[RelatedCard|DisplayName]] — #relationship-tag description
```

Self-validation: Body must have substantive content; `## 关联` must have at least one entry.

---

### 2. Action Card (行动卡) — `concepts/`

```markdown
---
title: "Action Title"
aliases: []
type: "[[concept]]"
card_type: "[[action]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Action Title

## 原理
> "Original quote explaining the principle behind this action method" — Author/Source

Explain the core logic in your own words — why these steps work

## 步骤
1. [Executable step with verb]
2. ...
```

Self-validation: `## 原理` must include an original quote (`> "..." — Author`) AND explanation in your own words; steps must be executable (contain verbs); 2-7 steps.

**Detection beyond numbered steps**: Action-worthy methods often appear in narrative as personal practices rather than step-by-step instructions. Signal phrases include "I always...", "my practice is...", "the way I do this is...", "over time I developed...", and similar first-person procedural descriptions. These are valid action card candidates — frame the narrative method into executable steps for the `## 步骤` section.

---

### 3. Insight Card (新知卡) — `concepts/` — ⭐ Highest Value

Insight cards record **cognitive framework shifts**, not mere knowledge accumulation. They answer "what did I get wrong before?" or "what didn't I realize before?".

**5 Detection Patterns**:

| Pattern | Signal Words | Example |
|---------|-------------|---------|
| Explicit reversal | "I used to think... actually...", "Not X but Y", "People often... but..." | "People often dismiss formatting conventions as trivial, but they actually reflect the author's disciplinary identity" |
| Correcting common misconception | "Many think...", "At first glance...", "On the surface... but deeply..." | "Structural reading isn't about chapter outlines — 'structure' means the author's knowledge structure" |
| Revealing hidden commonality | "Seemingly different X actually share Y", "Different as... but at the base..." | "Dawkins and Sacks differ like zoo and botanical garden, but share the same cognitive style" |
| Counter-intuitive conclusion | Causal reversal, scale reversal, direction reversal | "Not reading more is better, but mastering cognitive style to handle infinite authors" |
| Conceptual redefinition | Redefining a term, revealing misunderstood meaning | "'Structure' in structural reading means cognitive framework, not chapter structure" |

```markdown
---
title: "Insight Title"
aliases: []
type: "[[concept]]"
card_type: "[[insight]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Insight Title

## 已知
Previous understanding / common view

## 新知
New understanding — must include a specific cognitive change

## 证据
Evidence and examples supporting the new understanding

## 举例
Concrete examples showing how the insight applies to real situations
```

Self-validation: `## 已知` and `## 新知` must form a contrast; `## 新知` must contain a specific cognitive change, not vague statements; `## 举例` must be concrete. **Additional check: if an informational source yields zero insight cards, re-read the source for implicit reversals.**

---

### 4. Terminology Card (术语卡) — `concepts/`

```markdown
---
title: "Term Name"
aliases: []
type: "[[concept]]"
card_type: "[[terminology]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Term Name

## 定义
> "Original quote, preserve source language" — Author/Source, [[SourcePage]]

[Who] proposed in [when] under [what context], referring to [rigorous definition]

## 原理
Explain the principle in your own words — must not duplicate the definition

## 举例
- Concrete, practical examples
```

Self-validation: `## 定义` must start with `> "original quote"` format, preserving source language; `## 原理` must explain in your own words, not duplicate the definition (<50% similarity); at least one `## 举例`.

---

### 5. Person Card (人物卡) — `entities/`

```markdown
---
title: "Person Name"
aliases: []
type: "[[entity]]"
card_type: "[[person]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Person Name

## 小传
Full name, birth/death years, primary identity, key experiences

## 主要贡献
Core achievements and impact

## 代表作
Works, papers, projects, etc.

## 学术脉络
Academic mentorship, collaboration, debate relationships, and affiliations

### 人物关系 (Mentorship, Collaboration, Debate)
- [[Brunswik|Egon Brunswik]] — #extends PhD advisor, inherited lens model
- [[West|Stephen West]] — #backs collaborator, co-authored RAM (1987)
- [[Mischel|Walter Mischel]] — #challenges opposing position on personality consistency

### 学派与机构
- [[StanfordUniversity|Stanford University]] — #backs professor 1989-1995
- [[PSPB|PSPB]] — #backs multiple papers published
- Big Five school — #backs core member (plain text if no wiki page)

Format rule: Use `[[PageName|DisplayName]]` links for existing wiki pages; plain text for entities without pages.

## 别名
Other common names, foreign names
```

Self-validation: `## 小传` must not be empty; `## 主要贡献` must have at least one entry.

---

### 6. Schema Card (图示卡) — `concepts/`

#### Essential boundary: what qualifies as a schema card?

**Schema card ≠ a card that contains a diagram.** The single criterion:

> **If you delete the diagram, does the card's core knowledge remain?**
>
> - **Yes** → Not a schema card. Keep the original card_type; the diagram is a supporting element.
> - **No / severely残缺** → Schema card. The spatial structure IS the core knowledge; text cannot substitute it.

**Positive examples (genuine schema cards)**:

| Card | After deleting diagram |
|------|----------------------|
| Drama Triangle | Only "three roles dynamically switch" remains — the persecutor↔rescuer↔victim spatial topology is lost |
| Tripartite Mind Model | Only "three layers of mind" remains — the supervisory hierarchy (autonomous→algorithmic→reflective) and bottom-up arrow direction are lost |
| PAC Model | Only "three ego states" remains — P-A-C nested structure and second-order subdivision containment are lost |

**Negative examples (should NOT be schema cards)**:

| Card | Essence | Correct card_type |
|------|---------|-------------------|
| G Formula | An equation definition; G=C+S+P is already complete | `terminology` |
| WOOP Method | Four executable steps | `action` |
| Five Book Tiers | Five-level classification index | `index-card` |

#### Template

```markdown
---
title: "Framework/Model Name"
aliases: []
type: "[[concept]]"
card_type: "[[schema]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Framework/Model Name

## 图示结构
[Choose from the 6 visualization forms below based on the model's spatial/structural nature]

## 说明
How parts relate, applicable scenarios, theoretical significance
```

#### Six Visualization Forms (available for all card types)

**Form 1: Spatial Structure Diagram (ASCII / Mermaid)** — for frameworks with spatial relationships

```
        Persecutor
           /\
          /  \
Rescuer —————— Victim
```

Use ASCII art or Mermaid flowchart/quadrantChart/graph.

**Form 2: Formula** — for mathematical/logical equations

```markdown
$$G = C + S + P$$

| Symbol | Meaning |
|--------|---------|
| G | Game |
| C | Con |
```

**Form 3: Table/Matrix** — for dimensional comparison

**Form 4: Hierarchy List** — for classification trees

**Form 5: Flow/Stages** — for sequential/phase/cycle models

**Form 6: Instance Fill** — concrete examples following the theoretical framework (can overlay any form above)

#### Form Selection

| Model Essence | Preferred Form |
|---------------|---------------|
| Spatial relations (up/down, inside/outside, near/far) | Form 1: ASCII box-layer |
| 2×2 / 3×3 matrix | Form 1: Mermaid quadrantChart |
| Flow / causal chain | Form 1: Mermaid flowchart or Form 5 |
| Classification hierarchy | Form 4: Indented tree or Mermaid mindmap |
| Mathematical relation | Form 2: Formula + symbol table |
| Dimension comparison (features × types) | Form 3: Markdown table |

Self-validation: Core knowledge severely残缺 when diagram is removed; `## 图示结构` must include at least one visualization; `## 说明` must not be empty.

---

### 7. Event Card (事件卡) — `entities/`

STAR model: Situation (Time) + Space + Actor + Reaction.

```markdown
---
title: "Event Name"
aliases: []
type: "[[entity]]"
card_type: "[[event]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Event Name

## 概述
1-2 sentences answering: "what is this event, in a nutshell?" — person/organization did what, when, where, with what significance. A reader should understand the event from this section alone.

## 时间 (Time)
When it happened, duration, or timeline

## 空间 (Space)
Location, setting, environment

## 行动者 (Actor)
People/organizations involved: [[PersonName]], their roles and motivations

## 反应 (Reaction)
Outcomes, impacts, responses from various parties, subsequent developments
```

Self-validation: At least 3 of the 4 STAR fields must be filled (cannot be all empty).

---

### 8. Quote Card (金句卡) — `atoms/`

Quote cards are a **personal capture mechanism** — record sentences that "hit you." They don't need objective importance, only subjective impact.

Key principle: **Better to capture too many than miss one.** Every quote card must answer: **Why did you pick it?**

```markdown
---
title: "Quote — Author"
aliases: []
type: "[[atom]]"
card_type: "[[quote]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Quote — Author

## 原文
> "Original quote" — Author, Source

## 摘录理由
> Why did this hit you? — Striking insight / Beautiful expression / Thought-provoking / Stylish phrasing / Emotional resonance / Other

Write 1-3 sentences in your own words explaining what moved you. Be specific — which word was well-chosen? What layer of meaning surprised you? What did it help you clarify?

## 评论 (optional)
Further free-form reflections
```

Self-validation: `## 摘录理由` is required and must specify the concrete reason; `## 原文` and attribution must not be empty; the reason must not merely restate the quote.

**Floor rule for source pages**: When a source page's `## 关键引用` section has 3+ entries, extract at least one quote card. Narrative sources with strong writing style should produce 2-3 quote cards per ingest — the personal capture mechanism only works if you actually capture.

**AI constraint**: AI has no "personal feelings," but can simulate from a reader's perspective. Prioritize sentences with genuine linguistic highlights or cognitive impact. When uncertain: capture more, let the reader (user) judge.

---

### 9. New Word Card (新词卡) — `atoms/`

For words **invented** by a specific writer, or **creative repurposing** of existing words.

```markdown
---
title: "New Word"
aliases: []
type: "[[atom]]"
card_type: "[[new-word]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# New Word

## 新词
The word and its definition in your own words

## 原句
Original sentence containing the word (context)

## 造句
Example usage or sentence using the word
```

Self-validation: `## 新词` definition must not copy the source verbatim; must include `## 原句`.

---

### 10. Index Card (索引卡) — `concepts/`

```markdown
---
title: "Index Title"
aliases: []
type: "[[concept]]"
card_type: "[[index-card]]"
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Index Title

## 索引类型
Classification dimension (e.g., by theme, by time, by person)

## 条目
- [[PageName1]] — one-line description
- [[PageName2]] — one-line description
```

Self-validation: `## 索引类型` must not be empty; at least 2 `## 条目`.

#### Timeline Variant

When listing milestones, historical events, or any sequence unfolding over time, use the **time prefix** format in `## 条目`:

```markdown
## 条目
- **YYYY-MM-DD**: Event description — [[RelatedCard]]
- **YYYY-MM**: Event description — detail without link
- **YYYY**: Event description
```

Rules:
- Date prefix in bold (`**YYYY-MM-DD**`) followed by colon and space
- Entries sorted ascending (oldest first) by default; reverse chronological for recent-events-only lists
- Optional `[[wikilink]]` at end to connect to person/event/concept cards
- Time range spans: `**YYYY-MM** – **YYYY-MM**` for event ranges
- The "Situation" field can use specific dates, or relative epoch descriptions when exact dates are unknown

---

### 11. Synthesis Card (综述卡) — `syntheses/`

<!-- CONFIGURABLE: Adjust synthesis template to match your wiki's structure -->

```markdown
---
title: "Synthesis Title"
aliases: []
type: "[[synthesis]]"
tags: []
sources:
  - "[[source1]]"
  - "[[source2]]"
seed: "[[SeedCard]]"
scope:
  - "[[Card1]]"
  - "[[Card2]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
revisions: []
---

# Synthesis Title

## 维度
Grouping dimension and rationale

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

Self-validation: `## 维度` must not be empty; at least 2 groups; `## 原卡链接` at least 2 entries.

---

## Card Extraction Guidelines

The goal of the Card Method is to extract **atomic knowledge fragments** — one card, one idea.

### Density Targets

<!-- CONFIGURABLE: Adjust targets for your domain -->

| Source Type | Expected Cards (概念+实体+原子) |
|------------|-------------------------------|
| Research paper (10-30 pages) | 8-15 |
| Book chapter (dense, 20-50 pages) | 8-15 |
| Book chapter (light) | 5-8 |
| Blog post / short article | 3-6 |

These are floors, not ceilings.

### Card Type Diversity — Avoid Schema-Only Extraction

The most common failure mode is producing only 2-3 schema cards for a chapter and stopping. A healthy extraction uses 4+ different card types. **For informational text, insight cards are non-optional — a zero-insight extraction is a red flag that requires re-scanning the source.**

| If the source... | Create a... |
|-----------------|-------------|
| Defines a term or concept | **terminology** card |
| Reveals a cognitive shift (old→new understanding) | **insight** card |
| Describes a framework with visual structure | **schema** card |
| Gives actionable steps or methods | **action** card |
| Lists/classifies things | **index-card** card |
| Introduces a person | **person** card |
| Describes a research experiment, study, or historical event | **event** card |
| Has a striking quote worth independent tracking | **quote** card |
| Introduces a domain-specific unfamiliar term | **new-word** card |
| Has free-form knowledge that fits no template above | **basic** card |

**Anti-pattern**: merging 3-4 distinct concepts into one schema card just because they share a theme.
**Anti-pattern**: changing a card to `schema` just because it contains a diagram/table/formula. Use the **diagram deletion test**: if removing the diagram leaves the core knowledge intact, the diagram is a supporting element, not the card's essence.

### Narrative Source Extraction

Narrative-heavy sources (long-form journalism, personal essays, memoirs) differ fundamentally from informational sources. Their knowledge is embedded in storytelling, not structured as claims and evidence.

**Detection patterns specific to narrative sources:**

| Narrative pattern | What to extract | Card type |
|---|---|---|
| Author describes a personal routine or method ("I always...", "My practice is...") | The method itself, framed into executable steps | action |
| Author describes a shift in their own thinking ("I used to think... but then...") | The cognitive transformation | insight |
| Author mentions an organization, experiment, study, or historical moment | The event/initiative as a knowledge artifact | event |
| A sentence with striking metaphor, vivid description, or elegant phrasing | The sentence itself, with reason for selection | quote |
| A person introduced with backstory and substantial contribution | The person profile | person |
| A domain-specific term coined or redefined in the narrative | The term definition | terminology |

**Key principle**: Narrative sources are NOT lower-value than informational sources. They often contain more memorable insights precisely because knowledge is embedded in concrete human experience. The extraction challenge is different, not easier — you must detect structured knowledge within unstructured storytelling.

**Common failure modes**:
- Skipping action card extraction because the method has no numbered steps (look for "I do X" patterns)
- Skipping insight card extraction because the insight is told through anecdote rather than stated directly
- Skipping event card extraction because the initiative is mentioned in passing rather than described formally
- Creating zero quote cards for a well-written narrative source (hard rule: 2-3 quote cards per narrative ingest)

### Image Preservation

Source images (format `![](image-file)`) carry important knowledge. When creating wiki cards:

- Note the relationship between images and surrounding text — text before images usually explains them
- When an image directly illustrates core card content, include the image reference in the card
- Use the exact same `![](image-file)` format as the source; don't modify filenames or paths
- Don't blindly copy all images — only those directly relevant to **this card**

**Image strategy by card_type**:

| card_type | Image Strategy |
|-----------|---------------|
| schema | **Must include** source images (in `## 图示结构`; can supplement or replace ASCII/Mermaid) |
| terminology | Include in `## 原理` or `## 举例` if it helps understanding |
| insight | Include in relevant section if it shows the core contrast of cognitive change |
| action | Include in `## 步骤` if it shows step flow |
| person / event / quote / new-word | Optional |
| basic / index-card | Free choice |

### Extraction Scan (Mental Checklist)

After writing the source page, go through this checklist **in priority order**:

1. ⭐ **Every cognitive reversal (old→new understanding)** → insight card candidate — scan for ALL 5 detection patterns. **If the result is 0 insight cards for an informational source, re-read the source immediately.**
2. **Every defined term** → terminology card candidate
3. **Every numbered step / method / how-to** → action card candidate
4. **Every diagram/model/framework where spatial structure IS the core knowledge** → schema card candidate
5. **Every person with substantial contribution** → person card candidate
6. **Every research experiment, study, or historical event** → event card candidate
7. **Every striking sentence worth remembering** → quote card candidate (better to capture too many)
8. **Every domain-specific jargon introduced** → new-word card candidate

9. **For narrative-heavy sources (long-form journalism, personal essays, memoirs), additionally check**:
   - **Embedded methods**: Any personal practice described through storytelling → action card (even without numbered steps)
   - **Narrative insight**: Any described change in the author's own understanding → insight card
   - **Mentioned initiatives/events**: Any organizations, experiments, or historical moments referenced → event card
   - **Linguistic highlights**: Any particularly striking phrasing, metaphor, or elegant expression → quote card
   - Run this check AFTER the standard checklist; narrative sources have BOTH informational content AND story-embedded knowledge

**Post-extraction self-check**:
- Did I produce at least one insight card? If not, re-read the source specifically for implicit reversals.
- Did I merge multiple independent concepts into one schema card? If so, split them.
- Did I use at least 4 different card types? If not, scan for missing categories.
- ⭐ **Did I use #challenges at least once, or confirm there is genuinely nothing contradictory in this batch?** If zero #challenges, scan once more: does any new card disagree with an existing wiki page? Sources often debate. Missing #challenges usually means an academic conflict was silently smoothed into #extends.
- Did I include relevant source images in schema/terminology/insight cards? If the source had images near key concepts, check that they were preserved.
<!-- CONFIGURABLE: If your wiki uses a different language, add your own H1 language check rule here -->
