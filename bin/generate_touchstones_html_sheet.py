#!/usr/bin/env python3
"""
generate_touchstones_html_sheet.py
===================================
Parses mod_guide_table.md and generates the Table Guide · Universe Creation
printable reference sheet.

Usage:
    python3 generate_touchstones_html_sheet.py path/to/mod_guide_table.md [--output-dir ./sheets]

Output:
    sheet_table_guide_universe_creation.html
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
class UniverseCreationData:
    campaign_options: list          # [{"name": str, "desc": str}, ...]
    intro_read_aloud: str           # blockquote before Step 1
    step_a_read_aloud: str          # Step 1: Brainstorm Titles blockquote
    step_b_read_aloud: str          # Step 2: Narrow the List blockquote
    step_b_notes: list              # non-blockquote guidance after Step 2 quote
    step_c_read_aloud: str          # Step 3: Set Expectations blockquote
    step_c_note: str                # prose note after Step 3 questions
    finally_read_aloud: str         # closing "Finally, who will you be" blockquote


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def extract_blockquote(text: str) -> str:
    """
    Extract the first contiguous blockquote (> lines) from text.
    Strips '> ' prefixes, resolves line continuations, returns HTML-ready string.
    Blank '>' lines become paragraph breaks (<br><br>).
    """
    lines = []
    in_quote = False
    for line in text.splitlines():
        m = re.match(r'^>\s?(.*)', line)
        if m:
            in_quote = True
            lines.append(m.group(1))
        elif in_quote:
            break  # stop at first non-quote line after we've started

    if not lines:
        return ""

    paragraphs = []
    current = []
    for line in lines:
        stripped = line.rstrip('\\').strip()
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
    """
    Extract all blockquote blocks from text in order.
    Each contiguous run of '> ' lines is one block.
    """
    results = []
    current = []
    for line in text.splitlines():
        m = re.match(r'^>\s?(.*)', line)
        if m:
            current.append(m.group(1))
        else:
            if current:
                # Process this block
                paragraphs = []
                para = []
                for l in current:
                    stripped = l.rstrip('\\').strip()
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


def parse_campaign_options(section: str) -> list:
    """
    Parse campaign length options.
    Looks for: - **One-Shot** – A single-session adventure.
    Shortens descriptions to fit the picker widget.
    """
    desc_overrides = {
        "One-Shot":         "Single session",
        "9-Hour Campaign":  "3 sessions",
        "30-Hour Campaign": "10 sessions",
    }
    options = []
    for m in re.finditer(r'-\s+\*\*(.+?)\*\*\s+[–-]+\s+(.+)', section):
        name = m.group(1).strip()
        desc = desc_overrides.get(name, m.group(2).strip().rstrip('.'))
        options.append({"name": name, "desc": desc})
    return options


def parse_universe_creation(text: str) -> UniverseCreationData:
    """Parse the # Universe Creation section from mod_guide_table.md."""

    section_m = re.search(
        r'^# Universe Creation\s*(.*?)(?=\n# |\Z)',
        text, re.DOTALL | re.MULTILINE
    )
    if not section_m:
        sys.exit("ERROR: Could not find '# Universe Creation' section in guide.")
    section = section_m.group(1)

    # Campaign options
    campaign_section_m = re.search(
        r'##\s+1\.\s+Decide on Campaign Length(.*?)(?=\n##|\n#|\Z)',
        section, re.DOTALL
    )
    campaign_options = []
    if campaign_section_m:
        campaign_options = parse_campaign_options(campaign_section_m.group(1))
    if not campaign_options:
        campaign_options = [
            {"name": "One-Shot",         "desc": "Single session"},
            {"name": "9-Hour Campaign",  "desc": "3 sessions"},
            {"name": "30-Hour Campaign", "desc": "10 sessions"},
        ]

    # Establish Touchstones section
    touchstones_m = re.search(
        r'###\s+3\.\s+Establish Touchstones(.*?)(?=\n###|\n##|\n#|\Z)',
        section, re.DOTALL
    )
    intro_read_aloud = ""
    if touchstones_m:
        # Intro blockquote — before Step 1
        pre_step1 = touchstones_m.group(1).split('####')[0]
        intro_read_aloud = extract_blockquote(pre_step1)

    # Step 1: Brainstorm Titles
    step1_m = re.search(
        r'####\s+Step 1[:\.]?\s+Brainstorm Titles(.*?)(?=####|\Z)',
        section, re.DOTALL
    )
    step_a_read_aloud = ""
    if step1_m:
        step_a_read_aloud = extract_blockquote(step1_m.group(1))

    # Step 2: Narrow the List
    step2_m = re.search(
        r'####\s+Step 2[:\.]?\s+Narrow the List(.*?)(?=####|\Z)',
        section, re.DOTALL
    )
    step_b_read_aloud = ""
    step_b_notes = []
    if step2_m:
        step2_text = step2_m.group(1)
        # The read-aloud is after "Then say:"
        then_say_m = re.search(r'Then say:(.*?)(?=!\[|---|\n####|\Z)', step2_text, re.DOTALL)
        if then_say_m:
            step_b_read_aloud = extract_blockquote(then_say_m.group(1))
        # Guidance notes
        if re.search(r'machine guns|interstellar', step2_text):
            step_b_notes.append(
                "Watch for: genres incompatible with the rules (machine guns, interstellar travel). "
                "PCs should start <strong>scrappy</strong> — not super-powered. "
                "Titles must be known to everyone at the table."
            )
        if re.search(r'more than three titles are circled', step2_text):
            step_b_notes.append(
                "If more than 3 are circled, <strong>GM selects the final 3</strong>."
            )

    # Step 3: Set Expectations
    step3_m = re.search(
        r'####\s+Step 3[:\.]?\s+Set Expectations(.*?)(?=\n#|\Z)',
        section, re.DOTALL
    )
    step_c_read_aloud = ""
    step_c_note = ""
    finally_read_aloud = ""
    if step3_m:
        step3_text = step3_m.group(1)
        quotes = extract_all_blockquotes(step3_text)
        if quotes:
            step_c_read_aloud = quotes[0]
        if len(quotes) > 1:
            finally_read_aloud = quotes[1]
        note_m = re.search(
            r"These questions don.t need to be answered procedurally[^\n]*",
            step3_text
        )
        if note_m:
            step_c_note = note_m.group(0).strip()

    return UniverseCreationData(
        campaign_options=campaign_options,
        intro_read_aloud=intro_read_aloud,
        step_a_read_aloud=step_a_read_aloud,
        step_b_read_aloud=step_b_read_aloud,
        step_b_notes=step_b_notes,
        step_c_read_aloud=step_c_read_aloud,
        step_c_note=step_c_note,
        finally_read_aloud=finally_read_aloud,
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

  .section { margin-bottom: 0.15in; }

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
  .section-head.accent { background: var(--accent); }
  .section-head.warm   { background: var(--warm); }
  .section-head.green  { background: var(--green); }

  .campaign-picker {
    display: flex;
    border: 1.5px solid var(--ink);
    margin-bottom: 8px;
  }

  .campaign-option {
    flex: 1;
    padding: 7px 6px;
    text-align: center;
    border-right: 1px solid var(--mid);
  }
  .campaign-option:last-child { border-right: none; }

  .campaign-circle {
    width: 18px;
    height: 18px;
    border: 1.5px solid var(--ink);
    border-radius: 50%;
    display: inline-block;
    margin-bottom: 4px;
  }

  .campaign-name {
    font-size: 9.5px;
    font-weight: 700;
    display: block;
    letter-spacing: 0.03em;
  }

  .campaign-desc {
    font-size: 8px;
    color: var(--rule);
    display: block;
    margin-top: 2px;
    line-height: 1.4;
  }

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

  .touchstone-box {
    border: 2px solid var(--ink);
    padding: 8px 10px;
    background: var(--light);
    margin-bottom: 8px;
  }

  .touchstone-label {
    font-size: 7.5px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--rule);
    margin-bottom: 6px;
  }

  .touchstone-entry {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 5px;
  }

  .touchstone-num {
    font-family: 'IM Fell English', serif;
    font-size: 18px;
    color: var(--mid);
    flex-shrink: 0;
    width: 16px;
    text-align: center;
  }

  .touchstone-line {
    flex: 1;
    border-bottom: 1.5px solid var(--ink);
    height: 20px;
  }

  .step-block {
    border-left: 3px solid var(--mid);
    padding-left: 8px;
    margin-bottom: 8px;
  }
  .step-block.accent { border-left-color: var(--accent); }
  .step-block.warm   { border-left-color: var(--warm); }

  .step-title {
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--rule);
    margin-bottom: 5px;
  }
  .step-title strong { color: var(--ink); }

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
    margin-bottom: 6px;
  }
  .rule-note strong { color: var(--ink); }
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
    "GM sheet (matching campaign length)",
    "Character sheets (one per player)",
    "Move cards (remove cards not matching campaign length)",
    "Deckahedron per player (20 cards each)",
    "Token supply (progress, XP, Harm, Exhaustion)",
    "Blank paper &mdash; for the Touchstone List brainstorm",
    "Index cards + pens for everyone",
]


