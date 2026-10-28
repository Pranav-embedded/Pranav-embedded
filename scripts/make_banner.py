"""Builds assets/banner.png: dark gradient, name + waveform on the left, portrait fading in on the right.

Usage:  python scripts/make_banner.py path/to/portrait.png
Needs:  pip install Pillow numpy
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 3200, 840                      # drawn at 2x, saved at 1600x420
NAME, TAG = "PRANAV DUSE", "VLSI ENGINEER"
SUB = "RTL Design  /  Verification  /  FPGA  /  Embedded"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def glow(size, center, radius, color, strength):
    yy, xx = np.mgrid[0:size[1], 0:size[0]]
    d = np.sqrt((xx - center[0]) ** 2 + (yy - center[1]) ** 2) / radius
    a = np.clip(1 - d, 0, 1) ** 1.8 * strength
    img = np.zeros((size[1], size[0], 4), np.uint8)
    img[..., :3] = color
    img[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(img, "RGBA")

def main(portrait_path):
    base = Image.new("RGBA", (W, H), (4, 8, 16, 255))
    base = Image.alpha_composite(base, glow((W, H), (W - 120, -60), 1500, (10, 140, 215), 0.55))
    base = Image.alpha_composite(base, glow((W, H), (1100, H + 200), 1300, (8, 70, 110), 0.30))

    # portrait: crop head + shoulders, scale, fade in from the left
    p = Image.open(portrait_path).convert("RGB").crop((0, 90, 1168, 1023))
    scale = 0.9
    p = p.resize((int(p.width * scale), int(p.height * scale)), Image.LANCZOS)
    x0, y0 = W - p.width, H - p.height
    mask = np.ones((p.height, p.width), np.float32)
    fade = int(p.width * 0.55)
    mask[:, :fade] = np.linspace(0, 1, fade)[None, :] ** 1.6
    mask[: int(p.height * 0.06), :] *= np.linspace(0, 1, int(p.height * 0.06))[:, None]
    pa = p.convert("RGBA")
    pa.putalpha(Image.fromarray((mask * 255).astype(np.uint8)))
    base.alpha_composite(pa, (x0, y0))

    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    bold, mono, monob = ImageFont.truetype(BOLD, 190), ImageFont.truetype(MONO, 54), ImageFont.truetype(MONOB, 50)

    def spaced(x, y, s, font, fill, tracking):
        for ch in s:
            d.text((x, y), ch, font=font, fill=fill)
            x += d.textlength(ch, font=font) + tracking

    x0t = 230
    d.rounded_rectangle((x0t, 205, x0t + 520, 293), radius=44, outline=(120, 220, 255, 230), width=4, fill=(0, 20, 35, 140))
    spaced(x0t + 42, 217, TAG, monob, (150, 230, 255, 255), 6)
    spaced(x0t + 4, 322, NAME, bold, (0, 0, 0, 170), 14)
    spaced(x0t, 316, NAME, bold, (245, 250, 255, 255), 14)
    spaced(x0t, 566, SUB, mono, (170, 215, 240, 255), 3)

    # digital waveform under the text
    pattern = [1,0,1,1,0,0,1,0,1,0,1,1,1,0,0,1,0,1,1,0,1,0,0,1,1,0,1,0,1,1,0,0,1,0,1,1,0,1,0,1,1,0,0,1]
    y_hi, y_lo, step, x, pts, prev = 735, 785, 66, x0t, [], pattern[0]
    for b in pattern:
        if x > 2000:
            break
        yv = y_hi if b else y_lo
        if b != prev:
            pts.append((x, y_hi if prev else y_lo))
        pts.append((x, yv)); x += step; pts.append((x, yv)); prev = b
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).line(pts, fill=(90, 200, 255, 200), width=14, joint="curve")
    g = g.filter(ImageFilter.GaussianBlur(14))
    d.line(pts, fill=(170, 235, 255, 255), width=5, joint="curve")

    out = Image.alpha_composite(Image.alpha_composite(base, g), lay).convert("RGB")
    arr = np.asarray(out).astype(np.float32) + np.random.default_rng(7).normal(0, 1.3, (H, W, 3))   # fine grain, avoids banding
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((1600, 420), Image.LANCZOS).save("assets/banner.png", optimize=True)
    print("wrote assets/banner.png")

if __name__ == "__main__":
    main(sys.argv[1])
