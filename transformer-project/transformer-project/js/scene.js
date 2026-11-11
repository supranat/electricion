/* สร้างฉากและโมเดล 3D จากข้อมูลชิ้นส่วน */
const errorMessage = document.getElementById("error");
function showError(message) {
  if (errorMessage) {
    errorMessage.textContent = message;
    errorMessage.hidden = false;
  } else {
    console.error(message);
  }
}

function fail(message) {
  showError(message);
  throw new Error(message);
}

if (!window.THREE) {
  fail("โหลด Three.js ไม่สำเร็จ กรุณาตรวจสอบอินเทอร์เน็ตหรือการเชื่อมต่อ CDN แล้วโหลดหน้าเว็บใหม่");
}

if (typeof PARTS === "undefined" || !Array.isArray(PARTS)) {
  fail("ไม่พบข้อมูลชิ้นส่วน กรุณาตรวจสอบว่า js/data.js โหลดสำเร็จ");
}

if (typeof PROJECT === "undefined" || !Array.isArray(PROJECT)) {
  fail("ไม่พบข้อมูลสเปกระบบ กรุณาตรวจสอบว่า js/data.js โหลดสำเร็จ");
}

if (typeof LAYOUT === "undefined" || !LAYOUT || typeof LAYOUT !== "object" || Array.isArray(LAYOUT)) {
  fail("ไม่พบค่าระดับ LAYOUT กรุณาตรวจสอบว่า js/data.js เป็นฉบับล่าสุด");
}

if (PARTS.length === 0) fail("ไม่พบรายการชิ้นส่วนสำหรับสร้างโมเดล");
PROJECT.forEach(function (item, index) {
  if (!item || typeof item !== "object" ||
      typeof item.label !== "string" || !item.label.trim() ||
      typeof item.value !== "string") {
    fail("ข้อมูลสเปกระบบลำดับที่ " + (index + 1) + " ต้องมี label และ value เป็นข้อความ");
  }
});

["poleZ", "beamY", "beamHeight", "beamTopY", "wireY", "bushingScale"].forEach(function (key) {
  if (!Number.isFinite(LAYOUT[key])) fail("ค่า LAYOUT." + key + " ต้องเป็นตัวเลขจำกัด");
});
if (LAYOUT.poleZ <= 0 || LAYOUT.beamHeight <= 0 || LAYOUT.bushingScale <= 0) {
  fail("ค่า LAYOUT.poleZ, beamHeight และ bushingScale ต้องมากกว่า 0");
}
if (LAYOUT.wireY <= 0 ||
    Math.abs(LAYOUT.beamTopY - (LAYOUT.beamY + LAYOUT.beamHeight / 2)) > 0.001) {
  fail("ค่า LAYOUT.wireY หรือระดับขอบบนของคานไม่สอดคล้องกัน");
}

const ids = new Set();
PARTS.forEach(function (part, index) {
  const label = part && part.id ? '"' + part.id + '"' : "ลำดับที่ " + (index + 1);
  const isVector = function (value, length) {
    return Array.isArray(value) && value.length === length && value.every(Number.isFinite);
  };
  if (!part || typeof part !== "object") fail("ข้อมูลชิ้นส่วน " + label + " ต้องเป็น object");
  if (typeof part.id !== "string" || !part.id.trim()) fail("ชิ้นส่วน " + label + " ต้องมี id");
  if (ids.has(part.id)) fail("พบ id ซ้ำในข้อมูลชิ้นส่วน: " + part.id);
  ids.add(part.id);
  if (typeof part.name !== "string" || !part.name.trim()) fail("ชิ้นส่วน " + label + " ต้องมี name");
  if (part.shape !== "box" && part.shape !== "cyl") fail("shape ของชิ้นส่วน " + label + " ต้องเป็น box หรือ cyl");
  if (!isVector(part.size, 3) || part.size.some(function (value) { return value <= 0; })) {
    fail("size ของชิ้นส่วน " + label + " ต้องเป็นตัวเลขบวก 3 ค่า");
  }
  if (!isVector(part.pos, 3)) fail("pos ของชิ้นส่วน " + label + " ต้องเป็นตัวเลข 3 ค่า");
  if (part.rot !== undefined && !isVector(part.rot, 3)) fail("rot ของชิ้นส่วน " + label + " ต้องเป็นตัวเลข 3 ค่า");
  if (!part.spec || typeof part.spec !== "object" || Array.isArray(part.spec)) {
    fail("spec ของชิ้นส่วน " + label + " ต้องเป็น object");
  }
  if (part.color !== undefined && typeof part.color !== "string") {
    fail("color ของชิ้นส่วน " + label + " ต้องเป็นข้อความสี");
  }
});

