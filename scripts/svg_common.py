"""Shared SVG helpers: theme colors, escaping, and the rounded-card wrapper.

Used by svg_banner.py and svg_leaderboard.py so the two generated images
share one look. SVG (not a plain-text code block) is what gives us real
color and lets GitHub scale the image to fit the README column instead of
horizontal-scrolling a wide <pre> block.
"""
from xml.sax.saxutils import escape as xml_escape

FONT_STACK = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "dots": "#484f58",
        "key": "#e3b341",
        "accent": "#7ee3e3",
        "section": "#79c0ff",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "text": "#24292f",
        "muted": "#57606a",
        "dots": "#c9d1d9",
        "key": "#9a6700",
        "accent": "#0b6e6e",
        "section": "#0969da",
    },
}


def esc(text: str) -> str:
    return xml_escape(str(text))


def char_width(font_size: int) -> float:
    return font_size * 0.6


def wrap_card(width: int, height: int, theme: dict, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT_STACK}">'
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" '
        f'fill="{theme["bg"]}" stroke="{theme["border"]}"/>'
        f'{body}'
        f'</svg>'
    )
