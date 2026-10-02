const API_BASE = localStorage.getItem("RAMAZ_API_BASE") || "http://127.0.0.1:8000";

const AGENTS = [
  { id: "ASSISTANT-NDS", name: "معاون", type: "Assistant" },
  { id: "TECH-MANAGER", name: "رئیس تکنیکال", type: "Manager" },
  { id: "FUND-MANAGER", name: "رئیس فاندامنتال", type: "Manager" },
  { id: "TECH-NDS-01", name: "NDS Worker", type: "Employee", dept: "technical" },
  { id: "TECH-ICT-01", name: "ICT Worker", type: "Employee", dept: "technical" },
  { id: "TECH-RTM-01", name: "RTM Worker", type: "Employee", dept: "technical" },
  { id: "TECH-SD-01", name: "Supply Demand Worker", type: "Employee", dept: "technical" },
  { id: "TECH-ASH-01", name: "Ash Trigger Worker", type: "Employee", dept: "technical" },
  { id: "FUND-NEWS-01", name: "News Worker", type: "Employee", dept: "fundamental" },
  { id: "FUND-X-01", name: "X Worker", type: "Employee", dept: "fundamental" },
  { id: "FUND-YT-01", name: "YouTube Worker", type: "Employee", dept: "fundamental" },
  { id: "FUND-TG-01", name: "Telegram Worker", type: "Employee", dept: "fundamental" },
];

// Cache for UI lists (source of truth = backend)
const agentMemory = {};
AGENTS.forEach((a) => {
  agentMemory[a.id] = { training: [], experience: [], discoveries: [], exams: [] };
});

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res.text();
}

function setStatus(ok, text) {
  const el = document.getElementById("systemStatus");
  if (!el) return;
  el.textContent = text;
  el.className = "status-badge " + (ok ? "ok" : "err");
}

// Tabs
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
  });
});

document.querySelectorAll(".sub-tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".sub-tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".dept-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`dept-${btn.dataset.dept}`).classList.add("active");
  });
});

function trainingMiniUI(agentId) {
  return `
    <div class="training-box">
      <h3 style="font-size:13px;color:#c7d2fe">آموزش این نقش</h3>
      <input type="text" placeholder="عنوان آموزش" id="title-${agentId}" />
      <textarea rows="3" placeholder="متن آموزش" id="content-${agentId}"></textarea>
      <input type="file" id="file-${agentId}" accept=".pdf,image/*,video/*" />
      <button class="btn" onclick="saveTrainingFor('${agentId}')">ذخیره آموزش در Backend</button>
      <div class="folder-list" id="list-train-${agentId}"><div class="empty">آموزشی ثبت نشده</div></div>

      <h3 style="font-size:13px;color:#c7d2fe;margin-top:8px">امتحان (فقط ارزیابی)</h3>
      <textarea rows="2" placeholder="سؤال امتحان" id="q-${agentId}"></textarea>
      <input type="number" min="0" max="1" step="0.1" value="0.8" id="score-${agentId}" />
      <input type="text" placeholder="بازخورد" id="fb-${agentId}" />
      <button class="btn" onclick="examFor('${agentId}')">ثبت نتیجه امتحان</button>
      <div class="folder-list" id="list-exam-${agentId}"><div class="empty">امتحانی ثبت نشده</div></div>

      <h3 style="font-size:13px;color:#c7d2fe;margin-top:8px">انتقال به تجربه (فقط کاربر)</h3>
      <select id="promote-train-${agentId}"></select>
      <button class="btn primary" onclick="promoteTraining('${agentId}')">تأیید کاربر: انتقال آموزش به تجربه</button>

      <h3 style="font-size:13px;color:#c7d2fe;margin-top:8px">کشف‌های پیشنهادی ایجنت</h3>
      <div class="folder-list" id="list-disc-${agentId}"><div class="empty">کشف معلقی نیست</div></div>

      <h3 style="font-size:13px;color:#c7d2fe;margin-top:8px">تجربه‌ها</h3>
      <div class="folder-list" id="list-exp-${agentId}"><div class="empty">تجربه‌ای ثبت نشده</div></div>

      <h3 style="font-size:13px;color:#c7d2fe;margin-top:8px">مدل / API فعال</h3>
      <div class="folder-list" id="list-models-${agentId}"><div class="empty">مدلی متصل نیست</div></div>
      <input type="text" id="model-name-${agentId}" placeholder="نام مدل مثلا OpenAI-A" />
      <input type="text" id="model-provider-${agentId}" placeholder="provider مثلا openai" />
      <input type="text" id="model-id-${agentId}" placeholder="model_id مثلا gpt-4.1" />
      <button class="btn" onclick="attachModelFor('${agentId}')">اتصال مدل به Backend</button>
    </div>
  `;
}

