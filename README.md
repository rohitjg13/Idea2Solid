# Idea2Solid: Prompt-Driven OpenSCAD Generation

## Overview

Idea2Solid turns natural language design requests into manufacturable 3D models. The system combines Retrieval Augmented Generation (RAG) with OpenSCAD exemplars, letting a user describe an object (for example, "a beveled phone stand with cable channel") and receiving validated OpenSCAD plus an STL export. The workflow collects relevant code snippets, prompts an OpenAI chat model (default `gpt-4o-mini`, override via `IDEA2SOLID_MODEL` if you have GPT-5-Codex (Preview) access) to synthesize a script, validates the result, and runs OpenSCAD headlessly to emit geometry.

## Reason for picking up this project

The project showcases every major concept from MAT496. It relies on prompt engineering and structured outputs, performs semantic search over an OpenSCAD corpus, uses RAG to ground model generations, and calls external tools (OpenSCAD CLI) from a LangGraph-managed pipeline. LangSmith will support evaluation and debugging of the graph. This integration of course topics into a tangible CAD assistant aligns tightly with the capstone objectives.

## Plan

I plan to execute these steps to complete my project.

- [X] Curate 10-15 high-quality OpenSCAD exemplars with metadata, descriptions, and parameter notes stored in `data/snippets`.
- [X] Embed the exemplars, stand up a vector store (FAISS or Chroma), and expose retrieval nodes inside a LangGraph workflow.
- [X] Design the LangGraph pipeline: user prompt ingestion, retrieval, GPT synthesis with guardrails, code linting via `openscad --check`, and error handling.
- [X] Automate STL generation by invoking OpenSCAD headlessly and returning file handles through the graph.
- [X] Instrument the graph with LangSmith traces and add regression prompts to validate geometry consistency.
- [X] Package the solution with a frontend (FastAPI + Svelte) for interactive use.
- [X] Added a STL Viewer to the frontend
