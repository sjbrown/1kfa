#! /usr/bin/env python

import os
from PIL import Image
from datetime import datetime

import core
import objects

VERSION = '0.93'
user = None
game = None

def main():
    now_str = datetime.now().strftime('%Y-%m-%d-%H-%M')
    user = objects.User()
    game = objects.Game(user, 'Game-%s' % now_str)

    #game.make_poker_deck('/tmp/cards_v%s/move_deck' % VERSION)
    #game.make_poker_deck('/tmp/cards_v%s/starter' % VERSION)
    #game.make_poker_deck('/tmp/cards_v%s/level_deck' % VERSION)
    #game.make_poker_deck('/tmp/cards_v%s/mundane_deck' % VERSION)
    #game.make_poker_deck('/tmp/cards_v%s/magic_deck' % VERSION)
    #game.make_booklet('/tmp/cards_v%s/booklet' % VERSION)
    game.make_square_deck('/tmp/cards')
    game.make_square_deck('/tmp/cards/red')
    game.make_square_deck('/tmp/cards/green')
    game.make_square_deck('/tmp/cards/wounds')
    game.make_square_deck('/tmp/cards/blessing')

if __name__ == '__main__':

    main()