const cv = document.getElementById("cv");
if (!cv) fail("ไม่พบ canvas สำหรับแสดงฉาก 3D (id=cv)");
const stage = document.getElementById("stage");
if (!stage) fail("ไม่พบพื้นที่แสดงฉาก 3D (id=stage)");

let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true });
} catch (error) {
  showError("สร้างฉาก 3D ไม่ได้ เบราว์เซอร์หรืออุปกรณ์อาจไม่รองรับ WebGL");
  throw error;
}

renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.88;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x281517);
scene.fog = new THREE.Fog(0x281517, 42, 110);
const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 180);

scene.add(new THREE.HemisphereLight(0xffe6d3, 0x55403a, 0.78));
const sun = new THREE.DirectionalLight(0xffedcf, 1.55);
sun.position.set(-12, 22, 10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -18;
sun.shadow.camera.right = 18;
sun.shadow.camera.top = 20;
sun.shadow.camera.bottom = -12;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 60;
sun.shadow.bias = -0.0004;
scene.add(sun);

function createNoiseTexture(baseColor, seed, count, size) {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  if (!context) fail("สร้างพื้นผิวลายวัสดุไม่ได้ เบราว์เซอร์ไม่รองรับ Canvas 2D");
  context.fillStyle = baseColor;
  context.fillRect(0, 0, canvas.width, canvas.height);
  let value = seed;
  function random() {
    value = (value * 1664525 + 1013904223) % 4294967296;
    return value / 4294967296;
  }
  for (let i = 0; i < count; i++) {
    const shade = Math.floor(random() * 110 + 70);
    context.fillStyle = "rgba(" + shade + "," + shade + "," + shade + "," + (random() * 0.12 + 0.025) + ")";
    context.fillRect(random() * 256, random() * 256, random() * size + 1, random() * size + 1);
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.encoding = THREE.sRGBEncoding;
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
  return texture;
}

const concreteTexture = createNoiseTexture("#858780", 38, 1900, 5);
concreteTexture.repeat.set(2, 4);
const groundTexture = createNoiseTexture("#354832", 87, 5000, 7);
groundTexture.repeat.set(18, 18);

const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(180, 180),
  new THREE.MeshStandardMaterial({ map: groundTexture, color: 0x9aaa82, roughness: 1 })
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.04;
ground.receiveShadow = true;
scene.add(ground);

const meshes = [];
const pickMeshes = [];
const outlines = [];

function addDetail(mesh, part) {
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.userData.part = part;
  mesh.material = mesh.material.clone();
  scene.add(mesh);
  meshes.push(mesh);
  pickMeshes.push(mesh);
  return mesh;
}

function addBox(part, size, position, material, rotation) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(size[0], size[1], size[2]), material);
  mesh.position.set(position[0], position[1], position[2]);
  if (rotation) mesh.rotation.set(rotation[0], rotation[1], rotation[2]);
  return addDetail(mesh, part);
}

function addCylinder(part, radiusTop, radiusBottom, height, position, material, segments) {
  const mesh = new THREE.Mesh(
    new THREE.CylinderGeometry(radiusTop, radiusBottom, height, segments || 20),
    material
  );
  mesh.position.set(position[0], position[1], position[2]);
  return addDetail(mesh, part);
}

function addWire(part, points, radius, material) {
  if (!Array.isArray(points) || points.length < 2 ||
      !Number.isFinite(radius) || radius <= 0 ||
      points.some(function (point) {
        return !Array.isArray(point) || point.length !== 3 || !point.every(Number.isFinite);
      })) {
    fail("ข้อมูลแนวสายไฟของชิ้นส่วน " + part.name + " ไม่ถูกต้อง");
  }
  const curve = new THREE.CatmullRomCurve3(points.map(function (point) {
    return new THREE.Vector3(point[0], point[1], point[2]);
  }));
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, 32, radius, 8, false), material);
  return addDetail(mesh, part);
}

