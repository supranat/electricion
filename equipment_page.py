import inspect
import os

import streamlit as st
import calculator_page
from PIL import Image, UnidentifiedImageError


APP_DIR = os.path.dirname(os.path.abspath(__file__))
BUTTON_WIDTH = (
    {"width": "stretch"}
    if "width" in inspect.signature(st.button).parameters
    else {"use_container_width": True}
)
IMAGE_WIDTH = (
    {"width": "stretch"}
    if "width" in inspect.signature(st.image).parameters
    else {"use_container_width": True}
)

CATEGORIES = {
    "transformer": {
        "title": "หม้อแปลง",
        "icon": "🔌",
        "description": "ภาพและข้อมูลหม้อแปลง",
        "image": "images/transformer/front.jpg",
    },
    "poles": {
        "title": "เสาไฟ",
        "icon": "⚡",
        "description": "ตัวอย่างเสาไฟคอนกรีต",
        "image": "poles/overview.jpg",
    },
    "tray": {
        "title": "ราง",
        "icon": "▤",
        "description": "คู่มือรางเดินสายไฟ 5 ชนิด พร้อมตัวช่วยคำนวณขนาด",
        "image": "tray/overview.jpg",
    },
    "breakers": {
        "title": "เบรกเกอร์",
        "icon": "⏚",
        "description": "ภาพและข้อมูลเบรกเกอร์",
        "image": "images/breakers/overview.png",
    },
    "cables": {
        "title": "สายไฟ",
        "icon": "〰️",
        "description": "ภาพและข้อมูลสายไฟ",
        "image": "images/cables/overview.jpg",
    },
}


@st.dialog("รายละเอียดอุปกรณ์")
def _show_category(category):
    item = CATEGORIES[category]
    st.subheader(item["title"])
    st.caption(item["description"])
    image_path = os.path.join(APP_DIR, item["image"])
    if os.path.isfile(image_path):
        try:
            with Image.open(image_path) as image:
                image.verify()
            st.image(image_path, caption=item["description"], **IMAGE_WIDTH)
        except (UnidentifiedImageError, OSError, ValueError):
            st.warning(f"เปิดรูป `{item['image']}` ไม่ได้ กรุณาตรวจสอบไฟล์รูป")
    else:
        st.info(f"เพิ่มรูปภาพได้ที่ `{item['image']}`")
    st.warning("หน้านี้ยังไม่มีสูตรคำนวณ โปรดให้วิศวกรตรวจสอบก่อนใช้งานจริง")


def _render_category_card(column, key, item, go):
    with column:
        st.markdown(
            f'<div class="equipment-card"><div class="icon">{item["icon"]}</div>'
            f'<div class="title">{item["title"]}</div></div>',
            unsafe_allow_html=True,
        )
        button_label = (
            "ดูข้อมูลรางทั้งหมด" if key == "tray"
            else "ดูข้อมูลเสาไฟ" if key == "poles"
            else "เปิดหน้าข้อมูลเบรกเกอร์" if key == "breakers"
            else "เปิดตารางขนาดสายไฟ" if key == "cables"
            else "ดูรายละเอียด"
        )
        if key == "transformer":
            clicked = st.button(
                button_label,
                key=f"equipment_{key}",
                on_click=go,
                args=(calculator_page.PAGE_TRANSFORMER_3D,),
                **BUTTON_WIDTH,
            )
        elif key == "poles":
            clicked = st.button(
                button_label,
                key=f"equipment_{key}",
                on_click=go,
                args=("poles",),
                **BUTTON_WIDTH,
            )
        elif key == "breakers":
            clicked = st.button(
                button_label,
                key=f"equipment_{key}",
                on_click=go,
                args=("breakers",),
                **BUTTON_WIDTH,
            )
        elif key == "cables":
            clicked = st.button(
                button_label,
                key=f"equipment_{key}",
                on_click=go,
                args=("cable_table",),
                **BUTTON_WIDTH,
            )
        elif key == "tray":
            clicked = st.button(
                button_label,
                key=f"equipment_{key}",
                on_click=go,
                args=("tray_guide",),
                **BUTTON_WIDTH,
            )
        else:
            clicked = st.button(button_label, key=f"equipment_{key}", **BUTTON_WIDTH)

    if clicked and key not in ("transformer", "poles", "breakers", "cables", "tray"):
        _show_category(key)