def render_left_column(data: UniverseCreationData) -> str:
    options_html = ""
    for opt in data.campaign_options:
        options_html += (
            f'        <div class="campaign-option">\n'
            f'          <span class="campaign-circle"></span>\n'
            f'          <span class="campaign-name">{opt["name"]}</span>\n'
            f'          <span class="campaign-desc">{opt["desc"]}</span>\n'
            f'        </div>\n'
        )

    items_html = "".join(checklist_item(c) for c in COMPONENTS)

    step_b_notes_html = "".join(
        rule_note(n, "margin-bottom:4px;") for n in data.step_b_notes
    )

    return (
        f'  <div class="col-left">\n\n'
        f'    <div class="section">\n'
        f'{section_head("Decide on Campaign Length")}'
        f'      <div class="campaign-picker">\n{options_html}      </div>\n'
        f'{rule_note("New players: start with <strong>One-Shot</strong>.")}'
        f'    </div>\n\n'
        f'    <div class="section">\n'
        f'{section_head("Gather Game Components", "warm")}'
        f'      <ul class="checklist">\n{items_html}      </ul>\n'
        f'    </div>\n\n'
        f'    <div class="section">\n'
        f'{section_head("Establish Touchstones", "accent")}'
        f'{rule_note("Place blank paper at the center of the table. Read aloud:", "margin-bottom:8px;")}'
        f'{read_aloud(data.intro_read_aloud)}'
        f'      <div class="step-block accent">\n'
        f'        <div class="step-title"><strong>A &middot; Brainstorm Titles</strong></div>\n'
        f'{read_aloud(data.step_a_read_aloud, "margin-bottom:6px;")}'
        f'      </div>\n\n'
        f'      <div class="step-block warm">\n'
        f'        <div class="step-title"><strong>B &middot; Narrow the List</strong></div>\n'
        f'{read_aloud(data.step_b_read_aloud, "margin-bottom:6px;")}'
        f'{step_b_notes_html}'
        f'      </div>\n\n'
        f'    </div>\n\n'
        f'  </div><!-- end col-left -->\n'
    )


