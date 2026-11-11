import inspect
import math

import streamlit as st

# ---------------------------------------------------------------
# ตั้งชื่อหน้าให้ตรงกับ router ของแอปคุณ (แก้ 3 ค่านี้ค่าเดียวจบ)
# ---------------------------------------------------------------
PAGE_HOME = "dashboard"           # หน้าแรก
PAGE_EQUIPMENT = "equipment_calc" # หน้าหม้อแปลงและอุปกรณ์เสริม
PAGE_CURRENT = "current_calc"     # หน้านี้
PAGE_TRANSFORMER_CALC = "transformer_calc"
PAGE_TRANSFORMER_INFO = "transformer_info"
PAGE_TRANSFORMER_3D = "transformer_3d"

STANDARD_TRANSFORMER_SIZES_KVA = (
    10, 15, 20, 25, 30, 40, 50, 63, 75, 100, 125, 160, 200, 250,
    315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500,
)

BUTTON_WIDTH = (
    {"width": "stretch"}
    if "width" in inspect.signature(st.button).parameters
    else {"use_container_width": True}
)

CSS = """
<style>
.app-header {
    display: flex; align-items: center; gap: 14px;
    padding-bottom: 12px; border-bottom: 1px solid #B9D3F2;
}
.app-logo {
    width: 60px; height: 60px; border-radius: 14px;
    background: #0B3A75; color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.7rem; font-weight: 800;
}
.app-title { margin: 0; color: #0B3A75; font-size: 2rem; font-weight: 800; line-height: 1.1; }
.app-sub { margin: 0; color: #3F5B7D; font-size: .8rem; font-weight: 700; letter-spacing: .12em; }

.page-title { color: #0B3A75; font-size: 2rem; font-weight: 800; margin: 18px 0 6px; }

.info-box {
    background: #E3EFFF; border-left: 5px solid #1E6FD9;
    border-radius: 10px; padding: 14px 18px;
    color: #0B3A75; font-weight: 700; font-size: 1.05rem;
}
.info-note { color: #3F5B7D; margin-top: 12px; font-size: 1rem; }

.result-box {
    background: #FFFFFF; border: 2px solid #1E6FD9; border-radius: 16px;
    padding: 20px; text-align: center;
    box-shadow: 0 8px 22px rgba(11, 58, 117, .12);
}
.result-label { color: #3F5B7D; font-size: 1.05rem; font-weight: 700; }
.result-value { color: #0B3A75; font-size: 2.6rem; font-weight: 800; line-height: 1.2; }
.result-detail { color: #3F5B7D; font-size: .95rem; margin-top: 6px; }

.current-hero {
    background: linear-gradient(120deg, #0B3A75, #1E6FD9);
    border-radius: 20px; padding: 26px 30px; margin: 20px 0;
    color: #FFFFFF;
}
.current-hero h1 { margin: 0 0 6px; color: #FFFFFF; font-size: 2rem; }
.current-hero p { margin: 0; color: #E3EFFF; font-size: 1rem; }
.current-section-title { color: #0B3A75; font-size: 1.15rem; font-weight: 800; }
.current-result {
    background: linear-gradient(145deg, #F2F7FF, #FFFFFF);
    border: 1px solid #B9D3F2; border-radius: 18px;
    padding: 24px; text-align: center; margin: 8px 0 16px;
}
.current-result-label { color: #3F5B7D; font-size: 1rem; font-weight: 700; }
.current-result-value { color: #0B3A75; font-size: 3rem; font-weight: 800; line-height: 1.2; }
.current-result-detail { color: #3F5B7D; font-size: .95rem; margin-top: 8px; }
.current-formula {
    background: #F5F8FC; border-radius: 12px; padding: 12px 16px;
    color: #3F5B7D; text-align: center; font-weight: 700;
}
.current-disclaimer {
    color: #64748B; font-size: .9rem; line-height: 1.5; margin-top: 14px;
}

/* ปุ่มใหญ่ อ่านและกดง่าย สำหรับผู้สูงอายุ */
.st-key-btn_calc button, .st-key-btn_next_equipment button,
.st-key-nav_home button, .st-key-nav_equipment button {
    border-radius: 14px !important;
    transition: transform .18s ease, box-shadow .18s ease;
}
.st-key-btn_calc button, .st-key-btn_next_equipment button { min-height: 72px; }
.st-key-btn_calc button p, .st-key-btn_next_equipment button p {
    font-size: 1.5rem !important; font-weight: 800 !important;
}
.st-key-btn_calc button {
    background: #1E6FD9 !important; border: 0 !important;
    box-shadow: 0 6px 14px rgba(30, 111, 217, .35);
}
.st-key-btn_calc button p { color: #FFFFFF !important; }
.st-key-btn_next_equipment button {
    background: #FFFFFF !important; border: 2px solid #1E6FD9 !important;
}
.st-key-btn_next_equipment button p { color: #0B3A75 !important; }
.st-key-nav_home button, .st-key-nav_equipment button {
    background: #FFFFFF !important; border: 1px solid #B9D3F2 !important; min-height: 48px;
}
.st-key-nav_home button p, .st-key-nav_equipment button p {
    color: #0B3A75 !important; font-weight: 800 !important; font-size: 1.05rem !important;
}
.st-key-btn_calc button:hover, .st-key-btn_next_equipment button:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 22px rgba(11, 58, 117, .25) !important;
}
.st-key-btn_calc button:focus-visible, .st-key-btn_next_equipment button:focus-visible {
    outline: 3px solid #D99A00 !important; outline-offset: 3px;
}
@media (max-width: 640px) {
    .app-title { font-size: 1.5rem; }
    .page-title { font-size: 1.6rem; }
    .result-value { font-size: 2.1rem; }
    .current-hero { padding: 22px; }
    .current-hero h1 { font-size: 1.6rem; }
    .current-result-value { font-size: 2.4rem; }
}
</style>
"""


def calculate_current(
    power_w: float,
    voltage: float,
    pf: float,
    three_phase: bool,
) -> float:
    """คำนวณกระแสจากกำลังไฟฟ้าจริง โดย power_w ต้องมีหน่วยเป็นวัตต์"""
    if not all(math.isfinite(value) for value in (power_w, voltage, pf)):
        raise ValueError("กำลังไฟฟ้า แรงดัน และ Power factor ต้องเป็นค่าจำกัด")
    if power_w < 0:
        raise ValueError("กำลังไฟฟ้าต้องไม่ติดลบ")
    if voltage <= 0:
        raise ValueError("แรงดันไฟฟ้าต้องมากกว่า 0")
    if not 0 < pf <= 1:
        raise ValueError("Power factor ต้องมากกว่า 0 และไม่เกิน 1")
    if not isinstance(three_phase, bool):
        raise TypeError("three_phase ต้องเป็นค่า True หรือ False")

    k = math.sqrt(3) if three_phase else 1
    return power_w / (k * voltage * pf)


