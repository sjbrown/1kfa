#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import shutil
from itertools import product
from cards import cards, blessing_cards, wound_cards, dice_print_rules
from cards import spot_it_map, spot_it_rules, calc_zodiac

from svg_dom import DOM, export_square_png
from version import VERSION

FACE_SVG = 'deckahedron_face.svg'

'''
 title_to_element

{'anchor_two_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1cb0>,
 'anchor_one_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1d40>,
 'anchor_three_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1cf8>,
 'anchor_one_x': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1d88>,
 'bulb_two_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1a70>,
 'bulb_one_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1b00>,
 'bulb_three_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1ab8>,
 'bulb_one_x': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1b48>,
 'crescent_two_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1b90>,
 'crescent_one_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1c20>,
 'crescent_three_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1bd8>,
 'crescent_one_x': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1c68>,
 'dart_two_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a18c0>,
 'dart_one_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a19e0>,
 'dart_three_check': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1998>,
 'dart_one_x': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1a28>,
 'deck_1': <Element {http://www.w3.org/2000/svg}rect at 0x7f63b24a1878>,
 'deck_2': <Element {http://www.w3.org/2000/svg}rect at 0x7f63b24a1830>,
 'deck_3': <Element {http://www.w3.org/2000/svg}rect at 0x7f63b24a1710>,
 'deck_4': <Element {http://www.w3.org/2000/svg}rect at 0x7f63b24a16c8>,
 'exhaustable': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1950>,
 'proficient': <Element {http://www.w3.org/2000/svg}g at 0x7f63b24a1908>}

cards

[{'Pro': False, 'Stamina': False, 'a': 1, 'b': 1, 'c': 1, 'd': 1},
 {'Pro': False, 'Stamina': False, 'a': 1, 'b': 2, 'c': 4, 'd': 1},
 {'Pro': False, 'Stamina': False, 'a': 1, 'b': 2, 'c': 3, 'd': 2},
 {'Pro': False, 'Stamina': False, 'a': 1, 'b': 4, 'c': 3, 'd': 4},
 {'Pro': True, 'Stamina': False, 'a': 2, 'b': 2, 'c': 3, 'd': 4},
 {'Pro': True, 'Stamina': False, 'a': 2, 'b': 3, 'c': 2, 'd': 3},
 {'Pro': False, 'Stamina': False, 'a': 1, 'b': 1, 'c': 2, 'd': 3},
 {'Pro': False, 'Stamina': False, 'a': 2, 'b': 1, 'c': 2, 'd': 3},
 {'Pro': False, 'Stamina': False, 'a': 2, 'b': 2, 'c': 1, 'd': 2},
 {'Pro': False, 'Stamina': False, 'a': 3, 'b': 1, 'c': 2, 'd': 2},
 {'Pro': False, 'Stamina': True, 'a': 4, 'b': 4, 'c': 4, 'd': 4},
 {'Pro': False, 'Stamina': True, 'a': 1, 'b': 3, 'c': 3, 'd': 4},
 {'Pro': False, 'Stamina': True, 'a': 3, 'b': 3, 'c': 4, 'd': 2},
 {'Pro': False, 'Stamina': True, 'a': 3, 'b': 1, 'c': 3, 'd': 4},
 {'Pro': False, 'Stamina': True, 'a': 1, 'b': 2, 'c': 2, 'd': 4},
 {'Pro': True, 'Stamina': True, 'a': 3, 'b': 2, 'c': 1, 'd': 4},
 {'Pro': True, 'Stamina': True, 'a': 1, 'b': 4, 'c': 4, 'd': 2},
 {'Pro': True, 'Stamina': True, 'a': 3, 'b': 4, 'c': 3, 'd': 4},
 {'Pro': False, 'Stamina': True, 'a': 4, 'b': 3, 'c': 4, 'd': 2},
 {'Pro': False, 'Stamina': True, 'a': 3, 'b': 3, 'c': 1, 'd': 3}]
'''



def set_zodiac(dom, nw_animal, ne_animal, se_animal, sw_animal):
    directions = ['nw', 'ne', 'se', 'sw']
    d_map = dict(nw=nw_animal, ne=ne_animal, se=se_animal, sw=sw_animal)
    for d in directions:
        keep_animal = d_map[d]
        d_titles = ['o_%s_%s' % (x,d) for x in spot_it_map.values()]
        d_titles += ['o_goat_%s' % d, 'o_dragon_%s' % d]
        for d_title in d_titles:
            if keep_animal not in d_title:
                dom.cut_element(d_title)

