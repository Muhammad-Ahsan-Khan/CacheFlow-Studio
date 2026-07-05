"use strict";

const memoryValues = Array.from({ length: 20 }, (_, index) => (index + 1) * 10);
const policyDetails = {
  FIFO: {
    title: "First In, First Out",
    description: "When the cache is full, the oldest inserted value is replaced first.",
    rule: "Oldest insertion"
  },
  LRU: {
    title: "Least Recently Used",
    description: "When the cache is full, the value that has gone unused for the longest time is replaced.",
    rule: "Oldest recent use"
  }
};

const elements = {
  policyButtons: [...document.querySelectorAll("[data-policy]")],
  accessCount: document.querySelector("#accessCount"),
  accessOutput: document.querySelector("#accessOutput"),
  speedSelect: document.querySelector("#speedSelect"),
  seedInput: document.querySelector("#seedInput"),
  runButton: document.querySelector("#runButton"),
  resetButton: document.querySelector("#resetButton"),
  exportButton: document.querySelector("#exportButton"),
  connectionDot: document.querySelector("#connectionDot"),
  connectionText: document.querySelector("#connectionText"),
  ratioMetric: document.querySelector("#ratioMetric"),
  hitMetric: document.querySelector("#hitMetric"),
  missMetric: document.querySelector("#missMetric"),
  accessMetric: document.querySelector("#accessMetric"),
  policyMetric: document.querySelector("#policyMetric"),
  ratioHint: document.querySelector("#ratioHint"),
  runState: document.querySelector("#runState"),
  requestValue: document.querySelector("#requestValue"),
  requestIndex: document.querySelector("#requestIndex"),
  cacheBank: document.querySelector("#cacheBank"),
  resultBanner: document.querySelector("#resultBanner"),
  memoryGrid: document.querySelector("#memoryGrid"),
  ratioDonut: document.querySelector("#ratioDonut"),
  donutValue: document.querySelector("#donutValue"),
  legendHits: document.querySelector("#legendHits"),
  legendMisses: document.querySelector("#legendMisses"),
  trendLine: document.querySelector("#trendLine"),
  policyBadge: document.querySelector("#policyBadge"),
  policyTitle: document.querySelector("#policyTitle"),
  policyDescription: document.querySelector("#policyDescription"),
  policyRule: document.querySelector("#policyRule"),
  activityBody: document.querySelector("#activityBody")
};

const state = {
  policy: "FIFO",
  source: null,
  events: [],
  ratios: [],
  running: false,
  requestedAccesses: 30
};

function buildStaticViews() {
  elements.cacheBank.innerHTML = Array.from({ length: 5 }, (_, index) => `
    <div class="cache-slot" data-slot="${index}">
      <small>LINE ${index}</small><strong>__</strong>
    </div>`).join("");

  elements.memoryGrid.innerHTML = memoryValues.map((value, index) => `
    <div class="memory-cell" data-memory-index="${index}">
      <small>${String(index).padStart(2, "0")}</small><strong>${value}</strong>
    </div>`).join("");
}

function setPolicy(policy) {
  if (state.running) return;
  state.policy = policy;
  elements.policyButtons.forEach(button => button.classList.toggle("active", button.dataset.policy === policy));
  const detail = policyDetails[policy];
  elements.policyBadge.textContent = policy;
  elements.policyTitle.textContent = detail.title;
  elements.policyDescription.textContent = detail.description;
  elements.policyRule.textContent = detail.rule;
  elements.policyMetric.textContent = `${policy} policy selected`;
}

function setRunState(kind, label) {
  elements.runState.className = `run-state ${kind}`;
  elements.runState.innerHTML = `<span></span>${label}`;
  elements.connectionDot.classList.toggle("running", kind === "running");
  elements.connectionText.textContent = label;
}

