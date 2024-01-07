from itertools import *
from random import shuffle


def reduce_search_space(orig_space, new_card):
    new_space = []
    for card in orig_space:
        num_matches = len(set(new_card).intersection(set(card)))
        if num_matches == 1:
            new_space.append(card)
    return new_space

def make_decks(num_symbols, symbols_per_card):
    all_choices = list(combinations(range(num_symbols), symbols_per_card))

    first_card = all_choices.pop(0)

    initial_search_space = reduce_search_space(all_choices, first_card)

    solutions = {}
    for i in range(50):
        solution = [first_card]
        shuffle(initial_search_space)
        search_space = initial_search_space[:]
        while search_space:
            new_card = search_space.pop(0)
            search_space = reduce_search_space(search_space, new_card)
            solution.append(new_card)
        solutions[len(solution)] = solution

    return solutions

