#! /usr/bin/python

import os, sys

DEBUG = os.environ.get('DEBUG', 1)
PYTHON_1KFA_DIR = os.environ.get('PYTHON_1KFA_DIR', os.environ['HOME'] + '/work/1kfa/resolution_cards')
SVG_SRC_DIR = os.environ.get('SVG_SRC_DIR', os.environ['HOME'] + '/work/1kfa/resolution_cards')
BUILD_DIR = os.environ.get('BUILD_DIR', os.environ['HOME'] + '/work/1kfa/images')

sys.path.append(PYTHON_1KFA_DIR)

print sys.path

from version import VERSION
from svg_dom import DOM, export_png, ensure_dirs, get_attrib, set_attrib

def run(cmd):
    if DEBUG:
        print cmd
    status = os.system(cmd)
    if status != 0:
        print 'Error', status
        sys.exit(status)


def replace_symbol_with_layer(s_dom, symbol_title, l_file, layer_label):
    for symbol in s_dom.title_to_elements[symbol_title]:
        l_dom = DOM(SVG_SRC_DIR + '/' + l_file)
        layer_group = l_dom.layers[layer_label]
        set_attrib(layer_group, 'groupmode', None)
        parent = symbol.getparent()
        parent.replace(symbol, layer_group)

def make_suits():
    dom = DOM(SVG_SRC_DIR + '/suits.svg')
    for suit in ['anvil', 'blades', 'crown', 'dragon']:
        name = 'suit_' + suit
        svg_fpath = '%s/%s.svg' % (BUILD_DIR, name)
        png_fpath = '%s/%s.png' % (BUILD_DIR, name)
        dom.layer_only_show(name)
        dom.write_file('%s/%s.svg' % (BUILD_DIR, name))
        export_png(svg_fpath, png_fpath, 200, 200)

def make_character_sheet():
    dom = DOM(SVG_SRC_DIR + '/character_sheet.svg')
    replace_symbol_with_layer(dom, 'xp_icon', 'xp_icon.svg', 'xp_icon')
    dom.write_file(BUILD_DIR + '/character_sheet.svg')

if __name__ == '__main__':
    ensure_dirs(BUILD_DIR)
    make_suits()
    make_character_sheet()
