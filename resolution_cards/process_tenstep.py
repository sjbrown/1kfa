#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import re
import sys
import string
from collections import defaultdict, OrderedDict
from pprint import pprint, pformat
from version import VERSION

DIR = '/tmp/cards_v' + VERSION

from svg_dom import DOM, export_png, export_tall_png, ensure_dirs

DEBUG = 1

def filenamify(s):
    x = s.lower()
    l = [c for c in x if c in (' ' + string.ascii_lowercase)]
    x = ''.join(l)
    x = x.replace(' ', '_')
    return x


def filter_dom_elements(dom, card, front_or_back):
    dom.layer_hide('template')
    dom.layer_show('blackbg')
    dom.layer_show('whitebg')
    dom.layer_show('gradient_bg')
    dom.layer_show('number')
    dom.layer_show('front')
    if front_or_back == 'back':
        dom.layer_show('back')
    else:
        dom.layer_hide('back')



def make_card_dom(card, front_or_back):
    dom = DOM('tenstep_card.svg')

    if DEBUG:
        print '\nWorking on ' + card['title']
        print '\n'
        pprint(card)

    filter_dom_elements(dom, card, front_or_back)

    dom.replace_h1(card['title'])
    dom.replace_text('number', card['number'])
    print "STYLE", card.get('desc_style')
    dom.replace_text(
        'desc_detail',
        card['desc_detail'],
        style=card.get('desc_style')
    )


    return dom

def custom_card_dom(card, front_or_back):
    tail = filenamify(card['title'])
    fpath = 'tenstep_card__' + tail + '_' + front_or_back + '.svg'
    if os.path.isfile(fpath):
        print 'Found custom card', fpath
        return DOM(fpath)
    return None


def card_filenames(card, front_or_back):
    dirpath = '%s/%s/' % (DIR, card.get('component'))

    # Create the svg file and export a PNG
    number = card.get('number')
    svg_filename = dirpath + front_or_back + '%02d_%s.svg' % (
        int(number),
        filenamify(card['title'])
    )
    png_filename = dirpath + front_or_back + '%02d_%s.png' % (
        int(number),
        filenamify(card['title'])
    )
    return svg_filename, png_filename

def make_deck(cards):
    for i, card in enumerate(cards):
        try:
            front_dom = custom_card_dom(card, 'front')
            if not front_dom:
                front_dom = make_card_dom(card, 'front')
            back_dom = custom_card_dom(card, 'back')
            if not back_dom:
                back_dom = make_card_dom(card, 'back')
        except:
            print 'FAIL'
            print 'card:'
            pprint(card)
            raise

        svg_filename, png_filename = card_filenames(card, 'front')
        front_dom.write_file(svg_filename)
        export_tall_png(svg_filename, png_filename)

        svg_filename, png_filename = card_filenames(card, 'back')
        back_dom.write_file(svg_filename)
        export_tall_png(svg_filename, png_filename)



class Card:
    pass

def parse(s):
    retval = ''
    for line in s.split('\n'):
        l = line.strip()
        if not l:
            continue
        if l.startswith('|'):
            retval += '\n' + l[1:]
        elif l.startswith('*'):
            retval += '\n' + u'✷' + l[1:]
        else:
            retval += ' ' + l

    return retval.strip()

def make_card(C):
    title = getattr(C, 'title',
                 # If no 'title', use the class name
                 C.__name__.replace('_', ' '))
    desc_detail = parse(C.desc)

    card = {
        'title': title,
        'component': 'tenstep',
        'desc_detail': desc_detail,
        'number': str(getattr(C, 'number', 'x')),
        'desc_style': getattr(C, 'desc_style', None),
    }
    return card


class Establish_Touchstones(Card):
  number = 1
  desc = u'''
    Brainstorm titles
    |
    |
    Narrow titles
    |
    |
    Establish expectations
    '''

class Create_GM_Worksheet(Card):
  number = 2
  desc = ''

class Set_Character_Expectations(Card):
  number = 3
  desc = ''

class Choose_Move_Cards(Card):
  number = 4
  desc = '''
  All "A" Cards
  |
  |
  (#players + 1) "B" Cards
  |
  |
  (#players + 1) "C" Cards
  '''

class Choose_Dex_Int_Str(Card):
  number = 5
  desc = '''
  Distribute 6 points
  |
  |
  No attribute can be 0
  '''

class Name_Your_Character(Card):
  number = 6
  desc = ''

class Add_Flesh(Card):
  number = 7
  desc_style = {'font-size': '8px', 'font-family': 'serif'}
  desc = '''
  * What species is your character, human, or something else from our Touchstone List?
  * Does your character steal things, or do they respect the concept of private property?
  * Before the adventure starts, is your character engaged in any kind of profession?
  * Does your character believe in gods? Is there some kind of religious practice or religious organization for them?
  * Does your character enjoy the outdoors, or city life? Are they extreme in that preference?
  * Roughly how old is your character?  Have they ever killed a person before?
  * What's your character's social standing? When they first walk into a room full of people, do they provoke any reaction?
  '''

class Choose_Risk_Drivers(Card):
  number = 8
  desc_style = {'font-size': '10px'}
  desc = '''
  * Expose an embarrassment
  * Locate a prize
  * Extract a secret
  * Become enamored
  * Sell your services
  * Break down a barrier
  * Choose a side
  * Be an agent of justice
  * Take pity on the desperate
  * Start a grudge
  * Consort with the unsavory
  * Believe an impossible claim
  * Get called out on your boasting
  '''

class Choose_Items_And_Weapons(Card):
  number = 9
  desc = '''
  2 Pack Cards
  |
  |
  RECEIVE CARDS tag
  |
  |
  2 Item Cards
  '''

class The_Hearth(Card):
  number = 10
  desc_style = {'font-size': '14px'}
  desc = '''
  * Specific People
  * Food
  * Song
  * Environmental feature
  * Ritual or festival
  * Group activity
  '''

if __name__ == '__main__':
    locs = locals()
    cards = []
    for k, v in locs.items():
        if Card in getattr(v, '__bases__', []):
            cards.append(make_card(v))

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(DIR + '/tenstep'):
        os.makedirs(DIR + '/tenstep')

    import parse_cards_csv

    make_deck(cards)
