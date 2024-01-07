import re
from itertools import izip_longest

def percent(num, den):
    return '%2.0f%%' % ((float(num)/den) * 100)

def parse(fname, level=2):
    f = file(fname)
    c = f.read()
    f.close()
    num_lines = len(c.split('\n'))
    headings = []
    print 'num lines', num_lines
    regexp = '#{1,%s}\s' % level
    for i, line in enumerate(c.split('\n')):
        if re.match(regexp, line):
            amount_through = percent(i, num_lines)
            headings.append( (amount_through, line) )
    return headings

def markdown(player, gm):
    collection = izip_longest(gm, player)
    for p, g, c in collection:
        pp = '%s %s' % (p or ('',''))
        gg = '%s %s' % (g or ('',''))
        cc = '%s %s' % (c or ('',''))
        print '| `%s` | `%s` | `%s` |' % (pp, gg, cc)

player = parse('mod_guide_player.md')
gm = parse('mod_guide_gm.md')

markdown(player, gm)
