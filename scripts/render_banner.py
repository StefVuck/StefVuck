#!/usr/bin/env python3
"""Regenerate the ASCII-portrait banner and language leaderboard as SVGs and
wire them into README.md, so the profile README stays reproducible instead
of being a hand-edited static blob.

SVG (not a plain-text code block) is what gives these real color and lets
GitHub scale them to fit the README column instead of horizontal-scrolling
a wide <pre> block.

Run via .github/workflows/update-profile-banner.yml after the
Github-Language-Stats action refreshes stats/*.json, or manually with:
    python scripts/render_banner.py
"""
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).parent))
from ascii_face import build_ascii
import svg_banner
import svg_leaderboard

ROOT = Path(__file__).parent.parent
README_PATH = ROOT / "README.md"
FACE_SOURCE = ROOT / "assets" / "ascii_face_source.png"
LEADERBOARD_JSON = ROOT / "stats" / "leaderboard_by_lines.json"
LANGUAGE_COLORS_PATH = Path(__file__).parent / "language_colors.json"
ASSETS_DIR = ROOT / "assets"
USERNAME = "StefVuck"

BANNER_START, BANNER_END = "<!--ASCII-BANNER:START-->", "<!--ASCII-BANNER:END-->"
LEADERBOARD_START, LEADERBOARD_END = "<!--LANG-LEADERBOARD:START-->", "<!--LANG-LEADERBOARD:END-->"

# Fallback profile data used if the GitHub API call fails (e.g. rate limit),
# so a flaky run doesn't wipe the banner. Update if these facts change.
FALLBACK_PROFILE = {
    "public_repos": 37,
    "followers": 37,
    "following": 20,
    "public_gists": 4,
    "created_at": "2023-08-15T16:20:05Z",
}

FALLBACK_LEADERBOARD = [
    {"language": "TypeScript", "value": 35600, "color": "#2b7489"},
    {"language": "Python", "value": 18300, "color": "#3572A5"},
    {"language": "Swift", "value": 13200, "color": "#ffac45"},
    {"language": "Lua", "value": 4300, "color": "#000080"},
    {"language": "Elixir", "value": 3600, "color": "#6e4a7e"},
    {"language": "Go", "value": 3300, "color": "#00ADD8"},
    {"language": "CUDA", "value": 2500, "color": "#888888"},
    {"language": "Nix", "value": 2300, "color": "#7e7eff"},
    {"language": "C++", "value": 1900, "color": "#f34b7d"},
    {"language": "Zig", "value": 1500, "color": "#ec915c"},
    {"language": "Shell", "value": 1500, "color": "#89e051"},
    {"language": "Haskell", "value": 988, "color": "#5e5086"},
    {"language": "C", "value": 683, "color": "#555555"},
    {"language": "Rust", "value": 548, "color": "#dea584"},
    {"language": "COBOL", "value": 367, "color": "#555555"},
    {"language": "Arduino", "value": 299, "color": "#bd79d1"},
    {"language": "Assembly", "value": 287, "color": "#6E4C13"},
    {"language": "PowerShell", "value": 287, "color": "#012456"},
    {"language": "SQL", "value": 275, "color": "#e38c00"},
    {"language": "Dockerfile", "value": 171, "color": "#384d54"},
    {"language": "CMake", "value": 81, "color": "#DA3434"},
    {"language": "Makefile", "value": 45, "color": "#427819"},
    {"language": "Svelte", "value": 31, "color": "#ff3e00"},
]


def fetch_profile() -> dict:
    url = f"https://api.github.com/users/{USERNAME}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USERNAME}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=10) as resp:
            return json.load(resp)
    except (URLError, TimeoutError, OSError) as exc:
        print(f"Warning: could not fetch live profile ({exc}); using fallback data")
        return FALLBACK_PROFILE


def format_uptime(created_at: str, today: date = None) -> str:
    created = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").date()
    today = today or date.today()

    years = today.year - created.year
    months = today.month - created.month
    days = today.day - created.day
    if days < 0:
        months -= 1
        prev_month = today.month - 1 or 12
        prev_year = today.year if today.month > 1 else today.year - 1
        import calendar
        days += calendar.monthrange(prev_year, prev_month)[1]
    if months < 0:
        years -= 1
        months += 12

    return f"{years} years, {months} months, {days} days"


