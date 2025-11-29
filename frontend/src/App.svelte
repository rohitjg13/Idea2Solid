<script>
  const apiBase = import.meta.env.VITE_IDEA2SOLID_API?.replace(/\/$/, "") || "http://localhost:8000";

  let prompt = "";
  let loading = false;
  let error = null;
  let result = null;

  function reset() {
    error = null;
    result = null;
  }

  async function submitPrompt() {
    reset();
    const trimmed = prompt.trim();
    if (!trimmed) {
      error = "Prompt cannot be empty.";
      return;
    }

    loading = true;
    try {
      const response = await fetch(`${apiBase}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json"
        },
        body: JSON.stringify({ prompt: trimmed })
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || `Request failed with status ${response.status}`);
      }

      result = await response.json();
    } catch (err) {
      error = err?.message ?? "Unexpected error";
    } finally {
      loading = false;
    }
  }

  function formatSnippet(snippet) {
    const title = snippet?.title || "Untitled";
    const score = typeof snippet?.score === "number" ? snippet.score.toFixed(3) : "?";
    return `${title} (score ${score})`;
  }
</script>

<main class="layout">
  <section class="panel">
    <h1>Idea2Solid</h1>
    <p class="tagline">Prompt-driven OpenSCAD generation with validation and STL export.</p>

    <label for="prompt">Design prompt</label>
    <textarea
      id="prompt"
      bind:value={prompt}
      placeholder="e.g. A modular desk organizer with pen slots and sticky note tray"
      rows="5"
    />

    <button class="primary" on:click={submitPrompt} disabled={loading}>
      {#if loading}
        Generating…
      {:else}
        Generate Model
      {/if}
    </button>

    {#if error}
      <div class="callout error">{error}</div>
    {/if}
  </section>

  <section class="panel results">
    <h2>Results</h2>
    {#if loading}
      <p>Running retrieval, synthesis, and validation…</p>
    {:else if result}
      <div class="result-block">
        <h3>Validation</h3>
        <ul>
          <li>Status: {result.validation?.status ?? "unknown"}</li>
          <li>Export: {result.export?.status ?? "unknown"}</li>
        </ul>
      </div>

      {#if result.errors && result.errors.length}
        <div class="callout warning">
          <h4>Warnings</h4>
          <ul>
            {#each result.errors as item}
              <li>{item}</li>
            {/each}
          </ul>
        </div>
      {/if}

      {#if result.snippets?.length}
        <div class="result-block">
          <h3>Referenced Snippets</h3>
          <ul>
            {#each result.snippets as snippet}
              <li>{formatSnippet(snippet)}</li>
            {/each}
          </ul>
        </div>
      {/if}

      <div class="result-block">
        <h3>OpenSCAD Code</h3>
        <pre>{result.code || "<no code>"}</pre>
      </div>

      {#if result.stl_url}
        <div class="result-block">
          <h3>Outputs</h3>
          <a
            class="download"
            href={`${apiBase}${result.stl_url}`}
            target="_blank"
            rel="noopener"
            download
          >
            Download STL
          </a>
        </div>
      {/if}
    {:else}
      <p>Provide a prompt to generate OpenSCAD code and an STL file.</p>
    {/if}
  </section>
</main>

<style>
  .layout {
    min-height: 100vh;
    display: grid;
    grid-template-columns: minmax(320px, 420px) 1fr;
    gap: 2rem;
    padding: 2rem 3rem;
    box-sizing: border-box;
  }

  .panel {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 12px 40px rgba(15, 23, 42, 0.35);
  }

  h1 {
    margin: 0 0 0.75rem;
    font-size: 2.2rem;
    letter-spacing: 0.02em;
  }

  h2 {
    margin-top: 0;
  }

  h3 {
    margin-bottom: 0.5rem;
  }

  .tagline {
    margin: 0 0 1.5rem;
    color: rgba(148, 163, 184, 0.9);
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }

  textarea {
    width: 100%;
    resize: vertical;
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    padding: 0.75rem 0.9rem;
    font-size: 1rem;
    font-family: inherit;
    background: rgba(15, 23, 42, 0.65);
    color: inherit;
    min-height: 120px;
  }

  textarea:focus {
    outline: 2px solid #38bdf8;
    outline-offset: 2px;
  }

  .primary {
    margin-top: 1rem;
    background: linear-gradient(120deg, #38bdf8, #6366f1);
    color: #0f172a;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    transition: transform 120ms ease, box-shadow 150ms ease;
  }

  .primary:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 12px 24px rgba(99, 102, 241, 0.35);
  }

  .primary:disabled {
    opacity: 0.6;
    cursor: progress;
  }

  .results {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .result-block {
    background: rgba(15, 23, 42, 0.65);
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    padding: 1rem 1.25rem;
  }

  pre {
    margin: 0;
    white-space: pre-wrap;
    font-family: "JetBrains Mono", "Fira Code", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    background: rgba(15, 23, 42, 0.85);
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    max-height: 360px;
    overflow: auto;
  }

  .callout {
    border-radius: 12px;
    padding: 1rem 1.25rem;
    border: 1px solid;
  }

  .callout.error {
    border-color: rgba(248, 113, 113, 0.6);
    background: rgba(185, 28, 28, 0.2);
  }

  .callout.warning {
    border-color: rgba(250, 204, 21, 0.6);
    background: rgba(202, 138, 4, 0.25);
  }

  .callout h4 {
    margin: 0 0 0.5rem;
  }

  .download {
    display: inline-block;
    padding: 0.6rem 1rem;
    background: rgba(56, 189, 248, 0.15);
    border-radius: 10px;
  }

  @media (max-width: 960px) {
    .layout {
      grid-template-columns: 1fr;
      padding: 1.5rem;
    }

    .results {
      order: -1;
    }
  }
</style>
