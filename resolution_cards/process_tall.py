#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import re
import sys
import string
from pprint import pprint, pformat
from tall_cards import cards
from version import VERSION

DIR = '/tmp/cards_v' + VERSION

from svg_dom import DOM, export_png, export_tall_png, ensure_dirs

DEBUG = int(os.environ.get('DEBUG', 1))

def filenamify(s):
    x = s.lower()
    l = [c for c in x if c in (' ' + string.ascii_lowercase)]
    x = ''.join(l)
    x = x.replace(' ', '_')
    return x


def filter_dom_elements(dom, card):
    cut_these = [
      'spacer',
      'mod_str', 'mod_int', 'mod_dex', 'mod_bond',
      'mod_str/dex/int', 'mod_int/dex', 'mod_dex/str',
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
    ]
    card_spots = card.get('spots') or {}
    has_card_spots = any(card_spots[x] for x in card_spots)
    checks = [
        x for x in [card.get('slash_check'), card.get('one_check'),
                    card.get('two_check'), card.get('three_check')]
        if x not in (None, '')
    ]
    dom.layer_hide('template')
    dom.layer_show('std_heading')
    #print 'Checks: ', checks
    #print 'Has card spots: ', has_card_spots

    # first, turn on / off the 'flags'
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

        cut_these.remove('spot_level_0')
        cut_these.remove('spot_level_g1')
        cut_these.remove('spot_level_g2')

        if len(checks) == 0:
            dom.layer_hide('spot_3lines')
            dom.layer_hide('spot_slash_check')
            dom.layer_hide('spot_two_check')
            dom.layer_hide('spot_three_check')
        elif len(checks) == 2:
            dom.layer_hide('spot_3lines')
            if not card.get('slash_check'):
                dom.layer_hide('spot_slash_check')
            if not card.get('two_check'):
                dom.layer_hide('spot_two_check')
            if not card.get('three_check'):
                dom.layer_hide('spot_three_check')
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
                #print 'Showing', key
                dom.layer_show(key)
            if not card.get('slash_check') and 'slash_check' in key:
                #print 'hiding ot: ', key
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

    if card.get('reqs'):
        cut_these.remove(card['reqs'])

    if card.get('campaign'):
        cut_these.remove('campaign')

    if card.get('levels'):
        [cut_these.remove('level_' + lvl) for lvl in card['levels']]

    if card.get('circles'):
        [cut_these.remove(x) for x in card['circles']]
    if card.get('attr'):
        keep = 'mod_' + card['attr'].lower()
        cut_these.remove(keep)
    else:
        cut_these.append('mod_shield')
        cut_these.append('flip')

    for x in cut_these:
        dom.cut_element(x)



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

    # Create the svg file and export a PNG
    svg_filename = DIR + '/deck_card_face_3lines.svg'
    png_filename = DIR + '/deck_card_face_3lines.png'
    dom.write_file(svg_filename)
    export_tall_png(svg_filename, png_filename)



def make_card_dom(card):
    dom = DOM('tall_card_front.svg')

    if DEBUG:
        print '\nWorking on ' + card['title']
        print '\n'
        pprint(card)

    if card.get('levels') and not card.get('level_start'):
        raise Exception("Levels only works with level_start")

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
        dom.replace_text('words_one_check', card['one_check'], ideal_num_chars=40)
    if card.get('slash_check'):
        dom.replace_text('words_left', card['slash_check'], ideal_num_chars=30)
        dom.replace_text('spot_words_left', card['slash_check'], ideal_num_chars=30)
    elif card.get('two_check'):
        dom.replace_text('words_left', card['two_check'], ideal_num_chars=30)
        dom.replace_text('spot_words_left', card['two_check'], ideal_num_chars=30)
        dom.replace_text('words_two_check', card['two_check'], ideal_num_chars=40)
    else:
        # Card has nothing to do with flips
        dom.replace_text('spot_words_left', '')
        dom.replace_text('words_left', '')
    dom.replace_text('words_right', card['three_check'], ideal_num_chars=20)
    dom.replace_text('spot_words_right', card['three_check'], ideal_num_chars=20)
    dom.replace_text('words_three_check', card['three_check'], ideal_num_chars=40)

    if card.get('one_check') or card.get('slash_check') or card.get('two_check'):
        dom.replace_text('desc_detail', card['desc_detail'],
                         ideal_num_chars=200)
    else:
        dom.replace_text('desc_detail', card['desc_detail'],
                         ideal_num_chars=400)
    dom.replace_h1(card['title'])

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

    # Create the svg file and export a PNG
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

def make_deck(cards):
    export_tall_png('tall_card_back2.svg', DIR + '/move_deck/back.png')
    export_tall_png('tall_card_back2.svg', DIR + '/starter/back.png')
    export_tall_png('equipment_back1.svg', DIR + '/magic_deck/back.png')
    export_tall_png('equipment_back2.svg', DIR + '/mundane_deck/back.png')

    export_tall_png('tall_card_stats.svg', DIR + '/booklet/face18_stats.png')
    export_tall_png('tall_card_hints.svg', DIR + '/booklet/face19_hints.png')

    #one_blank_3lines_front()

    for i, card in enumerate(cards):
        try:
            dom = custom_card_dom(card)
            if not dom:
                dom = make_card_dom(card)
        except:
            print 'FAIL'
            print 'card:'
            pprint(card)
            raise

        svg_filename, png_filename = card_filenames(card, i)

        dom.write_file(svg_filename)

        export_tall_png(svg_filename, png_filename)


def make_documentation_images(cards):
    return
    """
    tmp_template_filename = DIR + '/move_card_template.svg'
    for i, card in enumerate(cards):
        slug = filenamify(card['title'])
        _svg_filename, png_filename = card_filenames(card, i)
        doc_img_filename = '../images/move_%s.png' % slug
        template_filename = '../images/move_card_template.svg'
        if os.path.isfile(doc_img_filename):
            c = file(template_filename).read()
            c = re.sub(
              'xlink:href="file://.*.png"',
              'xlink:href="file://%s"' % png_filename,
              c
            )
            outfile = file(tmp_template_filename, 'w')
            outfile.write(c)
            outfile.close()

            export_png(tmp_template_filename, doc_img_filename, 381, 381)

    """

def make_deck_from_svg_dir(dirpath, fpart=None):
    for fname in os.listdir(dirpath):
        if fname.endswith('.svg'):
            if fpart and fpart not in fname:
                continue
            base = os.path.splitext(fname)[0]
            png_filename = DIR + '/%s.png' % base
            export_tall_png(dirpath + '/' +fname, png_filename)


if __name__ == '__main__':
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    import parse_cards_csv

    if len(sys.argv) > 1:
        card_grep = sys.argv[1]
        filtered = cards + parse_cards_csv.get_objs(card_grep)
        if DEBUG:
            print 'filtering for', card_grep
        filtered = [c for c in filtered
          if card_grep.lower() in c['title'].lower()]
    else:
        filtered = cards + parse_cards_csv.get_objs()

    make_deck(filtered)
    make_documentation_images(filtered)