function updateMetrics(event) {
  elements.ratioMetric.textContent = `${event.hit_ratio.toFixed(2)}%`;
  elements.hitMetric.textContent = event.hits;
  elements.missMetric.textContent = event.misses;
  elements.accessMetric.textContent = `${event.accesses} / ${state.requestedAccesses}`;
  elements.ratioHint.textContent = event.accesses < 5 ? "Early simulation data" : "Current cache efficiency";
  elements.ratioDonut.style.setProperty("--ratio", event.hit_ratio);
  elements.donutValue.textContent = `${Math.round(event.hit_ratio)}%`;
  elements.legendHits.textContent = event.hits;
  elements.legendMisses.textContent = event.misses;
}

function updateVisualizer(event) {
  elements.requestValue.textContent = event.value;
  elements.requestIndex.textContent = `Memory index ${event.index}`;

  document.querySelectorAll(".memory-cell").forEach(cell => {
    cell.classList.toggle("active", Number(cell.dataset.memoryIndex) === event.index);
  });

  document.querySelectorAll(".cache-slot").forEach((slot, index) => {
    slot.classList.remove("active-hit", "active-miss");
    slot.querySelector("strong").textContent = event.cache[index] ?? "__";
    if (index === event.slot) slot.classList.add(event.outcome === "HIT" ? "active-hit" : "active-miss");
  });

  if (event.outcome === "HIT") {
    elements.resultBanner.className = "result-banner hit";
    elements.resultBanner.innerHTML = `<span class="result-symbol">✓</span><div><strong>Cache hit</strong><small>Value ${event.value} was already available in line ${event.slot}.</small></div>`;
  } else {
    const replacement = event.evicted === null ? "an empty cache line" : `value ${event.evicted}`;
    elements.resultBanner.className = "result-banner miss";
    elements.resultBanner.innerHTML = `<span class="result-symbol">↓</span><div><strong>Cache miss</strong><small>Loaded ${event.value} into line ${event.slot}, replacing ${replacement}.</small></div>`;
  }
}

function appendEvent(event) {
  if (state.events.length === 1) elements.activityBody.innerHTML = "";
  const snapshot = event.cache.map(value => value ?? "__").join(", ");
  const replacement = event.evicted === null ? "—" : event.evicted;
  const row = document.createElement("tr");
  row.innerHTML = `
    <td>${event.step}</td>
    <td>Index ${event.index} <strong>→ ${event.value}</strong></td>
    <td><span class="event-pill ${event.outcome.toLowerCase()}">${event.outcome}</span></td>
    <td>Line ${event.slot}</td>
    <td>${replacement}</td>
    <td><span class="cache-code">[ ${snapshot} ]</span></td>`;
  elements.activityBody.prepend(row);
}

