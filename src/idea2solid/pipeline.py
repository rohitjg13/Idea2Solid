from __future__ import annotations

import re
import subprocess
import tempfile
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, TypedDict

from .vector_store import SnippetVectorStore


class GenerationState(TypedDict, total=False):
    """State container shared across pipeline nodes."""

    question: str
    snippets: List[Dict[str, Any]]
    context: str
    prompt: str
    code: str
    validation: Dict[str, Any]
    errors: List[str]


def _lazy_import(module_path: str, attr: str) -> Any:
    module = import_module(module_path)
    return getattr(module, attr)


def _ingest(state: GenerationState) -> GenerationState:
    question = state.get("question")
    if not question or not question.strip():
        raise ValueError("Pipeline requires a non-empty 'question' in the state.")
    return {"question": question.strip()}


def _retrieve(
    state: GenerationState,
    vector_store: SnippetVectorStore,
    *,
    top_k: int,
) -> GenerationState:
    question = state.get("question")
    raw_results: Sequence[Any] = vector_store.similarity_search_with_score(
        question, k=top_k
    )
    snippets: List[Dict[str, Any]] = []
    context_blocks: List[str] = []
    for index, result in enumerate(raw_results, start=1):
        doc, score = result
        metadata = getattr(doc, "metadata", {}) or {}
        code = _extract_code(doc.page_content)
        snippet = {
            "id": metadata.get("id"),
            "title": metadata.get("title"),
            "summary": metadata.get("summary"),
            "parameters": metadata.get("parameters"),
            "tags": metadata.get("tags"),
            "notes": metadata.get("notes"),
            "score": score,
            "code": code,
        }
        snippets.append(snippet)
        context_blocks.append(
            "\n".join(
                [
                    f"Snippet {index}: {snippet['title']}",
                    f"Score: {score:.4f}",
                    f"Summary: {snippet['summary']}",
                    "Parameters:",
                    "\n".join(
                        f"- {name}: {desc}"
                        for name, desc in (snippet.get("parameters") or {}).items()
                    ),
                    "Code:",
                    code,
                ]
            )
        )

    return {
        "snippets": snippets,
        "context": "\n\n".join(context_blocks),
    }


def _build_prompt(question: str, context: str) -> str:
    return (
        "You are an OpenSCAD expert helping convert natural language requests into "
        "valid OpenSCAD code. Follow these rules:\n"
        "- Use only OpenSCAD syntax supported by the latest stable release.\n"
        "- Define a `module main()` entry point that renders the design.\n"
        "- Keep tunable parameters at the top with sensible defaults.\n"
        "- Avoid importing external libraries.\n"
        "- Return only OpenSCAD code.\n"
        "\n"
        f"User request:\n{question}\n\n"
        f"Reference snippets:\n{context}\n\n"
        "OpenSCAD code:"
    )


def _apply_guardrails(code: str) -> List[str]:
    errors: List[str] = []
    if not re.search(r"module\s+main\s*\(", code):
        errors.append("Generated code must include `module main()`.")
    if "import(" in code:
        errors.append("External `import()` statements are not allowed.")
    return errors


def _synthesize(
    state: GenerationState,
    *,
    model: str,
    temperature: float,
) -> GenerationState:
    context = state.get("context", "")
    question = state.get("question", "")
    prompt = _build_prompt(question, context)

    chat_cls = _lazy_import("langchain_openai", "ChatOpenAI")
    messages_module = import_module("langchain_core.messages")
    system_message = getattr(messages_module, "SystemMessage")
    human_message = getattr(messages_module, "HumanMessage")

    llm = chat_cls(model=model, temperature=temperature)
    response = llm.invoke(
        [
            system_message(content="You generate OpenSCAD code only."),
            human_message(content=prompt),
        ]
    )
    code = getattr(response, "content", "")
    errors = _apply_guardrails(code)
    return {"prompt": prompt, "code": code, "errors": errors}


def _validate(
    state: GenerationState,
    *,
    openscad_path: str,
) -> GenerationState:
    code = state.get("code", "")
    errors = list(state.get("errors", []))
    if not code.strip():
        errors.append("Model returned empty OpenSCAD code.")
        return {"errors": errors}

    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False) as handle:
        handle.write(code)
        handle_path = Path(handle.name)

    try:
        result = subprocess.run(
            [openscad_path, "--check", str(handle_path)],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        errors.append("OpenSCAD CLI not found. Install it or set OPENCAD_PATH.")
        validation = {"status": "missing", "stderr": ""}
    else:
        validation = {
            "status": "passed" if result.returncode == 0 else "failed",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
        if result.returncode != 0:
            errors.append("OpenSCAD validation failed; check stderr for details.")
    finally:
        handle_path.unlink(missing_ok=True)

    return {"validation": validation, "errors": errors}


def build_generation_pipeline(
    vector_store: SnippetVectorStore,
    *,
    top_k: int = 5,
    model: str = "gpt-5-codex-preview",
    temperature: float = 0.2,
    openscad_path: str = "openscad",
) -> Any:
    """Create a LangGraph pipeline: ingest -> retrieve -> synthesize -> validate."""

    state_graph_cls, end_token = _get_langgraph_primitives()

    graph = state_graph_cls(GenerationState)
    graph.add_node("ingest", lambda state: _ingest(state))
    graph.add_node(
        "retrieve",
        lambda state: _retrieve(state, vector_store=vector_store, top_k=top_k),
    )
    graph.add_node(
        "synthesize",
        lambda state: _synthesize(state, model=model, temperature=temperature),
    )
    graph.add_node(
        "validate",
        lambda state: _validate(state, openscad_path=openscad_path),
    )

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "retrieve")
    graph.add_edge("retrieve", "synthesize")
    graph.add_edge("synthesize", "validate")
    graph.add_edge("validate", end_token)

    compiled = graph.compile()
    compiled.config = {  # type: ignore[attr-defined]
        "top_k": top_k,
        "model": model,
        "temperature": temperature,
        "openscad_path": openscad_path,
    }
    return compiled


def _extract_code(page_content: str) -> str:
    marker = "OpenSCAD Code:\n"
    if marker in page_content:
        return page_content.split(marker, maxsplit=1)[1]
    return page_content


def _get_langgraph_primitives():
    module = import_module("langgraph.graph")
    return getattr(module, "StateGraph"), getattr(module, "END")
