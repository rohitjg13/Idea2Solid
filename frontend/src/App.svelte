<script>
  import StlViewer from "./StlViewer.svelte";

  const apiBase = import.meta.env.VITE_IDEA2SOLID_API?.replace(/\/$/, "") || "http://localhost:8000";

  let prompt = "";
  let loading = false;
  let error = null;
  let result = null;
  let showDetails = false;

  function reset() {
    error = null;
    result = null;
    showDetails = false;
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

  function toggleDetails() {
    showDetails = !showDetails;
  }
</script>

<main class="layout">
  <section class="panel input-panel">
    <header>
      <h1>Idea2Solid</h1>
      <p class="tagline">Prompt-driven OpenSCAD generation.</p>
    </header>

    <div class="form-group">
      <label for="prompt">Describe your object</label>
      <textarea
        id="prompt"
        bind:value={prompt}
        placeholder="e.g. A modular desk organizer with pen slots and sticky note tray"
        rows="6"
      />
    </div>

    <button class="primary-btn" on:click={submitPrompt} disabled={loading}>
      {#if loading}
        <span class="spinner"></span> Generating Model...
      {:else}
        Generate 3D Model
      {/if}
    </button>

    {#if error}
      <div class="callout error">
        <strong>Error:</strong> {error}
      </div>
    {/if}
  </section>

  <section class="panel results-panel">
    {#if loading}
      <div class="loading-state">
        <div class="loader"></div>
        <p>Synthesizing geometry, validating code, and exporting STL...</p>
      </div>
    {:else if result}
      <div class="preview-section">
        {#if result.stl_url}
          <div class="viewer-wrapper">
            <StlViewer url={`${apiBase}${result.stl_url}`} />
          </div>
          <div class="actions">
            <a
              class="download-btn"
              href={`${apiBase}${result.stl_url}`}
              target="_blank"
              rel="noopener"
              download
            >
              Download STL
            </a>
            <button class="secondary-btn" on:click={toggleDetails}>
              {showDetails ? "Hide Details" : "Show Code & Details"}
            </button>
          </div>
        {:else}
          <div class="no-preview">
            <p>No STL generated. Check errors below.</p>
          </div>
        {/if}
      </div>

      {#if showDetails || !result.stl_url}
        <div class="details-section">
          {#if result.errors && result.errors.length}
            <div class="callout warning">
              <h4>Warnings & Errors</h4>
              <ul>
                {#each result.errors as item}
                  <li>{item}</li>
                {/each}
              </ul>
            </div>
          {/if}

          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">Validation Status</span>
              <span class={`status-badge ${result.validation?.status === 'passed' ? 'success' : 'failure'}`}>
                {result.validation?.status ?? "unknown"}
              </span>
            </div>
            <div class="detail-item">
              <span class="label">Export Status</span>
              <span class={`status-badge ${result.export?.status === 'success' ? 'success' : 'failure'}`}>
                {result.export?.status ?? "unknown"}
              </span>
            </div>
          </div>

          {#if result.snippets?.length}
            <div class="detail-block">
              <h3>Referenced Snippets</h3>
              <ul class="snippet-list">
                {#each result.snippets as snippet}
                  <li>{formatSnippet(snippet)}</li>
                {/each}
              </ul>
            </div>
          {/if}

          <div class="detail-block">
            <h3>OpenSCAD Code</h3>
            <pre>{result.code || "<no code>"}</pre>
          </div>
        </div>
      {/if}
    {:else}
      <div class="empty-state">
        <div class="placeholder-cube"></div>
        <p>Enter a prompt to generate your 3D model.</p>
      </div>
    {/if}
  </section>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background-color: #0f172a;
    color: #f8fafc;
  }

  .layout {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 2rem;
    padding: 2rem;
    box-sizing: border-box;
    max-width: 1600px;
    margin: 0 auto;
  }

  .panel {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }

  .input-panel {
    gap: 1.5rem;
    height: fit-content;
    position: sticky;
    top: 2rem;
  }

  header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(to right, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .tagline {
    margin: 0.5rem 0 0;
    color: #94a3b8;
    font-size: 0.95rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  label {
    font-weight: 600;
    font-size: 0.9rem;
    color: #cbd5e1;
  }

  textarea {
    width: 100%;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 1rem;
    color: #f8fafc;
    font-family: inherit;
    font-size: 1rem;
    resize: vertical;
    box-sizing: border-box;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  textarea:focus {
    outline: none;
    border-color: #38bdf8;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
  }

  .primary-btn {
    background: #38bdf8;
    color: #0f172a;
    border: none;
    padding: 1rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.5rem;
  }

  .primary-btn:hover:not(:disabled) {
    background: #0ea5e9;
    transform: translateY(-1px);
  }

  .primary-btn:disabled {
    background: #475569;
    color: #94a3b8;
    cursor: not-allowed;
  }

  .results-panel {
    min-height: 600px;
    padding: 0;
    overflow: hidden;
    background: #0f172a; /* Darker background for the viewer area */
    border: 1px solid #334155;
  }

  .empty-state, .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #64748b;
    text-align: center;
    padding: 2rem;
  }

  .placeholder-cube {
    width: 64px;
    height: 64px;
    border: 2px dashed #334155;
    margin-bottom: 1rem;
    border-radius: 8px;
  }

  .loader {
    width: 40px;
    height: 40px;
    border: 3px solid #334155;
    border-top-color: #38bdf8;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .preview-section {
    position: relative;
    width: 100%;
    height: 600px; /* Fixed height for viewer */
    background: #000;
  }

  .viewer-wrapper {
    width: 100%;
    height: 100%;
  }

  .actions {
    position: absolute;
    bottom: 1.5rem;
    right: 1.5rem;
    display: flex;
    gap: 1rem;
    z-index: 10;
  }

  .download-btn, .secondary-btn {
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;
    backdrop-filter: blur(4px);
  }

  .download-btn {
    background: rgba(56, 189, 248, 0.9);
    color: #0f172a;
    border: none;
  }

  .download-btn:hover {
    background: #38bdf8;
  }

  .secondary-btn {
    background: rgba(30, 41, 59, 0.8);
    color: #f8fafc;
    border: 1px solid #475569;
  }

  .secondary-btn:hover {
    background: rgba(30, 41, 59, 1);
    border-color: #64748b;
  }

  .details-section {
    padding: 2rem;
    background: #1e293b;
    border-top: 1px solid #334155;
  }

  .detail-grid {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94a3b8;
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .status-badge.success {
    background: rgba(34, 197, 94, 0.2);
    color: #4ade80;
  }

  .status-badge.failure {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
  }

  .detail-block {
    margin-top: 2rem;
  }

  .detail-block h3 {
    font-size: 1.1rem;
    color: #e2e8f0;
    margin-bottom: 1rem;
  }

  .snippet-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .snippet-list li {
    background: #0f172a;
    padding: 0.75rem;
    border-radius: 6px;
    border: 1px solid #334155;
    font-size: 0.9rem;
    color: #cbd5e1;
  }

  pre {
    background: #0f172a;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #334155;
    overflow-x: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    line-height: 1.5;
    color: #e2e8f0;
    margin: 0;
  }

  .callout {
    padding: 1rem;
    border-radius: 8px;
    margin-top: 1rem;
    font-size: 0.9rem;
  }

  .callout.error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: #fca5a5;
  }

  .callout.warning {
    background: rgba(234, 179, 8, 0.1);
    border: 1px solid rgba(234, 179, 8, 0.2);
    color: #fde047;
    margin-bottom: 2rem;
  }

  .callout ul {
    margin: 0.5rem 0 0 1.2rem;
    padding: 0;
  }

  @media (max-width: 1024px) {
    .layout {
      grid-template-columns: 1fr;
      padding: 1rem;
    }

    .input-panel {
      position: static;
    }

    .preview-section {
      height: 400px;
    }
  }
</style>