def _set_pf_from_preset():
    preset = st.session_state["cc_pf_preset"]
    if preset != "กำหนดเอง":
        st.session_state["cc_pf"] = preset


def _sync_pf_preset():
    pf = st.session_state["cc_pf"]
    presets = (0.8, 0.85, 0.9, 0.95, 1.0)
    st.session_state["cc_pf_preset"] = next(
        (value for value in presets if math.isclose(value, pf)),
        "กำหนดเอง",
    )


def _sync_power_unit():
    previous_unit = st.session_state["cc_power_unit"]
    selected_unit = st.session_state["cc_unit"]
    if previous_unit != selected_unit:
        power_value = st.session_state.get("cc_power", 0.0)
        st.session_state["cc_power"] = (
            power_value / 1000 if selected_unit == "kW" else power_value * 1000
        )
        st.session_state["cc_power_unit"] = selected_unit


def _current_page_css():
    return f"""
    <style>
    :root {{
        --ec-bg:#F2F7FF; --ec-panel:#FFFFFF; --ec-ink:#0C2A5B;
        --ec-muted:#51648A; --ec-line:#CFE0FB; --ec-accent:#1D6FDC;
        --ec-soft:#E6F0FF; --ec-glow:29,111,220;
        --ec-gradient:linear-gradient(120deg,#0C2A5B,#1D6FDC,#4AA3FF);
        color-scheme:light;
    }}
    [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(ellipse 75% 35% at 50% 100%,rgba(var(--ec-glow),.08),transparent 72%),
            var(--ec-bg);
        color:var(--ec-ink);
    }}
    [data-testid="stHeader"] {{background:transparent}}
    [data-testid="stMainBlockContainer"] {{
        width:100%; max-width:1180px; margin:0 auto;
        padding:1.2rem 1rem 2rem;
    }}
    .stApp, .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"] {{
        color:var(--ec-ink);
    }}
    .stApp [data-testid="stVerticalBlockBorderWrapper"] {{
        background:var(--ec-panel); border:1px solid var(--ec-line);
        border-radius:18px; box-shadow:0 8px 24px rgba(12,42,91,.08);
    }}
    .stApp hr, .stApp [data-testid="stDivider"] {{border-color:var(--ec-line)}}
    .stApp [data-testid="stWidgetLabel"] p {{color:var(--ec-muted);font-weight:650}}
    .stApp input, .stApp [data-baseweb="input"] input {{
        color:var(--ec-ink) !important;
    }}
    .stApp [data-baseweb="input"] > div, .stApp [data-baseweb="select"] > div {{
        background:var(--ec-soft); border-color:var(--ec-line);
    }}
    .stApp [data-testid="stSlider"] [role="slider"] {{
        background:var(--ec-accent); border-color:var(--ec-accent);
    }}
    .stApp [data-testid="stSlider"] [data-testid="stTickBar"] {{background:var(--ec-line)}}
    .stApp [data-testid="stRadio"] [role="radiogroup"] {{
        gap:.4rem;
    }}
    .stApp [data-testid="stRadio"] [role="radiogroup"] label {{
        background:#FFFFFF; border:1px solid var(--ec-line);
        border-radius:10px; padding:.35rem .75rem;
    }}
    .stApp [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {{
        border-color:var(--ec-accent); box-shadow:0 0 0 1px var(--ec-accent);
    }}
    .stApp button {{
        color:var(--ec-ink); border-color:var(--ec-line); border-radius:10px;
        transition:transform .16s ease, box-shadow .16s ease;
    }}
    .stApp button:hover {{
        border-color:var(--ec-accent); box-shadow:0 0 18px rgba(var(--ec-glow),.12);
        transform:translateY(-1px);
    }}
    .st-key-btn_next_equipment button {{
        width:100%; min-height:50px; background:#FFFFFF;
        border:1px solid var(--ec-accent);
    }}
    .ec-hero {{
        display:flex; align-items:center; justify-content:space-between; gap:20px;
        padding:24px 28px; margin:4px 0 20px; border:1px solid var(--ec-line);
        border-radius:20px; background:
            radial-gradient(ellipse at 92% 10%,rgba(var(--ec-glow),.12),transparent 45%),
            linear-gradient(120deg,#FFFFFF,#F2F7FF); box-shadow:0 8px 24px rgba(12,42,91,.08);
    }}
    .ec-kicker {{color:var(--ec-accent);font-size:.75rem;font-weight:800;letter-spacing:.16em}}
    .ec-title {{
        margin:4px 0 0; font-size:clamp(1.7rem,4vw,2.4rem); font-weight:850;
        background:var(--ec-gradient); background-size:200% 100%;
        -webkit-background-clip:text; background-clip:text; color:transparent !important;
        -webkit-text-fill-color:transparent; animation:ec-flow 7s linear infinite;
    }}
    .ec-subtitle {{margin:5px 0 0;color:var(--ec-muted) !important}}
    .ec-live {{
        white-space:nowrap; border:1px solid var(--ec-line); border-radius:99px;
        padding:8px 12px; color:var(--ec-accent); background:var(--ec-soft);
        font-size:.8rem; font-weight:800;
    }}
    .ec-section {{font-size:1.08rem;font-weight:800;margin:0 0 8px}}
    .ec-hint {{color:var(--ec-muted) !important;font-size:.85rem}}
    .ec-result-label {{color:var(--ec-muted);font-weight:700}}
    .ec-result {{
        padding:20px 12px; margin:8px 0 16px; border:1px solid var(--ec-line);
        border-radius:16px; background:
            radial-gradient(ellipse at 50% 0,rgba(var(--ec-glow),.08),transparent 68%),
            #F7FAFF;
    }}
    .ec-amp {{
        margin:4px 0; font-size:clamp(3rem,8vw,4.7rem); font-weight:850;
        line-height:1.08; color:var(--ec-accent);
        text-shadow:0 2px 12px rgba(var(--ec-glow),.16);
    }}
    .ec-amp small {{font-size:.4em}}
    .ec-summary {{color:var(--ec-muted);font-size:.88rem}}
    .ec-row {{
        display:flex;justify-content:space-between;gap:12px;padding:10px 0;
        border-bottom:1px solid var(--ec-line);
    }}
    .ec-row span {{color:var(--ec-muted)}}
    .ec-row b {{text-align:right}}
    .ec-formula {{
        margin-top:16px;padding:12px;border-radius:12px;text-align:center;
        background:#F2F7FF;color:var(--ec-accent);font-weight:750;
    }}
    .ec-formula small {{display:block;margin-top:5px;color:var(--ec-muted);font-weight:500}}
    .ec-disclaimer {{font-size:.78rem;color:var(--ec-muted) !important;line-height:1.55}}
    @keyframes ec-flow {{to {{background-position:200% 0}}}}
    @media (prefers-reduced-motion:reduce) {{.ec-title {{animation:none}}}}
    @media (max-width:760px) {{
        [data-testid="stMainBlockContainer"] {{padding:1rem .75rem}}
        .ec-hero {{padding:20px;align-items:flex-start}}
        .ec-live {{font-size:.7rem}}
    }}
    </style>
    """


