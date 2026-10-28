"""Builds assets/profile-card.svg: ASCII portrait on the left, terminal-style info on the right.

Run locally:   python scripts/build_card.py
In Actions:    runs daily (see .github/workflows/update-card.yml) and refreshes the GitHub stats.

Only the Python standard library is needed. Edit the PROFILE section below to change the text.
"""
import json
import os
import urllib.request
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = os.environ.get("GH_USER") or "Pranav-embedded"
TOKEN = os.environ.get("GH_TOKEN") or ""

# ───────────────────────────── PROFILE (edit me) ─────────────────────────────
HANDLE = ("pranav", "duse")
INFO = [
    ("Role", "VLSI Engineer · RTL Design & Verification"),
    ("Status", "Final-year ECE student"),
    ("Education", "PES Modern College of Engineering, Pune"),
    ("Focus", "Verilog · VHDL · FPGA · Verification"),
    ("Building", "5-stage RISC-V (RV32I) CPU on FPGA"),
    ("Learning", "SystemVerilog · UVM"),
]
STACK = [
    ("HDL", "Verilog, VHDL, SystemVerilog"),
    ("Software", "C, C++, Python, MATLAB"),
    ("EDA", "Vivado, XSIM, ModelSim, KiCad"),
    ("Hardware", "STM32, Arduino, ESP32, FPGA"),
    ("Robotics", "ROS 2, Gazebo, Isaac Sim"),
]
CONTACT = [
    ("Email", "dusepranav@gmail.com"),
    ("LinkedIn", "pranav-duse-20034227a"),
    ("Instagram", "pranav_duse"),
    ("GitHub", USER),
]
# ─────────────────────────────────────────────────────────────────────────────

FONT = "'JetBrains Mono','Fira Code','SF Mono',Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"
W, H = 1000, 700
CW_A, LH_A = 6.0, 11.0          # ASCII cell size
FS, CW = 14, 8.4                # info font size / char width
KEY_X, VAL_X = 492, 604         # info columns
KEY2_X, VAL2_X = 744, 836
RIGHT = 962
ROW = 23


# ───────────────────────────── GitHub stats ─────────────────────────────
def _get(url, data=None):
    headers = {"User-Agent": "profile-card", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch_stats():
    s = {k: "—" for k in ("repos", "stars", "commits", "followers", "contrib", "lang")}
    try:
        u = _get(f"https://api.github.com/users/{USER}")
        s["repos"] = f"{u['public_repos']:,}"
        s["followers"] = f"{u['followers']:,}"
    except Exception as e:  # noqa: BLE001
        print("profile fetch failed:", e)
    try:
        repos, page = [], 1
        while page <= 5:
            chunk = _get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}")
            repos += chunk
            if len(chunk) < 100:
                break
            page += 1
        s["stars"] = f"{sum(r['stargazers_count'] for r in repos):,}"
        langs = Counter(r["language"] for r in repos if r.get("language") and not r.get("fork"))
        if langs:
            s["lang"] = langs.most_common(1)[0][0]
    except Exception as e:  # noqa: BLE001
        print("repo fetch failed:", e)
    try:
        c = _get(f"https://api.github.com/search/commits?q=author:{USER}&per_page=1")
        s["commits"] = f"{c['total_count']:,}"
    except Exception as e:  # noqa: BLE001
        print("commit fetch failed:", e)
    if TOKEN:
        try:
            q = {"query": 'query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{totalContributions}}}}',
                 "variables": {"l": USER}}
            g = _get("https://api.github.com/graphql", data=json.dumps(q).encode())
            n = g["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
            s["contrib"] = f"{n:,}"
        except Exception as e:  # noqa: BLE001
            print("graphql fetch failed:", e)
    return s


# ───────────────────────────── SVG helpers ─────────────────────────────
def text(x, y, s, fill, weight=400, anchor="start", size=FS, cw=CW, fit=True, extra=""):
    n = len(s)
    tl = f' textLength="{n * cw:.1f}" lengthAdjust="spacing"' if fit and n > 1 and anchor == "start" else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-weight="{weight}" font-size="{size}" '
            f'text-anchor="{anchor}"{tl}{extra}>{escape(s)}</text>')


