#!/usr/bin/env python3
"""
parse_quickstart_data.py
=========================
Pure markdown parsing primitives for the 1kFA quickstart sheet pipeline.

Returns structured Python data only — no HTML, no CSS, no rendering.
HTML rendering lives in render_sheet_html.py.

All generate_*.py scripts import from here. Nothing in this module
produces output on its own.
"""

import re


# ── INLINE MARKDOWN ───────────────────────────────────────────────────────────

# Each span is a dict: {'type': 'text'|'bold'|'italic', 'text': str}

def parse_inline_md(text: str) -> list:
    """
    Parse inline markdown bold/italic into a list of typed spans.

    Returns a list of dicts, each with keys:
        type: 'text' | 'bold' | 'italic'
        text: str (plain text content, no markdown syntax)

    Example:
        "Hello **world** and *you*"
        -> [
            {'type': 'text',   'text': 'Hello '},
            {'type': 'bold',   'text': 'world'},
            {'type': 'text',   'text': ' and '},
            {'type': 'italic', 'text': 'you'},
           ]
    """
    spans  = []
    cursor = 0
    for m in re.finditer(r'\*\*(.+?)\*\*|\*(.+?)\*', text):
        if m.start() > cursor:
            spans.append({'type': 'text', 'text': text[cursor:m.start()]})
        if m.group(1) is not None:
            spans.append({'type': 'bold',   'text': m.group(1)})
        else:
            spans.append({'type': 'italic', 'text': m.group(2)})
        cursor = m.end()
    if cursor < len(text):
        spans.append({'type': 'text', 'text': text[cursor:]})
    return spans


def spans_to_plain(spans: list) -> str:
    """Collapse a span list to a plain string, discarding emphasis."""
    return "".join(s['text'] for s in spans)


# ── BLOCKQUOTE EXTRACTION ─────────────────────────────────────────────────────

# A blockquote is a list of paragraph dicts:
#   {'type': 'para',   'spans': [span, ...]}   -- a run of inline text
#   {'type': 'bullet', 'spans': [span, ...]}   -- a '- ' prefixed line

def _parse_blockquote_lines(lines: list) -> list:
    """
    Convert raw blockquote lines (leading '>' already stripped) into a list
    of paragraph dicts.
    """
    paragraphs = []
    current    = []

    def flush():
        if current:
            spans = parse_inline_md(" ".join(current))
            paragraphs.append({'type': 'para', 'spans': spans})
            current.clear()

    for line in lines:
        stripped = line.rstrip('\\').strip()
        if stripped == "" or stripped == ">":
            flush()
        elif stripped.startswith("- "):
            flush()
            paragraphs.append({'type': 'bullet', 'spans': parse_inline_md(stripped[2:])})
        else:
            current.append(stripped)

    flush()
    return paragraphs


def extract_blockquote(text: str) -> list:
    """
    Extract the first contiguous blockquote block from text.

    Returns a list of paragraph dicts. Returns [] if none found.
    """
    lines    = []
    in_quote = False

    for line in text.splitlines():
        m = re.match(r'^>\s?(.*)', line)
        if m:
            in_quote = True
            lines.append(m.group(1))
        elif in_quote:
            break

    return _parse_blockquote_lines(lines) if lines else []


def extract_all_blockquotes(text: str) -> list:
    """
    Extract all contiguous blockquote blocks from text, in order.

    Returns a list of blockquotes, each a list of paragraph dicts.
    """
    results = []
    current = []

    for line in text.splitlines():
        m = re.match(r'^>\s?(.*)', line)
        if m:
            current.append(m.group(1))
        else:
            if current:
                parsed = _parse_blockquote_lines(current)
                if parsed:
                    results.append(parsed)
                current = []

    if current:
        parsed = _parse_blockquote_lines(current)
        if parsed:
            results.append(parsed)

    return results


# ── BULLET LIST EXTRACTION ────────────────────────────────────────────────────

def parse_bullet_list(text: str) -> list:
    """
    Extract a markdown bullet list as a list of span lists.

    Each item is a list of span dicts (see parse_inline_md).

    Example:
        "- Hello **world**\n- Foo *bar*"
        -> [
            [{'type': 'text', 'text': 'Hello '}, {'type': 'bold', 'text': 'world'}],
            [{'type': 'text', 'text': 'Foo '},   {'type': 'italic', 'text': 'bar'}],
           ]
    """
    return [
        parse_inline_md(m.group(1).strip())
        for m in re.finditer(r'^\s*[-*]\s+(.+)$', text, re.MULTILINE)
        if m.group(1).strip()
    ]
