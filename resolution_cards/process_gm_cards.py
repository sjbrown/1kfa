#!/usr/bin/env python3
"""
gm_card_generator.py
====================
Parses mod_guide_gm.md and generates Inkscape-compatible SVG playing cards
(2.5 x 3.5 in, 750x1050 px viewBox) for the GM Move Deck.

Usage:
    python3 gm_card_generator.py <path/to/mod_guide_gm.md> <output_directory>

Example:
    python3 gm_card_generator.py ~/1kfa/mod_guide_gm.md ~/Desktop/gm-cards

The script finds two sections in the guide:
  1. Dramatic Action GM Moves  — ### headings with fenced-code card blocks
  2. Combat GM Move Deck       — ordered list items under "When a combat interlude begins"

It regenerates only files whose source content has changed (based on a hash
stored in a sidecar file), so incremental runs are fast.

Dependencies: Python 3.8+ standard library only. No pip installs needed.
"""

import argparse
import hashlib
import os
import re
import sys
import textwrap


# ---------------------------------------------------------------------------
# Card dimensions and design constants
# ---------------------------------------------------------------------------

W, H = 750, 1050
RADIUS = 24

COLORS = {
    # Accent bar colors — assigned per card title in ACCENT_MAP below
    "damage":   "#C0410E",
    "shadow":   "#3C3489",
    "neutral":  "#5F5E5A",
    "pivot":    "#0F6E56",
    "resource": "#854F0B",
    "fear":     "#533489",
    "rally":    "#1D9E75",
    "chapter":  "#854F0B",
    # Fixed palette
    "offwhite": "#F8F6F1",
    "ink":      "#1A1917",
    "muted":    "#5F5E5A",
    "rule":     "#888780",
    "border":   "#C8C6BE",
    "divider":  "#DDDBD3",
}

# Map card title keywords → accent color key.
# Checked case-insensitively against the start of the title.
ACCENT_MAP = [
    ("escalate",    "damage"),
    ("deal damage", "damage"),
    ("pivot",       "pivot"),
    ("price",       "neutral"),
    ("threat",      "shadow"),
    ("all eyes",    "neutral"),
    ("use up",      "resource"),
    ("separate",    "neutral"),
    # combat
    ("special ability", "damage"),
    ("reinforcement",   "neutral"),
    ("disarm",          "neutral"),
    ("imperiled",       "shadow"),
    ("tactical",        "shadow"),
    ("echo",            "fear"),
    ("glory",           "rally"),
    ("separation",      "chapter"),
    ("revelation",      "chapter"),
    ("reunion",         "chapter"),
]

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS  = "Helvetica Neue, Arial, sans-serif"

# Wrap width in characters for body text and prompts
WRAP_BODY   = 37
WRAP_PROMPT = 36
WRAP_BULLET = 37


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def extract_dramatic_action_cards(text):
    """
    Finds the 'Dramatic Action GM Moves' section and returns a list of
    card dicts parsed from each ### heading + fenced code block.

    Each card dict has keys:
        title       str
        deck_label  str  ("Dramatic Action")
        raw_block   str  (verbatim content of the ``` fence)
        chapter     bool (always False for DA cards)
    """
    # Find the section bounded by "## Dramatic Action GM Moves" and the next ##
    section_match = re.search(
        r'## Dramatic Action GM Moves\b.*?(?=\n## |\Z)',
        text, re.DOTALL
    )
    if not section_match:
        sys.exit("ERROR: Could not find '## Dramatic Action GM Moves' section in the guide.")

    section = section_match.group(0)

    # Split into ### subsections
    subsections = re.split(r'\n(?=### )', section)

    cards = []
    for sub in subsections:
        heading = re.match(r'### (.+)', sub)
        if not heading:
            continue
        title = heading.group(1).strip()

        # Skip meta-sections that aren't actual move cards
        if re.search(r'(GM move is more than|triggering|journey point)', title, re.I):
            continue

        # Extract the fenced code block (the card face)
        fence = re.search(r'```\n(.*?)```', sub, re.DOTALL)
        raw_block = fence.group(1) if fence else ""

        if not raw_block.strip():
            continue

        cards.append({
            "title":      title,
            "deck_label": "Dramatic Action",
            "raw_block":  raw_block,
            "chapter":    False,
        })

    return cards


