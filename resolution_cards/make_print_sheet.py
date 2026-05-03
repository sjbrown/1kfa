#!/usr/bin/env python3
"""
make_print_sheet.py
===================
Arranges up to 9 card SVG files in a 3×3 grid on a single 8.5×11in SVG
suitable for printing on standard letter paper.

Usage:
    python3 make_print_sheet.py <card_dir> <output_file> [--start N] [--guides]

Arguments:
    card_dir      Directory containing card SVG files (from process_gm_cards.py)
    output_file   Path for the output sheet SVG

Options:
    --start N     Start from the Nth card (1-indexed). Default: 1.
                  Use to generate multiple sheets from a large deck:
                    sheet 1: --start 1   (cards 1-9)
                    sheet 2: --start 10  (cards 10-18)
    --guides      Draw cut guides (hairline crosshairs at card corners).
                  Off by default — use for cutting accuracy.
    --fill        If fewer than 9 cards are available, repeat from the
                  beginning to fill the sheet. Default: leave cells empty.

Examples:
    # Single sheet, first 9 cards
    python3 make_print_sheet.py ~/Desktop/gm-cards sheet_1.svg

    # Second sheet, cards 10-18, with cut guides
    python3 make_print_sheet.py ~/Desktop/gm-cards sheet_2.svg --start 10 --guides

    # Generate all sheets automatically
    python3 make_print_sheet.py ~/Desktop/gm-cards sheet_1.svg --start 1
    python3 make_print_sheet.py ~/Desktop/gm-cards sheet_2.svg --start 10

Dependencies: Python 3.8+ standard library only.
"""

import argparse
import math
import os
import re
import sys


# ---------------------------------------------------------------------------
# Page and grid constants
# ---------------------------------------------------------------------------

# Sheet: 8.5 × 11 in at 300 DPI
SHEET_W = 2550   # px
SHEET_H = 3300   # px

# Card size (must match process_gm_cards.py output)
CARD_W = 750
CARD_H = 1050

# Grid
COLS = 3
ROWS = 3
CARDS_PER_SHEET = COLS * ROWS

# Margins: center the 3×3 grid on the sheet
GRID_W = COLS * CARD_W   # 2250
GRID_H = ROWS * CARD_H   # 3150

MARGIN_X = (SHEET_W - GRID_W) // 2   # 150  (0.5in each side)
MARGIN_Y = (SHEET_H - GRID_H) // 2   # 75   (0.25in each side)

# Cut guide size (extends beyond card corner)
GUIDE_LEN = 30    # px
GUIDE_GAP = 10    # gap between card edge and guide start
GUIDE_COLOR = "#CCCCCC"
GUIDE_WIDTH = 1   # hairline


# ---------------------------------------------------------------------------
# SVG content extraction
# ---------------------------------------------------------------------------

def extract_svg_inner(filepath):
    """
    Reads a card SVG file and returns:
        (viewBox, inner_content)

    inner_content is everything between <svg ...> and </svg>, with
    Inkscape/sodipodi namespace elements stripped so they don't pollute
    the sheet SVG's namespace.

    We inline each card as a <g transform="..."> block rather than using
    <symbol>/<use> because some SVG renderers don't correctly inherit
    font and clip-path attributes across symbol boundaries.
    """
    with open(filepath, encoding='utf-8') as f:
        raw = f.read()

    # Extract viewBox (should always be "0 0 750 1050")
    vb_match = re.search(r'viewBox=["\']([^"\']+)["\']', raw)
    viewbox = vb_match.group(1) if vb_match else f"0 0 {CARD_W} {CARD_H}"

    # Strip the outer <svg ...> and </svg> tags
    inner = re.sub(r'<svg\b[^>]*>', '', raw, count=1)
    inner = re.sub(r'</svg\s*>\s*$', '', inner.strip())

    # Strip sodipodi:namedview blocks entirely
    inner = re.sub(
        r'<sodipodi:namedview\b[^/]*/>', '', inner, flags=re.DOTALL
    )
    inner = re.sub(
        r'<sodipodi:namedview\b.*?</sodipodi:namedview>', '', inner, flags=re.DOTALL
    )

    # Strip defs blocks — we'll collect and deduplicate clip-paths separately
    defs_blocks = re.findall(r'<defs\b[^>]*>(.*?)</defs>', inner, re.DOTALL)
    inner = re.sub(r'<defs\b[^>]*>.*?</defs>', '', inner, flags=re.DOTALL)

    defs_content = '\n'.join(defs_blocks)

    return viewbox, defs_content.strip(), inner.strip()