const concreteMaterial = new THREE.MeshStandardMaterial({
  map: concreteTexture,
  color: 0xd0cec2,
  roughness: 0.95
});
const steelMaterial = new THREE.MeshStandardMaterial({ color: 0x444b4c, metalness: 0.78, roughness: 0.34 });
const galvanizedMaterial = new THREE.MeshStandardMaterial({ color: 0x9da6a5, metalness: 0.72, roughness: 0.3 });
const ceramicMaterial = new THREE.MeshStandardMaterial({ color: 0xe9e5d7, roughness: 0.24, metalness: 0.04 });
const wireMaterial = new THREE.MeshStandardMaterial({ color: 0x393e3d, metalness: 0.74, roughness: 0.3 });
const transformerMaterial = new THREE.MeshStandardMaterial({
  color: 0x687461,
  metalness: 0.62,
  roughness: 0.4
});
const transformerDetailMaterial = new THREE.MeshStandardMaterial({
  color: 0x4f5c4d,
  metalness: 0.58,
  roughness: 0.45
});

function addBushing(part, x, topY, z, highVoltage) {
  const scale = LAYOUT.bushingScale;
  const layers = highVoltage
    ? [
        [0.105, 0.14, 0.13, 0.09, steelMaterial],
        [0.105, 0.12, 0.11, 0.21, ceramicMaterial],
        [0.082, 0.105, 0.1, 0.315, ceramicMaterial],
        [0.055, 0.08, 0.1, 0.41, ceramicMaterial],
        [0.025, 0.025, 0.12, 0.52, galvanizedMaterial]
      ]
    : [
        [0.105, 0.14, 0.13, 0.09, steelMaterial],
        [0.105, 0.12, 0.11, 0.21, ceramicMaterial],
        [0.082, 0.105, 0.1, 0.315, ceramicMaterial],
        [0.03, 0.03, 0.1, 0.42, galvanizedMaterial]
      ];
  layers.forEach(function (layer) {
    addCylinder(
      part,
      layer[0],
      layer[1],
      layer[2] * scale,
      [x, topY + layer[3] * scale, z],
      layer[4],
      20
    );
  });
}

function addTransformerDetails(part, position) {
  const x = position[0], y = position[1], z = position[2];
  const width = part.size[0], height = part.size[1], length = part.size[2];
  const top = y + height / 2;
  const bottom = y - height / 2;
  const rimMaterial = new THREE.MeshStandardMaterial({ color: 0x8c927d, metalness: 0.7, roughness: 0.32 });
  addBox(part, [width + 0.08, 0.09, length + 0.08], [x, top + 0.02, z], rimMaterial);
  addBox(part, [width - 0.12, 0.06, length - 0.12], [x, bottom - 0.03, z], steelMaterial);

  const finSpan = length - 0.3;
  for (let side = -1; side <= 1; side += 2) {
    for (let i = 0; i < 11; i++) {
      addBox(
        part,
        [0.07, height * 0.68, 0.055],
        [x + side * (width / 2 + 0.03), y - 0.02, z - finSpan / 2 + i * finSpan / 10],
        transformerDetailMaterial
      );
    }
  }

  const widthScale = width / 1.3;
  [-0.4, 0, 0.4].forEach(function (offset) {
    addBushing(part, x + offset * widthScale, top, z - length * 0.29, true);
  });
  [-0.45, -0.15, 0.15, 0.45].forEach(function (offset) {
    addBushing(part, x + offset * widthScale, top, z + length * 0.29, false);
  });

  addBox(
    part,
    [0.34, 0.32, 0.18],
    [x + width / 2 + 0.07, y + height * 0.12, z + length * 0.27],
    transformerDetailMaterial
  );
  addCylinder(
    part,
    0.09,
    0.09,
    0.13,
    [x + width / 2 + 0.26, y + height * 0.13, z + length * 0.27],
    galvanizedMaterial,
    20
  );
  addCylinder(
    part,
    0.16,
    0.16,
    0.12,
    [x + width / 2 + 0.27, y - height * 0.2, z - length * 0.25],
    galvanizedMaterial,
    24
  );

  addBox(part, [width * 1.2, 0.08, 0.13], [x, bottom - 0.08, z - length * 0.29], steelMaterial);
  addBox(part, [width * 1.2, 0.08, 0.13], [x, bottom - 0.08, z + length * 0.29], steelMaterial);
}

const cabinetMaterial = new THREE.MeshStandardMaterial({
  color: 0x626e68, metalness: 0.48, roughness: 0.52
});
const phaseMaterials = [
  new THREE.MeshStandardMaterial({ color: 0xa92e26, roughness: 0.62 }),
  new THREE.MeshStandardMaterial({ color: 0xd5a62c, roughness: 0.62 }),
  new THREE.MeshStandardMaterial({ color: 0x355d9a, roughness: 0.62 }),
  new THREE.MeshStandardMaterial({ color: 0x36393a, roughness: 0.62 })
];

