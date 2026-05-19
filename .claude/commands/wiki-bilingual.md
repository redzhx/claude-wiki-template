Create a bilingual (native-language + original) reading version of one or more source files.

Usage: /wiki-bilingual $ARGUMENTS

$ARGUMENTS can be:
- A single file path: `raw/article-foo.md`
- A pattern: `raw/article-*`

## Workflow Steps

### For a Single File

1. Read the source file completely
2. Extract metadata: H1 title and any URL/date/author from leading lines
3. Check if `raw/bilingual/<name>-bilingual.md` already exists. If yes:
   - Read existing bilingual file
   - Show which source it was based on and when
   - Ask user: skip / update / overwrite
4. Check for a glossary (`.claude/glossary.md`) and scan the source text for matching terminology
5. Translate the content paragraph by paragraph into the wiki's primary language:
   - Preserve section structure (## headings, --- separators)
   - Preserve paragraph boundaries
   - Preserve technical terms in original language
   - Preserve markdown formatting (bold, italic, links, lists, blockquotes)
   - Preserve code blocks and image markdown verbatim
   - For very long paragraphs (>5 sentences), split into smaller paragraph pairs
6. Write the bilingual file to `raw/bilingual/<name>-bilingual.md` using the format:
```markdown
---
original: "raw/<path-to-original>.md"
source_url: "<source-url>"
skip_ingest: true
created: <today>
updated: <today>
---

# Bilingual: <English Title>

> **Original**: [/raw/<filename>.md](/raw/<filename>.md)
> **Source**: <url>

---

## English Header / Translation Header

> Original English paragraph content, preserved verbatim.

Translation paragraph content, maintaining paragraph-by-paragraph correspondence.

> Next original paragraph...

Translation paragraph continues...
```
7. Add a reference link from the original to the bilingual version:
   - For `raw/` files: append `> 📖 [Bilingual Version](bilingual/<filename>-bilingual.md)` at the very end
   - Skip this step if the link already exists
8. **Update the wiki source page** (if it exists) so the bilingual link appears in the browser:
   - Check if `wiki/sources/<same-slug>.md` exists
   - If yes, add `📖 [Bilingual Version](/raw/bilingual/<filename>-bilingual.md)` to the `## 源文件` section if not already present
   - Update the `updated` date in the frontmatter
9. **Rebuild browser** (`build_browser.py` reads wiki files directly):
   ```bash
   python tools/build_browser.py
   ```
10. Summarize: what file was created, line count, any notable translation decisions

### For Batch (multiple files)

1. Resolve $ARGUMENTS to a list of file paths (use bash glob or ls)
2. Present the list to the user and ask for confirmation
3. For each file in the list, follow the Single File workflow steps 1-8
4. Run `python tools/build_browser.py` to rebuild the card browser
5. Provide a summary table: | File | Status | Lines | Notes |
