from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from idea2solid import (
    SnippetVectorStore,
    build_generation_pipeline,
    build_run_config,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SNIPPET_DIR = BASE_DIR / "data" / "snippets"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_vector_store = SnippetVectorStore.from_snippet_dir(SNIPPET_DIR)
_pipeline = build_generation_pipeline(
    _vector_store,
    top_k=4,
    output_dir=OUTPUT_DIR,
)


def _coerce_jsonable(value: Any) -> Any:
    """Best-effort conversion to standard JSON-serializable types."""

    if isinstance(value, dict):
        return {key: _coerce_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_coerce_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_coerce_jsonable(item) for item in value]
    # Handle numpy scalars without importing numpy explicitly
    item_attr = getattr(value, "item", None)
    if callable(item_attr):
        try:
            return item_attr()
        except Exception:  # pragma: no cover - defensive fallback
            pass
    if isinstance(value, (set, frozenset)):
        return [_coerce_jsonable(item) for item in value]
    return value


def _allowed_origins() -> List[str]:
    raw = os.getenv("IDEA2SOLID_CORS_ORIGINS", "http://localhost:5173")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    if "*" in origins:
        return ["*"]
    return origins or ["http://localhost:5173"]


app = FastAPI(title="Idea2Solid API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    code: str
    validation: Dict[str, Any]
    export: Dict[str, Any]
    stl_path: Optional[str] = None
    stl_url: Optional[str] = None
    errors: List[str]
    snippets: Optional[List[Dict[str, Any]]] = None


@app.get("/")
def index() -> Dict[str, str]:
    return {"status": "ok", "message": "Idea2Solid API is running."}


@app.post("/api/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    run_config = build_run_config(
        run_name="api-generate",
        tags=["api"],
        metadata={"prompt": prompt},
    )

    try:
        result = _pipeline.invoke({"question": prompt}, config=run_config)
    except Exception as exc:  # pragma: no cover - defensive until dedicated tests arrive
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {exc}") from exc

    code = result.get("code", "")
    validation = result.get("validation", {}) or {}
    export = result.get("export", {}) or {}
    errors = list(result.get("errors", []))
    snippets = result.get("snippets")

    stl_path = result.get("stl_path")
    stl_url: Optional[str] = None
    if stl_path:
        stl_filename = Path(stl_path).name
        candidate = OUTPUT_DIR / stl_filename
        if candidate.exists():
            stl_url = f"/outputs/{stl_filename}"
        else:
            errors.append("STL file missing on disk after export.")

    sanitized_snippets = None
    if snippets:
        sanitized_snippets = [
            {key: _coerce_jsonable(val) for key, val in (snippet or {}).items()}
            for snippet in snippets
        ]

    return GenerateResponse(
        code=code,
        validation=_coerce_jsonable(validation),
        export=_coerce_jsonable(export),
        errors=[_coerce_jsonable(err) for err in errors],
        stl_path=stl_path,
        stl_url=stl_url,
        snippets=sanitized_snippets,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
