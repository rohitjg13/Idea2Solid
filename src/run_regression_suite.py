"""Run a set of regression prompts to verify Idea2Solid pipeline stability."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv

from idea2solid import SnippetVectorStore, build_generation_pipeline, build_run_config

BASE_DIR = Path(__file__).resolve().parent.parent
SNIPPET_DIR = BASE_DIR / "data" / "snippets"
OUTPUT_DIR = BASE_DIR / "outputs"

REGRESSION_PROMPTS: List[Tuple[str, str]] = [
    (
        "usb_dock",
        "Design a desktop USB cable dock that keeps five cables upright and easy to grab.",
    ),
    (
        "planter",
        "Create a small tapered planter with a drainage hole and sturdy rim for succulents.",
    ),
    (
        "gear_blank",
        "Generate a 24 tooth spur gear blank ready for machining with weight reduction holes.",
    ),
]


def main() -> None:
    load_dotenv()

    vector_store = SnippetVectorStore.from_snippet_dir(SNIPPET_DIR)
    pipeline = build_generation_pipeline(
        vector_store,
        top_k=4,
        output_dir=OUTPUT_DIR,
    )

    failures = []

    for slug, prompt in REGRESSION_PROMPTS:
        config = build_run_config(
            run_name=f"regression-{slug}",
            tags=["regression"],
            metadata={"prompt": prompt},
        )
        result = pipeline.invoke({"question": prompt}, config=config)

        validation = result.get("validation", {})
        export = result.get("export", {})
        errors = result.get("errors", [])

        success = (
            validation.get("status") == "passed"
            and export.get("status") == "success"
            and not errors
        )

        if success:
            print(f"[PASS] {slug}: validation and export succeeded -> {result.get('stl_path', '<missing>')}")
        else:
            print(f"[FAIL] {slug}: pipeline reported issues")
            print(f"  Validation status: {validation.get('status')} | Export status: {export.get('status')}")
            if errors:
                for err in errors:
                    print(f"    - {err}")
            failures.append(slug)

    if failures:
        print("\nRegression suite failed for prompts:", ", ".join(failures))
        sys.exit(1)

    print("\nAll regression prompts passed without errors.")


if __name__ == "__main__":
    main()