def calculate_transformer_kva(load_kw, power_factor, reserve_percent):
    """คำนวณกำลังหม้อแปลงเบื้องต้นจาก kVA = kW / PF พร้อมสำรองโหลด"""
    if load_kw <= 0:
        raise ValueError("กำลังไฟฟ้าต้องมากกว่า 0 kW")
    if not 0 < power_factor <= 1:
        raise ValueError("Power factor ต้องมากกว่า 0 และไม่เกิน 1")
    if reserve_percent < 0:
        raise ValueError("เปอร์เซ็นต์สำรองโหลดต้องไม่ติดลบ")
    return load_kw / power_factor * (1 + reserve_percent / 100)


_TC_SCOPE = '[data-testid="stAppViewContainer"]:has(.transformer-calc-theme)'

_TRANSFORMER_FONTS_CSS = (
    "<style>@import url('https://fonts.googleapis.com/css2?"
    "family=Orbitron:wght@500;700;900&family=Kanit:wght@400;500;600;700"
    "&family=JetBrains+Mono:wght@400;600&display=swap');</style>"
)

_TRANSFORMER_CSS_TEMPLATE = """
<style>
@property --tc-num { syntax: "<integer>"; initial-value: 0; inherits: false; }

@S,
[data-testid="stMain"]:has(.transformer-calc-theme) {
    color: #fff1e8 !important;
    background:
        radial-gradient(ellipse at 6% 6%, rgba(255, 90, 24, .22), transparent 34%),
        radial-gradient(ellipse at 96% 92%, rgba(34, 229, 255, .08), transparent 38%),
        linear-gradient(rgba(255, 122, 26, .04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 122, 26, .04) 1px, transparent 1px),
        linear-gradient(135deg, #0b0710, #1a0b10 55%, #0a0608) !important;
    background-size: auto, auto, 38px 38px, 38px 38px, auto !important;
    background-attachment: fixed !important;
}
@S [data-testid="stMain"],
@S [data-testid="stMainBlockContainer"] { background: transparent !important; }

/* scanline + moving scan bar */
@S::before {
    content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background: repeating-linear-gradient(0deg, rgba(255,255,255,.022) 0 1px, transparent 1px 3px);
}
@S::after {
    content: ""; position: fixed; left: 0; right: 0; top: 0; height: 140px;
    z-index: 0; pointer-events: none;
    background: linear-gradient(180deg, transparent, rgba(255,122,26,.07), transparent);
    animation: tc-scan 9s linear infinite;
}
@keyframes tc-scan { from { transform: translateY(-160px); } to { transform: translateY(100vh); } }

@S h1, @S h2, @S h3, @S p, @S label,
@S [data-testid="stCaptionContainer"] { color: #fff1e8 !important; }
@S [data-testid="stWidgetLabel"] p {
    color: #ffc9a3 !important; font-family: "Kanit", sans-serif; font-weight: 500;
    letter-spacing: .02em;
}

/* hero */
@S .tc-hero {
    display: flex; align-items: flex-start; justify-content: space-between; gap: 18px;
    padding: 6px 2px 18px; margin-bottom: 18px;
    border-bottom: 1px solid rgba(255, 142, 79, .28);
}
@S .tc-kicker {
    font-family: "Orbitron", "Kanit", sans-serif; font-size: .72rem; font-weight: 700;
    letter-spacing: .28em; color: #22e5ff; text-shadow: 0 0 10px rgba(34,229,255,.55);
}
@S .tc-title {
    margin: 6px 0 4px; font-family: "Kanit", sans-serif; font-weight: 700;
    font-size: clamp(1.8rem, 4.5vw, 2.7rem); line-height: 1.15; color: #fff1e8;
    text-shadow: 0 0 22px rgba(255, 122, 26, .5);
    animation: tc-glitch .8s steps(1) 1;
}
@S .tc-subtitle { color: #d9a98a; font-size: .98rem; line-height: 1.5; max-width: 760px; }
@keyframes tc-glitch {
    0%   { transform: translate(0); text-shadow: 0 0 22px rgba(255,122,26,.5); }
    15%  { transform: translate(-3px, 1px); text-shadow: 3px 0 #22e5ff, -3px 0 #ff2b4a; }
    30%  { transform: translate(3px, -1px); text-shadow: -3px 0 #22e5ff, 3px 0 #ff2b4a; }
    45%  { transform: translate(-1px, 0); text-shadow: 2px 0 #22e5ff, -2px 0 #ff2b4a; }
    60%  { transform: translate(0); text-shadow: 0 0 22px rgba(255,122,26,.5); }
    100% { transform: translate(0); text-shadow: 0 0 22px rgba(255,122,26,.5); }
}
@S .tc-status {
    display: inline-flex; align-items: center; gap: 8px; white-space: nowrap;
    font-family: "Orbitron", sans-serif; font-size: .7rem; font-weight: 700; letter-spacing: .14em;
    padding: 8px 14px; border-radius: 999px;
    border: 1px solid rgba(34,229,255,.5); color: #22e5ff; background: rgba(34,229,255,.07);
    box-shadow: 0 0 16px rgba(34,229,255,.18);
}
@S .tc-status i {
    width: 8px; height: 8px; border-radius: 50%; background: currentColor;
    box-shadow: 0 0 10px currentColor; animation: tc-blink 1.4s ease-in-out infinite;
}
@S .tc-status.is-done  { color: #ffa24a; border-color: rgba(255,162,74,.6); background: rgba(255,122,26,.09); box-shadow: 0 0 16px rgba(255,122,26,.25); }
@S .tc-status.is-error { color: #ff4d6d; border-color: rgba(255,77,109,.6); background: rgba(255,77,109,.09); box-shadow: 0 0 16px rgba(255,77,109,.25); }
@keyframes tc-blink { 0%,100% { opacity: 1; } 50% { opacity: .25; } }

/* form card with corner brackets */
@S [data-testid="stForm"] {
    position: relative; padding: 24px; border-radius: 18px;
    border: 1px solid rgba(255, 126, 67, .35);
    background: linear-gradient(145deg, rgba(36, 18, 20, .82), rgba(14, 9, 14, .9)) !important;
    backdrop-filter: blur(8px);
    box-shadow: 0 16px 40px rgba(0,0,0,.35), 0 0 28px rgba(255, 77, 29, .1), inset 0 0 30px rgba(255,122,26,.04);
}
@S [data-testid="stForm"]::before,
@S [data-testid="stForm"]::after {
    content: ""; position: absolute; width: 26px; height: 26px; pointer-events: none;
}
@S [data-testid="stForm"]::before {
    top: -1px; left: -1px; border-top: 2px solid #ff7a1a; border-left: 2px solid #ff7a1a;
    border-top-left-radius: 18px; filter: drop-shadow(0 0 6px #ff7a1a);
}
@S [data-testid="stForm"]::after {
    bottom: -1px; right: -1px; border-bottom: 2px solid #22e5ff; border-right: 2px solid #22e5ff;
    border-bottom-right-radius: 18px; filter: drop-shadow(0 0 6px #22e5ff);
}

/* inputs */
@S input {
    color: #fff1e8 !important; background: transparent !important;
    font-family: "JetBrains Mono", ui-monospace, Consolas, monospace !important;
    font-size: 1.15rem !important; font-weight: 600;
}
@S [data-baseweb="input"],
@S [data-baseweb="input"] > div,
@S [data-testid="stNumberInputContainer"] {
    background: #1b0f12 !important; border-color: rgba(255, 142, 79, .4) !important;
    border-radius: 10px !important;
}
@S [data-baseweb="input"]:focus-within,
@S [data-testid="stNumberInputContainer"]:focus-within {
    border-color: #ff7a1a !important;
    box-shadow: 0 0 0 1px #ff7a1a, 0 0 20px rgba(255, 122, 26, .4) !important;
}
@S [data-testid="stNumberInput"] button,
@S [data-testid="stNumberInputStepUp"],
@S [data-testid="stNumberInputStepDown"] {
    background: #2a1710 !important; color: #ff9a54 !important;
    border-color: rgba(255,142,79,.35) !important;
}
@S [data-testid="stNumberInput"] button:hover {
    background: #4a2314 !important; color: #ffd0a8 !important;
    box-shadow: 0 0 14px rgba(255,122,26,.4);
}
@S [data-testid="stNumberInput"] button svg { fill: currentColor !important; color: currentColor !important; }

/* buttons */
@S div.stButton > button,
@S [data-testid="stFormSubmitButton"] > button {
    color: #fff4ed !important; border-radius: 12px !important;
    border: 1px solid rgba(255, 151, 84, .6) !important;
    background: linear-gradient(120deg, #a92c1b, #f05220 58%, #ff9b45) !important;
    transition: transform .18s ease, box-shadow .18s ease;
}
@S div.stButton > button p,
@S [data-testid="stFormSubmitButton"] > button p {
    color: #fff4ed !important; font-family: "Kanit", sans-serif; font-weight: 600;
}
@S [data-testid="stFormSubmitButton"] > button {
    min-height: 62px; box-shadow: 0 0 22px rgba(255,92,26,.4);
    animation: tc-pulse 2.6s ease-in-out infinite;
}
@S [data-testid="stFormSubmitButton"] > button p { font-size: 1.3rem !important; letter-spacing: .04em; }
@S div.stButton > button:hover,
@S [data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-3px); box-shadow: 0 12px 30px rgba(255,92,26,.55), 0 0 26px rgba(255,154,84,.5) !important;
}
@S div.stButton > button:focus-visible,
@S [data-testid="stFormSubmitButton"] > button:focus-visible { outline: 3px solid #22e5ff !important; outline-offset: 3px; }
@keyframes tc-pulse {
    0%,100% { box-shadow: 0 0 18px rgba(255,92,26,.35); }
    50%     { box-shadow: 0 0 34px rgba(255,92,26,.65); }
}
@S .st-key-transformer_back_current div.stButton > button {
    min-height: 44px; background: rgba(255,122,26,.08) !important;
    border: 1px solid rgba(255,142,79,.6) !important; border-radius: 10px !important;
    box-shadow: 0 0 14px rgba(255,92,26,.18);
}
@S .st-key-transformer_back_current div.stButton > button p { color: #ffb27a !important; font-weight: 700; }
@S .st-key-transformer_back_current div.stButton > button:hover {
    background: rgba(255,122,26,.2) !important; transform: translateX(-3px);
    box-shadow: 0 0 22px rgba(255,122,26,.45) !important;
}

/* alerts */
@S [data-testid="stAlert"] {
    border: 1px solid rgba(255,148,77,.48) !important; border-radius: 12px !important;
    background: rgba(55, 30, 22, .88) !important; box-shadow: 0 8px 24px rgba(0,0,0,.25) !important;
}
@S [data-testid="stAlert"] p { color: #ffe8d9 !important; }

/* cards */
@S .tc-card {
    position: relative; margin: 14px 0; padding: 20px 22px; border-radius: 16px;
    border: 1px solid rgba(255,126,67,.32);
    background: linear-gradient(145deg, rgba(40,20,20,.88), rgba(14,9,14,.92));
    box-shadow: 0 12px 32px rgba(0,0,0,.3), inset 0 0 26px rgba(255,122,26,.04);
    animation: tc-rise .5s ease-out both;
}
@keyframes tc-rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@S .tc-label {
    font-family: "Orbitron", "Kanit", sans-serif; font-size: .68rem; font-weight: 700;
    letter-spacing: .2em; color: #22e5ff; opacity: .9;
}
@S .tc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
@S .tc-cell { text-align: center; padding: 10px 6px; }
@S .tc-big {
    margin: 10px 0 4px; font-family: "Orbitron", sans-serif; font-weight: 900;
    font-size: clamp(2rem, 5vw, 3.2rem); line-height: 1.1;
}
@S .tc-big small { font-size: .38em; font-weight: 700; letter-spacing: .1em; margin-left: 6px; }
@S .tc-cyan  { color: #22e5ff; text-shadow: 0 0 22px rgba(34,229,255,.55); }
@S .tc-amber { color: #ff9a54; text-shadow: 0 0 22px rgba(255,122,26,.6); animation: tc-pop .6s ease-out both; }
@keyframes tc-pop { from { opacity: 0; transform: scale(.88); filter: blur(4px); } to { opacity: 1; transform: none; filter: none; } }
@S .tc-sub { color: #d9a98a; font-size: .92rem; }
@S .tc-count { --tc-num: 0; animation: tc-count 1.1s ease-out 1 both; counter-reset: tcn var(--tc-num); }
@S .tc-count::before { content: counter(tcn); }
@keyframes tc-count { from { --tc-num: 0; } }

/* size map */
@S .tc-chips { display: grid; grid-template-columns: repeat(auto-fill, minmax(62px, 1fr)); gap: 7px; margin-top: 12px; }
@S .tc-chip {
    text-align: center; padding: 8px 0; border-radius: 8px;
    font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: .85rem; font-weight: 600;
    border: 1px solid rgba(255,142,79,.3); color: #e8b797; background: rgba(255,122,26,.05);
}
@S .tc-chip.is-low  { opacity: .35; text-decoration: line-through; }
@S .tc-chip.is-pick {
    color: #1a0b06; background: linear-gradient(120deg, #ff7a1a, #ffb27a); border-color: #ffd0a8;
    box-shadow: 0 0 20px rgba(255,122,26,.75); transform: scale(1.08); animation: tc-pop .6s ease-out both;
}
@S .tc-legend { margin-top: 12px; color: #b98a6e; font-size: .82rem; }

/* terminal */
@S .tc-term-bar {
    display: flex; align-items: center; gap: 6px; margin: -6px 0 12px;
    font-family: "Orbitron", sans-serif; font-size: .66rem; letter-spacing: .16em; color: #b98a6e;
}
@S .tc-term-bar b { width: 9px; height: 9px; border-radius: 50%; background: #ff4d6d; display: inline-block; }
@S .tc-term-bar b:nth-child(2) { background: #ffb02e; }
@S .tc-term-bar b:nth-child(3) { background: #22e5ff; margin-right: 8px; }
@S .tc-term-body { font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: .92rem; line-height: 1.85; color: #ffd9bf; }
@S .tc-term-body .p { color: #ff7a1a; margin-right: 8px; }
@S .tc-term-body .k { display: inline-block; min-width: 170px; color: #b98a6e; }
@S .tc-term-body .v { color: #22e5ff; font-weight: 600; }
@S .tc-term-msg { margin-top: 8px; padding-top: 10px; border-top: 1px dashed rgba(255,142,79,.3); font-family: "Kanit", sans-serif; color: #fff1e8; }
@S .tc-cursor {
    display: inline-block; width: 9px; height: 1.05em; margin-left: 4px; vertical-align: -2px;
    background: #ff7a1a; animation: tc-blink 1s steps(1) infinite;
}

/* ---- background FX layers ---- */
@S [data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }
@S .tc-fx { position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; }
@S .tc-orb { position: absolute; border-radius: 50%; will-change: transform; }
@S .tc-orb.o1 { width: 52vmax; height: 52vmax; left: -14vmax; top: -16vmax; background: radial-gradient(circle, rgba(255,90,24,.22), transparent 66%); animation: tc-drift-a 22s ease-in-out infinite alternate; }
@S .tc-orb.o2 { width: 46vmax; height: 46vmax; right: -16vmax; bottom: -12vmax; background: radial-gradient(circle, rgba(34,229,255,.14), transparent 66%); animation: tc-drift-b 26s ease-in-out infinite alternate; }
@S .tc-orb.o3 { width: 34vmax; height: 34vmax; right: 8vw; top: -10vmax; background: radial-gradient(circle, rgba(255,43,74,.12), transparent 66%); animation: tc-drift-a 30s ease-in-out infinite alternate-reverse; }
@keyframes tc-drift-a { to { transform: translate(9vmax, 7vmax) scale(1.12); } }
@keyframes tc-drift-b { to { transform: translate(-8vmax, -6vmax) scale(1.1); } }
@S .tc-floor {
    position: absolute; left: -60%; right: -60%; bottom: -2vh; height: 52vh; opacity: .5;
    background:
        linear-gradient(rgba(255,122,26,.42) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,122,26,.42) 1px, transparent 1px);
    background-size: 64px 64px;
    transform-origin: 50% 100%; transform: perspective(380px) rotateX(64deg);
    -webkit-mask-image: linear-gradient(to top, #000 8%, transparent 88%);
            mask-image: linear-gradient(to top, #000 8%, transparent 88%);
    animation: tc-floor 3.2s linear infinite;
}
@keyframes tc-floor { to { background-position: 0 64px, 0 0; } }
@S .tc-ring {
    position: absolute; right: -150px; top: 16vh; width: 440px; height: 440px; border-radius: 50%;
    border: 1px dashed rgba(34,229,255,.3); animation: tc-spin 48s linear infinite;
}
@S .tc-ring::before {
    content: ""; position: absolute; inset: 38px; border-radius: 50%;
    border: 2px dotted rgba(255,122,26,.32); animation: tc-spin 30s linear infinite reverse;
}
@S .tc-ring::after {
    content: ""; position: absolute; inset: 92px; border-radius: 50%;
    border: 1px solid rgba(34,229,255,.22); box-shadow: inset 0 0 40px rgba(34,229,255,.1);
}
@S .tc-ring.r2 {
    right: auto; left: -110px; top: auto; bottom: 14vh; width: 300px; height: 300px;
    border-color: rgba(255,122,26,.3); animation-duration: 60s; animation-direction: reverse;
}
@keyframes tc-spin { to { transform: rotate(360deg); } }
@S .tc-stream {
    position: absolute; top: -160px; left: var(--x); width: 1px; height: 140px;
    background: linear-gradient(180deg, transparent, rgba(34,229,255,.75));
    animation: tc-fall var(--t) linear var(--d) infinite;
}
@S .tc-stream:nth-child(even) { background: linear-gradient(180deg, transparent, rgba(255,154,84,.75)); }
@keyframes tc-fall { to { transform: translateY(calc(100vh + 320px)); } }
@S .tc-dots { position: absolute; top: 0; left: 0; width: 2px; height: 2px; border-radius: 50%; }
@S .tc-dots.a { background: #ff9a54; box-shadow: @DOTS_A; animation: tc-dots-up 55s linear infinite; }
@S .tc-dots.b { width: 3px; height: 3px; background: #22e5ff; opacity: .8; box-shadow: @DOTS_B; animation: tc-dots-up 85s linear infinite; }
@keyframes tc-dots-up { to { transform: translateY(-100vh); } }
@S .tc-hud {
    position: absolute; bottom: 14px; font-family: "Orbitron", sans-serif; font-size: .62rem;
    letter-spacing: .2em; color: rgba(255,178,122,.45); white-space: nowrap;
}
@S .tc-hud.l { left: 18px; }
@S .tc-hud.r { right: 18px; }
@S .tc-hud i { display: inline-block; width: 6px; height: 6px; margin-right: 8px; border-radius: 50%; background: #22e5ff; animation: tc-blink 1.4s ease-in-out infinite; }

@media (max-width: 680px) {
    @S .tc-hero { flex-direction: column; }
    @S .tc-ring, @S .tc-hud { display: none; }
    @S .tc-floor { height: 36vh; }
    @S .tc-grid { grid-template-columns: 1fr; }
    @S .tc-term-body .k { min-width: 120px; }
    @S [data-testid="stForm"] { padding: 16px; }
}
@media (prefers-reduced-motion: reduce) {
    @S .tc-floor, @S .tc-orb, @S .tc-ring, @S .tc-ring::before, @S .tc-stream, @S .tc-dots, @S .tc-hud i,
    @S::after, @S .tc-title, @S .tc-card, @S .tc-count, @S .tc-amber, @S .tc-chip.is-pick,
    @S .tc-status i, @S .tc-cursor, @S [data-testid="stFormSubmitButton"] > button { animation: none !important; }
}
.transformer-calc-theme { display: none; }
</style>
"""


