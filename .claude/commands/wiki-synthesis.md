Synthesize a theme from wiki cards into a structured overview.

Usage: /wiki-synthesis $ARGUMENTS

$ARGUMENTS can be either:
- A seed card: `[[PageName]]` — AI auto-collects all related cards
- A theme + card list: `"Theme Name" from [[Card1]], [[Card2]], [[Card3]]`

Follow the Synthesis Workflow defined in CLAUDE.md:
1. Read the seed card(s) / user-specified cards
2. Auto-discover related cards by grepping for the seed card's title/aliases across wiki/
3. Choose a grouping dimension suitable for the data
4. Group cards into 4±3 groups
5. Extract verbatim fact sentences from each card's fields
6. Write the synthesis page to wiki/syntheses/<slug>.md
7. Update wiki/index.md and wiki/log.md