function employeeCard(agent) {
  return `
    <div class="employee-card">
      <h4>${agent.name} <span style="color:#9aaccb;font-size:12px">(${agent.id})</span></h4>
      <div class="mini-card" style="margin-bottom:10px">
        <h3>گزارش‌های کارمند</h3>
        <div class="folder-list"><div class="empty">خالی</div></div>
      </div>
      <div class="mini-card" style="margin-bottom:10px">
        <h3>گزارش لحظه‌ای کارمند</h3>
        <div class="live-slide small">
          <div class="slide-label">LIVE</div>
          <div class="slide-body">در انتظار ورودی تصویری / منبع...</div>
        </div>
      </div>
      ${trainingMiniUI(agent.id)}
    </div>
  `;
}

function renderEmployees() {
  const tech = AGENTS.filter((a) => a.dept === "technical");
  const fund = AGENTS.filter((a) => a.dept === "fundamental");
  document.getElementById("technicalEmployees").innerHTML = tech.map(employeeCard).join("");
  document.getElementById("fundamentalEmployees").innerHTML = fund.map(employeeCard).join("");

  [
    ["train-ASSISTANT-NDS", "ASSISTANT-NDS"],
    ["train-TECH-MANAGER", "TECH-MANAGER"],
    ["train-FUND-MANAGER", "FUND-MANAGER"],
  ].forEach(([el, id]) => {
    const node = document.getElementById(el);
    if (node) node.innerHTML = trainingMiniUI(id);
  });
}

function fillAgentSelects() {
  const opts = AGENTS.map((a) => `<option value="${a.id}">${a.name} (${a.id})</option>`).join("");
  ["trainingAgentSelect", "examAgentSelect", "memoryAgentSelect"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = opts;
  });
}

