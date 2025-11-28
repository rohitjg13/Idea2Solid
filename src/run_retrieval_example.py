"""Example script demonstrating snippet retrieval workflow."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from idea2solid import build_retrieval_graph, load_snippet_corpus, SnippetVectorStore

BASE_DIR = Path(__file__).resolve().parent.parent
SNIPPET_DIR = BASE_DIR / "data" / "snippets"


def main() -> None:
    load_dotenv()

    vector_store = SnippetVectorStore.from_snippet_dir(SNIPPET_DIR)
    graph = build_retrieval_graph(vector_store, top_k=3)

    question = (
        "Design a compact organizer that can hold multiple USB cables upright "
        "and keeps them accessible on a desk."
    )
    result = graph.invoke({"question": question})

    retrieved = result.get("snippets", [])
    print("Retrieved Snippets:\n")
    for snippet in retrieved:
        print(f"- {snippet['title']} (score={snippet['score']:.4f})")
    print("\nContext Block:\n")
    print(result.get("context", "<none>"))


if __name__ == "__main__":
    main()
