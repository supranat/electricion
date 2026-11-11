/* การควบคุม: หมุน ซูม คลิกเลือกชิ้นส่วน และแสดงข้อมูล */
const DEFAULT_VIEW = { theta: 0.9, phi: 1.25, radius: 16, y: 5.2 };
const MIN_RADIUS = 3, MAX_RADIUS = 40;

let theta = DEFAULT_VIEW.theta, phi = DEFAULT_VIEW.phi, radius = DEFAULT_VIEW.radius;
let goalTheta = theta, goalPhi = phi, goalRadius = radius;
let selected = null;
let autoRotate = false;
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const target = new THREE.Vector3(0, DEFAULT_VIEW.y, 0);
const goalTarget = target.clone();
const modelCallout = document.getElementById("model-callout");
const calloutCard = document.getElementById("callout-card");
const calloutLine = document.getElementById("callout-line");
const calloutManufacturer = document.getElementById("callout-manufacturer");
const calloutRating = document.getElementById("callout-rating");
const calloutDimensions = document.getElementById("callout-dimensions");

function clampValue(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

function formatMeters(value) {
  return Number(value).toLocaleString("th-TH", { maximumFractionDigits: 2 });
}

function dimensionText(part) {
  if (part.shape === "cyl") {
    return "ขนาดโมเดล: สูง " + formatMeters(part.size[2]) + " ม. · Ø " +
      formatMeters(part.size[0] * 2) + "–" + formatMeters(part.size[1] * 2) + " ม.";
  }
  return "ขนาดโมเดล: " + part.size.map(formatMeters).join(" × ") + " ม.";
}

function findMesh(part) {
  return meshes.find(function (item) { return item.userData.part === part; }) || null;
}

function updateModelCallout() {
  if (!selected) {
    modelCallout.hidden = true;
    return;
  }

  const mesh = findMesh(selected);
  if (!mesh) {
    modelCallout.hidden = true;
    return;
  }

  const stage = document.getElementById("stage");
  const rect = stage.getBoundingClientRect();
  const lift = selected.shape === "box" ? selected.size[1] * 0.1 : 0;
  const anchor = new THREE.Vector3(
    mesh.position.x,
    mesh.position.y + lift,
    mesh.position.z
  );
  anchor.project(camera);
  if (anchor.z < -1 || anchor.z > 1) {
    modelCallout.hidden = true;
    return;
  }

  modelCallout.hidden = false;
  const x = (anchor.x + 1) * rect.width / 2;
  const y = (-anchor.y + 1) * rect.height / 2;
  const cardWidth = calloutCard.offsetWidth;
  const cardHeight = calloutCard.offsetHeight;
  const cardX = Math.max(12, Math.min(rect.width - cardWidth - 12, x + 24));
  const cardY = Math.max(12, Math.min(rect.height - cardHeight - 12, y - cardHeight - 54));
  calloutCard.style.left = cardX + "px";
  calloutCard.style.top = cardY + "px";
  calloutLine.setAttribute("x1", String(x));
  calloutLine.setAttribute("y1", String(y));
  calloutLine.setAttribute("x2", String(Math.max(cardX + 16, Math.min(cardX + cardWidth - 16, x + 24))));
  calloutLine.setAttribute("y2", String(cardY + cardHeight));
}

function renderProjectSpecs() {
  const specs = document.getElementById("project-specs");
  PROJECT.forEach(function (item) {
    const label = document.createElement("dt");
    const value = document.createElement("dd");
    label.textContent = item.label;
    value.textContent = item.value;
    specs.append(label, value);
  });
}

function renderPartsList() {
  const list = document.getElementById("parts-list");
  document.getElementById("part-count").textContent = String(PARTS.length).padStart(2, "0");
  document.getElementById("parts-count-label").textContent = PARTS.length + " รายการ";

  PARTS.forEach(function (part, index) {
    const row = document.createElement("div");
    const button = document.createElement("button");
    const visibilityLabel = document.createElement("label");
    const visibility = document.createElement("input");
    const number = document.createElement("span");
    const name = document.createElement("span");
    const shape = document.createElement("span");
    row.className = "part-row";
    row.dataset.partId = part.id;
    button.type = "button";
    button.className = "part-button";
    button.setAttribute("aria-pressed", "false");
    visibilityLabel.className = "part-visibility";
    visibilityLabel.title = "แสดงหรือซ่อน " + part.name;
    visibilityLabel.setAttribute("aria-label", "แสดงหรือซ่อน " + part.name);
    visibility.type = "checkbox";
    visibility.checked = true;
    visibility.setAttribute("aria-label", "แสดง " + part.name);
    number.className = "part-number";
    number.textContent = String(index + 1).padStart(2, "0");
    name.className = "part-name";
    name.textContent = part.name;
    shape.className = "part-shape";
    shape.textContent = part.shape === "cyl" ? "CYL" : "BOX";
    button.append(number, name, shape);
    button.addEventListener("click", function () { selectPart(part); });
    visibility.addEventListener("change", function () {
      setPartVisibility(part, visibility.checked);
      visibility.setAttribute("aria-label", (visibility.checked ? "ซ่อน " : "แสดง ") + part.name);
    });
    visibilityLabel.append(visibility);
    row.append(button, visibilityLabel);
    list.append(row);
  });
}

function placeCamera() {
  camera.position.set(
    target.x + radius * Math.sin(phi) * Math.cos(theta),
    target.y + radius * Math.cos(phi),
    target.z + radius * Math.sin(phi) * Math.sin(theta)
  );
  camera.lookAt(target);
}

function showInfo(part) {
  document.getElementById("pt").textContent = part.name;
  document.getElementById("part-hint").textContent =
    (part.shape === "cyl" ? "ทรงกระบอก" : "ทรงกล่อง") + " · ขนาดและตำแหน่งอ้างอิงเป็นเมตร";
  const table = document.getElementById("pl");
  table.replaceChildren();
  Object.keys(part.spec).forEach(function (key) {
    const row = document.createElement("tr");
    const label = document.createElement("td");
    const value = document.createElement("td");
    label.textContent = key;
    const rawValue = part.spec[key];
    value.textContent = rawValue === "" || rawValue === null || rawValue === undefined
      ? "— (ยังไม่ได้ใส่ข้อมูล)"
      : String(rawValue);
    row.append(label, value);
    table.append(row);
  });
}

function focusPart(part) {
  const mesh = findMesh(part);
  if (!mesh) return;
  const longest = part.shape === "cyl"
    ? part.size[2]
    : Math.max(part.size[0], part.size[1], part.size[2]);
  goalRadius = clampValue(longest * 2.4 + 2.5, 3.5, 16);
  goalTarget.copy(mesh.position);
  setActiveView(null);
}

function resetView() {
  const turns = Math.round((theta - DEFAULT_VIEW.theta) / (2 * Math.PI));
  goalTheta = DEFAULT_VIEW.theta + turns * 2 * Math.PI;
  goalPhi = DEFAULT_VIEW.phi;
  goalRadius = DEFAULT_VIEW.radius;
  goalTarget.set(0, DEFAULT_VIEW.y, 0);
  setActiveView("angle");
}

const VIEW_PRESETS = {
  front: { theta: Math.PI / 2, phi: 1.28, radius: 19, target: [0, 5.2, 0] },
  angle: { theta: DEFAULT_VIEW.theta, phi: DEFAULT_VIEW.phi, radius: DEFAULT_VIEW.radius, target: [0, DEFAULT_VIEW.y, 0] },
  side: { theta: 0, phi: 1.32, radius: 19, target: [0, 5.2, 0] },
  top: { theta: Math.PI / 2, phi: .32, radius: 23, target: [0, 2.4, 0] }
};

function setActiveView(name) {
  document.querySelectorAll(".view-button[data-view]").forEach(function (button) {
    button.setAttribute("aria-pressed", String(button.dataset.view === name));
  });
}

function setView(name) {
  const view = VIEW_PRESETS[name];
  if (!view) return;
  const turns = Math.round((theta - view.theta) / (2 * Math.PI));
  goalTheta = view.theta + turns * 2 * Math.PI;
  goalPhi = view.phi;
  goalRadius = view.radius;
  goalTarget.set(view.target[0], view.target[1], view.target[2]);
  setActiveView(name);
}

function setPartVisibility(part, visible) {
  meshes.forEach(function (mesh) {
    if (mesh.userData.part === part) mesh.visible = visible;
  });
  outlines.forEach(function (outline) {
    if (outline.userData.part === part) outline.visible = visible;
  });

  const row = document.querySelector('.part-row[data-part-id="' + part.id + '"]');
  if (row) row.classList.toggle("is-hidden", !visible);

  if (!visible && selected === part) {
    selected = null;
    highlight(null);
    modelCallout.hidden = true;
    document.getElementById("pt").textContent = "เลือกชิ้นส่วนเพื่อดูรายละเอียด";
    document.getElementById("part-hint").textContent =
      "เลือกจากรายการหรือคลิกชิ้นส่วนในแบบจำลอง";
    document.getElementById("pl").replaceChildren();
    document.querySelectorAll(".part-button").forEach(function (button) {
      button.setAttribute("aria-pressed", "false");
    });
  }
}

function selectPart(part) {
  const partMeshes = meshes.filter(function (mesh) {
    return mesh.userData.part === part;
  });
  if (!partMeshes.some(function (mesh) { return mesh.visible; })) return;
  selected = part;
  showInfo(part);
  highlight(part);
  focusPart(part);
  calloutManufacturer.textContent = part.spec["ผู้ผลิต"] || part.spec["ยี่ห้อ"] || "ไม่ระบุ";
  calloutRating.textContent = part.spec["พิกัด"] || part.spec["ขนาด"] || part.name;
  calloutDimensions.textContent = dimensionText(part);
  document.querySelectorAll(".part-button").forEach(function (button, index) {
    button.setAttribute("aria-pressed", String(PARTS[index] === part));
  });
}

function highlight(part) {
  meshes.forEach(function (mesh) {
    mesh.material.emissive.setHex(mesh.userData.part === part ? 0x8f2d10 : 0x35130d);
  });
  outlines.forEach(function (outline) {
    outline.material.color.setHex(outline.userData.part === part ? 0xffc078 : 0x4e2b27);
  });
}

renderProjectSpecs();
renderPartsList();

document.querySelectorAll(".view-button[data-view]").forEach(function (button) {
  button.addEventListener("click", function () {
    setView(button.dataset.view);
  });
});

const autoRotateButton = document.getElementById("auto-rotate");
autoRotateButton.disabled = reducedMotion.matches;
autoRotateButton.title = reducedMotion.matches
  ? "ปิดการหมุนอัตโนมัติตามการตั้งค่าลดการเคลื่อนไหวของอุปกรณ์"
  : "เปิดหรือปิดการหมุนโมเดลอัตโนมัติ";
autoRotateButton.addEventListener("click", function () {
  if (reducedMotion.matches) return;
  autoRotate = !autoRotate;
  autoRotateButton.setAttribute("aria-pressed", String(autoRotate));
  autoRotateButton.textContent = autoRotate ? "หยุดหมุนอัตโนมัติ" : "หมุนอัตโนมัติ";
});
reducedMotion.addEventListener("change", function (event) {
  autoRotateButton.disabled = event.matches;
  if (event.matches) {
    autoRotate = false;
    autoRotateButton.setAttribute("aria-pressed", "false");
    autoRotateButton.textContent = "หมุนอัตโนมัติ";
  }
});

document.getElementById("show-all-parts").addEventListener("click", function () {
  PARTS.forEach(function (part) {
    setPartVisibility(part, true);
  });
  document.querySelectorAll(".part-visibility input").forEach(function (checkbox) {
    checkbox.checked = true;
  });
});

(function addResetButton() {
  const stageElement = document.getElementById("stage");
  if (getComputedStyle(stageElement).position === "static") stageElement.style.position = "relative";
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = "รีเซ็ตมุมมอง";
  button.setAttribute("aria-label", "รีเซ็ตมุมมองกล้อง");
  button.style.cssText =
    "position:absolute;left:14px;bottom:14px;z-index:5;padding:10px 18px;" +
    "font:inherit;font-size:1.05rem;font-weight:700;cursor:pointer;color:#ffe6d2;" +
    "background:rgba(40,21,23,.88);border:1px solid rgba(255,151,84,.6);border-radius:10px;";
  button.addEventListener("click", resetView);
  stageElement.append(button);
})();

const fullscreenToggle = document.getElementById("fullscreen-toggle");
function updateFullscreenToggle() {
  const isFullscreen = document.fullscreenElement === document.documentElement;
  fullscreenToggle.setAttribute("aria-pressed", String(isFullscreen));
  fullscreenToggle.innerHTML = isFullscreen
    ? '<span aria-hidden="true">⛶</span> ออกจากเต็มจอ'
    : '<span aria-hidden="true">⛶</span> ดูแบบเต็มจอ';
}

fullscreenToggle.addEventListener("click", function () {
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(function (error) {
      errorMessage.textContent = "ออกจากโหมดเต็มจอไม่ได้: " + error.message;
      errorMessage.hidden = false;
    });
    return;
  }

  if (!document.fullscreenEnabled || !document.documentElement.requestFullscreen) {
    errorMessage.textContent = "เบราว์เซอร์นี้ไม่รองรับการแสดงผลเต็มจอ";
    errorMessage.hidden = false;
    return;
  }

  document.documentElement.requestFullscreen().catch(function (error) {
    errorMessage.textContent = "เปิดโหมดเต็มจอไม่ได้: " + error.message;
    errorMessage.hidden = false;
  });
});