def render_right_column(data: UniverseCreationData) -> str:
    step_c_note_html = (
        rule_note(data.step_c_note, "margin-bottom:6px;")
        if data.step_c_note else ""
    )

    return (
        f'  <div class="col-right">\n\n'
        f'    <div class="section">\n'
        f'{section_head("Touchstone List", "green")}'
        f'      <div class="touchstone-box">\n'
        f'        <div class="touchstone-label">Circled titles &mdash; final 3</div>\n'
        f'        <div class="touchstone-entry"><span class="touchstone-num">1</span><span class="touchstone-line"></span></div>\n'
        f'        <div class="touchstone-entry"><span class="touchstone-num">2</span><span class="touchstone-line"></span></div>\n'
        f'        <div class="touchstone-entry"><span class="touchstone-num">3</span><span class="touchstone-line"></span></div>\n'
        f'      </div>\n'
        f'{rule_note("Use the list to ask: <em>&ldquo;Did anyone in [title] do something like this?&rdquo;</em>", "margin-bottom:4px;")}'
        f'{rule_note("Consult it when the table debates whether a PC&rsquo;s action is <strong>uncertain</strong> or <strong>impossible</strong>.")}'
        f'    </div>\n\n'
        f'    <div class="section">\n'
        f'      <div class="section-head accent">\n'
        f'        Establish Touchstones'
        f' <span style="font-weight:normal; opacity:0.7; font-size:7px; letter-spacing:0.1em;">'
        f'&nbsp;&middot; C &middot; SET EXPECTATIONS</span>\n'
        f'      </div>\n'
        f'{read_aloud(data.step_c_read_aloud, "margin-bottom:8px;")}'
        f'{step_c_note_html}'
        f'    </div>\n\n'
        f'    <div class="section">\n'
        f'{read_aloud(data.finally_read_aloud)}'
        f'    </div>\n\n'
        f'    <div class="section">\n'
        f'      <div style="border: 1px solid var(--green); padding: 7px 9px; font-size: 9.5px; display:flex; gap:8px; align-items:center;">\n'
        f'        <span style="font-size:20px; color:var(--green); flex-shrink:0;">&#8594;</span>\n'
        f'        <span>\n'
        f'          <strong style="font-size:8px; text-transform:uppercase; letter-spacing:0.12em; color:var(--green); display:block; margin-bottom:2px;">Universe Creation Complete</strong>\n'
        f'          Hand off to the <strong>Player Guide</strong> for Character Creation. The GM Guide picks up at <em>Gather Around the Hearth</em>.\n'
        f'        </span>\n'
        f'      </div>\n'
        f'    </div>\n\n'
        f'  </div><!-- end col-right -->\n'
    )


