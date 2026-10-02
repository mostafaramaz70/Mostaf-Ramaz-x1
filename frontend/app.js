const API_BASE = "http://127.0.0.1:8000";

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

function setStatus(ok, text) {
  const el = document.getElementById("systemStatus");
  el.textContent = text;
  el.className = "status-badge " + (ok ? "ok" : "err");
}

async function loadSystem() {
  const box = document.getElementById("systemInfo");
  try {
    const data = await api("/");
    box.innerHTML = `
      <p><strong>سیستم:</strong> ${data.system}</p>
      <p><strong>نسخه:</strong> ${data.version}</p>
      <p><strong>وضعیت Runtime:</strong> ${data.status}</p>
      <p><strong>زمان:</strong> ${data.timestamp}</p>
    `;
    setStatus(true, `وضعیت: ${data.status}`);
  } catch (e) {
    box.innerHTML = `<p style="color:#fca5a5">اتصال برقرار نشد. Backend را اجرا کنید.</p><p>${e.message}</p>`;
    setStatus(false, "Backend قطع است");
  }
}

async function loadAgents() {
  const box = document.getElementById("agentsList");
  try {
    const agents = await api("/agents");
    if (!agents.length) {
      box.innerHTML = "<p>Agentی ثبت نشده است.</p>";
      return;
    }
    box.innerHTML = agents.map(a => `
      <div class="agent-item">
        <strong>${a.agent_id}</strong>
        <span class="tag ${String(a.status || '').toLowerCase()}">${a.status || '-'}</span>
        <div style="color:#9aaccb;font-size:12px;margin-top:4px">
          ${a.name || ''} | ${a.agent_type || ''} | ${a.department || ''}
        </div>
      </div>
    `).join("");
  } catch (e) {
    box.innerHTML = `<p style="color:#fca5a5">خطا در دریافت Agentها</p>`;
  }
}

async function loadMissions() {
  const box = document.getElementById("missionsList");
  try {
    const missions = await api("/missions");
    if (!missions.length) {
      box.innerHTML = "<p>هنوز Missionی ثبت نشده است.</p>";
      return;
    }
    box.innerHTML = missions.slice().reverse().map(m => `
      <div class="mission-item">
        <strong>${m.mission_id}</strong>
        <span class="tag">${m.status || '-'}</span>
        <div style="color:#9aaccb;font-size:12px;margin-top:4px">
          ${m.mission_objective || ''}
        </div>
      </div>
    `).join("");
  } catch (e) {
    box.innerHTML = `<p style="color:#fca5a5">خطا در دریافت Missionها</p>`;
  }
}

async function runMission(event) {
  event.preventDefault();
  const objective = document.getElementById("objective").value.trim();
  const symbol = document.getElementById("symbol").value.trim() || "EURUSD";
  const priority = document.getElementById("priority").value;
  const resultBox = document.getElementById("missionResult");

  resultBox.textContent = "در حال اجرای Mission...";

  try {
    const data = await api("/missions/run", {
      method: "POST",
      body: JSON.stringify({
        objective,
        priority,
        mission_input: {
          symbol,
          timeframe: "M1",
          context: "Submitted from Ramaz X1 Frontend"
        },
        success_criteria: "Produce valid analysis report"
      })
    });

    resultBox.textContent = JSON.stringify(data, null, 2);
    await loadMissions();
  } catch (e) {
    resultBox.textContent = "خطا در اجرای Mission:\n" + e.message;
  }
}

// Initial load
loadSystem();
loadAgents();
loadMissions();
