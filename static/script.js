/* ================================================================
   Meeting Intelligence — Front-End Logic
   AJAX analysis, tabs, theme, history, word cloud, downloads
   ================================================================ */

// ── State ────────────────────────────────────────────────────
let currentResult = null;
let currentTranscript = "";

// ── DOM helpers ──────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);
const show = (el) => el.classList.remove("hidden");
const hide = (el) => el.classList.add("hidden");

// ── Sample transcripts ──────────────────────────────────────
const SAMPLES = {
  1: `Ravi: Good morning everyone. Let's start with the sprint update.
Priya: I completed the user authentication module yesterday. I will start working on the dashboard by tomorrow.
Arun: The database migration is still in progress. I need help from Ravi to review the schema changes.
Ravi: Sure, I will review the schema by end of day. We agreed to prioritize the API integration for this sprint.
Priya: I will test the login page before November 8. There's a bug in the password reset flow that needs urgent attention.
Arun: I will fix the password reset bug today. It's a critical blocker for the release.
Ravi: Good. We decided to move the release date to November 15 to allow more testing time.
Priya: Should we also update the documentation before the release?
Ravi: Yes, Arun should update the API documentation by November 12.
Arun: I will complete the backend and API docs by November 12.
Ravi: We agreed to integrate both parts and submit the project on November 15. Let's meet again tomorrow at 10 AM.`,

  2: `Sarah: Welcome everyone. Today we're discussing the Q4 product roadmap.
Mike: The mobile app has reached 50,000 downloads. We should focus on improving user retention.
Sarah: I agree. What's our current retention rate?
Lisa: It's at 35 percent for 30-day retention. Industry average is around 40 percent.
Mike: We decided to implement push notifications to improve engagement. I will create the notification system design by November 20.
Sarah: Good idea. Lisa, can you analyze which features users engage with most?
Lisa: I will run the user behavior analysis by next week. We should also consider adding a tutorial for new users.
Sarah: Let's do that. The team agreed to add an onboarding tutorial. Mike will handle the implementation.
Mike: I should have a prototype ready by December 1. Is that timeline acceptable?
Sarah: That works. We also need to address the payment gateway issues. There have been 15 failed transactions this week.
Lisa: That's urgent. I will investigate the payment failures immediately and report back by tomorrow.
Sarah: We approved the budget for hiring two more developers. The job postings should go live by November 10.
Mike: Any thoughts on whether we should build the analytics dashboard in-house or use a third-party solution?
Sarah: We decided to go with a custom in-house solution for better data control. Lisa will lead that project.`
};


// ── Theme toggle ─────────────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem("mi-theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  updateThemeIcon(saved);
}

function toggleTheme() {
  const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("mi-theme", next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const icon = $("#themeIcon");
  if (!icon) return;
  icon.innerHTML = theme === "dark"
    ? '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>'
    : '<path d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z"/>';
}


// ── Tabs ──────────────────────────────────────────────────────
function initTabs() {
  $$(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      $$(".tab").forEach((t) => t.classList.remove("active"));
      $$(".tab-panel").forEach((p) => p.classList.remove("active"));
      tab.classList.add("active");
      const panel = $(`#tab-${tab.dataset.tab}`);
      if (panel) panel.classList.add("active");
    });
  });
}


// ── Load sample transcript ───────────────────────────────────
function loadSample(id) {
  const ta = $("#transcript");
  if (ta && SAMPLES[id]) {
    ta.value = SAMPLES[id];
    ta.focus();
    toast("Sample transcript loaded!");
  }
}


// ── Toast ─────────────────────────────────────────────────────
function toast(msg) {
  const el = $("#toast");
  if (!el) return;
  el.textContent = msg;
  el.classList.remove("hidden");
  el.classList.add("show");
  setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => el.classList.add("hidden"), 300);
  }, 2200);
}


// ── Form submission (AJAX) ───────────────────────────────────
function initForm() {
  const form = $("#analyzeForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = $("#analyzeBtn");
    const loading = $("#loading");
    const errorEl = $("#errorMsg");
    const resultsEl = $("#results");

    hide(errorEl);
    hide(resultsEl);
    show(loading);
    btn.disabled = true;

    try {
      const fileInput = $("#fileInput");
      const file = fileInput && fileInput.files[0];
      let data;

      if (file) {
        // Send as form data
        const fd = new FormData(form);
        const resp = await fetch("/api/analyze", { method: "POST", body: fd });
        data = await resp.json();
        if (!resp.ok) throw new Error(data.error || "Analysis failed.");
      } else {
        // Send as JSON
        const transcript = $("#transcript").value.trim();
        const resp = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ transcript }),
        });
        data = await resp.json();
        if (!resp.ok) throw new Error(data.error || "Analysis failed.");
      }

      currentResult = data;
      currentTranscript = data.transcript || $("#transcript").value.trim();
      renderResults(data);
      saveToHistory(currentTranscript, data);
      show(resultsEl);
      resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      errorEl.textContent = err.message;
      show(errorEl);
    } finally {
      hide(loading);
      btn.disabled = false;
    }
  });
}


