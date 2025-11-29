<script>
  import StlViewer from "./StlViewer.svelte";

  const apiBase = import.meta.env.VITE_IDEA2SOLID_API?.replace(/\/$/, "") || "http://localhost:8000";

  let prompt = "";
  let loading = false;
  let error = null;
  let result = null;
  let showDetails = false;
  let modelDimensions = null;

  function reset() {
    error = null;
    result = null;
    showDetails = false;
    modelDimensions = null;
  }

  function handleDimensions(event) {
    modelDimensions = event.detail;
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
      <h1>IDEA2SOLID</h1>
      <p class="tagline">PROMPT-DRIVEN OPENSCAD GENERATION</p>
    </header>

    <div class="form-group">
      <label for="prompt">DESCRIBE YOUR OBJECT</label>
      <textarea
        id="prompt"
        bind:value={prompt}
        placeholder="E.G. A MODULAR DESK ORGANIZER WITH PEN SLOTS..."
        rows="6"
      />
    </div>

    <button class="primary-btn" on:click={submitPrompt} disabled={loading}>
      {#if loading}
        <span class="spinner"></span> GENERATING...
      {:else}
        GENERATE 3D MODEL
      {/if}
    </button>

    {#if error}
      <div class="callout error">
        <strong>ERROR:</strong> {error}
      </div>
    {/if}
  </section>

  <section class="panel results-panel">
    {#if loading}
      <div class="loading-state">
        <div class="loader"></div>
        <p>SYNTHESIZING GEOMETRY...</p>
      </div>
    {:else if result}
      <div class="preview-section">
        {#if result.stl_url}
          <div class="viewer-wrapper">
            <StlViewer url={`${apiBase}${result.stl_url}`} on:dimensions={handleDimensions} />
          </div>
          {#if modelDimensions}
            <div class="dimensions-overlay">
              <div class="dim-row"><span>W:</span> {modelDimensions.x.toFixed(1)}mm</div>
              <div class="dim-row"><span>D:</span> {modelDimensions.y.toFixed(1)}mm</div>
              <div class="dim-row"><span>H:</span> {modelDimensions.z.toFixed(1)}mm</div>
            </div>
          {/if}
          <div class="actions">
            <a
              class="download-btn"
              href={`${apiBase}${result.stl_url}`}
              target="_blank"
              rel="noopener"
              download
            >
              DOWNLOAD STL
            </a>
            <button class="secondary-btn" on:click={toggleDetails}>
              {showDetails ? "HIDE DETAILS" : "SHOW CODE & DETAILS"}
            </button>
          </div>
        {:else}
          <div class="no-preview">
            <p>NO STL GENERATED. CHECK ERRORS BELOW.</p>
          </div>
        {/if}
      </div>

      {#if showDetails || !result.stl_url}
        <div class="details-section">
          {#if result.errors && result.errors.length}
            <div class="callout warning">
              <h4>WARNINGS & ERRORS</h4>
              <ul>
                {#each result.errors as item}
                  <li>{item}</li>
                {/each}
              </ul>
            </div>
          {/if}

          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">VALIDATION STATUS</span>
              <span class={`status-badge ${result.validation?.status === 'passed' ? 'success' : 'failure'}`}>
                {result.validation?.status ?? "UNKNOWN"}
              </span>
            </div>
            <div class="detail-item">
              <span class="label">EXPORT STATUS</span>
              <span class={`status-badge ${result.export?.status === 'success' ? 'success' : 'failure'}`}>
                {result.export?.status ?? "UNKNOWN"}
              </span>
            </div>
          </div>

          {#if result.snippets?.length}
            <div class="detail-block">
              <h3>REFERENCED SNIPPETS</h3>
              <ul class="snippet-list">
                {#each result.snippets as snippet}
                  <li>{formatSnippet(snippet)}</li>
                {/each}
              </ul>
            </div>
          {/if}

          <div class="detail-block">
            <h3>OPENSCAD CODE</h3>
            <pre>{result.code || "<NO CODE>"}</pre>
          </div>
        </div>
      {/if}
    {:else}
      <div class="empty-state">
        <div class="placeholder-cube"></div>
        <p>ENTER A PROMPT TO GENERATE YOUR 3D MODEL.</p>
      </div>
    {/if}
  </section>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    background-color: #000000;
    color: #ffffff;
    letter-spacing: 0.02em;
  }

  .layout {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 2rem;
    padding: 2rem;
    box-sizing: border-box;
    max-width: 1800px;
    margin: 0 auto;
  }

  .panel {
    background: #000000;
    border: 1px solid #ffffff;
    padding: 2rem;
    display: flex;
    flex-direction: column;
  }

  .input-panel {
    gap: 2rem;
    height: fit-content;
    position: sticky;
    top: 2rem;
  }

  header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 900;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: -0.05em;
    line-height: 1;
  }

  .tagline {
    margin: 0.5rem 0 0;
    color: #888888;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  label {
    font-weight: 700;
    font-size: 0.8rem;
    color: #ffffff;
    letter-spacing: 0.05em;
  }

  textarea {
    width: 100%;
    background: #000000;
    border: 1px solid #333333;
    padding: 1rem;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    resize: vertical;
    box-sizing: border-box;
    transition: border-color 0.2s;
    text-transform: uppercase;
  }

  textarea:focus {
    outline: none;
    border-color: #ffffff;
  }

  textarea::placeholder {
    color: #444444;
  }

  .primary-btn {
    background: #ffffff;
    color: #000000;
    border: 1px solid #ffffff;
    padding: 1rem;
    font-weight: 800;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .primary-btn:hover:not(:disabled) {
    background: #000000;
    color: #ffffff;
  }

  .primary-btn:disabled {
    background: #333333;
    border-color: #333333;
    color: #666666;
    cursor: not-allowed;
  }

  .results-panel {
    min-height: 600px;
    padding: 0;
    overflow: hidden;
  }

  .empty-state, .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #666666;
    text-align: center;
    padding: 2rem;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    font-size: 0.8rem;
  }

  .placeholder-cube {
    width: 64px;
    height: 64px;
    border: 1px solid #333333;
    margin-bottom: 1rem;
  }

  .loader {
    width: 40px;
    height: 40px;
    border: 2px solid #333333;
    border-top-color: #ffffff;
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
    height: 600px;
    background: #000000;
    border-bottom: 1px solid #ffffff;
  }

  .viewer-wrapper {
    width: 100%;
    height: 100%;
  }

  .dimensions-overlay {
    position: absolute;
    bottom: 1.5rem;
    left: 1.5rem;
    background: #000000;
    border: 1px solid #ffffff;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    z-index: 10;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #ffffff;
    pointer-events: none;
  }

  .dim-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }

  .dim-row span {
    color: #888888;
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
    font-weight: 700;
    font-size: 0.8rem;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 1px solid #ffffff;
  }

  .download-btn {
    background: #ffffff;
    color: #000000;
  }

  .download-btn:hover {
    background: #000000;
    color: #ffffff;
  }

  .secondary-btn {
    background: #000000;
    color: #ffffff;
  }

  .secondary-btn:hover {
    background: #ffffff;
    color: #000000;
  }

  .details-section {
    padding: 2rem;
    background: #000000;
  }

  .detail-grid {
    display: flex;
    gap: 3rem;
    margin-bottom: 3rem;
    border-bottom: 1px solid #333333;
    padding-bottom: 2rem;
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #888888;
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border: 1px solid #333333;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .status-badge.success {
    border-color: #ffffff;
    color: #ffffff;
  }

  .status-badge.failure {
    border-color: #ff0000;
    color: #ff0000;
  }

  .detail-block {
    margin-top: 2rem;
  }

  .detail-block h3 {
    font-size: 1rem;
    color: #ffffff;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
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
    background: #000000;
    padding: 0.75rem;
    border: 1px solid #333333;
    font-size: 0.8rem;
    color: #cccccc;
    font-family: 'JetBrains Mono', monospace;
  }

  pre {
    background: #000000;
    padding: 1.5rem;
    border: 1px solid #333333;
    overflow-x: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.6;
    color: #cccccc;
    margin: 0;
  }

  .callout {
    padding: 1rem;
    border: 1px solid #ffffff;
    margin-top: 1rem;
    font-size: 0.8rem;
    text-transform: uppercase;
  }

  .callout.error {
    border-color: #ff0000;
    color: #ff0000;
  }

  .callout.warning {
    border-color: #ffff00;
    color: #ffff00;
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
