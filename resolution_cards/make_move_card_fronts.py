#!/usr/bin/env python3
"""
make_move_card_fronts.py

Lays out move card face PNGs onto 8.5×11in SVG print sheets.
Each PNG has a thick black border (top:70 right:60 bottom:70 left:60 px)
that is eliminated by zooming the SVG viewport into the interior content.

PNG dimensions:  825 × 1125 px
Border:          top=70, right=60, bottom=70, left=60
Interior:        705 × 985 px

Card slot:       750 × 1050 px  (2.5 × 3.5 in @ 300 dpi)
Sheet:           2550 × 3300 px (8.5 × 11 in @ 300 dpi)
Grid:            3 × 3 per sheet, with margins
"""

import os
import glob
import math
import argparse
import subprocess

# --- PNG geometry ---
PNG_W = 825
PNG_H = 1125
BORDER_TOP    = 70
BORDER_RIGHT  = 60
BORDER_BOTTOM = 70
BORDER_LEFT   = 60
INTERIOR_W = PNG_W - BORDER_LEFT - BORDER_RIGHT  # 705
INTERIOR_H = PNG_H - BORDER_TOP  - BORDER_BOTTOM  # 985

# --- Card slot at 300 dpi ---
CARD_W = 750   # 2.5 in
CARD_H = 1050  # 3.5 in

# --- Sheet at 300 dpi ---
SHEET_W = 2550  # 8.5 in
SHEET_H = 3300  # 11 in

COLS = 3
ROWS = 3
CARDS_PER_SHEET = COLS * ROWS

# Margins: centre the 3×3 grid on the sheet
TOTAL_CARD_W = COLS * CARD_W        # 2250
TOTAL_CARD_H = ROWS * CARD_H        # 3150
MARGIN_X = (SHEET_W - TOTAL_CARD_W) // 2   # 150
MARGIN_Y = (SHEET_H - TOTAL_CARD_H) // 2   # 75


def card_image_element(png_path: str, x: int, y: int) -> str:
    """
    Returns an SVG <image> element that renders the card face, cropped to
    eliminate the black border. The PNG is scaled so that its interior
    fills the card slot exactly, then shifted so the border falls outside
    the clip region.
    """
    # Scale factor: fit interior to card slot
    scale_x = CARD_W / INTERIOR_W
    scale_y = CARD_H / INTERIOR_H

    # Rendered PNG dimensions at this scale
    rendered_w = PNG_W * scale_x
    rendered_h = PNG_H * scale_y

    # Offset: shift the PNG so BORDER_LEFT/TOP land outside (to the left/above) the slot
    offset_x = x - BORDER_LEFT * scale_x
    offset_y = y - BORDER_TOP  * scale_y

    clip_id = f"clip_{os.path.basename(png_path).replace('.', '_')}_x{x}_y{y}"
    abs_path = os.path.abspath(png_path)

    return f"""  <defs>
    <clipPath id="{clip_id}">
      <rect x="{x}" y="{y}" width="{CARD_W}" height="{CARD_H}" />
    </clipPath>
  </defs>
  <image
    x="{offset_x:.4f}" y="{offset_y:.4f}"
    width="{rendered_w:.4f}" height="{rendered_h:.4f}"
    xlink:href="{abs_path}"
    clip-path="url(#{clip_id})"
    preserveAspectRatio="none" />"""


def make_sheet(stub: str, card_paths: list, sheet_index: int, output_dir: str, export_pdf):
    elements = []
    for slot, png_path in enumerate(card_paths):
        col = slot % COLS
        row = slot // COLS
        x = MARGIN_X + col * CARD_W
        y = MARGIN_Y + row * CARD_H
        elements.append(card_image_element(png_path, x, y))

    cut_v1_x = MARGIN_X
    cut_v2_x = MARGIN_X + CARD_W
    cut_v3_x = MARGIN_X + CARD_W*2
    cut_v4_x = MARGIN_X + CARD_W*3
    cut_h1_y = MARGIN_Y
    cut_h2_y = MARGIN_Y + CARD_H
    cut_h3_y = MARGIN_Y + CARD_H*2
    cut_h4_y = MARGIN_Y + CARD_H*3
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{SHEET_W}" height="{SHEET_H}"
     viewBox="0 0 {SHEET_W} {SHEET_H}">
  <rect width="{SHEET_W}" height="{SHEET_H}" fill="white" />
{''.join(elements)}
  <g id="cuts">
  <rect id="cut_v1" width="2" height="{SHEET_H}" fill="black" x="{cut_v1_x}"/>
  <rect id="cut_v2" width="2" height="{SHEET_H}" fill="black" x="{cut_v2_x}"/>
  <rect id="cut_v3" width="2" height="{SHEET_H}" fill="black" x="{cut_v3_x}"/>
  <rect id="cut_v4" width="2" height="{SHEET_H}" fill="black" x="{cut_v4_x}"/>
  <rect id="cut_h1" width="{SHEET_W}" height="2" fill="black" y="{cut_h1_y}"/>
  <rect id="cut_h2" width="{SHEET_W}" height="2" fill="black" y="{cut_h2_y}"/>
  <rect id="cut_h3" width="{SHEET_W}" height="2" fill="black" y="{cut_h3_y}"/>
  <rect id="cut_h4" width="{SHEET_W}" height="2" fill="black" y="{cut_h4_y}"/>
  </g>
</svg>"""

    out_path = os.path.join(output_dir, f"{stub}_sheet{sheet_index:02d}.svg")
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"  wrote {out_path}")

    if export_pdf:
        pdf_path = out_path[:-4] + '.pdf'
        print(f"  exporting {pdf_path} ...")
        subprocess.run(
            ["inkscape", f"--export-pdf={pdf_path}", out_path],
        check=True,
        )
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Lay out move card face PNGs on print sheets.")
    parser.add_argument(
        "--input-dir",
        default="/tmp/cards_v0.95/move_deck",
        help="Directory containing face*.png files",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/cards_v0.95",
        help="Output directory for sheet SVGs",
    )
    parser.add_argument(
        "--export-pdfs",
        action="store_true",
        help="After writing SVGs, run Inkscape to export each as a PDF.",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    pngs = sorted(glob.glob(os.path.join(args.input_dir, "face*.png")))
    if not pngs:
        print(f"No face*.png files found in {args.input_dir}")
        return

    print(f"Found {len(pngs)} card face PNGs.")
    num_sheets = math.ceil(len(pngs) / CARDS_PER_SHEET)
    print(f"Generating {num_sheets} sheet(s)...")

    for sheet_idx in range(num_sheets):
        batch = pngs[sheet_idx * CARDS_PER_SHEET : (sheet_idx + 1) * CARDS_PER_SHEET]
        stub = os.path.basename(args.input_dir)
        make_sheet(stub, batch, sheet_idx + 1, args.output_dir, args.export_pdfs)


    print("Done.")


if __name__ == "__main__":
    main()
