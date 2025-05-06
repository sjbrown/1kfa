#! /usr/bin/env python3

import tall_cards
import parse_cards_csv


if __name__ == '__main__':
    moves = parse_cards_csv.get_dicts_from_spreadsheet('./character_move_sheet.csv', {}, '')
    for tc in tall_cards.cards:
        parse_cards_csv.brief_print(tc)
    for move in moves:
        parse_cards_csv.brief_print(move)
