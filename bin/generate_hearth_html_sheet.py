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


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class HearthData:
    at_home_read_aloud: str         # "What makes your character feel most at home..."
    at_home_followup: str           # "Follow up questions might be needed..."
    choose_hearth_read_aloud: str   # "This is a game where you all play together..."
    hearth_examples_read_aloud: str # "The Hearth can be a specific person..."
    hearth_options: list            # ["Specific People", "Food", ...]
    make_sure_note: str             # "With follow up questions, make sure everyone agrees..."
    must_be_separated_note: str     # "An important aspect of The Hearth is that it must..."
    risk_life_read_aloud: str       # "Briefly, why would your character risk..."


# ---------------------------------------------------------------------------
# Parser helpers
# ---------------------------------------------------------------------------

def md_to_html_inline(text: str) -> str:
    """Convert inline markdown bold/italic to HTML."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text


def extract_first_blockquote(text: str) -> str:
    """
    Extract the first contiguous blockquote block from text.
    Returns HTML-ready string.
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
        stripped = md_to_html_inline(stripped)
        if stripped == "":
            if current:
                paragraphs.append(" ".join(current))
                current = []
        else:
            current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))

    return "<br><br>\n        ".join(paragraphs)


def extract_all_blockquotes(text: str) -> list:
    """Extract all contiguous blockquote blocks from text in order."""
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
                    stripped = md_to_html_inline(stripped)
                    if stripped == "":
                        if para:
                            paragraphs.append(" ".join(para))
                            para = []
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
            stripped = md_to_html_inline(stripped)
            if stripped == "":
                if para:
                    paragraphs.append(" ".join(para))
                    para = []
            else:
                para.append(stripped)
        if para:
            paragraphs.append(" ".join(para))
        q = "<br><br>\n        ".join(paragraphs)
        if q:
            results.append(q)

    return results


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
        at_home_followup = md_to_html_inline(at_home_followup)

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
    make_sure_note = md_to_html_inline(make_sure_m.group(1).strip()) if make_sure_m else ""

    # "An important aspect of The Hearth is that it must be something..."
    must_be_m = re.search(
        r'(An important aspect of The Hearth is that it must be something[^.]+\.[^.]+\.)',
        section, re.DOTALL
    )
    must_be_separated_note = ""
    if must_be_m:
        must_be_separated_note = " ".join(must_be_m.group(1).split()).strip()
        must_be_separated_note = md_to_html_inline(must_be_separated_note)

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
# Hardcoded content not in the guide
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
        f'{rule_note(data.at_home_followup, "margin-bottom:6px;")}'
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
        f'{rule_note(data.make_sure_note)}'
        f'    </div>\n\n'

        # Record The Hearth + Step 3
        f'    <div class="section">\n'
        f'{section_head("Record The Hearth", "green")}'
        f'{rule_note("Record on the GM Sheet.", "margin-bottom:4px;")}'
        f'{rule_note(data.must_be_separated_note, "margin-bottom:6px;")}'

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
    args = parser.parse_args()

    if not os.path.exists(args.guide):
        print(f"Error: {args.guide} not found.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Parsing {args.guide}...")
    with open(args.guide, encoding="utf-8") as f:
        text = f.read()

    data = parse_hearth(text)

    print(f"  at-home read-aloud:   {len(data.at_home_read_aloud)} chars")
    print(f"  at-home followup:     {data.at_home_followup[:60]!r}...")
    print(f"  choose-hearth r/a:    {len(data.choose_hearth_read_aloud)} chars")
    print(f"  examples read-aloud:  {len(data.hearth_examples_read_aloud)} chars")
    print(f"  hearth options:       {data.hearth_options}")
    print(f"  make-sure note:       {data.make_sure_note[:60]!r}...")
    print(f"  must-be-separated:    {data.must_be_separated_note[:60]!r}...")
    print(f"  risk-life read-aloud: {len(data.risk_life_read_aloud)} chars")

    html = render_sheet(data)
    filename = "sheet_gm_guide_hearth.html"
    out_path = os.path.join(args.output_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