def extract_combat_cards(text):
    """
    Finds the ordered list under '### When a combat interlude begins' and
    returns one card dict per list item.

    Card face content is synthesised from the list item text because the
    combat deck has no fenced-code card blocks in the source — only the
    list that enumerates the cards.

    Each card dict:
        title       str
        deck_label  str  ("Combat")
        raw_block   str  (synthesised card text, same format as DA blocks)
        chapter     bool
    """
    # Find the numbered list
    section_match = re.search(
        r'### When a combat interlude begins\b(.*?)(?=\n### |\Z)',
        text, re.DOTALL
    )
    if not section_match:
        sys.exit("ERROR: Could not find '### When a combat interlude begins' section.")

    section = section_match.group(0)

    # Collect all ordered list items (possibly multi-line with indented continuation)
    # Pattern: lines starting with " 1. " or "    " continuation
    raw_items = []
    current = None
    for line in section.splitlines():
        ol_match = re.match(r'\s{1,3}1\.\s+(.*)', line)
        continuation = re.match(r'\s{4,}(.*)', line) if current is not None else None
        if ol_match:
            if current is not None:
                raw_items.append(current)
            current = ol_match.group(1).strip()
        elif continuation and current is not None:
            current = current + " " + continuation.group(1).strip()
        else:
            if current is not None:
                raw_items.append(current)
                current = None
    if current is not None:
        raw_items.append(current)

    cards = []
    for item in raw_items:
        chapter = bool(re.match(r'\(only in some chapters\)', item, re.I))
        # Strip the chapter prefix if present
        item_clean = re.sub(r'^\(only in some chapters\)\s*', '', item, flags=re.I).strip()

        # Parse "Title - description" or "Title / description"
        title_body = re.split(r'\s*[-/&]\s*', item_clean, maxsplit=1)
        title = title_body[0].strip()
        body  = title_body[1].strip() if len(title_body) > 1 else ""

        # Normalise title capitalisation
        title = title.strip().rstrip('.')

        # Build a synthetic raw_block in the same style as DA fenced blocks
        raw_block = body if body else title

        cards.append({
            "title":      title,
            "deck_label": "Combat",
            "raw_block":  raw_block,
            "chapter":    chapter,
        })

    return cards


# ---------------------------------------------------------------------------
# Card face content: parse raw_block into structured fields
# ---------------------------------------------------------------------------

