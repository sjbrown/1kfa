#!/usr/bin/env python3
"""
generate_scene_sheets.py

Parses mod_guide_gm.md and generates printable Adventure Scene sheets
for each chapter of the One-Shot and 9-Hour 1kFA campaigns.

Usage:
    python3 generate_scene_sheets.py path/to/mod_guide_gm.md [--output-dir ./sheets]

Output:
    sheet_oneshot_ch1.html
    sheet_oneshot_ch2.html
    sheet_oneshot_ch3.html
    sheet_oneshot_ch4.html
    sheet_9hr_ch1.html
    ... etc.
"""

import re
import sys
import os
import argparse
from dataclasses import dataclass, field
from typing import Optional


# ── DATA STRUCTURES ──────────────────────────────────────────────────────────

@dataclass
class ChapterData:
    campaign: str           # "oneshot" or "9hr"
    chapter_num: int
    chapter_title: str      # e.g. "Start in a place of normalcy / comfort"
    chapter_aka: str        # e.g. "You" (9hr only)
    journey_point_text: str
    chapter_questions: list[str]
    stake_ideas: list[str]
    primary_bar_length: int
    skull_bar_length: int
    skull_triggers: list[dict]   # {"text": str, "combat": bool, "pursuit": bool}
    transition_text: str
    deck_note: str          # any special deck modification note
    watch_for_need: str
    watch_for_premise: str


# ── PARSER ───────────────────────────────────────────────────────────────────

def parse_guide(path: str) -> tuple[list[ChapterData], list[str]]:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract the universal scene questions from ### Procedures for an Adventure Scene
    general_questions = parse_general_scene_questions(text)

    chapters = []

    # ── ONE-SHOT ──
    oneshot_match = re.search(
        r'# One-Shot Campaign\s*(.*?)(?=\n# |\Z)',
        text, re.DOTALL
    )
    if oneshot_match:
        chapters += parse_campaign_chapters(oneshot_match.group(1), "oneshot")

    # ── 9-HOUR ──
    ninehr_match = re.search(
        r'# 9-hour Campaign\s*(.*?)(?=\n# |\Z)',
        text, re.DOTALL
    )
    if ninehr_match:
        chapters += parse_campaign_chapters(ninehr_match.group(1), "9hr")

    return chapters, general_questions



def parse_campaign_chapters(campaign_text: str, campaign_id: str) -> list[ChapterData]:
    """Split a campaign section into individual chapter blocks and parse each."""
    # Split on ## Chapter N: headings
    chapter_blocks = re.split(r'\n(?=## Chapter)', campaign_text)

    results = []
    for block in chapter_blocks:
        ch = parse_chapter_block(block, campaign_id)
        if ch:
            results.append(ch)
    return results


def parse_chapter_block(block: str, campaign_id: str) -> Optional['ChapterData']:
    """Parse a single ## Chapter N: ... block."""

    # Chapter heading
    heading = re.match(
        r'## Chapter (\d+)[:\.]?\s*(.*?)(?:\n|$)',
        block
    )
    if not heading:
        return None

    chapter_num = int(heading.group(1))
    chapter_title_raw = heading.group(2).strip()

    # AKA lines
    aka_matches = re.findall(r'\*\*AKA[:\s]*(.*?)\*\*', block)
    chapter_aka = aka_matches[0].strip() if aka_matches else ""

    # Clean chapter title — strip leading "Start in..." type if AKA is the short name
    chapter_title = chapter_title_raw

    # Journey point text — first paragraph after heading (before ### subheadings)
    jp_text = extract_journey_point(block, campaign_id, chapter_num)

    # Chapter-specific scene questions (from "### Chapter N Scene procedures")
    chapter_questions = extract_chapter_questions(block, chapter_num)

    # Stake ideas
    stake_ideas = extract_stake_ideas(block)

    # Progress bar sizes
    primary_bar = extract_bar_length(block, "primary")
    skull_bar = extract_bar_length(block, "skull")

    # Skull triggers
    skull_triggers = extract_skull_triggers(block)

    # Deck modification note
    deck_note = extract_deck_note(block)

    # Transition text — synthesised from chapter context
    transition_text = extract_transition(block, campaign_id, chapter_num)

    return ChapterData(
        campaign=campaign_id,
        chapter_num=chapter_num,
        chapter_title=chapter_title,
        chapter_aka=chapter_aka,
        journey_point_text=jp_text,
        chapter_questions=chapter_questions,
        stake_ideas=stake_ideas,
        primary_bar_length=primary_bar,
        skull_bar_length=skull_bar,
        skull_triggers=skull_triggers,
        transition_text=transition_text,
        deck_note=deck_note,
        watch_for_need="Signs of an approaching threat; what annoys, frustrates, or stifles characters at home.",
        watch_for_premise="A statement or action that asserts a fundamental truth. Write it down. Use it later for puzzles, monsters, villains.",
    )


