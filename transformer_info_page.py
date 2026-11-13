import base64
import io
import inspect
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageOps

import calculator_page
from site_theme import apply_embedded_theme
from hero_background import HERO_BACKGROUND_CSS, HERO_NETWORK_SCRIPT


APP_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = APP_DIR / "templates" / "transformer_info.html"
IMAGE_DIR = APP_DIR / "images"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
PREFERRED_IMAGE_PATH = IMAGE_DIR / "transformer" / "front.jpg"
TRANSPARENT_PIXEL_URI = (
    "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="
)
BUTTON_WIDTH = (
    {"width": "stretch"}
    if "width" in inspect.signature(st.button).parameters
    else {"use_container_width": True}
)


@st.cache_data(show_spinner=False)
def transparent_data_uri(image_bytes: bytes) -> str:
    with Image.open(io.BytesIO(image_bytes)) as source:
        image = ImageOps.exif_transpose(source).convert("RGBA")

    width, height = image.size
    for seed in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)):
        red, green, blue, alpha = image.getpixel(seed)
        if alpha and min(red, green, blue) > 225:
            ImageDraw.floodfill(image, seed, (255, 255, 255, 0), thresh=45)

    alpha = image.getchannel("A")
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    image.putalpha(alpha)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def find_transformer_image() -> Path | None:
    if not IMAGE_DIR.is_dir():
        return None
    if PREFERRED_IMAGE_PATH.is_file():
        return PREFERRED_IMAGE_PATH

    files = sorted(
        path
        for path in IMAGE_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    for path in files:
        if path.stem.lower() == "transformer":
            return path
    for path in files:
        if path.parent.name.lower() == "transformer":
            return path
    for path in files:
        name = path.stem.lower()
        if "transform" in name or "หม้อแปลง" in path.stem:
            return path
    return None


def _read_template() -> str | None:
    try:
        page_html = TEMPLATE_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        st.error(f"อ่านเทมเพลตหน้าแสดงข้อมูลหม้อแปลงไม่ได้: {exc}")
        return None

    required_markers = (
        'src="__TRANSFORMER_IMG__"',
        "__HERO_BACKGROUND_CSS__",
        "__HERO_NETWORK_SCRIPT__",
    )
    missing_markers = [marker for marker in required_markers if marker not in page_html]
    if missing_markers:
        st.error(
            f"ไม่พบตำแหน่งข้อมูล {', '.join(missing_markers)} "
            f"ในเทมเพลต {TEMPLATE_PATH}"
        )
        return None
    return page_html


def _load_image_uri() -> str:
    image_path = find_transformer_image()
    if image_path is None:
        st.warning(f"ไม่พบรูปหม้อแปลงในโฟลเดอร์ {IMAGE_DIR}")
        return TRANSPARENT_PIXEL_URI

    try:
        return transparent_data_uri(image_path.read_bytes())
    except (Image.DecompressionBombError, OSError, ValueError) as exc:
        st.error(f"ประมวลผลรูปหม้อแปลง {image_path} ไม่ได้: {exc}")
        return TRANSPARENT_PIXEL_URI


def render_transformer_info_page(go) -> None:
    page_html = _read_template()
    if page_html is None:
        return
    page_html = page_html.replace(
        'src="__TRANSFORMER_IMG__"',
        f'src="{_load_image_uri()}"',
        1,
    )
    page_html = page_html.replace("__HERO_BACKGROUND_CSS__", HERO_BACKGROUND_CSS, 1)
    page_html = page_html.replace("__HERO_NETWORK_SCRIPT__", HERO_NETWORK_SCRIPT, 1)

    st.markdown(
        """
        <style>
        html, body, .stApp, [data-testid="stApp"],
        [data-testid="stAppViewContainer"], [data-testid="stMain"],
        [data-testid="stMainBlockContainer"], .main, .block-container {
            background: #F3F7FC !important;
            background-image: none !important;
        }
        .stApp::before, .stApp::after,
        [data-testid="stAppViewContainer"]::before,
        [data-testid="stAppViewContainer"]::after {
            display: none !important;
        }
        [data-testid="stSidebar"], [data-testid="stSidebarNav"],
        [data-testid="stSidebarCollapsedControl"], [data-testid="stHeader"] {
            display: none !important;
        }
        .block-container {
            max-width: none !important;
            padding: .35rem .75rem 0 !important;
        }
        .stApp div.st-key-transformer_info_home div.stButton > button,
        .stApp div.st-key-transformer_info_open_3d div.stButton > button,
        .stApp div.st-key-transformer_info_open_calculator div.stButton > button {
            position: relative;
            overflow: hidden;
            width: 100%;
            border: 1px solid #bfd2e6 !important;
            border-radius: 14px !important;
            background: #ffffff !important;
            transition: transform .2s, box-shadow .2s, background .2s;
        }
        .stApp div.st-key-transformer_info_home div.stButton > button p,
        .stApp div.st-key-transformer_info_open_3d div.stButton > button p,
        .stApp div.st-key-transformer_info_open_calculator div.stButton > button p {
            color: #104f8c !important;
            font-weight: 700;
        }
        .stApp div.st-key-transformer_info_home div.stButton > button:hover,
        .stApp div.st-key-transformer_info_open_3d div.stButton > button:hover,
        .stApp div.st-key-transformer_info_open_calculator div.stButton > button:hover {
            border-color: #176fc5 !important;
            background: #edf6ff !important;
            box-shadow: 0 6px 18px rgba(23, 111, 197, .12);
            transform: translateY(-2px);
        }
        .stApp div.st-key-transformer_info_home div.stButton > button:hover p,
        .stApp div.st-key-transformer_info_open_3d div.stButton > button:hover p,
        .stApp div.st-key-transformer_info_open_calculator div.stButton > button:hover p {
            color: #104f8c !important;
        }
        iframe[title="ข้อมูลหม้อแปลงไฟฟ้า"] {
            display: block;
            width: 100% !important;
            height: calc(100vh - 82px) !important;
            min-height: 480px;
            border: 0;
            background: #F3F7FC !important;
        }
        @media (prefers-reduced-motion: reduce) {
            .stApp div.st-key-transformer_info_home div.stButton > button,
            .stApp div.st-key-transformer_info_open_3d div.stButton > button,
            .stApp div.st-key-transformer_info_open_calculator div.stButton > button {
                transition: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    back, model, calculator = st.columns(3)
    with back:
        st.button(
            "← หน้าแรก",
            on_click=go,
            args=(calculator_page.PAGE_HOME,),
            key="transformer_info_home",
            **BUTTON_WIDTH,
        )
    with model:
        st.button(
            "เปิดโมเดล 3D",
            on_click=go,
            args=(calculator_page.PAGE_TRANSFORMER_3D,),
            key="transformer_info_open_3d",
            **BUTTON_WIDTH,
        )
    with calculator:
        st.button(
            "คำนวณขนาดหม้อแปลง",
            on_click=go,
            args=(calculator_page.PAGE_TRANSFORMER_CALC,),
            key="transformer_info_open_calculator",
            **BUTTON_WIDTH,
        )

    st.iframe(
        apply_embedded_theme(page_html),
        width="stretch",
        height=900,
        alt="ข้อมูลหม้อแปลงไฟฟ้า",
    )
