#!/usr/bin/env python3
"""Shared configuration loader for wiki template tools.

Reads tools/config.yaml and provides typed access to all settings.
Falls back to sensible defaults if the config file is missing.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = REPO_ROOT / "tools" / "config.yaml"


def _load_raw() -> dict:
    """Load the raw config dict from YAML, or return empty dict."""
    if CONFIG_PATH.exists():
        if yaml is not None:
            return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
        else:
            raise ImportError(
                "PyYAML is required to load config.yaml. Install with: pip install pyyaml"
            )
    return {}


# Load once at module level
_config = _load_raw()


def get(key: str, default=None):
    """Get a config value by dot-separated key path (e.g. 'lint.min_outbound_links')."""
    keys = key.split(".")
    val = _config
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return default
        if val is None:
            return default
    return val


# ── Convenience accessors used by tools ────────────────────────────────

def wiki_dir() -> Path:
    return REPO_ROOT / get("wiki_dir", "wiki")


def index_file() -> Path:
    return REPO_ROOT / get("index_file", "wiki/index.md")


def log_file() -> Path:
    return REPO_ROOT / get("log_file", "wiki/log.md")


def graph_dir() -> Path:
    return REPO_ROOT / get("graph_dir", "graph")


def graph_json() -> Path:
    return REPO_ROOT / get("graph_json", "graph/graph.json")


def raw_dir() -> Path:
    return REPO_ROOT / get("raw_dir", "raw")


def excluded_dirs() -> set:
    return set(get("excluded_dirs", ["archive", "types"]))


def excluded_files() -> set:
    return set(get("excluded_files", ["index.md", "log.md", "lint-report.md", "health-report.md", "overview.md"]))


def relation_required_dirs() -> set:
    return set(get("relation_required_dirs", ["entities", "concepts", "atoms"]))


def stub_threshold() -> int:
    return get("stub_threshold_chars", 100)


def required_fields_all() -> list:
    return get("required_fields_all", ["title", "type", "created", "updated"])


def required_fields_card() -> list:
    return get("required_fields_card", ["card_type", "tags", "sources"])


def card_dirs() -> set:
    return set(get("card_dirs", ["entities", "concepts", "atoms"]))


def valid_types() -> set:
    return set(get("valid_types", ["source", "entity", "concept", "synthesis", "query", "atom"]))


def valid_card_types() -> set:
    return set(get("valid_card_types", [
        "person", "event", "terminology", "insight", "action",
        "schema", "basic", "index-card", "quote", "new-word",
    ]))


def type_display_names() -> set:
    return set(get("type_display_names", []))


def relations_header() -> str:
    return get("relations_header", "## 关联")


def type_color(type_name: str) -> str:
    colors = get("type_colors", {})
    return colors.get(type_name, "#999999")


def card_type_color(ct_name: str) -> str:
    colors = get("card_type_colors", {})
    return colors.get(ct_name, "#999999")


def llm_model_env() -> str:
    return get("llm.model_env", "LLM_MODEL")


def llm_default_model() -> str:
    return get("llm.default_model", "claude-sonnet-4-6")


def llm_max_tokens() -> int:
    return get("llm.max_tokens", 3000)


def lint_min_outbound() -> int:
    return get("lint.min_outbound_links", 2)


def lint_hub_min_chars() -> int:
    return get("lint.min_content_chars_for_hub", 500)


def lint_missing_entity_min() -> int:
    return get("lint.missing_entity_min_mentions", 3)


def lint_sample_size() -> int:
    return get("lint.semantic_sample_size", 20)


def lint_truncate_chars() -> int:
    return get("lint.semantic_page_truncate_chars", 1500)