def extract_journey_point(block: str, campaign: str, chapter_num: int) -> str:
    """Extract journey point text from ```journey_point_requirement fenced block."""
    m = re.search(r'```journey_point_requirement\s*\n(.*?)```', block, re.DOTALL)
    if m:
        return m.group(1).strip()
    return "Earn this Journey Point by fulfilling the chapter's narrative condition."


def extract_chapter_questions(block: str, chapter_num: int) -> list[str]:
    """Extract the chapter-specific scene questions from ### Chapter N Scene procedures."""
    proc_match = re.search(
        r'### Chapter \d+ Scene procedures.*?(?:answer\s+\d+\s+of\s+the\s+following\s+questions?|following\s+questions?)[:\s]*((?:\s*\*[^\n]+\n?)+)',
        block, re.DOTALL | re.IGNORECASE
    )
    if proc_match:
        return parse_bullet_list(proc_match.group(1))

    # Fallback: any bullet list after "Scene procedures"
    proc_section = re.search(r'### Chapter \d+ Scene procedures(.*?)(?=###|\Z)', block, re.DOTALL)
    if proc_section:
        bullets = re.findall(r'^\s*\*\s+(.+)$', proc_section.group(1), re.MULTILINE)
        # Filter out sub-bullets that are stake ideas etc.
        return [b.strip() for b in bullets if b.strip() and '?' in b][:6]

    return []


def extract_stake_ideas(block: str) -> list[str]:
    """Extract stake ideas from the chapter scene procedures."""
    proc_section = re.search(r'### Chapter \d+ Scene procedures(.*?)(?=###|\Z)', block, re.DOTALL)
    if not proc_section:
        return []

    text = proc_section.group(1)

    # Find the "Create the primary stake along these lines" list
    stake_match = re.search(
        r'(?:Create the primary stake|primary stake)[^\n]*\n((?:\s*\*[^\n]+\n?)+)',
        text, re.IGNORECASE
    )
    if stake_match:
        return parse_bullet_list(stake_match.group(1))

    return []


def extract_bar_length(block: str, bar_type: str) -> int:
    """Extract progress bar length from 'should be **N units long**' pattern."""
    if bar_type == "primary":
        # Match "primary ✔ progress bar" or "primary progress bar" (encoding-safe)
        pattern = r'primary\s+(?:✔\s+)?progress bar should be \*\*(\d+) units'
    else:
        pattern = r'skull progress bar should be \*\*(\d+) units'

    m = re.search(pattern, block, re.IGNORECASE)
    return int(m.group(1)) if m else (7 if bar_type == "primary" else 3)


def extract_skull_triggers(block: str) -> list[dict]:
    """Extract skull trigger questions."""
    triggers_match = re.search(
        r'\*\*When the skull progress bar increments\*\*[^\n]*\n((?:[\s\S]*?))(?=\n###|\n##|\n#|\Z)',
        block
    )
    if not triggers_match:
        return []

    text = triggers_match.group(1)
    items = []

    # Match top-level bullets (* text) and their sub-bullets (indented * text)
    lines = text.split('\n')
    current = None
    for line in lines:
        top = re.match(r'^\s{0,2}\*\s+(.+)', line)
        sub = re.match(r'^\s{3,}\*\s+(.+)', line)
        if top and not sub:
            if current:
                items.append(current)
            txt = top.group(1).strip()
            combat = bool(re.search(r'combat scene', txt, re.IGNORECASE))
            pursuit = bool(re.search(r'pursuit scene', txt, re.IGNORECASE))
            # Remove inline sub-references from main text
            txt = re.sub(r'\s*-\s*Start a (Combat|Pursuit) Scene', '', txt)
            current = {"text": txt, "combat": combat, "pursuit": pursuit}
        elif sub and current:
            sub_txt = sub.group(1).strip()
            if re.search(r'combat scene', sub_txt, re.IGNORECASE):
                current["combat"] = True
            elif re.search(r'pursuit scene', sub_txt, re.IGNORECASE):
                current["pursuit"] = True

    if current:
        items.append(current)

    return items[:6]  # cap at 6