def _tc_shadows(count, color, seed):
    """สร้างจุดอนุภาคแบบ box-shadow (ซ้ำที่ +100vh เพื่อให้วนต่อเนื่อง)"""
    import random

    rng = random.Random(seed)
    points = []
    for _ in range(count):
        x, y = rng.randint(1, 99), rng.randint(1, 99)
        points.append(f"{x}vw {y}vh 3px 0 {color}")
        points.append(f"{x}vw {y + 100}vh 3px 0 {color}")
    return ",".join(points)


def _transformer_theme_css():
    css = _TRANSFORMER_CSS_TEMPLATE
    css = css.replace("@DOTS_A", _tc_shadows(38, "#ff9a54", 7))
    css = css.replace("@DOTS_B", _tc_shadows(26, "#22e5ff", 21))
    return css.replace("@S", _TC_SCOPE)


def _tc_fx_html():
    streams = "".join(
        f'<i class="tc-stream" style="--x:{x}%;--t:{t}s;--d:-{d}s"></i>'
        for x, t, d in (
            (6, 7, 2), (17, 11, 6), (29, 9, 1), (41, 13, 8),
            (58, 8, 4), (72, 12, 9), (84, 10, 3), (93, 14, 7),
        )
    )
    return "".join([
        '<div class="tc-fx">',
        '<i class="tc-orb o1"></i><i class="tc-orb o2"></i><i class="tc-orb o3"></i>',
        '<i class="tc-floor"></i>',
        '<i class="tc-ring"></i><i class="tc-ring r2"></i>',
        f'<div class="tc-streams">{streams}</div>',
        '<i class="tc-dots a"></i><i class="tc-dots b"></i>',
        '<div class="tc-hud l"><i></i>PWR.CORE v2.6 · GRID 50Hz</div>',
        '<div class="tc-hud r">380V · 3-PHASE · ONLINE</div>',
        '</div>',
    ])


