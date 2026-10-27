const $ = (s) => document.querySelector(s);
const JOBS = [];

const CHIPS = [
  "hi",
  "Employed at Meru Labs, not serving notice yet",
  "30 days on paper, buyout possible",
  "Current 24 LPA fixed, expected 32 LPA",
  "Hybrid Bengaluru is fine, no relocation needed",
];

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => showTab(btn.dataset.tab));
});

function showTab(id) {
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("on", b.dataset.tab === id));
  document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("on", p.id === id));
  if (id === "dash") loadDash();
  if (id === "screen") {
    loadSlots();
    loadChatHistory();
  }
}

async function api(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const j = await res.json();
      msg = j.detail || JSON.stringify(j);
    } catch (_) {}
    throw new Error(msg);
  }
  return res.json();
}

async function boot() {
  try {
    const h = await api("/api/health");
    const labels = {
      anthropic: "Claude (Anthropic)",
      gemini: "Gemini (free-tier key)",
      groq: "Groq Llama (free-tier key)",
      ollama: "Ollama (local)",
      heuristic: "Heuristic — add Gemini/Groq/Ollama/Claude in .env",
    };
    $("#health").textContent = labels[h.provider] || h.provider || "Unknown engine";
    $("#health").classList.toggle("ok", Boolean(h.llm));
  } catch (e) {
    $("#health").textContent = "API offline — start uvicorn on port 8000";
  }
  renderChips();
  await refreshCandidates();
  await loadJobs();
  await loadDash();
}

function renderChips() {
  $("#chips").innerHTML = CHIPS.map(
    (t) => `<button type="button" class="chip" data-msg="${encodeURIComponent(t)}">${t}</button>`
  ).join("");
  $("#chips").addEventListener("click", (ev) => {
    const btn = ev.target.closest(".chip");
    if (!btn) return;
    sendChat(decodeURIComponent(btn.dataset.msg));
  });
}

async function refreshCandidates() {
  const status = $("#statusFilter").value;
  const searchTerm = ($("#candSearch")?.value || "").toLowerCase().trim();
  const q = status ? `?status=${encodeURIComponent(status)}` : "";
  const data = await api(`/api/candidates${q}`);
  const rows = data.candidates.filter(c => !searchTerm || (c.full_name && c.full_name.toLowerCase().includes(searchTerm)) || (c.skills && c.skills.toLowerCase().includes(searchTerm)))
    .map(
      (c) => `<tr data-cid="${c.id}">
        <td>${c.id}</td>
        <td>${esc(c.full_name)}</td>
        <td>${esc(c.current_location)}</td>
        <td>${esc(c.source_channel)}</td>
        <td>${c.latest_score ?? "—"}</td>
        <td>${badge(c.latest_status)}</td>
      </tr>`
    )
    .join("");
  $("#candTable").innerHTML = `<table><thead><tr>
    <th>ID</th><th>Name</th><th>Location</th><th>Channel</th><th>Score</th><th>Status</th>
  </tr></thead><tbody>${rows || "<tr><td colspan=6>No candidates yet — ingest samples first</td></tr>"}</tbody></table>`;
  const sel = $("#chatCand");
  const keep = sel.value;
  sel.innerHTML = data.candidates
    .map((c) => `<option value="${c.id}">${c.id} · ${c.full_name || "unnamed"}</option>`)
    .join("");
  if (keep) sel.value = keep;
}

