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

# Conclusion

I had planned to create a modern, prompt-driven 3D modeling tool that generates OpenSCAD code and STL files. I think I have achieved the conclusion satisfactorily.

The reason for my satisfaction is that we have successfully built a complete end-to-end pipeline. On the backend, I integrated a specialized OpenSCAD cheat sheet into the LangGraph pipeline to ensure high-quality code generation. On the frontend, I implemented a UI using Svelte and Three.js, featuring real-time 3D rendering, automatic dimension calculation, and a responsive layout.

# Video Summary Link: https://www.youtube.com/watch?v=rm5AlsJbGOs

# Demo
![demo-1](https://github.com/user-attachments/assets/aa010e32-0a1d-4094-bbe0-bd943d703467)

![demo-2](https://github.com/user-attachments/assets/f8a5ea81-5d4f-4a69-8ef4-17aa9237b328)
