"""Builds assets/project-1..4.svg and assets/highlights.svg in the same style as the profile card.

Run:  python scripts/build_project_cards.py
Edit the PROJECTS / HIGHLIGHTS lists below, then run it again.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
FONT = "'JetBrains Mono','Fira Code','SF Mono',Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"

# title, tags, three bullets (keep each under ~46 characters), status chips: (label, solid?)
PROJECTS = [
    ("5-Stage RISC-V CPU",
     ["Verilog", "Vivado", "FPGA"],
     ["Runs real RV32I instructions on an FPGA",
      "Forwarding, stall and flush handle hazards",
      "Written in Verilog, simulated in Vivado"],
     [("IN PROGRESS", False)]),
    ("UART IP Core + FIFO",
     ["Verilog-2001", "Testbench", "UVM"],
     ["5 synthesizable RTL modules",
      "Self-checking loopback testbench",
      "Found and fixed a real FIFO bug"],
     [("RTL DONE", True), ("UVM IN PROGRESS", False)]),
    ("Spider-Inspired Quadruped Robot",
     ["ESP32-CAM", "ROS 2", "Isaac Sim"],
     ["12 synced servos, live video, custom dashboard",
      "Walking explored in simulation",
      "Disaster-response team project"],
     [("3RD PLACE · CIRCUITVISTA 2K26", True)]),
    ("Freelance PCB Design",
     ["KiCad", "Gerber", "BOM"],
     ["Boards for paid clients, built in KiCad",
      "ERC/DRC checked before delivery",
      "Schematic to Gerbers and parts list"],
     [("CLIENT WORK DELIVERED", True)]),
]

# big text, small text, label
HIGHLIGHTS = [
    ("3rd", "of 200+ teams", "CircuitVista 2K26"),
    ("Top 10", "teams, research paper challenge", "IEEE Innovate & Investigate · 2025"),
    ("VHDL", "Design of Digital Circuits", "L&T EduTech course"),
]

DEFS = '''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#08141f"/><stop offset="1" stop-color="#050b12"/></linearGradient>
  <radialGradient id="glow" cx="1" cy="0" r="0.9"><stop offset="0" stop-color="#0f8fd0" stop-opacity="0.34"/><stop offset="0.6" stop-color="#0b4f6c" stop-opacity="0.10"/><stop offset="1" stop-color="#0b4f6c" stop-opacity="0"/></radialGradient>
  <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7fd3ff"/><stop offset="1" stop-color="#0b6fa8"/></linearGradient>
</defs>
<style>.c{animation:fi .6s ease both}@keyframes fi{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style>'''


def t(x, y, s, fill, size, weight=400, anchor="start", cw_ratio=0.6, fit=False, extra=""):
    tl = f' textLength="{len(s) * size * cw_ratio:.1f}" lengthAdjust="spacing"' if fit and len(s) > 1 else ""
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{tl}{extra}>{escape(s)}</text>')


def chip(x, y, label, solid):
    w = len(label) * 6.9 + 28
    if solid:
        box = f'<rect x="{x}" y="{y}" width="{w:.1f}" height="24" rx="12" fill="#1aa7ec"/>'
        txt = t(x + 14, y + 16, label, "#04131c", 11.5, 700, fit=True)
    else:
        box = (f'<rect x="{x}" y="{y}" width="{w:.1f}" height="24" rx="12" fill="#0a1d2b" stroke="#43b6f3" '
               f'stroke-width="1.4" stroke-dasharray="4 3"/>')
        txt = t(x + 14, y + 16, label, "#7fd3ff", 11.5, 700, fit=True)
    return box + txt, w


def project_card(i, title, tags, bullets, chips):
    W, H = 460, 252
    parts = [f'<rect width="{W}" height="{H}" rx="16" fill="url(#bg)"/>', f'<rect width="{W}" height="{H}" rx="16" fill="url(#glow)"/>']
    parts.append(t(28, 56, f"0{i}", "#1d5a7d", 30, 700))
    parts.append(t(80, 52, title, "#eaf7ff", 19 if len(title) < 26 else 16.5, 700))
    x = 30
    for tag in tags:
        w = len(tag) * 6.6 + 20
        parts.append(f'<rect x="{x}" y="78" width="{w:.1f}" height="22" rx="11" fill="#0d2a3d" stroke="#1a5878" stroke-width="1"/>')
        parts.append(t(x + 10, 93, tag, "#7fd3ff", 11, 400, fit=True))
        x += w + 8
    for k, b in enumerate(bullets):
        y = 134 + k * 26
        parts.append(f'<rect x="30" y="{y - 9}" width="6" height="6" rx="1.5" fill="#1aa7ec"/>')
        parts.append(t(46, y, b, "#b7d9ea", 13.5))
    x = 30
    for label, solid in chips:
        svg, w = chip(x, 212, label, solid)
        parts.append(svg)
        x += w + 8
    parts.append(f'<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="15.5" fill="none" stroke="#12354a" stroke-width="1.5"/>')
    body = "\n".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" '
            f'aria-label="{escape(title)}">\n{DEFS}\n<g class="c">\n{body}\n</g>\n</svg>\n')


def highlights():
    W, H, cw, gap = 1000, 150, 320, 20
    parts = []
    for i, (big, small, label) in enumerate(HIGHLIGHTS):
        x = i * (cw + gap)
        parts.append(f'<g transform="translate({x},0)"><rect width="{cw}" height="{H - 4}" rx="16" fill="url(#bg)"/>'
                     f'<rect width="{cw}" height="{H - 4}" rx="16" fill="url(#glow)"/>'
                     f'<rect x="0" y="26" width="5" height="{H - 56}" rx="2.5" fill="url(#bar)"/>'
                     + t(30, 70, big, "#7fd3ff", 44, 700)
                     + t(30, 100, small, "#d3e9f6", 14)
                     + t(30, 124, label, "#6b8fa6", 12.5)
                     + f'<rect x="0.75" y="0.75" width="{cw - 1.5}" height="{H - 5.5}" rx="15.5" fill="none" stroke="#12354a" stroke-width="1.5"/></g>')
    body = "\n".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" '
            f'aria-label="Highlights">\n{DEFS}\n<g class="c">\n{body}\n</g>\n</svg>\n')


def main():
    OUT.mkdir(exist_ok=True)
    for i, p in enumerate(PROJECTS, 1):
        (OUT / f"project-{i}.svg").write_text(project_card(i, *p), encoding="utf-8")
    (OUT / "highlights.svg").write_text(highlights(), encoding="utf-8")
    print("wrote", len(PROJECTS), "project cards and highlights.svg")


if __name__ == "__main__":
    main()
