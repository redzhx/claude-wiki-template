# Language Adaptation Guide

The template defaults to English. To adapt for another language:

## For Chinese (中文) — reference configuration

The original Cognitive Atlas project uses Chinese. Key changes:

### 1. CLAUDE.md
Add output language rules:
```markdown
## Output Language
All wiki page body text MUST be written in Chinese (中文).

### H1 Title Language Rules
| Card Type | H1 Language |
|-----------|-------------|
| concept | Chinese or bilingual |
| person (foreign) | English or bilingual |
| person (Chinese) | Chinese |
| event | Chinese or bilingual |
| atom | Chinese |
```

### 2. Schema Files
Translate section headers in `.claude/schema/workflows.md`, `page-format.md`, and `card-types.md`:
- `## Summary` → `## 摘要`
- `## Key Claims` → `## 核心观点`
- `## Connections` → `## 关联`

### 3. Config
Add Chinese display names to `tools/config.yaml`:
```yaml
type_display_names:
  - 源文件
  - 实体
  - 概念
  - 综述
  - 问答
  - 原子
  - 人物卡
  - 事件卡
  - 术语卡
  - 新知卡
  - 行动卡
  - 图示卡
  - 基础卡
  - 索引卡
  - 金句卡
  - 新词卡
```

## For Other Languages

Follow the same pattern:
1. Translate section headers in all `.claude/schema/*.md` files
2. Add `<!-- CONFIGURABLE -->` markers where you've made changes
3. Update `type_display_names` in config
4. Translate UI text in `build_graph.py` HTML template
5. Update `CLAUDE.md` language rules
