/* =====================================================
   EE-05 reference model data
   All model dimensions and positions are in meters.
   The approximate elevations and 4.2 m pole spacing are visual estimates,
   not construction dimensions. Verify all dimensions against the issued
   project drawing and site measurements before any engineering use.
   ===================================================== */
const PROJECT = [
  { label: "แบบอ้างอิง", value: "EE-05 · DETAIL OF CONCRETE POLE TR 1000kVA" },
  { label: "สถานะ", value: "แบบจำลองประกอบอ้างอิงแบบ EE-05 · ไม่ใช่แบบก่อสร้าง" },
  { label: "กำลังไฟฟ้า", value: "1,000 kVA" },
  { label: "แรงดันด้านสูง", value: "22 kV (อุปกรณ์ตามแบบ 27 kV)" },
  { label: "แรงดันด้านต่ำ", value: "230/400 V" },
  { label: "เสารองรับ", value: "คอนกรีตอัดแรง 2 ต้น · สูง 12 ม. · ฝังดิน 2 ม." },
  { label: "ระยะห่างเสา", value: "ประมาณ 4.2 ม. · ประเมินจากสัดส่วนภาพ" },
  { label: "คานรองรับหม้อแปลง", value: "150 × 300 × 4,600 มม." },
  { label: "ระดับแนวคานโดยประมาณ", value: "ฟิวส์ 7.9 ม. · ล่อฟ้า 6.4 ม. · หม้อแปลง 3.9 ม." },
  { label: "ระบบสายแรงต่ำ", value: "Cable ladder กว้าง 500 มม. · เดินลงตู้ที่ระดับพื้น" },
  { label: "คำเตือน", value: "แบบระบุ DO NOT SCALE · ตรวจสอบระยะจริงและแบบอนุมัติก่อนใช้งาน" }
];