function esc(v) {
  if (v == null || v === "") return "—";
  return String(v)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function badge(status) {
  if (!status) return "—";
  const cls = status.includes("AI Fit") ? "fit" : "low";
  return `<span class="tag ${cls}">${esc(status)}</span>`;
}

$("#statusFilter").addEventListener("change", () => refreshCandidates().catch(() => {}));

$("#candTable").addEventListener("click", (ev) => {
  const tr = ev.target.closest("tr[data-cid]");
  if (!tr) return;
  $("#chatCand").value = tr.dataset.cid;
  showTab("screen");
});

$("#ingest").addEventListener("click", async () => {
  $("#ingestLog").textContent = "Parsing sample resumes…";
  try {
    const data = await api("/api/resumes/ingest-samples", { method: "POST" });
    $("#ingestLog").textContent = data.results
      .map((r) => `${r.file} → #${r.candidate_id} (${r.action})`)
      .join("\n");
    await refreshCandidates();
  } catch (e) {
    $("#ingestLog").textContent = e.message;
  }
});

$("#files").addEventListener("change", async (ev) => {
  const fd = new FormData();
  [...ev.target.files].forEach((f) => fd.append("files", f));
  $("#ingestLog").textContent = "Uploading…";
  try {
    const data = await api("/api/resumes/upload", { method: "POST", body: fd });
    $("#ingestLog").textContent = JSON.stringify(data.results, null, 2);
    await refreshCandidates();
  } catch (e) {
    $("#ingestLog").textContent = e.message;
  }
});

async function loadJobs() {
  const data = await api("/api/jobs");
  JOBS.splice(0, JOBS.length, ...data.jobs);
  $("#jobSelect").innerHTML = data.jobs
    .map((j) => `<option value="${j.id}">${esc(j.title)}</option>`)
    .join("");
  showJdPreview();
}

$("#jobSelect").addEventListener("change", showJdPreview);

function showJdPreview() {
  const job = JOBS.find((j) => String(j.id) === $("#jobSelect").value);
  $("#jdPreview").textContent = job ? (job.jd_text || "").slice(0, 700) : "";
}

$("#runScore").addEventListener("click", async () => {
  const job_id = Number($("#jobSelect").value);
  $("#scoreOut").innerHTML = "Scoring…";
  try {
    const data = await api("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_id }),
    });
    const names = Object.fromEntries(
      [...document.querySelectorAll("#chatCand option")].map((o) => [o.value, o.textContent])
    );
    const rows = data.scores
      .map(
        (s) => `<tr>
          <td>${esc(names[s.candidate_id] || s.candidate_id)}</td>
          <td>${s.fitment_score}</td>
          <td>${badge(s.status)}</td>
          <td>${esc(s.summary_bullets).replaceAll("\n", "<br>")}</td>
        </tr>`
      )
      .join("");
    $("#scoreOut").innerHTML = `<table><thead><tr><th>Candidate</th><th>Score</th><th>Status</th><th>Fitment</th></tr></thead><tbody>${rows}</tbody></table>`;
    await refreshCandidates();
  } catch (e) {
    $("#scoreOut").textContent = e.message;
  }
});

$("#chatCand").addEventListener("change", () => loadChatHistory());

async function loadChatHistory() {
  const cid = $("#chatCand").value;
  $("#chatBox").innerHTML = "";
  if (!cid) return;
  const data = await api(`/api/candidates/${cid}`);
  (data.chat || []).forEach((m) => addBubble(m.role === "user" ? "user" : "assistant", m.message));
}

$("#chatForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = $("#chatInput").value.trim();
  if (!message) return;
  $("#chatInput").value = "";
  await sendChat(message);
});

async function sendChat(message) {
  const cid = $("#chatCand").value;
  if (!cid) return;
  addBubble("user", message);
  try {
    const data = await api(`/api/chat/${cid}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    addBubble("assistant", data.reply);
    await loadSlots();
  } catch (err) {
    addBubble("assistant", err.message);
  }
}

function addBubble(role, text) {
  const el = document.createElement("div");
  el.className = `bubble ${role}`;
  el.textContent = text;
  $("#chatBox").appendChild(el);
  $("#chatBox").scrollTop = $("#chatBox").scrollHeight;
}

async function loadSlots() {
  const data = await api("/api/interviews");
  const cid = $("#chatCand").value;
  $("#slots").innerHTML = data.open_slots
    .map(
      (s) => `<button type="button" class="slot" data-slot="${s.id}">
        Book ${s.id}<br><span>${esc(s.label)} · ${esc(s.channel)}</span>
      </button>`
    )
    .join("") || "<p>No open slots</p>";
  const rows = data.interviews
    .map(
      (i) => `<tr>
        <td>${i.id}</td>
        <td>${esc(i.full_name || i.candidate_id)}</td>
        <td>${esc(i.slot_time)}</td>
        <td>${esc(i.confirmation_status)}</td>
        <td>
          <button type="button" class="tiny" data-iv="${i.id}" data-act="confirm">Confirm</button>
          <button type="button" class="tiny" data-iv="${i.id}" data-act="noshow">No-show</button>
        </td>
      </tr>`
    )
    .join("");
  $("#ivTable").innerHTML = `<table><thead><tr><th>ID</th><th>Candidate</th><th>Slot</th><th>Status</th><th></th></tr></thead><tbody>${rows}</tbody></table>`;
  const queued = (data.reminders || []).filter((r) => r.status === "queued").length;
  const sent = (data.reminders || []).filter((r) => r.status === "sent").length;
  if (!$("#reminderLog").dataset.locked) {
    $("#reminderLog").textContent = `Reminders: ${queued} queued (T-24h / T-2h / T-15m), ${sent} sent. Mock channel only.`;
  }
  $("#slots").dataset.cid = cid;
}

$("#slots").addEventListener("click", async (ev) => {
  const btn = ev.target.closest(".slot");
  if (!btn) return;
  const cid = $("#chatCand").value;
  if (!cid) return;
  try {
    await api(`/api/interviews/book/${cid}?slot_id=${encodeURIComponent(btn.dataset.slot)}`, {
      method: "POST",
    });
    addBubble("assistant", `Booked ${btn.dataset.slot}. Status: Scheduled. T-24h / T-2h / T-15m reminders queued locally.`);
    await loadSlots();
  } catch (e) {
    addBubble("assistant", e.message);
  }
});

$("#ivTable").addEventListener("click", async (ev) => {
  const btn = ev.target.closest("button[data-iv]");
  if (!btn) return;
  try {
    await api(`/api/interviews/confirm/${btn.dataset.iv}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: btn.dataset.act }),
    });
    await loadSlots();
  } catch (e) {
    alert(e.message);
  }
});

