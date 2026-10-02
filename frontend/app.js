const technicalWorkers = [
  { id: "TECH-NDS-01", name: "NDS Worker" },
  { id: "TECH-ICT-01", name: "ICT Worker" },
  { id: "TECH-RTM-01", name: "RTM Worker" },
  { id: "TECH-SD-01", name: "Supply Demand Worker" },
  { id: "TECH-ASH-01", name: "Ash Trigger Worker" },
];

const fundamentalWorkers = [
  { id: "FUND-NEWS-01", name: "News Worker" },
  { id: "FUND-X-01", name: "X Worker" },
  { id: "FUND-YT-01", name: "YouTube Worker" },
  { id: "FUND-TG-01", name: "Telegram Worker" },
];

// Tabs
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
  });
});

// Department sub-tabs
document.querySelectorAll(".sub-tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".sub-tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".dept-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`dept-${btn.dataset.dept}`).classList.add("active");
  });
});

function employeeCard(worker) {
  return `
    <div class="employee-card">
      <h4>${worker.name} <span style="color:#9aaccb;font-size:12px">(${worker.id})</span></h4>

      <div class="mini-card" style="margin-bottom:10px">
        <h3>گزارش‌های کارمند</h3>
        <div class="folder-list">
          <div class="empty">پوشه گزارش‌ها خالی است</div>
        </div>
      </div>

      <div class="mini-card" style="margin-bottom:10px">
        <h3>گزارش لحظه‌ای کارمند</h3>
        <div class="live-slide small">
          <div class="slide-label">LIVE</div>
          <div class="slide-body">در انتظار ورودی تصویری / منبع...</div>
        </div>
      </div>

      <div class="mini-card">
        <h3>ورودی دیداری</h3>
        <input type="file" accept="image/*" multiple onchange="previewInline(this)" />
        <div class="media-preview"></div>
      </div>
    </div>
  `;
}

function renderEmployees() {
  document.getElementById("technicalEmployees").innerHTML =
    technicalWorkers.map(employeeCard).join("");
  document.getElementById("fundamentalEmployees").innerHTML =
    fundamentalWorkers.map(employeeCard).join("");
}

function previewInline(input) {
  const box = input.parentElement.querySelector(".media-preview");
  box.innerHTML = "";
  [...input.files].forEach((file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = document.createElement("img");
      img.src = e.target.result;
      img.alt = file.name;
      box.appendChild(img);
    };
    reader.readAsDataURL(file);
  });
}

function previewMedia(inputId, previewId) {
  const input = document.getElementById(inputId);
  const box = document.getElementById(previewId);
  box.innerHTML = "";
  [...input.files].forEach((file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = document.createElement("img");
      img.src = e.target.result;
      img.alt = file.name;
      box.appendChild(img);
    };
    reader.readAsDataURL(file);
  });
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
      img.alt = file.name;
      preview.appendChild(img);
    };
    reader.readAsDataURL(file);
  });

  const payload = {
    type: "VISUAL_MISSION_INPUT",
    source_note: note || null,
    files: files.map((f) => ({ name: f.name, type: f.type, size: f.size })),
    created_at: new Date().toISOString(),
    message: "Mission text form removed. Intake is screenshot / chart capture / source based."
  };

  log.textContent = JSON.stringify(payload, null, 2);

  // Also reflect in outputs folder as intake record
  const outputs = document.getElementById("finalOutputs");
  if (outputs.querySelector(".empty")) outputs.innerHTML = "";
  const item = document.createElement("div");
  item.className = "folder-item";
  item.textContent = `ورودی دیداری ثبت شد — فایل‌ها: ${files.length} — منبع: ${note || "نامشخص"}`;
  outputs.prepend(item);
}

renderEmployees();
