#!/usr/bin/env python3
"""
make_move_card_backs.py
=======================
Generates printable 8.5x11in SVG sheets of character move card backs.
Each card back shows the move name (large) and the traits it uses (bold, bottom).
Cards are arranged 3x3 per sheet. Output files are written to ./output/.

Usage:
    python3 make_move_card_backs.py <character_move_sheet.md> [--output-dir DIR]

Requires parse_character_moves.py alongside this script (or on PYTHONPATH).
"""

import sys
import os
import argparse
from math import ceil

# ---------------------------------------------------------------------------
# Card dimensions (2.5 x 3.5 in at 96 dpi, matching the existing pipeline)
CARD_W = 240
CARD_H = 336

# Page dimensions: 8.5 x 11 in at 96 dpi
PAGE_W = 816
PAGE_H = 1056

COLS = 3
ROWS = 3
CARDS_PER_PAGE = COLS * ROWS

MARGIN_X = (PAGE_W - COLS * CARD_W) / 2
MARGIN_Y = (PAGE_H - ROWS * CARD_H) / 2

# Card palette
CARD_BG        = "#4a4a4a"
CARD_BORDER    = "#c8a96e"
TRAIT_BG       = "#0f0f1e"
TITLE_COLOR    = "#f0e6d3"
TRAIT_COLOR    = "#c8a96e"
NO_TRAIT_COLOR = "#666688"

CORNER_R = 8

# ---------------------------------------------------------------------------
# Loading

def load_moves(md_path: str) -> list[dict]:
    """
    Load moves via handy_moves(), then sort:
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    from parse_character_moves import handy_moves
    return handy_moves(md_path)


# ---------------------------------------------------------------------------
# SVG generation

TITLE_PADDING = 20
TITLE_MAX_W   = CARD_W - TITLE_PADDING * 2   # 200px

FSIZE_1_LINE = 54
FSIZE_2_LINE = 44
FSIZE_3_LINE = 34


def split_title(name: str) -> list[str]:
    words = name.split()
    if len(words) <= 1:
        return words if words else [name]
    if len(words) == 2:
        return words
    mid = (len(words) + 1) // 2
    return [" ".join(words[:mid]), " ".join(words[mid:])]


def card_svg(move: dict, x: float, y: float) -> str:

    lines = split_title(move.title)
    n = len(lines)
    fsize  = FSIZE_1_LINE if n == 1 else (FSIZE_2_LINE if n == 2 else FSIZE_3_LINE)
    line_h = fsize * 1.18

    title_zone_h  = CARD_H * 0.72
    total_text_h  = line_h * n
    title_y_start = (title_zone_h - total_text_h) / 2 + fsize * 0.88

    title_lines_svg = ""
    for i, line in enumerate(lines):
        ty = title_y_start + i * line_h
        length_attrs = (
            f'textLength="{TITLE_MAX_W}" lengthAdjust="spacingAndGlyphs" '
            if len(line) > 5 else ""
        )
        title_lines_svg += (
            f'<text x="{CARD_W / 2:.1f}" y="{ty:.1f}" '
            f'text-anchor="middle" dominant-baseline="auto" '
            f'font-family="OptimusPrinceps, Georgia, \'Times New Roman\', serif" font-style="normal" ' 
            f'style="font-family:OptimusPrinceps;-inkscape-font-specification:\'OptimusPrinceps Medium\';" '
            f'font-size="{fsize}" font-weight="bold" '
            f'fill="{TITLE_COLOR}" '
            f'{length_attrs}>'
            f'{_xml(line)}</text>\n'
        )
    footer_h = CARD_H * 0.22
    footer_y = CARD_H - footer_h

    if move.attrs:
        trait_str   = "  \u00b7  ".join(move.attrs)
        trait_color = TRAIT_COLOR
        trait_fsize = 22
    else:
        trait_str   = "no flip"
        trait_color = NO_TRAIT_COLOR
        trait_fsize = 16

    trait_cy = footer_y + footer_h / 2 + trait_fsize * 0.35
    sep_y    = footer_y + 1

    groups = move.get('groups') or []
    group_tag_svg = ""
    if groups:
        tag_fsize = 9
        tag_label = "  ·  ".join(g.upper() for g in groups)
        tag_pad_x = 6
        tag_pad_y = 3
        tag_h = tag_fsize + tag_pad_y * 2
        tag_w = len(tag_label) * tag_fsize * 0.6 + tag_pad_x * 2
        tag_x = CARD_W - tag_w - 4
        tag_y = CARD_H - tag_h - 4
        group_tag_svg = (
            f'<rect x="{tag_x:.1f}" y="{tag_y:.1f}" '
            f'width="{tag_w:.1f}" height="{tag_h:.1f}" '
            f'rx="3" ry="3" fill="{TRAIT_BG}" opacity="0.9"/>'
            f'<text x="{tag_x + tag_pad_x:.1f}" y="{tag_y + tag_pad_y + tag_fsize * 0.85:.1f}" '
            f'font-family="\'Gill Sans\', \'Trebuchet MS\', Arial, sans-serif" '
            f'font-size="{tag_fsize}" font-weight="bold" letter-spacing="1" '
            f'fill="{TRAIT_COLOR}" opacity="0.7">{_xml(tag_label)}</text>'
        )

    return f"""\
