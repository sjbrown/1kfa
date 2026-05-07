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
run('python3 resolution_cards/process_gm_cards.py mod_guide_gm.md /tmp/1kfa_gm_cards')
run('cd resolution_cards; python3 process_square.py')
run('cd resolution_cards; python3 process_tall.py')
run('cd resolution_cards; python3 process_print_and_play.py')
run('bash bin/gzip_artifacts.sh')

print("")
print("Now optionally publish:")
print("cp /tmp/1kfa_guide_build/1kfa_guide_*.* /a/work/files_1kfa_com/latest/")
print("cd /a/work/files_1kfa_com/; bash upload.sh")