def render_calculator_page(go):
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"]:has(.equipment-theme),
        [data-testid="stMain"]:has(.equipment-theme) {
            color: #fff1e8 !important;
            background:
                radial-gradient(ellipse at 8% 8%, rgba(255, 75, 28, .2), transparent 32%),
                radial-gradient(ellipse at 92% 18%, rgba(255, 153, 55, .13), transparent 34%),
                linear-gradient(rgba(255, 112, 55, .035) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 112, 55, .035) 1px, transparent 1px),
                linear-gradient(135deg, #160b0d, #241014 55%, #120b0d) !important;
            background-size: auto, auto, 38px 38px, 38px 38px, auto !important;
            background-attachment: fixed !important;
        }
        [data-testid="stAppViewContainer"]:has(.equipment-theme) [data-testid="stMain"],
        [data-testid="stAppViewContainer"]:has(.equipment-theme) [data-testid="stMainBlockContainer"] {
            background: transparent !important;
        }
        [data-testid="stAppViewContainer"]:has(.equipment-theme) h1,
        [data-testid="stAppViewContainer"]:has(.equipment-theme) h2,
        [data-testid="stAppViewContainer"]:has(.equipment-theme) h3,
        [data-testid="stAppViewContainer"]:has(.equipment-theme) p,
        [data-testid="stAppViewContainer"]:has(.equipment-theme) label,
        [data-testid="stAppViewContainer"]:has(.equipment-theme) [data-testid="stCaptionContainer"] {
            color: #fff1e8 !important;
        }
        .equipment-theme { display: none; }
        .equipment-card {
            min-height: 120px; margin-bottom: 8px; padding: 18px 10px;
            text-align: center;
            background: radial-gradient(ellipse at 50% 0, rgba(255, 114, 55, .16), transparent 70%),
                linear-gradient(145deg, rgba(43, 21, 22, .96), rgba(24, 15, 17, .96));
            border: 1px solid rgba(255, 126, 67, .42);
            border-radius: 16px;
            box-shadow: 0 10px 28px rgba(0,0,0,.2), 0 0 20px rgba(255,77,29,.08);
            transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
        }
        .equipment-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 166, 100, .75);
            box-shadow: 0 14px 32px rgba(0,0,0,.28), 0 0 24px rgba(255,77,29,.18);
        }
        .equipment-card .icon { font-size: 1.9rem; line-height: 1.2; }
        .equipment-card .title { margin-top: 8px; color: #ffe4d5; font-size: 1.1rem; font-weight: 800; }
        .st-key-equipment_transformer button, .st-key-equipment_poles button,
        .st-key-equipment_tray button, .st-key-equipment_breakers button,
        .st-key-equipment_cables button, .st-key-equipment_back button {
            min-height: 58px; border: 1px solid rgba(255, 151, 84, .55) !important;
            border-radius: 14px !important;
            background: linear-gradient(120deg, #8f251a, #d9411d 58%, #e97c31) !important;
            box-shadow: 0 6px 16px rgba(122, 39, 20, .28);
            transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
        }
        .st-key-equipment_transformer button p, .st-key-equipment_poles button p,
        .st-key-equipment_tray button p, .st-key-equipment_breakers button p,
        .st-key-equipment_cables button p, .st-key-equipment_back button p {
            color: #fff4ed !important; font-size: 1.05rem !important; font-weight: 800 !important;
        }
        .st-key-equipment_transformer button:hover, .st-key-equipment_poles button:hover,
        .st-key-equipment_tray button:hover, .st-key-equipment_breakers button:hover,
        .st-key-equipment_cables button:hover, .st-key-equipment_back button:hover {
            transform: translateY(-3px); box-shadow: 0 12px 24px rgba(255,78,29,.26) !important;
            background: linear-gradient(120deg, #aa2c1b, #f05220 58%, #ff9b45) !important;
        }
        body:has(.equipment-theme) [data-testid="stDialog"],
        body:has(.equipment-theme) [role="dialog"] {
            color: #fff1e8 !important;
            border: 1px solid rgba(255, 126, 67, .48) !important;
            border-radius: 20px !important;
            background: linear-gradient(145deg, #261416, #160e10) !important;
            box-shadow: 0 20px 70px rgba(0,0,0,.55), 0 0 28px rgba(255,77,29,.16) !important;
        }
        body:has(.equipment-theme) [role="dialog"] h1,
        body:has(.equipment-theme) [role="dialog"] h2,
        body:has(.equipment-theme) [role="dialog"] p,
        body:has(.equipment-theme) [role="dialog"] [data-testid="stCaptionContainer"] {
            color: #fff1e8 !important;
        }
        body:has(.equipment-theme) [role="dialog"] [data-testid="stImage"] {
            padding: 10px;
            border: 1px solid rgba(255, 126, 67, .28);
            border-radius: 14px;
            background: #211416 !important;
        }
        body:has(.equipment-theme) [role="dialog"] [data-testid="stAlert"] {
            border-color: rgba(255, 148, 77, .48) !important;
            background: rgba(55, 30, 22, .94) !important;
        }
        @media (prefers-reduced-motion: reduce) {
            .equipment-card, .equipment-card:hover,
            .st-key-equipment_transformer button, .st-key-equipment_poles button,
            .st-key-equipment_tray button, .st-key-equipment_breakers button,
            .st-key-equipment_cables button, .st-key-equipment_back button { transition: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="equipment-theme"></div>', unsafe_allow_html=True)

    categories = list(CATEGORIES.items())
    top_columns = st.columns(3)
    for column, (key, item) in zip(top_columns, categories[:3]):
        _render_category_card(column, key, item, go)

    bottom_columns = st.columns([0.5, 1, 1, 0.5])
    for column, (key, item) in zip(bottom_columns[1:3], categories[3:]):
        _render_category_card(column, key, item, go)

    st.caption("หน้าแสดงข้อมูลอุปกรณ์และรูปประกอบ สูตรคำนวณจะเพิ่มภายหลัง")
    st.button(
        "กลับไปหน้าคำนวณกระแสไฟฟ้า",
        on_click=go,
        args=("current_calc",),
        key="equipment_back",
        **BUTTON_WIDTH,
    )
