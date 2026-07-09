"""Build a colored, proportional bar-chart SVG for the language leaderboard.

A real per-language-colored bar chart reads far better than a monochrome
density-ramp text chart: color separates the rows at a glance, and exact bar
length (sqrt-scaled so the long tail stays visible) makes the breadth of
languages used obvious rather than just the top one.
"""
import math

from svg_common import esc, char_width, wrap_card, THEMES


def render(data: list[dict], username: str, theme_name: str = "dark",
           font_size: int = 13, bar_max_px: int = 260) -> str:
    """data: [{"language": str, "value": number, "color": "#hex"}, ...] sorted desc."""
    theme = THEMES[theme_name]
    cw = char_width(font_size)
    line_h = font_size + 9
    pad = 16
    row_gap_after_header = line_h * 2

    name_col_chars = max((len(d["language"]) for d in data), default=8) + 1
    name_col_px = name_col_chars * cw
    value_col_px = 7 * cw

    total = sum(d["value"] for d in data)
    max_val = max((d["value"] for d in data), default=1)
    scaled_max = math.sqrt(max_val) if max_val > 0 else 1

    def fmt(v):
        return f'{v/1000:.1f}K' if v >= 1000 else str(int(v))

    width = int(pad * 2 + name_col_px + bar_max_px + value_col_px + 12)
    height = int(pad * 2 + row_gap_after_header + len(data) * line_h)

    body_parts = [
        f'<text x="{pad}" y="{pad + font_size}" font-size="{font_size + 2}" '
        f'font-weight="bold" fill="{theme["section"]}">'
        f'$ lang-stats --by-lines {esc(username)}</text>',
        f'<text x="{pad}" y="{pad + font_size + line_h}" font-size="{font_size}" '
        f'fill="{theme["muted"]}">{len(data)} languages tracked &#183; {fmt(total)} lines total</text>',
    ]

    bar_x = pad + name_col_px
    for i, entry in enumerate(data):
        y_top = pad + row_gap_after_header + i * line_h
        y_text = y_top + font_size
        bar_h = font_size - 1

        filled = max(4, round(math.sqrt(max(entry["value"], 0)) / scaled_max * bar_max_px))

        body_parts.append(
            f'<text x="{bar_x - 6}" y="{y_text}" font-size="{font_size}" text-anchor="end" '
            f'fill="{theme["text"]}">{esc(entry["language"])}</text>'
        )
        body_parts.append(
            f'<rect x="{bar_x}" y="{y_top}" width="{bar_max_px}" height="{bar_h}" rx="2" '
            f'fill="{theme["border"]}"/>'
        )
        body_parts.append(
            f'<rect x="{bar_x}" y="{y_top}" width="{filled}" height="{bar_h}" rx="2" '
            f'fill="{entry["color"]}"/>'
        )
        body_parts.append(
            f'<text x="{bar_x + bar_max_px + 8}" y="{y_text}" font-size="{font_size}" '
            f'fill="{theme["muted"]}">{fmt(entry["value"])}</text>'
        )

    return wrap_card(width, height, theme, ''.join(body_parts))
