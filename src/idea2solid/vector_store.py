"""Vector store helper for OpenSCAD snippet retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Iterable, List, Sequence

from .snippet_loader import SnippetRecord, build_documents, load_snippet_corpus


def _lazy_import(path: str, attr: str) -> Any:
    module = import_module(path)
    return getattr(module, attr)


@dataclass
class SnippetVectorStore:
    """Wrap a FAISS-backed vector store for snippet retrieval."""

    store: Any
    records: List[SnippetRecord]

    @classmethod
    def from_snippet_dir(
        cls,
        snippet_dir: str | Path,
        embeddings_model: str = "text-embedding-3-large",
    ) -> "SnippetVectorStore":
        """Load snippets and index them with the configured embedding model."""
        embeddings_cls = _lazy_import("langchain_openai", "OpenAIEmbeddings")
        vector_store_cls = _lazy_import("langchain_community.vectorstores", "FAISS")

        records = load_snippet_corpus(snippet_dir)
        documents = build_documents(records)
        embeddings = embeddings_cls(model=embeddings_model)
        store = vector_store_cls.from_documents(documents=documents, embedding=embeddings)
        return cls(store=store, records=records)

    def similarity_search(
        self,
        query: str,
        *,
        k: int = 5,
    ) -> Sequence[Any]:
        """Return the top-k similar documents for the given query."""
        return self.store.similarity_search(query, k=k)

    def similarity_search_with_score(
        self,
        query: str,
        *,
        k: int = 5,
    ) -> Sequence[Any]:
        """Return the top-k similar documents with similarity scores."""
        return self.store.similarity_search_with_score(query, k=k)
