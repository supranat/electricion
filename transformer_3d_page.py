from pathlib import Path
import inspect

import streamlit as st

import calculator_page


BUTTON_WIDTH = (
    {"width": "stretch"}
    if "width" in inspect.signature(st.button).parameters
    else {"use_container_width": True}
)


def _find_project():
    root = Path(__file__).parent
    for p in root.rglob("index.html"):
        if p.parent.name == "transformer-project":
            return p.parent
    return None


def _build_transformer_html():
    base = _find_project()
    if base is None:
        raise FileNotFoundError(
            "หาโฟลเดอร์ transformer-project ไม่เจอ ตรวจชื่อโฟลเดอร์และว่ามี index.html ข้างใน"
        )

    def read(path):
        return (base / path).read_text(encoding="utf-8")

    page_html = read("index.html")
    page_html = page_html.replace(
        '<link rel="stylesheet" href="css/style.css">',
        "<style>" + read("css/style.css") + "</style>",
    )
    for name in ["data", "scene", "main"]:
        page_html = page_html.replace(
            '<script src="js/%s.js"></script>' % name,
            "<script>" + read("js/%s.js" % name) + "</script>",
        )
    return page_html


def show_transformer_3d():
    try:
        page_html = _build_transformer_html()
    except OSError as exc:
        st.error(f"เปิดหน้าโมเดลหม้อแปลง 3D ไม่ได้: {exc}")
        return

    st.iframe(
        page_html,
        width="stretch",
        height=760,
        alt="โมเดลหม้อแปลงไฟฟ้า 3D",
    )


def show_transformer_3d_fullscreen(go):
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
            background: #10090c !important;
        }
        iframe[title="โมเดลหม้อแปลงไฟฟ้า 3D เต็มหน้าจอ"] {
            display: block;
            width: 100% !important;
            height: calc(100vh - 68px) !important;
            min-height: 620px;
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
        key="transformer_3d_back",
        **BUTTON_WIDTH,
    )

    try:
        page_html = _build_transformer_html()
    except OSError as exc:
        st.error(f"เปิดหน้าโมเดลหม้อแปลง 3D ไม่ได้: {exc}")
        return

    page_html = page_html.replace(
        "</style>",
        """
        html, body {
            width: 100%;
            min-height: 100%;
        }
        header, main {
            max-width: none;
        }
        .blueprint-layout {
            grid-template-columns: minmax(0, 1fr);
        }
        #stage {
            width: 100%;
            height: min(56.25vw, 68vh, 760px);
            aspect-ratio: 16 / 9;
        }
        #panel {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
        .drawing-titleblock {
            margin-bottom: 12px;
        }
        @media (max-width: 760px) {
            #stage {
                height: auto;
                aspect-ratio: 16 / 9;
            }
            #panel {
                grid-template-columns: 1fr;
            }
            #panel > section + section {
                border-top: 1px solid var(--line);
                border-left: 0;
            }
        }
        </style>
        """,
        1,
    )
    st.iframe(
        page_html,
        width="stretch",
        height=900,
        alt="โมเดลหม้อแปลงไฟฟ้า 3D เต็มหน้าจอ",
    )