function linePost(part, x, y, z) {
  addCylinder(part, 0.07, 0.085, 0.08, [x, y + 0.04, z], galvanizedMaterial, 16);
  for (let ring = 0; ring < 4; ring++) {
    addCylinder(
      part,
      ring % 2 === 0 ? 0.105 : 0.067,
      ring % 2 === 0 ? 0.105 : 0.067,
      0.055,
      [x, y + 0.105 + ring * 0.085, z],
      ceramicMaterial,
      16
    );
  }
  addCylinder(part, 0.025, 0.035, 0.1, [x, y + 0.48, z], galvanizedMaterial, 12);
}

function suspensionUnit(part, x, y, z) {
  addCylinder(part, 0.035, 0.045, 0.16, [x, y + 0.08, z], galvanizedMaterial, 12);
  const discCount = 12;
  for (let disc = 0; disc < discCount; disc++) {
    const discY = y - 0.04 - disc * 0.14;
    addCylinder(
      part,
      disc % 2 === 0 ? 0.105 : 0.073,
      disc % 2 === 0 ? 0.105 : 0.073,
      0.07,
      [x, discY, z],
      ceramicMaterial,
      16
    );
    addCylinder(part, 0.028, 0.028, 0.1, [x, discY - 0.08, z], galvanizedMaterial, 12);
  }
  addBox(part, [0.14, 0.1, 0.14], [x, y - 1.84, z], galvanizedMaterial);
}

function addDoubleTopCrossarms(part) {
  const x = part.pos[0], y = part.pos[1], z = part.pos[2];
  addBox(part, [2, 0.12, 0.12], [x, y, z], concreteMaterial);
  addBox(part, [2, 0.12, 0.12], [x, y - 0.2, z], concreteMaterial);
  addBox(part, [0.2, 0.42, 0.24], [x, y - 0.1, z], galvanizedMaterial);
}

function addSuspensionCrossarm(part) {
  const x = part.pos[0], z = part.pos[2];
  addBox(part, part.size, part.pos, concreteMaterial);
  addBox(part, [0.2, 0.28, 0.24], [x, part.pos[1] - 0.04, z], galvanizedMaterial);
}

function addSuspensionUnits(part) {
  const x = part.pos[0], z = part.pos[2];
  const top = part.pos[1] + part.size[2] / 2;
  [-0.52, 0, 0.52].forEach(function (offset) {
    suspensionUnit(part, x + offset, top, z);
  });
}

function addCrossarmPostSet(part, arresterSet) {
  const x = part.pos[0], y = part.pos[1], z = part.pos[2];
  if (arresterSet) {
    [-1.25, 0, 1.25].forEach(function (offset) {
      linePost(part, x, y - 0.25, z + offset);
    });
  } else {
    [-0.72, 0, 0.72].forEach(function (offset) {
      linePost(part, x + offset, y - 0.22, z);
    });
  }
}

function addCutoutFuses(part) {
  const x = part.pos[0], y = part.pos[1], z = part.pos[2];
  [-1.25, 0, 1.25].forEach(function (offset) {
    const phaseZ = z + offset;
    addBox(part, [0.16, 0.08, 0.22], [x - 0.12, y - 0.18, phaseZ], galvanizedMaterial);
    addCylinder(part, 0.045, 0.055, 0.56, [x, y, phaseZ], ceramicMaterial, 16);
    addCylinder(part, 0.075, 0.075, 0.045, [x, y + 0.25, phaseZ], galvanizedMaterial, 16);
    addCylinder(part, 0.075, 0.075, 0.045, [x, y - 0.25, phaseZ], galvanizedMaterial, 16);
    addWire(part, [
      [x - 0.2, y + 0.25, phaseZ],
      [x, y + 0.12, phaseZ],
      [x + 0.2, y + 0.25, phaseZ]
    ], 0.012, wireMaterial);
  });
}

