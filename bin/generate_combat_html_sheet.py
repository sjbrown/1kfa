#!/usr/bin/env python3
"""
generate_combat_html_sheet.py
==============================
Parses mod_guide_gm.md to extract:
  - Shadow Point augmentation table
  - Special abilities list

Everything else is hardcoded (turn structure, setup, closing).

Usage:
    python3 generate_combat_html_sheet.py path/to/mod_guide_gm.md [--output-dir ./sheets]

Output:
    sheet_combat_interlude.html
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CombatData:
    augmentations: list   # [{"cost": str, "effect": str}, ...]
    abilities: list       # [{"name": str, "desc": str}, ...]


# ---------------------------------------------------------------------------
# Parser helpers
# ---------------------------------------------------------------------------

def md_to_html_inline(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text


def parse_augmentation_table(text: str) -> list:
    """
    Parse the markdown pipe table after
    "spend *Shadow points* according to this table".

    Format:
        | Shadow points       | Foe augmentation
        |---------------------|------------------
        | 2                   | Raise Might to d6
        ...
    """
    marker_m = re.search(
        r'spend \*Shadow points\* according to this table\.\n(.*?)(?=\n\n\S|\Z)',
        text, re.DOTALL
    )
    if not marker_m:
        return []

    rows = []
    for m in re.finditer(
        r'^\|\s*(\d+)\s*\|\s*(.+?)\s*\|?\s*$',
        marker_m.group(1),
        re.MULTILINE
    ):
        cost   = m.group(1).strip()
        effect = md_to_html_inline(m.group(2).strip())
        rows.append({"cost": cost, "effect": effect})
    return rows


def parse_special_abilities(text: str) -> list:
    """
    Parse the bullet list of special abilities.

    Format:
        * **Cleave**: When this foe deals damage, also deal 1 damage...
        * **Entrap**: Add a "Trapped" hazard...
    """
    marker_m = re.search(
        r'or invent your own:\n\n(.*?)To augment a combat interlude',
        text, re.DOTALL
    )
    if not marker_m:
        return []

    abilities = []
    for m in re.finditer(
        r'^\s*\*\s+\*\*(.+?)\*\*:\s*(.+?)(?=\n\s*\*\s+\*\*|\Z)',
        marker_m.group(1),
        re.MULTILINE | re.DOTALL
    ):
        name = m.group(1).strip()
        desc = " ".join(m.group(2).split())  # collapse whitespace
        desc = md_to_html_inline(desc)
        abilities.append({"name": name, "desc": desc})
    return abilities


def parse_combat(text: str) -> CombatData:
    augmentations = parse_augmentation_table(text)
    abilities     = parse_special_abilities(text)
    return CombatData(augmentations=augmentations, abilities=abilities)


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
    font-size: 10px;
    color: var(--ink);
    padding: 1.5rem;
  }

  .page {
    background: white;
    width: 8.5in;
    min-height: 11in;
    margin: 0 auto;
    padding: 0.38in 0.42in 0.35in;
    box-shadow: 0 4px 24px rgba(0,0,0,0.18);
    border-radius: 2px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr auto;
    gap: 0 0.26in;
  }

  .header {
    grid-column: 1 / -1;
    border-bottom: 2.5px solid var(--ink);
    padding-bottom: 0.08in;
    margin-bottom: 0.13in;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
  }
  .guide-badge {
    display: inline-block;
    background: var(--danger);
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
    margin-top: 0.1in;
    padding-top: 5px;
    font-size: 7.5px;
    color: var(--rule);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    display: flex;
    justify-content: space-between;
  }

  .section { margin-bottom: 0.11in; }

  .section-head {
    font-size: 7px;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    color: white;
    background: var(--ink);
    padding: 3px 7px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .section-head.danger  { background: var(--danger); }
  .section-head.accent  { background: var(--accent); }
  .section-head.green   { background: var(--green); }
  .section-head.warm    { background: var(--warm); }

  .rule-note {
    font-size: 8.5px;
    color: var(--rule);
    line-height: 1.5;
    margin-bottom: 4px;
  }
  .rule-note strong { color: var(--ink); }

  .checklist { list-style: none; padding: 0; }
  .checklist li {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    padding: 2px 0;
    border-bottom: 0.5px solid var(--mid);
    font-size: 9px;
    line-height: 1.4;
  }
  .checklist li:last-child { border-bottom: none; }
  .cb { width: 11px; height: 11px; border: 1.5px solid var(--ink); flex-shrink: 0; margin-top: 1px; }

  .foe-template {
    border: 1.5px solid var(--ink);
    background: var(--light);
    padding: 6px 8px;
    margin-bottom: 6px;
    font-size: 8.5px;
  }
  .foe-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
  .foe-field { display: flex; flex-direction: column; gap: 1px; }
  .foe-field-label { font-size: 6.5px; text-transform: uppercase; letter-spacing: 0.15em; color: var(--rule); }
  .foe-field-line { border-bottom: 1.5px solid var(--ink); width: 90px; height: 16px; }
  .foe-field-line.long { width: 130px; }
  .foe-might-opts { display: flex; gap: 5px; align-items: center; }
  .foe-might-opt { border: 1.5px solid var(--mid); border-radius: 2px; padding: 1px 5px; font-size: 8px; }
  .foe-stamina-bar { display: flex; align-items: center; gap: 4px; margin-bottom: 2px; }
  .foe-stamina-label { font-size: 6.5px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--rule); flex-shrink: 0; }
  .stamina-pips { display: flex; gap: 2px; }
  .pip { width: 12px; height: 12px; border: 1.5px solid var(--ink); border-radius: 1px; flex-shrink: 0; }
  .pip.filled { background: var(--ink); }
  .pip.plus { border-style: dashed; border-color: var(--rule); }
  .ability-label { font-size: 6.5px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--rule); margin-bottom: 1px; }
  .foe-ability-line { border-bottom: 1px solid var(--mid); height: 15px; margin-top: 3px; width: 100%; }

  .sp-table { width: 100%; border-collapse: collapse; font-size: 8.5px; margin-bottom: 5px; }
  .sp-table th {
    font-size: 7px; text-transform: uppercase; letter-spacing: 0.13em;
    color: var(--rule); border-bottom: 1px solid var(--mid);
    padding: 2px 4px; text-align: left; font-weight: 700;
  }
  .sp-table td { padding: 2px 4px; border-bottom: 0.5px dotted var(--mid); vertical-align: middle; }
  .sp-table tr:last-child td { border-bottom: none; }
  .sp-table tbody tr:nth-child(even) td {
    background: var(--light);
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .sp-table tbody tr:nth-child(odd) td { background: white; }
  .sp-cost { font-weight: 700; color: var(--accent); text-align: center; width: 28px; }

  .ability-list { list-style: none; padding: 0; }
  .ability-item {
    display: flex; gap: 5px; padding: 2px 0;
    border-bottom: 0.5px dotted var(--mid); font-size: 8.5px; line-height: 1.4;
  }
  .ability-item:last-child { border-bottom: none; }
  .ability-name { font-weight: 700; flex-shrink: 0; min-width: 64px; }

  .turn-block { border-left: 3px solid var(--mid); padding-left: 8px; margin-bottom: 7px; }
  .turn-block.players { border-left-color: var(--green); }
  .turn-block.gm      { border-left-color: var(--danger); }
  .turn-title { font-size: 7.5px; text-transform: uppercase; letter-spacing: 0.18em; color: var(--rule); margin-bottom: 4px; }
  .turn-title strong { color: var(--ink); }
  .turn-steps { list-style: none; padding: 0; }
  .turn-step { display: flex; gap: 5px; padding: 2px 0; font-size: 8.5px; line-height: 1.4; border-bottom: 0.5px dotted var(--mid); }
  .turn-step:last-child { border-bottom: none; }
  .step-num { font-weight: 700; color: var(--rule); flex-shrink: 0; min-width: 14px; text-align: right; }

  .close-items { list-style: none; padding: 0; }
  .close-item { display: flex; align-items: flex-start; gap: 6px; padding: 2.5px 0; font-size: 8.5px; line-height: 1.4; border-bottom: 0.5px solid var(--mid); }
  .close-item:last-child { border-bottom: none; }

  .math-box { border: 1px solid var(--mid); background: var(--light); padding: 6px 8px; margin-bottom: 6px; font-size: 8.5px; }
  .math-formula { font-family: 'Space Mono', monospace; font-size: 9px; font-weight: 700; border: 1px solid var(--mid); padding: 3px 6px; background: white; display: inline-block; margin: 4px 0; }
  .math-table { width: 100%; border-collapse: collapse; font-size: 8px; margin-top: 4px; }
  .math-table th { font-size: 6.5px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--rule); border-bottom: 1px solid var(--mid); padding: 1px 4px; text-align: left; }
  .math-table td { padding: 1.5px 4px; border-bottom: 0.5px dotted var(--mid); }
  .math-table tr:last-child td { border-bottom: none; }
  .math-cost { font-weight: 700; color: var(--ink); text-align: right; }
"""


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def cb() -> str:
    return '<span class="cb"></span>'

