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

// Local memory store for UI (mirrors future backend memory)
const agentMemory = {};
AGENTS.forEach((a) => {
  agentMemory[a.id] = { training: [], experience: [] };
});

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
      <button class="btn" onclick="saveTrainingFor('${agentId}')">ذخیره آموزش</button>
      <div class="folder-list" id="list-train-${agentId}"><div class="empty">آموزشی ثبت نشده</div></div>

      <h3 style="font-size:13px;color:#c7d2fe;margin-top:8px">امتحان</h3>
      <textarea rows="2" placeholder="سؤال امتحان" id="q-${agentId}"></textarea>
      <input type="number" min="0" max="1" step="0.1" value="0.8" id="score-${agentId}" />
      <input type="text" placeholder="بازخورد" id="fb-${agentId}" />
      <button class="btn primary" onclick="examFor('${agentId}')">ثبت امتحان</button>
      <div class="folder-list" id="list-exp-${agentId}"><div class="empty">تجربه‌ای ثبت نشده</div></div>
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

  // managers + assistant training boxes
  const map = [
    ["train-ASSISTANT-NDS", "ASSISTANT-NDS"],
    ["train-TECH-MANAGER", "TECH-MANAGER"],
    ["train-FUND-MANAGER", "FUND-MANAGER"],
  ];
  map.forEach(([el, id]) => {
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
  const mem = agentMemory[agentId];

  const tList = document.getElementById(`list-train-${agentId}`);
  if (tList) {
    tList.innerHTML = mem.training.length
      ? mem.training.map((t) => `<div class="folder-item"><span class="tag">TRAIN</span>${t.title}</div>`).join("")
      : `<div class="empty">آموزشی ثبت نشده</div>`;
  }

  const eList = document.getElementById(`list-exp-${agentId}`);
  if (eList) {
    eList.innerHTML = mem.experience.length
      ? mem.experience.map((e) => `<div class="folder-item"><span class="tag ok">EXP</span>نمره ${e.score} — ${e.feedback || ""}</div>`).join("")
      : `<div class="empty">تجربه‌ای ثبت نشده</div>`;
  }
}

function saveTrainingFor(agentId) {
  const title = (document.getElementById(`title-${agentId}`)?.value || "").trim() || "آموزش بدون عنوان";
  const content = (document.getElementById(`content-${agentId}`)?.value || "").trim();
  const fileInput = document.getElementById(`file-${agentId}`);
  const fileName = fileInput?.files?.[0]?.name || null;

  if (!content && !fileName) {
    alert("متن آموزش یا فایل لازم است.");
    return;
  }

  agentMemory[agentId].training.push({
    id: `TRAIN-${Date.now()}`,
    title,
    content,
    fileName,
    source: "USER",
    created_at: new Date().toISOString(),
  });

  renderLists(agentId);
  renderAgentMemory();
}

function examFor(agentId) {
  const question = (document.getElementById(`q-${agentId}`)?.value || "").trim();
  const score = Number(document.getElementById(`score-${agentId}`)?.value || 0);
  const feedback = (document.getElementById(`fb-${agentId}`)?.value || "").trim();

  if (!question) {
    alert("سؤال امتحان لازم است.");
    return;
  }

  const passed = score >= 0.7;
  const exp = {
    id: `EXP-${Date.now()}`,
    question,
    score,
    feedback,
    passed,
    created_at: new Date().toISOString(),
    from_training_count: agentMemory[agentId].training.length,
  };

  // Only transfer to experience if acceptable
  if (passed) {
    agentMemory[agentId].experience.push(exp);
  }

  renderLists(agentId);
  renderAgentMemory();

  alert(passed
    ? "قبول شد و به حافظه تجربه منتقل شد."
    : "نمره کافی نبود. به تجربه منتقل نشد.");
}

function saveTraining() {
  const agentId = document.getElementById("trainingAgentSelect").value;
  const title = document.getElementById("trainingTitle").value.trim() || "آموزش بدون عنوان";
  const content = document.getElementById("trainingContent").value.trim();
  const sourceType = document.getElementById("trainingSourceType").value;
  const fileName = document.getElementById("trainingFile").files?.[0]?.name || null;

  if (!content && !fileName) {
    alert("متن یا فایل آموزش لازم است.");
    return;
  }

  agentMemory[agentId].training.push({
    id: `TRAIN-${Date.now()}`,
    title,
    content,
    fileName,
    source: sourceType,
    created_at: new Date().toISOString(),
  });

  renderLists(agentId);
  renderAgentMemory();
  alert("آموزش در حافظه ایجنت ذخیره شد.");
}

function submitExam() {
  const agentId = document.getElementById("examAgentSelect").value;
  const question = document.getElementById("examQuestion").value.trim();
  const expected = document.getElementById("examExpected").value.trim();
  const score = Number(document.getElementById("examScore").value || 0);
  const feedback = document.getElementById("examFeedback").value.trim();
  const log = document.getElementById("examLog");

  if (!question) {
    alert("سؤال امتحان لازم است.");
    return;
  }

  const passed = score >= 0.7;
  const record = {
    agent_id: agentId,
    question,
    expected,
    score,
    feedback,
    passed,
    transferred_to_experience: passed,
    created_at: new Date().toISOString(),
  };

  if (passed) {
    agentMemory[agentId].experience.push({
      id: `EXP-${Date.now()}`,
      question,
      expected,
      score,
      feedback,
      passed: true,
      created_at: record.created_at,
    });
  }

  log.textContent = JSON.stringify(record, null, 2);
  renderLists(agentId);
  renderAgentMemory();
}

function renderAgentMemory() {
  const agentId = document.getElementById("memoryAgentSelect")?.value || AGENTS[0].id;
  const mem = agentMemory[agentId];

  const tBox = document.getElementById("memoryTrainingList");
  const eBox = document.getElementById("memoryExperienceList");
  if (!tBox || !eBox) return;

  tBox.innerHTML = mem.training.length
    ? mem.training.map((t) => `<div class="folder-item"><span class="tag">${t.source || "USER"}</span>${t.title}</div>`).join("")
    : `<div class="empty">خالی</div>`;

  eBox.innerHTML = mem.experience.length
    ? mem.experience.map((e) => `<div class="folder-item"><span class="tag ok">n=${e.score}</span>${e.question}</div>`).join("")
    : `<div class="empty">خالی</div>`;
}

function submitVisualMission() {
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
    type: "VISUAL_MISSION_INPUT",
    source_note: note || null,
    files: files.map((f) => ({ name: f.name, type: f.type, size: f.size })),
    created_at: new Date().toISOString(),
  };
  log.textContent = JSON.stringify(payload, null, 2);

  const outputs = document.getElementById("finalOutputs");
  if (outputs.querySelector(".empty")) outputs.innerHTML = "";
  const item = document.createElement("div");
  item.className = "folder-item";
  item.textContent = `ورودی دیداری — فایل‌ها: ${files.length} — منبع: ${note || "نامشخص"}`;
  outputs.prepend(item);
}

renderEmployees();
fillAgentSelects();
renderAgentMemory();