def parse_card_block(raw_block, title):
    """
    Parses a raw fenced-code block (or synthesised string for combat cards)
    into structured fields the SVG renderer uses.

    Returns a dict:
        prompt        str or None
        sections      list of section dicts:
                          {"label": str or None, "bullets": [str], "text": str or None}
        rule          str or None   (line(s) ending with "Deck" or "deck" or "reshuffle")
    """
    lines = raw_block.strip().splitlines()

    # --- Identify rule lines (footer) ---
    RULE_PAT = re.compile(
        r'(shuffle|reshuffle|then:|maximum)', re.I
    )

    prompt   = None
    sections = []
    rule_lines = []

    current_label   = None
    current_bullets = []
    current_texts   = []

    def flush_section():
        if current_label or current_bullets or current_texts:
            sections.append({
                "label":   current_label,
                "bullets": list(current_bullets),
                "text":    " ".join(current_texts).strip() or None,
            })

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Bullet item:  " * text"
        if re.match(r'\s*\*\s+', line):
            bullet_text = re.sub(r'\s*\*\s+', '', line).strip()
            current_bullets.append(bullet_text)
            i += 1
            continue

        # Answer / prompt line
        if re.match(r'Answer\s*:', line, re.I):
            # Collect the prompt — may span next line(s) if indented
            prompt_parts = []
            i += 1
            while i < len(lines):
                nxt = lines[i].rstrip()
                if not nxt.strip():
                    break
                if re.match(r'\s{2,}', nxt):
                    prompt_parts.append(nxt.strip())
                    i += 1
                else:
                    break
            if prompt_parts:
                prompt = " ".join(prompt_parts)
            else:
                # Inline prompt on same line: "Answer: foo"
                inline = re.sub(r'Answer\s*:\s*', '', line, flags=re.I).strip()
                if inline:
                    prompt = inline
            continue

        # Rule / footer lines
        if RULE_PAT.search(line):
            rule_lines.append(line.strip())
            i += 1
            continue

        # Section label lines: "Choose:", "Choose one:", "Then:", bare label
        if re.match(r'(Choose|Then|Place|Add|Use|If they|Option)', line.strip(), re.I):
            flush_section()
            current_label   = line.strip().rstrip(':').strip()
            current_bullets = []
            current_texts   = []
            i += 1
            continue

        # Plain text
        flush_section()
        current_label   = None
        current_bullets = []
        current_texts   = [line.strip()]
        i += 1
        # Collect continuation lines
        while i < len(lines):
            nxt = lines[i].rstrip()
            if not nxt.strip() or re.match(r'\s*\*\s+', nxt):
                break
            if re.match(r'(Choose|Then|Place|Add|Use|Answer|If they|Option)', nxt.strip(), re.I):
                break
            if RULE_PAT.search(nxt):
                break
            current_texts.append(nxt.strip())
            i += 1
        flush_section()
        current_label   = None
        current_bullets = []
        current_texts   = []

    flush_section()

    rule = " ".join(rule_lines).strip() or None

    return {
        "prompt":   prompt,
        "sections": sections,
        "rule":     rule,
    }


# ---------------------------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------------------------

