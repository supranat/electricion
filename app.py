import base64
import functools
import hashlib
import hmac
import html
import inspect
import io
import json
import os
import secrets
import streamlit as st
from PIL import Image

import calculator_page
import header as app_header
import tranformers8
import transformer_3d_page
import transformer_info_page
from site_theme import apply_embedded_theme


LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")  # โลโก้จริงของบริษัท วางไว้ข้าง app.py
HOME_HTML_FILE = "electrical-hud-premium.html"
TRANSFORMER_DETAILS_PAGE = "transformer_details"
CABLE_CALCULATOR_PAGE = "cable_calculator"
CABLE_TABLE_PAGE = "cable_table"
CABLE_DETAIL_PAGE = "cable_detail"
TRAY_GUIDE_PAGE = "tray_guide"
CABLE_HTML_DIR = os.path.join("cables")
FULL_SCREEN_PAGES = {
    TRANSFORMER_DETAILS_PAGE,
    calculator_page.PAGE_TRANSFORMER_INFO,
    calculator_page.PAGE_TRANSFORMER_3D,
    CABLE_CALCULATOR_PAGE,
    CABLE_TABLE_PAGE,
    CABLE_DETAIL_PAGE,
    TRAY_GUIDE_PAGE,
    "poles",
    "breakers",
    "dashboard",
}


st.set_page_config(
    page_title="Attaporn Engineering & Supply | Electrical Calculator",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "⚡",
    layout="wide",
)

# Streamlit รุ่นใหม่เลิกใช้ use_container_width แล้วใช้ width="stretch" แทน (รองรับทั้งสองแบบ)
WIDE = {"width": "stretch"} if "width" in inspect.signature(st.button).parameters else {"use_container_width": True}

# =====================================================================
# 1) ข้อมูลที่แก้ได้ที่เดียว (ชื่อเมนู / ข้อความ) เปลี่ยนตามกระดาษแพลนได้ที่นี่
# =====================================================================
BRAND = {"logo": "AK", "title": "Electrical Calculator", "tagline": "ATTAPORN ENGINEERING & SUPPLY"}

# เมนูบน (ตามแถวบนของกระดาษ) ตอนนี้ทำไว้ 2 หน้า ที่เหลือเพิ่มได้ใน PAGES
TOP_NAV = [
    (calculator_page.PAGE_HOME, "หน้าแรก"),
    (CABLE_CALCULATOR_PAGE, "สายไฟ"),
    (calculator_page.PAGE_CURRENT, "คำนวณกระแส"),
    (calculator_page.PAGE_TRANSFORMER_CALC, "คำนวณหม้อแปลง"),
    (calculator_page.PAGE_TRANSFORMER_INFO, "ข้อมูลหม้อแปลง"),
    (TRANSFORMER_DETAILS_PAGE, "หม้อแปลง 3 เฟส"),
]

# เมนูซ้าย (ตามคอลัมน์ซ้ายของกระดาษ รายการที่ขีดฆ่าไว้ถูกตัดออกแล้ว)
SIDE_MENU = [
    ("contact", "ติดต่อ"),
    ("repair", "การซ่อมบำรุง"),
    ("transformer", "หม้อแปลง"),
    ("poles", "เสาไฟ"),
    ("breakers", "เบรกเกอร์"),
]

# ข้อมูลตัวอย่างของหน้าสินค้า ยังไม่ใช่ข้อมูลจริง ใส่ราคา/รหัสจริงทีหลัง
SAMPLE_PRODUCTS = {
    "transformer": ["หม้อแปลง 3 เฟส 100 kVA", "หม้อแปลง 3 เฟส 160 kVA", "หม้อแปลง 3 เฟส 250 kVA"],
    "poles": ["เสาไฟคอนกรีต 8 ม.", "เสาไฟคอนกรีต 9 ม.", "เสาไฟคอนกรีต 12 ม."],
    "breakers": ["MCCB 3P 63 A", "MCCB 3P 100 A", "MCCB 3P 250 A"],
}
TITLES = {k: v for k, v in TOP_NAV + SIDE_MENU}
TITLES.update({"login": "เข้าสู่ระบบ", "register": "สมัครสมาชิก", "logout": "ออกจากระบบ"})