def section_head(label: str, color: str = "") -> str:
    cls = ("section-head " + color).strip()
    return f'      <div class="{cls}">{label}</div>\n'

def rule_note(text: str, style: str = "") -> str:
    s = f' style="{style}"' if style else ""
    return f'      <p class="rule-note"{s}>{text}</p>\n'

def checklist_item(text: str) -> str:
    return f'        <li>{cb()}<span>{text}</span></li>\n'


# ---------------------------------------------------------------------------
# Hardcoded content
# ---------------------------------------------------------------------------

SETUP_ITEMS = [
    "Shuffle the GM <strong>Combat Move Deck</strong> (remove cards not intended for current chapter)",
    "Ready a stack of blank index cards for foes &amp; hazards",
    "Default foe count: <strong># of PCs &minus; 1</strong>",
]

CLOSE_ITEMS = [
    ("cb", "All players may use <strong>Take a Breather</strong>, flipping Str"),
    ("cb", "Swap Combat GM Move Deck for <strong>Dramatic Action GM Move Deck</strong>"),
    ("cb", "If <em>any</em> PCs survived: add <strong>1 &#10004; token</strong> to a progress bar (players&rsquo; choice)"),
    ("cb", "If <em>all</em> PCs survived: add <strong>1 more &#10004; token</strong>"),
    ("cb", "<strong>Loot:</strong> let players propose searching the battlefield. If no ideas, write &ldquo;What we found on [foe]&rdquo; on a blank card &mdash; it can be spent as Pack when the fiction supports it"),
]


