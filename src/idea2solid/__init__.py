"""Idea2Solid package with RAG utilities for OpenSCAD snippet retrieval."""

from .snippet_loader import load_snippet_corpus
from .vector_store import SnippetVectorStore
from .retrieval_graph import build_retrieval_graph
from .pipeline import build_generation_pipeline, DEFAULT_MODEL
from .tracing import build_run_config, langsmith_enabled

__all__ = [
    "load_snippet_corpus",
    "SnippetVectorStore",
    "build_retrieval_graph",
    "build_generation_pipeline",
    "DEFAULT_MODEL",
    "build_run_config",
    "langsmith_enabled",
]