document.addEventListener("fullscreenchange", function () {
  updateFullscreenToggle();
  window.dispatchEvent(new Event("resize"));
});

updateFullscreenToggle();

const pointers = new Map();
let dragging = false, moved = 0, lastX = 0, lastY = 0;
let pinchStartDistance = 0, pinchStartRadius = 0;
cv.style.touchAction = "none";

function pointerDistance() {
  const points = Array.from(pointers.values());
  return Math.hypot(points[0].x - points[1].x, points[0].y - points[1].y);
}

cv.addEventListener("pointerdown", function (e) {
  cv.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (pointers.size === 1) {
    dragging = true; moved = 0; lastX = e.clientX; lastY = e.clientY;
  } else if (pointers.size === 2) {
    dragging = false;
    pinchStartDistance = pointerDistance();
    pinchStartRadius = goalRadius;
  }
});
cv.addEventListener("pointermove", function (e) {
  if (!pointers.has(e.pointerId)) return;
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

  if (pointers.size === 2) {
    const distance = pointerDistance();
    if (pinchStartDistance > 0 && distance > 0) {
      goalRadius = clampValue(pinchStartRadius * pinchStartDistance / distance, MIN_RADIUS, MAX_RADIUS);
      setActiveView(null);
    }
    return;
  }

  if (!dragging) return;
  const dx = e.clientX - lastX, dy = e.clientY - lastY;
  moved += Math.abs(dx) + Math.abs(dy);
  if (dx || dy) setActiveView(null);
  goalTheta -= dx * 0.006;
  goalPhi = clampValue(goalPhi - dy * 0.005, 0.2, 1.5);
  lastX = e.clientX; lastY = e.clientY;
});
cv.addEventListener("pointerup", function (e) {
  const wasDragging = dragging;
  pointers.delete(e.pointerId);
  if (!wasDragging) return;
  dragging = false;
  if (moved > 6) return;                       // ถ้าลากอยู่ ไม่ถือว่าเป็นการคลิก
  const r = cv.getBoundingClientRect();
  const mouse = new THREE.Vector2(
    ((e.clientX - r.left) / r.width) * 2 - 1,
    -((e.clientY - r.top) / r.height) * 2 + 1
  );
  const ray = new THREE.Raycaster();
  ray.setFromCamera(mouse, camera);
  const hit = ray.intersectObjects(pickMeshes.filter(function (mesh) {
    return mesh.visible;
  }))[0];
  if (hit) selectPart(hit.object.userData.part);
});
cv.addEventListener("pointercancel", function (e) {
  pointers.delete(e.pointerId);
  dragging = false;
});
cv.addEventListener("dblclick", resetView);
cv.addEventListener("wheel", function (e) {
  e.preventDefault();
  goalRadius = clampValue(goalRadius * Math.exp(e.deltaY * 0.0012), MIN_RADIUS, MAX_RADIUS);
  setActiveView(null);
}, { passive: false });

function loop() {
  requestAnimationFrame(loop);
  const ease = 0.16;
  if (autoRotate && !reducedMotion.matches) goalTheta += 0.0025;
  const cameraEase = reducedMotion.matches ? 1 : ease;
  theta += (goalTheta - theta) * cameraEase;
  phi += (goalPhi - phi) * cameraEase;
  radius += (goalRadius - radius) * cameraEase;
  target.lerp(goalTarget, cameraEase);
  placeCamera();
  renderer.render(scene, camera);
  updateModelCallout();
}
loop();