function renderLists(agentId) {
  const mem = agentMemory[agentId] || { training: [], experience: [], discoveries: [], exams: [], models: [] };

  const tList = document.getElementById(`list-train-${agentId}`);
  if (tList) {
    tList.innerHTML = mem.training.length
      ? mem.training.map((t) => `<div class="folder-item"><span class="tag">TRAIN</span>${t.title || t.id} <small>(${t.id})</small></div>`).join("")
      : `<div class="empty">آموزشی ثبت نشده</div>`;
  }

  const promote = document.getElementById(`promote-train-${agentId}`);
  if (promote) {
    promote.innerHTML = mem.training.length
      ? mem.training.map((t) => `<option value="${t.id}">${t.title || t.id}</option>`).join("")
      : `<option value="">آموزشی نیست</option>`;
  }

  const examList = document.getElementById(`list-exam-${agentId}`);
  if (examList) {
    examList.innerHTML = mem.exams.length
      ? mem.exams.map((e) => `<div class="folder-item"><span class="tag warn">EXAM</span>نمره ${e.score} — ${e.question || ""}</div>`).join("")
      : `<div class="empty">امتحانی ثبت نشده</div>`;
  }

  const dList = document.getElementById(`list-disc-${agentId}`);
  if (dList) {
    const pending = (mem.discoveries || []).filter((d) => d.status === "PENDING_USER_APPROVAL");
    dList.innerHTML = pending.length
      ? pending.map((d) => `
          <div class="folder-item">
            <div><span class="tag warn">DISCOVERY</span>${typeof d.content === "string" ? d.content : JSON.stringify(d.content)}</div>
            <button class="btn" onclick="approveDiscovery('${agentId}','${d.id}')">تأیید کاربر → تجربه</button>
            <button class="btn" onclick="rejectDiscovery('${agentId}','${d.id}')">رد کشف</button>
          </div>`).join("")
      : `<div class="empty">کشف معلقی نیست</div>`;
  }

  const eList = document.getElementById(`list-exp-${agentId}`);
  if (eList) {
    eList.innerHTML = mem.experience.length
      ? mem.experience.map((e) => `<div class="folder-item"><span class="tag ok">EXP</span>${e.id}</div>`).join("")
      : `<div class="empty">تجربه‌ای ثبت نشده</div>`;
  }

  const mList = document.getElementById(`list-models-${agentId}`);
  if (mList) {
    const models = mem.models || [];
    mList.innerHTML = models.length
      ? models.map((m) => `
          <div class="folder-item">
            <span class="tag ${m.is_active ? "ok" : ""}">${m.is_active ? "ACTIVE" : m.status || "MODEL"}</span>
            ${m.name || m.model_id} (${m.provider})
            ${!m.is_active ? `<button class="btn" onclick="switchModelFor('${agentId}','${m.id}')">فعال کردن</button>` : ""}
          </div>`).join("")
      : `<div class="empty">مدلی متصل نیست</div>`;
  }
}

async function refreshAgentData(agentId) {
  try {
    const [training, experience, discoveries, modelsResp] = await Promise.all([
      api(`/training/${agentId}`).catch(() => []),
      api(`/experience/${agentId}`).catch(() => []),
      api(`/discoveries/${agentId}/pending`).catch(() => []),
      api(`/models/${agentId}`).catch(() => ({ models: [] })),
    ]);

    agentMemory[agentId] = {
      training: training || [],
      experience: experience || [],
      discoveries: discoveries || [],
      exams: agentMemory[agentId]?.exams || [],
      models: modelsResp.models || [],
    };
    renderLists(agentId);
  } catch (e) {
    console.error(e);
  }
}

async function refreshAllAgents() {
  for (const a of AGENTS) {
    await refreshAgentData(a.id);
  }
  await renderAgentMemory();
}

async function loadSystem() {
  try {
    const data = await api("/");
    setStatus(true, `Backend: ${data.status || "ok"}`);
  } catch (e) {
    setStatus(false, "Backend قطع است");
  }
}

async function saveTrainingFor(agentId) {
  const title = (document.getElementById(`title-${agentId}`)?.value || "").trim() || "آموزش بدون عنوان";
  const content = (document.getElementById(`content-${agentId}`)?.value || "").trim();
  const fileName = document.getElementById(`file-${agentId}`)?.files?.[0]?.name || null;
  if (!content && !fileName) return alert("متن آموزش یا فایل لازم است.");

  try {
    await api("/training", {
      method: "POST",
      body: JSON.stringify({
        agent_id: agentId,
        title,
        content: content || `[FILE] ${fileName}`,
        source: "USER",
        tags: fileName ? ["file", fileName] : ["manual"],
      }),
    });
    await refreshAgentData(agentId);
    await renderAgentMemory();
    alert("آموزش در Backend ذخیره شد.");
  } catch (e) {
    alert("خطا در ذخیره آموزش: " + e.message);
  }
}

