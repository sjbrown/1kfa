#!/usr/bin/env python3
"""
generate_character_html_sheet.py
=================================
Parses mod_guide_player.md and generates the Player Guide · Character Creation
printable reference sheet.

Usage:
    python3 generate_character_html_sheet.py path/to/mod_guide_player.md [--output-dir ./sheets]

Output:
    sheet_player_guide_character_creation.html
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CharacterCreationData:
    move_card_table: list           # [{"players": str, "cards": str}, ...]
    traits_read_aloud: str          # blockquote from Choose Dex/Int/Str
    name_read_aloud: str            # blockquote from Choose a Name
    worldcloth_questions: list      # list of question strings
    worldcloth_followup: str        # default follow-up line
    initiation_read_aloud: str      # last blockquote from Initiation (the "To choose..." one)
    initiation_options: list        # list of option strings
    receive_cards: list             # [{"move": str, "item": str}, ...]


# ---------------------------------------------------------------------------
# Parser helpers
# ---------------------------------------------------------------------------

def extract_blockquote(text: str) -> str:
    """
    Extract the first contiguous blockquote from text.
    Returns HTML-ready string with <br><br> paragraph breaks.
    """
    lines = []
    in_quote = False
    for line in text.splitlines():
        m = re.match(r'^>\s?(.*)', line)
        if m:
            in_quote = True
            lines.append(m.group(1))
        elif in_quote:
            break

    if not lines:
        return ""

    paragraphs = []
    current = []
    for line in lines:
        stripped = line.rstrip('\\').strip()
        # strip markdown bold/italic for HTML rendering
        stripped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
        stripped = re.sub(r'\*(.+?)\*', r'<em>\1</em>', stripped)
        if stripped == "" or stripped == ">":
            if current:
                paragraphs.append(" ".join(current))
                current = []
        else:
            # Handle bullet lines inside blockquotes
            if stripped.startswith("- "):
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
                paragraphs.append("&ndash;&nbsp;" + stripped[2:])
            else:
                current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))

    return "<br><br>\n        ".join(paragraphs)


def extract_all_blockquotes(text: str) -> list:
    """Extract all contiguous blockquote blocks from text."""
    results = []
    current = []
    for line in text.splitlines():
        m = re.match(r'^>\s?(.*)', line)
        if m:
            current.append(m.group(1))
        else:
            if current:
                paragraphs = []
                para = []
                for l in current:
                    stripped = l.rstrip('\\').strip()
                    stripped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
                    stripped = re.sub(r'\*(.+?)\*', r'<em>\1</em>', stripped)
                    if stripped == "":
                        if para:
                            paragraphs.append(" ".join(para))
                            para = []
                    elif stripped.startswith("- "):
                        if para:
                            paragraphs.append(" ".join(para))
                            para = []
                        paragraphs.append("&ndash;&nbsp;" + stripped[2:])
                    else:
                        para.append(stripped)
                if para:
                    paragraphs.append(" ".join(para))
                q = "<br><br>\n        ".join(paragraphs)
                if q:
                    results.append(q)
                current = []
    if current:
        paragraphs = []
        para = []
        for l in current:
            stripped = l.rstrip('\\').strip()
            stripped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
            stripped = re.sub(r'\*(.+?)\*', r'<em>\1</em>', stripped)
            if stripped == "":
                if para:
                    paragraphs.append(" ".join(para))
                    para = []
            elif stripped.startswith("- "):
                if para:
                    paragraphs.append(" ".join(para))
                    para = []
                paragraphs.append("&ndash;&nbsp;" + stripped[2:])
            else:
                para.append(stripped)
        if para:
            paragraphs.append(" ".join(para))
        q = "<br><br>\n        ".join(paragraphs)
        if q:
            results.append(q)
    return results


def parse_bullet_list(text: str) -> list:
    return [
        re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>',
        re.sub(r'\*(.+?)\*', r'<em>\1</em>', m.group(1).strip()))
        for m in re.finditer(r'^\s*[-*]\s+(.+)$', text, re.MULTILINE)
        if m.group(1).strip()
    ]


def parse_move_card_table(text: str) -> list:
    """Parse the | Number of PCs | Additional Cards | table."""
    rows = []
    for m in re.finditer(r'^\|\s*(\d)\s*\|\s*(\d+)\s*\|', text, re.MULTILINE):
        rows.append({"players": m.group(1), "cards": m.group(2)})
    return rows


def parse_receive_cards(text: str) -> list:
    """Parse the RECEIVE CARDS bullet list."""
    section_m = re.search(
        r'RECEIVE CARDS.*?\n((?:\s*[-*].+\n?)+)',
        text, re.DOTALL
    )
    if not section_m:
        return []
    items = []
    for m in re.finditer(r'[-*]\s+\*\*(.+?)\*\*\s*[—-]+\s*(?:take\s+)?(.+)', section_m.group(1)):
        move = m.group(1).strip()
        item = m.group(2).strip().rstrip('.')
        # strip italic markers
        item = re.sub(r'\*(.+?)\*', r'<em>\1</em>', item)
        items.append({"move": move, "item": item})
    return items


def parse_worldcloth_questions(text: str) -> tuple:
    """
    Returns (questions: list[str], followup: str).
    Questions are the bulleted list from Cut from the Worldcloth.
    Followup is the default follow-up line.
    """
    section_m = re.search(
        r'## Cut from the Worldcloth(.*?)(?=\n## |\n# |\Z)',
        text, re.DOTALL
    )
    if not section_m:
        return [], ""

    section = section_m.group(1)

    # Default follow-up
    followup = ""
    fu_m = re.search(r'you can default to this one:\s*\n\s*[-*]\s+(.+)', section)
    if fu_m:
        followup = fu_m.group(1).strip()

    # The 7 questions are the bullet list after "This conversation might also add details..."
    q_section_m = re.search(
        r'This conversation might also add details.*?\n((?:\s*[-*].+\n?)+)',
        section, re.DOTALL
    )
    questions = []
    if q_section_m:
        questions = parse_bullet_list(q_section_m.group(1))

    return questions, followup


def parse_initiation(text: str) -> tuple:
    """Returns (last_blockquote: str, options: list[str])."""
    section_m = re.search(
        r'## Initiation to Dark Gardens(.*?)(?=\n## |\n# |\Z)',
        text, re.DOTALL
    )
    if not section_m:
        return "", []

    section = section_m.group(1)

    # Get all blockquotes — we want the last one ("To choose...")
    quotes = extract_all_blockquotes(section)
    last_quote = quotes[-1] if quotes else ""

    # Options list — after "Here are the available Initiations"
    options_m = re.search(
        r'Here are the available Initiations.*?\n((?:\s*[-*].+\n?)+)',
        section, re.DOTALL
    )
    options = parse_bullet_list(options_m.group(1)) if options_m else []

    return last_quote, options


def parse_character_creation(text: str) -> CharacterCreationData:
    """Parse the # Character Creation section from mod_guide_player.md."""
    section_m = re.search(
        r'^# Character Creation\s*(.*?)(?=\n# |\Z)',
        text, re.DOTALL | re.MULTILINE
    )
    if not section_m:
        sys.exit("ERROR: Could not find '# Character Creation' section in guide.")
    section = section_m.group(1)

    # Move card table
    move_card_section_m = re.search(
        r'## Choose Move Cards(.*?)(?=\n## |\Z)',
        section, re.DOTALL
    )
    move_card_table = []
    if move_card_section_m:
        move_card_table = parse_move_card_table(move_card_section_m.group(1))

    # Traits read-aloud
    traits_section_m = re.search(
        r'## Choose Dex / Int / Str(.*?)(?=\n## |\Z)',
        section, re.DOTALL
    )
    traits_read_aloud = ""
    if traits_section_m:
        traits_read_aloud = extract_blockquote(traits_section_m.group(1))

    # Name read-aloud
    name_section_m = re.search(
        r'## Choose a Name(.*?)(?=\n## |\Z)',
        section, re.DOTALL
    )
    name_read_aloud = ""
    if name_section_m:
        name_read_aloud = extract_blockquote(name_section_m.group(1))

    # Worldcloth questions and follow-up
    worldcloth_questions, worldcloth_followup = parse_worldcloth_questions(section)

    # Initiation
    initiation_read_aloud, initiation_options = parse_initiation(section)

    # Receive cards — parse from the Weapons and Items section
    weapons_section_m = re.search(
        r'# Weapons and Items(.*?)(?=\n# |\Z)',
        text, re.DOTALL
    )
    receive_cards = []
    if weapons_section_m:
        receive_cards = parse_receive_cards(weapons_section_m.group(1))

    return CharacterCreationData(
        move_card_table=move_card_table,
        traits_read_aloud=traits_read_aloud,
        name_read_aloud=name_read_aloud,
        worldcloth_questions=worldcloth_questions,
        worldcloth_followup=worldcloth_followup,
        initiation_read_aloud=initiation_read_aloud,
        initiation_options=initiation_options,
        receive_cards=receive_cards,
    )


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """
  @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

  :root {
    --ink:      #1A1917;
    --light:    #F5F2EB;
    --mid:      #E0DDD5;
    --rule:     #888780;
    --accent:   #3C3489;
    --warm:     #854F0B;
    --danger:   #C0410E;
    --green:    #0F6E56;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  @media print {
    body { background: white; padding: 0; }
    .page { box-shadow: none; margin: 0; border-radius: 0; }
  }

  body {
    background: #ccc;
    font-family: 'Space Mono', monospace;
    font-size: 10.5px;
    color: var(--ink);
    padding: 1.5rem;
  }

  .page {
    background: white;
    width: 8.5in;
    min-height: 11in;
    margin: 0 auto;
    padding: 0.45in 0.45in 0.4in;
    box-shadow: 0 4px 24px rgba(0,0,0,0.18);
    border-radius: 2px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr auto;
    gap: 0 0.28in;
  }

  .header {
    grid-column: 1 / -1;
    border-bottom: 2.5px solid var(--ink);
    padding-bottom: 0.1in;
    margin-bottom: 0.16in;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
  }

  .guide-badge {
    display: inline-block;
    background: var(--ink);
    color: white;
    font-family: 'IM Fell English', serif;
    font-size: 11px;
    padding: 2px 8px;
    margin-bottom: 5px;
    letter-spacing: 0.04em;
  }

  .header h1 {
    font-family: 'IM Fell English', serif;
    font-size: 24px;
    line-height: 1;
    letter-spacing: 0.01em;
  }

  .header-right {
    text-align: right;
    font-size: 8px;
    color: var(--rule);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    line-height: 1.8;
    padding-bottom: 2px;
  }

  .col-left  { grid-column: 1; }
  .col-right { grid-column: 2; }

  .footer {
    grid-column: 1 / -1;
    border-top: 1px solid var(--mid);
    margin-top: 0.12in;
    padding-top: 6px;
    font-size: 7.5px;
    color: var(--rule);
    text-transform: uppercase;
    letter-spacing: 0.12em;
  }

  .section { margin-bottom: 0.13in; }

  .section-head {
    font-size: 7.5px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: white;
    background: var(--ink);
    padding: 3px 7px;
    margin-bottom: 7px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .section-head.accent  { background: var(--accent); }
  .section-head.warm    { background: var(--warm); }
  .section-head.green   { background: var(--green); }
  .section-head.danger  { background: var(--danger); }

  .checklist { list-style: none; padding: 0; }
  .checklist li {
    display: flex;
    align-items: flex-start;
    gap: 7px;
    padding: 3px 0;
    border-bottom: 0.5px solid var(--mid);
    font-size: 10px;
    line-height: 1.4;
  }
  .checklist li:last-child { border-bottom: none; }

  .cb {
    width: 12px;
    height: 12px;
    border: 1.5px solid var(--ink);
    flex-shrink: 0;
    margin-top: 1px;
  }

  .read-aloud {
    font-style: italic;
    font-size: 9.5px;
    color: var(--accent);
    border-left: 2px solid var(--accent);
    padding: 3px 7px;
    margin-bottom: 6px;
    line-height: 1.5;
  }

  .rule-note {
    font-size: 9px;
    color: var(--rule);
    line-height: 1.5;
    margin-bottom: 5px;
  }
  .rule-note strong { color: var(--ink); }

  .data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 9px;
    margin-bottom: 6px;
  }
  .data-table th {
    text-align: left;
    font-weight: 700;
    font-size: 7.5px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--rule);
    border-bottom: 1px solid var(--mid);
    padding: 2px 4px;
  }
  .data-table td {
    padding: 2px 4px;
    border-bottom: 0.5px dotted var(--mid);
  }
  .data-table tr:last-child td { border-bottom: none; }

  .rank-row {
    display: flex;
    gap: 4px;
    margin-bottom: 6px;
    flex-wrap: wrap;
  }
  .rank-pill {
    border: 1.5px solid var(--mid);
    border-radius: 2px;
    padding: 2px 6px;
    font-size: 8.5px;
    display: flex;
    gap: 4px;
    align-items: center;
  }
  .rank-pill .rank-name { font-weight: 700; }
  .rank-pill .rank-num  { color: var(--rule); }

  .q-list { list-style: none; padding: 0; }
  .q-list li {
    display: flex;
    align-items: flex-start;
    gap: 5px;
    padding: 2.5px 0;
    font-size: 9.5px;
    line-height: 1.4;
    border-bottom: 0.5px dotted var(--mid);
  }
  .q-list li:last-child { border-bottom: none; }
  .q-sym {
    color: var(--rule);
    flex-shrink: 0;
    font-size: 9px;
    margin-top: 2px;
  }

  .init-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1px 8px;
    margin-bottom: 5px;
  }
  .init-item {
    font-size: 9px;
    padding: 2px 0;
    border-bottom: 0.5px dotted var(--mid);
    line-height: 1.4;
    display: flex;
    align-items: flex-start;
    gap: 4px;
  }

  .followup-box {
    border: 1px dashed var(--warm);
    padding: 4px 7px;
    margin-top: 5px;
    font-size: 9px;
    color: var(--warm);
    line-height: 1.4;
  }
  .followup-box strong { color: var(--warm); }

  .handoff {
    border: 1px solid var(--green);
    padding: 7px 9px;
    font-size: 9.5px;
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .handoff-arrow { font-size: 20px; color: var(--green); flex-shrink: 0; }
  .handoff-label {
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--green);
    display: block;
    margin-bottom: 2px;
    font-weight: 700;
  }
"""


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def cb() -> str:
    return '<span class="cb"></span>'

