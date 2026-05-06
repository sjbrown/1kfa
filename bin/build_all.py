#! /usr/bin/env python3

import os, sys

DEBUG = os.environ.get('DEBUG', 1)

def run(cmd):
    if DEBUG:
        print(cmd)
    status = os.system(cmd)
    if status != 0:
        print('Error', status)
        sys.exit(status)

run('pandoc --version')
run('bash bin/build_pdf_guides.sh')
run('cd resolution_cards; python3 process.py')
run('cd resolution_cards; python3 process_tall.py')
run('cd resolution_cards; python3 process_tenstep.py')
run('cd resolution_cards; python3 process_print_and_play.py')
run('bash bin/gzip_artifacts.sh')
