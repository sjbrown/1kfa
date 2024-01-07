#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import os, sys

filename = sys.argv[1]

fp = open(filename)
c = fp.read()
fp.close()

c = c.replace('DATE', time.asctime())
c = c.replace('*FAST*', '![FAST](images/fast.png)')
c = c.replace('✗', '![X symbol](images/result_0.png)')

c = c.replace('✔✔✔', '![triple check](images/result_3.png)')
c = c.replace('✔✔', '![double check](images/result_2.png)')
c = c.replace('✔', '![single check](images/result_1.png)')
c = c.replace('\xef\xb8\x8e', '')
c = c.replace('✅', '![single check](images/result_1.png)')

c = c.replace('mod_guide_player.md', '1kfa_guide_player.html')
c = c.replace('mod_guide_gm.md', '1kfa_guide_gm.html')

lines = []
for line in c.split('\n'):
    if line.startswith('![') and line.endswith('}'):
        lines.append('<div class="floatimage">')
        lines.append(line)
        lines.append('</div>')
    else:
        lines.append(line)

c = '\n'.join(lines)

fp = open(filename, 'w')
fp.write(c)
fp.close()