def _tc_hero_html(status):
    labels = {"ready": "SYSTEM READY", "done": "ANALYSIS COMPLETE", "error": "INPUT ERROR"}
    css_class = {"ready": "", "done": " is-done", "error": " is-error"}[status]
    title = "คำนวณขนาดหม้อแปลง"
    return "".join([
        '<div class="tc-hero"><div>',
        '<div class="tc-kicker">TRANSFORMER SIZING // AI MODULE</div>',
        f'<div class="tc-title">{title}</div>',
        '<div class="tc-subtitle">ใส่กำลังไฟฟ้าจริงรวมของทุกเฟส เพื่อประมาณขนาดจาก '
        'kVA = kW ÷ Power factor และเผื่อกำลังสำรอง</div>',
        '</div>',
        f'<div class="tc-status{css_class}"><i></i>{labels[status]}</div>',
        '</div>',
    ])


def _tc_waiting_html():
    return "".join([
        '<div class="tc-card">',
        '<div class="tc-term-bar"><b></b><b></b><b></b>AI ANALYSIS · transformer.sizing</div>',
        '<div class="tc-term-body">',
        '<div><span class="p">&gt;</span>status <span class="v">awaiting_input</span></div>',
        '<div class="tc-term-msg"><span class="p">&gt;</span>'
        'กรอกข้อมูลด้านบนแล้วกดปุ่มคำนวณ เพื่อเริ่มวิเคราะห์ขนาดหม้อแปลง'
        '<span class="tc-cursor"></span></div>',
        '</div></div>',
    ])


