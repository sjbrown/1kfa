#!/usr/bin/env python3

import string
import re, ast, sys
from pprint import pprint
from collections import defaultdict

class CaseInsensitiveDotDict(dict):
    def __init__(self, init_dict=None, **kwargs):
        super().__init__()
        init_dict = init_dict or {}
        # merge in both the passed dict and any kwargs
        for k, v in {**init_dict, **kwargs}.items():
            self[k] = v

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key.lower()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = key.lower()
        super().__setitem__(key, value)

    def __contains__(self, key):
        if isinstance(key, str):
            key = key.lower()
        return super().__contains__(key)

    def get(self, key, default=None):
        if isinstance(key, str):
            key = key.lower()
        return super().get(key, default)

    def __getattr__(self, name):
        # only called if normal attribute lookup fails
        if name in self:
            return self[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    #def __repr__(self):
        #return f"{type(self).__name__}({dict(self)})"

def parse_out_shadow_points(results):
    shadowpoint_pattern = re.compile(
        r'^(.*?)'            # (1) reluctantly grab all chars up to…
        r'\[('               # literal “ [ ” then start group(2)
          r'\S*shadow point' # any whitespace chars, then “shadow point”
          r'\S*'             # then more whitespace chars
        r')\]'               # close the bracket and the group
        r'(.*)',             # remainder goes in group (3)
        re.IGNORECASE,
    )

    shadow_points = {}
    new_results = {}
    
    for key, body in results.items():
        m = shadowpoint_pattern.search(body)
        if not m:
            shadow_points[key] = None
        else:
            body = m.group(1).strip() + ' ' + m.group(3).strip()
            shadow_points[key] = 'shadow point'
        new_results[key] = body

    return new_results, shadow_points

def parse_out_progress(results):
    progress_pattern = re.compile(
        r'^(.*?)'            # (1) reluctantly grab all chars up to…
        r'\[('               # literal “ [ ” then start group(2)
          r'[^\]]*?progress' # any non-] chars, then “progress”
          r'[^\]]*?'         # then more non-] chars, reluctantly
        r')\]'              # close the bracket and the group
        r'(.*)',             # remainder goes in group (3)
        re.IGNORECASE        # make “Progress” / “PROGRESS” match too
    )

    progress = {}
    new_results = {}
    
    for key, body in results.items():
        m = progress_pattern.search(body)
        if not m:
            progress[key] = None
        else:
            body = m.group(1).strip() + ' ' + m.group(3).strip()
            prog_str = m.group(2).strip().lower()
            if prog_str == 'gray progress':
                progress[key] = ['gray']
            elif prog_str == 'green progress':
                progress[key] = ['green']
            elif prog_str == 'gray progress, green progress':
                progress[key] = ['gray', 'green']
            elif prog_str == '2x green progress':
                progress[key] = ['green', 'green']
            else:
                raise Exception(f'Could not parse progress "{prog_str}"')
        new_results[key] = body

    return new_results, progress

def parse_detail_sections(text):
    """
    Splits on lines beginning '# ' to pull out each move's detail
    block.  Returns a dict:
      move_name -> {
         attrs: [...],
         flags: [...],
         levels: [...],
         results: { '✗':..., '✓':..., '✔':..., '✔✔':... },
         details: "full **Details**: text…"
      }
    """
    moves = re.split(r'(?m)^#\s+', text)[1:]
    detail_map = {}
    for move in moves:
        d = {}
        lines = move.splitlines()
        name = lines[0].strip()
        body = "\n".join(lines[1:])
        # grab python3 block
        m = re.search(r'```python3\s*(.*?)```', body, re.DOTALL)
        if not m:
            raise Exception(f'Could not find python attrs section for move {name}')
        block = m.group(1)
        def get_key_and_val(line):
            #print('l', line)
            m = re.search(r"(.+)\s*=\s*(.*)", line)
            key = m.group(1).strip().lower()
            val = ast.literal_eval(m.group(2))
            return key, val
        for py_line in block.split('\n'):
            if '=' not in py_line:
                continue
            key, val = get_key_and_val(py_line)
            d[key] = val

        # map levels → numeric m-keys and spots
        numeric = []
        for lvl in d.get('levels', []):
            if lvl.startswith('r'):
                numeric.append(-int(lvl[1:]))
            elif lvl.startswith('g'):
                numeric.append(int(lvl[1:]))
            else:
                numeric.append(0)
        for val, lvl in zip(numeric, d.get('levels', [])):
            key = f"m{val}"
            # star the 0-level
            valstr = str(val) + ('*' if lvl == '0' else '')
            d[key] = valstr
        d['spots'] = {v: [] for v in numeric}

        # grab flip results
        results = dict(re.findall(r'([✗✓✔]{1,2}): *(.*)\n', body))
        #print(f'\nresults {results}\n')
        results, progress = parse_out_progress(results)
        results, shadow_points = parse_out_shadow_points(results)
        # grab **Details** section
        dm = re.search(r'\*\*Details\*\*:\s*(.*)', body, re.DOTALL)
        details = dm.group(1).strip() if dm else ""
        detail_map[name] = {
            'title': name,
            'Deckahedron Move': name,
            'results': results,
            'progress': progress,
            'shadow_points': shadow_points,
            'details': details,
            'effect': details,
            'mod': d.get('attrs', ''),
            'attr': d.get('attrs', []),
            'notes': d.get('notes', ''),
            'tags': d.get('tags', []),
            'campaign': d.get('campaign'),
            'circles': d.get('circles', []),
            'component': d.get('component'),
            'reqs': d.get('reqs', []),
            'level_start': d.get('level_start'),
            'one_x':      results.get('✗', ''),
            'one_check':  results.get('✓', ''),
            'two_check':  results.get('✔', ''),
            'three_check':results.get('✔✔', ''),
        }
        detail_map[name].update(d)

    as_list = [CaseInsensitiveDotDict(x) for x in detail_map.values()]
    set_slugs(as_list)

    return sorted(as_list, key=lambda x: x.slug)

def component_type(card):
    if card.get('component'):
        return card.get('component')
    elif card.get('equipment'):
        return 'mundane_deck'
    else:
        return 'move_deck'

def filenamify(s):
    x = s.lower()
    l = [c for c in x if c in (' ' + string.ascii_lowercase)]
    x = ''.join(l)
    x = x.replace(' ', '_')
    return x

def set_slugs(cards):
    enumerations = defaultdict(dict)
    for card in cards:
        com = component_type(card)
        enumeration = enumerations[com]
        numbers = list(enumeration.keys())
        next_number = max([0] + numbers) + 1
        custom_number = int(card.get('custom_number', 0))
        if custom_number:
            found = enumeration.get(custom_number)
            if found:
                enumeration[next_number] = found
            enumeration[custom_number] = card
        else:
            enumeration[next_number] = card
    for com, enumeration in enumerations.items():
        for num, card in enumeration.items():
            groups = card.get('groups')
            if groups:
                group_slug = '_' + '_'.join(groups)
            else:
                group_slug = ''
            name_slug = filenamify(card['title'])
            card['slug'] =  f'{com}/face{group_slug}{num:02d}_{name_slug}'


def handy_moves(md_path):
    text = open(md_path, encoding='utf-8').read()
    return parse_detail_sections(text)

def main(md_path):
    text = open(md_path, encoding='utf-8').read()
    pprint(parse_detail_sections(text))


if __name__=='__main__':
    if len(sys.argv)<2:
        print("Usage: python3 parse_moves.py character_move_sheet.md")
        sys.exit(1)
    main(sys.argv[1])

