"""Shared styling for standalone documents embedded inside the Streamlit app."""


EMBEDDED_THEME_CSS = """
:root {
  color-scheme: light !important;
  --bg: #f3f7fc !important;
  --bg2: #ffffff !important;
  --panel: #ffffff !important;
  --card: #ffffff !important;
  --main: #eaf2fa !important;
  --navy: #f3f7fc !important;
  --line: #d7e2ee !important;
  --line2: #bfd2e6 !important;
  --tx: #17324f !important;
  --ink: #17324f !important;
  --mut: #5b7188 !important;
  --mute: #5b7188 !important;
  --orange: #176fc5 !important;
  --ember1: #176fc5 !important;
  --ember2: #4a9be0 !important;
  --hi: #176fc5 !important;
  --cy: #358fda !important;
  --glow: rgba(23, 111, 197, .08) !important;
}
html, body {
  color-scheme: light !important;
  background: #f3f7fc !important;
  color: #17324f !important;
  font-family: 'Sarabun', 'Noto Sans Thai', Tahoma, sans-serif !important;
}
body { line-height: 1.65 !important; }
body::before, body::after { pointer-events: none; }
h1, h2, h3, h4, p, label, small, th, td { text-shadow: none !important; }
h1, h2, h3, h4 { color: #12385f !important; }
p, label, small { color: #506982 !important; }
a { color: #176fc5; }
.top, .sysbar, header {
  color: #17324f !important;
  background: rgba(255, 255, 255, .96) !important;
  border-color: #d7e2ee !important;
  box-shadow: 0 4px 16px rgba(23, 50, 79, .04) !important;
  backdrop-filter: blur(10px);
}
.hero, .panel, .card, .box, .meter, .tablebox, .glass, .search, .foot,
dialog, .detail, .result, .section-card {
  color: #17324f !important;
  background: #ffffff !important;
  border-color: #d7e2ee !important;
  box-shadow: 0 8px 24px rgba(23, 50, 79, .06) !important;
  backdrop-filter: none !important;
}
button, .btn, .chip, .jump, input, select, textarea {
  border-color: #bfd2e6 !important;
  border-radius: 10px !important;
  background: #ffffff !important;
  color: #173e68 !important;
  box-shadow: none !important;
  font-family: 'Sarabun', 'Noto Sans Thai', Tahoma, sans-serif !important;
}
button:hover, .btn:hover, .chip:hover, .jump:hover {
  border-color: #176fc5 !important;
  background: #edf6ff !important;
  color: #104f8c !important;
}
input:focus-visible, select:focus-visible, textarea:focus-visible,
button:focus-visible, a:focus-visible {
  outline: 3px solid rgba(23, 111, 197, .22) !important;
  outline-offset: 2px;
}
thead th { color: #36536f !important; background: #edf4fb !important; }
tbody tr:hover { background: #f0f7ff !important; }
@media (max-width: 640px) {
  .wrap { width: 100% !important; max-width: 100% !important; padding: 16px !important; }
  .top { padding: 10px 14px !important; }
  .hero { padding: 22px 18px !important; }
  .tablebox { max-width: 100vw; overflow-x: auto; }
  button, .btn, .chip, .jump { min-height: 44px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
"""


def apply_embedded_theme(page_html):
    """Add the shared app theme after a standalone page's existing styles."""
    theme = f"<style>{EMBEDDED_THEME_CSS}</style>"
    if "</head>" in page_html:
        return page_html.replace("</head>", theme + "</head>", 1)
    if "</body>" in page_html:
        return page_html.replace("</body>", theme + "</body>", 1)
    return page_html + theme
