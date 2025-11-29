"""Utilities for LangSmith/LangGraph tracing configuration."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

_DEFAULT_TAGS = ["idea2solid"]


def build_run_config(
    run_name: str,
    *,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return a LangGraph RunnableConfig with consistent tags/metadata.

    The configuration works whether or not LangSmith tracing is enabled. If
    `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` are set, the LangGraph
    run will appear in the LangSmith project (optionally override via
    `LANGCHAIN_PROJECT`).
    """

    merged_tags = _DEFAULT_TAGS + (tags or [])
    merged_metadata: Dict[str, Any] = {"run_name": run_name}
    if metadata:
        merged_metadata.update(metadata)

    project = os.getenv("LANGCHAIN_PROJECT")
    if project:
        merged_metadata.setdefault("project", project)

    return {
        "tags": merged_tags,
        "metadata": merged_metadata,
        "configurable": {"run_name": run_name},
    }


def langsmith_enabled() -> bool:
    """Return True when LangSmith tracing is active."""

    return os.getenv("LANGCHAIN_TRACING_V2", "").strip().lower() in {"true", "1"}