def make_unique(content, card_index):
    """
    Rewrites id= and url(#...) references in a card's SVG content so that
    IDs are unique across the sheet. Appends _cN to every id.
    """
    suffix = f'_c{card_index}'

    # Rewrite id="foo" → id="foo_cN"
    content = re.sub(
        r'\bid="([^"]+)"',
        lambda m: f'id="{m.group(1)}{suffix}"',
        content
    )

    # Rewrite url(#foo) → url(#foo_cN)
    content = re.sub(
        r'url\(#([^)]+)\)',
        lambda m: f'url(#{m.group(1)}{suffix})',
        content
    )

    # Rewrite xlink:href="#foo" → xlink:href="#foo_cN" (for older SVG)
    content = re.sub(
        r'href="#([^"]+)"',
        lambda m: f'href="#{m.group(1)}{suffix}"',
        content
    )

    return content


# ---------------------------------------------------------------------------
# Cut guides
# ---------------------------------------------------------------------------

def cut_guides_for_cell(col, row):
    """
    Returns SVG path data for hairline cut guides at the four corners
    of a card cell. Each corner gets an L-shaped crosshair outside the
    card boundary.
    """
    x = MARGIN_X + col * CARD_W
    y = MARGIN_Y + row * CARD_H
    x2 = x + CARD_W
    y2 = y + CARD_H

    lines = []
    for (cx, cy, dx, dy) in [
        (x,  y,  -1, -1),   # top-left
        (x2, y,   1, -1),   # top-right
        (x,  y2, -1,  1),   # bottom-left
        (x2, y2,  1,  1),   # bottom-right
    ]:
        # Horizontal arm
        hx1 = cx + dx * GUIDE_GAP
        hx2 = cx + dx * (GUIDE_GAP + GUIDE_LEN)
        lines.append(
            f'<line x1="{hx1}" y1="{cy}" x2="{hx2}" y2="{cy}" '
            f'stroke="{GUIDE_COLOR}" stroke-width="{GUIDE_WIDTH}"/>'
        )
        # Vertical arm
        vy1 = cy + dy * GUIDE_GAP
        vy2 = cy + dy * (GUIDE_GAP + GUIDE_LEN)
        lines.append(
            f'<line x1="{cx}" y1="{vy1}" x2="{cx}" y2="{vy2}" '
            f'stroke="{GUIDE_COLOR}" stroke-width="{GUIDE_WIDTH}"/>'
        )

    return '\n  '.join(lines)


# ---------------------------------------------------------------------------
# Sheet assembly
# ---------------------------------------------------------------------------

