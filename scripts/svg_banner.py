"""Build the ASCII-portrait + neofetch-stats pane content as SVG fragments.

Rendering as SVG (rather than a markdown code fence) is what gives the
banner real color and lets it scale to the README column width instead of
forcing a horizontal scrollbar.
"""
from svg_common import esc, char_width


def _stats_line_width(rows: list[dict], label_col: int) -> int:
    widest = 0
    for row in rows:
        if row["type"] == "kv":
            text = f'{row["label"]}: ' + '.' * max(label_col - len(row["label"]) - 1, 3) + f' {row["value"]}'
        elif row["type"] == "kv2":
            text = "   |   ".join(f'{label}: {value}' for label, value in row["pairs"])
        else:
            text = row.get("text", "")
        widest = max(widest, len(text))
    return widest


def label_column_width(rows: list[dict]) -> int:
    return max((len(r["label"]) + 1 for r in rows if r["type"] == "kv"), default=10) + 1


def body(face_lines: list[str], stats_rows: list[dict], theme: dict, font_size: int = 14,
         face_font_size: int = 8, pad: int = 16):
    """Returns (svg_fragment, width, height) for the face+stats pane.

    The portrait renders at its own (smaller) font size so a tall, high-detail
    ASCII face stays roughly stats-height instead of dominating the pane.
    """
    cw = char_width(font_size)
    line_h = font_size + 6
    face_cw = char_width(face_font_size)
    face_line_h = face_font_size + 4

    face_w_chars = max((len(l) for l in face_lines), default=0)
    label_col = label_column_width(stats_rows)
    stats_w_chars = _stats_line_width(stats_rows, label_col)
    gutter_chars = 4

    face_px = face_w_chars * face_cw
    gutter_px = gutter_chars * cw
    stats_px = stats_w_chars * cw

    face_h = len(face_lines) * face_line_h
    stats_h = len(stats_rows) * line_h

    width = int(pad * 2 + face_px + gutter_px + stats_px)
    height = int(pad * 2 + max(face_h, stats_h))

    parts = []

    for i, line in enumerate(face_lines):
        y = pad + (i + 1) * face_line_h - 4
        parts.append(
            f'<text x="{pad}" y="{y}" font-size="{face_font_size}" fill="{theme["accent"]}" '
            f'xml:space="preserve">{esc(line)}</text>'
        )

    stats_x = pad + face_px + gutter_px
    for i, row in enumerate(stats_rows):
        y = pad + (i + 1) * line_h - 4
        rtype = row["type"]

        if rtype == "blank":
            continue

        if rtype == "header":
            parts.append(
                f'<text x="{stats_x}" y="{y}" font-size="{font_size}" font-weight="bold" '
                f'fill="{theme["accent"]}">{esc(row["text"])}</text>'
            )
        elif rtype == "rule":
            dash_len = int(stats_w_chars)
            parts.append(
                f'<text x="{stats_x}" y="{y}" font-size="{font_size}" '
                f'fill="{theme["dots"]}">{"-" * dash_len}</text>'
            )
        elif rtype == "section":
            remaining = max(stats_w_chars - len(row["text"]) - 1, 3)
            parts.append(
                f'<text x="{stats_x}" y="{y}" font-size="{font_size}" font-weight="bold" '
                f'fill="{theme["section"]}">{esc(row["text"])} '
                f'<tspan fill="{theme["dots"]}">{"-" * remaining}</tspan></text>'
            )
        elif rtype == "raw":
            parts.append(
                f'<text x="{stats_x}" y="{y}" font-size="{font_size}" '
                f'fill="{theme["text"]}">{esc(row["text"])}</text>'
            )
        elif rtype == "kv":
            label = f'{row["label"]}:'
            dots = '.' * max(label_col - len(row["label"]) - 1, 3)
            parts.append(
                f'<text x="{stats_x}" y="{y}" font-size="{font_size}" xml:space="preserve">'
                f'<tspan fill="{theme["key"]}">{esc(label)}</tspan>'
                f'<tspan fill="{theme["dots"]}"> {esc(dots)} </tspan>'
                f'<tspan fill="{theme["text"]}">{esc(row["value"])}</tspan>'
                f'</text>'
            )
        elif rtype == "kv2":
            sub_col = row.get("sub_col", 10)
            tspans = []
            for idx, (sub_label, sub_value) in enumerate(row["pairs"]):
                sub_dots = '.' * max(sub_col - len(sub_label) - 1, 2)
                tspans.append(f'<tspan fill="{theme["key"]}">{esc(sub_label)}:</tspan>')
                tspans.append(f'<tspan fill="{theme["dots"]}"> {esc(sub_dots)} </tspan>')
                tspans.append(f'<tspan fill="{theme["text"]}">{esc(sub_value)}</tspan>')
                if idx == 0:
                    tspans.append(f'<tspan fill="{theme["dots"]}">   |   </tspan>')
            parts.append(
                f'<text x="{stats_x}" y="{y}" font-size="{font_size}" '
                f'xml:space="preserve">{"".join(tspans)}</text>'
            )

    return ''.join(parts), width, height