def leader(x1, x2, y):
    if x2 - x1 < 12:
        return ""
    return (f'<line x1="{x1 + 6:.1f}" y1="{y - 4:.1f}" x2="{x2 - 6:.1f}" y2="{y - 4:.1f}" stroke="#1f5272" '
            f'stroke-width="1.4" stroke-dasharray="1 5.5" stroke-linecap="round"/>')


def ascii_block(lines):
    """Each row is one <text>; characters are grouped into 3 brightness tiers."""
    dim, mid = set(".,:;-"), set("~=+*xo")
    colors = {"d": "#2c7aab", "m": "#43b6f3", "b": "#d9f3ff"}
    out = []
    for i, line in enumerate(lines):
        stripped = line.lstrip(" ")
        if not stripped:
            continue
        lead = len(line) - len(stripped)
        runs, cur, cur_t = [], "", None
        for ch in stripped:
            t = "d" if ch in dim else "m" if ch in mid else "b" if ch != " " else cur_t
            if t != cur_t and cur:
                runs.append((cur_t, cur))
                cur = ""
            cur_t = t or cur_t
            cur += ch
        if cur:
            runs.append((cur_t or "d", cur))
        spans = "".join(f'<tspan fill="{colors[t]}">{escape(r)}</tspan>' for t, r in runs)
        x = 38 + lead * CW_A
        y = 78 + i * LH_A
        out.append(f'<text class="a" style="animation-delay:{i * 0.025:.3f}s" x="{x:.1f}" y="{y:.1f}" '
                   f'font-size="10" xml:space="preserve" textLength="{len(stripped) * CW_A:.1f}" '
                   f'lengthAdjust="spacing">{spans}</text>')
    return "\n".join(out)


def waveform(y_hi, y_lo, x0, period=248):
    """A scrolling digital signal (five periods wide; the animation shifts it by one period)."""
    bits = [1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0]
    step = period / len(bits)
    pts, prev = [], None
    for rep in range(5):
        for k, b in enumerate(bits):
            x = x0 + rep * period + k * step
            y = y_hi if b else y_lo
            if prev is not None and prev != y:
                pts.append(f"L{x:.1f} {prev}")
            pts.append(f"{'M' if not pts else 'L'}{x:.1f} {y}")
            pts.append(f"L{x + step:.1f} {y}")
            prev = y
    return " ".join(pts)


def build(stats):
    ascii_lines = (ROOT / "scripts" / "portrait_ascii.txt").read_text().split("\n")
    rows, y, delay = [], 90, 0.35

    def add(svg):
        nonlocal delay
        rows.append(f'<g class="r" style="animation-delay:{delay:.2f}s">{svg}</g>')
        delay += 0.07

    # header
    add(text(KEY_X, y, HANDLE[0], "#ffffff", 700) + text(KEY_X + len(HANDLE[0]) * CW, y, "@", "#43b6f3", 700)
        + text(KEY_X + (len(HANDLE[0]) + 1) * CW, y, HANDLE[1], "#ffffff", 700)
        + f'<line x1="{KEY_X + (len(HANDLE[0]) + len(HANDLE[1]) + 2) * CW:.1f}" y1="{y - 5}" x2="{RIGHT}" y2="{y - 5}" stroke="#1d4a63" stroke-width="1.4"/>')
    y += ROW

    def kv(k, v):
        nonlocal y
        add(text(KEY_X, y, k, "#4cc3ff", 700) + leader(KEY_X + len(k) * CW, VAL_X, y) + text(VAL_X, y, v, "#d3e9f6"))
        y += ROW

    def sec(title):
        nonlocal y
        y += 10
        add(text(KEY_X, y, title, "#7fd3ff", 700)
            + f'<line x1="{KEY_X + len(title) * CW + 10:.1f}" y1="{y - 5}" x2="{RIGHT}" y2="{y - 5}" stroke="#1d4a63" stroke-width="1.4"/>')
        y += ROW

    def kv2(k1, v1, k2, v2):
        nonlocal y
        add(text(KEY_X, y, k1, "#4cc3ff", 700) + leader(KEY_X + len(k1) * CW, VAL_X, y) + text(VAL_X, y, v1, "#d3e9f6")
            + text(KEY2_X, y, k2, "#4cc3ff", 700) + leader(KEY2_X + len(k2) * CW, VAL2_X, y) + text(VAL2_X, y, v2, "#d3e9f6"))
        y += ROW

    for k, v in INFO:
        kv(k, v)
    sec("Stack")
    for k, v in STACK:
        kv(k, v)
    sec("Contact")
    for k, v in CONTACT:
        kv(k, v)
    sec("GitHub Stats")
    kv2("Repos", stats["repos"], "Stars", stats["stars"])
    kv2("Commits", stats["commits"], "Followers", stats["followers"])
    kv2("Contrib. 1y", stats["contrib"], "Top Lang", stats["lang"])

    prompt_y = H - 56
    wave = waveform(H - 40, H - 20, 36)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="Pranav Duse — VLSI engineer profile card">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#08141f"/><stop offset="1" stop-color="#050b12"/></linearGradient>
  <radialGradient id="glow" cx="0.92" cy="0.02" r="0.75"><stop offset="0" stop-color="#0f8fd0" stop-opacity="0.38"/><stop offset="0.55" stop-color="#0b4f6c" stop-opacity="0.14"/><stop offset="1" stop-color="#0b4f6c" stop-opacity="0"/></radialGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7fd3ff" stop-opacity="0"/><stop offset="1" stop-color="#7fd3ff" stop-opacity="0.35"/></linearGradient>
  <filter id="blur" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <clipPath id="wavebox"><rect x="36" y="{H - 52}" width="{W - 72}" height="40"/></clipPath>
  <clipPath id="asciibox"><rect x="30" y="64" width="440" height="{ROWS_PX}"/></clipPath>