def _tc_result_html(result):
    required = result["required_kva"]
    recommended = result["recommended_kva"]
    load_kw = result["load_kw"]
    pf = result["power_factor"]
    reserve = result["reserve_percent"]

    rounded = round(required, 2)
    int_part = int(rounded)
    if int_part < 1000:
        decimals = f"{rounded:.2f}".split(".")[1]
        required_html = f'<span class="tc-count" style="--tc-num:{int_part}"></span>.{decimals}'
    else:
        required_html = f"{required:,.2f}"

    if recommended is None:
        recommended_html = '<div class="tc-big tc-amber">N/A</div>'
        recommended_sub = "เกินรายการมาตรฐานในระบบ"
        selected_line = "out_of_range"
        message = ("ค่าที่คำนวณได้เกินขนาดมาตรฐานสูงสุดในระบบ "
                   f"({STANDARD_TRANSFORMER_SIZES_KVA[-1]:,} kVA) โปรดให้วิศวกรพิจารณา")
        util_line = "—"
    else:
        recommended_html = f'<div class="tc-big tc-amber">{recommended:,}<small>kVA</small></div>'
        recommended_sub = "ขนาดหม้อแปลงมาตรฐานที่แนะนำ"
        utilization = required / recommended * 100
        selected_line = f"{recommended:,} kVA"
        util_line = f"{utilization:.1f} %"
        message = (f"วิเคราะห์เสร็จสิ้น: โหลด {load_kw:,.2f} kW · PF {pf:.2f} → "
                   f"ควรเลือกหม้อแปลง {recommended:,} kVA (ใช้ประมาณ {utilization:.1f}% ของพิกัด)")

    chips = []
    for size in STANDARD_TRANSFORMER_SIZES_KVA:
        if recommended is not None and size == recommended:
            state = "is-pick"
        elif size < required:
            state = "is-low"
        else:
            state = "is-high"
        chips.append(f'<div class="tc-chip {state}">{size:,}</div>')

    rows = [
        ("load_input", f"{load_kw:,.2f} kW"),
        ("power_factor", f"{pf:.2f}"),
        ("reserve_margin", f"{reserve:.1f} %"),
        ("required_kva", f"{required:,.2f} kVA"),
        ("selected_kva", selected_line),
        ("utilization", util_line),
    ]
    terminal_rows = "".join(
        f'<div><span class="p">&gt;</span><span class="k">{k}</span><span class="v">{v}</span></div>'
        for k, v in rows
    )

    return "".join([
        '<div class="tc-card"><div class="tc-grid">',
        '<div class="tc-cell"><div class="tc-label">// REQUIRED CAPACITY</div>',
        f'<div class="tc-big tc-cyan">{required_html}<small>kVA</small></div>',
        '<div class="tc-sub">ขนาดที่ต้องการโดยประมาณ</div></div>',
        '<div class="tc-cell"><div class="tc-label">// STANDARD SIZE</div>',
        recommended_html,
        f'<div class="tc-sub">{recommended_sub}</div></div>',
        '</div></div>',
        '<div class="tc-card"><div class="tc-label">// STANDARD SIZE MAP (kVA)</div>',
        f'<div class="tc-chips">{"".join(chips)}</div>',
        '<div class="tc-legend">จางขีดฆ่า = เล็กกว่าที่ต้องการ · เรืองแสง = ขนาดที่เลือก · ปกติ = ขนาดที่ใหญ่กว่า</div>',
        '</div>',
        '<div class="tc-card">',
        '<div class="tc-term-bar"><b></b><b></b><b></b>AI ANALYSIS · transformer.sizing</div>',
        f'<div class="tc-term-body">{terminal_rows}',
        f'<div class="tc-term-msg"><span class="p">&gt;</span>{message}<span class="tc-cursor"></span></div>',
        '</div></div>',
    ])