// ── Render results ───────────────────────────────────────────
function renderResults(r) {
  // Stats
  $("#statWords").textContent = r.word_count.toLocaleString();
  $("#statDuration").textContent = r.duration;
  $("#statSentiment").textContent = `${r.sentiment.emoji} ${r.sentiment.label}`;
  $("#statActions").textContent = r.actions.length;

  // Summary
  $("#summaryText").textContent = r.summary;

  // Topics
  const topicsEl = $("#topicsChips");
  topicsEl.innerHTML = r.topics.length
    ? r.topics.map((t) => `<span class="chip">${esc(t)}</span>`).join("")
    : '<p class="muted">No topics detected.</p>';

  // Decisions
  const decisionsEl = $("#decisionsList");
  if (r.decisions.length) {
    decisionsEl.innerHTML =
      '<ul class="decision-list">' +
      r.decisions.map((d) => `<li>${esc(d)}</li>`).join("") +
      "</ul>";
  } else {
    decisionsEl.innerHTML = '<p class="muted">No explicit decisions detected.</p>';
  }

  // Word cloud
  renderWordCloud(r.word_cloud);

  // Actions
  renderActions(r.actions);

  // Speakers
  renderSpeakerBars(r.speaker_stats);
  renderSpeakerSentiment(r.speaker_sentiment);

  // Entities
  const entEl = $("#entitiesInfo");
  entEl.innerHTML = `
    <div class="entity-section"><strong>People:</strong> ${r.people.length ? r.people.map((p) => `<span class="chip">${esc(p)}</span>`).join(" ") : '<span class="muted">None detected</span>'}</div>
    <div class="entity-section" style="margin-top:10px"><strong>Dates:</strong> ${r.dates.length ? r.dates.map((d) => `<span class="chip">${esc(d)}</span>`).join(" ") : '<span class="muted">None detected</span>'}</div>
  `;

  // Sentiment detail
  renderSentimentDetail(r.sentiment);

  // Questions
  renderQuestions(r.questions);

  // Reset to first tab
  $$(".tab")[0]?.click();
}


// ── Word cloud ───────────────────────────────────────────────
function renderWordCloud(words) {
  const el = $("#wordCloud");
  if (!words || !words.length) {
    el.innerHTML = '<p class="muted">Not enough text for a word cloud.</p>';
    return;
  }
  // Shuffle for visual interest
  const shuffled = [...words].sort(() => Math.random() - 0.5);
  el.innerHTML = shuffled
    .map((w) => {
      const size = Math.max(0.7, (w.size / 100) * 2.4 + 0.7);
      const opacity = 0.5 + (w.size / 100) * 0.5;
      return `<span class="wc-word" style="font-size:${size}rem;opacity:${opacity}" title="${esc(w.text)}: ${w.count}">${esc(w.text)}</span>`;
    })
    .join("");
}


// ── Actions table ────────────────────────────────────────────
function renderActions(actions) {
  const el = $("#actionsTable");
  if (!actions.length) {
    el.innerHTML = '<p class="muted">No action items detected. Try phrases like "Name will…" or "I will…".</p>';
    return;
  }
  el.innerHTML = `
    <table>
      <thead><tr><th>Task</th><th>Owner</th><th>Deadline</th><th>Priority</th></tr></thead>
      <tbody>
        ${actions.map((a) => `
          <tr>
            <td>${esc(a.task)}</td>
            <td>${esc(a.owner)}</td>
            <td>${esc(a.deadline)}</td>
            <td><span class="priority-badge priority-${a.priority.toLowerCase()}">${a.priority}</span></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}


// ── Speaker bars ─────────────────────────────────────────────
function renderSpeakerBars(stats) {
  const el = $("#speakerBars");
  if (!stats || !stats.length) {
    el.innerHTML = '<p class="muted">No speaker labels detected. Use "Name: dialogue" format.</p>';
    return;
  }
  el.innerHTML = stats
    .map(
      (s) => `
    <div class="speaker-bar-item">
      <div class="speaker-bar-header">
        <span class="name">${esc(s.speaker)}</span>
        <span class="pct">${s.percentage}% · ${s.word_count} words</span>
      </div>
      <div class="speaker-bar-track">
        <div class="speaker-bar-fill" style="width:${s.percentage}%"></div>
      </div>
    </div>
  `
    )
    .join("");
}


