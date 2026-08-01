"""Build a colored, proportional bar-chart SVG for the language leaderboard,
with an optional "selected repos" panel beside it so the wide gap next to a
tall, narrow bar chart doesn't go to waste.

A real per-language-colored bar chart reads far better than a monochrome
density-ramp text chart: color separates the rows at a glance, and exact bar
length (sqrt-scaled so the long tail stays visible) makes the breadth of
languages used obvious rather than just the top one.
"""
import math
import textwrap

from svg_common import esc, char_width


def leaderboard_body(data: list[dict], username: str, theme: dict, font_size: int,
                       bar_max_px: int, pad: int):
    cw = char_width(font_size)
    line_h = font_size + 9
    row_gap_after_header = line_h * 2

    name_col_chars = max((len(d["language"]) for d in data), default=8) + 1
    name_col_px = name_col_chars * cw
    value_col_px = 7 * cw

    total = sum(d["value"] for d in data)
    max_val = max((d["value"] for d in data), default=1)
    scaled_max = math.sqrt(max_val) if max_val > 0 else 1

    def fmt(v):
        return f'{v/1000:.1f}K' if v >= 1000 else str(int(v))

    width = int(name_col_px + bar_max_px + value_col_px + 12)
    height = int(row_gap_after_header + len(data) * line_h)

    parts = [
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

        parts.append(
            f'<text x="{bar_x - 6}" y="{y_text}" font-size="{font_size}" text-anchor="end" '
            f'fill="{theme["text"]}">{esc(entry["language"])}</text>'
        )
        parts.append(
            f'<rect x="{bar_x}" y="{y_top}" width="{bar_max_px}" height="{bar_h}" rx="2" '
            f'fill="{theme["border"]}"/>'
        )
        parts.append(
            f'<rect x="{bar_x}" y="{y_top}" width="{filled}" height="{bar_h}" rx="2" '
            f'fill="{entry["color"]}"/>'
        )
        parts.append(
            f'<text x="{bar_x + bar_max_px + 8}" y="{y_text}" font-size="{font_size}" '
            f'fill="{theme["muted"]}">{fmt(entry["value"])}</text>'
        )

    return ''.join(parts), width, height


def repos_body(repos: list[dict], theme: dict, font_size: int, x: int, pad: int,
                 panel_width: int):
    line_h = font_size + 8
    y = pad + font_size

    parts = [
        f'<text x="{x}" y="{y}" font-size="{font_size + 2}" font-weight="bold" '
        f'fill="{theme["section"]}">$ ls ~/selected-repos</text>'
    ]
    y += line_h * 1.6

    # measured at font_size (the desc text's actual size), with a safety margin
    # since char_width is an approximation of real glyph metrics
    wrap_width = max(15, int(panel_width / char_width(font_size)) - 2)

    for repo in repos:
        parts.append(
            f'<text x="{x}" y="{y}" font-size="{font_size}" font-weight="bold" '
            f'fill="{theme["accent"]}">&#9656; {esc(repo["name"])}</text>'
        )
        y += line_h
        parts.append(
            f'<text x="{x}" y="{y}" font-size="{font_size - 1}" font-style="italic" '
            f'fill="{theme["key"]}">{esc(repo["tech"])}</text>'
        )
        y += line_h

        for wrapped_line in textwrap.wrap(repo["desc"], width=wrap_width) or [""]:
            parts.append(
                f'<text x="{x}" y="{y}" font-size="{font_size}" '
                f'fill="{theme["text"]}">{esc(wrapped_line)}</text>'
            )
            y += line_h
        y += line_h * 0.5

    return ''.join(parts), y