const PARTS = [
  {
    id: "pole1", kind: "pole", name: "เสาคอนกรีตอัดแรงต้นที่ 1",
    shape: "cyl", size: [0.17, 0.24, 12], pos: [0, 4, -2.1], color: "#9a9a94",
    spec: { "ขนาด": "สูง 12 ม. · ฝังดินประมาณ 2 ม.", "ชนิด": "เสาคอนกรีตอัดแรง", "ตำแหน่งยอดเสา": "ประมาณ 10 ม. เหนือระดับดิน", "ระยะห่างเสา": "ประมาณ 4.2 ม. (ประเมินจากภาพ)" }
  },
  {
    id: "pole2", kind: "pole", name: "เสาคอนกรีตอัดแรงต้นที่ 2",
    shape: "cyl", size: [0.17, 0.24, 12], pos: [0, 4, 2.1], color: "#9a9a94",
    spec: { "ขนาด": "สูง 12 ม. · ฝังดินประมาณ 2 ม.", "ชนิด": "เสาคอนกรีตอัดแรง", "ตำแหน่งยอดเสา": "ประมาณ 10 ม. เหนือระดับดิน", "ระยะห่างเสา": "ประมาณ 4.2 ม. (ประเมินจากภาพ)" }
  },
  {
    id: "pole-foundations", kind: "pole-foundations", name: "ฐานคอนกรีตรอบโคนเสา",
    shape: "box", size: [0.8, 1.8, 0.8], pos: [0, -0.9, 0], color: "#858780",
    spec: { "ชนิด": "ฐานคอนกรีตรอบโคนเสาใต้ดิน (แสดงเป็นชิ้นส่วนประกอบ)", "ความลึก": "ประมาณ 1.8 ม. · ขนาดจำลองเพื่อแสดงภาพ ไม่ใช่ขนาดจากแบบก่อสร้าง" }
  },
  {
    id: "top-double-crossarms", kind: "top-double-crossarms", name: "คานพาดยอดเสาแบบคู่",
    shape: "box", size: [2, 0.12, 0.12], pos: [0, 9.55, -2.1], color: "#8c8c86",
    spec: { "ขนาด": "120 × 120 × 2,000 มม. ต่อคาน · ติดตั้งแบบคู่", "วัสดุ": "คอนกรีตอัดแรง", "ตำแหน่ง": "ยอดเสาต้นที่ 1 · ระดับโดยประมาณ" }
  },
  {
    id: "top-suspension-crossarm", kind: "top-suspension-crossarm", name: "คานคอนกรีตรองรับลูกถ้วย Suspension",
    shape: "box", size: [2, 0.12, 0.12], pos: [0, 9.45, 2.1], color: "#8c8c86",
    spec: { "ขนาด": "ยาว 2,000 มม. · แทนชิ้นส่วนเดิม 2,350 มม.", "วัสดุ": "คอนกรีต ไม่ใช่เหล็กชุบ", "ตำแหน่ง": "ยอดเสาต้นที่ 2 · ย้ายจากระดับ 9.35 ม. ตามข้อกำหนด" }
  },
  {
    id: "line-posts-top", kind: "line-posts-top", name: "ลูกถ้วย Line Post 57-2L ชุดยอดเสา",
    shape: "cyl", size: [0.08, 0.1, 0.42], pos: [0, 9.9, -2.1], color: "#e9e5d7",
    spec: { "ชนิด": "Line Post 57-2L", "จำนวน": "3 ชุด", "ตำแหน่ง": "บนคานคู่ยอดเสาต้นที่ 1", "พิกัด": "ตรวจสอบกับแบบและข้อมูลผู้ผลิตก่อนก่อสร้าง" }
  },
  {
    id: "suspension-units", kind: "suspension-units", name: "ลูกถ้วย Suspension 52-1",
    shape: "cyl", size: [0.08, 0.1, 2], pos: [0, 8.3, 2.1], color: "#e9e5d7",
    spec: { "ชนิด": "Suspension 52-1", "ความยาว": "2,000 มม. (ตามข้อมูลที่ให้)", "จำนวน": "3 ชุดจำลอง", "หมายเหตุ": "เรขาคณิตแสดงประกอบภาพ · ตรวจรูปแบบ/จำนวนจากแบบอนุมัติ" }
  },
  {
    id: "overhead-conductors", kind: "overhead-conductors", name: "สายตัวนำแรงสูงเหนือยอดเสา",
    shape: "cyl", size: [0.018, 0.018, 1], pos: [0, 10.36, 0], color: "#393e3d",
    spec: { "จำนวน": "3 เฟส", "ตำแหน่ง": "พาดผ่านลูกถ้วยยอดเสา", "หมายเหตุ": "แนวสายเป็นภาพประกอบ ไม่ได้ระบุระยะ span ในแบบจำลอง" }
  },
  {
    id: "fuse-crossbeam", kind: "crossbeam", name: "คานฟิวส์คัตเอาท์",
    shape: "box", size: [0.1, 0.1, 4.2], pos: [0, 7.9, 0], color: "#8c8c86",
    spec: { "ขนาด": "100 × 100 × 4,200 มม.", "วัสดุ": "คอนกรีตอัดแรง", "ตำแหน่ง": "พาดระหว่างเสาสองต้น · ระดับประมาณ 7.9 ม." }
  },
  {
    id: "cutout-fuses", kind: "cutout-fuses", name: "ฟิวส์คัตเอาท์",
    shape: "cyl", size: [0.05, 0.07, 0.55], pos: [0, 8.25, 0], color: "#76846d",
    spec: { "จำนวน": "3 ชุด", "พิกัด": "27 kV · 100 A", "ตำแหน่ง": "ติดตั้งบนคานฟิวส์", "หมายเหตุ": "รูปทรงเป็นภาพจำลอง ไม่ใช่รายละเอียดประกอบติดตั้ง" }
  },
  {
    id: "lightning-crossbeam", kind: "crossbeam", name: "คานล่อฟ้า",
    shape: "box", size: [0.1, 0.1, 4.2], pos: [0, 6.4, 0], color: "#8c8c86",
    spec: { "ขนาด": "100 × 100 × 4,200 มม.", "วัสดุ": "คอนกรีตอัดแรง", "ตำแหน่ง": "พาดระหว่างเสาสองต้น · ระดับประมาณ 6.4 ม." }
  },
  {
    id: "line-posts-arrester", kind: "line-posts-arrester", name: "ลูกถ้วย Line Post 57-2L ชุดคานล่อฟ้า",
    shape: "cyl", size: [0.08, 0.1, 0.42], pos: [0, 6.75, 0], color: "#e9e5d7",
    spec: { "ชนิด": "Line Post 57-2L", "จำนวน": "3 ชุด", "ตำแหน่ง": "บนคานล่อฟ้า", "พิกัด": "ตรวจสอบกับแบบและข้อมูลผู้ผลิตก่อนก่อสร้าง" }
  },
  {
    id: "surge-arresters", kind: "surge-arresters", name: "ล่อฟ้า",
    shape: "cyl", size: [0.06, 0.075, 0.48], pos: [0, 7.05, 0], color: "#c5c6bd",
    spec: { "จำนวน": "3 ชุด", "พิกัด": "21 kV · 5 kA", "ตำแหน่ง": "บนคานล่อฟ้า", "หมายเหตุ": "ชิ้นส่วนจำลองเพื่ออธิบายองค์ประกอบ" }
  },
  {
    id: "transformer-crossbar", kind: "crossbeam", name: "คานเสริมเหนือหม้อแปลง",
    shape: "box", size: [0.1, 0.1, 4.2], pos: [0, 5.85, 0], color: "#8c8c86",
    spec: { "ขนาดจำลอง": "100 × 100 × 4,200 มม.", "วัสดุ": "คอนกรีตอัดแรง", "ตำแหน่ง": "แท่งเสริมพาดระหว่างเสาเหนือหม้อแปลง · ระดับประมาณ" }
  },
  {
    id: "beam", kind: "transformer-beam", name: "คานรองรับหม้อแปลง",
    shape: "box", size: [0.3, 0.15, 4.6], pos: [0, 3.9, 0], color: "#8c8c86",
    spec: { "ขนาด": "150 × 300 × 4,600 มม.", "วัสดุ": "คอนกรีตอัดแรง", "ตำแหน่ง": "พาดผ่านเสาสองต้น · ระดับประมาณ 3.9 ม." }
  },
  {
    id: "transformer-support-brackets", kind: "transformer-support-brackets", name: "ฐานรองคาน SUPPORT TRANSFORMER",
    shape: "box", size: [0.2, 0.24, 0.3], pos: [0, 3.9, 0], color: "#4c5554",
    spec: { "ชนิด": "ฐานรองคานที่เสาแต่ละต้น", "จำนวน": "2 ชุด", "ส่วนประกอบ": "แท่นรับและสลักเกลียว", "หมายเหตุ": "รายละเอียดชิ้นส่วนประกอบแสดงเชิงภาพ" }
  },
  {
    id: "tr", kind: "transformer", name: "หม้อแปลง 1,000 kVA",
    shape: "box", size: [1.3, 1.5, 1.9], pos: [0, 4.85, 0], color: "#687461",
    spec: {
      "พิกัด": "1,000 kVA · 22 kV - 230/400 V",
      "ขนาดโมเดล 3D": "1.3 × 1.5 × 1.9 ม. (สัดส่วนประกอบภาพ ไม่ใช่ขนาดจริง)",
      "ขนาดจริง": "ตรวจสอบป้ายชื่อและข้อมูลผู้ผลิต",
      "ผู้ผลิต": "ไม่ระบุในแบบจำลอง",
      "รุ่น": "ไม่ระบุ",
      "เลขเครื่อง": "ไม่ระบุ"
    }
  },
  {
    id: "ground-rods", kind: "ground-rods", name: "หลักดินเหล็กฉากสำหรับระบบล่อฟ้า",
    shape: "box", size: [0.06, 2, 0.06], pos: [0.36, -0.95, 2.1], color: "#747b79",
    spec: { "หน้าตัด": "เหล็กฉาก 60 × 60 × 5 มม.", "ความยาว": "2,000 มม.", "ตำแหน่ง": "ข้างเสา · ฝังดิน", "หมายเหตุ": "แทนแท่งกลมเดิมในภาพจำลอง" }
  },
  {
    id: "cable-ladder", kind: "cable-ladder", name: "Cable Ladder แรงต่ำ",
    shape: "box", size: [0.5, 3.8, 0.06], pos: [0.4, 1.9, -2.1], color: "#9da6a5",
    spec: { "ชนิด": "Cable Ladder", "ความกว้าง": "500 มม.", "แนวเดิน": "ลงตามเสาถึงตู้ไฟแรงต่ำที่ระดับพื้น", "หมายเหตุ": "ไม่ใช่ท่อร้อยสาย" }
  },
  {
    id: "lv-cables", kind: "lv-cables", name: "สายไฟแรงต่ำบน Cable Ladder",
    shape: "cyl", size: [0.025, 0.025, 3.8], pos: [0.4, 1.9, -2.1], color: "#c5a35b",
    spec: { "สายเฟส": "4 ชุด × (3 × 240 มม.², CV)", "สายนิวทรัล": "4 ชุด × (N × 150 มม.², CV)", "แนวเดิน": "จากหม้อแปลงลง Cable Ladder ถึงตู้ไฟ", "หมายเหตุ": "จำนวน/การจัดวางแสดงเพื่อสื่อสารแบบ ไม่ใช่การกำหนดวิธีติดตั้ง" }
  },
  {
    id: "lv-pad", kind: "lv-pad", name: "ฐานคอนกรีตตู้ไฟแรงต่ำ",
    shape: "box", size: [1.35, 0.2, 1.05], pos: [1.45, 0.1, -2.1], color: "#858780",
    spec: { "ชนิด": "ฐานคอนกรีตที่ระดับพื้น", "ขนาด": "ขนาดจำลองโดยประมาณเพื่อแสดงภาพเท่านั้น" }
  },
  {
    id: "lv-cabinet", kind: "lv-cabinet", name: "ตู้ไฟแรงต่ำ",
    shape: "box", size: [0.8, 2.5, 1.05], pos: [1.45, 1.45, -2.1], color: "#65716a",
    spec: { "ความสูง": "ประมาณ 2.5 ม. · ประเมินจากสัดส่วนในภาพ", "ตำแหน่ง": "ติดตั้งบนฐานคอนกรีตที่พื้น", "ขนาดจริง/รุ่น": "ยังไม่มีสเปกตู้จริง · ห้ามใช้ขนาดจำลองนี้สั่งผลิตหรือติดตั้ง" }
  }
];

const poleLayoutSource = PARTS.find(function (part) { return part.id === "pole1"; });
const beamLayoutSource = PARTS.find(function (part) { return part.id === "beam"; });
const conductorLayoutSource = PARTS.find(function (part) { return part.id === "overhead-conductors"; });
const LAYOUT = Object.freeze({
  poleZ: poleLayoutSource && Array.isArray(poleLayoutSource.pos) ? Math.abs(poleLayoutSource.pos[2]) : NaN,
  beamY: beamLayoutSource && Array.isArray(beamLayoutSource.pos) ? beamLayoutSource.pos[1] : NaN,
  beamHeight: beamLayoutSource && Array.isArray(beamLayoutSource.size) ? beamLayoutSource.size[1] : NaN,
  beamTopY: beamLayoutSource && Array.isArray(beamLayoutSource.pos) && Array.isArray(beamLayoutSource.size)
    ? beamLayoutSource.pos[1] + beamLayoutSource.size[1] / 2
    : NaN,
  wireY: conductorLayoutSource && Array.isArray(conductorLayoutSource.pos)
    ? conductorLayoutSource.pos[1]
    : NaN,
  bushingScale: 1
});
