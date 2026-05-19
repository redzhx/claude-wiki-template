Ingest a source document into the wiki.

Usage: /wiki-ingest $ARGUMENTS

$ARGUMENTS should be the path to a file in raw/, e.g. `raw/articles/my-article.md`

Follow the Ingest Workflow defined in CLAUDE.md exactly:
1. Read the source file at the given path
2. Read wiki/index.md and wiki/overview.md for current context
3. Read `.claude/schema/card-types.md` and `.claude/schema/page-format.md` for card templates and format rules
4. Write wiki/sources/<slug>.md (source page format per workflows.md), including the `## 分析` section with:
   - 作者/机构学术地位 (author/institution status and level)
   - 论文整体水平 (paper quality, peer-review status, contribution)
   - 有趣度 (graph centrality rank, temporal evaluation of interestingness)
5. **Validate**: verify `source_file` frontmatter field points to an actual file on disk
6. **Detect bilingual**: if a bilingual version exists (`raw/bilingual/<slug>-bilingual.md`), ensure the `## 源文件` section links to it
7. Update wiki/index.md — add the new entry under Sources
8. Update wiki/overview.md — revise synthesis if warranted
9. **Archive** existing pages if this new source adds information to existing entity/concept/atom pages
10. Create/update entity pages (wiki/entities/) — choose card_type: person or event, use the corresponding Card Type template
11. Create/update concept pages (wiki/concepts/) — choose the best card_type, use the corresponding Card Type template
12. Preserve relevant images from the source when they directly illustrate card content
13. Extract notable quotes and new words → create atom pages in wiki/atoms/ (only when genuinely striking)
14. Flag any contradictions with existing wiki content
15. Append to wiki/log.md: ## [today's date] ingest | <Title>
16. **Post-ingest validation** — check for broken `[[wikilinks]]`, verify all new pages are in `index.md`
17. **Rebuild browser**: `python tools/build_browser.py` (auto-runs via PostToolUse hook after wiki file edits)

Card type selection guide (refer to CLAUDE.md Card Type Guide for full templates):
- Person mentioned → person card in entities/
- Historical event → event card in entities/
- Term/concept defined → terminology card in concepts/
- Cognitive update (old vs new understanding) → insight card in concepts/
- How-to / method → action card in concepts/
- Framework / model / diagram → schema card in concepts/
- Memorable quote → quote card in atoms/
- New/unfamiliar term → new-word card in atoms/

**Narrative source extraction**: For long-form journalism, personal essays, and memoirs, narrative-embedded knowledge may not present itself as formal claims. Check for:
- Personal methods described through storytelling → action card
- Described change in understanding → insight card
- Mentioned organizations/experiments/events → event card
- Striking phrasing or metaphor → quote card (2-3 per narrative ingest)
See `.claude/schema/card-types.md` section "Narrative Source Extraction" for full guidance.

After completing all writes, summarize: what was added, which pages were created or updated, card types assigned, domain tags applied, and any contradictions found.
