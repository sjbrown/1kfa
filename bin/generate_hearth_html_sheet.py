#!/usr/bin/env python3
"""
generate_hearth_html_sheet.py
==============================
Parses mod_guide_gm.md and generates the GM Guide · Gather Around the Hearth
printable reference sheet.

Usage:
    python3 generate_hearth_html_sheet.py path/to/mod_guide_gm.md [--output-dir ./sheets]

Output:
    sheet_gm_guide_hearth.html
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from parse_quickstart_data import (
    extract_all_blockquotes,
    extract_blockquote,
    parse_inline_md,
    spans_to_plain,
)
from render_sheet_html import (
    CSS_BASE,
    cb,
    checklist_item,
    read_aloud,
    rule_note,
    section_head,
    spans_to_html,
    export_pdf,
)



# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class HearthData:
    at_home_read_aloud: str         # "What makes your character feel most at home..."
    at_home_followup: list          # span list
    choose_hearth_read_aloud: str   # "This is a game where you all play together..."
    hearth_examples_read_aloud: str # "The Hearth can be a specific person..."
    hearth_options: list            # ["Specific People", "Food", ...]
    make_sure_note: list            # span list
    must_be_separated_note: list    # span list
    risk_life_read_aloud: str       # "Briefly, why would your character risk..."


# ---------------------------------------------------------------------------
# Parser helpers
# ---------------------------------------------------------------------------

def parse_hearth_options(text: str) -> list:
    """Parse the bullet list of Hearth options."""
    return [
        m.group(1).strip()
        for m in re.finditer(r'^\s*\*\s+(.+)$', text, re.MULTILINE)
        if m.group(1).strip()
    ]


def parse_hearth(text: str) -> HearthData:
    """Parse the # Gather Around The Hearth section from mod_guide_gm.md."""
    section_m = re.search(
        r'^# Gather Around The Hearth\s*(.*?)(?=\n## Paint|\n# |\Z)',
        text, re.DOTALL | re.MULTILINE
    )
    if not section_m:
        sys.exit("ERROR: Could not find '# Gather Around The Hearth' section in guide.")
    section = section_m.group(1)

    # All blockquotes in order
    quotes = extract_all_blockquotes(section)

    # Quote 1: "What makes your character feel most at home..."
    at_home_read_aloud = quotes[0] if len(quotes) > 0 else ""

    # Prose after quote 1: "Follow up questions might be needed..."
    after_q1_m = re.search(
        r'Follow up questions might be needed\.(.*?)Then read aloud:',
        section, re.DOTALL
    )
    at_home_followup = ""
    if after_q1_m:
        at_home_followup = " ".join(after_q1_m.group(1).strip().splitlines()).strip()
        at_home_followup = parse_inline_md(at_home_followup)

    # Quote 2: "This is a game where you all play together..."
    choose_hearth_read_aloud = quotes[1] if len(quotes) > 1 else ""

    # Quote 3: "The Hearth can be a specific person..." (the examples)
    hearth_examples_read_aloud = quotes[2] if len(quotes) > 2 else ""

    # Quote 4: "Briefly, why would your character risk their life..."
    risk_life_read_aloud = quotes[3] if len(quotes) > 3 else ""

    # "With follow up questions, make sure everyone agrees..."
    make_sure_m = re.search(
        r'(With follow up questions, make sure everyone agrees[^.]+\.)',
        section
    )
    make_sure_note = parse_inline_md(make_sure_m.group(1).strip()) if make_sure_m else []

    # "An important aspect of The Hearth is that it must be something..."
    must_be_m = re.search(
        r'(An important aspect of The Hearth is that it must be something[^.]+\.[^.]+\.)',
        section, re.DOTALL
    )
    must_be_separated_note = ""
    if must_be_m:
        must_be_separated_note = " ".join(must_be_m.group(1).split()).strip()
        must_be_separated_note = parse_inline_md(must_be_separated_note)

    # Hearth options — bullet list between quotes 2 and 3
    # Find the section between "By consensus" and the Lift From Touchstones line
    options_m = re.search(
        r'By consensus.*?chooses one of these options:(.*?)The \*\*Lift From Touchstones\*\*',
        section, re.DOTALL
    )
    hearth_options = []
    if options_m:
        hearth_options = parse_hearth_options(options_m.group(1))

    # Fallback
    if not hearth_options:
        hearth_options = [
            "Specific People",
            "Food",
            "Song",
            "Environmental feature",
            "Ritual or festival",
            "Group activity",
        ]

    return HearthData(
        at_home_read_aloud=at_home_read_aloud,
        at_home_followup=at_home_followup,
        choose_hearth_read_aloud=choose_hearth_read_aloud,
        hearth_examples_read_aloud=hearth_examples_read_aloud,
        hearth_options=hearth_options,
        make_sure_note=make_sure_note,
        must_be_separated_note=must_be_separated_note,
        risk_life_read_aloud=risk_life_read_aloud,
    )


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = CSS_BASE + """
  .hearth-options {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3px 10px;
    margin-bottom: 7px;
  }
  .hearth-option {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 9.5px;
    padding: 2px 0;
  }
  .hearth-circle {
    width: 14px;
    height: 14px;
    border: 1.5px solid var(--ink);
    border-radius: 50%;
    flex-shrink: 0;
  }

  .step-block {
    border-left: 3px solid var(--mid);
    padding-left: 8px;
    margin-bottom: 8px;
  }
  .step-block.accent { border-left-color: var(--accent); }
  .step-block.green  { border-left-color: var(--green); }

  .step-title {
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--rule);
    margin-bottom: 4px;
  }
  .step-title strong { color: var(--ink); }

  .pc-table { width: 100%; border-collapse: collapse; margin-bottom: 6px; }
  .pc-table th {
    font-size: 7.5px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--rule);
    border-bottom: 1px solid var(--mid);
    padding: 2px 4px;
    text-align: left;
    font-weight: 700;
  }
  .pc-table td {
    border-bottom: 0.5px solid var(--mid);
    padding: 2px 4px;
    height: 22px;
  }

  .token-prompt {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 9px;
    color: var(--rule);
    padding: 4px 6px;
    border: 1px solid var(--mid);
    margin-bottom: 6px;
  }
  .token-icon {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
  }

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

COMPONENTS = [
    "One Deckahedron per player, shuffled",
    "Blessing card deck &mdash; shuffled, face-down",
    "Wound card deck &mdash; shuffled, face-down; place a wound token beside it to distinguish the two decks",
    "GM Move Deck (Dramatic Action) &mdash; shuffled, at hand",
    "Scene sheet",
    "Token supply accessible at center of table: progress &#10004;, XP, Harm, Exhaustion, Shadow Points, Journey Points, green tokens, red tokens",
    "Blank index cards (for foes during combat)",
]


# ---------------------------------------------------------------------------
# Column renderers
# ---------------------------------------------------------------------------

def render_left_column(data: HearthData) -> str:
    components_html = "".join(checklist_item(c) for c in COMPONENTS)

    hearth_options_html = "".join(
        f'          <div class="hearth-option"><span class="hearth-circle"></span><span>{opt}</span></div>\n'
        for opt in data.hearth_options
    )

    return (
        f'  <div class="col-left">\n\n'

        # Ready the Table
        f'    <div class="section">\n'
        f'{section_head("Ready the Table", "warm")}'
        f'      <ul class="checklist">\n{components_html}      </ul>\n'
        f'    </div>\n\n'

        # Gather Around the Hearth
        f'    <div class="section">\n'
        f'{section_head("Gather Around the Hearth", "accent")}'

        # Step 1
        f'      <div class="step-block accent">\n'
        f'        <div class="step-title"><strong>1 &middot; What Makes You Feel At Home?</strong></div>\n'
        f'{read_aloud(data.at_home_read_aloud, "margin-bottom:6px;")}'
        f'{rule_note(spans_to_html(data.at_home_followup), "margin-bottom:6px;")}'
        f'        <table class="pc-table">\n'
        f'          <thead><tr><th>PC</th><th>What makes them feel at home</th></tr></thead>\n'
        f'          <tbody>\n'
        f'            <tr><td></td><td></td></tr>\n'
        f'            <tr><td></td><td></td></tr>\n'
        f'            <tr><td></td><td></td></tr>\n'
        f'            <tr><td></td><td></td></tr>\n'
        f'            <tr><td></td><td></td></tr>\n'
        f'          </tbody>\n'
        f'        </table>\n'
        f'      </div>\n\n'

        # Step 2
        f'      <div class="step-block accent">\n'
        f'        <div class="step-title"><strong>2 &middot; Choose The Hearth</strong></div>\n'
        f'{read_aloud(data.choose_hearth_read_aloud, "margin-bottom:6px;")}'
        f'{rule_note("By consensus, choose one:", "margin-bottom:5px;")}'
        f'        <div class="hearth-options">\n{hearth_options_html}        </div>\n'
        f'      </div>\n\n'

        f'    </div>\n\n'
        f'  </div><!-- end col-left -->\n'
    )


def render_right_column(data: HearthData) -> str:
    return (
        f'  <div class="col-right">\n\n'

        # Hearth examples
        f'    <div class="section">\n'
        f'{section_head("The Hearth &mdash; Read Aloud Examples", "accent")}'
        f'{read_aloud(data.hearth_examples_read_aloud, "margin-bottom:7px;")}'
        f'{rule_note(spans_to_html(data.make_sure_note))}'
        f'    </div>\n\n'

        # Record The Hearth + Step 3
        f'    <div class="section">\n'
        f'{section_head("Record The Hearth", "green")}'
        f'{rule_note("Record on the GM Sheet.", "margin-bottom:4px;")}'
        f'{rule_note(spans_to_html(data.must_be_separated_note), "margin-bottom:6px;")}'

        f'      <div class="step-block green">\n'
        f'        <div class="step-title"><strong>3 &middot; Why Would You Risk Your Life For The Hearth?</strong></div>\n'
        f'{read_aloud(data.risk_life_read_aloud, "margin-bottom:5px;")}'
        f'{rule_note("Each player writes their answer on their character sheet. As they answer, move one <strong>Shadow Point</strong> onto the GM Sheet.", "margin-bottom:5px;")}'
        f'        <div class="token-prompt">\n'
        f'          <span class="token-icon"></span>\n'
        f'          <span>Move 1 Shadow Point to GM Sheet after each of the players&rsquo; answers</span>\n'
        f'        </div>\n'
        f'      </div>\n'
        f'    </div>\n\n'

        # Handoff
        f'    <div class="section">\n'
        f'      <div class="handoff">\n'
        f'        <span class="handoff-arrow">&#8594;</span>\n'
        f'        <span>\n'
        f'          <strong class="handoff-label">The Game Begins</strong>\n'
        f'          Paint the Opening Image, then consult the Scene Sheet and Chapter 1 procedures.\n'
        f'        </span>\n'
        f'      </div>\n'
        f'    </div>\n\n'

        f'  </div><!-- end col-right -->\n'
    )


# ---------------------------------------------------------------------------
# Full page renderer
# ---------------------------------------------------------------------------

def render_sheet(data: HearthData) -> str:
    return (
        f'<!DOCTYPE html>\n'
        f'<html lang="en">\n'
        f'<head>\n'
        f'<meta charset="UTF-8">\n'
        f'<title>1kFA &mdash; GM Guide &middot; Gather Around the Hearth</title>\n'
        f'<style>\n{CSS}\n</style>\n'
        f'</head>\n'
        f'<body>\n'
        f'<div class="page">\n\n'
        f'  <div class="header">\n'
        f'    <div class="header-left">\n'
        f'      <div class="guide-badge">GM Guide</div>\n'
        f'      <h1>Gather Around the Hearth</h1>\n'
        f'    </div>\n'
        f'    <div class="header-right">\n'
        f'      A Thousand Faces of Adventure<br>\n'
        f'      1kfa.com\n'
        f'    </div>\n'
        f'  </div>\n\n'
        f'{render_left_column(data)}\n'
        f'{render_right_column(data)}\n'
        f'  <div class="footer">\n'
        f'    <span>1kfa &middot; GM Guide &middot; Gather Around the Hearth</span>\n'
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
        description="Generate the 1kFA GM Guide Hearth sheet from mod_guide_gm.md"
    )
    parser.add_argument("guide", help="Path to mod_guide_gm.md")
    parser.add_argument(
        "--output-dir", default=".",
        help="Directory for the output HTML file (default: current directory)"
    )
    parser.add_argument(
        "--export-pdf", action="store_true",
        help="Also render the HTML to PDF using headless Chromium"
    )
    args = parser.parse_args()

    if not os.path.exists(args.guide):
        print(f"Error: {args.guide} not found.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Parsing {args.guide}...")
    with open(args.guide, encoding="utf-8") as f:
        text = f.read()

    data = parse_hearth(text)

    print(f"  at-home read-aloud:   {len(data.at_home_read_aloud)} paragraphs")
    print(f"  at-home followup:     {spans_to_plain(data.at_home_followup)[:60]!r}...")
    print(f"  choose-hearth r/a:    {len(data.choose_hearth_read_aloud)} paragraphs")
    print(f"  examples read-aloud:  {len(data.hearth_examples_read_aloud)} paragraphs")
    print(f"  hearth options:       {data.hearth_options}")
    print(f"  make-sure note:       {spans_to_plain(data.make_sure_note)[:60]!r}...")
    print(f"  must-be-separated:    {spans_to_plain(data.must_be_separated_note)[:60]!r}...")
    print(f"  risk-life read-aloud: {len(data.risk_life_read_aloud)} paragraphs")

    html = render_sheet(data)
    filename = "sheet_gm_guide_hearth.html"
    out_path = os.path.join(args.output_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  -> {out_path}")

    if args.export_pdf:
        pdf_path = out_path.replace(".html", ".pdf")
        print(f"  rendering PDF...")
        export_pdf(out_path, pdf_path)
        print(f"  -> {pdf_path}")



if __name__ == "__main__":
    main()
