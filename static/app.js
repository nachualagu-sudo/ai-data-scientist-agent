const state = { summary: null, model: null, selectedFile: null };
const MAX_CLIENT_FILE_BYTES = 10 * 1024 * 1024;
const $ = (id) => document.getElementById(id);

function message(text, type = "info") {
  const box = $("message");
  box.textContent = text;
  box.className = text ? `notice show ${type}` : "notice";
}

function setBusy(button, busy, busyText) {
  const label = button.querySelector(".button-label");
  if (!button.dataset.defaultLabel && label) button.dataset.defaultLabel = label.textContent;
  button.disabled = busy;
  button.classList.toggle("is-loading", busy);
  if (label) label.textContent = busy ? busyText : button.dataset.defaultLabel;
}

async function api(url, options = {}) {
  const response = await fetch(url, options);
  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[character]);
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return "0 KB";
  const units = ["B", "KB", "MB", "GB"];
  const unit = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / (1024 ** unit)).toFixed(unit > 1 ? 1 : 0)} ${units[unit]}`;
}

function table(records) {
  if (!records?.length) return '<div class="empty-state"><p>No records available.</p></div>';
  const keys = Object.keys(records[0]);
  return `<table><thead><tr>${keys.map((key) => `<th>${escapeHtml(key)}</th>`).join("")}</tr></thead><tbody>${records.map((row) => `<tr>${keys.map((key) => `<td>${escapeHtml(row[key])}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

function setOptions(select, values, includeNone = false) {
  const none = includeNone ? '<option value="">None</option>' : "";
  select.innerHTML = none + values.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
}

function markWorkflow(completedStep) {
  document.querySelectorAll(".workflow-summary > span").forEach((item, index) => {
    item.classList.toggle("complete", index < completedStep);
  });
}

function updateTargetHint() {
  const target = $("targetColumn").value;
  if (!target || !state.summary) return;
  const dataType = String(state.summary.data_types[target] || "");
  const numeric = /(int|float|double|decimal)/i.test(dataType);
  $("targetHint").textContent = numeric
    ? "Numeric column — Auto will usually use regression."
    : "Text/category column — Auto will use classification.";
}

function renderSummary(summary) {
  state.summary = summary;
  $("workspace").classList.remove("hidden");
  $("currentDataset").textContent = summary.dataset;
  const sampleNotice = $("sampleNotice");
  sampleNotice.classList.toggle("hidden", !summary.sampled);
  sampleNotice.textContent = summary.sampled
    ? `Large dataset: analysis, cleaning and model training use the first ${Number(summary.analysis_row_limit).toLocaleString()} rows only. The original upload is retained. Displayed counts and metrics do not describe the entire file.`
    : "";
  markWorkflow(1);

  const metrics = [
    { label: "Rows", value: summary.rows, icon: "↕", note: "Records" },
    { label: "Columns", value: summary.columns, icon: "≡", note: "Features" },
    { label: "Missing cells", value: summary.total_missing, icon: "!", note: summary.total_missing ? "Needs review" : "Complete" },
    { label: "Duplicates", value: summary.duplicates, icon: "⧉", note: summary.duplicates ? "Can be cleaned" : "Unique" },
  ];
  $("metrics").innerHTML = metrics.map((item) => `
    <article class="metric">
      <div class="metric-head"><span class="metric-icon">${item.icon}</span><span class="metric-trend">${item.note}</span></div>
      <strong>${Number(item.value).toLocaleString()}</strong><span>${item.label}</span>
    </article>`).join("");

  const columnRows = summary.column_names.map((name) => ({
    Column: name,
    "Data type": summary.data_types[name],
    "Missing values": summary.missing_values[name],
  }));
  $("columnsTable").innerHTML = table(columnRows);
  $("previewTable").innerHTML = table(summary.preview);
  setOptions($("xColumn"), summary.column_names);
  setOptions($("yColumn"), summary.column_names, true);
  setOptions($("targetColumn"), summary.column_names);

  const preferredTarget = summary.column_names.find((name) => name.toLowerCase() === "price");
  if (preferredTarget) $("targetColumn").value = preferredTarget;
  $("taskType").value = "auto";
  $("modelType").value = "auto";
  updateTargetHint();
  loadInsights();
}

async function loadSummary(silent = false) {
  try {
    renderSummary(await api("/dataset-summary"));
  } catch (error) {
    if (!silent) message(error.message, "error");
  }
}

async function loadInsights() {
  $("insightCards").innerHTML = '<div class="empty-state"><p>Generating insights…</p></div>';
  try {
    const data = await api("/dataset-insights");
    $("insightCards").innerHTML = data.insights.map((item) => `
      <article class="insight-card"><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.detail)}</p></article>`).join("");
  } catch (error) {
    $("insightCards").innerHTML = `<div class="notice show error">${escapeHtml(error.message)}</div>`;
  }
}

function showSelectedFile(file) {
  state.selectedFile = file;
  if (!file) {
    $("selectedFileName").textContent = "Choose a file or drop it here";
    $("selectedFileMeta").textContent = "CSV or XLSX · up to 10 MB";
    return;
  }
  $("selectedFileName").textContent = file.name;
  $("selectedFileMeta").textContent = `${formatBytes(file.size)} · Ready to upload`;
}

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.classList.remove("active");
      tab.setAttribute("aria-selected", "false");
    });
    document.querySelectorAll(".tab-content").forEach((content) => content.classList.remove("active"));
    button.classList.add("active");
    button.setAttribute("aria-selected", "true");
    $(button.dataset.tab).classList.add("active");
  });
});