def filter_dom_elements(dom, card, deck_title, dice_rule):
        for dt in ['deck_1', 'deck_2', 'deck_3', 'deck_4']:
            if dt == deck_title:
                continue
            dom.cut_element(dt)

        if not card.get('blessing'):
            dom.cut_element('copper_halo')
            dom.cut_element('gold_halo')
            dom.cut_element('wound')
        elif card.get('blessing') == 'copper':
            dom.cut_element('gold_halo')
            dom.cut_element('wound')
        elif card.get('blessing') == 'gold':
            dom.cut_element('copper_halo')
            dom.cut_element('wound')
        elif card.get('blessing') == 'wound':
            dom.cut_element('copper_halo')
            dom.cut_element('gold_halo')

        if not card.get('crit_win'):
            dom.cut_element('crit_win')

        if not card.get('crit_fail'):
            dom.cut_element('crit_fail')

        if not card.get('Pro'):
            dom.cut_element('proficient')

        if not card.get('Stamina'):
            dom.layer_hide('exhaustion')
            dom.layer_hide('exhaustion_center')
        else:
            dom.layer_show('exhaustion')
            dom.layer_show('exhaustion_center')

        # ---------------------------------------
        # numeral-style dice rules
        d4, d6 = dice_rule
        if d4 == 0:
            dom.layer_hide('d4')
        else:
            dom.layer_show('d4')
            cuts = {
                1: ('d4_2', 'd4_3', 'd4_4'),
                2: ('d4_1', 'd4_3', 'd4_4'),
                3: ('d4_1', 'd4_2', 'd4_4'),
                4: ('d4_1', 'd4_2', 'd4_3'),
            }
            for elname in cuts[d4]:
                dom.cut_element(elname)
        if d6 == 0:
            dom.layer_hide('d6')
        else:
            dom.layer_show('d6')
            cuts = {
                1: ('d6_2', 'd6_3', 'd6_4', 'd6_5', 'd6_6'),
                2: ('d6_1', 'd6_3', 'd6_4', 'd6_5', 'd6_6'),
                3: ('d6_1', 'd6_2', 'd6_4', 'd6_5', 'd6_6'),
                4: ('d6_1', 'd6_2', 'd6_3', 'd6_5', 'd6_6'),
                5: ('d6_1', 'd6_2', 'd6_3', 'd6_4', 'd6_6'),
                6: ('d6_1', 'd6_2', 'd6_3', 'd6_4', 'd6_5'),
            }
            for elname in cuts[d6]:
                dom.cut_element(elname)

        # ---------------------------------------
        # pip-style dice rules
        ## Choose the dice pips to print out
        #for titletuple in product(
        #    ['four', 'six'],
        #    ['nw', 'ne', 'sw', 'se'],
        #    ['1', '2']
        #):
        #    title = '_'.join(titletuple)
        #    if title not in dice_rule:
        #        dom.cut_element(title)

        # Choose how many ✔s and ✗s to show
        letter_to_prefix = {
          'a': 'anvil',
          'b': 'blades',
          'c': 'crown',
          'd': 'dragon',
        }
        score_to_suffix = {
          1: '_one_x',
          2: '_one_check',
          3: '_two_check',
          4: '_three_check',
        }
        suffixes = score_to_suffix.values()
        for letter, prefix in letter_to_prefix.items():
            for suffix in suffixes:
                title = prefix + suffix
                if title != prefix + score_to_suffix[card[letter]]:
                    dom.cut_element(title)


def make_back_card():
    raw_svg = file('deckahedron_back.svg').read()
    raw_svg = raw_svg.replace('VERSION', VERSION)
    back_svg_filename = '/tmp/cards/back.svg'
    fp = file(back_svg_filename, 'w')
    fp.write(raw_svg)
    fp.close()
    dom = get_dom_for_printing(back_svg_filename)
    dom.write_file(back_svg_filename)
    export_square_png(back_svg_filename, '/tmp/cards/back.png')

def make_deck(deck_number):

    for i, card in enumerate(cards):
        dom = get_dom_for_printing(FACE_SVG)
        dom.layer_hide('wound')
        dom.layer_show('registration_marks')
        dom.layer_show('zodiac')
        dom.layer_show('center_symbols')
        dom.layer_show('checks_xs')
        dom.layer_show('d6')
        dom.layer_show('d4')

        deck_title = 'deck_%s' % deck_number

        # ----- for pip-style cards ------
        #dice_rule = dice_print_rules[i][1]
        #dice_rule = dice_rule.split()
        # --- for numeral-style cards ----
        dice_rule = dice_print_rules[i][0]

        print 'dice rule %s %s' % (i, dice_rule)

        filter_dom_elements(dom, card, deck_title, dice_rule)
        zargs = [spot_it_map[x] for x in calc_zodiac(i)]
        set_zodiac(dom, *zargs)

        # Create the svg file and export a PNG
        svg_filename = '/tmp/cards/deck_%s_card_face%02d.svg' % (deck_number, (i+1))
        png_filename = '/tmp/cards/deck_%s_card_face%02d.png' % (deck_number, (i+1))

        dom.write_file(svg_filename)

        export_square_png(svg_filename, png_filename)

