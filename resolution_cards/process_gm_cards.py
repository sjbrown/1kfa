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

# Matches a fenced block with a specific language tag, capturing the content.
# Group 1 = fence tag suffix (e.g. "dramatic_action" or "combat")
# Group 2 = block content
_FENCE_RE = re.compile(
    r'```card_gm_(\w+)\n(.*?)```',
    re.DOTALL
)

# Looks backward from a fence for the nearest ### or #### heading above it.
_HEADING_RE = re.compile(r'#{3,4} (.+)')

# chapter_gated flag: present in the fence tag or content
_CHAPTER_TAG = 'chapter_gated'


def _heading_before(text, fence_start):
    """Return the nearest ### heading text that precedes fence_start."""
    preceding = text[:fence_start]
    headings = _HEADING_RE.findall(preceding)
    return headings[-1].strip() if headings else None


def extract_dramatic_action_cards(text):
    """
    Scans the full document for ```card_gm_dramatic_action fences.
    Each fence is one card. The ### heading immediately above it is the title.

    Each card dict:
        title       str
        deck_label  "Dramatic Action"
        raw_block   str   verbatim fence content
        chapter     False (DA cards are never chapter-gated)
    """
    cards = []
    for m in _FENCE_RE.finditer(text):
        tag, raw_block = m.group(1), m.group(2)
        if tag != 'dramatic_action':
            continue
        if not raw_block.strip() or raw_block.strip() == '???':
            continue
        title = _heading_before(text, m.start()) or "Untitled"
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
    """
    Scans the full document for ```card_gm_combat fences.
    Each fence is one card. The ### heading immediately above it is the title.

    chapter=True when the fence tag is ```card_gm_combat_chapter_gated.

    Each card dict:
        title       str
        deck_label  "Combat"
        raw_block   str   verbatim fence content
        chapter     bool
    """
    cards = []
    for m in _FENCE_RE.finditer(text):
        tag, raw_block = m.group(1), m.group(2)
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
    """
    Converts the verbatim fenced-block text into structured fields the SVG
    renderer uses.

    The guide's card blocks use a loose, inconsistent format. This parser
    handles all observed patterns:

      Answer:           — italic prompt, may span indented continuation lines
          indented text       e.g. Escalate the Danger, Pivot
      Answer:           — prompt on the same line
      inline text       e.g. "What negative consequence..."

      Choose one:       — section label followed by bullet list
       * bullet
       * bullet

      Plain prose       — body text (Deal Damage: "By default, deal 1-4 damage.")

      Rule footer lines — contain "shuffle", "reshuffle", "maximum", or start
                          with "Then:" and don't introduce a new section.

    "A threat approaches" has two parallel option groups with no Choose/Answer
    wrapper — they're recognised by the "Add a shadow point." / "Use a shadow
    point." opener and treated as labelled sections.

    Returns:
        prompt    str or None   — the Answer: text, rendered in italic
        sections  list of dicts — each {"label": str|None, "bullets": [str], "text": str|None}
        rule      str or None   — footer rule text
    """
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

    # Working state for the current section being accumulated
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

        # ── blank ──
        if not line:
            i += 1
            continue

        # ── rule footer ──
        # "Then:\nShuffle..." pattern: "Then:" alone on a line followed by
        # a shuffle line. Also catches inline "Then: Shuffle …"
        if re.match(r'^Then\s*:', line, re.I):
            # peek: if next non-blank line is a rule, absorb both
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and RULE_PAT.search(lines[j]):
                rule_lines.append(lines[j].strip())
                i = j + 1
            else:
                # "Then:" followed by non-rule — treat as section label
                flush()
                cur_label = line.rstrip(':')
                i += 1
            continue

        if RULE_PAT.search(line) and not BULLET_PAT.match(raw):
            # Only treat as a footer rule if the rule keyword appears early in
            # the line (i.e. it IS the point of the line, not buried in prose).
            # "Shuffle the GM Move Deck" → keyword at pos 0 → rule. ✓
            # "Expend stamina & reshuffle this deck" → keyword at pos 17 → body. ✓
            rule_pos = RULE_PAT.search(line).start()
            if rule_pos <= len(line) // 2:
                rule_lines.append(line)
                i += 1
                continue

        # ── Answer: prompt ──
        if ANSWER_PAT.match(line):
            inline = ANSWER_PAT.sub('', line).strip()
            parts  = [inline] if inline else []
            # collect indented continuation lines
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    break
                # indented by 2+ spaces relative to "Answer:"
                if re.match(r'  ', nxt):
                    parts.append(nxt.strip())
                    i += 1
                else:
                    break
            if parts:
                prompt = " ".join(parts)
            continue

        # ── bullet ──
        if BULLET_PAT.match(raw):
            cur_bullets.append(BULLET_PAT.sub('', raw).strip())
            i += 1
            continue

        # ── section label ──
        if LABEL_PAT.match(line):
            flush()
            cur_label = line.rstrip(':').rstrip('.')
            i += 1
            continue

        # ── plain text ──
        # Accumulate into current section's text, joining continuation lines
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
