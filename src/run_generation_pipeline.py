from __future__ import annotations

from dotenv import load_dotenv

from idea2solid import SnippetVectorStore, build_generation_pipeline

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SNIPPET_DIR = BASE_DIR / "data" / "snippets"


def main() -> None:
    load_dotenv()

    vector_store = SnippetVectorStore.from_snippet_dir(SNIPPET_DIR)
    pipeline = build_generation_pipeline(vector_store, top_k=3)

    request = "Design a compact desk hook that adheres under a table and holds a headset."
    result = pipeline.invoke({"question": request})

    print("Generated OpenSCAD code:\n")
    print(result.get("code", "<no code>"))

    print("\nValidation summary:\n")
    validation = result.get("validation", {})
    for key, value in validation.items():
        print(f"{key}: {value}")

    if result.get("errors"):
        print("\nErrors:")
        for err in result["errors"]:
            print(f"- {err}")


if __name__ == "__main__":
    main()
