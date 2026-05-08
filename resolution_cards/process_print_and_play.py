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
    print( 'Writing', new_pdf_name)
    fp = open(new_fname, 'w')
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
    if not pngs:
        print(f'\nNO PNGS FOUND IN {dirpath}!\n')
        return

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

def process_move_card_faces():
    for name in os.listdir(CARDSDIR):
        subdir = f'{CARDSDIR}/{name}'
        if not os.path.isdir(subdir):
            continue
        print('Processing', name)
        cmd = f'python make_move_card_fronts.py --input-dir {subdir} --output-dir {CARDSDIR}'
        os.system(cmd)
    for name in os.listdir(CARDSDIR):
        if 'sheet' in name and name.endswith('svg'):
            svg_name = f'{CARDSDIR}/{name}'
            pdf_name = f'{OUTDIR}/{name}'[:-4] + '.pdf'
            print(f'Processing {svg_name} -> {pdf_name}')
            export_pdf(svg_name, pdf_name)

def process_deckahedron_card_faces():
    DH_DIR = '/tmp/cards_square/'
    print(f'Processing {DH_DIR}')
    cmd = f'python make_square_card_fronts.py --input-dir {DH_DIR} --output-dir {DH_DIR}'
    os.system(cmd)
    for name in os.listdir(DH_DIR):
        if 'sheet' in name and name.endswith('svg'):
            svg_name = f'{DH_DIR}/{name}'
            pdf_name = f'{OUTDIR}/{name}'[:-4] + '.pdf'
            print(f'Processing {svg_name} -> {pdf_name}')
            export_pdf(svg_name, pdf_name)

if __name__ == '__main__':
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    print('Removing dir')
    cmd = f'rm -rf {OUTDIR}/print_and_play*pdf'
    os.system(cmd)

    process_move_card_faces()
    process_deckahedron_card_faces()

    fname = f'{TEMPLATEDIR}/character_sheet.svg'
    new_pdf_name = f'{OUTDIR}/character_sheet.pdf'
    print(f'\nWriting {new_pdf_name}\n')
    export_pdf(fname, new_pdf_name)

    fname = f'{TEMPLATEDIR}/gm_sheet.svg'
    new_pdf_name = f'{OUTDIR}/gm_sheet.pdf'
    print(f'\nWriting {new_pdf_name}\n')
    export_pdf(fname, new_pdf_name)