function addSurgeArresters(part) {
  const x = part.pos[0], y = part.pos[1], z = part.pos[2];
  [-1.25, 0, 1.25].forEach(function (offset) {
    const phaseZ = z + offset;
    addCylinder(part, 0.055, 0.07, 0.44, [x + 0.28, y, phaseZ], ceramicMaterial, 20);
    for (let ring = 0; ring < 3; ring++) {
      addCylinder(part, 0.085, 0.085, 0.035, [x + 0.28, y + 0.11 - ring * 0.11, phaseZ], galvanizedMaterial, 20);
    }
    addCylinder(part, 0.025, 0.035, 0.13, [x + 0.28, y + 0.29, phaseZ], galvanizedMaterial, 12);
    addCylinder(part, 0.025, 0.035, 0.13, [x + 0.28, y - 0.29, phaseZ], galvanizedMaterial, 12);
  });
}

function addPoleFoundations(part) {
  [-LAYOUT.poleZ, LAYOUT.poleZ].forEach(function (z) {
    addBox(part, [0.8, 1.8, 0.8], [0, -0.9, z], concreteMaterial);
    addBox(part, [0.58, 0.18, 0.58], [0, 0.05, z], concreteMaterial);
  });
}

function addGroundAngles(part) {
  [-LAYOUT.poleZ, LAYOUT.poleZ].forEach(function (z) {
    const side = z < 0 ? 1 : -1;
    const x = side * 0.5;
    addBox(part, [0.06, 2, 0.005], [x, -0.95, z], galvanizedMaterial);
    addBox(part, [0.005, 2, 0.06], [x + 0.03, -0.95, z + 0.03], galvanizedMaterial);
    addBox(part, [0.5, 0.025, 0.025], [x - side * 0.25, 0.025, z], galvanizedMaterial);
  });
}

function addSupportBrackets(part) {
  const beamY = LAYOUT.beamY;
  const halfBeam = LAYOUT.beamHeight / 2;
  [-LAYOUT.poleZ, LAYOUT.poleZ].forEach(function (z) {
    addBox(part, [0.3, 0.24, 0.34], [0, beamY - halfBeam - 0.12, z], galvanizedMaterial);
    addBox(part, [0.23, 0.05, 0.33], [0, beamY + halfBeam + 0.025, z], steelMaterial);
    [-0.12, 0.12].forEach(function (offset) {
      addCylinder(part, 0.025, 0.025, LAYOUT.beamHeight + 0.1, [0, beamY, z + offset], galvanizedMaterial, 12);
      addCylinder(part, 0.045, 0.045, 0.025, [0, beamY + halfBeam + 0.06, z + offset], galvanizedMaterial, 12);
      addCylinder(part, 0.045, 0.045, 0.025, [0, beamY - halfBeam - 0.01, z + offset], galvanizedMaterial, 12);
    });
  });
}

function addCableLadder(part) {
  const x = part.pos[0], y = part.pos[1], z = part.pos[2];
  const width = 0.5, height = part.size[1];
  [-width / 2, width / 2].forEach(function (offset) {
    addBox(part, [0.04, height, 0.04], [x, y, z + offset], galvanizedMaterial);
  });
  for (let rungY = y - height / 2 + 0.16; rungY < y + height / 2; rungY += 0.32) {
    addBox(part, [0.04, 0.035, width], [x, rungY, z], galvanizedMaterial);
  }
  [-0.32, 0.32].forEach(function (offset) {
    addBox(part, [0.25, 0.06, 0.05], [x - 0.14, y + offset, z], steelMaterial);
  });
}

function addLowVoltageCables(part) {
  const x = part.pos[0], z = part.pos[2];
  const startY = LAYOUT.beamTopY + 0.14;
  for (let bundle = 0; bundle < 4; bundle++) {
    for (let phase = 0; phase < 4; phase++) {
      const cableX = x - 0.13 + phase * 0.085;
      const cableZ = z - 0.16 + bundle * 0.105;
      addWire(part, [
        [0.15 + phase * 0.08, startY, cableZ],
        [cableX, startY - 0.4, cableZ],
        [cableX, 3.1, cableZ],
        [cableX, 0.18, cableZ],
        [0.72, 0.12, cableZ],
        [1.05, 0.15, cableZ]
      ], phase === 3 ? 0.018 : 0.022, phaseMaterials[phase]);
    }
  }
}

function addLvCabinet(part) {
  const x = part.pos[0], y = part.pos[1], z = part.pos[2];
  addBox(part, [0.8, 2.5, 1.05], [x, y, z], cabinetMaterial);
  addBox(part, [0.025, 2.28, 0.92], [x + 0.415, y, z], steelMaterial);
  addBox(part, [0.035, 0.16, 0.08], [x + 0.45, y + 0.05, z + 0.31], galvanizedMaterial);
  addBox(part, [0.025, 0.06, 0.06], [x + 0.44, y + 0.05, z + 0.27], steelMaterial);
  addBox(part, [0.035, 0.35, 0.23], [x + 0.435, y + 0.72, z - 0.3], steelMaterial);
}