# ---------------------------------------------------------------------------
# Column renderers
# ---------------------------------------------------------------------------

def render_left_column(data: CombatData) -> str:
    setup_items = "".join(checklist_item(i) for i in SETUP_ITEMS)

    # Augmentation table rows
    aug_rows = "".join(
        f'          <tr><td class="sp-cost">{r["cost"]}</td><td>{r["effect"]}</td></tr>\n'
        for r in data.augmentations
    )

    # Special abilities
    ability_items = "".join(
        f'        <li class="ability-item"><span class="ability-name">{a["name"]}</span><span>{a["desc"]}</span></li>\n'
        for a in data.abilities
    )

    return (
        f'  <div class="col-left">\n\n'

        # Setup
        f'    <div class="section">\n'
        f'{section_head("Setup", "danger")}'
        f'      <ul class="checklist" style="margin-bottom:6px;">\n{setup_items}      </ul>\n'
        f'{rule_note("For each foe or hazard, fill out a card:", "margin-bottom:5px;")}'
        f'      <div class="foe-template">\n'
        f'        <div class="foe-row">\n'
        f'          <div class="foe-field"><div class="foe-field-label">Name</div><div class="foe-field-line long"></div></div>\n'
        f'          <div class="foe-field"><div class="foe-field-label">Might</div>'
        f'<div class="foe-might-opts"><span class="foe-might-opt">d4</span><span class="foe-might-opt">d6</span><span class="foe-might-opt">d10</span></div></div>\n'
        f'        </div>\n'
        f'        <div class="foe-stamina-bar">\n'
        f'          <span class="foe-stamina-label">Stamina (default 5)</span>\n'
        f'          <div class="stamina-pips">\n'
        f'            <div class="pip filled"></div><div class="pip filled"></div><div class="pip filled"></div>'
        f'<div class="pip filled"></div><div class="pip filled"></div>'
        f'<div class="pip plus"></div><div class="pip plus"></div><div class="pip plus"></div>'
        f'<div class="pip plus"></div><div class="pip plus"></div>\n'
        f'          </div>\n'
        f'        </div>\n'
        f'        <div class="ability-label">Special Ability (optional)</div>\n'
        f'        <div class="foe-ability-line"></div>\n'
        f'      </div>\n'
        f'{rule_note("Place cards <strong>center table</strong> (threat not endangering a PC) or <strong>adjacent to a player</strong> (endangered). Follow the fiction.", "margin-bottom:4px;")}'
        f'{rule_note("Paint the combat scene. Describe all threats. <strong>Combat is now active.</strong>")}'
        f'    </div>\n\n'

        # Augmentation table
        f'    <div class="section">\n'
        f'{section_head("Spend Shadow Points to Augment", "accent")}'
        f'      <table class="sp-table">\n'
        f'        <thead><tr><th>Shadow Points</th><th>Augmentation</th></tr></thead>\n'
        f'        <tbody>\n{aug_rows}        </tbody>\n'
        f'      </table>\n'
        f'    </div>\n\n'

        # Special abilities
        f'    <div class="section">\n'
        f'{section_head("Special Abilities")}'
        f'      <ul class="ability-list">\n{ability_items}      </ul>\n'
        f'    </div>\n\n'

        # Encounter math
        f'    <div class="section">\n'
        f'{section_head("Encounter Balance")}'
        f'      <div class="math-box">\n'
        f'        <p class="rule-note" style="margin-bottom:3px;"><strong>Party Power</strong></p>\n'
        f'        <div class="math-formula">10 &times; (# of PCs) + (total XP held)</div>\n'
        f'        <table class="math-table" style="margin-top:5px;">\n'
        f'          <thead><tr><th>Allocation</th><th class="math-cost" style="text-align:right;">PP cost</th></tr></thead>\n'
        f'          <tbody>\n'
        f'            <tr><td>1 Stamina point</td><td class="math-cost">1</td></tr>\n'
        f'            <tr><td>Weapon: d6 damage</td><td class="math-cost">3</td></tr>\n'
        f'            <tr><td>1 Armor square</td><td class="math-cost">3</td></tr>\n'
        f'          </tbody>\n'
        f'        </table>\n'
        f'        <p class="rule-note" style="margin-top:4px;">Divide PP by avg Stamina per foe to estimate foe count. Then spend Shadow Points to augment.</p>\n'
        f'      </div>\n'
        f'    </div>\n\n'

        f'  </div><!-- end col-left -->\n'
    )


