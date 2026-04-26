const inputText = document.querySelector("#inputText");
const runBtn = document.querySelector("#runBtn");
const sampleBtn = document.querySelector("#sampleBtn");
const exportBtn = document.querySelector("#exportBtn");
const minLength = document.querySelector("#minLength");
const minLengthValue = document.querySelector("#minLengthValue");
const docCount = document.querySelector("#docCount");
const serviceStatus = document.querySelector("#serviceStatus");
const serviceVersion = document.querySelector("#serviceVersion");
const statusDot = document.querySelector(".status-dot");

const metrics = {
  tokens: document.querySelector("#metricTokens"),
  unique: document.querySelector("#metricUnique"),
  diversity: document.querySelector("#metricDiversity"),
  noise: document.querySelector("#metricNoise"),
};

const documentsEl = document.querySelector("#documents");
const termsEl = document.querySelector("#terms");
const annotationsEl = document.querySelector("#annotations");
const riskPanelEl = document.querySelector("#riskPanel");
const modelLabEl = document.querySelector("#modelLab");
const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:8000" : "";
let latestPayload = null;

const samples = [
  "Delivery was late and support never replied.\nI loved the clean checkout flow.\nThe app crashed twice after payment.\nPackaging was excellent but tracking was confusing.",
  "The refund took 12 days and nobody explained why.\nYour mobile app is fast and the new search is great.\nI am not happy with the broken promo code.\nThe agent was helpful, but the wait time was terrible.",
  "My order arrived damaged!!! Call me at 9876543210.\nThe product quality is amazing for the price.\nTracking emails went to support@example.com and never reached me.\nCheckout was smooth but returns were slow.",
];

function documentsFromInput() {
  return inputText.value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function getOptions() {
  const options = {};
  document.querySelectorAll("[data-option]").forEach((input) => {
    options[input.dataset.option] = input.checked;
  });
  options.min_token_length = Number(minLength.value);
  return options;
}

function updateDocumentCount() {
  const count = documentsFromInput().length;
  docCount.textContent = `${count} ${count === 1 ? "doc" : "docs"}`;
}

function setLoading(isLoading) {
  runBtn.disabled = isLoading;
  runBtn.textContent = isLoading ? "Analyzing..." : "Analyze";
}

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    const payload = await response.json();
    serviceStatus.textContent = "API online";
    serviceVersion.textContent = `${payload.service} ${payload.version}`;
    statusDot.classList.add("ok");
  } catch {
    serviceStatus.textContent = "API unavailable";
    serviceVersion.textContent = "Start FastAPI server";
  }
}

async function runPipeline() {
  const documents = documentsFromInput();
  updateDocumentCount();
  if (!documents.length) {
    documentsEl.innerHTML = '<div class="doc"><p>Add at least one document to process.</p></div>';
    return;
  }

  setLoading(true);
  try {
    const response = await fetch(`${API_BASE}/api/v1/pipeline`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ documents, options: getOptions() }),
    });

    if (!response.ok) {
      throw new Error(`Pipeline failed with ${response.status}`);
    }

    const payload = await response.json();
    latestPayload = payload;
    renderPipeline(payload);
  } catch (error) {
    documentsEl.innerHTML = `<div class="doc"><p>${error.message}</p></div>`;
  } finally {
    setLoading(false);
  }
}

function renderPipeline(payload) {
  const analytics = payload.corpus_analytics;
  metrics.tokens.textContent = analytics.tokens;
  metrics.unique.textContent = analytics.unique_tokens;
  metrics.diversity.textContent = analytics.lexical_diversity.toFixed(3);
  metrics.noise.textContent = analytics.noise_score.toFixed(3);

  documentsEl.innerHTML = payload.documents
    .map((document, index) => {
      const sentiment = document.sentiment;
      const triage = document.triage;
      const cleaned = document.preprocessing.cleaned_text || "No tokens retained";
      const warnings = document.preprocessing.warnings.length
        ? `<p>${document.preprocessing.warnings.join(" ")}</p>`
        : "";
      return `
        <article class="doc">
          <div class="doc-head">
            <strong>${triage.priority} · Document ${index + 1}</strong>
            <span class="label ${sentiment.label}">${sentiment.label} ${Math.round(sentiment.confidence * 100)}%</span>
          </div>
          <p>${escapeHtml(cleaned)}</p>
          <div class="triage-line">
            <span>${escapeHtml(triage.topic.name)}</span>
            <span>${escapeHtml(triage.recommendation.owner)}</span>
            <span>${escapeHtml(triage.recommendation.action)}</span>
          </div>
          ${warnings}
        </article>
      `;
    })
    .join("");

  renderTerms(payload.top_terms);
  renderRisk(payload.corpus_insight);
  renderModelLab(payload.documents);
  renderAnnotations(payload.documents[0]?.annotations.annotations ?? []);
}