def render_transformer_calc_page(go):
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(_TRANSFORMER_FONTS_CSS, unsafe_allow_html=True)
    st.markdown(
        _transformer_theme_css()
        + '\n<div class="transformer-calc-theme"></div>'
        + _tc_fx_html(),
        unsafe_allow_html=True,
    )

    back_col, _ = st.columns([1, 4])
    with back_col:
        st.button(
            "⬅ ย้อนกลับ",
            on_click=go,
            args=(PAGE_CURRENT,),
            key="transformer_back_current",
            **BUTTON_WIDTH,
        )

    hero_slot = st.empty()

    with st.form("transformer_calculator_form"):
        load_kw = st.number_input(
            "กำลังไฟฟ้ารวมของโหลด (kW)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
            key="transformer_load_kw",
        )
        power_factor = st.number_input(
            "Power factor",
            min_value=0.1,
            max_value=1.0,
            value=0.8,
            step=0.05,
            format="%.2f",
            key="transformer_power_factor",
        )
        reserve_percent = st.number_input(
            "กำลังสำรอง (%)",
            min_value=0.0,
            max_value=100.0,
            value=25.0,
            step=5.0,
            format="%.1f",
            key="transformer_reserve_percent",
        )
        submitted = st.form_submit_button("คำนวณขนาดหม้อแปลง", type="primary")

    if submitted:
        if load_kw <= 0:
            st.session_state["transformer_calc_result"] = {
                "error": "กรุณากรอกกำลังไฟฟ้ารวมมากกว่า 0 kW"
            }
        else:
            required_kva = calculate_transformer_kva(
                load_kw, power_factor, reserve_percent
            )
            recommended_kva = next(
                (
                    size
                    for size in STANDARD_TRANSFORMER_SIZES_KVA
                    if size >= required_kva
                ),
                None,
            )
            st.session_state["transformer_calc_result"] = {
                "required_kva": required_kva,
                "recommended_kva": recommended_kva,
                "load_kw": load_kw,
                "power_factor": power_factor,
                "reserve_percent": reserve_percent,
            }

    result = st.session_state.get("transformer_calc_result")
    if not result:
        status = "ready"
    elif "error" in result:
        status = "error"
    else:
        status = "done"
    hero_slot.markdown(_tc_hero_html(status), unsafe_allow_html=True)

    if not result:
        st.markdown(_tc_waiting_html(), unsafe_allow_html=True)
    elif "error" in result:
        st.warning(result["error"])
    else:
        st.markdown(_tc_result_html(result), unsafe_allow_html=True)
        st.warning("เป็นค่าประมาณเบื้องต้น ต้องให้วิศวกรไฟฟ้าตรวจสอบก่อนใช้งานจริง")
        st.button(
            "ดูรายละเอียดและโมเดล 3D หม้อแปลง",
            on_click=go,
            args=(PAGE_TRANSFORMER_INFO,),
            key="transformer_calc_open_details",
            **BUTTON_WIDTH,
        )

    st.markdown("---")
    st.subheader("ภาพและรายละเอียดอุปกรณ์ไฟฟ้า")
    render_calculator_page(go)