# ---------------------------------------------------------------------------
# Full page renderer
# ---------------------------------------------------------------------------

def render_sheet(data: UniverseCreationData) -> str:
    return (
        f'<!DOCTYPE html>\n'
        f'<html lang="en">\n'
        f'<head>\n'
        f'<meta charset="UTF-8">\n'
        f'<title>1kFA &mdash; Table Guide &middot; Universe Creation</title>\n'
        f'<style>\n{CSS}\n</style>\n'
        f'</head>\n'
        f'<body>\n'
        f'<div class="page">\n\n'
        f'  <div class="header">\n'
        f'    <div class="header-left">\n'
        f'      <div class="guide-badge">Table Guide</div>\n'
        f'      <h1>Universe Creation</h1>\n'
        f'    </div>\n'
        f'    <div class="header-right">\n'
        f'      A Thousand Faces of Adventure<br>\n'
        f'      1kfa.com\n'
        f'    </div>\n'
        f'  </div>\n\n'
        f'{render_left_column(data)}\n'
        f'{render_right_column(data)}\n'
        f'  <div class="footer">\n'
        f'    <span>1kfa &middot; Table Guide &middot; Universe Creation</span>\n'
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
        description="Generate the 1kFA Table Guide Universe Creation sheet from mod_guide_table.md"
    )
    parser.add_argument("guide", help="Path to mod_guide_table.md")
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

    data = parse_universe_creation(text)

    print(f"  campaign options:    {[o['name'] for o in data.campaign_options]}")
    print(f"  intro read-aloud:   {len(data.intro_read_aloud)} chars")
    print(f"  step A read-aloud:  {len(data.step_a_read_aloud)} chars")
    print(f"  step B read-aloud:  {len(data.step_b_read_aloud)} chars")
    print(f"  step B notes:       {len(data.step_b_notes)}")
    print(f"  step C read-aloud:  {len(data.step_c_read_aloud)} chars")
    print(f"  finally read-aloud: {len(data.finally_read_aloud)} chars")

    html = render_sheet(data)
    filename = "sheet_table_guide_universe_creation.html"
    out_path = os.path.join(args.output_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