def render_right_column(data: CombatData) -> str:
    close_items = "".join(
        f'        <li class="close-item">{cb()}<span>{text}</span></li>\n'
        for _, text in CLOSE_ITEMS
    )

    return (
        f'  <div class="col-right">\n\n'

        # Turn structure
        f'    <div class="section">\n'
        f'{section_head("Turn Structure &mdash; Each Round", "danger")}'
        f'      <div class="turn-block players">\n'
        f'        <div class="turn-title"><strong>Players</strong> &mdash; choose order among themselves</div>\n'
        f'        <ul class="turn-steps">\n'
        f'          <li class="turn-step"><span class="step-num">1</span><span>Each player takes a turn. May make <strong>1 move</strong>, or <strong>2 moves</strong> if one is tagged <em>FAST</em></span></li>\n'
        f'          <li class="turn-step"><span class="step-num">2</span><span>If <strong>endangered</strong> by a threat: either suffer its Might at end of turn, or use <em>Defy Danger</em> as one of your moves. &#10004;&#10004; on Defy Danger = move threat back to center</span></li>\n'
        f'          <li class="turn-step"><span class="step-num">3</span><span>A single <em>Defy Danger</em> applies to <strong>all</strong> threats currently endangering that PC</span></li>\n'
        f'          <li class="turn-step"><span class="step-num">4</span><span>On an &#10007;: GM draws 2 Combat Move cards, chooses 1 to invoke</span></li>\n'
        f'        </ul>\n'
        f'      </div>\n\n'
        f'      <div class="turn-block gm">\n'
        f'        <div class="turn-title"><strong>GM</strong> &mdash; after all players have acted</div>\n'
        f'        <ul class="turn-steps">\n'
        f'          <li class="turn-step"><span class="step-num">1</span><span>Apply the Might of <strong>one</strong> endangering threat (or trigger a special ability if none are endangering)</span></li>\n'
        f'          <li class="turn-step"><span class="step-num">2</span><span>Move up to <strong>half</strong> (rounded up) of all threats to endanger PCs. Describe each new threat</span></li>\n'
        f'          <li class="turn-step"><span class="step-num">3</span><span>Optionally declare foes <strong>fleeing</strong> &mdash; move their cards to GM Sheet. If players pursue before round ends, Pursuit Interlude begins</span></li>\n'
        f'        </ul>\n'
        f'      </div>\n\n'
        f'{rule_note("Rounds continue until all foes <em>or</em> all PCs are defeated, or a Pursuit Interlude is triggered.")}'
        f'    </div>\n\n'

        # Closing combat
        f'    <div class="section">\n'
        f'{section_head("Closing Combat", "green")}'
        f'      <ul class="close-items">\n{close_items}      </ul>\n'
        f'    </div>\n\n'

        f'  </div><!-- end col-right -->\n'
    )


