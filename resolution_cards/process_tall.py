#! /usr/bin/env python3

import os
import re
import sys
import string
from pprint import pprint, pformat
import parse_character_moves
from version import VERSION

from lxml import etree
from svg_dom import DOM, export_png, export_tall_png, ensure_dirs

DIR = '/tmp/cards_v' + VERSION
DEBUG = int(os.environ.get('DEBUG', 1))

def filenamify(s):
    x = s.lower()
    l = [c for c in x if c in (' ' + string.ascii_lowercase)]
    x = ''.join(l)
    x = x.replace(' ', '_')
    return x

CIRCLE_POSITIONS = ('✓', '✔', '✔✔')

# Elements cut by default; specific card data removes entries to preserve them.
_DEFAULT_CUT = [
    'spacer',
    'mod_str', 'mod_int', 'mod_dex',
    'mod_dexint', 'mod_dexstr', 'mod_intstr', 'mod_dexintstr',
    'wiz_ne', 'wiz_e', 'wiz_se', 'wiz_sw', 'wiz_w', 'wiz_nw',
    'rogue_ne', 'rogue_e', 'rogue_se', 'rogue_sw', 'rogue_w', 'rogue_nw',
    'fighter_ne', 'fighter_e', 'fighter_se', 'fighter_sw', 'fighter_w', 'fighter_nw',
    'all_ne', 'all_e', 'all_se', 'all_sw', 'all_w', 'all_nw',
    'spot_level_0', 'spot_level_g1', 'spot_level_g2',
    'spot_1_1', 'spot_2_1', 'spot_3_1',
    'spot_1_2', 'spot_2_2', 'spot_3_2',
    'level_r3', 'level_r2', 'level_r1',
    'level_0', 'level_g1', 'level_g2',
    'level_start_r3', 'level_start_r2', 'level_start_r1',
    'level_start_0', 'level_start_g1', 'level_start_g2',
    'spot_level_start_0', 'spot_level_start_g1', 'spot_level_start_g2',
    'C', 'CC/F', 'CC/W', 'CC/R',
    'campaign',
    'circle_progress_pos1', 'circle_progress_pos2', 'circle_progress_pos3',
]

def insert_circle_symbols(dom, card, attr, id_prefix, href_fn):
    """
    Insert SVG use-symbols into the three circle positions, then cut
    the placeholders.
    """
    data = getattr(card, attr)
    for key, pos_id in zip(CIRCLE_POSITIONS, [
      f'{id_prefix}_pos1', f'{id_prefix}_pos2', f'{id_prefix}_pos3',
    ]):
        if data[key]:
            dom.insert_use_symbol(pos_id, href_fn(data[key]))
        dom.cut_element_by_id(pos_id)

def insert_progress_symbols(dom, card):
    insert_circle_symbols(
        dom, card,
        attr='progress',
        id_prefix='circle_progress',
        href_fn=lambda val: f'symbols_progress.svg#{"".join(val)}_progress',
    )

def insert_shadow_point_symbols(dom, card):
    insert_circle_symbols(
        dom, card,
        attr='shadow_points',
        id_prefix='circle_shadow',
        href_fn=lambda val: 'symbols_shadow_point.svg#shadow_point',
    )


def _active_checks(card):
    """Return the list of non-empty check fields on this card."""
    return [
        x for x in [
            card.get('slash_check'), card.get('one_check'),
            card.get('two_check'),   card.get('three_check'),
        ]
        if x not in (None, '')
    ]


