Ingest a source document into the wiki.

Usage: /wiki-ingest $ARGUMENTS

$ARGUMENTS should be the path to a file in raw/, e.g. `raw/articles/my-article.md`

Follow the Ingest Workflow defined in CLAUDE.md exactly:
1. Read the source file at the given path
2. Read wiki/index.md and wiki/overview.md for current context
3. Write wiki/sources/<slug>.md (source page format per CLAUDE.md)
4. Update wiki/index.md — add the new entry under Sources
5. Update wiki/overview.md — revise synthesis if warranted
6. Create/update entity pages (wiki/entities/) — choose card_type: person or event, use the corresponding Card Type template
7. Create/update concept pages (wiki/concepts/) — choose the best card_type, use the corresponding Card Type template
8. Preserve relevant images from the source when they directly illustrate card content
9. Extract notable quotes and new words → create atom pages in wiki/atoms/ (only when genuinely striking)
10. Flag any contradictions with existing wiki content
11. Append to wiki/log.md: ## [today's date] ingest | <Title>

Card type selection guide (refer to CLAUDE.md Card Type Guide for full templates):
- Person mentioned → person card in entities/
- Historical event → event card in entities/
- Term/concept defined → terminology card in concepts/
- Cognitive update (old vs new understanding) → insight card in concepts/
- How-to / method → action card in concepts/
- Framework / model / diagram → schema card in concepts/
- Memorable quote → quote card in atoms/
- New/unfamiliar term → new-word card in atoms/

After completing all writes, summarize: what was added, which pages were created or updated, card types assigned, domain tags applied, and any contradictions found.
