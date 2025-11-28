"""Utility to load OpenSCAD snippet metadata and code into structured records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass
class SnippetRecord:
    """Container for a single OpenSCAD exemplar."""

    identifier: str
    title: str
    summary: str
    parameters: Dict[str, str]
    tags: List[str]
    notes: str
    code: str

    def to_document(self) -> Any:
        """Convert the record into a LangChain Document including metadata."""
        document_cls = _get_document_cls()
        metadata = {
            "id": self.identifier,
            "title": self.title,
            "summary": self.summary,
            "parameters": self.parameters,
            "tags": self.tags,
            "notes": self.notes,
        }
        content_parts = [
            f"Title: {self.title}",
            f"Summary: {self.summary}",
            "Parameters:",
        ]
        for name, description in self.parameters.items():
            content_parts.append(f"- {name}: {description}")
        content_parts.extend([
            "OpenSCAD Code:",
            self.code,
        ])
        return document_cls(page_content="\n".join(content_parts), metadata=metadata)


def load_snippet_corpus(snippet_dir: str | Path) -> List[SnippetRecord]:
    """Load all snippet JSON/SCAD pairs from the target directory."""
    base_path = Path(snippet_dir)
    if not base_path.exists():
        raise FileNotFoundError(f"Snippet directory not found: {base_path}")

    records: List[SnippetRecord] = []
    for metadata_path in sorted(base_path.glob("*.json")):
        with metadata_path.open("r", encoding="utf-8") as handle:
            metadata = json.load(handle)

        identifier = metadata.get("id") or metadata_path.stem
        scad_path = metadata_path.with_suffix(".scad")
        if not scad_path.exists():
            raise FileNotFoundError(
                f"Missing SCAD source for snippet '{identifier}': {scad_path}"
            )

        with scad_path.open("r", encoding="utf-8") as handle:
            code = handle.read()

        record = SnippetRecord(
            identifier=identifier,
            title=metadata.get("title", identifier.replace("_", " ")).strip(),
            summary=metadata.get("summary", ""),
            parameters=metadata.get("parameters", {}),
            tags=list(metadata.get("tags", [])),
            notes=metadata.get("notes", ""),
            code=code,
        )
        records.append(record)

    if not records:
        raise ValueError(f"No snippet records found in directory: {base_path}")

    return records


def build_documents(records: Iterable[SnippetRecord]) -> List[Any]:
    """Create LangChain documents for each record."""
    return [record.to_document() for record in records]


def _get_document_cls():
    """Import Document lazily so optional dependency errors surface clearly."""
    try:
        module = import_module("langchain_core.documents")
        return getattr(module, "Document")
    except ModuleNotFoundError as exc:
        raise ImportError(
            "langchain-core is required to create Document objects. "
            "Install the project dependencies (see requirements.txt)."
        ) from exc
