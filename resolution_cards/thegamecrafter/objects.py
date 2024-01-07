#! /usr/bin/env python

import os
import core


class User(dict):
    def __init__(self):
        udict = core.login()
        super(User, self).__init__(udict)
        self.id = udict['id']
        self.designer_id = user_designers(self.id)[0]['id']
        self.games = user_games(self.id)

class Game(dict):
    def __init__(self, user, name):
        self.user = user
        gdict = core.new_game(user, name)
        super(Game, self).__init__(gdict)
        self.id = gdict['id']
        self.folder = core.new_folder(user, name)
        self.parts = []

    def make_square_deck(self, dirpath):
        asset = '%s-sqdeck-%s' % (self['name'], len(self.parts))

        def face_card_test(filename):
            return filename.startswith('deck') and filename.endswith('.png')

        return self.make_deck(
            'smallsquaredeck', 'smallsquarecard', asset, dirpath, face_card_test
        )

    def make_poker_deck(self, dirpath):
        asset = '%s-pdeck-%s' % (self['name'], len(self.parts))

        def face_card_test(filename):
            return filename.startswith('face') and filename.endswith('.png')

        return self.make_deck(
            'pokerdeck', 'pokercard', asset, dirpath, face_card_test
        )

    def make_deck(self, deck_kind, card_kind, asset, dirpath, face_card_test):
        folder = core.new_folder(self.user, asset, self.folder['id'])

        back_filepath = dirpath + '/back.png'
        file_result = core.new_file(back_filepath, folder['id'])

        deck = new_deck(
            deck_kind, asset, self.id, back_file_id=file_result['id']
        )

        print 'Deck'
        print deck

        self.parts.append(deck)

        file_list = [dirpath + '/' + x
                     for x in os.listdir(dirpath)
                     if face_card_test(x)]
        for filepath in file_list:
            file_result = core.new_file(filepath, folder['id'])
            card = new_card(
                card_kind,
                os.path.basename(filepath),
                deck_id=deck['id'],
                file_id=file_result['id']
            )

    def make_booklet(self, dirpath):
        asset = '%s-booklet-%s' % (self['name'], len(self.parts))
        folder = core.new_folder(self.user, asset, self.folder['id'])

        booklet = new_booklet('smallbooklet', asset, self.id)

        print 'Booklet'
        print booklet

        self.parts.append(booklet)

        file_list = [dirpath + '/' + x
                     for x in os.listdir(dirpath)
                     if x.endswith('.png')]
        for filepath in file_list:
            file_result = core.new_file(filepath, folder['id'])
            card = new_booklet_page(
                'smallbookletpage',
                os.path.basename(filepath),
                booklet_id=booklet['id'],
                image_id=file_result['id']
            )


def user_games(user_id):
    result = core.get('user/%s/games' % user_id)
    if result['paging']['total_pages'] > 1:
        raise NotImplemented('Cannot handle pages yet')
    return result['items']

def user_designers(user_id):
    result = core.get('user/%s/designers' % user_id)

    if result['paging']['total_pages'] > 1:
        raise NotImplemented('Cannot handle pages yet')
    if len(result['items']) != 1:
        raise NotImplemented('Cannot handle 0 or >1 designers yet')

    return result['items']

def new_deck(kind, name, game_id, back_file_id=None):
    res = core.post(
        kind,
        name=name,
        game_id=game_id,
        back_id=back_file_id,
    )
    return res

def new_card(kind, name, deck_id, file_id=None):
    res = core.post(
        kind,
        name=name,
        deck_id=deck_id,
        face_id=file_id,
        has_proofed_face=1,
    )
    return res

def new_booklet(kind, name, game_id):
    res = core.post(
        kind,
        name=name,
        game_id=game_id,
    )
    return res

def new_booklet_page(kind, name, booklet_id, image_id):
    res = core.post(
        kind,
        name=name,
        booklet_id=booklet_id,
        image_id=image_id,
        has_proofed_image=1,
    )
    return res