function addOverheadConductors(part) {
  const wireY = LAYOUT.wireY;
  const poleZ = LAYOUT.poleZ;
  [-0.72, 0, 0.72].forEach(function (x) {
    addWire(part, [
      [x, wireY + 0.25, -14],
      [x, wireY + 0.06, -7],
      [x, wireY, -poleZ],
      [x, wireY - 0.04, 0],
      [x, wireY, poleZ],
      [x, wireY + 0.06, 7],
      [x, wireY + 0.25, 14]
    ], 0.018, wireMaterial);
  });
}

function materialFor(part) {
  if (part.kind === "pole" || part.kind === "crossbeam" ||
      part.kind === "transformer-beam" || part.kind === "top-double-crossarms" ||
      part.kind === "top-suspension-crossarm" || part.kind === "pole-foundations" ||
      part.kind === "lv-pad") return concreteMaterial;
  if (part.kind === "transformer") return transformerMaterial;
  if (part.kind === "lv-cabinet") return cabinetMaterial;
  if (part.kind === "ground-rods" || part.kind === "cable-ladder" ||
      part.kind === "transformer-support-brackets") return galvanizedMaterial;
  if (part.shape === "cyl" && part.kind !== "overhead-conductors") return ceramicMaterial;
  return new THREE.MeshStandardMaterial({
    color: part.color || "#888888", metalness: 0.35, roughness: 0.65
  });
}

function buildPart(part) {
  const x = part.pos[0], y = part.pos[1], z = part.pos[2];
  if (part.kind === "pole-foundations") return addPoleFoundations(part);
  if (part.kind === "top-double-crossarms") return addDoubleTopCrossarms(part);
  if (part.kind === "top-suspension-crossarm") return addSuspensionCrossarm(part);
  if (part.kind === "line-posts-top") return addCrossarmPostSet(part, false);
  if (part.kind === "suspension-units") return addSuspensionUnits(part);
  if (part.kind === "cutout-fuses") return addCutoutFuses(part);
  if (part.kind === "line-posts-arrester") return addCrossarmPostSet(part, true);
  if (part.kind === "surge-arresters") return addSurgeArresters(part);
  if (part.kind === "transformer-support-brackets") return addSupportBrackets(part);
  if (part.kind === "ground-rods") return addGroundAngles(part);
  if (part.kind === "cable-ladder") return addCableLadder(part);
  if (part.kind === "lv-cables") return addLowVoltageCables(part);
  if (part.kind === "lv-cabinet") return addLvCabinet(part);
  if (part.kind === "overhead-conductors") return addOverheadConductors(part);

  const material = materialFor(part);
  const geometry = part.shape === "cyl"
    ? new THREE.CylinderGeometry(part.size[0], part.size[1], part.size[2], 32)
    : new THREE.BoxGeometry(part.size[0], part.size[1], part.size[2]);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(x, y, z);
  if (part.rot) {
    mesh.rotation.set(
      part.rot[0] * Math.PI / 180,
      part.rot[1] * Math.PI / 180,
      part.rot[2] * Math.PI / 180
    );
  }
  addDetail(mesh, part);

  if (part.shape === "box") {
    const outline = new THREE.LineSegments(
      new THREE.EdgesGeometry(geometry),
      new THREE.LineBasicMaterial({ color: 0x4e2b27, transparent: true, opacity: 0.45 })
    );
    outline.position.copy(mesh.position);
    outline.rotation.copy(mesh.rotation);
    outline.userData.part = part;
    scene.add(outline);
    outlines.push(outline);
  }
  if (part.kind === "transformer") addTransformerDetails(part, part.pos);
}

function buildParts() {
  PARTS.forEach(buildPart);
}

buildParts();

function resize() {
  const rect = stage.getBoundingClientRect();
  if (rect.width <= 0 || rect.height <= 0) return;
  renderer.setSize(rect.width, rect.height, false);
  camera.aspect = rect.width / rect.height;
  camera.updateProjectionMatrix();
}

addEventListener("resize", resize);
if (typeof ResizeObserver !== "undefined") {
  new ResizeObserver(resize).observe(stage);
}
resize();
