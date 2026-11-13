"""Reusable technology-style header for the Streamlit application."""

import html

import streamlit as st


THEMES = {
    "blue": (
        "--panel:#ffffff;--core:#f3f7fc;--ink:#17324f;--mute:#5b7188;"
        "--line:#d7e2ee;--hi:#176fc5;--cy:#65a7e5;--deep:#104f8c;"
        "--onacc:#fff;--glow:rgba(23,111,197,.12);"
    ),
    "fire": (
        "--panel:rgba(35,21,17,.94);--core:#1a0a05;--ink:#fff1e4;--mute:#e7c9b4;"
        "--line:rgba(255,100,30,.35);--hi:#ff5a14;--cy:#ffb070;--deep:#b91c1c;"
        "--onacc:#fff;--glow:rgba(255,80,0,.4);"
    ),
}

CSS = r"""
.st-key-ak_header {
  --panel:#ffffff;--core:#f3f7fc;--ink:#17324f;--mute:#5b7188;
  --line:#d7e2ee;--hi:#176fc5;--cy:#65a7e5;--deep:#104f8c;
  --onacc:#fff;--glow:rgba(23,111,197,.12);
  position:relative;isolation:isolate;overflow:hidden;
  border:1px solid var(--line);border-radius:22px;
  padding:18px clamp(16px,2.4vw,28px) 14px;
  background:radial-gradient(ellipse 50% 160% at 0% 0%,rgba(23,111,197,.08),transparent 70%),var(--panel);
  -webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);
  box-shadow:0 0 0 1px rgba(255,255,255,.03) inset,0 18px 50px -18px var(--glow)
}
.st-key-ak_header::before {
  position:absolute;z-index:-1;inset:0;pointer-events:none;opacity:.35;
  background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);
  background-size:36px 36px;content:"";
  -webkit-mask-image:radial-gradient(ellipse at 15% 0%,#000,transparent 70%);
  mask-image:radial-gradient(ellipse at 15% 0%,#000,transparent 70%)
}
.st-key-ak_header [data-testid="stVerticalBlock"]{position:relative;z-index:1}
.ak-brand{display:flex;align-items:center;gap:16px;min-height:58px}
.ak-logo{position:relative;display:grid;width:64px;height:58px;flex:none;place-items:center;
  border:1px solid transparent;border-radius:13px;font-size:1.4rem;font-weight:800;letter-spacing:.04em;
  background:linear-gradient(var(--core),var(--core)) padding-box,
    conic-gradient(from 0deg,var(--hi),#65a7e5 22%,transparent 42%,var(--cy) 60%,transparent 78%,var(--hi)) border-box;
  box-shadow:0 0 22px -4px var(--glow),inset 0 0 18px rgba(23,111,197,.08);
}
.ak-logo::before{position:absolute;inset:5px;border:1px solid rgba(23,111,197,.22);border-radius:8px;content:""}
.ak-logo span{position:relative;background:linear-gradient(135deg,#17324f,#176fc5 55%,#65a7e5);
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.ak-brand-copy{min-width:0}
.ak-ttl{display:block;color:#17324f;font-size:clamp(1.25rem,2.2vw,1.8rem);font-weight:700;line-height:1.2}
.ak-sub{display:block;margin-top:3px;color:var(--mute);font-size:.68rem;letter-spacing:.16em}
.st-key-ak_auth{display:flex;justify-content:flex-end;align-items:center;gap:10px}
.ak-user{color:var(--mute);font-size:.9rem}
.stApp .st-key-header_login div.stButton>button,.stApp .st-key-header_register div.stButton>button{
  min-height:44px!important;border-radius:12px!important
}
.stApp .st-key-header_login div.stButton>button{border:1px solid var(--hi)!important;
  background:linear-gradient(135deg,var(--deep),var(--hi) 60%,#4a9be0)!important}
.stApp .st-key-header_login div.stButton>button p{color:#fff!important;font-weight:700!important}
.stApp .st-key-header_register div.stButton>button{
  border:1px solid var(--line)!important;background:rgba(255,255,255,.04)!important
}
.stApp .st-key-header_register div.stButton>button p{color:var(--ink)!important;font-weight:600!important}
.stApp .st-key-header_login div.stButton>button:hover,
.stApp .st-key-header_register div.stButton>button:hover{
  transform:translateY(-1px);box-shadow:0 0 20px -2px var(--glow)
}
@keyframes akpulse{0%,100%{box-shadow:0 0 16px -2px var(--glow)}50%{box-shadow:0 0 28px 2px var(--glow)}}
@media(max-width:640px){
  .st-key-ak_header{padding:14px}
  .st-key-ak_auth{justify-content:flex-start}
}
@media(prefers-reduced-motion:reduce){
  .st-key-ak_header *{animation:none!important;transition:none!important}
}
"""


def render_header(
    on_navigate,
    theme: str = "fire",
    user: str | None = None,
) -> None:
    """Render the shared brand and authentication controls."""
    theme_vars = THEMES.get(theme, THEMES["blue"])
    st.markdown(
        f"<style>{CSS}.st-key-ak_header{{{theme_vars}}}</style>",
        unsafe_allow_html=True,
    )
    with st.container(key="ak_header"):
        brand_column, auth_column = st.columns([1.3, 1], vertical_alignment="center")
        with brand_column:
            st.markdown(
                '<div class="ak-brand"><div class="ak-logo"><span>AK</span></div>'
                '<div class="ak-brand-copy"><span class="ak-ttl">Electrical Calculator</span>'
                '<small class="ak-sub">ATTAPORN ENGINEERING &amp; SUPPLY</small></div></div>',
                unsafe_allow_html=True,
            )
        with auth_column:
            with st.container(horizontal=True, wrap=True, key="ak_auth"):
                if user:
                    st.markdown(
                        f'<span class="ak-user">สวัสดี, {html.escape(user)}</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.button(
                        "Login",
                        key="header_login",
                        on_click=on_navigate,
                        args=("login",),
                        width="content",
                    )
                    st.button(
                        "Register",
                        key="header_register",
                        on_click=on_navigate,
                        args=("register",),
                        width="content",
                    )