function renderRisk(insight) {
  const topics = insight.topic_distribution
    .map((topic) => `<span>${escapeHtml(topic.name)} ${Math.round(topic.score * 100)}%</span>`)
    .join("");
  riskPanelEl.innerHTML = `
    <div class="risk ${insight.risk_level.toLowerCase()}">
      <span>Risk</span>
      <strong>${escapeHtml(insight.risk_level)}</strong>
    </div>
    <p><strong>${escapeHtml(insight.dominant_topic)}</strong> is the leading theme. Negative share is ${Math.round(
      insight.negative_share * 100,
    )}%.</p>
    <p>${escapeHtml(insight.recommended_next_step)}</p>
    <div class="topic-pills">${topics}</div>
  `;
}

function renderModelLab(documents) {
  const signals = documents.flatMap((document) =>
    document.triage.model_signals.map((signal) => ({
      ...signal,
      priority: document.triage.priority,
      topic: document.triage.topic.name,
      urgency: document.triage.urgency_score,
    })),
  );

  modelLabEl.innerHTML = signals.length
    ? signals
        .slice(0, 9)
        .map(
          (signal) => `
            <article class="model-card">
              <div>
                <strong>${escapeHtml(signal.model)}</strong>
                <span>${escapeHtml(signal.role)}</span>
              </div>
              <p>${escapeHtml(signal.prediction)} · ${Math.round(signal.confidence * 100)}%</p>
              <small>${escapeHtml(signal.priority)} · ${escapeHtml(signal.topic)} · urgency ${Math.round(
                signal.urgency * 100,
              )}%</small>
            </article>
          `,
        )
        .join("")
    : '<p class="muted">Run analysis to compare model signals.</p>';
}

function renderTerms(terms) {
  const max = Math.max(...terms.map((term) => term.count), 1);
  termsEl.innerHTML = terms.length
    ? terms
        .map(
          (term) => `
            <div class="term">
              <strong>${escapeHtml(term.token)}</strong>
              <div class="bar"><span style="width: ${(term.count / max) * 100}%"></span></div>
              <span>${term.count}</span>
            </div>
          `,
        )
        .join("")
    : '<p class="muted">No terms available.</p>';
}

function renderAnnotations(annotations) {
  annotationsEl.innerHTML = annotations.length
    ? annotations
        .slice(0, 48)
        .map(
          (item) => `
            <div class="annotation">
              <strong>${escapeHtml(item.token)}</strong>
              <span>${item.pos} / ${item.chunk}</span>
            </div>
          `,
        )
        .join("")
    : '<p class="muted">Run the pipeline to inspect token annotations.</p>';
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return entities[character];
  });
}

inputText.addEventListener("input", updateDocumentCount);
runBtn.addEventListener("click", runPipeline);
sampleBtn.addEventListener("click", () => {
  const current = samples.indexOf(inputText.value);
  inputText.value = samples[(current + 1) % samples.length];
  updateDocumentCount();
  runPipeline();
});
exportBtn.addEventListener("click", () => {
  if (!latestPayload) {
    return;
  }
  const report = JSON.stringify(latestPayload, null, 2);
  const blob = new Blob([report], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "clarity-triage-report.json";
  anchor.click();
  URL.revokeObjectURL(url);
});
minLength.addEventListener("input", () => {
  minLengthValue.textContent = minLength.value;
});

updateDocumentCount();
checkHealth();
runPipeline();
