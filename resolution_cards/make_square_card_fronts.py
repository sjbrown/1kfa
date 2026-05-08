#!/usr/bin/env python3
"""
make_square_card_fronts.py

Lays out square card face PNGs onto 8.5×11in SVG print sheets.

PNG dimensions:  825 × 825 px (no border)
Card slot:       750 × 750 px  (2.5 × 2.5 in @ 300 dpi)
Sheet:           2550 × 3300 px (8.5 × 11 in @ 300 dpi)
Grid:            3 × 4 per sheet
"""

import os
import glob
import math
import argparse

# --- Card slot at 300 dpi ---
CARD_W = 750
CARD_H = 750

# --- Sheet at 300 dpi ---
SHEET_W = 2550  # 8.5 in
SHEET_H = 3300  # 11 in

COLS = 3
ROWS = 4
CARDS_PER_SHEET = COLS * ROWS

# Margins: centre the 3×4 grid on the sheet
TOTAL_CARD_W = COLS * CARD_W   # 2250
TOTAL_CARD_H = ROWS * CARD_H   # 3000
MARGIN_X = (SHEET_W - TOTAL_CARD_W) // 2  # 150
MARGIN_Y = (SHEET_H - TOTAL_CARD_H) // 2  # 150


def card_image_element(png_path: str, x: int, y: int) -> str:
    abs_path = os.path.abspath(png_path)
    return f"""  <image
    x="{x}" y="{y}"
    width="{CARD_W}" height="{CARD_H}"
    xlink:href="{abs_path}"
    preserveAspectRatio="none" />"""


def make_sheet(stub: str, card_paths: list, sheet_index: int, output_dir: str):
    elements = []
    for slot, png_path in enumerate(card_paths):
        col = slot % COLS
        row = slot // COLS
        x = MARGIN_X + col * CARD_W
        y = MARGIN_Y + row * CARD_H
        elements.append(card_image_element(png_path, x, y))

    cut_lines = []
    for i in range(COLS + 1):
        cx = MARGIN_X + i * CARD_W
        cut_lines.append(f'  <rect width="2" height="{SHEET_H}" fill="black" x="{cx}"/>')
    for i in range(ROWS + 1):
        cy = MARGIN_Y + i * CARD_H
        cut_lines.append(f'  <rect width="{SHEET_W}" height="2" fill="black" y="{cy}"/>')

    cut_lines_str = "\n".join(cut_lines)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{SHEET_W}" height="{SHEET_H}"
     viewBox="0 0 {SHEET_W} {SHEET_H}">
  <rect width="{SHEET_W}" height="{SHEET_H}" fill="white" />
{''.join(elements)}
  <g id="cuts">
{cut_lines_str}
  </g>
</svg>"""

    out_path = os.path.join(output_dir, f"{stub}_sheet{sheet_index:02d}.svg")
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"  wrote {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Lay out square card face PNGs on print sheets.")
    parser.add_argument(
        "--input-dir",
        default="/tmp/cards_square",
        help="Directory containing deck_*_card_face*.png files",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/cards_square",
        help="Output directory for sheet SVGs",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    pngs = sorted(glob.glob(os.path.join(args.input_dir, "deck_*_card_face*.png")))
    if not pngs:
        print(f"No deck_*_card_face*.png files found in {args.input_dir}")
        return

    print(f"Found {len(pngs)} card face PNGs.")
    num_sheets = math.ceil(len(pngs) / CARDS_PER_SHEET)
    print(f"Generating {num_sheets} sheet(s)...")

    for sheet_idx in range(num_sheets):
        batch = pngs[sheet_idx * CARDS_PER_SHEET : (sheet_idx + 1) * CARDS_PER_SHEET]
        stub = os.path.basename(args.input_dir.rstrip('/'))
        make_sheet(stub, batch, sheet_idx + 1, args.output_dir)

    print("Done.")


if __name__ == "__main__":
    main()