def extract_deck_note(block: str) -> str:
    """Extract any special GM deck modification note."""
    m = re.search(r'(add the .+? to the GM Move Deck[^.]*\.)', block, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_transition(block: str, campaign: str, chapter_num: int) -> str:
    """Build a transition note pointing to the next chapter."""
    next_ch = chapter_num + 1

    # Try to find the next chapter title in the same block context
    if campaign == "oneshot":
        labels = {
            1: "Cross a Threshold with a True Choice.",
            2: "Take a Thing and Pay Its Price.",
            3: "Return to the Surface, Changed.",
            4: None,
        }
    else:
        labels = {
            1: "Chapter 2: Need — Call to Adventure.",
            2: "Chapter 3: Go — Cross the Threshold.",
            3: "Chapter 4: Search — Trials and Revelations.",
            4: "Chapter 5: Find.",
            5: "Chapter 6: Take &amp; Pay.",
            6: "Chapter 7: Return.",
            7: "Chapter 8: Change.",
            8: None,
        }

    next_label = labels.get(chapter_num)
    if not next_label:
        return "The campaign ends here. The story is complete."

    return f"Move toward {next_label}"


def parse_bullet_list(text: str) -> list[str]:
    """Parse a markdown bullet list into a list of strings."""
    items = re.findall(r'^\s*\*\s+(.+)$', text, re.MULTILINE)
    return [i.strip() for i in items if i.strip()]


# ── GENERAL SCENE QUESTIONS ───────────────────────────────────────────────────

def parse_general_scene_questions(text: str) -> list[str]:
    """
    Extract the universal scene questions from:
        ### Procedures for an Adventure Scene
        1. A "scene" is created ... answer the following questions:
         * ...
    """
    section = re.search(
        r'### Procedures for an Adventure Scene.*?answer the following questions?[:\s]*((?:\s*\*[^\n]+\n?)+)',
        text, re.DOTALL | re.IGNORECASE
    )
    if section:
        return parse_bullet_list(section.group(1))

    # Fallback: find the bullet list right after the section heading
    section2 = re.search(
        r'### Procedures for an Adventure Scene(.*?)(?=\n###|\n##|\Z)',
        text, re.DOTALL
    )
    if section2:
        return [b for b in parse_bullet_list(section2.group(1)) if '?' in b]

    return []


OPENING_IMAGE_PROMPTS = [
    "Establishing shot: setting, tone, who's present",
    "Where am I? Who's here? What's my role in this world?",
]


# ── CSS ───────────────────────────────────────────────────────────────────────

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
    body { background: white; }
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
    grid-template-rows: auto 1fr;
    gap: 0 0.22in;
    column-gap: 0.22in;
  }

  .header {
    grid-column: 1 / -1;
    border-bottom: 2px solid var(--ink);
    padding-bottom: 0.12in;
    margin-bottom: 0.14in;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
  }

  .header-left h1 {
    font-family: 'IM Fell English', serif;
    font-size: 22px;
    line-height: 1;
    letter-spacing: 0.01em;
  }

  .chapter-badge {
    display: inline-block;
    background: var(--ink);
    color: white;
    font-family: 'IM Fell English', serif;
    font-size: 11px;
    padding: 2px 8px;
    margin-bottom: 4px;
  }

  .col-left  { grid-column: 1; }
  .col-right { grid-column: 2; }

  .section { margin-bottom: 0.14in; }

  .section-head {
    font-size: 7.5px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: white;
    background: var(--ink);
    padding: 2px 6px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .section-head.accent  { background: var(--accent); }
  .section-head.warm    { background: var(--warm); }
  .section-head.danger  { background: var(--danger); }
  .section-head.green   { background: var(--green); }

  .checklist { list-style: none; padding: 0; }

  .checklist li {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    padding: 2.5px 0;
    border-bottom: 0.5px solid var(--mid);
    line-height: 1.4;
    font-size: 10px;
  }
  .checklist li:last-child { border-bottom: none; }

  .cb {
    width: 11px;
    height: 11px;
    border: 1.5px solid var(--ink);
    flex-shrink: 0;
    margin-top: 1px;
  }

  .arrow-item {
    display: flex;
    align-items: flex-start;
    gap: 5px;
    padding: 2px 0;
    font-size: 10px;
    line-height: 1.4;
  }

  .arrow-sym {
    color: var(--rule);
    flex-shrink: 0;
    font-size: 10px;
    margin-top: 1px;
  }

  .question-block {
    border: 1px solid var(--mid);
    padding: 5px 8px;
    margin-bottom: 6px;
  }

  .question-block .q-label {
    font-size: 7.5px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--rule);
    margin-bottom: 4px;
  }

  .q-item {
    display: flex;
    align-items: flex-start;
    gap: 5px;
    padding: 2px 0;
    font-size: 9.5px;
    line-height: 1.4;
    border-bottom: 0.5px dotted var(--mid);
  }
  .q-item:last-child { border-bottom: none; }

  .note-lines {
    border: 1px solid var(--mid);
    padding: 4px 6px;
  }

  .note-label {
    font-size: 7.5px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--rule);
    margin-bottom: 4px;
  }

  .line {
    border-bottom: 0.75px solid var(--mid);
    height: 18px;
    width: 100%;
  }

  .pb-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
    font-size: 9.5px;
  }

  .pb-label {
    min-width: 60px;
    color: var(--rule);
    font-size: 8.5px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .pb-note {
    font-size: 8px;
    color: var(--rule);
    font-style: italic;
  }

  .boxes { display: flex; gap: 3px; }

  .box {
    width: 14px;
    height: 14px;
    border: 1.5px solid var(--ink);
  }

  .box.skull { border-color: var(--danger); position: relative; }
  .box.skull::after {
    content: '☠';
    font-size: 8px;
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    color: var(--danger);
    opacity: 0.4;
  }

  .divider { border: none; border-top: 0.75px solid var(--mid); margin: 8px 0; }

  .stake-builder {
    border: 1px solid var(--warm);
    padding: 6px 8px;
    margin-bottom: 6px;
  }

  .trigger-list { list-style: none; padding: 0; }

  .trigger-list li {
    padding: 3px 0;
    border-bottom: 0.5px solid var(--mid);
    font-size: 9.5px;
    line-height: 1.4;
    display: flex;
    gap: 5px;
    align-items: flex-start;
  }
  .trigger-list li:last-child { border-bottom: none; }

  .t-icon { color: var(--danger); flex-shrink: 0; font-size: 9px; margin-top: 2px; }

  .t-sub {
    font-size: 8.5px;
    color: var(--rule);
    font-style: italic;
    display: block;
    margin-top: 1px;
  }

  .jp-box {
    border: 2px solid var(--green);
    padding: 6px 8px;
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin-bottom: 6px;
  }

  .jp-star { font-size: 22px; color: var(--green); line-height: 1; flex-shrink: 0; }

  .jp-text { font-size: 9.5px; line-height: 1.5; }

  .jp-text strong {
    display: block;
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--green);
    margin-bottom: 2px;
  }

  .premise-box {
    border: 1px dashed var(--accent);
    padding: 4px 6px;
    margin-top: 6px;
  }

  .mini-cols {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin-bottom: 6px;
  }

  .skull-bar-header {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 5px;
  }

  .skull-bar-label {
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--danger);
  }

  .skull-boxes { display: flex; gap: 6px; }

  .skull-box {
    width: 28px;
    height: 28px;
    border: 2px solid var(--danger);
    position: relative;
  }

  .skull-box::after {
    content: '☠';
    font-size: 13px;
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    color: var(--danger);
    opacity: 0.25;
  }

  .scene-record {
    border: 2px solid var(--ink);
    padding: 8px 10px;
    background: var(--light);
  }

  .sr-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .sr-label {
    font-size: 7.5px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--rule);
  }

  .sr-stake-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .sr-field-label {
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--rule);
    white-space: nowrap;
  }

  .sr-stake-line {
    flex: 1;
    border-bottom: 1.5px solid var(--ink);
    display: block;
    height: 16px;
  }

  .watch-box {
    background: var(--light);
    border-left: 3px solid var(--warm);
    padding: 5px 8px;
    margin-bottom: 6px;
  }

  .watch-item {
    display: flex;
    gap: 5px;
    align-items: flex-start;
    font-size: 9.5px;
    line-height: 1.4;
    margin-bottom: 2px;
  }

  .w-sym { color: var(--warm); flex-shrink: 0; }

  .footer {
    grid-column: 1 / -1;
    border-top: 1px solid var(--mid);
    margin-top: auto;
    padding-top: 6px;
    font-size: 7.5px;
    color: var(--rule);
    text-transform: uppercase;
    letter-spacing: 0.12em;
  }

  .deck-note {
    font-size: 8.5px;
    color: var(--danger);
    font-style: italic;
    border: 1px solid var(--danger);
    padding: 3px 6px;
    margin-top: 4px;
  }