// ── Speaker sentiment ────────────────────────────────────────
function renderSpeakerSentiment(items) {
  const el = $("#speakerSentiment");
  if (!items || !items.length) {
    el.innerHTML = '<p class="muted">No speaker data available.</p>';
    return;
  }
  el.innerHTML = items
    .map(
      (s) => `
    <div class="speaker-sent-item">
      <span class="speaker-sent-name">${esc(s.speaker)}</span>
      <span class="speaker-sent-badge">${s.emoji} ${s.sentiment} <small>(${s.score})</small></span>
    </div>
  `
    )
    .join("");
}


// ── Sentiment detail ─────────────────────────────────────────
function renderSentimentDetail(s) {
  const el = $("#sentimentDetail");
  el.innerHTML = `
    <div class="sentiment-big-emoji">${s.emoji}</div>
    <div class="sentiment-label-big">${s.label} (${s.compound})</div>
    <div class="sentiment-bars">
      <div class="sent-row"><span class="lbl">Positive</span><div class="bar-track"><div class="bar-fill pos" style="width:${s.positive * 100}%"></div></div><span class="val">${(s.positive * 100).toFixed(1)}%</span></div>
      <div class="sent-row"><span class="lbl">Negative</span><div class="bar-track"><div class="bar-fill neg" style="width:${s.negative * 100}%"></div></div><span class="val">${(s.negative * 100).toFixed(1)}%</span></div>
      <div class="sent-row"><span class="lbl">Neutral</span><div class="bar-track"><div class="bar-fill neu" style="width:${s.neutral * 100}%"></div></div><span class="val">${(s.neutral * 100).toFixed(1)}%</span></div>
    </div>
  `;
}


// ── Questions ────────────────────────────────────────────────
function renderQuestions(qs) {
  const el = $("#questionsList");
  if (!qs || !qs.length) {
    el.innerHTML = '<p class="muted">No questions detected in the transcript.</p>';
    return;
  }
  el.innerHTML = qs
    .map(
      (q) => `
    <div class="question-item">
      <span class="question-speaker">${esc(q.speaker)}</span>
      <p style="margin:4px 0 0">${esc(q.question)}</p>
    </div>
  `
    )
    .join("");
}


// ── Downloads ────────────────────────────────────────────────
async function downloadTxt() {
  if (!currentTranscript) return toast("No analysis to download.");
  try {
    const resp = await fetch("/api/download/txt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript: currentTranscript }),
    });
    if (!resp.ok) throw new Error("Download failed.");
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "meeting_report.txt";
    a.click();
    URL.revokeObjectURL(url);
    toast("Report downloaded!");
  } catch (err) {
    toast("Download failed: " + err.message);
  }
}

function copySummary() {
  if (!currentResult) return toast("Nothing to copy.");
  navigator.clipboard
    .writeText(currentResult.summary)
    .then(() => toast("Summary copied to clipboard!"))
    .catch(() => toast("Copy failed."));
}


// ── History (localStorage) ───────────────────────────────────
const HISTORY_KEY = "mi-history";
const MAX_HISTORY = 20;

function getHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; }
  catch { return []; }
}

function saveToHistory(transcript, result) {
  const history = getHistory();
  history.unshift({
    time: new Date().toISOString(),
    preview: transcript.substring(0, 120),
    transcript,
    summary: result.summary,
  });
  if (history.length > MAX_HISTORY) history.length = MAX_HISTORY;
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function openHistory() {
  const modal = $("#historyModal");
  const list = $("#historyList");
  const history = getHistory();

  if (!history.length) {
    list.innerHTML = '<p class="muted" style="text-align:center;padding:20px">No analyses yet.</p>';
  } else {
    list.innerHTML = history
      .map(
        (h, i) => `
      <div class="history-item" onclick="loadHistory(${i})">
        <div class="history-time">${new Date(h.time).toLocaleString()}</div>
        <div class="history-preview">${esc(h.preview)}…</div>
      </div>
    `
      )
      .join("");
  }
  show(modal);
}

function closeHistory() { hide($("#historyModal")); }

function clearHistory() {
  localStorage.removeItem(HISTORY_KEY);
  closeHistory();
  toast("History cleared.");
}

function loadHistory(index) {
  const history = getHistory();
  if (!history[index]) return;
  const ta = $("#transcript");
  ta.value = history[index].transcript;
  closeHistory();
  ta.focus();
  toast("Transcript loaded from history.");
}


// ── Escape HTML ──────────────────────────────────────────────
function esc(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}


// ── Init ─────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initTabs();
  initForm();

  $("#themeBtn")?.addEventListener("click", toggleTheme);
  $("#historyBtn")?.addEventListener("click", openHistory);
});
