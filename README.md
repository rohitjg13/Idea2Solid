# Idea2Solid: Prompt-Driven OpenSCAD Generation

## Overview

Idea2Solid turns natural language design requests into manufacturable 3D models. The system combines Retrieval Augmented Generation (RAG) with OpenSCAD exemplars, letting a user describe an object (for example, "a beveled phone stand with cable channel") and receiving validated OpenSCAD plus an STL export. The workflow collects relevant code snippets, prompts an OpenAI chat model (default `gpt-4o-mini`, override via `IDEA2SOLID_MODEL` if you have GPT-5-Codex (Preview) access) to synthesize a script, validates the result, and runs OpenSCAD headlessly to emit geometry.

## Reason for picking up this project

The project showcases every major concept from MAT496. It relies on prompt engineering and structured outputs, performs semantic search over an OpenSCAD corpus, uses RAG to ground model generations, and calls external tools (OpenSCAD CLI) from a LangGraph-managed pipeline. LangSmith will support evaluation and debugging of the graph. This integration of course topics into a tangible CAD assistant aligns tightly with the capstone objectives.

As a 3D printing enthusiast, I have personally experienced the friction between having an idea and creating a printable model. While 3D printers are increasingly accessible, professional CAD software remains a significant barrier to entry due to its steep learning curve. Idea2Solid bridges this gap by democratizing the design process, allowing makers to bypass complex manual modeling and go directly from a mental concept to a physical object using natural language.

## Plan

I plan to execute these steps to complete my project.

- [X] Curate 10-15 high-quality OpenSCAD exemplars with metadata, descriptions, and parameter notes stored in `data/snippets`.
- [X] Embed the exemplars, stand up a vector store (FAISS or Chroma), and expose retrieval nodes inside a LangGraph workflow.
- [X] Design the LangGraph pipeline: user prompt ingestion, retrieval, GPT synthesis with guardrails, code linting via `openscad --check`, and error handling.
- [X] Automate STL generation by invoking OpenSCAD headlessly and returning file handles through the graph.
- [X] Instrument the graph with LangSmith traces and add regression prompts to validate geometry consistency.
- [X] Package the solution with a frontend (FastAPI + Svelte) for interactive use.
- [X] Added a STL Viewer to the frontend

## AI Concepts Implemented

This project demonstrates the practical application of several key AI engineering concepts:

### Prompting

The system uses sophisticated prompt engineering in `pipeline.py`. We define a strict system persona ("OpenSCAD expert") and inject a dynamic "Cheat Sheet" into the context. This grounds the LLM in valid syntax and specific CSG (Constructive Solid Geometry) operations, reducing hallucinations and ensuring the generated code compiles correctly.

### Structured Output

The application relies on structured data handling throughout the pipeline.

- **Input**: User requests are processed into a structured `GenerationState`.
- **Retrieval**: Code snippets are stored and retrieved as structured JSON objects containing metadata, parameters, and code.
- **Response**: The API returns a strict JSON schema to the frontend, separating the raw OpenSCAD code, validation status, and file paths, allowing the UI to render specific components (like the 3D viewer or error logs) reliably.

### Semantic Search

Instead of simple keyword matching, the project uses a vector store to perform semantic search over a curated library of OpenSCAD snippets. If a user asks for a "holder", the system can retrieve examples of "boxes" or "containers" based on vector similarity, providing relevant context even if the exact words don't match.

### Retrieval Augmented Generation (RAG)

The core engine is a RAG pipeline.

1. **Retrieve**: The system searches the vector store for code snippets relevant to the user's prompt.
2. **Augment**: These snippets, along with the cheat sheet, are injected into the LLM's context window.
3. **Generate**: The LLM synthesizes new code by learning from the retrieved examples, resulting in higher quality and more syntactically correct OpenSCAD scripts.

### Tool Integration (OpenSCAD CLI)

The agent extends the LLM's capabilities by integrating with an external tool—the OpenSCAD CLI. The LLM generates the *code*, but the system calls the OpenSCAD binary to *compile* that code into a 3D mesh (STL). This allows the agent to perform a task (creating a physical file) that a text-only model cannot do on its own.

### LangGraph: State, Nodes, Graph

The backend orchestration is built entirely on **LangGraph**:

- **State**: A shared `GenerationState` dictionary tracks the request, code, validation results, and file paths across the lifecycle.
- **Nodes**: Distinct functions (`_retrieve`, `_synthesize`, `_validate`, `_export`) perform specific tasks.
- **Graph**: A directed graph defines the workflow topology, ensuring that validation only happens after synthesis, and export only happens after successful validation.

## Conclusion

I had planned to create a modern, prompt-driven 3D modeling tool that generates OpenSCAD code and STL files. I think I have achieved the conclusion satisfactorily.

The reason for my satisfaction is that we have successfully built a complete end-to-end pipeline. On the backend, I integrated a specialized OpenSCAD cheat sheet into the LangGraph pipeline to ensure high-quality code generation. On the frontend, I implemented a UI using Svelte and Three.js, featuring real-time 3D rendering, automatic dimension calculation, and a responsive layout.

## Video Summary Link

https://www.youtube.com/watch?v=rm5AlsJbGOs

## Demo

![demo-1](https://github.com/user-attachments/assets/aa010e32-0a1d-4094-bbe0-bd943d703467)

![demo-2](https://github.com/user-attachments/assets/f8a5ea81-5d4f-4a69-8ef4-17aa9237b328)