function examFor(agentId) {
  const question = (document.getElementById(`q-${agentId}`)?.value || "").trim();
  const score = Number(document.getElementById(`score-${agentId}`)?.value || 0);
  const feedback = (document.getElementById(`fb-${agentId}`)?.value || "").trim();
  if (!question) return alert("سؤال امتحان لازم است.");

  // Exam remains local evaluation record; promotion is explicit user action via backend
  agentMemory[agentId].exams = agentMemory[agentId].exams || [];
  agentMemory[agentId].exams.push({
    id: `EXAM-${Date.now()}`,
    question,
    score,
    feedback,
    created_at: new Date().toISOString(),
  });
  renderLists(agentId);
  alert("نتیجه امتحان ثبت شد. انتقال به تجربه فقط با تأیید جداگانه کاربر انجام می‌شود.");
}

async function promoteTraining(agentId) {
  const trainingId = document.getElementById(`promote-train-${agentId}`)?.value;
  if (!trainingId) return alert("آموزشی برای انتقال انتخاب نشده است.");

  const ok = confirm("آیا تأیید می‌کنید این آموزش به تجربه منتقل شود؟");
  if (!ok) return;

  try {
    await api("/experience/from-training", {
      method: "POST",
      body: JSON.stringify({
        agent_id: agentId,
        training_id: trainingId,
        approved_by: "USER",
      }),
    });
    await refreshAgentData(agentId);
    await renderAgentMemory();
    alert("با تأیید کاربر به تجربه منتقل شد.");
  } catch (e) {
    alert("خطا در انتقال: " + e.message);
  }
}

async function approveDiscovery(agentId, discoveryId) {
  const ok = confirm("تأیید می‌کنید این کشف به تجربه منتقل شود؟");
  if (!ok) return;
  try {
    await api("/discoveries/approve", {
      method: "POST",
      body: JSON.stringify({
        agent_id: agentId,
        discovery_id: discoveryId,
        decided_by: "USER",
      }),
    });
    await refreshAgentData(agentId);
    await renderAgentMemory();
  } catch (e) {
    alert("خطا: " + e.message);
  }
}

async function rejectDiscovery(agentId, discoveryId) {
  try {
    await api("/discoveries/reject", {
      method: "POST",
      body: JSON.stringify({
        agent_id: agentId,
        discovery_id: discoveryId,
        reason: "Rejected by USER",
        decided_by: "USER",
      }),
    });
    await refreshAgentData(agentId);
  } catch (e) {
    alert("خطا: " + e.message);
  }
}

async function attachModelFor(agentId) {
  const name = (document.getElementById(`model-name-${agentId}`)?.value || "").trim() || "model";
  const provider = (document.getElementById(`model-provider-${agentId}`)?.value || "").trim() || "openai";
  const modelId = (document.getElementById(`model-id-${agentId}`)?.value || "").trim() || "gpt-4.1";

  try {
    await api("/models/attach", {
      method: "POST",
      body: JSON.stringify({
        agent_id: agentId,
        name,
        provider,
        model_id: modelId,
        role: "primary",
        set_active: true,
      }),
    });
    await refreshAgentData(agentId);
    alert("مدل به Backend متصل و ذخیره شد.");
  } catch (e) {
    alert("خطا در اتصال مدل: " + e.message);
  }
}

async function switchModelFor(agentId, modelRefId) {
  try {
    await api("/models/switch", {
      method: "POST",
      body: JSON.stringify({ agent_id: agentId, model_ref_id: modelRefId }),
    });
    await refreshAgentData(agentId);
  } catch (e) {
    alert("خطا در تعویض مدل: " + e.message);
  }
}

async function saveTraining() {
  const agentId = document.getElementById("trainingAgentSelect").value;
  const title = document.getElementById("trainingTitle").value.trim() || "آموزش بدون عنوان";
  const content = document.getElementById("trainingContent").value.trim();
  const sourceType = document.getElementById("trainingSourceType").value;
  const fileName = document.getElementById("trainingFile").files?.[0]?.name || null;
  if (!content && !fileName) return alert("متن یا فایل آموزش لازم است.");

  try {
    await api("/training", {
      method: "POST",
      body: JSON.stringify({
        agent_id: agentId,
        title,
        content: content || `[FILE] ${fileName}`,
        source: sourceType,
        tags: fileName ? [sourceType.toLowerCase(), fileName] : [sourceType.toLowerCase()],
      }),
    });
    await refreshAgentData(agentId);
    await renderAgentMemory();
    alert("آموزش در Backend ذخیره شد.");
  } catch (e) {
    alert("خطا: " + e.message);
  }
}