def section_head(label: str, color: str = "") -> str:
    cls = ("section-head " + color).strip()
    return f'      <div class="{cls}">{label}</div>\n'

def read_aloud(text: str, style: str = "") -> str:
    s = f' style="{style}"' if style else ""
    return f'      <div class="read-aloud"{s}>\n        &ldquo;{text}&rdquo;\n      </div>\n'

def rule_note(text: str, style: str = "") -> str:
    s = f' style="{style}"' if style else ""
    return f'      <p class="rule-note"{s}>{text}</p>\n'

def checklist_item(text: str) -> str:
    return f'        <li>{cb()}<span>{text}</span></li>\n'


# ---------------------------------------------------------------------------
# Column renderers
# ---------------------------------------------------------------------------

COMPONENTS = [
    "Character sheet &mdash; one per player",
    "Deckahedron (20 cards) per player &mdash; or use the app",
    "Move Deck &mdash; remove cards not matching campaign length",
    "Pen or pencil per player",
]


def render_left_column(data: CharacterCreationData) -> str:
    # Move card table rows
    table_rows = "".join(
        f'          <tr><td>{r["players"]}</td><td>{r["cards"]}</td></tr>\n'
        for r in data.move_card_table
    ) or '          <tr><td>1</td><td>3</td></tr>\n          <tr><td>2</td><td>6</td></tr>\n          <tr><td>3</td><td>8</td></tr>\n          <tr><td>4</td><td>13</td></tr>\n          <tr><td>5</td><td>15</td></tr>\n'

    components_html = "".join(checklist_item(c) for c in COMPONENTS)

    return (
        f'  <div class="col-left">\n\n'

        # Components
        f'    <div class="section">\n'
        f'{section_head("Components", "warm")}'
        f'      <ul class="checklist">\n{components_html}      </ul>\n'
        f'    </div>\n\n'

        # Choose Move Cards
        f'    <div class="section">\n'
        f'{section_head("Choose Move Cards", "accent")}'
        f'      <p class="rule-note" style="margin-bottom:6px;">Lay out all 3 cards marked <strong>A</strong>. Add more based on player count, stacked in 3 streams &mdash; only title visible on lower cards.</p>\n'
        f'      <table class="data-table" style="margin-bottom:7px;">\n'
        f'        <thead><tr><th># of Players</th><th>Additional Cards</th></tr></thead>\n'
        f'        <tbody>\n{table_rows}        </tbody>\n'
        f'      </table>\n'
        f'      <p class="rule-note">Pick order: use <strong>The Rule Beneath All Rules</strong>. Each player picks 3 cards.</p>\n'
        f'    </div>\n\n'

        # Choose Traits
        f'    <div class="section">\n'
        f'{section_head("Choose Dex / Int / Str", "accent")}'
        f'      <div class="rank-row">\n'
        f'        <div class="rank-pill"><span class="rank-name">Anvil</span><span class="rank-num">1</span></div>\n'
        f'        <div class="rank-pill"><span class="rank-name">Blades</span><span class="rank-num">2</span></div>\n'
        f'        <div class="rank-pill"><span class="rank-name">Crown</span><span class="rank-num">3</span></div>\n'
        f'        <div class="rank-pill"><span class="rank-name">Dragon</span><span class="rank-num">4</span></div>\n'
        f'      </div>\n'
        f'{read_aloud(data.traits_read_aloud, "margin-bottom:7px;")}'
        f'    </div>\n\n'

        # Choose Name
        f'    <div class="section">\n'
        f'{section_head("Choose a Name", "accent")}'
        f'{read_aloud(data.name_read_aloud)}'
        f'      <p class="rule-note">Players write their name on their sheet, bold and large so everyone can read it.</p>\n'
        f'    </div>\n\n'

        f'  </div><!-- end col-left -->\n'
    )


