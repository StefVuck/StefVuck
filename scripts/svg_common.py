"""Shared SVG helpers: theme colors, escaping, and the rounded-card wrapper.

Used by svg_banner.py and svg_leaderboard.py so the two generated images
share one look. SVG (not a plain-text code block) is what gives us real
color and lets GitHub scale the image to fit the README column instead of
horizontal-scrolling a wide <pre> block.
"""
from xml.sax.saxutils import escape as xml_escape

FONT_STACK = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"

TITLEBAR_H = 30
TRAFFIC_LIGHTS = (("#ff5f56", 14), ("#ffbd2e", 34), ("#27c93f", 54))

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "titlebar": "#161b22",
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
        "titlebar": "#f6f8fa",
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


def wrap_terminal(width: int, height: int, theme: dict, body: str, title: str = "") -> str:
    """Wrap body content in a tmux/Ghostty-style terminal window: rounded
    card, a titlebar with macOS-style traffic-light dots, and the body
    content (already laid out relative to y=0) shifted below it."""
    total_h = height + TITLEBAR_H
    clip_id = f"card-clip-{abs(hash((width, total_h, title))) % 100000}"

    dots = ''.join(
        f'<circle cx="{x}" cy="{TITLEBAR_H / 2}" r="6" fill="{color}"/>'
        for color, x in TRAFFIC_LIGHTS
    )
    title_svg = (
        f'<text x="{width / 2}" y="{TITLEBAR_H / 2 + 4}" font-size="12" '
        f'text-anchor="middle" fill="{theme["muted"]}">{esc(title)}</text>'
        if title else ''
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_h}" '
        f'viewBox="0 0 {width} {total_h}" font-family="{FONT_STACK}">'
        f'<defs><clipPath id="{clip_id}">'
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{total_h - 1}" rx="8"/>'
        f'</clipPath></defs>'
        f'<g clip-path="url(#{clip_id})">'
        f'<rect x="0" y="0" width="{width}" height="{total_h}" fill="{theme["bg"]}"/>'
        f'<rect x="0" y="0" width="{width}" height="{TITLEBAR_H}" fill="{theme["titlebar"]}"/>'
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{width}" y2="{TITLEBAR_H}" stroke="{theme["border"]}"/>'
        f'{dots}{title_svg}'
        f'<g transform="translate(0,{TITLEBAR_H})">{body}</g>'
        f'</g>'
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{total_h - 1}" rx="8" '
        f'fill="none" stroke="{theme["border"]}"/>'
        f'</svg>'
    )
