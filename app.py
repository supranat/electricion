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


LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")  # โลโก้จริงของบริษัท วางไว้ข้าง app.py
HOME_HTML_FILE = "electrical-hud-premium.html"  # ไฟล์หน้าแรกใหม่ (วางไว้ข้าง app.py)
TRANSFORMER_DETAILS_PAGE = "transformer_details"
FULL_SCREEN_PAGES = {
    TRANSFORMER_DETAILS_PAGE,
    calculator_page.PAGE_TRANSFORMER_INFO,
    calculator_page.PAGE_TRANSFORMER_3D,
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
        theme="fire",
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
        .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { background:#000!important; }
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
        build_pole_page_html(),
        width="stretch",
        height=2200,
        alt="ข้อมูลเสาไฟ",
    )


def page_dashboard():
    st.markdown(
        """
        <style>
        .block-container { max-width:none!important; padding:0!important; }
        [data-testid="stHeader"] { display:none; }
        .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { background:#000!important; }
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
    st.html(
        """
        <style>
        .stApp:has(.breaker-theme) .block-container {
            max-width: none !important;
            padding: 0 !important;
        }
        .stApp:has(.breaker-theme) [data-testid="stHeader"] {
            display: none;
        }
        .stApp:has(.breaker-theme),
        .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"],
        .stApp:has(.breaker-theme) [data-testid="stMain"] {
            color: #eaf4ff !important;
            background: linear-gradient(135deg, #06101f, #091a31 54%, #06101d) !important;
        }
        .stApp:has(.breaker-theme) {
            position: relative;
            isolation: isolate;
            min-height: 100vh;
            --breaker-background-image: __BREAKER_BACKGROUND_IMAGE__;
        }
        .stApp:has(.breaker-theme)::before,
        .stApp:has(.breaker-theme)::after {
            content: "";
            position: fixed;
            pointer-events: none;
        }
        .stApp:has(.breaker-theme)::before {
            inset: -12%;
            z-index: 0;
            background-image:
                linear-gradient(rgba(2, 8, 23, .3), rgba(2, 8, 23, .55)),
                linear-gradient(rgba(58, 145, 255, .065) 1px, transparent 1px),
                linear-gradient(90deg, rgba(58, 145, 255, .065) 1px, transparent 1px),
                var(--breaker-background-image);
            background-size: auto, 48px 48px, 48px 48px, cover;
            background-position: center, center, center, center;
            background-repeat: no-repeat, repeat, repeat, no-repeat;
            transform: translate3d(-2.5%, -1.5%, 0) scale(1.08);
            animation: breakerBackgroundDrift 14s ease-in-out infinite alternate;
            will-change: transform;
        }
        .stApp:has(.breaker-theme)::after {
            inset: -2%;
            z-index: 0;
            background:
                radial-gradient(circle at 22% 30%, rgba(0, 110, 255, .17), transparent 38%),
                radial-gradient(circle at 80% 68%, rgba(0, 207, 255, .12), transparent 36%),
                radial-gradient(circle at 54% 92%, rgba(214, 173, 88, .07), transparent 34%);
            animation: breakerEnergyPulse 5.8s ease-in-out infinite alternate;
            will-change: opacity, transform;
        }
        .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"],
        .stApp:has(.breaker-theme) [data-testid="stMain"] {
            position: relative;
            z-index: 1;
            background: transparent !important;
        }
        .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"]::before {
            content: "";
            position: fixed;
            z-index: 0;
            top: 0;
            left: 0;
            width: 100%;
            height: 130px;
            pointer-events: none;
            background: linear-gradient(
                180deg,
                transparent,
                rgba(0, 140, 255, .025) 28%,
                rgba(0, 190, 255, .085) 50%,
                rgba(0, 140, 255, .025) 72%,
                transparent
            );
            animation: breakerScanMove 7.5s linear infinite;
            will-change: transform;
        }
        .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"]::after {
            content: "";
            position: fixed;
            z-index: 0;
            inset: -35%;
            pointer-events: none;
            background: linear-gradient(
                112deg,
                transparent 43%,
                rgba(0, 170, 255, .018) 47%,
                rgba(45, 205, 255, .13) 50%,
                rgba(0, 170, 255, .025) 53%,
                transparent 58%
            );
            mix-blend-mode: screen;
            transform: translate3d(-55%, 0, 0);
            animation: breakerLightSweep 9s ease-in-out infinite;
            will-change: transform;
        }
        @keyframes breakerBackgroundDrift {
            0% { transform: translate3d(-3%, -2%, 0) scale(1.1); }
            100% { transform: translate3d(3%, 2%, 0) scale(1.1); }
        }
        @keyframes breakerEnergyPulse {
            from { opacity: .55; transform: scale(1); }
            to { opacity: 1; transform: scale(1.035); }
        }
        @keyframes breakerScanMove {
            from { transform: translateY(-100vh); }
            to { transform: translateY(100vh); }
        }
        @keyframes breakerLightSweep {
            0%, 12% { transform: translate3d(-55%, 0, 0); opacity: 0; }
            28% { opacity: .8; }
            70% { opacity: .8; }
            88%, 100% { transform: translate3d(55%, 0, 0); opacity: 0; }
        }
        .stApp:has(.breaker-theme) [data-testid="stMainBlockContainer"] {
            position: relative;
            z-index: 1;
            background: transparent !important;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page {
            --breaker-cyan: #efd18b;
            --breaker-gold: #d6ad58;
            --breaker-blue: #398cff;
            --breaker-ink: #f3f5fa;
            --breaker-muted: #a9b7c8;
            color: var(--breaker-ink);
            width: min(100%, 1600px);
            margin: 0 auto;
            padding: 12px clamp(18px, 4vw, 64px) 10px;
            font-family: 'Sarabun', 'Noto Sans Thai', Tahoma, sans-serif;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page * {
            font-family: inherit;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page p,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page h1,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page h2,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page h3,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page span,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page strong {
            font-family: inherit !important;
        }
        .breaker-theme { display: none; }
        .stApp:has(.breaker-theme) .st-key-breakers_home {
            padding: 12px clamp(18px, 4vw, 64px) 0;
        }
        .stApp:has(.breaker-theme) .st-key-breakers_home button {
            width: auto !important;
            min-height: 44px;
            padding: 0 20px;
            border: 1px solid rgba(224, 188, 104, .62) !important;
            border-radius: 12px !important;
            background: linear-gradient(120deg, rgba(91, 67, 29, .88), rgba(17, 43, 69, .96)) !important;
            box-shadow: inset 0 1px rgba(255,255,255,.08), 0 5px 18px rgba(3,10,20,.25);
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
        }
        .stApp:has(.breaker-theme) .st-key-breakers_home button p {
            color: #f7e6bd !important;
            font-size: .9rem !important;
            font-weight: 700 !important;
            letter-spacing: .02em;
        }
        .stApp:has(.breaker-theme) .st-key-breakers_home button:hover {
            transform: translateY(-2px);
            border-color: #f2d78e !important;
            box-shadow: 0 8px 24px rgba(3,10,20,.34), 0 0 18px rgba(214,173,88,.18);
        }
        .stApp:has(.breaker-theme) .st-key-breakers_home button:focus-visible {
            outline: 2px solid #f2d78e;
            outline-offset: 3px;
        }
        .breaker-topline {
            display: flex; align-items: center; justify-content: space-between;
            gap: 16px; padding: 4px 0 24px;
            border-bottom: 1px solid rgba(214, 173, 88, .22);
        }
        .breaker-brand { display: flex; align-items: center; gap: 12px; }
        .breaker-mark {
            display: grid; place-items: center; width: 42px; height: 42px;
            border: 1px solid rgba(224, 188, 104, .68); border-radius: 12px;
            background: linear-gradient(145deg, rgba(57, 140, 255, .28), rgba(214, 173, 88, .12));
            color: var(--breaker-cyan); font-weight: 900; letter-spacing: -1px;
            box-shadow: 0 0 24px rgba(0, 181, 255, .12), 0 0 14px rgba(214,173,88,.12);
        }
        .breaker-brand strong { display: block; font-size: 1rem; letter-spacing: .08em; }
        .breaker-brand small, .breaker-status { color: var(--breaker-muted); font-size: .76rem; letter-spacing: .12em; }
        .breaker-status { display: flex; align-items: center; gap: 8px; }
        .breaker-status i { width: 8px; height: 8px; border-radius: 50%; background: #e6c372; box-shadow: 0 0 12px rgba(230,195,114,.75); }
        .breaker-hero {
            display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(300px, .9fr);
            gap: clamp(24px, 5vw, 72px); align-items: center; padding: clamp(36px, 6vw, 86px) 0 42px;
        }
        .breaker-kicker { color: var(--breaker-cyan) !important; font-size: .78rem !important; font-weight: 800; letter-spacing: .16em; }
        .breaker-hero-copy h1 {
            max-width: 760px; margin: 12px 0 16px; font-size: clamp(2.5rem, 6vw, 5.2rem) !important;
            line-height: 1.08 !important; letter-spacing: -.035em;
            background: linear-gradient(100deg, #fff 8%, #dceaff 48%, #f0d48f 100%);
            -webkit-background-clip: text; background-clip: text; color: transparent !important;
            text-shadow: 0 0 42px rgba(51, 147, 255, .16), 0 0 22px rgba(214,173,88,.12);
        }
        .breaker-lead { max-width: 690px; color: #b6c8dc !important; font-size: 1.04rem !important; line-height: 1.9 !important; }
        .breaker-chips { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 24px; }
        .breaker-chip {
            padding: 7px 12px; border: 1px solid rgba(214, 173, 88, .38); border-radius: 999px;
            background: linear-gradient(120deg, rgba(10, 40, 70, .72), rgba(72, 54, 25, .34)); color: #f0dfb8 !important; font-size: .8rem;
        }
        .stApp:has(.breaker-theme) iframe[title="โมเดลเบรกเกอร์ 3D แบบหมุนได้"] {
            display: block; width: 100% !important; height: 400px !important; border: 0;
            background: transparent;
        }
        .breaker-hero-copy { padding-top: 18px; }
        .breaker-model-note { margin: 2px 0 0; color: #8fa9c3 !important; font-size: .78rem !important; }
        .breaker-metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 4px 0 54px; }
        .breaker-metric {
            padding: 18px 20px; border: 1px solid rgba(214, 173, 88, .22); border-radius: 16px;
            background: linear-gradient(145deg, rgba(13, 36, 64, .88), rgba(7, 21, 39, .94));
            box-shadow: inset 0 1px rgba(255,255,255,.035), 0 12px 30px rgba(0,0,0,.12);
        }
        .breaker-metric strong { display: block; color: #f0d48f !important; font-size: 1.6rem; line-height: 1.2; letter-spacing: .02em; }
        .breaker-metric span { color: var(--breaker-muted) !important; font-size: .82rem; }
        .breaker-section-head { display: flex; justify-content: space-between; gap: 18px; align-items: end; margin-bottom: 18px; }
        .breaker-section-head h2 { margin: 4px 0 0; color: #f0f8ff !important; font-size: clamp(1.6rem, 3vw, 2.2rem) !important; }
        .breaker-section-head p { margin: 0; color: #b7c3d1 !important; font-size: .86rem !important; }
        .breaker-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
        .breaker-card {
            position: relative; padding: 22px; border: 1px solid rgba(214, 173, 88, .25); border-radius: 18px;
            background:
                linear-gradient(115deg, rgba(214,173,88,.045), transparent 42%),
                linear-gradient(150deg, rgba(15, 39, 68, .96), rgba(7, 19, 36, .98));
            box-shadow: 0 16px 40px rgba(0, 0, 0, .16); transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
            overflow: hidden;
        }
        .breaker-card:hover { transform: translateY(-4px); border-color: rgba(240, 212, 143, .72); box-shadow: 0 20px 46px rgba(0, 118, 255, .14), 0 0 22px rgba(214,173,88,.12); }
        .breaker-card::after { content: ""; position: absolute; width: 120px; height: 120px; right: -52px; top: -60px; border-radius: 50%; background: rgba(214, 173, 88, .1); filter: blur(2px); }
        .breaker-image-stage {
            display: grid; min-height: 190px; margin: 8px 0 16px; place-items: center;
        }
        .breaker-image-stage img {
            display: block; width: auto; height: auto; max-width: 90%; max-height: 180px;
            object-fit: contain; filter: drop-shadow(0 14px 12px rgba(0, 0, 0, .35));
        }
        .breaker-no-image {
            max-width: 220px; color: #a9b7c8; font-size: .82rem; line-height: 1.65; text-align: center;
        }
        .breaker-reference {
            display: grid; grid-template-columns: minmax(110px, 180px) minmax(0, 1fr);
            align-items: center; gap: 20px; margin-top: 20px; padding: 14px 0;
            border-top: 1px solid rgba(214, 173, 88, .18);
        }
        .breaker-reference img {
            display: block; width: 100%; max-height: 190px; object-fit: contain;
            filter: drop-shadow(0 14px 12px rgba(0, 0, 0, .35));
        }
        .breaker-reference h3 { margin: 4px 0 6px; color: #eef4fa !important; font-size: 1rem !important; }
        .breaker-reference p { margin: 0; color: var(--breaker-muted) !important; font-size: .84rem !important; }
        .breaker-card-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
        .breaker-type { color: #e8c879 !important; font-size: .72rem; font-weight: 800; letter-spacing: .12em; }
        .breaker-badge { padding: 4px 9px; border: 1px solid rgba(214, 173, 88, .42); border-radius: 999px; color: #f0dfb8 !important; background: rgba(214,173,88,.08); font-size: .72rem; }
        .breaker-model { margin: 18px 0 2px; color: #eef4fa !important; font-size: 1.38rem; font-weight: 800; letter-spacing: .015em; }
        .breaker-card .rating { margin: 0; color: #f0d48f !important; font-size: clamp(2rem, 3.5vw, 2.8rem) !important; font-weight: 900; line-height: 1.2 !important; text-shadow: 0 0 18px rgba(214,173,88,.16); }
        .breaker-spec { display: flex; justify-content: space-between; gap: 12px; padding: 12px 0 0; margin-top: 16px; border-top: 1px solid rgba(214, 173, 88, .18); color: var(--breaker-muted) !important; font-size: .84rem; }
        .breaker-spec strong { color: #e8c879 !important; }
        .breaker-notice {
            display: flex; gap: 13px; align-items: flex-start; margin-top: 22px; padding: 16px 18px;
            border: 1px solid rgba(214, 173, 88, .34); border-radius: 14px;
            background: linear-gradient(110deg, rgba(75, 53, 20, .24), rgba(11, 34, 57, .55)); color: #e5d7b8 !important; font-size: .88rem;
        }
        .breaker-notice strong { color: #f0d48f !important; }
        .breaker-footer { margin-top: 44px; padding-top: 18px; border-top: 1px solid rgba(214, 173, 88, .2); color: #9eacbd !important; font-size: .76rem; letter-spacing: .08em; }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page p {
            color: #b7c3d1 !important;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-kicker,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-type,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-badge,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-spec strong,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-notice strong {
            color: #efd18b !important;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-hero-copy h1 {
            color: transparent !important;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-brand strong,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-model,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-section-head h2 {
            color: #eef4fa !important;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-metric strong,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-card .rating {
            color: #f0d48f !important;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-brand small,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-status,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-metric span,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-spec,
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page .breaker-footer {
            color: #a9b7c8 !important;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page button {
            color: #f5e5bd;
        }
        .stApp:has(.breaker-theme) [data-testid="stMarkdownContainer"] .breaker-page :focus-visible {
            outline: 2px solid #efd18b;
            outline-offset: 3px;
        }
        @media (max-width: 900px) {
            .breaker-hero { grid-template-columns: 1fr; }
            .breaker-grid { grid-template-columns: 1fr 1fr; }
        }
        @media (max-width: 600px) {
            .breaker-topline { align-items: flex-start; }
            .breaker-status { font-size: .65rem; }
            .breaker-metrics { grid-template-columns: 1fr; gap: 9px; margin-bottom: 38px; }
            .breaker-metric { display: flex; justify-content: space-between; align-items: center; }
            .breaker-grid { grid-template-columns: 1fr; }
            .breaker-reference { grid-template-columns: 110px minmax(0, 1fr); gap: 12px; }
            .breaker-section-head { display: block; }
            .breaker-section-head p { margin-top: 6px; }
            .stApp:has(.breaker-theme)::before {
                background-size: auto, 38px 38px, 38px 38px, cover;
                animation-duration: 18s;
            }
            .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"]::before { height: 90px; }
        }
        @media (prefers-reduced-motion: reduce) {
            .stApp:has(.breaker-theme)::before,
            .stApp:has(.breaker-theme)::after,
            .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"]::before,
            .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"]::after {
                animation: none !important;
            }
            .stApp:has(.breaker-theme)::before {
                transform: none;
                will-change: auto;
            }
            .stApp:has(.breaker-theme)::after {
                transform: none;
                opacity: .7;
                will-change: auto;
            }
            .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"]::before {
                opacity: 0;
                will-change: auto;
            }
            .stApp:has(.breaker-theme) [data-testid="stAppViewContainer"]::after {
                opacity: 0;
                will-change: auto;
            }
        }
        @media (prefers-reduced-motion: reduce) {
            .breaker-card, .breaker-card:hover { transition: none; transform: none; }
            .stApp:has(.breaker-theme) .st-key-breakers_home button { transition: none; }
        }
        </style>
        <div class="breaker-theme" aria-hidden="true"></div>
        """.replace("__BREAKER_BACKGROUND_IMAGE__", _breaker_background_image_css()),
    )
    st.button(
        "← กลับหน้าแรก",
        on_click=go,
        args=(calculator_page.PAGE_HOME,),
        key="breakers_home",
    )

    image_100a = _breaker_product_image("mccb-3p-100a.png")
    image_unrated = _breaker_product_image("mccb-reference-unrated.png")
    product_cards = []
    for product in SAMPLE_PRODUCTS["breakers"]:
        product_parts = product.split()
        model_name = " ".join(product_parts[:-2])
        rating = " ".join(product_parts[-2:])
        if rating == "100 A":
            product_image = (
                '<div class="breaker-image-stage">'
                f'<img src="{image_100a}" alt="เบรกเกอร์ MCCB 3P 100 A จากภาพที่ผู้ใช้ให้มา">'
                '</div>'
            )
        else:
            product_image = (
                '<div class="breaker-image-stage"><span class="breaker-no-image">'
                'ยังไม่มีรูปสินค้ารุ่นนี้ที่ยืนยันพิกัดได้</span></div>'
            )
        product_cards.append(
            '<article class="breaker-card">'
            '<div class="breaker-card-top"><span class="breaker-type">MCCB · 3-POLE</span>'
            '<span class="breaker-badge">ตัวอย่าง</span></div>'
            f'{product_image}'
            f'<div class="breaker-model">{html.escape(model_name)}</div>'
            f'<p class="rating">{html.escape(rating)}</p>'
            '<div class="breaker-spec"><span>จำนวนขั้ว</span><strong>3P</strong></div>'
            '<div class="breaker-spec"><span>ข้อมูลรุ่นและราคา</span><strong>รอยืนยัน</strong></div>'
            '</article>'
        )

    st.markdown(
        '<main class="breaker-page">'
        '<div class="breaker-topline">'
        '<div class="breaker-brand"><div class="breaker-mark">AK</div>'
        '<div><strong>AK ELECTRICAL</strong><small>ENGINEERING &amp; SUPPLY</small></div></div>'
        '<div class="breaker-status"><i></i> PROTECTION SYSTEMS</div>'
        '</div>'
        '</main>',
        unsafe_allow_html=True,
    )
    hero_copy, model_column = st.columns([1.05, 0.95], gap="large", vertical_alignment="center")
    with hero_copy:
        st.markdown(
            '<div class="breaker-page breaker-hero-copy">'
            '<p class="breaker-kicker">SMART POWER · CIRCUIT PROTECTION</p>'
            '<h1>ระบบป้องกัน<br>วงจรไฟฟ้า</h1>'
            '<p class="breaker-lead">เลือกดูเบรกเกอร์ตัวอย่าง พร้อมภาพและข้อมูลเบื้องต้นในหน้าเดียว '
            'ออกแบบให้อ่านง่ายทั้งบนคอมพิวเตอร์และโทรศัพท์มือถือ</p>'
            '<div class="breaker-chips"><span class="breaker-chip">MCCB</span>'
            '<span class="breaker-chip">3 Pole</span><span class="breaker-chip">Interactive 3D</span></div>'
            '<p class="breaker-model-note">ภาพสินค้า 100A แบบเอียง/หมุนเพื่อแสดงมิติ 3D ไม่ใช่โมเดล GLB</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    with model_column:
        st.iframe(
            _build_breaker_model_html(image_100a),
            width="stretch",
            height=400,
            tab_index=0,
            alt="ภาพสินค้าเบรกเกอร์ 3D แบบเอียงและหมุนได้",
        )

    st.markdown(
        '<main class="breaker-page">'
        '<section class="breaker-metrics" aria-label="ภาพรวมรายการ">'
        '<div class="breaker-metric"><strong>03</strong><span>รายการตัวอย่าง</span></div>'
        '<div class="breaker-metric"><strong>MCCB</strong><span>ชนิดอุปกรณ์ในรายการตัวอย่าง</span></div>'
        '<div class="breaker-metric"><strong>3P</strong><span>จำนวนขั้วตามชื่อรุ่นตัวอย่าง</span></div>'
        '</section>'
        '<section aria-labelledby="breaker-catalog-title">'
        '<div class="breaker-section-head"><div><p class="breaker-kicker">CATALOG / SAMPLE RANGE</p>'
        '<h2 id="breaker-catalog-title">รายการเบรกเกอร์</h2></div>'
        '<p>ตัวเลขด้านล่างเป็นรายการตัวอย่าง ไม่ใช่การยืนยันสินค้าคงคลัง</p></div>'
        f'<div class="breaker-grid">{"".join(product_cards)}</div>'
        '</section>'
        '<section class="breaker-reference" aria-label="ภาพสินค้าอ้างอิงที่ยังไม่ระบุรุ่น">'
        f'<img src="{image_unrated}" alt="ภาพเบรกเกอร์ MCCB อ้างอิง ยังไม่ระบุรุ่นหรือกระแสพิกัด">'
        '<div><span class="breaker-type">REFERENCE IMAGE</span>'
        '<h3>ภาพเบรกเกอร์อ้างอิง</h3>'
        '<p>ภาพนี้ยังยืนยันรุ่นและกระแสพิกัดไม่ได้ จึงไม่ผูกกับรายการ 63A หรือ 250A</p></div>'
        '</section>'
        '<div class="breaker-notice"><span aria-hidden="true">ⓘ</span><span>'
        '<strong>หมายเหตุ:</strong> รุ่นและกระแสพิกัดที่แสดงเป็นข้อมูลตัวอย่างจากรายการเดิม '
        'ยังไม่มีข้อมูลแรงดันพิกัด ความสามารถตัดกระแสลัดวงจร เส้นโค้งการตัด ผู้ผลิต ราคา '
        'หรือสถานะสินค้า โปรดตรวจสอบเอกสารผู้ผลิตและข้อมูลจริงก่อนเลือกใช้งาน</span></div>'
        '<footer class="breaker-footer">AK ELECTRICAL · CIRCUIT PROTECTION · '
        'ข้อมูลเพื่อแสดงตัวอย่างเท่านั้น</footer>'
        '</main>',
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
            background: #071426 !important;
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
if st.session_state.user:
    with st.container(key="logout_footer"):
        _, logout_column = st.columns([5, 1])
        logout_column.button(
            "ออกจากระบบ",
            on_click=do_logout,
            key="header_logout",
            **WIDE,
        )

