"use strict";

const CORE_FILES = ["__init__.py", "wish_calculator.py", "pull_calculator.py", "mixed_calculator.py", "storage.py"];
const state = {
  pyodide: null,
  ready: false,
  banner: "agent",
  events: { events: [], generated_at: null, error: null },
};

const $ = (id) => document.getElementById(id);
const pct = (value) => `${(Number(value) * 100).toFixed(2)}%`;

function setStatus(text, ok = true) {
  const el = $("runtime-status");
  el.textContent = text;
  el.style.color = ok ? "var(--success)" : "var(--error)";
}

function todayISO() {
  const d = new Date();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${month}-${day}`;
}

function copiesWord(value) {
  const n = Number(value);
  if (n % 10 === 1 && n % 100 !== 11) return "копия";
  if (n >= 2 && n <= 4) return "копии";
  return "копий";
}

async function fetchText(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.text();
}

async function boot() {
  try {
    setStatus("Загрузка Python…");
    const pyodide = await loadPyodide({
      indexURL: "https://cdn.jsdelivr.net/pyodide/v0.28.2/full/",
    });
    pyodide.FS.mkdirTree("/app/core");
    for (const file of CORE_FILES) {
      pyodide.FS.writeFile(`/app/core/${file}`, await fetchText(`./py/core/${file}`));
    }
    pyodide.FS.writeFile("/app/web_bridge.py", await fetchText("./py/web_bridge.py"));
    await pyodide.runPythonAsync(`
import sys
sys.path.insert(0, "/app")
import web_bridge
`);
    state.pyodide = pyodide;
    state.ready = true;
    await loadEvents();
    setStatus("ГОТОВО");
  } catch (error) {
    console.error(error);
    setStatus("ОШИБКА PYTHON", false);
  }
}

async function loadEvents() {
  try {
    const response = await fetch("./data/events.json", { cache: "no-store" });
    if (!response.ok) throw new Error(String(response.status));
    state.events = await response.json();
    const count = state.events.events?.length || 0;
    $("events-status").textContent = state.events.error
      ? "снимок недоступен"
      : `${count} событий · снимок ${state.events.generated_at?.slice(0, 10) || ""}`;
  } catch (error) {
    console.warn("events snapshot:", error);
    $("events-status").textContent = "снимок недоступен";
  }
}

function call(name, payload) {
  if (!state.ready) throw new Error("Python ещё загружается");
  state.pyodide.globals.set("_bridge_name", name);
  state.pyodide.globals.set("_bridge_payload", JSON.stringify(payload));
  const raw = state.pyodide.runPython(`
import json as _json
import web_bridge as _bridge
_json.dumps(getattr(_bridge, _bridge_name)(**_json.loads(_bridge_payload)), ensure_ascii=False)
`);
  state.pyodide.globals.delete("_bridge_name");
  state.pyodide.globals.delete("_bridge_payload");
  return JSON.parse(raw);
}

function showResult(element, isError = false) {
  element.hidden = false;
  element.classList.toggle("error", isError);
}

function setBusy(button, progress, busy) {
  button.disabled = busy;
  progress.hidden = !busy;
}

async function withProgress(button, progress, handler) {
  if (!state.ready) {
    setStatus("Python ещё загружается", false);
    return;
  }
  setBusy(button, progress, true);
  await new Promise((resolve) => setTimeout(resolve, 40));
  try {
    handler();
  } catch (error) {
    console.error(error);
    setStatus("ОШИБКА РАСЧЁТА", false);
  } finally {
    setBusy(button, progress, false);
  }
}

function eventIncome(days) {
  if (!state.events.events?.length) {
    return { polychromes_min: 0, polychromes_max: 0, tapes: 0, pulls_min: 0, pulls_max: 0, count: 0 };
  }
  return call("event_income", { events: state.events.events, start_iso: todayISO(), days });
}

/* ---------- chance tab ---------- */

const wishCopies = $("wish-copies");

function syncWishBanner() {
  const isEngine = state.banner === "w_engine";
  const max = isEngine ? 5 : 7;
  wishCopies.max = String(max);
  wishCopies.value = String(Math.min(Number(wishCopies.value), max));
  $("wish-subtitle").textContent = isEngine
    ? "канал W-ENGINE · 75/25 · hard pity 80"
    : "канал агента · 50/50 · hard pity 90";
  $("wish-pity").max = isEngine ? "79" : "89";
  $("wish-pity-hint").textContent = isEngine ? "0–79" : "0–89";
  $("wish-guarantee-hint").textContent = isEngine ? "следующий S — оружие" : "следующий S — ивент";
  $("wish-hard").textContent = isEngine ? "80" : "90";
  $("wish-guarantee-stat").textContent = isEngine ? "160" : "180";
  updateWishCopiesLabel();
}

function updateWishCopiesLabel() {
  const value = Number(wishCopies.value);
  const level = state.banner === "agent" ? `M${value - 1}` : `R${value}`;
  $("wish-copies-label").textContent = `${level} · ${value} ${copiesWord(value)}`;
}

function calculateWish() {
  const pity = Number($("wish-pity").value);
  const pulls = Number($("wish-pulls").value);
  const copies = Number(wishCopies.value);
  const guarantee = $("wish-guarantee").checked;
  const result = $("wish-result");
  try {
    const probability = call("wish_chance", {
      pity,
      pulls,
      copies,
      banner: state.banner,
      guarantee,
    });
    const unit = state.banner === "agent" ? "КОПИЙ" : "W-ENGINE";
    $("wish-result-value").textContent = `ШАНС ≥${copies} ${unit}: ${pct(probability)}`;
    $("wish-result-hint").textContent = `Пити ${pity} · ${pulls} круток · ${guarantee ? "гарант активен" : "50/50"}`;
    $("wish-result-bar").style.width = `${Math.min(100, probability * 100)}%`;
    showResult(result, false);
  } catch (error) {
    $("wish-result-value").textContent = "ПРОВЕРЬТЕ ЗНАЧЕНИЯ";
    $("wish-result-hint").textContent = String(error.message || error);
    showResult(result, true);
  }
}

document.querySelectorAll("[data-banner]").forEach((button) => {
  button.addEventListener("click", () => {
    state.banner = button.dataset.banner;
    document.querySelectorAll("[data-banner]").forEach((b) => b.classList.toggle("active", b === button));
    syncWishBanner();
    $("wish-result").hidden = true;
  });
});
wishCopies.addEventListener("input", updateWishCopiesLabel);
$("wish-calc").addEventListener("click", () =>
  withProgress($("wish-calc"), $("wish-progress"), calculateWish),
);

/* ---------- pulls tab ---------- */

function calculatePulls() {
  const result = $("pull-result");
  try {
    const days = Number($("pull-days").value);
    const includeEvents = $("pull-events").checked;
    const income = includeEvents ? eventIncome(days) : { pulls_min: 0, pulls_max: 0, count: 0 };
    const forecast = call("pull_forecast", {
      current_pulls: Number($("pull-current").value),
      current_polychromes: Number($("pull-poly").value),
      current_monochromes: Number($("pull-mono").value),
      subscription_days: Number($("pull-sub").value),
      days,
      event_pulls_min: income.pulls_min,
      event_pulls_max: income.pulls_max,
    });
    const total = forecast.total_pulls_min === forecast.total_pulls_max
      ? String(forecast.total_pulls_max)
      : `${forecast.total_pulls_min}–${forecast.total_pulls_max}`;
    $("pull-result-value").textContent = `🎯 ИТОГО КРУТОК: ${total}`;
    $("pull-result-hint").textContent = includeEvents
      ? `Ивенты: +${income.pulls_min}–${income.pulls_max} · ${income.count} событий`
      : "Ивенты отключены";
    const lines = [
      `Без эндгейма: ${forecast.base_min}`,
      `С эндгеймом: ${forecast.base_max}`,
      `Ивенты: +${forecast.events_min}–${forecast.events_max}`,
      "",
      ...Object.entries(forecast)
        .filter(([key, value]) => typeof value === "number" && !["base_min", "base_max", "events_min", "events_max"].includes(key))
        .map(([key, value]) => `${key}: ${value}`),
    ];
    $("pull-result-details").textContent = lines.join("\n");
    showResult(result, false);
  } catch (error) {
    $("pull-result-value").textContent = "ПРОВЕРЬТЕ ЗНАЧЕНИЯ";
    $("pull-result-details").textContent = String(error.message || error);
    showResult(result, true);
  }
}

$("pull-calc").addEventListener("click", () =>
  withProgress($("pull-calc"), $("pull-progress"), calculatePulls),
);

/* ---------- mixed tab ---------- */

const mixAgentCopies = $("mix-agent-copies");
const mixEngineCopies = $("mix-engine-copies");

function updateMixLabels() {
  const agent = Number(mixAgentCopies.value);
  const engine = Number(mixEngineCopies.value);
  $("mix-agent-copies-label").textContent = `M${agent - 1} · ${agent} ${copiesWord(agent)}`;
  $("mix-engine-copies-label").textContent = `R${engine} · ${engine} ${copiesWord(engine)}`;
}

function calculateMix() {
  const result = $("mix-result");
  try {
    const data = call("mixed_chance", {
      total_pulls: Number($("mix-total").value),
      agent_copies: Number(mixAgentCopies.value),
      engine_copies: Number(mixEngineCopies.value),
      agent_pity: Number($("mix-agent-pity").value),
      agent_guarantee: $("mix-agent-guarantee").checked,
      engine_pity: Number($("mix-engine-pity").value),
      engine_guarantee: $("mix-engine-guarantee").checked,
    });
    $("mix-result-value").textContent = `ШАНС НА ОБА: ${pct(data.both_probability)}`;
    $("mix-result-bar").style.width = `${Math.min(100, data.both_probability * 100)}%`;
    $("mix-result-details").textContent = [
      `Агент: ${pct(data.agent_probability)} · ${data.agent_pulls} круток · ${data.agent_copies} коп.`,
      `W-Engine: ${pct(data.engine_probability)} · ${data.engine_pulls} круток · ${data.engine_copies} коп.`,
      `Сплит: ${data.agent_pulls} / ${data.engine_pulls}`,
    ].join("\n");
    showResult(result, false);
  } catch (error) {
    $("mix-result-value").textContent = "ПРОВЕРЬТЕ ЗНАЧЕНИЯ";
    $("mix-result-details").textContent = String(error.message || error);
    showResult(result, true);
  }
}

mixAgentCopies.addEventListener("input", updateMixLabels);
mixEngineCopies.addEventListener("input", updateMixLabels);
$("mix-calc").addEventListener("click", () =>
  withProgress($("mix-calc"), $("mix-progress"), calculateMix),
);

/* ---------- tabs ---------- */

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b === button));
    document.querySelectorAll(".panel").forEach((panel) => {
      panel.hidden = panel.id !== `panel-${button.dataset.tab}`;
    });
  });
});

syncWishBanner();
updateMixLabels();
boot();