# ---------------------------------------------------------------------------
# Full page renderer
# ---------------------------------------------------------------------------

def render_sheet(data: CombatData) -> str:
    return (
        f'<!DOCTYPE html>\n'
        f'<html lang="en">\n'
        f'<head>\n'
        f'<meta charset="UTF-8">\n'
        f'<title>1kFA &mdash; Combat Interlude Reference</title>\n'
        f'<style>\n{CSS}\n</style>\n'
        f'</head>\n'
        f'<body>\n'
        f'<div class="page">\n\n'
        f'  <div class="header">\n'
        f'    <div class="header-left">\n'
        f'      <div class="guide-badge">GM Guide</div>\n'
        f'      <h1>Combat Interlude</h1>\n'
        f'    </div>\n'
        f'    <div class="header-right">\n'
        f'      A Thousand Faces of Adventure<br>\n'
        f'      1kfa.com\n'
        f'    </div>\n'
        f'  </div>\n\n'
        f'{render_left_column(data)}\n'
        f'{render_right_column(data)}\n'
        f'  <div class="footer">\n'
        f'    <span>1kfa &middot; GM Guide &middot; Combat Interlude</span>\n'
        f'    <span>On &#10007; during Dramatic Action: GM can start a Combat Interlude via the Pivot or Escalate the Danger moves</span>\n'
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
        description="Generate the 1kFA Combat Interlude reference sheet from mod_guide_gm.md"
    )
    parser.add_argument("guide", help="Path to mod_guide_gm.md")
    parser.add_argument(
        "--output-dir", default=".",
        help="Directory for output HTML file (default: current directory)"
    )
    args = parser.parse_args()

    if not os.path.exists(args.guide):
        print(f"Error: {args.guide} not found.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Parsing {args.guide}...")
    with open(args.guide, encoding="utf-8") as f:
        text = f.read()

    data = parse_combat(text)

    print(f"  augmentation rows: {len(data.augmentations)}")
    for r in data.augmentations:
        print(f"    {r['cost']:>2}  {r['effect']}")
    print(f"  special abilities: {len(data.abilities)}")
    for a in data.abilities:
        print(f"    {a['name']}")

    html = render_sheet(data)
    filename = "sheet_combat_interlude.html"
    out_path = os.path.join(args.output_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