def _configure_layers(dom, card, checks):
    """Show, hide, or cut layers based on card data. No element cutting here."""
    dom.layer_show('std_heading')
    dom.layer_show('prog_3lines_positions')
    dom.layer_hide('positions')

    card_spots = card.get('spots') or {}
    has_card_spots = any(card_spots[x] for x in card_spots)

    for key in dom.layers:
        if card.get('flags') and 'flags' in key:
            dom.layer_show(key)
        elif 'flags' in key:
            dom.cut_layer(key)

    if has_card_spots:
        for key in dom.layers:
            if 'spot_' in key:
                dom.layer_show(key)
            elif 'std_' in key:
                dom.cut_layer(key)

        if len(checks) == 0:
            dom.layer_hide('spot_3lines')
            dom.layer_hide('spot_slash_check')
            dom.layer_hide('spot_two_check')
            dom.layer_hide('spot_three_check')
        elif len(checks) == 2:
            dom.layer_hide('spot_3lines')
            if not card.get('slash_check'):  dom.layer_hide('spot_slash_check')
            if not card.get('two_check'):    dom.layer_hide('spot_two_check')
            if not card.get('three_check'):  dom.layer_hide('spot_three_check')
        elif len(checks) == 3:
            dom.layer_hide('spot_slash_check')
            dom.layer_hide('spot_two_check')
            dom.layer_hide('spot_three_check')
        else:
            raise ValueError('Spots! %s' % pformat(card))

        for i in range(3):
            if '1' in card.get('spots')[i]:
                cut_these.remove('spot_%s_1' % (i+1))
            if '2' in card.get('spots')[i]:
                cut_these.remove('spot_%s_2' % (i+1))
            if 'EX' in card.get('spots')[i]:
                dom.layer_hide('spot_br')
            if 'BR' in card.get('spots')[i]:
                dom.layer_hide('spot_ex')

    else: # Not a 'spots' style card
        for key in dom.layers:
            if 'spot_' in key:
                dom.cut_layer(key)
            elif 'std_' in key:
                dom.layer_show(key)
            elif '3lines' in key:
                dom.layer_show(key)
            if not card.get('slash_check') and 'slash_check' in key:
                dom.layer_hide(key)
            if not card.get('two_check') and 'two_check' in key:
                dom.layer_hide(key)
            if not card.get('three_check') and 'three_check' in key:
                dom.layer_hide(key)

    for key in dom.layers:
        if card.get('equipment') and 'equipment' in key:
            dom.layer_show(key)
        elif 'equipment' in key:
            dom.layer_hide(key)

        if 'more_power' in key:
            dom.layer_hide(key)
            if card.get('title','').lower() in [
                '____ of unerring dispatch',
                '____ of vitality',
                '____ bow',
                '____ sword',
            ]:
                dom.layer_show(key)

        if card.get('campaign') and 'campaign' in key:
            dom.layer_show(key)
        elif 'campaign' in key:
            dom.layer_hide(key)

        if card.get('reqs') and 'reqs' in key:
            dom.layer_show(key)
        elif 'reqs' in key:
            dom.layer_hide(key)

        if card.get('tags') and 'tags' in key:
            dom.layer_show(key)
        elif 'tags' in key:
            dom.layer_hide(key)

        if card.get('circles') and 'class_' in key:
            dom.layer_show(key)

        if len(checks) == 0:
            if '_2lines' in key or '_3lines' in key:
                dom.layer_hide(key)
        elif len(checks) == 2:
            if '_0lines' in key or '_3lines' in key:
                dom.layer_hide(key)
        elif len(checks) == 3:
            if '_0lines' in key or '_2lines' in key:
                dom.layer_hide(key)

        if 'levels' in key and not card.get('levels'):
            dom.layer_hide(key)

    if not ''.join(card.results.values()):
        dom.layer_hide('3lines')


def _build_cut_list(card, checks):
    """Return the list of element IDs to cut, given this card's data."""
    cut_these = list(_DEFAULT_CUT)

    card_spots = card.get('spots') or {}
    has_card_spots = any(card_spots[x] for x in card_spots)

    if has_card_spots:
        cut_these.remove('spot_level_0')
        cut_these.remove('spot_level_g1')
        cut_these.remove('spot_level_g2')
        for i, spot in enumerate(card.get('spots')):
            if '1' in spot: cut_these.remove('spot_%s_1' % (i+1))
            if '2' in spot: cut_these.remove('spot_%s_2' % (i+1))

    if card.get('reqs'):
        cut_these.remove(card['reqs'])
    if card.get('campaign'):
        cut_these.remove('campaign')
    if card.get('levels'):
        for lvl in card['levels']:
            cut_these.remove('level_' + lvl)
    if card.get('circles'):
        for x in card['circles']:
            cut_these.remove(x)

    sattrs = ''.join(sorted(x.lower() for x in card.get('attrs', [])))
    if sattrs == 'dex':
        cut_these.remove('mod_dex')
    elif sattrs == 'int':
        cut_these.remove('mod_int')
    elif sattrs == 'str':
        cut_these.remove('mod_str')
    elif sattrs == 'dexint':
        cut_these.remove('mod_dexint')
    elif sattrs == 'dexstr':
        cut_these.remove('mod_dexstr')
    elif sattrs == 'intstr':
        cut_these.remove('mod_intstr')
    elif sattrs == 'dexintstr':
        cut_these.remove('mod_dexintstr')
    else:
        cut_these.append('g_flip_shield')

    return cut_these


def filter_dom_elements(dom, card):
    checks = _active_checks(card)
    _configure_layers(dom, card, checks)
    cut_these = _build_cut_list(card, checks)

    if card.get('progress'):
        insert_progress_symbols(dom, card)
    if card.get('shadow_points'):
        insert_shadow_point_symbols(dom, card)

    for x in cut_these:
        dom.cut_element(x)


"""
def one_blank_3lines_front():
    dom = DOM('tall_card_front.svg')

    filter_dom_elements(dom, {})
    dom.replace_text('VERSION', VERSION)
    dom.replace_text('words_one_check', '')
    dom.replace_text('words_two_check', '')
    dom.replace_text('words_three_check', '')
    dom.replace_text('desc_detail', '')
    dom.replace_h1('')
    for key in dom.layers:
        if (
          'slash_check' in key
          or
          'two_check' in key
          or
          'three_check' in key
          or
          '2lines' in key
          or
          'spot' in key
        ):
            dom.layer_hide(key)
        elif '3lines' in key:
            dom.layer_show(key)

    svg_filename = DIR + '/deck_card_face_3lines.svg'
    dom.write_file(svg_filename)
    # PNG export intentionally omitted — run make_deck_pngs() locally
"""