"""


# ── HTML RENDERER ─────────────────────────────────────────────────────────────

def cb() -> str:
    return '<span class="cb"></span>'

def boxes(n: int) -> str:
    return '<div class="boxes">' + '<div class="box"></div>' * n + '</div>'

def skull_boxes(n: int) -> str:
    return '<div class="skull-boxes">' + '<div class="skull-box"></div>' * n + '</div>'

def q_items(questions: list[str]) -> str:
    return '\n'.join(
        f'        <div class="q-item">{cb()}<span>{q}</span></div>'
        for q in questions
    )

def arrow_items(items: list[str]) -> str:
    return '\n'.join(
        f'        <div class="arrow-item"><span class="arrow-sym">→</span><span>{item}</span></div>'
        for item in items
    )

def note_lines(n: int) -> str:
    lines = '\n'.join('        <div class="line"></div>' for _ in range(n))
    return f'      <div class="note-lines" style="margin-top:6px;">\n{lines}\n      </div>'

def render_skull_triggers(triggers: list[dict]) -> str:
    items = []
    for t in triggers:
        sub = ""
        if t.get("combat"):
            sub = '\n            <span class="t-sub">→ Start a Combat Scene</span>'
        elif t.get("pursuit"):
            sub = '\n            <span class="t-sub">→ Start a Pursuit Scene</span>'
        items.append(
            f'        <li>\n          <span class="t-icon">☠</span>\n'
            f'          <span>{t["text"]}{sub}\n          </span>\n        </li>'
        )
    return '\n'.join(items)


def render_sheet(ch: ChapterData, general_questions: list[str]) -> str:
    campaign_label = "One-Shot Campaign" if ch.campaign == "oneshot" else "9-Hour Campaign"
    badge_text = f"Chapter {ch.chapter_num}"
    if ch.chapter_aka:
        badge_text += f" · {ch.chapter_aka}"

    footer_text = f"1kfa · {campaign_label} · {ch.chapter_title} · Date ____________"

    # Chapter questions label
    if ch.campaign == "9hr" and ch.chapter_aka:
        ch_q_label = f"Chapter {ch.chapter_num}: {ch.chapter_aka} — check 3"
    else:
        ch_q_label = f"Chapter {ch.chapter_num} — check 3"

    # Build primary ✔ boxes
    primary_boxes = boxes(ch.primary_bar_length)
    skull_bar = skull_boxes(ch.skull_bar_length)

    # Journey point block
    jp_block = f"""    <div class="section">
      <div class="jp-box">
        <div class="jp-star">★</div>
        <div class="jp-text">
          <strong>Chapter {ch.chapter_num} Journey Point</strong>
          {ch.journey_point_text}
        </div>
      </div>
    </div>"""

    # Scene questions (general + chapter-specific)
    chapter_q_html = ""
    if ch.chapter_questions:
        chapter_q_html = f"""      <div class="question-block" style="margin-top:6px;">
        <div class="q-label">{ch_q_label}</div>
{q_items(ch.chapter_questions)}
      </div>"""

    scene_questions_block = f"""    <div class="section">
      <div class="section-head accent">Answer Scene Questions</div>
      <div class="question-block">
        <div class="q-label">Narrative Authority Waterfall — answer all</div>
{q_items(general_questions)}
      </div>
{chapter_q_html}
      <div class="note-lines" style="margin-bottom:6px; margin-top:6px;">
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
      </div>
      <div class="checklist">
        <li>{cb()}<span>Shuffle GM Move Deck</span></li>
        {'<li><div class="deck-note">' + ch.deck_note + '</div></li>' if ch.deck_note else ''}
        <li>{cb()}<span>Index cards ready for floating stakes</span></li>
      </div>
    </div>"""

    # NPCs block
    npc_slot = """        <div class="note-lines">
          <div class="note-label">NPC Name</div>
          <div class="line"></div>
          <div class="line"></div>
          <div class="line"></div>
        </div>"""

    npc_block = f"""    <div class="section">
      <div class="section-head">NPCs in This Scene</div>
      <div class="mini-cols">
{npc_slot}
{npc_slot}
      </div>
      <div class="mini-cols" style="margin-top:6px;">
{npc_slot}
{npc_slot}
      </div>
    </div>"""

    # Stake ideas block
    stake_html = arrow_items(ch.stake_ideas) if ch.stake_ideas else \
        '        <div class="arrow-item"><span class="arrow-sym">→</span><span>Consult chapter guidance for stake ideas.</span></div>'

    stake_block = f"""    <div class="section">
      <div class="section-head warm">Declare the Primary Stake</div>
      <div class="stake-builder">
{stake_html}
      </div>
    </div>"""

    # Primary stake card
    stake_card = f"""    <div class="section">
      <div class="scene-record">
        <div class="sr-top-row">
          <div class="sr-label" style="margin-bottom:0;">Primary Stake</div>
          {primary_boxes}
        </div>
        <div class="sr-stake-row" style="margin-top:6px;">
          <span class="sr-field-label">Name</span>
          <span class="sr-stake-line"></span>
        </div>
      </div>
    </div>"""

    # Opening image block
    opening_image_block = f"""    <div class="section">
      <div class="section-head accent">Paint the Opening Image</div>
      <div class="checklist">
        {''.join(f'<li><span class="arrow-sym" style="color:var(--rule); font-size:10px;">→</span><span>{p}</span></li>' for p in OPENING_IMAGE_PROMPTS)}
      </div>
      <div class="note-lines" style="margin-top:6px;">
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
      </div>
    </div>"""


    # Skull triggers block
    skull_triggers_html = render_skull_triggers(ch.skull_triggers)
    skull_block = f"""    <div class="section">
      <div class="section-head danger">When the Skull Bar Increments</div>
      <ul class="trigger-list">
{skull_triggers_html}
      </ul>
    </div>"""

    # Transition block
    transition_block = f"""    <div class="section">
      <div style="border: 1px solid var(--green); padding: 6px 8px; font-size: 9.5px; display:flex; gap:8px; align-items:center;">
        <span style="font-size:20px; color:var(--green);">→</span>
        <span><strong style="font-size:8px; text-transform:uppercase; letter-spacing:0.12em; color:var(--green); display:block; margin-bottom:2px;">When Chapter {ch.chapter_num} Ends</strong>
        {ch.transition_text}</span>
      </div>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>1kFA — {campaign_label} Ch.{ch.chapter_num} Adventure Scene</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="page">

  <!-- HEADER -->
  <div class="header">
    <div class="header-left">
      <div class="chapter-badge">{badge_text}</div>
      <h1>Adventure Scene <span style="font-family:'Space Mono',monospace; font-size:13px; font-weight:normal; color:var(--rule); letter-spacing:0.05em;">· <span style="border-bottom: 1.5px solid var(--ink); display:inline-block; min-width:2.5in;">&nbsp;</span></span></h1>
    </div>
    <div class="header-right">
      <div class="skull-bar-header">
        <div class="skull-bar-label">Skull ☠</div>
        {skull_bar}
      </div>
    </div>
  </div>

  <!-- LEFT COLUMN -->
  <div class="col-left">

