#! /usr/bin/env python2
# -*- coding: utf-8 -*-


from cards import cards as deck
from random import shuffle

chars = '🂠 🃟 ٭ ■ ⚔♛♞⚒🀆🀫🀰  🀹  🀺   🀻  🀼   🁀  🁁  🁂  🁃  '
anvil = '⚒'
blades = '⚔'
crown = '♛'
dragon = '♞'
cardback = '🂠 '
cardup = '🃟 '
RED="31" #"\033[0;31m"
BLU="34" # "\033[0;34m"
GRN="32" #"\033[0;32m"
YEL="33" # "\033[0;33m"
NOCOLOR="\033[0m"
#WHT= "\[\033[0;38m\]"   ;  WHT1="\[\033[1;38m\]"  #white
#BWHT="\[\033[0;45m\]"  ;  BWHT1="\[\033[1;48m\]"  #white

COL_FMT = "\033[%s;%sm"
BG = "0"

p1 = {
  'deck': deck,
  'resolving': [],
  'discard': [],
  'exhaustion': [],
  'tokens': []
}

shuffle(p1['deck'])

def flip():
    card = p1['deck'].pop()
    p1['resolving'].append(card)

def discard():
    [p1['discard'].append(card) for card in p1['resolving']]
    p1['resolving'] = []

def exhaust():
    [p1['exhaustion'].append(card) for card in p1['resolving']]
    p1['resolving'] = []

def reshuffle():
    discard()
    p1['deck'] = p1['deck'] + p1['discard']
    p1['discard'] = []
    shuffle(p1['deck'])



def red(s):
    return COL_FMT % (BG, "31") + s #+ NOCOLOR
def green(s):
    return COL_FMT % (BG, GRN) + s #+ NOCOLOR
def yellow(s):
    return COL_FMT % (BG, YEL) + s #+ NOCOLOR
def blue(s):
    return COL_FMT % (BG, BLU) + s #+ NOCOLOR
def white_bg_on():
    global BG
    BG = "47"
def white_bg_off():
    global BG
    BG = "0"

def face(card):
    white_bg_on()
    a = red('%s %s' % (anvil, card['a']))
    b = blue('%s %s' % (blades, card['b']))
    c = yellow('%s %s' % (crown, card['c']))
    d = green('%s %s' % (dragon, card['d']))
    white_bg_off()
    return ' '.join([a, b, c, d]) + NOCOLOR

def print_state():
  deck = cardback + 'x%s' % len(p1['deck'])
  resolving = ',  '.join([face(card) for card in p1['resolving']])
  discard = 'Dis%sx%s' % (cardup, len(p1['discard']))
  exhaust = 'Ex%sx%s' % (cardup, len(p1['exhaustion']))
  print('| %s | %s | %s |  %s |' % (deck, resolving, discard, exhaust))


print_state()


try:
    while True:
        print('')
        print_state()
        print('')
        command = raw_input('flip, discard, exhaust, reshuffle ? > ')
        command = command.lower() or 'X'
        fn = {
            'X': lambda: None,
            'f': flip,
            'd': discard,
            'e': exhaust,
            'r': reshuffle,
        }[command[0]]
        fn()

except (EOFError, KeyboardInterrupt):
    print('\nEND\n')