def make_card_dom(card):
    dom = DOM('tall_card_front.svg')

    if DEBUG:
        print(f'\nWorking on {card["title"]}\n')
        pprint(card)

    #if card.levels and not card.get('level_start'):
    #    raise Exception("Levels only works with level_start")

    filter_dom_elements(dom, card)

    if card.get('campaign'):
        if card.get('campaign') == '3':
            dom.replace_text('campaign_text', 'One-Shot Campaign')
        elif card.get('campaign') == '9':
            dom.replace_text('campaign_text', '9hr / 30hr Campaign')
        else:
            dom.replace_text('campaign_text', '30hr Campaign')

    if card.get('flags'):
        flags_text = ','.join(card['flags'])
        dom.replace_text('flags_text', flags_text)

    if card.get('tags'):
        tag_text = ','.join(card['tags'])
        dom.replace_text('card_tags_text', tag_text)

    if card.get('one_check'):
        dom.replace_text('words_one_check', card['one_check'],
                         style=card.get('style_one_check'))
    if card.get('slash_check'):
        dom.replace_text('words_left', card['slash_check'])
        dom.replace_text('spot_words_left', card['slash_check'])
    elif card.get('two_check'):
        dom.replace_text('words_left', card['two_check'])
        dom.replace_text('spot_words_left', card['two_check'])
        dom.replace_text('words_two_check', card['two_check'],
                         style=card.get('style_two_check'))
    else:
        # Card has nothing to do with flips
        dom.replace_text('spot_words_left', '')
        dom.replace_text('words_left', '')
    dom.replace_text('words_right', card['three_check'])
    dom.replace_text('spot_words_right', card['three_check'])
    dom.replace_text('words_three_check', card['three_check'],
                     style=card.get('style_three_check'))

    if card.get('one_check') or card.get('slash_check') or card.get('two_check'):
        dom.replace_text('desc_detail_half', card['details'],
                         style=card.get('style_details', None))
    else:
        dom.replace_text('desc_detail_full', card['details'],
                         style=card.get('style_details', None))
    dom.replace_h1(card['title'], style=card.get('style_title'))

    return dom


def custom_card_dom(card):
    tail = filenamify(card['title'])
    fpath = 'tall_card__' + tail + '.svg'
    if os.path.isfile(fpath):
        return DOM(fpath)
    return None


def component_type(card):
    if card.get('component'):
        return card.get('component')
    elif card.get('equipment'):
        return 'mundane_deck'
    else:
        return 'move_deck'


def card_filenames(card, i):
    dirpath = '%s/%s/' % (DIR, component_type(card))
    os.makedirs(dirpath, exist_ok=True)

    number = card.get('custom_number', (i+1))
    svg_filename = dirpath + 'face%02d_%s.svg' % (
        number,
        filenamify(card['title'])
    )
    png_filename = dirpath + 'face%02d_%s.png' % (
        number,
        filenamify(card['title'])
    )
    return svg_filename, png_filename


def make_deck_svgs(cards):
    """Write all card SVG files. No Inkscape required."""
    for i, card in enumerate(cards):
        try:
            dom = custom_card_dom(card)
            if not dom:
                dom = make_card_dom(card)
        except:
            print('FAIL')
            print('card:')
            pprint(card)
            raise

        svg_filename, _ = card_filenames(card, i)
        dom.write_file(svg_filename)
        print(f'  wrote  {svg_filename}')


def make_deck_pngs(cards):
    """Export all PNGs via Inkscape."""
    export_tall_png('tall_card_back2.svg', DIR + '/move_deck/back.png')
    export_tall_png('tall_card_back2.svg', DIR + '/starter/back.png')
    export_tall_png('equipment_back1.svg', DIR + '/magic_deck/back.png')
    export_tall_png('equipment_back2.svg', DIR + '/mundane_deck/back.png')

    #export_tall_png('tall_card_stats.svg', DIR + '/dramatic_action/face18_stats.png')
    #export_tall_png('tall_card_hints.svg', DIR + '/dramatic_action/face19_hints.png')

    for i, card in enumerate(cards):
        svg_filename, png_filename = card_filenames(card, i)
        dom = DOM(svg_filename)
        export_tall_png(svg_filename, png_filename, dom.references)
        print(f'  exported  {png_filename}')


def make_deck_from_svg_dir(dirpath, fpart=None):
    for fname in os.listdir(dirpath):
        if fname.endswith('.svg'):
            if fpart and fpart not in fname:
                continue
            base = os.path.splitext(fname)[0]
            png_filename = DIR + '/%s.png' % base
            export_tall_png(dirpath + '/' + fname, png_filename)


if __name__ == '__main__':
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    filtered = parse_character_moves.handy_moves('character_move_sheet.md')

    card_grep = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if card_grep:
        filtered = [c for c in filtered
                    if card_grep.lower() in c['title'].lower()]

    make_deck_svgs(filtered)

    if '--no-pngs' not in sys.argv:
        make_deck_pngs(filtered)

    print(f'\n\nFinished. Output in {DIR}')
