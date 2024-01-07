#! /usr/bin/env python
# -*- coding: utf-8 -*-

import random
import itertools
from collections import defaultdict, OrderedDict

from cards import (
  cards,
  pct,
  count_checks_in_suit, # count_checks_in_suit(cards, suit)
  count_exes_in_suit,
  Card,
  Deckahedron,
  one_flip,
  two_flip,
  three_flip,
  four_flip,
  analyze, # analyze(func, possible_results, *args)
)

def dart_counts(deck):
    c1,c2,c3,c4 = four_flip(deck)
    print deck
    print '--'
    print c1, c1['d'], c1.count_checks('d')
    print c2, c2['c'], c2.count_checks('c')
    print c3, c3['b'], c3.count_checks('b')
    print c4, c4['a'], c4.count_checks('a')


#dart_counts(Deckahedron)

def dart_rigging():
    deck = Deckahedron[:]
    c1,c2,c3,c4 = four_flip(deck)
    return (
        c1.count_checks('d') + c2.count_checks('c') + c3.count_checks('b') + c4.count_checks('a')
    )
counts = analyze(dart_rigging, [0,1,2,3,4,5,6,7,8])
print counts[0]
print counts[1]

def crescent_rigging():
    deck = Deckahedron[:]
    c1,c2,c3 = three_flip(deck)
    return (
        c1.count_checks('c') + c2.count_checks('b') + c3.count_checks('a')
    )
counts = analyze(crescent_rigging, [0,1,2,3,4,5,6])
print counts[0]
print counts[1]

def bulb_rigging():
    deck = Deckahedron[:]
    c1,c2 = two_flip(deck)
    return (
        c1.count_checks('b') + c2.count_checks('a')
    )
counts = analyze(bulb_rigging, [0,1,2,3,4])
print counts[0]
print counts[1]

def anchor_rigging():
    deck = Deckahedron[:]
    c1 = one_flip(deck)
    return (
        c1.count_checks('a')
    )
counts = analyze(anchor_rigging, [0,1,2])
print counts[0]
print counts[1]