def make_blessing_deck():
    for i, card in enumerate(blessing_cards):
        dom = get_dom_for_printing(FACE_SVG)
        dom.layer_hide('wound')
        dom.layer_show('zodiac')
        dom.layer_show('center_symbols')
        dom.layer_show('checks_xs')

        filter_dom_elements(dom, card, '', [0,0])
        set_zodiac(dom, 'dragon', 'dragon', 'dragon', 'dragon')

        # Create the svg file and export a PNG
        svg_filename = '/tmp/cards/blessing/deck_blessing_card_face%s.svg' % ((i+1))
        png_filename = '/tmp/cards/blessing/deck_blessing_card_face%s.png' % ((i+1))

        dom.write_file(svg_filename)

        export_square_png(svg_filename, png_filename)


def make_wound_deck():
    for i, card in enumerate(wound_cards):
        dom = get_dom_for_printing(FACE_SVG)
        dom.layer_show('zodiac')
        dom.layer_show('wound')
        dom.layer_show('checks_xs')

        filter_dom_elements(dom, card, '', [0,0])
        set_zodiac(dom, 'goat', 'goat', 'goat', 'goat')

        # Create the svg file and export a PNG
        svg_filename = '/tmp/cards/wounds/deck_wound_card_face%s.svg' % ((i+1))
        png_filename = '/tmp/cards/wounds/deck_wound_card_face%s.png' % ((i+1))

        dom.write_file(svg_filename)

        export_square_png(svg_filename, png_filename)

def make_green_deck():
    svg_filename = 'greencard_front.svg'
    png_filename = '/tmp/cards/green/greencard_front.png'
    dom = get_dom_for_printing(svg_filename)
    svg_filename = '/tmp/cards/green/' + svg_filename
    dom.write_file(svg_filename)
    export_square_png(svg_filename, png_filename)

    svg_filename = 'greencard_back.svg'
    png_filename = '/tmp/cards/green/back.png'
    dom = get_dom_for_printing(svg_filename)
    svg_filename = '/tmp/cards/green/' + svg_filename
    dom.write_file(svg_filename)
    export_square_png(svg_filename, png_filename)

def make_red_deck():
    svg_filename = 'redcard_front.svg'
    png_filename = '/tmp/cards/red/redcard_front.png'
    dom = get_dom_for_printing(svg_filename)
    svg_filename = '/tmp/cards/red/' + svg_filename
    dom.write_file(svg_filename)
    export_square_png(svg_filename, png_filename)

    svg_filename = 'redcard_back.svg'
    png_filename = '/tmp/cards/red/back.png'
    dom = get_dom_for_printing(svg_filename)
    svg_filename = '/tmp/cards/red/' + svg_filename
    dom.write_file(svg_filename)
    export_square_png(svg_filename, png_filename)

def get_dom_for_printing(fname):
    dom = DOM(fname)
    dom.layer_hide('bg_after_cut')
    dom.layer_show('bg_bleed')
    if 'cutline' in dom.layers:
        dom.layer_hide('cutline')
    return dom

if __name__ == '__main__':
    if not os.path.exists('/tmp/cards'):
        os.makedirs('/tmp/cards')
    if not os.path.exists('/tmp/cards/wounds'):
        os.makedirs('/tmp/cards/wounds')
    if not os.path.exists('/tmp/cards/blessing'):
        os.makedirs('/tmp/cards/blessing')
    if not os.path.exists('/tmp/cards/red'):
        os.makedirs('/tmp/cards/red')
    if not os.path.exists('/tmp/cards/green'):
        os.makedirs('/tmp/cards/green')
    make_back_card()
    shutil.copy('/tmp/cards/back.png', '/tmp/cards/wounds/back.png')
    shutil.copy('/tmp/cards/back.png', '/tmp/cards/blessing/back.png')
    make_green_deck()
    make_red_deck()
    if os.environ.get('PARALLEL'):
        from multiprocessing import Pool
        from functools import partial
        pool = Pool(6)
        def doit(partl):
          partl()
        pool.apply_async(doit, [
          partial(make_deck, 1),
          partial(make_deck, 2),
          partial(make_deck, 3),
          partial(make_deck, 4),
          partial(make_wound_deck),
          partial(make_blessing_deck),
        ])
    else:
        print('')
        print('You can use PARALLEL=1 to make this faster')
        print('')
        make_deck(1)
        make_deck(2)
        make_deck(3)
        make_deck(4)
        make_wound_deck()
        make_blessing_deck()
