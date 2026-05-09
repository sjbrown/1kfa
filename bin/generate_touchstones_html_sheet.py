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
from parse_quickstart_data import (
    extract_all_blockquotes,
    extract_blockquote,
)
from render_sheet_html import (
    CSS_BASE,
    cb,
    checklist_item,
    read_aloud,
    rule_note,
    section_head,
)



# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class UniverseCreationData:
    campaign_options: list          # [{"name": str, "desc": str}, ...]
    intro_read_aloud: list          # blockquote paragraphs
    step_a_read_aloud: list         # blockquote paragraphs
    step_b_read_aloud: list         # blockquote paragraphs
    step_b_notes: list              # non-blockquote guidance after Step 2 quote
    step_c_read_aloud: list         # blockquote paragraphs
    step_c_note: str                # prose note after Step 3 questions
    finally_read_aloud: list        # blockquote paragraphs


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

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

CSS = CSS_BASE


# ---------------------------------------------------------------------------
# HTML helpers
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
    print(f"  intro read-aloud:   {len(data.intro_read_aloud)} paragraphs")
    print(f"  step A read-aloud:  {len(data.step_a_read_aloud)} paragraphs")
    print(f"  step B read-aloud:  {len(data.step_b_read_aloud)} paragraphs")
    print(f"  step B notes:       {len(data.step_b_notes)}")
    print(f"  step C read-aloud:  {len(data.step_c_read_aloud)} paragraphs")
    print(f"  finally read-aloud: {len(data.finally_read_aloud)} paragraphs")

    html = render_sheet(data)
    filename = "sheet_table_guide_universe_creation.html"
    out_path = os.path.join(args.output_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