def load_leaderboard_data() -> list[dict]:
    if LEADERBOARD_JSON.exists():
        with open(LEADERBOARD_JSON, encoding="utf-8") as f:
            data = json.load(f)
        if data:
            return sorted(data, key=lambda d: d["value"], reverse=True)

    print("Warning: no stats/leaderboard_by_lines.json found; using fallback data")
    return FALLBACK_LEADERBOARD


def build_stats_rows(profile: dict, top_language: str, language_count: int) -> list[dict]:
    uptime = format_uptime(profile.get("created_at", FALLBACK_PROFILE["created_at"]))
    return [
        {"type": "header", "text": f"stefan@{USERNAME.lower()}"},
        {"type": "rule"},
        {"type": "kv", "label": "OS", "value": "macOS, Linux, Embedded Targets"},
        {"type": "kv", "label": "Host", "value": "University of Glasgow"},
        {"type": "kv", "label": "Uptime", "value": uptime},
        {"type": "kv", "label": "Role", "value": "Software Dev @ Squarepoint Capital"},
        {"type": "kv", "label": "Field", "value": "MEng Electronics & Software Eng."},
        {"type": "kv", "label": "IDE", "value": "Neovim, VS Code, CLion"},
        {"type": "blank"},
        {"type": "kv", "label": "Languages.Proficient", "value": "Python, C++, TypeScript, JS"},
        {"type": "kv", "label": "Languages.Learning", "value": "Rust, Elixir, ARM/x86 Assembly"},
        {"type": "kv", "label": "Languages.Real", "value": "English"},
        {"type": "blank"},
        {"type": "section", "text": "Contact"},
        {"type": "kv", "label": "Email", "value": "stefan@stefvuck.dev"},
        {"type": "kv", "label": "LinkedIn", "value": "/in/stefan-vučković"},
        {"type": "kv", "label": "Portfolio", "value": "stefvuck.dev"},
        {"type": "kv", "label": "GitHub", "value": f"@{USERNAME}"},
        {"type": "blank"},
        {"type": "section", "text": "GitHub Stats"},
        {"type": "raw", "text": (
            f"Repos: {profile.get('public_repos', '?')}     "
            f"Followers: {profile.get('followers', '?')}     "
            f"Following: {profile.get('following', '?')}"
        )},
        {"type": "kv", "label": "Public Gists", "value": str(profile.get("public_gists", "?"))},
        {"type": "kv", "label": "Languages Tracked", "value": f"{language_count} ({top_language} top)"},
    ]


def replace_between(content: str, start_marker: str, end_marker: str, new_block: str) -> str:
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    replacement = f"{start_marker}\n{new_block}\n{end_marker}"
    if not pattern.search(content):
        raise ValueError(f"Markers {start_marker}/{end_marker} not found in README.md")
    return pattern.sub(lambda _m: replacement, content, count=1)


def picture_tag(dark_path: str, light_path: str, alt: str) -> str:
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="{dark_path}">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="{light_path}">\n'
        f'  <img alt="{alt}" src="{light_path}">\n'
        "</picture>"
    )


def main():
    ASSETS_DIR.mkdir(exist_ok=True)

    profile = fetch_profile()
    leaderboard_data = load_leaderboard_data()
    top_language = leaderboard_data[0]["language"] if leaderboard_data else "N/A"
    language_count = len(leaderboard_data)

    face_lines = build_ascii(str(FACE_SOURCE))
    stats_rows = build_stats_rows(profile, top_language, language_count)

    for theme in ("dark", "light"):
        banner_svg = svg_banner.render(face_lines, stats_rows, theme_name=theme)
        (ASSETS_DIR / f"banner_{theme}.svg").write_text(banner_svg, encoding="utf-8")

        leaderboard_svg = svg_leaderboard.render(leaderboard_data, USERNAME, theme_name=theme)
        (ASSETS_DIR / f"leaderboard_{theme}.svg").write_text(leaderboard_svg, encoding="utf-8")

    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_between(
        readme, BANNER_START, BANNER_END,
        picture_tag("assets/banner_dark.svg", "assets/banner_light.svg",
                    "ASCII portrait and neofetch-style stats for StefVuck")
    )
    readme = replace_between(
        readme, LEADERBOARD_START, LEADERBOARD_END,
        picture_tag("assets/leaderboard_dark.svg", "assets/leaderboard_light.svg",
                    "Language usage leaderboard for StefVuck")
    )

    old = README_PATH.read_text(encoding="utf-8")
    if readme != old:
        README_PATH.write_text(readme, encoding="utf-8")
        print("README.md updated")
    else:
        print("README.md already up to date")


if __name__ == "__main__":
    main()