# =====================================================================
# 2) ธีม (CSS)
# =====================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700;800&display=swap');
:root { --navy:#0B3A75; --blue:#1E6FD9; --bg:#EDF3FA; --side:#DCEBFF; --line:#B9D3F2; --ink:#0B2A4A; --mute:#3F5B7D; }

/* ---------- พื้นฐาน: บังคับธีมน้ำเงินอ่อน ไม่ว่าเครื่องจะเปิดโหมดมืดหรือไม่ ---------- */
html { font-size: 20px !important; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background-color: var(--bg) !important;
  background-image:
    radial-gradient(ellipse at 8% 8%, rgba(255, 112, 48, .10), transparent 30%),
    radial-gradient(ellipse at 92% 18%, rgba(22, 139, 255, .10), transparent 34%),
    radial-gradient(ellipse at 58% 100%, rgba(255, 172, 92, .09), transparent 36%),
    linear-gradient(rgba(22, 92, 170, .035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(22, 92, 170, .035) 1px, transparent 1px),
    linear-gradient(135deg, #F2F7FD 0%, #EAF1F9 52%, #F8F1EB 100%) !important;
  background-size: auto, auto, auto, 34px 34px, 34px 34px, auto !important;
  background-attachment: fixed !important;
}
.stApp, .stApp [data-testid="stMarkdownContainer"] { color: var(--ink) !important; font-family: 'Sarabun', 'Noto Sans Thai', Tahoma, sans-serif !important; line-height: 1.6; }
.stApp [data-testid="stMarkdownContainer"] p, .stApp li, .stApp label p { color: var(--ink) !important; font-size: 1.1rem; }
.stApp label p { font-weight: 600; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: var(--navy) !important; font-weight: 800 !important; font-family: 'Sarabun', Tahoma, sans-serif !important; }
.stApp h3 { font-size: 1.8rem !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--mute) !important; font-size: 1.05rem !important; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1.2rem; max-width: 1180px; }

/* ---------- ปุ่ม (สีชัด ตัวหนังสือใหญ่) ---------- */
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
  background: #FFFFFF !important; border: 2px solid #8DB8EE !important; border-radius: 12px; min-height: 52px;
  transition: transform .18s ease, box-shadow .18s ease, background .18s ease; }
div.stButton > button p, div.stButton > button span, div[data-testid="stFormSubmitButton"] > button p {
  color: var(--navy) !important; font-size: 1.25rem !important; font-weight: 700 !important; }
div.stButton > button[kind="primary"], div.stButton > button[data-testid="stBaseButton-primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"], div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--blue) !important; border-color: var(--blue) !important; }
div.stButton > button[kind="primary"] p, div.stButton > button[data-testid="stBaseButton-primary"] p,
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"] p, div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primaryFormSubmit"] p { color: #FFFFFF !important; }
div.stButton > button:hover:not(:disabled), div[data-testid="stFormSubmitButton"] > button:hover:not(:disabled) {
  transform: translateY(-5px) !important; box-shadow: 0 12px 22px rgba(11,58,117,.25); border-color: var(--blue) !important; }
div.stButton > button:active:not(:disabled) { transform: translateY(-1px) !important; box-shadow: 0 4px 10px rgba(11,58,117,.25); }
div.stButton > button:disabled { opacity: .5; cursor: not-allowed; }
@media (prefers-reduced-motion: reduce) { div.stButton > button, div.stButton > button:hover { transition: none; transform: none !important; } }

/* ---------- 3 ปุ่มกลางหน้า: Login / Register / Logout ---------- */
.st-key-c_login button, .st-key-c_register button, .st-key-c_logout button { min-height: 64px; border-radius: 16px; }
.st-key-c_login button p, .st-key-c_register button p, .st-key-c_logout button p { font-size: 1.4rem !important; }
.st-key-c_login button { background: var(--blue) !important; border-color: var(--blue) !important; }
.st-key-c_register button { background: var(--navy) !important; border-color: var(--navy) !important; }
.st-key-c_login button p, .st-key-c_register button p { color: #FFFFFF !important; }
.st-key-c_logout button { background: #FFFFFF !important; border: 2px solid #C2410C !important; }
.st-key-c_logout button p { color: #C2410C !important; }
.st-key-c_logout button:hover:not(:disabled) { background: #FFF1EA !important; }
.st-key-logout_footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255, 126, 67, .28); }
.st-key-logout_footer div.stButton > button {
  min-height: 46px; border: 1px solid rgba(255, 126, 67, .55) !important;
  border-radius: 12px; background: linear-gradient(135deg, #7f1d1d, #c2410c) !important;
}
.st-key-logout_footer div.stButton > button p { color: #fff !important; font-size: .9rem !important; font-weight: 700 !important; }
.st-key-logout_footer div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(194, 65, 12, .24); }
.ak-auth-title { text-align: center; font-weight: 800; font-size: 1.4rem; color: var(--navy); margin: 18px 0 4px; }
.ak-auth-status { text-align: center; color: var(--mute); font-size: 1.15rem; margin-bottom: 14px; }

/* ---------- ช่องกรอกข้อมูล ---------- */
.stApp input, .stApp textarea { color: var(--ink) !important; background: #FFFFFF !important; font-size: 1.2rem !important; }
div[data-baseweb="input"], div[data-baseweb="base-input"] { background: #FFFFFF !important; border-color: #8DB8EE !important; border-radius: 10px !important; }
div[data-testid="stNumberInput"] button { background: var(--side) !important; color: var(--navy) !important; }
div[data-testid="stForm"] { background: #FFFFFF; border: 1px solid var(--line); border-radius: 14px; }

/* ---------- ผลคำนวณและตาราง ---------- */
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { color: var(--mute) !important; font-size: 1.2rem !important; font-weight: 600; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] div { color: var(--navy) !important; font-size: 3.2rem !important; font-weight: 800 !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 10px; }

/* ---------- ส่วนหัว แบนเนอร์ การ์ด ---------- */
.ak-logo { width:72px; height:72px; border-radius:14px; background:var(--navy); color:#fff; display:flex; align-items:center; justify-content:center; font-size:1.9rem; font-weight:800; letter-spacing:-1px; }
.ak-logo-img { height:76px; width:auto; border-radius:8px; background:#fff; }
.ak-title { font-size:2rem; font-weight:800; color:var(--navy); line-height:1.2; }
.ak-tag { font-size:.95rem; font-weight:700; letter-spacing:1.2px; color:var(--mute); }
.ak-head { display:flex; align-items:center; gap:16px; }
.ak-hero { background:linear-gradient(120deg,#2169CE,#1A5CBF); border-radius:16px; padding:36px 32px; margin:8px 0 18px; }
.stApp .ak-hero h1, .stApp .ak-hero p { color:#FFFFFF !important; }
.stApp .ak-hero h1 { font-size:2.3rem !important; margin:0 0 8px; }
.stApp .ak-hero p { font-size:1.3rem; font-weight:500; margin:0; }
.ak-card { background:linear-gradient(#fff,#fff) padding-box, linear-gradient(135deg,#DC2626 0%,#16A34A 25%,#0EA5E9 50%,#EAB308 75%,#1E3A8A 100%) border-box; border:3px solid transparent; border-radius:14px; padding:18px 20px; font-size:1.15rem; color:var(--ink); }
.ak-card b { color:var(--navy); font-size:1.3rem; }
.stApp [class*="st-key-h_"] button {
  border:3px solid transparent !important;
  background:linear-gradient(#fff,#fff) padding-box, linear-gradient(135deg,#DC2626 0%,#16A34A 25%,#0EA5E9 50%,#EAB308 75%,#1E3A8A 100%) border-box !important;
  border-radius:12px !important;
}
.stApp [class*="st-key-h_"] button:hover:not(:disabled) {
  box-shadow:0 0 0 3px rgba(30,58,138,.14), 0 8px 18px rgba(11,58,117,.2) !important;
}
.ak-note { color:var(--mute); font-size:1.1rem; }
.ak-photo { margin:0 0 16px; background:#fff; border:2px solid var(--line); border-radius:14px; overflow:hidden; transition: transform .18s ease, box-shadow .18s ease; }
.ak-photo:hover { transform: translateY(-5px); box-shadow: 0 12px 22px rgba(11,58,117,.25); border-color: var(--blue); }
.ak-photo img { display:block; width:100%; aspect-ratio:4/3; object-fit:contain; background:#fff; }
.ak-photo figcaption { padding:10px 14px; font-weight:700; font-size:1.15rem; color:var(--navy); border-top:1px solid var(--line); background:var(--side); }
.ak-photo-open { display:block; cursor:zoom-in; }
.ak-photo-modal { position:fixed; z-index:99999; inset:0; display:none; align-items:center; justify-content:center; padding:24px; background:rgba(0,0,0,.88); }
.ak-photo-modal:target { display:flex; }
.ak-photo-modal-backdrop { position:absolute; inset:0; cursor:zoom-out; }
.ak-photo-modal-content { position:relative; z-index:1; width:min(100%,1100px); max-height:100%; padding:16px; border-radius:14px; background:#fff; box-shadow:0 18px 60px rgba(0,0,0,.5); }
.ak-photo-modal-content img { width:auto; height:auto; max-width:100%; max-height:calc(100vh - 110px); aspect-ratio:auto; margin:auto; object-fit:contain; }
.ak-photo-modal-content p { margin:8px 0 0; text-align:center; color:var(--navy); font-size:1rem; }
.ak-photo-modal-close { position:absolute; z-index:2; top:8px; right:12px; width:40px; height:40px; border-radius:50%; background:#fff; color:var(--navy); text-align:center; text-decoration:none; font-size:30px; line-height:38px; box-shadow:0 2px 12px rgba(0,0,0,.35); }
.ak-photo-empty { aspect-ratio:4/3; display:flex; align-items:center; justify-content:center; text-align:center; padding:12px; color:var(--mute); background:#F7FBFF; font-size:1.05rem; }
.ak-photo-empty b { color:var(--navy); font-size:1.2rem; }
.ak-pole-photo { border:1px solid transparent; background:linear-gradient(#fff,#fff) padding-box,linear-gradient(135deg,#0B3A75,#168BFF,#52E5C2) border-box; border-radius:20px; box-shadow:0 12px 30px rgba(11,42,74,.12); }
.ak-pole-photo:hover { box-shadow:0 18px 38px rgba(22,111,217,.25),0 0 0 3px rgba(22,139,255,.12); }
.ak-pole-photo img { aspect-ratio:1/1; }
.ak-pole-photo figcaption { background:linear-gradient(110deg,#071426,#0B3A75); color:#fff; border:0; }
.ak-pole-photo figcaption small { color:#B9D9FF; font-weight:500; }
.pole-guide { --pg-hi:#52E5C2; --pg-muted:#BDD0E4; margin:34px 0; padding:clamp(22px,4vw,42px); overflow:hidden; border:1px solid rgba(82,229,194,.35); border-radius:26px; color:#fff; background:radial-gradient(ellipse at 8% 0%,rgba(22,139,255,.25),transparent 36%),radial-gradient(ellipse at 100% 100%,rgba(82,229,194,.12),transparent 36%),linear-gradient(135deg,#050B14,#071426 55%,#0B1F3A); box-shadow:0 22px 60px rgba(7,20,38,.22); }
.pole-guide * { box-sizing:border-box; }
.pole-guide .pg-eyebrow { color:var(--pg-hi); font-size:13px; font-weight:800; letter-spacing:2px; }
.stApp [data-testid="stMarkdownContainer"] .pole-guide h2 { margin:4px 0 8px; color:#fff!important; font-size:clamp(26px,4vw,40px)!important; }
.stApp [data-testid="stMarkdownContainer"] .pole-guide h3 { display:flex; align-items:center; gap:12px; margin:34px 0 14px; color:#fff!important; font-size:clamp(19px,2.4vw,25px)!important; }
.pole-guide h3:after { content:""; flex:1; height:1px; background:linear-gradient(90deg,rgba(82,229,194,.55),transparent); }
.stApp [data-testid="stMarkdownContainer"] .pole-guide p { margin:0 0 10px; color:var(--pg-muted)!important; font-size:1rem!important; }
.pole-guide .pg-lead { max-width:760px; }
.pole-guide .pg-tag { display:inline-block; padding:3px 12px; border:1px solid var(--pg-hi); border-radius:99px; color:#fff; background:rgba(82,229,194,.12); font-size:13px; }
.pole-guide .pg-steps { display:grid; gap:12px; margin:0; padding:0; list-style:none; counter-reset:pgstep; }
.pole-guide .pg-steps>li { position:relative; padding:18px 20px 18px 72px; border:1px solid rgba(22,139,255,.35); border-radius:16px; background:linear-gradient(150deg,rgba(11,31,58,.92),rgba(0,0,0,.62)); counter-increment:pgstep; transition:transform .2s,border-color .2s,box-shadow .2s; }
.pole-guide .pg-steps>li:hover { transform:translateY(-3px); border-color:var(--pg-hi); box-shadow:0 12px 26px rgba(22,139,255,.18); }
.pole-guide .pg-steps>li:before { content:counter(pgstep); position:absolute; top:17px; left:17px; display:grid; width:38px; height:38px; place-items:center; border-radius:12px; color:#06111F; background:var(--pg-hi); font-weight:900; box-shadow:0 0 18px rgba(82,229,194,.35); }
.pole-guide .pg-steps b { display:block; margin-bottom:4px; color:#fff; font-size:1.03rem; }
.pole-guide .pg-sizes,.pole-guide .pg-files { display:grid; grid-template-columns:repeat(auto-fit,minmax(125px,1fr)); gap:10px; margin:12px 0 4px; }
.pole-guide .pg-photo-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:14px 0 4px; }
.pole-guide .pg-photo-grid .ak-photo { margin:0; }
.pole-guide .pg-photo-grid .ak-pole-photo img { aspect-ratio:1/1; }
.pole-guide .pg-size,.pole-guide .pg-file { padding:12px; border:1px solid rgba(82,229,194,.28); border-radius:13px; text-align:center; background:rgba(22,139,255,.1); }
.pole-guide .pg-size b { display:block; color:var(--pg-hi); font-size:1.22rem; }
.pole-guide .pg-file code { color:#fff; font-weight:700; }
.pole-guide .pg-file small { display:block; color:var(--pg-muted); }
.pole-guide .pg-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; margin-top:14px; }
.pole-guide .pg-box { padding:17px 19px; border:1px solid rgba(22,139,255,.35); border-radius:16px; background:linear-gradient(150deg,rgba(22,139,255,.12),rgba(0,0,0,.55)); }
.pole-guide .pg-box h4 { margin:0 0 8px; color:#fff; font-size:1rem; }
.pole-guide .pg-box ul { margin:0; padding-left:20px; color:var(--pg-muted); }
.pole-guide .pg-box li { margin:5px 0; color:var(--pg-muted); font-size:.95rem; }
.pole-guide .pg-warning { border-color:rgba(255,176,32,.5); background:linear-gradient(150deg,rgba(255,176,32,.12),rgba(0,0,0,.55)); }
.pole-guide .pg-note { margin-top:18px!important; padding:14px 17px; border-left:3px solid var(--pg-hi); border-radius:0 10px 10px 0; background:rgba(22,139,255,.1); }
@media(max-width:800px) { .pole-guide .pg-photo-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media(max-width:560px) { .pole-guide .pg-steps>li { padding:64px 16px 16px; } .pole-guide .pg-photo-grid { grid-template-columns:1fr; } .ak-pole-photo img { aspect-ratio:4/3; } }
@media (prefers-reduced-motion: reduce) { .ak-photo, .ak-photo:hover { transition:none; transform:none; } }
hr.ak { border:0; border-top:2px solid var(--line); margin:10px 0 18px; }

/* ---------- กล่องข้อความแจ้งเตือน ---------- */
.stApp [data-testid="stAlert"] {
  border: 3px solid var(--blue) !important; border-radius: 12px !important;
  background: #FFFFFF !important; box-shadow: 0 0 0 1px rgba(30,111,217,.15) !important;
}
.stApp [data-testid="stAlert"] [data-testid="stMarkdownContainer"],
.stApp [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
  color: var(--ink) !important; font-size: 1.1rem !important;
  font-weight: 700 !important; line-height: 1.6 !important;
}
.stApp [data-testid="stExpander"], .stApp details {
  border: 4px solid #111111 !important; border-radius: 14px !important;
  box-shadow: 0 0 0 3px rgba(17,17,17,.25), 0 0 12px rgba(255,214,0,.45) !important;
}
.stApp [data-testid="stExpander"]:nth-of-type(even), .stApp details:nth-of-type(even) {
  border-color: #FFD600 !important;
  box-shadow: 0 0 0 3px rgba(255,214,0,.35), 0 0 12px rgba(255,214,0,.5) !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def colorize_frames():
    """สลับสีกรอบ expander เป็นดำ/เหลืองด้วย JS (ใช้ st.html จึงไม่ต้อง import components)"""
    st.html(
        """
        <script>
        (() => {
          const COLORS = ["#111111", "#FFD600"];

          function paint() {
            let items = document.querySelectorAll('[data-testid="stExpander"]');
            if (!items.length) items = document.querySelectorAll('details');

            items.forEach(function (el, i) {
              const c = COLORS[i % COLORS.length];
              el.style.setProperty('border', '4px solid ' + c, 'important');
              el.style.setProperty('border-radius', '14px', 'important');
              el.style.setProperty('box-shadow', '0 0 0 3px ' + c + '40', 'important');
            });
          }

          paint();
          if (!window.__akPaintObserver) {
            window.__akPaintObserver = new MutationObserver(paint);
            window.__akPaintObserver.observe(document.body, { childList: true, subtree: true });
          }
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


colorize_frames()


@functools.lru_cache(maxsize=1)
def logo_html():
    """โลโก้จริงจากไฟล์ logo.jpg (ฝังเป็น base64) ถ้าไม่มีไฟล์ใช้กล่องตัวอักษร AK แทน"""
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img class="ak-logo-img" src="data:image/jpeg;base64,{b64}" alt="โลโก้ AK Attaporn Engineering & Supply">'
    return f'<div class="ak-logo">{BRAND["logo"]}</div>'


# =====================================================================
# 3) ระบบสมาชิกแบบง่าย (เก็บใน users.json) เหมาะกับงานต้นแบบเท่านั้น
# =====================================================================
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, encoding="utf-8") as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"ไฟล์บัญชีผู้ใช้ {USERS_FILE} มีรูปแบบ JSON ไม่ถูกต้อง"
                ) from exc
        if not isinstance(users, dict):
            raise ValueError(f"ไฟล์บัญชีผู้ใช้ {USERS_FILE} ต้องเป็น JSON object")
        return users
    return {}


def hash_pw(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 120_000).hex()


def register_user(name, pw):
    if not isinstance(name, str) or not isinstance(pw, str):
        return False, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
    name = name.strip()
    if not name or len(pw) < 6:
        return False, "กรอกชื่อผู้ใช้ และรหัสผ่านอย่างน้อย 6 ตัว"

    users = load_users()
    if name in users:
        return False, "ชื่อผู้ใช้นี้ถูกใช้แล้ว"
    salt = secrets.token_hex(16)
    users[name] = {"salt": salt, "hash": hash_pw(pw, salt), "role": "user"}
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)
    return True, "สมัครสมาชิกสำเร็จ"


def check_login(name, pw):
    if not isinstance(name, str) or not isinstance(pw, str):
        return False
    name = name.strip()
    u = load_users().get(name)
    if not isinstance(u, dict):
        return False
    salt = u.get("salt")
    expected_hash = u.get("hash")
    if not isinstance(salt, str) or not isinstance(expected_hash, str):
        return False
    try:
        actual_hash = hash_pw(pw, salt)
    except (TypeError, ValueError):
        return False
    return secrets.compare_digest(expected_hash, actual_hash)


def get_user_role(username):
    if not isinstance(username, str) or not username:
        return "user"
    user_data = load_users().get(username, {})
    if not isinstance(user_data, dict):
        return "user"
    role = user_data.get("role", "user")
    return role if role in ("user", "admin") else "user"


def is_admin():
    """Check the admin role from stored user data, not form input."""
    return get_user_role(st.session_state.get("user")) == "admin"


SESSION_COOKIE_NAME = "ak_session"


@st.cache_resource
def session_signing_key():
    """Keep signing consistent across Streamlit sessions in this process."""
    configured_secret = os.environ.get("AK_SESSION_SECRET")
    if configured_secret:
        return configured_secret.encode("utf-8")
    return secrets.token_bytes(32)


def create_session_token(username):
    payload = base64.urlsafe_b64encode(
        json.dumps({"username": username}, separators=(",", ":")).encode("utf-8")
    ).rstrip(b"=").decode("ascii")
    signature = hmac.new(
        session_signing_key(),
        payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return f"{payload}.{encoded_signature}"


def verify_session_token(token):
    if not isinstance(token, str):
        return None
    try:
        payload, encoded_signature = token.split(".", 1)
        signature = base64.urlsafe_b64decode(
            encoded_signature + "=" * (-len(encoded_signature) % 4)
        )
        expected_signature = hmac.new(
            session_signing_key(),
            payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
        decoded_payload = base64.urlsafe_b64decode(
            payload + "=" * (-len(payload) % 4)
        )
        session_data = json.loads(decoded_payload)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    username = session_data.get("username") if isinstance(session_data, dict) else None
    if not isinstance(username, str) or username not in load_users():
        return None
    return username


def set_session_cookie(token):
    cookie_value = json.dumps(f"{SESSION_COOKIE_NAME}={token}; Path=/; SameSite=Strict")
    st.html(
        f"""
        <script>
        const cookie = {cookie_value};
        const secure = window.location.protocol === "https:" ? "; Secure" : "";
        document.cookie = cookie + secure;
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def clear_session_cookie():
    st.html(
        f"""
        <script>
        const secure = window.location.protocol === "https:" ? "; Secure" : "";
        document.cookie = "{SESSION_COOKIE_NAME}=; Path=/; Max-Age=0; SameSite=Strict" + secure;
        </script>
        """,
        unsafe_allow_javascript=True,
    )


# =====================================================================
# 4) สถานะและการเปลี่ยนหน้า
# =====================================================================
st.session_state.setdefault("page", calculator_page.PAGE_HOME)
st.session_state.setdefault("user", None)
st.session_state.setdefault("_pending_session_cookie", None)
st.session_state.setdefault("_clear_session_cookie", False)
st.session_state.setdefault("_skip_session_cookie_restore", False)

if st.session_state.pop("_clear_session_cookie", False):
    st.session_state["_skip_session_cookie_restore"] = True
    st.session_state["_pending_session_cookie"] = None
    clear_session_cookie()
elif (
    st.session_state.get("user") is None
    and not st.session_state.get("_skip_session_cookie_restore")
):
    cookie_token = st.context.cookies.get(SESSION_COOKIE_NAME)
    restored_user = verify_session_token(cookie_token)
    if restored_user:
        st.session_state.user = restored_user

pending_session_cookie = st.session_state.pop("_pending_session_cookie", None)
if pending_session_cookie:
    set_session_cookie(pending_session_cookie)

APP_PAGE_QUERY_ROUTES = {
    "home": calculator_page.PAGE_HOME,
    "dashboard": calculator_page.PAGE_HOME,
    "cable_calculator": CABLE_CALCULATOR_PAGE,
    "cable_table": CABLE_TABLE_PAGE,
    "cable_detail": CABLE_DETAIL_PAGE,
    "current_calc": calculator_page.PAGE_CURRENT,
    "equipment_calc": calculator_page.PAGE_EQUIPMENT,
    "transformer_calc": calculator_page.PAGE_TRANSFORMER_CALC,
    "transformer_3d": calculator_page.PAGE_TRANSFORMER_3D,
    "transformer_info": calculator_page.PAGE_TRANSFORMER_INFO,
    "transformer_details": TRANSFORMER_DETAILS_PAGE,
    "poles": "poles",
    "transformer": "transformer",
    "breakers": "breakers",
    "contact": "contact",
    "repair": "repair",
    "login": "login",
    "register": "register",
}

requested_page = st.query_params.get("page")
if requested_page in APP_PAGE_QUERY_ROUTES:
    st.session_state.page = APP_PAGE_QUERY_ROUTES[requested_page]
    del st.query_params["page"]


def go(page):
    st.session_state.page = page
    if "page" in st.query_params:
        del st.query_params["page"]


def do_logout():
    st.session_state.user = None
    st.session_state.page = "logout"
    st.session_state["_pending_session_cookie"] = None
    st.session_state["_clear_session_cookie"] = True


# =====================================================================
# 5) ส่วนหัว (โลโก้ AK + ชื่อเว็บ + Login/Register)
# =====================================================================
# หน้าแรก (HUD) มีแถบหัวของตัวเองแล้ว จึงไม่แสดงส่วนหัวของแอปซ้ำ
if (
    st.session_state.page not in FULL_SCREEN_PAGES
    and st.session_state.page != calculator_page.PAGE_HOME
) or st.session_state.page == "poles":
    app_header.render_header(
        on_navigate=go,
        theme="blue",
        user=st.session_state.user,
    )

NOTE_STYLE = {  # (พื้นหลัง, สีตัวอักษร, สีแถบข้าง)
    "info": ("#E3F0FF", "#0B3A75", "#1E6FD9"),
    "warn": ("#FFF3CD", "#6B4A00", "#D99A00"),
    "error": ("#FDE7E7", "#8A1C1C", "#D64545"),
    "ok": ("#E0F5E8", "#14532D", "#2E9E5B"),
}


def note(kind, text):
    """กล่องข้อความแจ้งเตือนสีชัด (แทน st.warning/info/error ที่สีเพี้ยนเมื่อเปิดโหมดมืด)"""
    try:
        bg, fg, border = NOTE_STYLE[kind]
    except KeyError as exc:
        raise ValueError(f"ชนิดกล่องข้อความไม่รองรับ: {kind}") from exc
    st.markdown(
        f'<div style="border:3px solid {border};border-left-width:10px;border-radius:10px;'
        f'background:{bg};color:{fg};padding:12px 16px;margin:8px 0;'
        f'font-size:1.1rem;font-weight:700;line-height:1.6;overflow-wrap:anywhere">'
        f'{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


# =====================================================================
# 5.5) แกลเลอรีรูปสินค้า (อ่านรูปจากโฟลเดอร์ images/ ข้างไฟล์ app.py)
#      วางรูปตามชื่อไฟล์ในตาราง GALLERY เช่น images/transformer/front.jpg
#      ถ้ายังไม่มีรูป จะขึ้นกรอบ "ยังไม่มีรูป" บอกชื่อไฟล์ที่ต้องวาง
# =====================================================================
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
EXTS = ("jpg", "jpeg", "png", "webp")
GALLERY_TITLE = {
    "transformer": "รูปหม้อแปลง (5 มุม)",
    "poles": "เสาไฟคอนกรีตตั้งแต่ขนาด 6 ถึง 12",
    "breakers": "รูปเบรกเกอร์ไฟ",
}
GALLERY = {  # โฟลเดอร์ -> [(ชื่อไฟล์ไม่รวมนามสกุล, คำอธิบายใต้รูป)]
    "transformer": [("product_front", "ด้านหน้า"), ("left", "ด้านข้างซ้าย"), ("right", "ด้านข้างขวา"),
                    ("back", "ด้านหลัง"), ("top", "ด้านบน")],
    "poles": [("front", "เสาต้นที่ 1"), ("back", "เสาต้นที่ 2"), ("top", "เสาต้นที่ 3"), ("bottom", "เสาต้นที่ 4")],
    "breakers": [("overview", "เบรกเกอร์ไฟ")],
}


def find_image(folder, slot):
    """หาไฟล์รูปตามชื่อ slot (ไม่สนตัวพิมพ์เล็ก/ใหญ่ ทั้งชื่อไฟล์และนามสกุล)"""
    d = os.path.join(IMAGE_DIR, folder)
    if not os.path.isdir(d):
        return None
    for name in sorted(os.listdir(d)):
        base, _, ext = name.rpartition(".")
        if base.lower() == slot and ext.lower() in EXTS:
            return os.path.join(d, name)
    return None


@functools.lru_cache(maxsize=64)
def encode_image(path, _mtime):
    """ย่อรูปไม่เกิน 1100 px แล้วแปลงเป็น base64 (ช่วยให้หน้าเว็บโหลดเร็ว)"""
    with Image.open(path) as im:
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[3])
        bg.thumbnail((1100, 1100))
        buf = io.BytesIO()
        bg.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def photo_card(folder, slot, label, include_modal=True):
    cap = html.escape(label)
    card_class = "ak-pole-photo" if folder == "poles" else ""
    path = find_image(folder, slot)
    if path:
        try:
            b64 = encode_image(path, os.path.getmtime(path))
            if folder == "poles" and slot in ("front", "back", "top", "bottom"):
                modal_id = f"ak-pole-{slot}-modal"
                image = f'<img src="data:image/jpeg;base64,{b64}" alt="{cap}">'
                figure = (
                    f'<figure class="ak-photo {card_class}"><a class="ak-photo-open" href="#{modal_id}" '
                    f'aria-label="ขยายรูป{cap}">{image}</a>'
                    f'<figcaption>{cap}<br><small>คลิกที่รูปเพื่อขยาย</small></figcaption></figure>'
                )
                if not include_modal:
                    return figure, True
                return (
                    figure +
                    f'<div class="ak-photo-modal" id="{modal_id}" role="dialog" '
                    f'aria-modal="true" aria-label="รูป{cap}">'
                    f'<a class="ak-photo-modal-backdrop" href="#" aria-label="ปิดรูป"></a>'
                    f'<div class="ak-photo-modal-content">'
                    f'<a class="ak-photo-modal-close" href="#" aria-label="ปิดรูป">×</a>'
                    f'{image}<p>{cap} · คลิกพื้นหลังหรือ × เพื่อปิด</p></div></div>'
                ), True
            return (f'<figure class="ak-photo {card_class}"><img src="data:image/jpeg;base64,{b64}" alt="{cap}">'
                    f"<figcaption>{cap}</figcaption></figure>"), True
        except (OSError, ValueError) as exc:
            filename = html.escape(os.path.basename(path))
            note("error", f"อ่านไฟล์รูป `{filename}` ไม่ได้: {exc}")
            return (f'<figure class="ak-photo"><div class="ak-photo-empty"><div>'
                    f"<b>อ่านรูปไม่ได้</b><br>{filename}</div></div>"
                    f"<figcaption>{cap}</figcaption></figure>"), False
    hint = html.escape(f"วางไฟล์ images/{folder}/{slot}.jpg")
    return (f'<figure class="ak-photo"><div class="ak-photo-empty"><div><b>ยังไม่มีรูป</b><br>{hint}</div></div>'
            f"<figcaption>{cap}</figcaption></figure>"), False


def gallery(key):
    items = GALLERY.get(key, [])
    if not items:
        return
    st.markdown(f"#### {GALLERY_TITLE[key]}")
    found = 0
    columns_per_row = 2 if key == "poles" else 3
    for i in range(0, len(items), columns_per_row):
        cols = st.columns(columns_per_row)
        for col, (slot, label) in zip(cols, items[i:i + columns_per_row]):
            card, ok = photo_card(key, slot, label)
            found += ok
            col.markdown(card, unsafe_allow_html=True)
    if found < len(items):
        st.caption(f"แสดงรูปได้ {found} จาก {len(items)} รูป โปรดตรวจสอบไฟล์รูปในช่องที่เหลือ")


def build_pole_page_html():
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pole_guide.html")
    with open(template_path, encoding="utf-8") as template_file:
        page_html = template_file.read()

    images = {}
    for slot in ("front", "back", "top", "bottom"):
        path = find_image("poles", slot)
        images[slot] = (
            f"data:image/jpeg;base64,{encode_image(path, os.path.getmtime(path))}"
            if path else None
        )

    placeholder = "__POLE_IMAGES__"
    if placeholder not in page_html:
        raise ValueError(f"ตัวแปรรูปภาพ {placeholder} ไม่พบใน {template_path}")
    return page_html.replace(placeholder, json.dumps(images, ensure_ascii=True))


def page_poles():
    st.markdown(
        """
        <style>
        .block-container { max-width:none!important; padding:0!important; }
        [data-testid="stHeader"] { display:none; }
        .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { background:#F3F7FC!important; }
        iframe[title="ข้อมูลเสาไฟ"] { display:block; width:100%!important; border:0; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        "← กลับหน้าแรก",
        on_click=go,
        args=(calculator_page.PAGE_HOME,),
        key="poles_home",
        **WIDE,
    )
    st.iframe(
        apply_embedded_theme(build_pole_page_html()),
        width="stretch",
        height=2200,
        alt="ข้อมูลเสาไฟ",
    )


def page_tray_guide():
    """Render the interactive cable-tray guide and sizing helper."""
    st.markdown(
        """
        <style>
        .block-container { max-width:none!important; padding:0!important; }
        [data-testid="stHeader"] { display:none; }
        iframe[title="คู่มือรางเดินสายไฟ"] { display:block; width:100%!important; border:0; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        "← กลับหน้ารวมอุปกรณ์",
        on_click=go,
        args=(calculator_page.PAGE_EQUIPMENT,),
        key="tray_guide_back",
        **WIDE,
    )
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tray_guide.html")
    with open(template_path, encoding="utf-8") as template_file:
        page_html = template_file.read()
    st.iframe(page_html, width="stretch", height="content", alt="คู่มือรางเดินสายไฟ")


def page_dashboard():
    st.markdown(
        """
        <style>
        .block-container { max-width:none!important; padding:0!important; }
        [data-testid="stHeader"] { display:none; }
        .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { background:#F3F7FC!important; }
        iframe[title="ศูนย์ควบคุมพลังงานไฟฟ้า"] { display:block; width:100%!important; border:0; }
        .st-key-dashboard_nav_bridge { display:none!important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    allowed_pages = json.dumps(sorted(APP_PAGE_QUERY_ROUTES))
    st.html(
        f"""
        <script>
        (() => {{
          if (window.__akDashboardNav) return;
          window.__akDashboardNav = true;
          const allowedPages = new Set({allowed_pages});
          window.addEventListener("message", (event) => {{
            const message = event.data;
            const fromDashboardFrame = Array.from(document.querySelectorAll("iframe"))
              .some((frame) => frame.contentWindow === event.source);
            if (!fromDashboardFrame || !message || message.type !== "ak-app-navigate" ||
                !allowedPages.has(message.page)) {{
              return;
            }}
            const button = document.querySelector(
              ".st-key-dashboard_nav_" + message.page + " button"
            );
            if (button) button.click();
          }});
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )
    # หน้าแรกใหม่: electrical-hud-premium.html (วางไว้ข้าง app.py)
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), HOME_HTML_FILE)
    with open(template_path, encoding="utf-8") as template_file:
        page_html = template_file.read()
    st.iframe(page_html, width="stretch", height="content", alt="ศูนย์ควบคุมพลังงานไฟฟ้า")
    with st.container(key="dashboard_nav_bridge"):
        for route_key, target_page in APP_PAGE_QUERY_ROUTES.items():
            st.button(
                route_key,
                key=f"dashboard_nav_{route_key}",
                on_click=go,
                args=(target_page,),
            )


def _go_to_cable_detail(cable_id):
    st.session_state["_cable_detail_to_open"] = cable_id
    st.session_state.page = CABLE_DETAIL_PAGE


def page_cable_screen(page_key):
    """Render the standalone cable HTML pages inside Streamlit and bridge their links."""
    page_files = {
        CABLE_CALCULATOR_PAGE: "สายไฟ · AK Electrical Calculator.html",
        CABLE_TABLE_PAGE: "ตารางขนาดสาย.html",
        CABLE_DETAIL_PAGE: "สายไฟ · AK Electrical Calculator.html",
    }
    page_titles = {
        CABLE_CALCULATOR_PAGE: "เครื่องคิดเลขสายไฟ",
        CABLE_TABLE_PAGE: "ตารางขนาดสายไฟ",
        CABLE_DETAIL_PAGE: "รายละเอียดสายไฟ",
    }
    page_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CABLE_HTML_DIR, page_files[page_key])
    with open(page_path, encoding="utf-8") as page_file:
        page_html = page_file.read()

    if page_key == CABLE_TABLE_PAGE:
        image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), CABLE_HTML_DIR, "images")
        for image_name, image_type in (
            ("thw-blue.jpg", "image/jpeg"),
            ("vaf-sample.jpg", "image/jpeg"),
            ("nyy-sample.png", "image/png"),
            ("cv-sample.jpg", "image/jpeg"),
        ):
            image_path = os.path.join(image_dir, image_name)
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("ascii")
            page_html = page_html.replace(
                f"images/{image_name}", f"data:{image_type};base64,{image_data}"
            )

    cable_id = None
    if page_key in (CABLE_CALCULATOR_PAGE, CABLE_DETAIL_PAGE):
        cable_id = st.session_state.pop("_cable_detail_to_open", None)
    if page_key == CABLE_DETAIL_PAGE and cable_id:
        injected_id = json.dumps(cable_id, ensure_ascii=True)
        detail_css = """
        <style>
        :root[data-cable-detail="true"] .wrap { display:none!important; }
        :root[data-cable-detail="true"] dialog#dlg[open] {
          position:fixed; inset:0; margin:0; width:100%; height:100vh; max-height:100vh;
          border:0; border-radius:0; box-shadow:none; background:var(--bg); overflow:auto;
        }
        :root[data-cable-detail="true"] dialog#dlg::backdrop { background:transparent; backdrop-filter:none; }
        </style>
        """
        page_html = page_html.replace("</head>", detail_css + "</head>", 1)
        detail_boot = f"""
        <script>
          window.__AK_CABLE_DETAIL_PAGE = true;
          document.documentElement.dataset.cableDetail = "true";
          open({injected_id});
        </script>
        """
        page_html = page_html.replace("</body>", detail_boot + "</body>", 1)

    link_bridge = """
    <script>
    (() => {
      document.addEventListener("click", (event) => {
        const link = event.target.closest("a[href]");
        if (!link) return;
        const href = link.getAttribute("href") || "";
        let page = null;
        let cable = null;
        if (href.includes("ตารางขนาดสาย.html")) {
          page = "cable_table";
        } else if (href.includes("สายไฟ · AK Electrical Calculator.html")) {
          try { cable = new URL(link.href, window.location.href).searchParams.get("cable"); }
          catch (_) { cable = null; }
          page = cable ? "cable_detail" : "cable_calculator";
        }
        if (!page) return;
        event.preventDefault();
        window.parent.postMessage({type: "ak-app-navigate", page, cable}, "*");
      });
    })();
    </script>
    """
    page_html = page_html.replace("</body>", link_bridge + "</body>", 1)

    st.markdown(
        """
        <style>
        .block-container { max-width:none!important; padding:0!important; }
        [data-testid="stHeader"] { display:none; }
        .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { background:#F3F7FC!important; }
        .st-key-cable_nav_bridge { display:none!important; }
        iframe[title="เครื่องคิดเลขสายไฟ"],iframe[title="ตารางขนาดสายไฟ"],iframe[title="รายละเอียดสายไฟ"] { display:block;width:100%!important;border:0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cable_routes = json.dumps([CABLE_CALCULATOR_PAGE, CABLE_TABLE_PAGE, CABLE_DETAIL_PAGE, "home"])
    cable_ids = json.dumps(["THW", "IEC 01", "VAF", "NYY", "CV"])
    st.html(
        f"""
        <script>
        (() => {{
          if (window.__akCableNav) return;
          window.__akCableNav = true;
          const allowedPages = new Set({cable_routes});
          const allowedCables = new Set({cable_ids});
          window.addEventListener("message", (event) => {{
            const message = event.data;
            const fromCableFrame = Array.from(document.querySelectorAll("iframe"))
              .some((frame) => frame.contentWindow === event.source);
            if (!fromCableFrame || !message || message.type !== "ak-app-navigate" ||
                !allowedPages.has(message.page)) return;
            let selector;
            if (message.page === "{CABLE_DETAIL_PAGE}" && allowedCables.has(message.cable)) {{
              const slug = String(message.cable).toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
              selector = ".st-key-cable_nav_detail_" + slug + " button";
            }} else if (message.page === "home") {{
              selector = ".st-key-cable_nav_home button";
            }} else {{
              selector = ".st-key-cable_nav_" + message.page + " button";
            }}
            const button = document.querySelector(selector);
            if (button) button.click();
          }});
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )

    page_html = apply_embedded_theme(page_html)
    iframe_height = 1000 if page_key == CABLE_DETAIL_PAGE else "content"
    st.iframe(page_html, width="stretch", height=iframe_height, alt=page_titles[page_key])

    with st.container(key="cable_nav_bridge"):
        st.button(
            "กลับหน้าแรก",
            key="cable_nav_home",
            on_click=go,
            args=(calculator_page.PAGE_HOME,),
        )
        st.button(
            "เปิดเครื่องคิดเลขสายไฟ",
            key=f"cable_nav_{CABLE_CALCULATOR_PAGE}",
            on_click=go,
            args=(CABLE_CALCULATOR_PAGE,),
        )
        st.button(
            "เปิดตารางขนาดสายไฟ",
            key=f"cable_nav_{CABLE_TABLE_PAGE}",
            on_click=go,
            args=(CABLE_TABLE_PAGE,),
        )
        st.button(
            "เปิดหน้ารายละเอียดสายไฟ",
            key=f"cable_nav_{CABLE_DETAIL_PAGE}",
            on_click=go,
            args=(CABLE_DETAIL_PAGE,),
        )
        for cable_id in ["THW", "IEC 01", "VAF", "NYY", "CV"]:
            slug = "_".join(cable_id.lower().split())
            st.button(
                f"เปิดรายละเอียด {cable_id}",
                key=f"cable_nav_detail_{slug}",
                on_click=_go_to_cable_detail,
                args=(cable_id,),
            )


# =====================================================================
# 6) หน้าต่าง ๆ
# =====================================================================


def page_products(key):
    if key == "poles":
        page_poles()
        return
    if key == "breakers":
        page_breakers()
        return
    st.subheader(TITLES[key])
    gallery(key)
    st.caption("ข้อมูลตัวอย่าง รอแทนด้วยรายการและราคาจริง")
    st.dataframe(
        [{"ลำดับ": i + 1, "รายการ": n + " (ตัวอย่าง)", "ราคา": "รอระบุ"} for i, n in enumerate(SAMPLE_PRODUCTS[key])],
        hide_index=True, **WIDE,
    )


def _build_breaker_model_html(image_data):
    return f"""
    <!doctype html>
    <html lang="th">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        * {{ box-sizing: border-box; }}
        html, body {{ width: 100%; height: 100%; margin: 0; overflow: hidden; }}
        body {{ color: #eaf7ff; background: transparent; font-family: "Segoe UI", "Noto Sans Thai", Tahoma, sans-serif; }}
        .stage {{ position: relative; display: grid; width: 100%; height: 100%; min-height: 320px; place-items: center; overflow: hidden; background: transparent; }}
        .stage::before {{ content: ""; position: absolute; z-index: 0; left: 20%; right: 20%; bottom: 12%; height: 16%; border-radius: 50%; background: radial-gradient(ellipse, rgba(42, 139, 255, .18), transparent 72%); filter: blur(12px); pointer-events: none; }}
        .model-space {{ position: relative; z-index: 1; display: grid; width: min(100%, 360px); height: min(76%, 340px); min-height: 250px; place-items: center; perspective: 900px; touch-action: none; cursor: grab; user-select: none; }}
        .model-space:active {{ cursor: grabbing; }}
        .product {{ display: block; width: auto; height: auto; max-width: 82%; max-height: 92%; object-fit: contain; transform: rotateX(var(--pitch, -5deg)) rotateY(var(--yaw, -10deg)); transform-style: preserve-3d; filter: drop-shadow(0 22px 18px rgba(0, 0, 0, .38)) drop-shadow(0 0 24px rgba(42, 139, 255, .18)); pointer-events: none; }}
        .caption {{ position: absolute; z-index: 2; right: 12px; bottom: 8px; left: 12px; display: flex; align-items: center; justify-content: center; gap: 12px; color: #b7c8db; font-size: 12px; }}
        .caption button {{ padding: 6px 12px; border: 1px solid rgba(224, 188, 104, .55); border-radius: 999px; background: rgba(15, 34, 54, .72); color: #f5dfaa; font: 700 11px "Segoe UI", "Noto Sans Thai", sans-serif; cursor: pointer; }}
        .caption button:focus-visible {{ outline: 2px solid #f0cf83; outline-offset: 3px; }}
        @media (max-width: 520px) {{ .model-space {{ width: 100%; height: 78%; }} .product {{ max-width: 88%; }} .caption {{ font-size: 11px; }} }}
        @media (prefers-reduced-motion: reduce) {{ .product {{ transition: none; }} }}
      </style>
    </head>
    <body>
      <div class="stage">
        <div class="model-space" id="modelSpace" role="group" aria-label="ลากภาพสินค้า MCCB 3P 100A เพื่อปรับมุม">
          <img class="product" id="product" src="{image_data}" alt="เบรกเกอร์ MCCB 3P 100A">
        </div>
        <div class="caption"><span>ลากเพื่อปรับมุมมอง · ภาพสินค้าแบบเอียง 3D</span><button id="reset" type="button">รีเซ็ตมุม</button></div>
      </div>
      <script>
        (() => {{
          const space = document.getElementById("modelSpace");
          const product = document.getElementById("product");
          const reset = document.getElementById("reset");
          if (!space || !product || !reset) return;
          const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
          let yaw = -10;
          let pitch = -5;
          let dragging = false;
          let previousX = 0;
          let previousY = 0;
          let touched = false;

          function render() {{
            product.style.setProperty("--yaw", yaw + "deg");
            product.style.setProperty("--pitch", pitch + "deg");
          }}

          space.addEventListener("pointerdown", (event) => {{
            dragging = true;
            touched = true;
            previousX = event.clientX;
            previousY = event.clientY;
            space.setPointerCapture(event.pointerId);
          }});
          space.addEventListener("pointermove", (event) => {{
            if (!dragging) return;
            yaw = Math.max(-35, Math.min(35, yaw + (event.clientX - previousX) * .45));
            pitch = Math.max(-22, Math.min(22, pitch - (event.clientY - previousY) * .35));
            previousX = event.clientX;
            previousY = event.clientY;
            render();
          }});
          function stopDragging() {{ dragging = false; }}
          space.addEventListener("pointerup", stopDragging);
          space.addEventListener("pointercancel", stopDragging);
          reset.addEventListener("click", () => {{
            yaw = -10;
            pitch = -5;
            touched = true;
            render();
          }});

          const startedAt = performance.now();
          function animate(time) {{
            if (!reduceMotion && !touched && !dragging) {{
              yaw = -10 + Math.sin((time - startedAt) / 1800) * 7;
              render();
            }}
            requestAnimationFrame(animate);
          }}
          render();
          requestAnimationFrame(animate);
        }})();
      </script>
    </body>
    </html>
    """


@functools.lru_cache(maxsize=2)
def _encode_breaker_background(path, modified_at):
    try:
        with Image.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((1920, 1080))
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=78, optimize=True)
    except (OSError, ValueError) as exc:
        raise ValueError(f"อ่านภาพพื้นหลังเบรกเกอร์ไม่ได้: {path}") from exc
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f'url("data:image/jpeg;base64,{encoded}")'


@functools.lru_cache(maxsize=4)
def _encode_breaker_product_image(path, modified_at):
    try:
        with Image.open(path) as source:
            image = source.convert("RGBA")
            image.thumbnail((600, 600))
            output = io.BytesIO()
            image.save(output, format="PNG", optimize=True)
    except (OSError, ValueError) as exc:
        raise ValueError(f"อ่านรูปสินค้าเบรกเกอร์ไม่ได้: {path}") from exc
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _breaker_product_image(filename):
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "images",
        "breakers",
        filename,
    )
    try:
        modified_at = os.stat(path).st_mtime_ns
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"ไม่พบรูปสินค้าเบรกเกอร์: {path}") from exc
    return _encode_breaker_product_image(path, modified_at)


def _breaker_background_image_css():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "images",
        "breakers",
        "background.jpg",
    )
    try:
        modified_at = os.stat(path).st_mtime_ns
    except FileNotFoundError:
        return "none"
    return _encode_breaker_background(path, modified_at)


def page_breakers():
    background_image = _breaker_background_image_css()
    st.html(
        """
        <style>
        .stApp:has(.breaker-theme) .block-container { max-width: none !important; padding: 0 !important; }
        .stApp:has(.breaker-theme) [data-testid="stHeader"] { display: none; }
        .stApp:has(.breaker-theme),
        .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"],
        .stApp:has(.breaker-theme) [data-testid="stMain"] {
            color: #edf5ff !important;
            background: #F3F7FC !important;
        }
        .stApp:has(.breaker-theme) { position: relative; isolation: isolate; min-height: 100vh; --breaker-background-image: __BREAKER_BACKGROUND_IMAGE__; }
        .stApp:has(.breaker-theme)::before,
        .stApp:has(.breaker-theme)::after { content: ""; position: fixed; inset: 0; pointer-events: none; }
        .stApp:has(.breaker-theme)::before {
            z-index: 0;
            background-image: linear-gradient(135deg, rgba(3,10,22,.72), rgba(4,20,37,.78)),
                linear-gradient(rgba(58,145,255,.045) 1px, transparent 1px),
                linear-gradient(90deg, rgba(58,145,255,.045) 1px, transparent 1px),
                var(--breaker-background-image);
            background-size: auto, 48px 48px, 48px 48px, cover;
            background-position: center, center, center, center;
            background-repeat: no-repeat, repeat, repeat, no-repeat;
        }
        .stApp:has(.breaker-theme)::after {
            z-index: 0;
            background: radial-gradient(circle at 18% 12%, rgba(0,130,255,.14), transparent 35%),
                radial-gradient(circle at 85% 70%, rgba(0,205,255,.10), transparent 34%);
        }
        .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"],
        .stApp:has(.breaker-theme) [data-testid="stMain"],
        .stApp:has(.breaker-theme) [data-testid="stMainBlockContainer"] { position: relative; z-index: 1; background: transparent !important; }
        .stApp:has(.breaker-theme) [data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] { gap: .55rem; }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page {
            --breaker-gold: #efd18b; --breaker-blue: #69b8ff; --breaker-ink: #f3f5fa; --breaker-muted: #b3c1d1;
            width: min(100%, 1540px); margin: 0 auto; padding: 8px clamp(18px, 4vw, 58px); color: var(--breaker-ink);
            font-family: 'Sarabun', 'Noto Sans Thai', Tahoma, sans-serif;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page * { font-family: inherit; }
        .breaker-theme { display: none; }
        .stApp:has(.breaker-theme) .st-key-breakers_home { padding: 14px clamp(18px, 4vw, 58px) 0; }
        .stApp:has(.breaker-theme) .st-key-breakers_home button {
            width: auto !important; min-height: 42px; padding: 0 16px; border: 1px solid rgba(239,209,139,.48) !important;
            border-radius: 10px !important; color: #f7e6bd !important; background: rgba(11,30,52,.85) !important;
        }
        .stApp:has(.breaker-theme) .st-key-breakers_home button p { color: #f7e6bd !important; font-size: .88rem !important; font-weight: 700 !important; }
        .stApp:has(.breaker-theme) .st-key-breakers_home button:hover { border-color: #efd18b !important; background: rgba(22,54,82,.96) !important; }
        .stApp:has(.breaker-theme) .st-key-breakers_home button:focus-visible,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page a:focus-visible {
            outline: 2px solid #efd18b; outline-offset: 3px;
        }
        .breaker-topline { display:flex; align-items:center; justify-content:space-between; gap:16px; padding:4px 0 17px; border-bottom:1px solid rgba(185,211,242,.24); }
        .breaker-brand { display:flex; align-items:center; gap:11px; }
        .breaker-mark { display:grid; place-items:center; width:40px; height:40px; border:1px solid rgba(239,209,139,.55); border-radius:11px; color:#efd18b; background:rgba(18,54,89,.72); font-weight:900; }
        .breaker-brand strong { display:block; color:#f3f5fa; font-size:.95rem; letter-spacing:.07em; }
        .breaker-brand small,.breaker-status { color:#aebfd1; font-size:.68rem; letter-spacing:.1em; }
        .breaker-status { display:flex; align-items:center; gap:8px; }
        .breaker-status i { width:7px; height:7px; border-radius:50%; background:#83d6a0; box-shadow:0 0 10px rgba(131,214,160,.5); animation:breaker-pulse 2.8s ease-in-out infinite; }
        .breaker-anchor-nav { display:flex; gap:8px; flex-wrap:wrap; padding:13px 0 4px; }
        .breaker-anchor-nav a { padding:6px 11px; border:1px solid rgba(185,211,242,.22); border-radius:999px; color:#d3deea; background:rgba(8,24,42,.65); font-size:.76rem; text-decoration:none; }
        .breaker-anchor-nav a:hover { border-color:rgba(239,209,139,.6); color:#efd18b; }
        .breaker-hero { display:grid; grid-template-columns:minmax(0,1.08fr) minmax(330px,.92fr); gap:clamp(22px,4vw,58px); align-items:center; padding:clamp(28px,4vw,54px) 0 28px; }
        .breaker-kicker { margin:0 0 9px; color:#efd18b !important; font-size:.72rem !important; font-weight:800; letter-spacing:.13em; }
        .breaker-hero-copy h1 { max-width:680px; margin:0 0 13px; color:#f5f8fc !important; font-size:clamp(2.15rem,4.2vw,3.75rem) !important; line-height:1.12 !important; letter-spacing:-.025em; }
        .breaker-hero-copy h1 span { color:#efd18b; }
        .breaker-lead { max-width:610px; margin:0; color:#c2cfdd !important; font-size:.98rem !important; line-height:1.8 !important; }
        .breaker-actions { display:flex; flex-wrap:wrap; gap:9px; margin-top:20px; }
        .breaker-actions a { display:inline-flex; align-items:center; gap:8px; min-height:40px; padding:8px 13px; border:1px solid rgba(239,209,139,.46); border-radius:9px; color:#fff1ce; background:rgba(82,59,24,.28); font-size:.78rem; font-weight:700; text-decoration:none; }
        .breaker-actions a:first-child { color:#071426; border-color:#efd18b; background:#efd18b; }
        .breaker-actions a:hover { filter:brightness(1.08); }
        .breaker-hero-note { margin:15px 0 0; color:#9fb0c3 !important; font-size:.72rem !important; line-height:1.6 !important; }
        .breaker-model-panel { padding:13px 14px 8px; border:1px solid rgba(185,211,242,.24); border-radius:15px; background:linear-gradient(145deg,rgba(13,38,64,.88),rgba(5,17,31,.93)); box-shadow:0 16px 36px rgba(0,0,0,.18); }
        .breaker-model-heading { display:flex; justify-content:space-between; gap:12px; align-items:center; color:#dce7f2; font-size:.78rem; font-weight:700; }
        .breaker-model-heading span:last-child { color:#efd18b; font-size:.68rem; }
        .breaker-model-note { margin:0 0 2px; color:#a5b5c6 !important; font-size:.68rem !important; text-align:center; }
        .stApp:has(.breaker-theme) iframe[title="โมเดลเบรกเกอร์ 3D แบบหมุนได้"] { display:block; width:calc(100% - clamp(36px,8vw,116px)) !important; height:330px !important; margin:0 clamp(18px,4vw,58px); border:1px solid rgba(185,211,242,.2); border-radius:12px; background:rgba(6,18,32,.7); box-shadow:inset 0 1px rgba(255,255,255,.035); }
        .breaker-metrics { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:10px 0 39px; }
        .breaker-metric { display:flex; align-items:center; justify-content:space-between; gap:12px; min-height:72px; padding:14px 17px; border:1px solid rgba(185,211,242,.2); border-radius:12px; background:rgba(7,23,41,.78); }
        .breaker-metric strong { color:#efd18b !important; font-size:1.28rem; line-height:1.2; }
        .breaker-metric span { color:#c0ccda !important; font-size:.76rem; text-align:right; }
        .breaker-section-head { display:flex; justify-content:space-between; gap:18px; align-items:end; margin:0 0 15px; }
        .breaker-section-head h2 { margin:3px 0 0; color:#f1f6fc !important; font-size:clamp(1.4rem,2.7vw,1.9rem) !important; }
        .breaker-section-head p { max-width:470px; margin:0; color:#b2c0cf !important; font-size:.76rem !important; text-align:right; }
        .breaker-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:13px; }
        .breaker-card { position:relative; padding:18px; border:1px solid rgba(185,211,242,.22); border-radius:14px; background:linear-gradient(145deg,rgba(15,39,66,.96),rgba(7,19,35,.98)); box-shadow:0 12px 26px rgba(0,0,0,.14); overflow:hidden; }
        .breaker-card { animation:breaker-enter .55s cubic-bezier(.2,.7,.25,1) both; transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease; }
        .breaker-card:nth-child(2) { animation-delay:.08s; }
        .breaker-card:nth-child(3) { animation-delay:.16s; }
        .breaker-card::after { content:""; position:absolute; inset:0; z-index:0; pointer-events:none; background:linear-gradient(112deg,transparent 20%,rgba(255,255,255,.055) 48%,transparent 70%); transform:translateX(-130%); transition:transform .7s ease; }
        .breaker-card:hover { transform:translateY(-4px); border-color:rgba(239,209,139,.68); box-shadow:0 18px 36px rgba(0,0,0,.25),0 0 22px rgba(65,153,230,.08); }
        .breaker-card:hover::after { transform:translateX(130%); }
        .breaker-card-top { display:flex; align-items:center; justify-content:space-between; gap:8px; }
        .breaker-type { color:#efd18b !important; font-size:.66rem; font-weight:800; letter-spacing:.1em; }
        .breaker-badge { padding:3px 8px; border:1px solid rgba(185,211,242,.25); border-radius:999px; color:#c4d0dd !important; background:rgba(185,211,242,.06); font-size:.64rem; }
        .breaker-image-stage { display:grid; min-height:145px; margin:10px 0 7px; place-items:center; }
        .breaker-image-stage img { display:block; width:auto; height:auto; max-width:82%; max-height:145px; object-fit:contain; filter:drop-shadow(0 12px 11px rgba(0,0,0,.32)); transition:transform .24s ease,filter .24s ease; }
        .breaker-card:hover .breaker-image-stage img { transform:scale(1.045); filter:drop-shadow(0 15px 13px rgba(0,0,0,.42)); }
        .breaker-no-image { max-width:230px; padding:12px; border:1px dashed rgba(185,211,242,.28); border-radius:10px; color:#afbdcc; font-size:.75rem; line-height:1.6; text-align:center; }
        .breaker-model { margin:7px 0 0; color:#edf4fb !important; font-size:1.03rem; font-weight:800; }
        .breaker-rating-row { display:flex; align-items:baseline; gap:7px; margin:2px 0 10px; }
        .breaker-card .rating { margin:0; color:#efd18b !important; font-size:2rem !important; font-weight:900; line-height:1.15 !important; }
        .breaker-card .rating-unit { color:#b8c6d4 !important; font-size:.8rem; }
        .breaker-spec { display:flex; justify-content:space-between; gap:12px; padding:8px 0 0; margin-top:8px; border-top:1px solid rgba(185,211,242,.14); color:#b5c3d1 !important; font-size:.72rem; }
        .breaker-spec strong { color:#e6d39d !important; font-weight:700; text-align:right; }
        .breaker-reference { display:grid; grid-template-columns:minmax(120px,170px) minmax(0,1fr); align-items:center; gap:18px; margin-top:16px; padding:14px 17px; border:1px solid rgba(185,211,242,.18); border-radius:12px; background:rgba(6,20,36,.64); }
        .breaker-reference img { display:block; width:100%; max-height:140px; object-fit:contain; filter:drop-shadow(0 10px 9px rgba(0,0,0,.3)); }
        .breaker-reference h3 { margin:3px 0 5px; color:#edf4fb !important; font-size:.95rem !important; }
        .breaker-reference p { margin:0; color:#b4c2d0 !important; font-size:.75rem !important; line-height:1.7 !important; }
        .breaker-photo-feature { display:grid; grid-template-columns:minmax(0,1.1fr) minmax(250px,.9fr); gap:clamp(16px,3vw,30px); align-items:center; margin:18px 0 8px; padding:clamp(14px,2.2vw,22px); border:1px solid rgba(185,211,242,.2); border-radius:15px; background:linear-gradient(120deg,rgba(12,34,58,.9),rgba(7,20,35,.78)); }
        .breaker-photo-feature figure { margin:0; overflow:hidden; border:1px solid rgba(185,211,242,.18); border-radius:11px; background:#f4f6f8; }
        .breaker-photo-feature img { display:block; width:100%; max-height:260px; object-fit:contain; transition:transform .35s ease; }
        .breaker-photo-feature figure:hover img { transform:scale(1.025); }
        .breaker-photo-feature h3 { margin:4px 0 8px; color:#f1f6fc !important; font-size:1.05rem !important; }
        .breaker-photo-feature p { margin:0; color:#b8c6d4 !important; font-size:.78rem !important; line-height:1.75 !important; }
        .breaker-photo-label { display:inline-flex; padding:4px 9px; border:1px solid rgba(239,209,139,.34); border-radius:999px; color:#efd18b; font-size:.65rem; font-weight:800; letter-spacing:.06em; }
        @keyframes breaker-enter { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
        @keyframes breaker-pulse { 0%,100% { box-shadow:0 0 7px rgba(131,214,160,.35); } 50% { box-shadow:0 0 14px rgba(131,214,160,.75); } }
        .breaker-guide-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:11px; margin-top:14px; }
        .breaker-guide-item { display:flex; gap:10px; padding:13px; border:1px solid rgba(185,211,242,.17); border-radius:11px; background:rgba(6,20,36,.54); }
        .breaker-guide-item b { display:grid; place-items:center; flex:0 0 25px; width:25px; height:25px; border-radius:8px; color:#071426; background:#efd18b; font-size:.7rem; }
        .breaker-guide-item span { color:#c1cbd7 !important; font-size:.72rem; line-height:1.55; }
        .breaker-notice { display:flex; gap:11px; align-items:flex-start; margin-top:16px; padding:13px 15px; border:1px solid rgba(239,209,139,.27); border-radius:11px; color:#e0d5bd !important; background:rgba(70,49,21,.2); font-size:.75rem; line-height:1.7; }
        .breaker-notice strong { color:#efd18b !important; }
        .breaker-footer { display:flex; justify-content:space-between; gap:12px; margin-top:27px; padding:13px 0 4px; border-top:1px solid rgba(185,211,242,.18); color:#9eacbd !important; font-size:.66rem; letter-spacing:.06em; }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page p { color:#b7c3d1 !important; }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-kicker,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-type,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-badge,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-spec strong,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-notice strong { color:#efd18b !important; }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-brand strong,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-model,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-section-head h2 { color:#edf4fb !important; }
        @media(max-width:1050px) {
            .breaker-hero { grid-template-columns:minmax(0,1fr) minmax(280px,.9fr); gap:24px; }
            .breaker-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .breaker-guide-grid { grid-template-columns:1fr; }
        }
        @media(max-width:760px) {
            .stApp:has(.breaker-theme) iframe[title="โมเดลเบรกเกอร์ 3D แบบหมุนได้"] { width:calc(100% - 36px) !important; margin:0 18px; }
            .breaker-topline { align-items:flex-start; }
            .breaker-status { font-size:.62rem; }
            .breaker-hero { grid-template-columns:1fr; padding-top:28px; }
            .breaker-hero-copy h1 { font-size:clamp(2rem,8vw,3rem) !important; }
            .breaker-model-panel { max-width:600px; width:100%; margin:0 auto; }
            .breaker-metrics { grid-template-columns:1fr; gap:8px; margin-bottom:29px; }
            .breaker-metric { min-height:58px; }
            .breaker-section-head { display:block; }
            .breaker-section-head p { margin-top:5px; text-align:left; }
            .breaker-grid { grid-template-columns:1fr; }
            .breaker-reference { grid-template-columns:105px minmax(0,1fr); gap:12px; }
            .breaker-photo-feature { grid-template-columns:1fr; }
            .breaker-anchor-nav { overflow-x:auto; flex-wrap:nowrap; }
            .breaker-anchor-nav a { white-space:nowrap; }
        }
        @media(max-width:480px) {
            .breaker-brand small { font-size:.58rem; }
            .breaker-status { max-width:125px; text-align:right; }
            .breaker-reference { grid-template-columns:1fr; }
            .breaker-reference img { max-height:120px; }
            .breaker-footer { display:block; line-height:1.8; }
        }
        @media(prefers-reduced-motion:reduce) {
            .stApp:has(.breaker-theme)::before,.stApp:has(.breaker-theme)::after { animation:none !important; }
            .breaker-status i,.breaker-card { animation:none !important; }
            .breaker-card,.breaker-card::after,.breaker-image-stage img,.breaker-photo-feature img { transition:none !important; }
            .breaker-card:hover { transform:none; }
        }
        </style>
        <div class="breaker-theme" aria-hidden="true"></div>
        """.replace("__BREAKER_BACKGROUND_IMAGE__", background_image),
    )

    st.button(
        "← กลับหน้าแรก",
        on_click=go,
        args=(calculator_page.PAGE_HOME,),
        key="breakers_home",
        **WIDE,
    )

    image_100a = _breaker_product_image("mccb-3p-100a.png")
    image_unrated = _breaker_product_image("mccb-reference-unrated.png")
    image_overview = _breaker_product_image("overview.png")
    product_cards = []
    for product in SAMPLE_PRODUCTS["breakers"]:
        product_parts = product.split()
        model_name = " ".join(product_parts[:-2])
        rating_value, rating_unit = product_parts[-2:]
        if rating_value == "100":
            product_image = (
                '<div class="breaker-image-stage">'
                f'<img src="{image_100a}" alt="เบรกเกอร์ MCCB 3P 100 A จากภาพสินค้า">'
                '</div>'
            )
        else:
            product_image = (
                '<div class="breaker-image-stage"><span class="breaker-no-image">'
                'ยังไม่มีภาพที่ยืนยันว่าเป็นรุ่นนี้'
                '</span></div>'
            )
        product_cards.append(
            '<article class="breaker-card">'
            '<div class="breaker-card-top"><span class="breaker-type">MCCB · 3 POLE</span>'
            '<span class="breaker-badge">ข้อมูลตัวอย่าง</span></div>'
            f'{product_image}'
            f'<h3 class="breaker-model">{html.escape(model_name)}</h3>'
            f'<div class="breaker-rating-row"><p class="rating">{html.escape(rating_value)}</p>'
            f'<span class="rating-unit">{html.escape(rating_unit)}</span></div>'
            '<div class="breaker-spec"><span>จำนวนขั้ว</span><strong>3P</strong></div>'
            '<div class="breaker-spec"><span>ข้อมูลรุ่นและราคา</span><strong>รอยืนยัน</strong></div>'
            '</article>'
        )

    st.markdown(
        '<div class="breaker-page">'
        '<header class="breaker-topline">'
        '<div class="breaker-brand"><div class="breaker-mark">AK</div>'
        '<div><strong>AK ELECTRICAL</strong><small>ENGINEERING &amp; SUPPLY</small></div></div>'
        '<div class="breaker-status"><i></i> PROTECTION SYSTEMS</div>'
        '</header>'
        '<nav class="breaker-anchor-nav" aria-label="ทางลัดในหน้า">'
        '<a href="#breaker-catalog">รายการเบรกเกอร์</a><a href="#breaker-guide">ข้อมูลที่ควรตรวจสอบ</a>'
        '</nav>'
        '</div>',
        unsafe_allow_html=True,
    )

    hero_copy, model_column = st.columns([1.08, 0.92], gap="large", vertical_alignment="center")
    with hero_copy:
        st.markdown(
            '<section class="breaker-page breaker-hero-copy">'
            '<p class="breaker-kicker">SMART POWER · CIRCUIT PROTECTION</p>'
            '<h1>เบรกเกอร์ไฟฟ้า<br><span>ข้อมูลรวมในหน้าเดียว</span></h1>'
            '<p class="breaker-lead">เลือกดูรายการเบรกเกอร์ตัวอย่าง ภาพสินค้า และข้อมูลเบื้องต้นได้ในหน้าเดียว '
            'จัดลำดับให้อ่านภาพรวมก่อน แล้วค่อยเปรียบเทียบรายการ</p>'
            '<div class="breaker-actions"><a href="#breaker-catalog">ดูรายการเบรกเกอร์ <span>↓</span></a>'
            '<a href="#breaker-guide">ข้อมูลที่ควรตรวจสอบ</a></div>'
            '<p class="breaker-hero-note">ภาพ MCCB 3P 100 A เป็นภาพตัวอย่าง และหมุนปรับมุมได้ด้วยเมาส์หรือการสัมผัส</p>'
            '</section>',
            unsafe_allow_html=True,
        )
    with model_column:
        st.markdown(
            '<div class="breaker-page breaker-model-panel"><div class="breaker-model-heading">'
            '<span>ภาพตัวอย่างเบรกเกอร์</span><span>MCCB · 3P · 100 A</span></div></div>',
            unsafe_allow_html=True,
        )
        st.iframe(
            _build_breaker_model_html(image_100a),
            width="stretch",
            height=330,
            tab_index=0,
            alt="ภาพสินค้าเบรกเกอร์ 3D แบบเอียงและหมุนได้",
        )
        st.markdown(
            '<div class="breaker-page breaker-model-note">ลากภาพเพื่อปรับมุมมอง · กดรีเซ็ตมุมเพื่อกลับตำแหน่งเริ่มต้น</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="breaker-page">'
        '<section class="breaker-metrics" aria-label="ภาพรวมรายการ">'
        '<div class="breaker-metric"><strong>03</strong><span>รายการตัวอย่างในหน้านี้</span></div>'
        '<div class="breaker-metric"><strong>MCCB</strong><span>ชนิดที่แสดงในรายการตัวอย่าง</span></div>'
        '<div class="breaker-metric"><strong>3P</strong><span>จำนวนขั้วตามชื่อรายการ</span></div>'
        '</section>'
        '<section id="breaker-catalog" aria-labelledby="breaker-catalog-title">'
        '<div class="breaker-section-head"><div><p class="breaker-kicker">CATALOG · SAMPLE RANGE</p>'
        '<h2 id="breaker-catalog-title">รายการเบรกเกอร์</h2></div>'
        '<p>รายการนี้เป็นตัวอย่าง ยังไม่ใช่การยืนยันสินค้าคงคลังหรือรายละเอียดจากผู้ผลิต</p></div>'
        f'<div class="breaker-grid">{"".join(product_cards)}</div>'
        '</section>'
        '<section class="breaker-reference" aria-label="ภาพอ้างอิงที่ยังไม่ระบุรุ่น">'
        f'<img src="{image_unrated}" alt="ภาพเบรกเกอร์ MCCB อ้างอิง ยังไม่ระบุรุ่นหรือพิกัด">'
        '<div><span class="breaker-type">REFERENCE IMAGE</span>'
        '<h3>ภาพอ้างอิงที่ยังไม่ผูกกับรายการสินค้า</h3>'
        '<p>ยังยืนยันรุ่นและกระแสพิกัดจากภาพนี้ไม่ได้ จึงแสดงแยกจากรายการ 63 A และ 250 A</p></div>'
        '</section>'
        '<section class="breaker-photo-feature" aria-label="ภาพรวมเบรกเกอร์หลายรูปแบบ">'
        f'<figure><img src="{image_overview}" alt="ภาพรวมตัวอย่างเบรกเกอร์หลายรูปแบบและหลายแบรนด์" loading="lazy"></figure>'
        '<div><span class="breaker-photo-label">PHOTO OVERVIEW</span>'
        '<h3>ภาพรวมอุปกรณ์หลายรูปแบบ</h3>'
        '<p>ภาพนี้ใช้ประกอบการดูรูปทรงเบื้องต้น มีสินค้าหลายแบบและหลายแบรนด์รวมอยู่ด้วย '
        'จึงไม่ได้จับคู่กับพิกัดหรือรุ่นใดในรายการด้านบน</p></div>'
        '</section>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="breaker-page"><section id="breaker-guide" aria-labelledby="breaker-guide-title">'
        '<div class="breaker-section-head"><div><p class="breaker-kicker">BEFORE YOU COMPARE</p>'
        '<h2 id="breaker-guide-title">ข้อมูลที่ควรตรวจสอบก่อนเลือก</h2></div>'
        '<p>ใช้รายละเอียดจากฉลากและเอกสารผู้ผลิตของรุ่นจริง</p></div>'
        '<div class="breaker-guide-grid">'
        '<div class="breaker-guide-item"><b>01</b><span>รุ่น ผู้ผลิต และจำนวนขั้ว</span></div>'
        '<div class="breaker-guide-item"><b>02</b><span>กระแสและแรงดันพิกัด</span></div>'
        '<div class="breaker-guide-item"><b>03</b><span>ความสามารถตัดกระแสลัดวงจรและข้อมูลการตัดวงจร</span></div>'
        '</div>'
        '<div class="breaker-notice"><span aria-hidden="true">ⓘ</span><span>'
        '<strong>หมายเหตุ:</strong> รายการรุ่นและกระแสที่แสดงเป็นข้อมูลตัวอย่างจากรายการเดิม '
        'ข้อมูลแรงดันพิกัด ความสามารถตัดกระแสลัดวงจร เส้นโค้งการตัด ราคา และสถานะสินค้ายังรอยืนยัน '
        'โปรดตรวจสอบเอกสารผู้ผลิตและข้อมูลจริงก่อนเลือกใช้งาน</span></div>'
        '</section><footer class="breaker-footer"><span>AK ELECTRICAL · CIRCUIT PROTECTION</span>'
        '<span>ข้อมูลตัวอย่างสำหรับการเปิดดู</span></footer></div>',
        unsafe_allow_html=True,
    )


def page_transformer_details():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: none !important;
            padding: 0 !important;
        }
        [data-testid="stHeader"] {
            display: none;
        }
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: #F3F7FC !important;
        }
        iframe[title="หน้าหม้อแปลงสามเฟส"] {
            display: block;
            width: 100% !important;
            height: calc(100vh - 64px) !important;
            min-height: 600px;
            border: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        "← กลับหน้าแรก",
        on_click=go,
        args=(calculator_page.PAGE_HOME,),
        key="transformer_details_home",
        **WIDE,
    )
    page_html = tranformers8.HTML.replace(
        "</style>",
        ".site{display:none!important}.wrap{width:100%;max-width:none;padding:0 clamp(16px,3vw,48px) 60px}</style>",
        1,
    )
    page_html = apply_embedded_theme(page_html)
    st.iframe(page_html, width="stretch", height=900, alt="หน้าหม้อแปลงสามเฟส")


def page_transformer_3d():
    transformer_3d_page.show_transformer_3d_fullscreen(go)


def page_contact():
    st.subheader("ติดต่อ")
    st.markdown('<div class="ak-card">โทร: (รอระบุ)<br>LINE: (รอระบุ)<br>ที่อยู่: (รอระบุ)<br>เวลาทำการ: (รอระบุ)</div>', unsafe_allow_html=True)


def page_repair():
    st.subheader("การซ่อมบำรุง")
    st.caption("รายการตัวอย่าง รอแก้เป็นบริการที่รับจริง")
    st.markdown("- ตรวจเช็กตู้ไฟและเบรกเกอร์\n- ซ่อมบำรุงหม้อแปลง\n- งานเดินสายและติดตั้งอุปกรณ์ไฟฟ้า")


AUTH_PAGE_CSS = """
<style>
[data-testid="stAppViewContainer"]:has(.auth-theme) {
    background:
        radial-gradient(ellipse at 8% 12%, rgba(255, 73, 28, .2), transparent 34%),
        radial-gradient(ellipse at 92% 84%, rgba(255, 153, 55, .14), transparent 36%),
        linear-gradient(rgba(255, 115, 55, .04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 115, 55, .04) 1px, transparent 1px),
        linear-gradient(135deg, #13090b, #211013 52%, #100b0d) !important;
    background-size: auto, auto, 42px 42px, 42px 42px, auto !important;
    background-attachment: fixed !important;
}
[data-testid="stAppViewContainer"]:has(.auth-theme) [data-testid="stMain"] {
    background: transparent !important;
}
[data-testid="stAppViewContainer"]:has(.auth-theme) [data-testid="stMainBlockContainer"] {
    max-width: 1120px;
    padding: clamp(1rem, 3vw, 2rem) clamp(.75rem, 3vw, 1.5rem) 3rem;
}
.auth-theme { display: none; }
.auth-showcase {
    position: relative;
    isolation: isolate;
    display: flex;
    min-height: 570px;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
    padding: clamp(26px, 4vw, 48px);
    border: 1px solid rgba(255, 132, 75, .36);
    border-radius: 26px;
    background:
        radial-gradient(ellipse at 82% 18%, rgba(255, 89, 39, .24), transparent 38%),
        linear-gradient(145deg, rgba(48, 23, 21, .97), rgba(22, 14, 17, .98));
    box-shadow: 0 24px 70px rgba(0, 0, 0, .34), 0 0 38px rgba(255, 78, 20, .1);
}
.auth-showcase::before {
    position: absolute;
    z-index: -1;
    right: -140px;
    bottom: -180px;
    width: 420px;
    height: 420px;
    border: 1px solid rgba(255, 159, 93, .26);
    border-radius: 50%;
    box-shadow: 0 0 0 28px rgba(255, 145, 75, .035), 0 0 0 70px rgba(255, 145, 75, .025);
    content: "";
}
.auth-showcase-top {
    display: flex;
    align-items: center;
    gap: 14px;
}
.auth-brand-mark {
    display: grid;
    width: 54px;
    height: 54px;
    flex: none;
    place-items: center;
    border: 1px solid rgba(255, 157, 90, .7);
    border-radius: 16px;
    color: #fff3e9;
    background: linear-gradient(145deg, rgba(255, 83, 34, .28), rgba(255, 153, 66, .08));
    box-shadow: 0 0 24px rgba(255, 84, 34, .22), inset 0 0 18px rgba(255, 128, 63, .12);
    font-size: 1.25rem;
    font-weight: 900;
}
.auth-brand-copy { min-width: 0; }
.auth-brand-copy b {
    display: block;
    color: #fff3e9;
    font-size: 1rem;
}
.auth-brand-copy span {
    display: block;
    margin-top: 2px;
    color: #caa99b;
    font-size: .68rem;
    letter-spacing: .12em;
}
.auth-live {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    width: fit-content;
    margin-top: 44px;
    padding: 7px 11px;
    border: 1px solid rgba(255, 144, 82, .32);
    border-radius: 999px;
    color: #ffc078;
    background: rgba(255, 102, 47, .08);
    font-size: .7rem;
    font-weight: 800;
    letter-spacing: .1em;
}
.auth-live::before {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #ff8b38;
    box-shadow: 0 0 12px #ff5a24;
    content: "";
    animation: authPulse 1.8s ease-in-out infinite;
}
.auth-showcase h1 {
    margin: 15px 0 10px;
    color: #fff3e9 !important;
    font-size: clamp(2rem, 4vw, 3rem) !important;
    font-weight: 850 !important;
    line-height: 1.2;
}
.stApp [data-testid="stMarkdownContainer"] .auth-showcase-lead {
    max-width: 460px;
    margin: 0;
    color: #e6c6b7 !important;
    font-size: .96rem !important;
    line-height: 1.8 !important;
}
.auth-benefits {
    display: grid;
    gap: 12px;
    margin-top: 30px;
}
.auth-benefit {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #f5e1d7;
    font-size: .84rem;
}
.auth-benefit i {
    display: grid;
    width: 28px;
    height: 28px;
    flex: none;
    place-items: center;
    border: 1px solid rgba(255, 151, 84, .35);
    border-radius: 9px;
    color: #ffad68;
    background: rgba(255, 91, 40, .1);
    font-size: .8rem;
    font-style: normal;
}
.auth-showcase-foot {
    margin-top: 36px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 126, 67, .2);
    color: #bd9e91;
    font-size: .7rem;
    line-height: 1.65;
}
.auth-form-intro {
    margin: 4px 0 16px;
}
.auth-form-intro h2 {
    margin: 0;
    color: #fff3e9 !important;
    font-size: 1.55rem !important;
    font-weight: 800 !important;
}
.stApp [data-testid="stMarkdownContainer"] .auth-form-intro p {
    margin: 5px 0 0;
    color: #c9aaa0 !important;
    font-size: .82rem !important;
}
.st-key-auth_form_column [data-testid="stForm"] {
    padding: clamp(20px, 3vw, 30px);
    border: 1px solid rgba(255, 126, 67, .34);
    border-radius: 22px;
    background:
        radial-gradient(ellipse at 100% 0, rgba(255, 89, 39, .1), transparent 45%),
        linear-gradient(145deg, rgba(33, 20, 20, .97), rgba(22, 16, 18, .98)) !important;
    box-shadow: 0 18px 54px rgba(0, 0, 0, .3);
}
.st-key-auth_form_column [data-testid="stWidgetLabel"] p {
    margin-bottom: 5px;
    color: #f4ded3 !important;
    font-size: .78rem !important;
    font-weight: 700 !important;
}
.st-key-auth_form_column [data-baseweb="input"] > div {
    min-height: 48px;
    border: 1px solid rgba(255, 146, 97, .32) !important;
    border-radius: 12px;
    background: rgba(18, 14, 15, .88) !important;
    transition: border-color .2s ease, box-shadow .2s ease;
}
.st-key-auth_form_column [data-baseweb="input"] > div:focus-within {
    border-color: #ff743b !important;
    box-shadow: 0 0 0 3px rgba(255, 101, 43, .16);
}
.st-key-auth_form_column input {
    color: #fff4ec !important;
    caret-color: #ff7138;
    background: transparent !important;
    font-size: .85rem !important;
}
.st-key-auth_form_column input::placeholder { color: #90766e !important; }
.st-key-auth_form_column [data-testid="stFormSubmitButton"] { margin-top: 12px; }
.st-key-auth_form_column div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primaryFormSubmit"] {
    min-height: 52px;
    border: 1px solid rgba(255, 175, 112, .65) !important;
    border-radius: 13px;
    background: linear-gradient(110deg, #b72b18, #f05220 56%, #ff9b45) !important;
    box-shadow: 0 8px 24px rgba(255, 77, 26, .24);
    transition: transform .2s ease, box-shadow .2s ease, filter .2s ease;
}
.st-key-auth_form_column [data-testid="stFormSubmitButton"] button p {
    color: #fff !important;
    font-size: .9rem !important;
    font-weight: 800 !important;
}
.st-key-auth_form_column div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    transform: translateY(-2px);
    filter: brightness(1.08);
    box-shadow: 0 12px 30px rgba(255, 77, 26, .36);
}
.st-key-auth_form_column [data-testid="stButton"] button {
    width: 100%;
    min-height: 46px;
    border: 1px solid rgba(255, 126, 67, .35) !important;
    border-radius: 12px;
    color: #ffe4d5 !important;
    background: rgba(50, 25, 20, .55) !important;
    transition: transform .2s ease, box-shadow .2s ease, background .2s ease;
}
.st-key-auth_form_column [data-testid="stButton"] button p {
    color: #ffe4d5 !important;
    font-size: .78rem !important;
    font-weight: 700 !important;
}
.st-key-auth_form_column [data-testid="stButton"] button:hover {
    transform: translateY(-2px);
    background: rgba(105, 41, 24, .75) !important;
    box-shadow: 0 8px 22px rgba(255, 77, 26, .16);
}
.stApp .st-key-auth_form_column [data-testid="stMarkdownContainer"] .auth-switch-note {
    margin: 15px 0 7px;
    color: #bda096 !important;
    font-size: .74rem !important;
    text-align: center;
}
.st-key-auth_form_column [data-testid="stAlert"] {
    border: 1px solid rgba(255, 150, 91, .42) !important;
    border-radius: 12px;
    background: rgba(65, 35, 25, .92) !important;
}
.st-key-auth_form_column [data-testid="stAlert"] p { color: #fff0e6 !important; }
.st-key-auth_form_column [data-testid="stCaptionContainer"] p {
    color: #bda096 !important;
    font-size: .7rem !important;
}
@keyframes authPulse {
    0%, 100% { opacity: .7; transform: scale(.85); }
    50% { opacity: 1; transform: scale(1.15); }
}
@media (max-width: 900px) {
    .auth-showcase { min-height: 0; }
    .auth-live { margin-top: 28px; }
}
@media (max-width: 760px) {
    .auth-showcase { padding: 24px; }
    .st-key-auth_form_column [data-testid="stForm"] { padding: 20px; }
}
@media (prefers-reduced-motion: reduce) {
    .auth-live::before,
    .st-key-auth_form_column button,
    .auth-showcase { animation: none !important; transition: none !important; }
}
</style>
"""


def render_auth_intro(title, description):
    st.markdown(AUTH_PAGE_CSS, unsafe_allow_html=True)
    st.markdown('<div class="auth-theme"></div>', unsafe_allow_html=True)
    left_column, right_column = st.columns([1.05, 0.95], gap="large")
    with left_column:
        st.markdown(
            f"""
            <section class="auth-showcase">
              <div>
                <div class="auth-showcase-top">
                  <div class="auth-brand-mark">AK</div>
                  <div class="auth-brand-copy">
                    <b>Electrical Calculator</b>
                    <span>ATTAPORN ENGINEERING &amp; SUPPLY</span>
                  </div>
                </div>
                <div class="auth-live">ELECTRICAL WORKSPACE</div>
                <h1>{html.escape(title)}</h1>
                <p class="auth-showcase-lead">{html.escape(description)}</p>
                <div class="auth-benefits">
                  <div class="auth-benefit"><i>01</i><span>รวมเครื่องมือคำนวณและข้อมูลอุปกรณ์ไฟฟ้า</span></div>
                  <div class="auth-benefit"><i>02</i><span>เข้าถึงหน้าใช้งานได้สะดวกในที่เดียว</span></div>
                  <div class="auth-benefit"><i>03</i><span>รหัสผ่านจัดเก็บเป็นค่าแฮช ไม่เก็บเป็นข้อความตรง</span></div>
                </div>
              </div>
              <div class="auth-showcase-foot">AK ELECTRICAL · POWERING YOUR WORKFLOW</div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    with right_column:
        auth_column = st.container(key="auth_form_column")
        with auth_column:
            st.markdown(
                '<div class="auth-form-intro">'
                f'<h2>{html.escape(title)}</h2>'
                f'<p>{html.escape(description)}</p>'
                "</div>",
                unsafe_allow_html=True,
            )
    return auth_column


def page_login():
    auth_column = render_auth_intro(
        "เข้าสู่ระบบ",
        "ลงชื่อเข้าใช้เพื่อไปต่อในศูนย์เครื่องมือไฟฟ้า",
    )
    with auth_column:
        with st.form("login"):
            u = st.text_input(
                "ชื่อผู้ใช้",
                placeholder="กรอกชื่อผู้ใช้",
                autocomplete="username",
            )
            p = st.text_input(
                "รหัสผ่าน",
                type="password",
                placeholder="กรอกรหัสผ่าน",
                autocomplete="current-password",
            )
            submitted = st.form_submit_button("เข้าสู่ระบบ", type="primary")
        if submitted:
            if check_login(u.strip(), p):
                st.session_state.user = u.strip()
                st.session_state.page = calculator_page.PAGE_HOME
                st.session_state["_pending_session_cookie"] = create_session_token(u.strip())
                st.session_state["_skip_session_cookie_restore"] = False
                st.rerun()
            note("error", "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        st.markdown(
            '<p class="auth-switch-note">ยังไม่มีบัญชีใช่ไหม?</p>',
            unsafe_allow_html=True,
        )
        st.button(
            "สมัครสมาชิก",
            on_click=go,
            args=("register",),
            key="to_reg",
        )
        st.button(
            "กลับหน้าแรก",
            on_click=go,
            args=(calculator_page.PAGE_HOME,),
            key="login_home",
        )


def page_register():
    auth_column = render_auth_intro(
        "สร้างบัญชีใหม่",
        "สมัครสมาชิกเพื่อเริ่มใช้งานเครื่องมือของ AK Electrical",
    )
    with auth_column:
        with st.form("register"):
            u = st.text_input(
                "ชื่อผู้ใช้",
                placeholder="ตั้งชื่อผู้ใช้",
                autocomplete="username",
            )
            p = st.text_input(
                "รหัสผ่าน",
                type="password",
                placeholder="อย่างน้อย 6 ตัวอักษร",
                autocomplete="new-password",
                help="ใช้รหัสผ่านอย่างน้อย 6 ตัวอักษร",
            )
            p2 = st.text_input(
                "ยืนยันรหัสผ่าน",
                type="password",
                placeholder="กรอกรหัสผ่านอีกครั้ง",
                autocomplete="new-password",
            )
            submitted = st.form_submit_button("สมัครสมาชิก", type="primary")
        if submitted:
            if not u.strip() or len(p) < 6:
                note("error", "กรอกชื่อผู้ใช้ และรหัสผ่านอย่างน้อย 6 ตัว")
            elif p != p2:
                note("error", "รหัสผ่านไม่ตรงกัน")
            else:
                ok, msg = register_user(u.strip(), p)
                note("ok" if ok else "error", msg)
        st.markdown(
            '<p class="auth-switch-note">มีบัญชีอยู่แล้ว?</p>',
            unsafe_allow_html=True,
        )
        st.button(
            "เข้าสู่ระบบ",
            on_click=go,
            args=("login",),
            key="to_login",
        )
        st.button(
            "กลับหน้าแรก",
            on_click=go,
            args=(calculator_page.PAGE_HOME,),
            key="register_home",
        )


def page_logout():
    st.subheader("ออกจากระบบแล้ว")
    st.write("ขอบคุณที่ใช้งาน")
    st.button(
        "กลับหน้าแรก",
        on_click=go,
        args=(calculator_page.PAGE_HOME,),
        key="back_home",
    )


ROUTES = {
    calculator_page.PAGE_HOME: page_dashboard,
    CABLE_CALCULATOR_PAGE: lambda: page_cable_screen(CABLE_CALCULATOR_PAGE),
    CABLE_TABLE_PAGE: lambda: page_cable_screen(CABLE_TABLE_PAGE),
    CABLE_DETAIL_PAGE: lambda: page_cable_screen(CABLE_DETAIL_PAGE),
    TRAY_GUIDE_PAGE: page_tray_guide,
    calculator_page.PAGE_CURRENT: lambda: calculator_page.render_current_calc_page(go),
    calculator_page.PAGE_EQUIPMENT: lambda: calculator_page.render_calculator_page(go),
    calculator_page.PAGE_TRANSFORMER_CALC: lambda: calculator_page.render_transformer_calc_page(go),
    calculator_page.PAGE_TRANSFORMER_INFO: lambda: transformer_info_page.render_transformer_info_page(go),
    TRANSFORMER_DETAILS_PAGE: page_transformer_details,
    calculator_page.PAGE_TRANSFORMER_3D: page_transformer_3d,
    "contact": page_contact, "repair": page_repair,
    "login": page_login, "register": page_register, "logout": page_logout,
}
page = st.session_state.page
if page in SAMPLE_PRODUCTS:
    page_products(page)
else:
    ROUTES.get(page, page_dashboard)()

# Shared visual polish for Streamlit pages. The dashboard and standalone
# product/calculator documents keep their own layouts, while controls stay
# consistent across the app.
st.markdown(
    """
    <style>
    :root {
      --ak-ink: #17324f;
      --ak-muted: #5b7188;
      --ak-blue: #176fc5;
      --ak-blue-dark: #104f8c;
      --ak-line: #d7e2ee;
      --ak-surface: #ffffff;
      --ak-soft: #f3f7fc;
    }
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stWidgetLabel"],
    .stApp [data-testid="stCaptionContainer"] {
      font-family: 'Sarabun', 'Noto Sans Thai', Tahoma, sans-serif !important;
    }
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stWidgetLabel"] p {
      color: var(--ak-ink) !important;
      line-height: 1.65;
    }
    .stApp [data-testid="stCaptionContainer"] p {
      color: var(--ak-muted) !important;
    }
    .stApp div.stButton > button,
    .stApp div[data-testid="stFormSubmitButton"] > button {
      min-height: 46px;
      border: 1px solid #bfd2e6 !important;
      border-radius: 12px !important;
      background: var(--ak-surface) !important;
      box-shadow: 0 2px 7px rgba(23, 50, 79, .05);
      transition: background .16s ease, border-color .16s ease, box-shadow .16s ease;
    }
    .stApp div.stButton > button p,
    .stApp div[data-testid="stFormSubmitButton"] > button p {
      color: var(--ak-blue-dark) !important;
      font-weight: 700 !important;
    }
    .stApp div.stButton > button:hover:not(:disabled),
    .stApp div[data-testid="stFormSubmitButton"] > button:hover:not(:disabled) {
      border-color: var(--ak-blue) !important;
      background: #f0f7ff !important;
      box-shadow: 0 5px 14px rgba(23, 50, 79, .1);
      transform: translateY(-1px);
    }
    .stApp div.stButton > button:focus-visible,
    .stApp div[data-testid="stFormSubmitButton"] > button:focus-visible {
      outline: 3px solid rgba(23, 111, 197, .24) !important;
      outline-offset: 2px;
    }
    .stApp input, .stApp textarea {
      border-radius: 10px !important;
      color: var(--ak-ink) !important;
    }
    .stApp [data-baseweb="input"],
    .stApp [data-baseweb="select"] > div {
      border-color: #c7d7e7 !important;
      border-radius: 10px !important;
      background: #fff !important;
    }
    .stApp [data-testid="stForm"] {
      border: 1px solid var(--ak-line) !important;
      border-radius: 16px !important;
      box-shadow: 0 8px 24px rgba(23, 50, 79, .05);
    }
    .stApp [data-testid="stAlert"] {
      border-width: 1px !important;
      border-radius: 12px !important;
      box-shadow: none !important;
    }
    .stApp [data-testid="stExpander"], .stApp details {
      border: 1px solid var(--ak-line) !important;
      border-radius: 14px !important;
      box-shadow: none !important;
      background: #fff;
    }
    .stApp [data-testid="stDataFrame"] {
      border: 1px solid var(--ak-line) !important;
      border-radius: 12px !important;
      overflow: hidden;
    }
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) {
      color: var(--ak-ink) !important;
      background: #f3f7fc !important;
      background-image: none !important;
    }
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) [data-testid="stMain"],
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) [data-testid="stMainBlockContainer"] {
      color: var(--ak-ink) !important;
      background: transparent !important;
    }
    /* Keep the calculator page in a normal vertical scroll flow, including touch devices. */
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) [data-testid="stMain"] {
      min-height: 100dvh !important;
      overflow-x: hidden !important;
      overflow-y: auto !important;
      overscroll-behavior-y: contain;
      -webkit-overflow-scrolling: touch;
      touch-action: pan-y;
    }
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) [data-testid="stMainBlockContainer"] {
      overflow: visible !important;
      touch-action: pan-y;
    }
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-fx,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme)::before,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme)::after {
      display: none !important;
    }
    @media (max-width: 760px) {
      .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme),
      .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) [data-testid="stMain"] {
        background-attachment: scroll !important;
      }
    }
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-hero,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-card,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-term-body {
      color: var(--ak-ink) !important;
      background: #fff !important;
      border-color: var(--ak-line) !important;
      box-shadow: 0 8px 24px rgba(23, 50, 79, .06) !important;
      text-shadow: none !important;
    }
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-title,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-hero p,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-card p,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-term-body,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-term-body .k,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-term-msg {
      color: var(--ak-ink) !important;
      text-shadow: none !important;
    }
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-kicker,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-cyan,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-amber,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-term-body .v {
      color: var(--ak-blue) !important;
      text-shadow: none !important;
    }
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-sub,
    .stApp [data-testid="stAppViewContainer"]:has(.transformer-calc-theme) .tc-legend {
      color: var(--ak-muted) !important;
    }
    @media (max-width: 640px) {
      .stApp div.stButton > button,
      .stApp div[data-testid="stFormSubmitButton"] > button { min-height: 48px; }
    }
    @media (prefers-reduced-motion: reduce) {
      .stApp div.stButton > button,
      .stApp div[data-testid="stFormSubmitButton"] > button { transition: none !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
if st.session_state.user:
    with st.container(key="logout_footer"):
        _, logout_column = st.columns([5, 1])
        logout_column.button(
            "ออกจากระบบ",
            on_click=do_logout,
            key="header_logout",
            **WIDE,
        )