<g transform="translate({x:.2f},{y:.2f})">
  <rect x="0" y="0" width="{CARD_W}" height="{CARD_H}"
        rx="{CORNER_R}" ry="{CORNER_R}"
        fill="{CARD_BG}" stroke="{CARD_BORDER}" stroke-width="2.5"/>
  <rect x="6" y="6" width="{CARD_W-12}" height="{CARD_H-12}"
        rx="{CORNER_R-2}" ry="{CORNER_R-2}"
        fill="none" stroke="{CARD_BORDER}" stroke-width="0.8" opacity="0.4"/>
  {title_lines_svg}
  <rect x="0" y="{footer_y:.1f}" width="{CARD_W}" height="{footer_h:.1f}"
        fill="{TRAIT_BG}" opacity="0.85"/>
  <rect x="0" y="{footer_y:.1f}" width="{CARD_W}" height="{footer_h:.1f}"
        fill="none" stroke="{CARD_BORDER}" stroke-width="0.5" opacity="0.5"/>
  <line x1="16" y1="{sep_y:.1f}" x2="{CARD_W-16}" y2="{sep_y:.1f}"
        stroke="{CARD_BORDER}" stroke-width="0.8" opacity="0.6"/>
  <text x="{CARD_W/2:.1f}" y="{trait_cy:.1f}"
        text-anchor="middle" dominant-baseline="auto"
        font-family="'Gill Sans', 'Trebuchet MS', Arial, sans-serif"
        font-size="{trait_fsize}" font-weight="bold"
        letter-spacing="3"
        fill="{trait_color}">{_xml(trait_str)}</text>
  {group_tag_svg}
</g>
"""


def _xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sheet_svg(cards_on_page: list, page_num: int, total_pages: int) -> str:
    # cards_on_page may contain None for blank slots between component groups
    cards_svg = ""
    for i, move in enumerate(cards_on_page):
        if move is None:
            continue
        col = i % COLS
        row = i // COLS
        x = MARGIN_X + col * CARD_W
        y = MARGIN_Y + row * CARD_H
        cards_svg += card_svg(move, x, y)

    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{PAGE_W}" height="{PAGE_H}"
     viewBox="0 0 {PAGE_W} {PAGE_H}">
  <!-- 1kFA Character Move Card Backs : sheet {page_num}/{total_pages} -->
  <rect width="{PAGE_W}" height="{PAGE_H}" fill="#f8f4ef"/>
  {cards_svg}
</svg>
"""


# ---------------------------------------------------------------------------
# Main

def main():
    parser = argparse.ArgumentParser(
        description="Generate printable character move card back sheets (3x3 SVG)."
    )
    parser.add_argument(
        "move_sheet",
        default='./character_move_sheet.md',
        help="Path to character_move_sheet.md",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default='/tmp/1kfa_move_card_backs/',
        help="Directory to write SVG files into (defaults to /tmp)",
    )
    parser.add_argument(
        "--export-pdfs",
        action="store_true",
        help="After writing SVGs, run Inkscape to export each as a PDF.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.move_sheet):
        sys.exit(f"ERROR: Move sheet not found: {args.move_sheet}")

    os.makedirs(args.output_dir, exist_ok=True)

    moves = load_moves(args.move_sheet)
    if not moves:
        sys.exit("ERROR: No moves parsed from the move sheet.")

    # Pad each component group to a page boundary so groups never share a sheet.
    from itertools import groupby
    padded = []
    for _component, group in groupby(moves, key=lambda m: m["component"]):
        group = list(group)
        remainder = len(group) % CARDS_PER_PAGE
        if remainder:
            group += [None] * (CARDS_PER_PAGE - remainder)
        padded.extend(group)

    total_pages = len(padded) // CARDS_PER_PAGE

    for page_idx in range(total_pages):
        chunk = padded[page_idx * CARDS_PER_PAGE : (page_idx + 1) * CARDS_PER_PAGE]
        svg   = sheet_svg(chunk, page_num=page_idx + 1, total_pages=total_pages)
        fname = f"move_card_backs_sheet_{page_idx+1:02d}.svg"
        fpath = os.path.join(args.output_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(svg)
        real_cards = sum(1 for c in chunk if c is not None)
        print(f"  wrote {fpath}  ({real_cards} cards)")

    print(f"\n{len(moves)} cards across {total_pages} sheet(s) -> {args.output_dir}/")

    if args.export_pdfs:
        import subprocess
        for page_idx in range(total_pages):
            fname = f"move_card_backs_sheet_{page_idx+1:02d}"
            svg_path = os.path.join(args.output_dir, fname + ".svg")
            pdf_path = os.path.join(args.output_dir, fname + ".pdf")
            print(f"  exporting {pdf_path} ...")
            subprocess.run(
                ["inkscape", f"--export-pdf={pdf_path}", svg_path],
                check=True,
            )
        print("PDF export done.")



if __name__ == "__main__":
    main()