</defs>
<style>
  .r{{animation:fi .55s ease both}}
  .a{{animation:fa .6s ease both}}
  @keyframes fi{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
  @keyframes fa{{from{{opacity:0}}to{{opacity:1}}}}
  .scan{{animation:sc 5.5s linear 1.4s infinite}}
  @keyframes sc{{0%{{transform:translateY(0);opacity:0}}8%{{opacity:1}}92%{{opacity:1}}100%{{transform:translateY({ROWS_PX - 18}px);opacity:0}}}}
  .cur{{animation:bl 1.1s steps(1) infinite}}
  @keyframes bl{{50%{{opacity:0}}}}
  .wave{{animation:wv 7s linear infinite}}
  @keyframes wv{{to{{transform:translateX(-248px)}}}}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>
  <rect width="{W}" height="42" fill="#0a1a27"/>
  <line x1="0" y1="42" x2="{W}" y2="42" stroke="#12354a" stroke-width="1.5"/>
  <circle cx="26" cy="21" r="6" fill="#1aa7ec"/><circle cx="46" cy="21" r="6" fill="#7fd3ff"/><circle cx="66" cy="21" r="6" fill="#c9e6f5"/>
  <text x="{W / 2}" y="26" text-anchor="middle" font-size="13" fill="#6b8fa6">pranav@duse — ~/profile</text>

  <g clip-path="url(#asciibox)">
{ascii_block(ascii_lines)}
    <rect class="scan" x="30" y="64" width="440" height="18" fill="url(#scan)" opacity="0"/>
  </g>

  <line x1="{KEY_X - 16}" y1="64" x2="{KEY_X - 16}" y2="{H - 58}" stroke="#12354a" stroke-width="1.2"/>
{chr(10).join(rows)}

  {text(KEY_X, prompt_y, "$", "#43b6f3", 700)}
  <rect class="cur" x="{KEY_X + 16}" y="{prompt_y - 12}" width="9" height="15" fill="#7fd3ff"/>

  <g clip-path="url(#wavebox)">
    <path class="wave" d="{wave}" fill="none" stroke="#43b6f3" stroke-width="5" opacity="0.55" filter="url(#blur)"/>
    <path class="wave" d="{wave}" fill="none" stroke="#bfeaff" stroke-width="1.8" stroke-linejoin="round"/>
  </g>
</g>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="17.5" fill="none" stroke="#12354a" stroke-width="1.5"/>
</svg>
'''


ROWS_PX = 0  # set in main()


def main():
    global ROWS_PX
    n = len((ROOT / "scripts" / "portrait_ascii.txt").read_text().rstrip("\n").split("\n"))
    ROWS_PX = int(n * LH_A + 8)
    svg = build(fetch_stats())
    out = ROOT / "assets" / "profile-card.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print("wrote", out, f"({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