{jp_block}

{scene_questions_block}

{npc_block}

  </div><!-- end col-left -->

  <!-- RIGHT COLUMN -->
  <div class="col-right">

{opening_image_block}

{stake_block}

{stake_card}


{skull_block}

{transition_block}

  </div><!-- end col-right -->

  <!-- FOOTER -->
  <div class="footer">
    <span>{footer_text}</span>
  </div>

</div><!-- end .page -->
</body>
</html>
"""
    return html


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate 1kFA Adventure Scene sheets from mod_guide_gm.md")
    parser.add_argument("guide", help="Path to mod_guide_gm.md")
    parser.add_argument("--output-dir", default=".", help="Directory for output HTML files")
    args = parser.parse_args()

    if not os.path.exists(args.guide):
        print(f"Error: {args.guide} not found.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Parsing {args.guide}...")
    chapters, general_questions = parse_guide(args.guide)

    if not chapters:
        print("No chapters found. Check that the guide contains '# One-Shot Campaign' or '# 9-hour Campaign' sections.")
        sys.exit(1)

    if not general_questions:
        print("Warning: could not find general scene questions under '### Procedures for an Adventure Scene'.")
    else:
        print(f"Found {len(general_questions)} general scene questions.")

    print(f"Found {len(chapters)} chapters.")

    for ch in chapters:
        html = render_sheet(ch, general_questions)
        filename = f"sheet_{ch.campaign}_ch{ch.chapter_num}.html"
        out_path = os.path.join(args.output_dir, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  → {out_path}  (primary bar: {ch.primary_bar_length}, skull: {ch.skull_bar_length}, triggers: {len(ch.skull_triggers)})")

    print("Done.")


if __name__ == "__main__":
    main()
