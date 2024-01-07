#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys

from svg_dom import DOM, export_tall_png

def make_card(src_svg, out_svg, out_png, shows, hides):
    dom = DOM(src_svg)

    for layer in hides:
        dom.layer_hide(layer)
    for layer in shows:
        dom.layer_show(layer)

    dom.write_file(out_svg)
    export_tall_png(out_svg, out_png)

def make_deck():
    make_card(
      'char_card_front.svg',
      '/tmp/tall_cards/char_card_back.svg',
      '/tmp/tall_cards/char_card_back.png',
      [],
      [
       'male_hero',
       'female_hero',
      ]
    )

    make_card(
      'char_card_front.svg',
      '/tmp/tall_cards/char_card_male.svg',
      '/tmp/tall_cards/char_card_male.png',
      ['male_hero'],
      ['female_hero']
    )

    make_card(
      'char_card_front.svg',
      '/tmp/tall_cards/char_card_female.svg',
      '/tmp/tall_cards/char_card_female.png',
      ['female_hero'],
      ['male_hero']
    )


if __name__ == '__main__':
    if not os.path.exists('/tmp/tall_cards'):
        os.makedirs('/tmp/tall_cards')

    make_deck()