$("datasetFile").addEventListener("change", (event) => showSelectedFile(event.target.files[0] || null));

const dropZone = $("dropZone");
["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  });
});
["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
  });
});
dropZone.addEventListener("drop", (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (!file) return;
  try {
    const transfer = new DataTransfer();
    transfer.items.add(file);
    $("datasetFile").files = transfer.files;
  } catch {
    state.selectedFile = file;
  }
  showSelectedFile(file);
});

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function setProgressStage(activeStage) {
  const stages = [$("stageUpload"), $("stageAnalyse"), $("stageReady")];
  stages.forEach((stage, index) => {
    stage.classList.remove("active", "done", "error");
    if (index < activeStage) stage.classList.add("done");
    if (index === activeStage) stage.classList.add("active");
  });
}

function openProgress(file) {
  $("progressFileName").textContent = file.name;
  $("progressFileSize").textContent = formatBytes(file.size);
  $("progressPercent").textContent = "0%";
  $("progressTitle").textContent = "Uploading your dataset";
  $("progressText").textContent = "Please keep this page open while the file is being transferred.";
  $("uploadProgress").value = 0;
  setProgressStage(0);
  $("progressOverlay").classList.remove("hidden");
  document.body.classList.add("modal-open");
}

function updateProgress(percent) {
  const safePercent = Math.min(100, Math.max(0, Math.round(percent)));
  $("uploadProgress").value = safePercent;
  $("progressPercent").textContent = `${safePercent}%`;
}

function showAnalysing() {
  $("uploadProgress").removeAttribute("value");
  $("progressPercent").textContent = "Processing";
  $("progressTitle").textContent = "Analysing your dataset";
  $("progressText").textContent = "Upload complete. Reading rows, columns, data types, and quality information…";
  setProgressStage(1);
}

function showReady() {
  $("uploadProgress").value = 100;
  $("progressPercent").textContent = "100%";
  $("progressTitle").textContent = "Dataset is ready";
  $("progressText").textContent = "Analysis completed successfully. Opening your workspace…";
  setProgressStage(2);
  $("stageReady").classList.remove("active");
  $("stageReady").classList.add("done");
}

function showProgressError(errorText) {
  $("uploadProgress").value = 0;
  $("progressPercent").textContent = "Failed";
  $("progressTitle").textContent = "Upload could not complete";
  $("progressText").textContent = errorText;
  document.querySelectorAll(".progress-stage").forEach((stage) => stage.classList.remove("active", "done"));
  $("stageUpload").classList.add("error");
}

function closeProgress() {
  $("progressOverlay").classList.add("hidden");
  document.body.classList.remove("modal-open");
}

function uploadDataset(file) {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("POST", "/upload-data");
    request.responseType = "json";
    request.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) updateProgress((event.loaded / event.total) * 100);
    });
    request.upload.addEventListener("load", showAnalysing);
    request.addEventListener("load", () => {
      const data = request.response || {};
      if (request.status >= 200 && request.status < 300) resolve(data);
      else reject(new Error(data.detail || `Request failed (${request.status})`));
    });
    request.addEventListener("error", () => reject(new Error("Network error. Check that the application server is still running.")));
    request.addEventListener("abort", () => reject(new Error("Upload was cancelled.")));
    const form = new FormData();
    form.append("file", file);
    request.send(form);
  });
}

$("uploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = $("datasetFile").files[0] || state.selectedFile;
  if (!file) {
    message("Choose a CSV or XLSX file first.", "error");
    return;
  }
  const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  if (![".csv", ".xlsx"].includes(extension)) {
    message("Only CSV and XLSX files are supported.", "error");
    return;
  }
  if (file.size > MAX_CLIENT_FILE_BYTES) {
    message("The selected file is larger than 10 MB.", "error");
    return;
  }

  const button = $("uploadButton");
  setBusy(button, true, "Analysing…");
  openProgress(file);
  message(`Uploading ${file.name} and analysing the data…`, "loading");
  try {
    const result = await uploadDataset(file);
    renderSummary(result);
    showReady();
    await delay(700);
    message(`${result.dataset} uploaded and analysed successfully.`, "success");
    $("workspace").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showProgressError(error.message);
    await delay(1200);
    message(error.message, "error");
  } finally {
    closeProgress();
    setBusy(button, false, "");
  }
});