$("#btnReminders").addEventListener("click", async () => {
  try {
    const data = await api("/api/reminders/dispatch", { method: "POST" });
    $("#reminderLog").dataset.locked = "1";
    $("#reminderLog").textContent = `Marked ${data.sent} reminder(s) sent. Real Meta WhatsApp would fire here.`;
    await loadSlots();
    await loadDash();
  } catch (e) {
    $("#reminderLog").textContent = e.message;
  }
});

$("#btnDossier").addEventListener("click", async () => {
  const cid = $("#chatCand").value;
  if (!cid) return;
  const job_id = $("#jobSelect").value;
  const q = job_id ? `?job_id=${job_id}` : "";
  const data = await api(`/api/candidates/${cid}/dossier${q}`);
  $("#dossier").hidden = false;
  $("#dossier").textContent = data.markdown;
});

async function loadDash() {
  const d = await api("/api/dashboard/summary");
  $("#kpis").innerHTML = [
    ["Sourced", d.sourced],
    ["AI Fit", d.qualified],
    ["Avg score", d.average_fitment_score],
    ["Interviews", d.interviews],
    ["Reminders queued", (d.reminders && d.reminders.queued) || 0],
    ["TTF days (mock)", d.avg_time_to_fill_days],
  ]
    .map(([l, n]) => `<div class="kpi"><div class="n">${n}</div><div class="l">${l}</div></div>`)
    .join("");
  $("#funnel").innerHTML =
    bars("By status", d.by_status) +
    bars("By channel", d.by_channel) +
    bars("Interview pipeline", d.interview_pipeline) +
    recruiterTable(d.activity_to_output);
}

function bars(title, obj) {
  const entries = Object.entries(obj || {});
  if (!entries.length) return `<h3>${title}</h3><p class="muted">No data yet</p>`;
  const max = Math.max(...entries.map(([, n]) => n), 1);
  const rows = entries
    .map(
      ([k, n]) => `<div class="bar"><span>${esc(k)} (${n})</span><i style="width:${(n / max) * 100}%"></i></div>`
    )
    .join("");
  return `<h3>${title}</h3>${rows}`;
}

function recruiterTable(rows) {
  if (!rows || !rows.length) return "";
  const body = rows
    .map(
      (r) => `<tr><td>${esc(r.recruiter_name)}</td><td>${r.login_hours}</td><td>${r.active_hours}</td>
      <td>${r.sourced}</td><td>${r.submitted}</td><td>${(r.flags || []).join("; ") || "—"}</td></tr>`
    )
    .join("");
  return `<h3>Activity-to-output (mocked Kredily + TeamLogger + CEIPAL)</h3>
    <table><thead><tr><th>Recruiter</th><th>Login h</th><th>Active h</th><th>Sourced</th><th>Submitted</th><th>Flags</th></tr></thead>
    <tbody>${body}</tbody></table>`;
}

boot();

$("#candSearch")?.addEventListener("input", () => refreshCandidates());

let sortKey = "id";
let sortAsc = true;
function sortTable(key) {
  if (sortKey === key) sortAsc = !sortAsc;
  else { sortKey = key; sortAsc = true; }
  refreshCandidates();
}
