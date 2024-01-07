#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import string
from pprint import pprint, pformat
from tall_cards import cards
from process_tall import filenamify
from version import VERSION

from svg_dom import DOM, export_pdf, export_tall_png

CARDSDIR = '/tmp/cards_v' + VERSION
OUTDIR = '/tmp/1kfa_pnp_build'
TEMPLATEDIR = os.environ.get('KFAREPO', '..') + '/resolution_cards'

DEBUG = int(os.environ.get('DEBUG', 1))

def write_pdf(suffix, raw):
    new_fname = OUTDIR + '/print_and_play_%s.svg' % suffix
    new_pdf_name = OUTDIR + '/print_and_play_%s.pdf' % suffix
    print 'Writing', new_pdf_name
    fp = file(new_fname, 'w')
    fp.write(raw)
    fp.close()
    export_pdf(new_fname, new_pdf_name)

def process_subdir(subdirname, raw_svg):
    counter = 1
    dirpath = CARDSDIR + '/' + subdirname
    pngs = [
        x for x in os.listdir(dirpath)
        if (x.endswith('.png') and x != 'back.png')
    ]

    for i, fname in enumerate(sorted(pngs)):
        if (i % 9) == 0:
            raw_svg_copy = str(raw_svg)

        raw_svg_copy = raw_svg_copy.replace(
            'cards_vVERSION/%d' % ((i%9)+1) + '.png',
            dirpath + '/' + fname
        )

        if (i % 9) == 8:
            suffix = subdirname + '%02d' % counter
            write_pdf(suffix, raw_svg_copy)
            counter += 1

    if (i % 9) != 8:
        # Remove all remaining links
        raw_svg_copy = re.sub('xlink:href="cards_vVERSION/..png"', '', raw_svg_copy)
        suffix = subdirname + '%02d' % counter
        write_pdf(suffix, raw_svg_copy)


if __name__ == '__main__':
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    print('Removing dir')
    print('rm -rf %s/print_and_play*pdf' % OUTDIR)
    os.system('rm -rf %s/print_and_play*pdf' % OUTDIR)
    fp = file('%s/print_and_play_move_template.svg' % TEMPLATEDIR)
    template = fp.read()
    fp.close()

    for name in os.listdir(CARDSDIR):
        if not os.path.isdir(CARDSDIR + '/' + name):
            continue
        print('Processing', name)
        process_subdir(name, template)


    fname = '%s/print_and_play_deckahedron_template.svg' % TEMPLATEDIR
    new_pdf_name = OUTDIR + '/print_and_play_deckahedron.pdf'
    print 'Writing', new_pdf_name
    export_pdf(fname, new_pdf_name)

