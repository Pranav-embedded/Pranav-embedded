"""Turn a portrait into ASCII art for the profile card.

Usage:  python scripts/make_ascii.py path/to/photo.png
Needs:  pip install Pillow numpy opencv-python-headless
Output: scripts/portrait_ascii.txt  (one line of text per row)

Tip: tweak CROP, COLS/ROWS, GAMMA and FLOOR below until the face looks right.
"""
import sys
import cv2
import numpy as np
from PIL import Image

COLS, ROWS = 70, 48                       # ASCII size (a character cell is ~6px wide, ~11px tall)
CROP = (400, 120, 920, 800)               # left, top, right, bottom of the face area in the source photo
GAMMA = 0.75                              # lower = brighter
FLOOR = 0.05                              # anything darker than this stays blank
RAMP = " .,:;-~=+*xoO#%@"                 # dark -> light

def main(path):
    im = Image.open(path).convert("RGB").crop(CROP)
    rgb = np.asarray(im)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32) / 255
    sat = hsv[..., 1]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    # Local contrast so shadows, hair and facial features show up in a low-key photo.
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(6, 6)).apply(gray).astype(np.float32) / 255
    # The photo's background is saturated blue, the subject is grey: saturation hides the background.
    gray *= 1 - np.clip((sat - 0.25) / 0.25, 0, 1)
    small = cv2.resize(gray, (COLS, ROWS), interpolation=cv2.INTER_AREA)
    small = np.clip((small - FLOOR) / (1 - FLOOR), 0, 1) ** GAMMA
    rows = ["".join(RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))] for v in r).rstrip() for r in small]
    open("scripts/portrait_ascii.txt", "w").write("\n".join(rows) + "\n")
    print("\n".join(rows))

if __name__ == "__main__":
    main(sys.argv[1])
