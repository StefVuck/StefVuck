"""Compose the face+stats pane and the lang-stats/selected-repos panes into
one tmux-style terminal window: a single title bar, one pane on top and a
vertical split underneath, joined by pane-divider lines.
"""
from svg_common import THEMES, wrap_terminal
import svg_banner
import svg_leaderboard


def render(face_lines: list[str], stats_rows: list[dict], leaderboard_data: list[dict],
           username: str, repos: list[dict], theme_name: str = "dark") -> str:
    theme = THEMES[theme_name]
    pad = 16
    gap = pad * 2

    top_body, top_w, top_h = svg_banner.body(face_lines, stats_rows, theme)

    board_body, board_w, board_h = svg_leaderboard.leaderboard_body(
        leaderboard_data, username, theme, font_size=13, bar_max_px=260, pad=pad
    )
    repos_x_local = board_w + gap
    repos_body, repos_content_h = svg_leaderboard.repos_body(
        repos, theme, font_size=13, x=repos_x_local + pad, pad=pad, panel_width=320
    )
    bottom_w = repos_x_local + pad + 320 + pad
    bottom_h = max(board_h, int(repos_content_h))

    total_w = max(top_w, bottom_w)
    total_h = top_h + gap + bottom_h + pad

    parts = [f'<g>{top_body}</g>']

    hdiv_y = top_h + pad
    parts.append(
        f'<line x1="0" y1="{hdiv_y}" x2="{total_w}" y2="{hdiv_y}" stroke="{theme["border"]}"/>'
    )

    bottom_y = top_h + gap
    parts.append(f'<g transform="translate(0,{bottom_y})">{board_body}</g>')

    vdiv_x = pad + board_w + pad
    parts.append(
        f'<line x1="{vdiv_x}" y1="{bottom_y + pad}" x2="{vdiv_x}" y2="{bottom_y + pad + bottom_h}" '
        f'stroke="{theme["border"]}"/>'
    )

    parts.append(f'<g transform="translate(0,{bottom_y})">{repos_body}</g>')

    title = f"stefan@{username.lower()}: ~ (neofetch | lang-stats | selected-repos)"
    return wrap_terminal(total_w, total_h, theme, ''.join(parts), title=title)