function renderTrend() {
  const ratios = state.ratios;
  if (!ratios.length) {
    elements.trendLine.setAttribute("points", "0,90");
    return;
  }
  const width = 320;
  const height = 88;
  const points = ratios.map((ratio, index) => {
    const x = ratios.length === 1 ? 0 : (index / (ratios.length - 1)) * width;
    const y = height - (ratio / 100) * height;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  elements.trendLine.setAttribute("points", points.join(" "));
}

function resetDashboard(closeSource = true) {
  if (closeSource && state.source) state.source.close();
  state.source = null;
  state.events = [];
  state.ratios = [];
  state.running = false;

  elements.ratioMetric.textContent = "0.00%";
  elements.hitMetric.textContent = "0";
  elements.missMetric.textContent = "0";
  elements.accessMetric.textContent = `0 / ${elements.accessCount.value}`;
  elements.ratioHint.textContent = "Waiting for data";
  elements.requestValue.textContent = "—";
  elements.requestIndex.textContent = "Memory index —";
  elements.ratioDonut.style.setProperty("--ratio", 0);
  elements.donutValue.textContent = "0%";
  elements.legendHits.textContent = "0";
  elements.legendMisses.textContent = "0";
  elements.resultBanner.className = "result-banner neutral";
  elements.resultBanner.innerHTML = `<span class="result-symbol">•</span><div><strong>Ready to simulate</strong><small>Select a policy and start the run.</small></div>`;
  elements.activityBody.innerHTML = `<tr class="empty-row"><td colspan="6">Simulation events will appear here.</td></tr>`;
  document.querySelectorAll(".cache-slot").forEach(slot => {
    slot.classList.remove("active-hit", "active-miss");
    slot.querySelector("strong").textContent = "__";
  });
  document.querySelectorAll(".memory-cell").forEach(cell => cell.classList.remove("active"));
  renderTrend();
  setRunState("idle", "Ready");
  toggleControls(false);
  elements.exportButton.disabled = true;
}

function toggleControls(running) {
  state.running = running;
  elements.policyButtons.forEach(button => button.disabled = running);
  elements.accessCount.disabled = running;
  elements.speedSelect.disabled = running;
  elements.seedInput.disabled = running;
  elements.runButton.disabled = running;
}

function runSimulation() {
  resetDashboard();
  state.requestedAccesses = Number(elements.accessCount.value);
  elements.accessMetric.textContent = `0 / ${state.requestedAccesses}`;
  toggleControls(true);
  setRunState("running", "Running");

  const query = new URLSearchParams({
    policy: state.policy,
    accesses: String(state.requestedAccesses),
    delay: elements.speedSelect.value
  });
  if (elements.seedInput.value.trim()) query.set("seed", elements.seedInput.value.trim());

  state.source = new EventSource(`/api/stream?${query}`);

  state.source.addEventListener("access", message => {
    const event = JSON.parse(message.data);
    state.events.push(event);
    state.ratios.push(event.hit_ratio);
    updateMetrics(event);
    updateVisualizer(event);
    appendEvent(event);
    renderTrend();
  });

  state.source.addEventListener("summary", message => {
    const summary = JSON.parse(message.data);
    elements.ratioHint.textContent = `${summary.policy} final efficiency`;
  });

  state.source.addEventListener("done", () => {
    state.source.close();
    state.source = null;
    toggleControls(false);
    setRunState("complete", "Complete");
    elements.exportButton.disabled = state.events.length === 0;
  });

  state.source.onerror = () => {
    if (!state.running) return;
    if (state.source) state.source.close();
    state.source = null;
    toggleControls(false);
    setRunState("idle", "Disconnected");
    elements.resultBanner.className = "result-banner neutral";
    elements.resultBanner.innerHTML = `<span class="result-symbol">!</span><div><strong>Connection ended</strong><small>Confirm that dashboard_server.py is still running.</small></div>`;
  };
}

function exportReport() {
  if (!state.events.length) return;
  const finalEvent = state.events.at(-1);
  const payload = {
    project: "CacheFlow Studio",
    generated_at: new Date().toISOString(),
    configuration: {
      policy: state.policy,
      requested_accesses: state.requestedAccesses,
      seed: elements.seedInput.value.trim() || null
    },
    summary: {
      hits: finalEvent.hits,
      misses: finalEvent.misses,
      accesses: finalEvent.accesses,
      hit_ratio: finalEvent.hit_ratio,
      final_cache: finalEvent.cache
    },
    events: state.events
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `cacheflow-${state.policy.toLowerCase()}-report.json`;
  link.click();
  URL.revokeObjectURL(url);
}

buildStaticViews();
setPolicy("FIFO");
resetDashboard(false);

elements.policyButtons.forEach(button => button.addEventListener("click", () => setPolicy(button.dataset.policy)));
elements.accessCount.addEventListener("input", () => {
  elements.accessOutput.value = elements.accessCount.value;
  elements.accessMetric.textContent = `0 / ${elements.accessCount.value}`;
});
elements.runButton.addEventListener("click", runSimulation);
elements.resetButton.addEventListener("click", () => resetDashboard());
elements.exportButton.addEventListener("click", exportReport);