function submitExam() {
  const agentId = document.getElementById("examAgentSelect").value;
  const question = document.getElementById("examQuestion").value.trim();
  const expected = document.getElementById("examExpected").value.trim();
  const score = Number(document.getElementById("examScore").value || 0);
  const feedback = document.getElementById("examFeedback").value.trim();
  const log = document.getElementById("examLog");
  if (!question) return alert("سؤال امتحان لازم است.");

  const record = {
    agent_id: agentId,
    question,
    expected,
    score,
    feedback,
    auto_transferred: false,
    note: "Transfer to experience requires explicit USER approval via promote endpoint",
    created_at: new Date().toISOString(),
  };

  agentMemory[agentId].exams = agentMemory[agentId].exams || [];
  agentMemory[agentId].exams.push(record);
  log.textContent = JSON.stringify(record, null, 2);
  renderLists(agentId);
}

async function renderAgentMemory() {
  const agentId = document.getElementById("memoryAgentSelect")?.value || AGENTS[0].id;
  const tBox = document.getElementById("memoryTrainingList");
  const eBox = document.getElementById("memoryExperienceList");
  if (!tBox || !eBox) return;

  try {
    const [training, experience] = await Promise.all([
      api(`/training/${agentId}`),
      api(`/experience/${agentId}`),
    ]);

    agentMemory[agentId].training = training || [];
    agentMemory[agentId].experience = experience || [];

    tBox.innerHTML = (training || []).length
      ? training.map((t) => `<div class="folder-item"><span class="tag">${t.source || "USER"}</span>${t.title || t.id}</div>`).join("")
      : `<div class="empty">خالی</div>`;

    eBox.innerHTML = (experience || []).length
      ? experience.map((e) => `<div class="folder-item"><span class="tag ok">EXP</span>${e.id}</div>`).join("")
      : `<div class="empty">خالی</div>`;
  } catch (e) {
    tBox.innerHTML = `<div class="empty">Backend قطع است</div>`;
    eBox.innerHTML = `<div class="empty">Backend قطع است</div>`;
  }
}

async function submitVisualMission() {
  const input = document.getElementById("missionMediaInput");
  const note = document.getElementById("missionSourceNote").value.trim();
  const log = document.getElementById("missionIntakeLog");
  const preview = document.getElementById("missionMediaPreview");
  preview.innerHTML = "";
  const files = [...input.files];

  if (!files.length && !note) {
    log.textContent = "هیچ ورودی دیداری یا منبعی ثبت نشد.";
    return;
  }

  // preview locally
  files.forEach((file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = document.createElement("img");
      img.src = e.target.result;
      preview.appendChild(img);
    };
    reader.readAsDataURL(file);
  });

  const payload = {
    source_note: note || null,
    files: files.map((f) => ({ name: f.name, type: f.type, size: f.size })),
    captured_by: "USER",
    source_type: "SCREENSHOT",
    meta: {},
  };

  try {
    const result = await api("/missions/visual", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    log.textContent = JSON.stringify(result, null, 2);

    const outputs = document.getElementById("finalOutputs");
    if (outputs.querySelector(".empty")) outputs.innerHTML = "";
    const item = document.createElement("div");
    item.className = "folder-item";
    item.textContent = `ورودی دیداری Backend — ${result.intake?.intake_id || ""} — فایل‌ها: ${files.length}`;
    outputs.prepend(item);
  } catch (e) {
    log.textContent = "خطا در ارسال به Backend:\n" + e.message;
  }
}

// init
renderEmployees();
fillAgentSelects();
loadSystem();
refreshAllAgents();
