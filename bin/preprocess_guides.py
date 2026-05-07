#! /usr/bin/env python3

import time
import re
import os, sys

filename = sys.argv[1]

with open(filename, encoding='utf-8') as fp:
    c = fp.read()

c = re.sub(r'```journey_point_requirement.*?```', '', c, flags=re.DOTALL)

c = c.replace('DATE', time.asctime())
c = c.replace('*FAST*', '![FAST](images/fast.png)')
c = c.replace('✗', '![X symbol](images/result_0.png)')

c = c.replace('✔✔✔', '![triple check](images/result_3.png)')
c = c.replace('✔✔', '![double check](images/result_2.png)')
c = c.replace('✔', '![single check](images/result_1.png)')
c = c.replace('✓', '![single check](images/result_1.png)')
c = c.replace('\ufe0e', '')
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

with open(filename, 'w', encoding='utf-8') as fp:
    fp.write(c)
