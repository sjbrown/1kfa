#!/usr/bin/env python3
"""
process_gm_cards.py
===================
Parses mod_guide_gm.md and generates Inkscape-compatible SVG playing cards
(2.5 x 3.5 in, 750x1050 px viewBox) for the GM Move Deck.

Usage:
    python3 process_gm_cards.py <path/to/mod_guide_gm.md> <output_directory>

Example:
    python3 process_gm_cards.py ~/1kfa/mod_guide_gm.md ~/Desktop/gm-cards

The script finds two sections in the guide:
  1. Dramatic Action GM Moves  — card_gm_dramatic_action fenced blocks
  2. Combat GM Move Deck       — card_gm_combat fenced blocks

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
    "damage":   "#C0410E",
    "shadow":   "#3C3489",
    "neutral":  "#5F5E5A",
    "pivot":    "#0F6E56",
    "resource": "#854F0B",
    "fear":     "#533489",
    "rally":    "#1D9E75",
    "chapter":  "#854F0B",
    "offwhite": "#F8F6F1",
    "ink":      "#1A1917",
    "muted":    "#5F5E5A",
    "rule":     "#888780",
    "border":   "#C8C6BE",
    "divider":  "#DDDBD3",
}

ACCENT_MAP = [
    ("escalate",        "damage"),
    ("deal damage",     "damage"),
    ("pivot",           "pivot"),
    ("price",           "neutral"),
    ("threat",          "shadow"),
    ("all eyes",        "neutral"),
    ("use up",          "resource"),
    ("separate",        "neutral"),
    ("special ability", "damage"),
    ("reinforcement",   "neutral"),
    ("disarm",          "neutral"),
    ("imperiled",       "shadow"),
    ("imperil",         "shadow"),
    ("tactical",        "shadow"),
    ("echo",            "fear"),
    ("glory",           "rally"),
    ("separation",      "chapter"),
    ("revelation",      "chapter"),
    ("reunion",         "chapter"),
]

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS  = "Helvetica Neue, Arial, sans-serif"

WRAP_BODY   = 37
WRAP_PROMPT = 36
WRAP_BULLET = 37


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r'```card_gm_(\w+)(?:\s+(\d+)x)?\n(.*?)```', re.DOTALL)
# Match ### or #### headings
_HEADING_RE = re.compile(r'#{3,4} (.+)')
_CHAPTER_TAG = 'chapter_gated'


def _heading_before(text, fence_start):
    preceding = text[:fence_start]
    headings = _HEADING_RE.findall(preceding)
    return headings[-1].strip() if headings else None


def extract_dramatic_action_cards(text):
    cards = []
    for m in _FENCE_RE.finditer(text):
        tag, multiplier, raw_block = m.group(1), m.group(2), m.group(3)
        if tag != 'dramatic_action':
            continue
        if not raw_block.strip() or raw_block.strip() == '???':
            continue
        title = _heading_before(text, m.start()) or "Untitled"
        count = int(multiplier) if multiplier else 1
        for _ in range(count):
            cards.append({
                "title":      title,
                "deck_label": "Dramatic Action",
                "raw_block":  raw_block,
                "chapter":    False,
            })
    if not cards:
        sys.exit("ERROR: No ```card_gm_dramatic_action fences found in the guide.")
    return cards


def extract_combat_cards(text):
    cards = []
    for m in _FENCE_RE.finditer(text):
        tag, raw_block = m.group(1), m.group(3)
        if not tag.startswith('combat'):
            continue
        if not raw_block.strip():
            continue
        title   = _heading_before(text, m.start()) or "Untitled"
        chapter = _CHAPTER_TAG in tag
        cards.append({
            "title":      title,
            "deck_label": "Combat",
            "raw_block":  raw_block,
            "chapter":    chapter,
        })
    if not cards:
        sys.exit("ERROR: No ```card_gm_combat fences found in the guide.")
    return cards


# ---------------------------------------------------------------------------
# Card face content: parse raw_block into structured fields
# ---------------------------------------------------------------------------

def parse_card_block(raw_block, title):
    RULE_PAT  = re.compile(r'\b(shuffle|reshuffle|maximum)\b', re.I)
    LABEL_PAT = re.compile(
        r'^(Choose\b|Then\b|Place\b|If they\b|Add a shadow point|Use a shadow point)'
    )
    ANSWER_PAT = re.compile(r'^Answer\s*:\s*', re.I)
    BULLET_PAT = re.compile(r'^\s*\*\s+')

    lines = raw_block.strip().splitlines()
    prompt     = None
    sections   = []
    rule_lines = []
    cur_label   = None
    cur_bullets = []
    cur_texts   = []

    def flush():
        nonlocal cur_label, cur_bullets, cur_texts
        text = " ".join(cur_texts).strip() or None
        if cur_label or cur_bullets or text:
            sections.append({
                "label":   cur_label,
                "bullets": list(cur_bullets),
                "text":    text,
            })
        cur_label, cur_bullets, cur_texts = None, [], []

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        if re.match(r'^Then\s*:', line, re.I):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and RULE_PAT.search(lines[j]):
                rule_lines.append(lines[j].strip())
                i = j + 1
            else:
                flush()
                cur_label = line.rstrip(':')
                i += 1
            continue

        if RULE_PAT.search(line) and not BULLET_PAT.match(raw):
            rule_pos = RULE_PAT.search(line).start()
            if rule_pos <= len(line) // 2:
                rule_lines.append(line)
                i += 1
                continue

        if ANSWER_PAT.match(line):
            inline = ANSWER_PAT.sub('', line).strip()
            parts  = [inline] if inline else []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    break
                if re.match(r'  ', nxt):
                    parts.append(nxt.strip())
                    i += 1
                else:
                    break
            if parts:
                prompt = " ".join(parts)
            continue

        if BULLET_PAT.match(raw):
            cur_bullets.append(BULLET_PAT.sub('', raw).strip())
            i += 1
            continue

        if LABEL_PAT.match(line):
            flush()
            cur_label = line.rstrip(':').rstrip('.')
            i += 1
            continue

        flush()
        cur_texts = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt:
                break
            if BULLET_PAT.match(lines[i]) or ANSWER_PAT.match(nxt):
                break
            if LABEL_PAT.match(nxt) or (RULE_PAT.search(nxt) and RULE_PAT.search(nxt).start() <= len(nxt) // 2):
                break
            cur_texts.append(nxt)
            i += 1
        flush()

    flush()
    rule = " ".join(rule_lines).strip() or None
    return {"prompt": prompt, "sections": sections, "rule": rule}


# ---------------------------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------------------------

def esc(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def wrap(text, width):
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
    title      = card["title"]
    deck_label = card["deck_label"]
    chapter    = card["chapter"]
    raw_block  = card["raw_block"]

    parsed   = parse_card_block(raw_block, title)
    prompt   = parsed["prompt"]
    sections = parsed["sections"]
    rule     = parsed["rule"]

    accent  = accent_for(title)
    card_id = "svg_" + slug(title)
    docname = slug(title) + ".svg"

    # Shadow and Death cards get a black header band with white text
    dark_card = title.lower() in ('shadow', 'death')

    out = []
    a = out.append

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

    # Background
    a(f'  <rect x="0" y="0" width="{W}" height="{H}" rx="{RADIUS}" ry="{RADIUS}"')
    a(f'        fill="{COLORS["offwhite"]}" clip-path="url(#card-clip)"/>')
    if dark_card:
        # Full black header band from top down to just below the title
        header_band_h = 200
        a(f'  <rect x="0" y="0" width="{W}" height="{header_band_h}" fill="#1A1917"')
        a(f'        clip-path="url(#card-clip)"/>')
    else:
        a(f'  <rect x="0" y="0" width="{W}" height="14" fill="{accent}"')
        a(f'        clip-path="url(#card-clip)"/>')
    a(f'  <rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="{RADIUS}" ry="{RADIUS}"')
    a(f'        fill="none" stroke="{COLORS["border"]}" stroke-width="3"/>')

    if chapter:
        a(f'  <rect x="0" y="{H-52}" width="{W}" height="52" fill="{accent}"')
        a(f'        opacity="0.12" clip-path="url(#card-clip)"/>')
        a(f'  <text x="{W//2}" y="{H-22}" text-anchor="middle"')
        a(f'        font-family="{FONT_SANS}" font-size="26" font-weight="600"')
        a(f'        fill="{accent}" letter-spacing="2">CHAPTER-GATED</text>')

    # Header
    deck_label_color = "#FFFFFF" if dark_card else COLORS["rule"]
    title_color      = "#FFFFFF" if dark_card else COLORS["ink"]

    a(f'  <text x="54" y="80" text-anchor="start"')
    a(f'        font-family="{FONT_SANS}" font-size="26" font-weight="normal"')
    a(f'        fill="{deck_label_color}" letter-spacing="2">{esc(deck_label.upper())}</text>')

    title_lines = wrap(title, 24)
    title_y = 130
    for i, tl in enumerate(title_lines):
        a(f'  <text x="54" y="{title_y + i * 52}"')
        a(f'        font-family="{FONT_SERIF}" font-size="65" font-weight="bold"')
        a(f'        fill="{title_color}">{esc(tl)}</text>')

    header_bottom = title_y + len(title_lines) * 52 + 10

    a(f'  <line x1="54" y1="{header_bottom + 4}" x2="{W - 54}" y2="{header_bottom + 4}"')
    a(f'        stroke="{COLORS["divider"]}" stroke-width="1.5"/>')

    cy = header_bottom + 48

    # Prompt
    if prompt:
        for ln in wrap(prompt, WRAP_PROMPT):
            a(f'  <text x="54" y="{cy}"')
            a(f'        font-family="{FONT_SERIF}" font-size="34" font-style="italic"')
            a(f'        fill="{COLORS["muted"]}">{esc(ln)}</text>')
            cy += 38
        cy += 14

    # Sections
    first_section = True
    for sec in sections:
        label   = sec["label"]
        bullets = sec["bullets"]
        text    = sec["text"]

        if not first_section and (label or bullets or text):
            a(f'  <line x1="54" y1="{cy}" x2="{W - 54}" y2="{cy}"')
            a(f'        stroke="{COLORS["divider"]}" stroke-width="1.5"/>')
            cy += 26
        first_section = False

        if label:
            display_label = label if label.endswith(":") else label + ":"
            a(f'  <text x="54" y="{cy}" text-anchor="start"')
            a(f'        font-family="{FONT_SANS}" font-size="29" font-weight="600"')
            a(f'        fill="{COLORS["rule"]}">{esc(display_label)}</text>')
            cy += 36

        for b in bullets:
            blines = wrap(b, WRAP_BULLET)
            a(f'  <text x="62" y="{cy}" font-family="{FONT_SANS}"')
            a(f'        font-size="31" fill="{COLORS["rule"]}">·</text>')
            for j, bl in enumerate(blines):
                a(f'  <text x="82" y="{cy + j * 34}"')
                a(f'        font-family="{FONT_SANS}" font-size="31"')
                a(f'        fill="{COLORS["ink"]}">{esc(bl)}</text>')
            cy += len(blines) * 34 + 10

        if text:
            for ln in wrap(text, WRAP_BODY):
                a(f'  <text x="54" y="{cy}"')
                a(f'        font-family="{FONT_SANS}" font-size="31"')
                a(f'        fill="{COLORS["ink"]}">{esc(ln)}</text>')
                cy += 36
            cy += 8

    # Rule footer
    if rule:
        footer_y = H - (100 if chapter else 70)
        a(f'  <line x1="54" y1="{footer_y - 20}" x2="{W - 54}" y2="{footer_y - 20}"')
        a(f'        stroke="{COLORS["divider"]}" stroke-width="1.5"/>')
        for i, rl in enumerate(wrap(rule, 42)):
            a(f'  <text x="54" y="{footer_y + i * 32}"')
            a(f'        font-family="{FONT_SANS}" font-size="29"')
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
    parser.add_argument("guide", help="Full path to mod_guide_gm.md")
    parser.add_argument("output_dir", help="Directory to write SVG files into")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate all files even if content hasn't changed")
    args = parser.parse_args()

    guide_path = os.path.expanduser(args.guide)
    out_dir    = os.path.expanduser(args.output_dir)

    if not os.path.isfile(guide_path):
        sys.exit(f"ERROR: Guide file not found: {guide_path}")

    os.makedirs(out_dir, exist_ok=True)

    with open(guide_path, encoding="utf-8") as f:
        text = f.read()

    da_cards     = extract_dramatic_action_cards(text)
    combat_cards = extract_combat_cards(text)

    all_cards = (
        [(c, i, len(da_cards))     for i, c in enumerate(da_cards)] +
        [(c, i, len(combat_cards)) for i, c in enumerate(combat_cards)]
    )

    hashes  = load_hashes(out_dir)
    written = 0
    skipped = 0

    for card, index, total in all_cards:
        fname = filename_for(card, index, total)
        svg   = render_svg(card)
        h     = content_hash(svg)

        if not args.force and hashes.get(fname) == h:
            skipped += 1
            continue

        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            f.write(svg)
        hashes[fname] = h
        written += 1
        print(f"  wrote  {fname}")

    save_hashes(out_dir, hashes)
    print(f"\nDone. {written} written, {skipped} unchanged. ({len(all_cards)} total cards)")
    if written > 0:
        print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()
