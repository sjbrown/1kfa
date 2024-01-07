#! /usr/bin/env python
# -*- coding: utf-8 -*-

import random
from collections import defaultdict, OrderedDict

class Card:
    component = 'booklet'

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
    component = getattr(C, 'component', 'tall_card')
    attr = getattr(C, 'attr', '')
    one_check = parse(getattr(C, 'one_check', ''))
    slash_check = parse(getattr(C, 'slash_check', ''))
    two_check = parse(getattr(C, 'two_check', ''))
    three_check = parse(getattr(C, 'three_check', ''))
    desc_detail = parse(C.desc)
    levels = getattr(C, 'levels', [])

    card = {
        'title': title,
        'custom_number': getattr(C, 'custom_number', None),
        'component': component,
        'attr_shield': bool(attr),
        'attr': attr,
        'one_check': one_check,
        'slash_check': slash_check,
        'two_check': two_check,
        'three_check': three_check,
        'desc_detail': desc_detail,
        'circles': getattr(C, 'circles', []),
        'spots': getattr(C, 'spots', {}),
        'levels': levels,
        'level_start': getattr(C, 'level_start', None),
    }
    return card


class Mix_It_Up(Card):
  attr = 'Str'
  custom_number = 10
  one_check = '''
    Deal 1 attack power and the foe attacks you
  '''
  two_check = '''
    Roll melee attack power and the foe attacks you
    '''
  three_check = '''
    Roll melee attack power and choose
    '''
  desc = u'''
    On a ✔✔✔, you can choose one:
    * Avoid the foe's attack
    * Add an extra attack power roll
    |
    |
    The foe's attack can be any GM move made directly with that NPC or monster.
    |
    |
    Some attacks may have additional effects depending on the triggering action,
    the circumstances, or the weapons involved
    |
    |
    Without a melee weapon, a character deals 1 attack power instead of rolling.
    '''

class Volley(Card):
  custom_number = 11
  attr = 'Dex'
  one_check = '''
    Roll attack power.
    GM chooses an option.
  '''
  two_check = '''
    Roll attack power.
    Choose an option
  '''
  three_check = '''
    Roll attack power.
  '''
  desc = u'''
    Send a volley flying with your ranged weapon.
    |
    Choices:
    * You have to move to get the shot, placing you in danger of the GM's choice
    * You have to take what you can get - halve your attack power
    * You have to take several shots - lose 1 PACK
  '''
  level_start = '0'
  levels = ['0', 'g1']

class Parley(Card):
  custom_number = 7
  attr = 'Int'
  slash_check = '''
    They demand concrete assurance or exchange, right now.
  '''
  three_check = '''
    They make a deal. Make a promise and get what you want.
  '''
  desc = u'''
    Using leverage, manipulate an NPC. "Leverage" is something they need or want.
    |
    |
    If your leverage is promises or threats without clear evidence, flip with 1 level of disadvantage.
  '''
  level_start = '0'
  levels = ['0', 'g1']

class Defy_Danger(Card):
  custom_number = 1
  attr = 'Str/Dex/Int'
  two_check = '''
    You do it, but there's a new complication
    '''
  one_check = '''
    Make progress, but stumble, hesitate, flinch
    |
    or pay a cost.
    '''
  three_check = '''
    Success
    '''
  desc = u'''
    When you act despite an imminent threat, say how you deal with it and flip.
    |
    If you do it...
    * by powering through or enduring, flip Str
    * by getting out of the way or acting fast, flip Dex
    * with quick wits or via mental fortitude, flip Int
    |
    |
    On a ✅ / ✔✔, the GM may ask you a question, offer you a worse outcome, hard bargain, or ugly choice
  '''

class Defend(Card):
  custom_number = 6
  attr = 'Str'
  slash_check = '''
    Spend 1 XP
    |
    Choose 1
  '''
  three_check = '''
    Spend 1 XP
    |
    Choose 2
  '''
  desc = '''
    Stand in defense of a person, item, or location that is under attack.
    The attack is redirected from the thing you defend to yourself. You
    may spend XP to choose:
    * Halve the attack's effect or damage
    * Open up the attacker to an ally giving +1 advantage against the attacker
    * Roll attack power against the attacker
    |
    |
    This move can interrupt an attack against an ally if you are in
    range and attack power has not yet been rolled.
  '''

class Discern(Card):
  custom_number = 4
  attr = 'Int'
  one_check = '''
    Ask the GM 1 question from the list
    '''
  two_check = '''
    Ask the GM 2 questions from the list
    '''
  three_check = '''
    Ask the GM 3 questions from the list
    '''
  desc = '''
    Closely study a situation or person, ask the GM your question(s), and
    gain a +1 advantage when acting on the answers. (Place tokens to remember
    where the advantages are, as appropriate)
    * What here is useful or valuable to me?
    * What happened here recently?
    * What is about to happen?
    * What should I be on the lookout for?
    * Who's really in control here?
    * What here is not what it appears to be?
    '''

class I_Know_This(Card):
  custom_number = 5
  attr = 'Int'
  slash_check = '''
    The GM tells you something interesting
    - it's on you to make it useful.
    '''
  three_check = '''
    The GM tells you something interesting
    and useful about the subject relevant to your situation
    '''
  desc = u'''
    State facts about the world or the people in it.
    |
    Consult your accumulated knowledge about something.
    |
    |
    (You may always do this through the normal course of playing the game,
    but when the GM doubts the fact or judges that the fact would provide
    significant benefit to the players, the I Know This move is triggered)
    |
    |
    On a ✅, the GM may ask you "How do you know this?".
    '''

class Rest(Card):
  custom_number = 12
  desc = u'''
    When not travelling, with a day to devote to rest, do the following:
    |
    * Step 1: Return all Exhaustion tokens to the supply
    * Step 2: Count the Harm and Wound tokens on your Exhaustion pile
    * Step 3: Keep that many cards in your Exhaustion pile, put the rest into your discard pile
    * Step 4: Return one Harm token to the supply
    * Step 5: Say who you blame for your injuries
    |
    |
    Magic items left idle regain their charges up to their capacity
    |
    |
    Gird all your armour
    |
    (remove Harm and Wound tokens from it)
    |
    |
    Learning skills, studying, or any action that takes
    mental or physical effort is not available when Resting.
    '''

class Seek_Help(Card):
  custom_number = 13
  desc = u'''
    When in a peaceful environment where external resources with healing
    powers are available:
    |
    * Step 1: Describe your healing experience
    * Step 2: Return all Exhaustion tokens to the supply
    * Step 3: Return all Harm tokens to the supply
    * Step 4: Count the Wound tokens on your Exhaustion pile
    * Step 5: Keep that many cards in your Exhaustion pile, put the rest into your discard pile
    * Step 6: Return all Wound cards to the supply
    * Step 7: Say who you are closer to forgiving
    * Step 8: If you are at The Hearth, return all Wound tokens to the supply
    |
    |
    As with Rest, idle magic items regain their charges. Gird all your armour.
    Seeking Help leaves no time for activities that take effort.
    '''



locs = locals()
cards = []
for k, v in locs.items():
    if Card in getattr(v, '__bases__', []):
        cards.append(make_card(v))
