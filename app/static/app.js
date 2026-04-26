const inputText = document.querySelector("#inputText");
const runBtn = document.querySelector("#runBtn");
const sampleBtn = document.querySelector("#sampleBtn");
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

const samples = [
  "Get 100% FREE access now!!!\nI absolutely looooved this product\nWorst service ever... 0/10\nCall me at 9876543210\nThis is THE best course!!!\nVisit https://openai.com now!\nNooooo this is baaad!!!\nOK OK OK I got it\nWin $$$ now!!! Limited offer!!!\nI am not happy with this",
  "The quick brown fox jumps over a beautiful knowledge graph.\nOur production pipeline is fast, clean, and reliable.\nThis release is not slow and not broken anymore.",
  "Email support@example.com for urgent access.\nThe model crashed twice but the new preprocessing flow is excellent.\nNever remove not from sentiment tasks.",
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
  runBtn.textContent = isLoading ? "Running..." : "Run pipeline";
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
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
    const response = await fetch("/api/v1/pipeline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ documents, options: getOptions() }),
    });

    if (!response.ok) {
      throw new Error(`Pipeline failed with ${response.status}`);
    }

    const payload = await response.json();
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
      const cleaned = document.preprocessing.cleaned_text || "No tokens retained";
      const warnings = document.preprocessing.warnings.length
        ? `<p>${document.preprocessing.warnings.join(" ")}</p>`
        : "";
      return `
        <article class="doc">
          <div class="doc-head">
            <strong>Document ${index + 1}</strong>
            <span class="label ${sentiment.label}">${sentiment.label} ${Math.round(sentiment.confidence * 100)}%</span>
          </div>
          <p>${escapeHtml(cleaned)}</p>
          ${warnings}
        </article>
      `;
    })
    .join("");

  renderTerms(payload.top_terms);
  renderAnnotations(payload.documents[0]?.annotations.annotations ?? []);
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
minLength.addEventListener("input", () => {
  minLengthValue.textContent = minLength.value;
});

updateDocumentCount();
checkHealth();
runPipeline();