def esc(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def wrap(text, width):
    """Word-wrap returning list of strings."""
    return textwrap.wrap(text, width=width) or [""]


def accent_for(title):
    key = title.lower()
    for fragment, color_key in ACCENT_MAP:
        if fragment in key:
            return COLORS[color_key]
    return COLORS["neutral"]


def slug(title):
    return re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')


# ---------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------

def render_svg(card):
    """
    Renders a complete Inkscape-compatible SVG string for one card dict.
    card keys: title, deck_label, raw_block, chapter
    """
    title     = card["title"]
    deck_label = card["deck_label"]
    chapter   = card["chapter"]
    raw_block = card["raw_block"]

    parsed = parse_card_block(raw_block, title)
    prompt   = parsed["prompt"]
    sections = parsed["sections"]
    rule     = parsed["rule"]

    accent = accent_for(title)
    card_id = "svg_" + slug(title)
    docname = slug(title) + ".svg"

    out = []
    a = out.append  # shorthand

    # ── SVG header with Inkscape namespaces ──
    a(f'<svg')
    a(f'   viewBox="0 0 {W} {H}"')
    a(f'   width="2.5in"')
    a(f'   height="3.5in"')
    a(f'   version="1.1"')
    a(f'   id="{card_id}"')
    a(f'   sodipodi:docname="{docname}"')
    a(f'   inkscape:version="1.2.2 (b0a8486541, 2022-12-01)"')
    a(f'   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"')
    a(f'   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"')
    a(f'   xmlns="http://www.w3.org/2000/svg"')
    a(f'   xmlns:svg="http://www.w3.org/2000/svg">')
    a(f'  <sodipodi:namedview')
    a(f'     id="namedview_{card_id}"')
    a(f'     pagecolor="#ffffff"')
    a(f'     bordercolor="#666666"')
    a(f'     borderopacity="1.0"')
    a(f'     inkscape:showpageshadow="2"')
    a(f'     inkscape:pageopacity="0.0"')
    a(f'     inkscape:pagecheckerboard="0"')
    a(f'     inkscape:deskcolor="#d1d1d1"')
    a(f'     showgrid="false"')
    a(f'     inkscape:window-x="0"')
    a(f'     inkscape:window-y="0"')
    a(f'     inkscape:window-maximized="1"')
    a(f'     inkscape:current-layer="{card_id}"')
    a(f'     inkscape:document-units="in" />')
    a(f'  <defs id="defs_{card_id}">')
    a(f'    <clipPath id="card-clip">')
    a(f'      <rect x="0" y="0" width="{W}" height="{H}" rx="{RADIUS}" ry="{RADIUS}"')
    a(f'            id="clip-rect_{card_id}"/>')
    a(f'    </clipPath>')
    a(f'  </defs>')

    # ── Card background ──
    a(f'  <rect x="0" y="0" width="{W}" height="{H}" rx="{RADIUS}" ry="{RADIUS}"')
    a(f'        fill="{COLORS["offwhite"]}" clip-path="url(#card-clip)"/>')
    # Accent bar
    a(f'  <rect x="0" y="0" width="{W}" height="14" fill="{accent}"')
    a(f'        clip-path="url(#card-clip)"/>')
    # Border
    a(f'  <rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="{RADIUS}" ry="{RADIUS}"')
    a(f'        fill="none" stroke="{COLORS["border"]}" stroke-width="3"/>')
    # Chapter-gated footer band
    if chapter:
        a(f'  <rect x="0" y="{H-52}" width="{W}" height="52" fill="{accent}"')
        a(f'        opacity="0.12" clip-path="url(#card-clip)"/>')
        a(f'  <text x="{W//2}" y="{H-22}" text-anchor="middle"')
        a(f'        font-family="{FONT_SANS}" font-size="22" font-weight="600"')
        a(f'        fill="{accent}" letter-spacing="2">CHAPTER-GATED</text>')

    # ── Header ──
    a(f'  <text x="54" y="80" text-anchor="start"')
    a(f'        font-family="{FONT_SANS}" font-size="22" font-weight="normal"')
    a(f'        fill="{COLORS["rule"]}" letter-spacing="2">{esc(deck_label.upper())}</text>')

    # Title — may wrap at 24 chars
    title_lines = wrap(title, 24)
    title_y = 130
    for i, tl in enumerate(title_lines):
        a(f'  <text x="54" y="{title_y + i * 52}"')
        a(f'        font-family="{FONT_SERIF}" font-size="54" font-weight="bold"')
        a(f'        fill="{COLORS["ink"]}">{esc(tl)}</text>')

    header_bottom = title_y + len(title_lines) * 52 + 10

    # Divider under header
    a(f'  <line x1="54" y1="{header_bottom + 4}" x2="{W - 54}" y2="{header_bottom + 4}"')
    a(f'        stroke="{COLORS["divider"]}" stroke-width="1.5"/>')

    cy = header_bottom + 48

    # ── Prompt (italic serif) ──
    if prompt:
        for ln in wrap(prompt, WRAP_PROMPT):
            a(f'  <text x="54" y="{cy}"')
            a(f'        font-family="{FONT_SERIF}" font-size="28" font-style="italic"')
            a(f'        fill="{COLORS["muted"]}">{esc(ln)}</text>')
            cy += 38
        cy += 14

    # ── Sections ──
    first_section = True
    for sec in sections:
        label   = sec["label"]
        bullets = sec["bullets"]
        text    = sec["text"]

        # Divider between sections (but not before the first)
        if not first_section and (label or bullets or text):
            a(f'  <line x1="54" y1="{cy}" x2="{W - 54}" y2="{cy}"')
            a(f'        stroke="{COLORS["divider"]}" stroke-width="1.5"/>')
            cy += 26
        first_section = False

        if label:
            display_label = label if label.endswith(":") else label + ":"
            a(f'  <text x="54" y="{cy}" text-anchor="start"')
            a(f'        font-family="{FONT_SANS}" font-size="24" font-weight="600"')
            a(f'        fill="{COLORS["rule"]}">{esc(display_label)}</text>')
            cy += 36

        for b in bullets:
            blines = wrap(b, WRAP_BULLET)
            a(f'  <text x="62" y="{cy}" font-family="{FONT_SANS}"')
            a(f'        font-size="26" fill="{COLORS["rule"]}">·</text>')
            for j, bl in enumerate(blines):
                a(f'  <text x="82" y="{cy + j * 34}"')
                a(f'        font-family="{FONT_SANS}" font-size="26"')
                a(f'        fill="{COLORS["ink"]}">{esc(bl)}</text>')
            cy += len(blines) * 34 + 10

        if text:
            for ln in wrap(text, WRAP_BODY):
                a(f'  <text x="54" y="{cy}"')
                a(f'        font-family="{FONT_SANS}" font-size="26"')
                a(f'        fill="{COLORS["ink"]}">{esc(ln)}</text>')
                cy += 36
            cy += 8

    # ── Rule footer ──
    if rule:
        footer_y = H - (100 if chapter else 70)
        a(f'  <line x1="54" y1="{footer_y - 20}" x2="{W - 54}" y2="{footer_y - 20}"')
        a(f'        stroke="{COLORS["divider"]}" stroke-width="1.5"/>')
        for i, rl in enumerate(wrap(rule, 42)):
            a(f'  <text x="54" y="{footer_y + i * 32}"')
            a(f'        font-family="{FONT_SANS}" font-size="24"')
            a(f'        fill="{COLORS["rule"]}">{esc(rl)}</text>')

    a('</svg>')

    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# File I/O and incremental update
# ---------------------------------------------------------------------------

HASH_FILE = ".gm_card_hashes"


def load_hashes(out_dir):
    path = os.path.join(out_dir, HASH_FILE)
    hashes = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if "\t" in line:
                    fname, h = line.split("\t", 1)
                    hashes[fname] = h
    return hashes


def save_hashes(out_dir, hashes):
    path = os.path.join(out_dir, HASH_FILE)
    with open(path, "w") as f:
        for fname, h in sorted(hashes.items()):
            f.write(f"{fname}\t{h}\n")


def content_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def filename_for(card, index, total):
    """
    Produces a stable, sortable filename.
    da_01_escalate_the_danger.svg  /  cb_01_deal_damage.svg
    """
    prefix = "da" if card["deck_label"] == "Dramatic Action" else "cb"
    n = str(index + 1).zfill(2)
    return f"{prefix}_{n}_{slug(card['title'])}.svg"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate GM Move Deck SVG cards from mod_guide_gm.md"
    )
    parser.add_argument(
        "guide",
        help="Full path to mod_guide_gm.md"
    )
    parser.add_argument(
        "output_dir",
        help="Directory to write SVG files into (created if it doesn't exist)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate all files even if content hasn't changed"
    )
    args = parser.parse_args()

    guide_path = os.path.expanduser(args.guide)
    out_dir    = os.path.expanduser(args.output_dir)

    if not os.path.isfile(guide_path):
        sys.exit(f"ERROR: Guide file not found: {guide_path}")

    os.makedirs(out_dir, exist_ok=True)

    with open(guide_path, encoding="utf-8") as f:
        text = f.read()

    # Parse both decks
    da_cards     = extract_dramatic_action_cards(text)
    combat_cards = extract_combat_cards(text)

    if not da_cards:
        print("WARNING: No Dramatic Action cards found. Check guide structure.")
    if not combat_cards:
        print("WARNING: No Combat cards found. Check guide structure.")

    all_cards = (
        [(c, i, len(da_cards))     for i, c in enumerate(da_cards)] +
        [(c, i, len(combat_cards)) for i, c in enumerate(combat_cards)]
    )

    hashes  = load_hashes(out_dir)
    written = 0
    skipped = 0

    for card, index, total in all_cards:
        fname   = filename_for(card, index, total)
        svg     = render_svg(card)
        h       = content_hash(svg)

        if not args.force and hashes.get(fname) == h:
            skipped += 1
            continue

        filepath = os.path.join(out_dir, fname)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)
        hashes[fname] = h
        written += 1
        print(f"  wrote  {fname}")

    save_hashes(out_dir, hashes)

    total_cards = len(all_cards)
    print(f"\nDone. {written} written, {skipped} unchanged. ({total_cards} total cards)")
    if written > 0:
        print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()
