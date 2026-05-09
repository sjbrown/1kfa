#!/usr/bin/env python3
"""
emit_gamedata.py
================
Build step: parses mod_guide_table.md via the existing pipeline and emits
gamedata.js — a JS module containing all structured content needed by the
web app.

Usage:
    python3 bin/emit_gamedata.py mod_guide_table.md --output web/gamedata.js

The emitted file has no dependencies and can be loaded as a <script> tag
or imported as a module.
"""

import argparse
import json
import os
import sys

# Allow running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from parse_quickstart_data import spans_to_plain
from generate_touchstones_html_sheet import parse_universe_creation
from generate_character_html_sheet import parse_character_creation
from generate_hearth_html_sheet import parse_hearth


def spans_to_js(spans: list) -> list:
    """Convert a span list to a plain serialisable list of dicts."""
    return [{'type': s['type'], 'text': s['text']} for s in spans]


def blockquote_to_js(bq: list) -> list:
    """Convert a blockquote (list of para dicts) to JS-serialisable form."""
    return [
        {'type': p['type'], 'spans': spans_to_js(p['spans'])}
        for p in bq
    ]


def build_gamedata(table_md_path: str, player_md_path: str, gm_md_path: str) -> dict:
    with open(table_md_path, encoding='utf-8') as f:
        table_text = f.read()
    with open(player_md_path, encoding='utf-8') as f:
        player_text = f.read()
    with open(gm_md_path, encoding='utf-8') as f:
        gm_text = f.read()

    uc   = parse_universe_creation(table_text)
    cc   = parse_character_creation(player_text)
    hearth = parse_hearth(gm_text)

    return {
        'universe_creation': {
            'campaign_options': uc.campaign_options,
            'intro':         blockquote_to_js(uc.intro_read_aloud),
            'step_a':        blockquote_to_js(uc.step_a_read_aloud),
            'step_b':        blockquote_to_js(uc.step_b_read_aloud),
            'step_b_notes':  uc.step_b_notes,
            'step_c':        blockquote_to_js(uc.step_c_read_aloud),
            'step_c_note':   uc.step_c_note,
            'finally':       blockquote_to_js(uc.finally_read_aloud),
        },
        'character_creation': {
            'traits_read_aloud':      blockquote_to_js(cc.traits_read_aloud),
            'worldcloth_questions':   [spans_to_js(q) for q in cc.worldcloth_questions],
            'worldcloth_followup':    spans_to_js(cc.worldcloth_followup),
            'name_read_aloud':        blockquote_to_js(cc.name_read_aloud),
            'initiation_read_aloud':  blockquote_to_js(cc.initiation_read_aloud),
            'initiation_options':     [spans_to_js(o) for o in cc.initiation_options],
            'receive_cards': [
                {'move': rc['move'], 'item': spans_to_js(rc['item'])}
                for rc in cc.receive_cards
            ],
        },
        'hearth': {
            'at_home_read_aloud':          blockquote_to_js(hearth.at_home_read_aloud),
            'at_home_followup':            spans_to_js(hearth.at_home_followup),
            'hearth_options':              hearth.hearth_options,
            'choose_hearth_read_aloud':    blockquote_to_js(hearth.choose_hearth_read_aloud),
            'hearth_examples_read_aloud':  blockquote_to_js(hearth.hearth_examples_read_aloud),
            'make_sure_note':              spans_to_js(hearth.make_sure_note),
            'must_be_separated_note':      spans_to_js(hearth.must_be_separated_note),
            'risk_life_read_aloud':        blockquote_to_js(hearth.risk_life_read_aloud),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description='Emit gamedata.js from 1kFA markdown guides'
    )
    parser.add_argument('table_md',  help='Path to mod_guide_table.md')
    parser.add_argument('player_md', help='Path to mod_guide_player.md')
    parser.add_argument('gm_md',     help='Path to mod_guide_gm.md')
    parser.add_argument('--output', default='web/gamedata.js',
                        help='Output path (default: web/gamedata.js)')
    args = parser.parse_args()

    for path in [args.table_md, args.player_md, args.gm_md]:
        if not os.path.exists(path):
            print(f'Error: {path} not found.', file=sys.stderr)
            sys.exit(1)

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    gamedata = build_gamedata(args.table_md, args.player_md, args.gm_md)
    js = 'const GAMEDATA = ' + json.dumps(gamedata, indent=2, ensure_ascii=False) + ';\n'

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(js)

    uc = gamedata['universe_creation']
    cc = gamedata['character_creation']
    h  = gamedata['hearth']
    print(f'  → {args.output}')
    print(f'    universe_creation:')
    print(f'      campaign_options:      {len(uc["campaign_options"])}')
    print(f'      step_a paragraphs:     {len(uc["step_a"])}')
    print(f'    character_creation:')
    print(f'      worldcloth_questions:  {len(cc["worldcloth_questions"])}')
    print(f'      initiation_options:    {len(cc["initiation_options"])}')
    print(f'      receive_cards:         {len(cc["receive_cards"])}')
    print(f'    hearth:')
    print(f'      hearth_options:        {len(h["hearth_options"])}')
    print(f'      examples paragraphs:   {len(h["hearth_examples_read_aloud"])}')


if __name__ == '__main__':
    main()