def render_right_column(data: CharacterCreationData) -> str:
    # Worldcloth questions
    q_items = "".join(
        f'        <li><span class="q-sym">&rarr;</span><span>{q}</span></li>\n'
        for q in data.worldcloth_questions
    )

    followup_html = ""
    if data.worldcloth_followup:
        fu = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>',
             re.sub(r'\*(.+?)\*', r'<em>\1</em>', data.worldcloth_followup))
        followup_html = (
            f'      <div class="followup-box">\n'
            f'        <strong>Default follow-up:</strong> &ldquo;{fu}&rdquo;\n'
            f'      </div>\n'
        )

    # Initiation options grid
    init_items = "".join(
        f'        <div class="init-item"><span class="q-sym">&middot;</span><span>{opt}</span></div>\n'
        for opt in data.initiation_options
    )

    # Weapons & Items checklist — build dynamically from parsed receive_cards
    weapons_items = [checklist_item("2 Pack cards")]
    for rc in data.receive_cards:
        weapons_items.append(checklist_item(f'<strong>{rc["move"]}</strong> &mdash; {rc["item"]}'))
    weapons_items.append(checklist_item("2 Item cards"))
    weapons_items.append(checklist_item("Mark Magic Item Charges"))
    weapons_html = "".join(weapons_items)

    return (
        f'  <div class="col-right">\n\n'

        # Worldcloth
        f'    <div class="section">\n'
        f'{section_head("Cut from the Worldcloth", "accent")}'
        f'      <p class="rule-note" style="margin-bottom:5px;">Address one question to one player at a time. Allow interruptions and riffing; re-center after. Add a follow-up of your own to each.</p>\n'
        f'      <ul class="q-list">\n{q_items}      </ul>\n'
        f'{followup_html}'
        f'    </div>\n\n'

        # Initiation
        f'    <div class="section">\n'
        f'{section_head("Initiation to Dark Gardens", "danger")}'
        f'{read_aloud(data.initiation_read_aloud, "margin-bottom:6px;")}'
        f'      <div class="init-grid">\n{init_items}      </div>\n'
        f'      <p class="rule-note">Tokens stay on the sheet &mdash; not available to spend yet.</p>\n'
        f'    </div>\n\n'

        # Weapons & Items
        f'    <div class="section">\n'
        f'{section_head("Weapons &amp; Items", "green")}'
        f'      <ul class="checklist">\n{weapons_html}      </ul>\n'
        f'    </div>\n\n'

        # Handoff
        f'    <div class="section">\n'
        f'      <div class="handoff">\n'
        f'        <span class="handoff-arrow">&#8594;</span>\n'
        f'        <span>\n'
        f'          <strong class="handoff-label">Character Creation Complete</strong>\n'
        f'          Hand off to the GM Guide at <em>Gather Around the Hearth</em>.\n'
        f'        </span>\n'
        f'      </div>\n'
        f'    </div>\n\n'

        f'  </div><!-- end col-right -->\n'
    )