def render_current_calc_page(go):
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(_current_page_css(), unsafe_allow_html=True)

    back_col, _ = st.columns([1, 4])
    with back_col:
        st.button(
            "⬅ กลับหน้าแรก",
            on_click=go,
            args=(PAGE_HOME,),
            key="current_back_home",
            **BUTTON_WIDTH,
        )

    st.markdown(
        """
        <div class="ec-hero">
            <div>
                <div class="ec-kicker">ATTAPORN ENGINEERING &amp; SUPPLY</div>
                <h1 class="ec-title">คำนวณกระแสไฟฟ้า</h1>
                <p class="ec-subtitle">ปรับค่าระบบไฟ แล้วดูผลคำนวณได้ทันที</p>
            </div>
            <div class="ec-live">● LIVE CALCULATION</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    form_col, result_col = st.columns([1.1, 0.9], gap="large")
    with form_col:
        with st.container(border=True):
            st.markdown('<div class="ec-section">ข้อมูลสำหรับคำนวณ</div>', unsafe_allow_html=True)
            unit = st.radio(
                "หน่วยกำลังไฟฟ้า",
                ["W", "kW"],
                format_func=lambda value: "วัตต์ (W)" if value == "W" else "กิโลวัตต์ (kW)",
                horizontal=True,
                key="cc_unit",
                on_change=_sync_power_unit,
            )
            st.session_state.setdefault("cc_power_unit", unit)
            st.session_state.setdefault("cc_power", 100.0)
            power_value = st.number_input(
                f"กำลังไฟฟ้า ({unit})",
                min_value=0.0,
                step=100.0 if unit == "W" else 0.5,
                format="%.2f",
                key="cc_power",
            )
            phase = st.radio(
                "ระบบไฟ",
                ["1 เฟส", "3 เฟส"],
                horizontal=True,
                key="cc_phase",
            )
            three_phase = phase == "3 เฟส"
            voltage_options = (380, 400, 416, "กำหนดเอง") if three_phase else (220, 230, "กำหนดเอง")
            voltage_default = 380 if three_phase else 220
            voltage_mode = st.radio(
                "แรงดันไฟฟ้า",
                voltage_options,
                format_func=lambda value: f"{value} V" if isinstance(value, int) else value,
                horizontal=True,
                key=f"cc_voltage_preset_{phase}",
            )
            if voltage_mode == "กำหนดเอง":
                voltage = st.number_input(
                    "กำหนดแรงดันเอง (V)",
                    min_value=0.0,
                    value=float(voltage_default),
                    step=10.0,
                    format="%.1f",
                    key=f"cc_voltage_custom_{phase}",
                )
            else:
                voltage = float(voltage_mode)

            st.session_state.setdefault("cc_pf", 0.95)
            if st.session_state["cc_pf"] <= 0:
                st.session_state["cc_pf"] = 0.01
            st.slider(
                "ตัวประกอบกำลัง (Power factor)",
                min_value=0.01,
                max_value=1.0,
                step=0.01,
                format="%.2f",
                key="cc_pf",
                on_change=_sync_pf_preset,
                help="โหลดความร้อนมักมี PF ใกล้ 1 ส่วนมอเตอร์ทั่วไปประมาณ 0.8",
            )
            if "cc_pf_preset" not in st.session_state:
                _sync_pf_preset()
            st.radio(
                "ค่าที่ใช้บ่อย",
                (0.8, 0.85, 0.9, 0.95, 1.0, "กำหนดเอง"),
                format_func=lambda value: f"{value:.2f}" if isinstance(value, float) else value,
                horizontal=True,
                key="cc_pf_preset",
                on_change=_set_pf_from_preset,
            )
            st.markdown(
                '<div class="ec-hint">ผลลัพธ์จะอัปเดตทันทีเมื่อเปลี่ยนค่าด้านบน</div>',
                unsafe_allow_html=True,
            )

        st.button(
            "ถัดไป: คำนวณหม้อแปลง ➜",
            on_click=go,
            args=(PAGE_TRANSFORMER_CALC,),
            key="btn_next_equipment",
            **BUTTON_WIDTH,
        )

    power_w = power_value * 1000 if unit == "kW" else power_value
    with result_col:
        with st.container(border=True):
            st.markdown('<div class="ec-section">ผลการคำนวณ</div>', unsafe_allow_html=True)
            pf = st.session_state["cc_pf"]
            if voltage <= 0 or pf <= 0:
                st.warning("แรงดันไฟฟ้าและ Power factor ต้องมากกว่า 0")
            else:
                amps = calculate_current(power_w, voltage, pf, three_phase) if power_w > 0 else 0
                apparent_kva = power_w / (pf * 1000) if power_w > 0 else 0
                breaker_sizes = (6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630)
                recommended_breaker = next(
                    (size for size in breaker_sizes if size >= amps * 1.25),
                    None,
                ) if amps > 0 else None
                breaker_text = (
                    f"{recommended_breaker} A"
                    if recommended_breaker
                    else "เกิน 630 A ให้วิศวกรพิจารณา" if amps > 0 else "—"
                )
                formula = "I = P / (√3 × V × PF)" if three_phase else "I = P / (V × PF)"
                denominator = f"{'1.732 × ' if three_phase else ''}{voltage:g} × {pf:.2f}"
                st.markdown(
                    f"""
                    <div class="ec-result">
                        <div class="ec-result-label">กระแสไฟฟ้าโดยประมาณ</div>
                        <div class="ec-amp">{amps:,.2f} <small>A</small></div>
                        <div class="ec-summary">
                            {power_value:,.2f} {unit} &nbsp;·&nbsp; {voltage:g} V
                            &nbsp;·&nbsp; PF {pf:.2f} &nbsp;·&nbsp; {phase}
                        </div>
                    </div>
                    <div class="ec-row"><span>กำลังจริง</span><b>{power_w / 1000:,.3f} kW</b></div>
                    <div class="ec-row"><span>กำลังปรากฏ</span><b>{apparent_kva:,.3f} kVA</b></div>
                    <div class="ec-row"><span>เบรกเกอร์แนะนำ (เผื่อ 25%)</span><b>{breaker_text}</b></div>
                    <div class="ec-formula">
                        {formula}
                        <small>= {power_w:,.2f} / ({denominator})</small>
                    </div>
                    <div class="ec-disclaimer">
                        ค่าที่ได้เป็นการประมาณเบื้องต้น ควรให้วิศวกรไฟฟ้าตรวจสอบก่อนนำไปใช้งานจริง
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if three_phase and voltage < 300:
                    st.warning("ระบบ 3 เฟสทั่วไปใช้แรงดันประมาณ 380 V โปรดตรวจสอบค่าแรงดัน")
                elif not three_phase and voltage > 260:
                    st.warning("ระบบ 1 เฟสทั่วไปใช้แรงดันประมาณ 220 V โปรดตรวจสอบค่าแรงดัน")


def render_calculator_page(go):
    """Render the equipment overview page while keeping the legacy import path."""
    from equipment_page import render_calculator_page as render_equipment_page

    render_equipment_page(go)