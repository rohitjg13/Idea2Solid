"""LangGraph workflow that performs snippet retrieval for Idea2Solid."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Dict, List, Sequence, TypedDict

from .vector_store import SnippetVectorStore


class RetrievalState(TypedDict, total=False):
    """Shared state object for the retrieval workflow."""

    question: str
    snippets: List[Dict[str, Any]]
    context: str


def _format_snippet(doc: Any, score: float) -> Dict[str, Any]:
    metadata = doc.metadata if hasattr(doc, "metadata") else {}
    return {
        "id": metadata.get("id"),
        "title": metadata.get("title"),
        "summary": metadata.get("summary"),
        "parameters": metadata.get("parameters"),
        "tags": metadata.get("tags"),
        "notes": metadata.get("notes"),
        "score": score,
        "code": _extract_code(doc.page_content),
    }


def _extract_code(page_content: str) -> str:
    """Grab the OpenSCAD code section from the stored document string."""
    marker = "OpenSCAD Code:\n"
    if marker in page_content:
        return page_content.split(marker, maxsplit=1)[1]
    return page_content


def build_retrieval_graph(
    vector_store: SnippetVectorStore,
    *,
    top_k: int = 5,
) -> Any:
    """Construct a LangGraph that retrieves snippets for a question."""

    def retrieve_snippets(state: RetrievalState) -> RetrievalState:
        question = state.get("question")
        if not question:
            raise ValueError("Retrieval graph requires 'question' in the state.")

        raw_results: Sequence[Any] = vector_store.similarity_search_with_score(
            question, k=top_k
        )
        formatted = []
        context_blocks = []
        for index, result in enumerate(raw_results, start=1):
            doc, score = result
            snippet_info = _format_snippet(doc, score)
            formatted.append(snippet_info)
            context_blocks.append(
                "\n".join(
                    [
                        f"Snippet {index}: {snippet_info['title']}",
                        f"Score: {score:.4f}",
                        f"Summary: {snippet_info['summary']}",
                        "Code:",
                        snippet_info["code"],
                    ]
                )
            )

        return {
            "snippets": formatted,
            "context": "\n\n".join(context_blocks),
        }

    state_graph_cls, end_token = _get_langgraph_primitives()
    graph = state_graph_cls(RetrievalState)
    graph.add_node("retrieve", retrieve_snippets)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", end_token)
    return graph.compile()


def _get_langgraph_primitives():
    module = import_module("langgraph.graph")
    return getattr(module, "StateGraph"), getattr(module, "END")
