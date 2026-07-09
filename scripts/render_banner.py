#!/usr/bin/env python3
"""Regenerate the ASCII portrait / neofetch banner and text leaderboard in
README.md from live data, so the profile README stays reproducible instead
of being a hand-edited static blob.

Run via `.github/workflows/update-profile-banner.yml` after the
Github-Language-Stats action refreshes stats/*.txt, or manually with:
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

ROOT = Path(__file__).parent.parent
README_PATH = ROOT / "README.md"
FACE_SOURCE = ROOT / "assets" / "ascii_face_source.png"
LEADERBOARD_TXT = ROOT / "stats" / "leaderboard_by_lines.txt"
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


def read_leaderboard() -> tuple[str, str, str]:
    """Returns (leaderboard_block_text, top_language, language_count)."""
    if not LEADERBOARD_TXT.exists():
        placeholder = (
            "$ lang-stats --by-lines StefVuck\n"
            "(no data yet - run the Update Language Statistics workflow first)"
        )
        return placeholder, "N/A", "?"

    text = LEADERBOARD_TXT.read_text(encoding="utf-8").rstrip("\n")
    lines = text.splitlines()

    count_match = re.search(r"(\d+) languages tracked", lines[1] if len(lines) > 1 else "")
    language_count = count_match.group(1) if count_match else "?"

    top_language = "N/A"
    for line in lines[2:]:
        stripped = line.strip()
        if stripped and not set(stripped) <= {"-"}:
            top_language = stripped.split()[0]
            break

    return text, top_language, language_count


def build_stats_lines(profile: dict, top_language: str, language_count: str) -> list[str]:
    uptime = format_uptime(profile.get("created_at", FALLBACK_PROFILE["created_at"]))
    return [
        f"stefan@{USERNAME.lower()}",
        "-----------------------------------",
        "OS: ................. macOS, Linux, Embedded Targets",
        "Host: ............... University of Glasgow",
        f"Uptime: .............. {uptime}",
        "Role: ................ Software Dev @ Squarepoint Capital",
        "Field: ............... MEng Electronics & Software Eng.",
        "IDE: ................. Neovim, VS Code, CLion",
        "",
        "Languages.Proficient:  Python, C++, TypeScript, JS",
        "Languages.Learning:    Rust, Elixir, ARM/x86 Assembly",
        "Languages.Real:        English",
        "",
        "Contact -----------------------------------",
        "Email: ............... stefan@stefvuck.dev",
        "LinkedIn: ............ /in/stefan-vučković",
        "Portfolio: ........... stefvuck.dev",
        f"GitHub: .............. @{USERNAME}",
        "",
        "GitHub Stats -----------------------------------",
        f"Repos: {profile.get('public_repos', '?')}     "
        f"Followers: {profile.get('followers', '?')}     "
        f"Following: {profile.get('following', '?')}",
        f"Public Gists: {profile.get('public_gists', '?')}",
        f"Languages tracked: {language_count}     Top: {top_language}",
    ]


def merge_face_and_stats(face_lines: list[str], stats_lines: list[str]) -> str:
    face_width = max(len(line) for line in face_lines)
    total = max(len(face_lines), len(stats_lines))
    out = []
    for i in range(total):
        face = face_lines[i] if i < len(face_lines) else ""
        stat = stats_lines[i] if i < len(stats_lines) else ""
        out.append(f"{face.ljust(face_width)}   {stat}".rstrip())
    return "\n".join(out)


def replace_between(content: str, start_marker: str, end_marker: str, new_block: str) -> str:
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL
    )
    replacement = f"{start_marker}\n```\n{new_block}\n```\n{end_marker}"
    if not pattern.search(content):
        raise ValueError(f"Markers {start_marker}/{end_marker} not found in README.md")
    return pattern.sub(lambda _m: replacement, content, count=1)


def main():
    profile = fetch_profile()
    leaderboard_text, top_language, language_count = read_leaderboard()

    face_lines = build_ascii(str(FACE_SOURCE))
    stats_lines = build_stats_lines(profile, top_language, language_count)
    banner = merge_face_and_stats(face_lines, stats_lines)

    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_between(readme, BANNER_START, BANNER_END, banner)
    readme = replace_between(readme, LEADERBOARD_START, LEADERBOARD_END, leaderboard_text)

    old = README_PATH.read_text(encoding="utf-8")
    if readme != old:
        README_PATH.write_text(readme, encoding="utf-8")
        print("README.md updated")
    else:
        print("README.md already up to date")


if __name__ == "__main__":
    main()