# ---------------------------------------------------------------------------
# Full page renderer
# ---------------------------------------------------------------------------

def render_sheet(data: CharacterCreationData) -> str:
    return (
        f'<!DOCTYPE html>\n'
        f'<html lang="en">\n'
        f'<head>\n'
        f'<meta charset="UTF-8">\n'
        f'<title>1kFA &mdash; Player Guide &middot; Character Creation</title>\n'
        f'<style>\n{CSS}\n</style>\n'
        f'</head>\n'
        f'<body>\n'
        f'<div class="page">\n\n'
        f'  <div class="header">\n'
        f'    <div class="header-left">\n'
        f'      <div class="guide-badge">Player Guide</div>\n'
        f'      <h1>Character Creation</h1>\n'
        f'    </div>\n'
        f'    <div class="header-right">\n'
        f'      A Thousand Faces of Adventure<br>\n'
        f'      1kfa.com\n'
        f'    </div>\n'
        f'  </div>\n\n'
        f'{render_left_column(data)}\n'
        f'{render_right_column(data)}\n'
        f'  <div class="footer">\n'
        f'    <span>1kfa &middot; Player Guide &middot; Character Creation</span>\n'
        f'  </div>\n\n'
        f'</div>\n'
        f'</body>\n'
        f'</html>\n'
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate the 1kFA Player Guide Character Creation sheet from mod_guide_player.md"
    )
    parser.add_argument("guide", help="Path to mod_guide_player.md")
    parser.add_argument(
        "--output-dir", default=".",
        help="Directory for the output HTML file (default: current directory)"
    )
    args = parser.parse_args()

    if not os.path.exists(args.guide):
        print(f"Error: {args.guide} not found.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Parsing {args.guide}...")
    with open(args.guide, encoding="utf-8") as f:
        text = f.read()

    data = parse_character_creation(text)

    print(f"  move card table rows: {len(data.move_card_table)}")
    print(f"  traits read-aloud:    {len(data.traits_read_aloud)} chars")
    print(f"  name read-aloud:      {len(data.name_read_aloud)} chars")
    print(f"  worldcloth questions: {len(data.worldcloth_questions)}")
    print(f"  worldcloth follow-up: {data.worldcloth_followup[:40]!r}...")
    print(f"  initiation read-aloud:{len(data.initiation_read_aloud)} chars")
    print(f"  initiation options:   {len(data.initiation_options)}")
    print(f"  receive cards:        {len(data.receive_cards)}")

    html = render_sheet(data)
    filename = "sheet_player_guide_character_creation.html"
    out_path = os.path.join(args.output_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