def build_sheet(card_files, output_path, draw_guides=False):
    """
    Embeds up to 9 card SVGs into a single sheet SVG.
    card_files: list of file paths, len 1–9.
    """
    all_defs = []
    cells = []

    for i, filepath in enumerate(card_files):
        col = i % COLS
        row = i // COLS
        tx  = MARGIN_X + col * CARD_W
        ty  = MARGIN_Y + row * CARD_H

        viewbox, defs, inner = extract_svg_inner(filepath)
        defs  = make_unique(defs,  i)
        inner = make_unique(inner, i)

        if defs.strip():
            all_defs.append(defs)

        # Scale card to fit cell if viewBox differs from expected
        vb_parts = viewbox.split()
        if len(vb_parts) == 4:
            vb_w, vb_h = float(vb_parts[2]), float(vb_parts[3])
            sx = CARD_W / vb_w
            sy = CARD_H / vb_h
            scale = f' scale({sx:.6f},{sy:.6f})' if (sx != 1.0 or sy != 1.0) else ''
        else:
            scale = ''

        cell = (
            f'  <!-- Card {i+1}: {os.path.basename(filepath)} -->\n'
            f'  <g transform="translate({tx},{ty}){scale}">\n'
            + '\n'.join(f'    {ln}' for ln in inner.splitlines())
            + '\n  </g>'
        )
        cells.append(cell)

        if draw_guides:
            cells.append(f'  <!-- Cut guides: cell {i+1} -->')
            cells.append('  ' + cut_guides_for_cell(col, row))

    defs_block = ''
    if all_defs:
        defs_block = '  <defs>\n'
        for d in all_defs:
            for ln in d.splitlines():
                defs_block += f'    {ln}\n'
        defs_block += '  </defs>\n'

    svg = f'''<svg
   viewBox="0 0 {SHEET_W} {SHEET_H}"
   width="8.5in"
   height="11in"
   version="1.1"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <sodipodi:namedview
     id="namedview_sheet"
     pagecolor="#ffffff"
     inkscape:document-units="in"
     showgrid="false" />
  <!-- Sheet: {COLS}x{ROWS} grid, {CARD_W}x{CARD_H}px cards -->
  <!-- Margin X: {MARGIN_X}px ({MARGIN_X/300:.3f}in)  Margin Y: {MARGIN_Y}px ({MARGIN_Y/300:.3f}in) -->
  <rect x="0" y="0" width="{SHEET_W}" height="{SHEET_H}" fill="white"/>
{defs_block}
{chr(10).join(cells)}
</svg>
'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)

    print(f"wrote {output_path}  ({len(card_files)} cards)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Arrange card SVGs in a 3×3 print sheet (8.5×11in)"
    )
    parser.add_argument(
        'card_dir',
        help='Directory of card SVG files produced by process_gm_cards.py'
    )
    parser.add_argument(
        'output_file',
        help='Output SVG path (e.g. sheet_1.svg)'
    )
    parser.add_argument(
        '--start', type=int, default=1, metavar='N',
        help='Start from the Nth card (1-indexed). Default: 1.'
    )
    parser.add_argument(
        '--guides', action='store_true',
        help='Draw hairline cut guides at card corners.'
    )
    parser.add_argument(
        '--fill', action='store_true',
        help='Repeat cards from the beginning to fill a partial sheet.'
    )
    args = parser.parse_args()

    card_dir = os.path.expanduser(args.card_dir)
    if not os.path.isdir(card_dir):
        sys.exit(f"ERROR: Not a directory: {card_dir}")

    # Collect and sort card SVGs
    all_cards = sorted(
        f for f in os.listdir(card_dir)
        if f.endswith('.svg') and not f.startswith('sheet_')
    )
    if not all_cards:
        sys.exit(f"ERROR: No SVG files found in {card_dir}")

    # Apply --start offset (convert to 0-indexed)
    start = args.start - 1
    if start >= len(all_cards):
        sys.exit(
            f"ERROR: --start {args.start} exceeds available cards ({len(all_cards)})"
        )

    page_cards = all_cards[start : start + CARDS_PER_SHEET]

    if args.fill and len(page_cards) < CARDS_PER_SHEET:
        # Pad by cycling from the beginning of all_cards
        needed = CARDS_PER_SHEET - len(page_cards)
        page_cards = page_cards + (all_cards * math.ceil(needed / len(all_cards)))[:needed]

    card_paths = [os.path.join(card_dir, f) for f in page_cards]

    output_path = os.path.expanduser(args.output_file)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    build_sheet(card_paths, output_path, draw_guides=args.guides)

    # Report if more sheets are needed
    remaining = len(all_cards) - start - len(page_cards)
    if remaining > 0:
        next_start = args.start + len(page_cards)
        print(
            f"{remaining} cards remain. "
            f"Run again with --start {next_start} for the next sheet."
        )
    else:
        print("All cards fit on this sheet.")


if __name__ == '__main__':
    main()