$("cleanButton").addEventListener("click", async () => {
  const button = $("cleanButton");
  setBusy(button, true, "Cleaning…");
  message("Cleaning missing values and duplicates…", "loading");
  try {
    const result = await api("/clean-data", { method: "POST" });
    $("cleanReport").innerHTML = `<div class="report">
      <div><strong>${result.duplicates_removed}</strong><br>Duplicates removed</div>
      <div><strong>${result.missing_values_before}</strong><br>Missing before</div>
      <div><strong>${result.missing_values_after}</strong><br>Missing after</div>
      <div><strong>${result.rows_after}</strong><br>Final rows</div>
    </div>`;
    $("downloadDataset").classList.remove("hidden");
    await loadSummary(true);
    markWorkflow(2);
    message(result.sampled
      ? "First rows cleaned and saved as a copy. Model training uses original rows to avoid evaluation leakage."
      : "Dataset cleaned successfully. Model training uses original rows to avoid evaluation leakage.", "success");
  } catch (error) {
    message(error.message, "error");
  } finally {
    setBusy(button, false, "");
  }
});

function syncChartControls() {
  const type = $("chartType").value;
  const noAxes = type === "heatmap";
  $("xColumn").disabled = noAxes;
  $("yColumn").disabled = noAxes || ["histogram", "box"].includes(type);
}

$("chartType").addEventListener("change", syncChartControls);

$("chartButton").addEventListener("click", async () => {
  const button = $("chartButton");
  setBusy(button, true, "Generating…");
  message("Generating chart…", "loading");
  try {
    const result = await api("/visualize-data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chart_type: $("chartType").value,
        x_column: $("xColumn").value || null,
        y_column: $("yColumn").value || null,
      }),
    });
    $("chartImage").src = `${result.chart_url}?t=${Date.now()}`;
    $("chartImage").classList.remove("hidden");
    $("chartPlaceholder").classList.add("hidden");
    markWorkflow(3);
    message("Chart generated successfully.", "success");
  } catch (error) {
    message(error.message, "error");
  } finally {
    setBusy(button, false, "");
  }
});

function syncModelChoices() {
  const task = $("taskType").value;
  const linear = $("modelType").querySelector('option[value="linear"]');
  const logistic = $("modelType").querySelector('option[value="logistic"]');
  linear.disabled = task === "classification";
  logistic.disabled = task === "regression";
  if ($("modelType").selectedOptions[0]?.disabled) $("modelType").value = "auto";
}

$("taskType").addEventListener("change", syncModelChoices);
$("targetColumn").addEventListener("change", () => {
  $("taskType").value = "auto";
  $("modelType").value = "auto";
  syncModelChoices();
  updateTargetHint();
});

$("trainButton").addEventListener("click", async () => {
  const button = $("trainButton");
  setBusy(button, true, "Training…");
  message("Training and evaluating the model. This can take a moment…", "loading");
  try {
    const result = await api("/train-model", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target_column: $("targetColumn").value,
        task_type: $("taskType").value,
        model_type: $("modelType").value,
      }),
    });
    state.model = result;
    $("modelResult").innerHTML = `<div class="model-card">
      <div><h3>${escapeHtml(result.model_type.replaceAll("_", " "))} · ${escapeHtml(result.task_type)}</h3><p>${result.training_rows.toLocaleString()} training rows · ${result.testing_rows.toLocaleString()} testing rows · target: ${escapeHtml(result.target)}</p></div>
      <div class="score-grid">${Object.entries(result.metrics).map(([key, value]) => `<span class="score"><strong>${escapeHtml(value)}</strong><br>${escapeHtml(key.replaceAll("_", " ").toUpperCase())}</span>`).join("")}</div>
    </div>`;
    renderPredictionForm(result);
    markWorkflow(4);
    message("Model trained and evaluated successfully.", "success");
  } catch (error) {
    message(error.message, "error");
  } finally {
    setBusy(button, false, "");
  }
});

function renderPredictionForm(model) {
  const form = $("predictionForm");
  form.innerHTML = model.feature_columns.map((name) => {
    const numeric = model.numeric_features.includes(name);
    const value = model.example_values[name] ?? "";
    return `<label>${escapeHtml(name)}<input name="${escapeHtml(name)}" type="${numeric ? "number" : "text"}" ${numeric ? 'step="any"' : ""} value="${escapeHtml(value)}" required></label>`;
  }).join("") + `<button class="primary-button" type="submit"><span class="button-label">Predict ${escapeHtml(model.target)}</span><span>→</span></button><div id="predictionResult" class="full"></div>`;
  $("predictionPanel").classList.remove("hidden");
}

$("predictionForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector('button[type="submit"]');
  const features = Object.fromEntries(new FormData(event.currentTarget).entries());
  setBusy(button, true, "Predicting…");
  try {
    const result = await api("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ features }),
    });
    $("predictionResult").innerHTML = `<div class="prediction-result">Predicted ${escapeHtml(result.target)}: ${escapeHtml(result.prediction)}</div>`;
  } catch (error) {
    message(error.message, "error");
  } finally {
    setBusy(button, false, "");
  }
});

syncChartControls();
syncModelChoices();
loadSummary(true);
