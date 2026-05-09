#!/usr/bin/env python3
"""
render_sheet_html.py
=====================
Shared HTML rendering helpers and base CSS for the 1kFA quickstart sheet
pipeline.

Converts structured data from parse_quickstart_data.py into HTML strings.
All generate_*.py scripts import from here for rendering; parse logic stays
in parse_quickstart_data.py.
"""


# ── INLINE RENDERING ──────────────────────────────────────────────────────────

def spans_to_html(spans: list) -> str:
    """Render a list of span dicts (from parse_inline_md) to an HTML string."""
    parts = []
    for span in spans:
        t = span['text']
        if span['type'] == 'bold':
            parts.append(f'<strong>{t}</strong>')
        elif span['type'] == 'italic':
            parts.append(f'<em>{t}</em>')
        else:
            parts.append(t)
    return "".join(parts)


def blockquote_to_html(paragraphs: list) -> str:
    """
    Render a blockquote (list of paragraph dicts from extract_blockquote)
    to an HTML string with <br><br> paragraph breaks.
    """
    parts = []
    for para in paragraphs:
        text = spans_to_html(para['spans'])
        if para['type'] == 'bullet':
            parts.append("&ndash;&nbsp;" + text)
        else:
            parts.append(text)
    return "<br><br>\n        ".join(parts)


def bullet_list_to_html(items: list) -> list:
    """
    Render a bullet list (list of span lists from parse_bullet_list) to a
    list of HTML strings, one per item.
    """
    return [spans_to_html(spans) for spans in items]


# ── COMPONENT HELPERS ─────────────────────────────────────────────────────────

def cb() -> str:
    return '<span class="cb"></span>'


def section_head(label: str, color: str = "") -> str:
    cls = ("section-head " + color).strip()
    return f'      <div class="{cls}">{label}</div>\n'


def read_aloud(paragraphs, style: str = "") -> str:
    """
    Render a blockquote (list of paragraph dicts, or a pre-rendered HTML str)
    as a read-aloud block.
    """
    if isinstance(paragraphs, list):
        text = blockquote_to_html(paragraphs)
    else:
        text = paragraphs
    s = f' style="{style}"' if style else ""
    return (
        f'      <div class="read-aloud"{s}>\n'
        f'        &ldquo;{text}&rdquo;\n'
        f'      </div>\n'
    )


def rule_note(text: str, style: str = "") -> str:
    s = f' style="{style}"' if style else ""
    return f'      <p class="rule-note"{s}>{text}</p>\n'


def checklist_item(text: str) -> str:
    return f'        <li>{cb()}<span>{text}</span></li>\n'


# ── BASE CSS ──────────────────────────────────────────────────────────────────
# Design tokens, reset, page layout, and component classes shared by all
# sheets. Sheet-specific CSS is appended locally in each generate_* script.

CSS_BASE = """
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
"""
