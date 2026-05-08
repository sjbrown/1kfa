#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import shutil
from lxml import etree
from collections import defaultdict

sys.path.append('/usr/share/inkscape/extensions/')
from version import VERSION

DEBUG = int(os.environ.get('DEBUG', 0))
SINGLETON = object()
XLINK_NS='http://www.w3.org/1999/xlink'
SVG_NS="http://www.w3.org/2000/svg"

def run(cmd):
    if DEBUG:
        print (cmd)
    os.system(cmd)

def just_basename(fpath):
    return os.path.splitext(os.path.basename(fpath))[0]

def ensure_dirs(filepath):
    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

def export_png(svg, png, width, height, references=None):
    build_dir = '/tmp'
    if references is None:
        references = []
    for fname in references:
        dirname = os.path.dirname(svg)
        shutil.copy(f'{dirname}/{fname}', f'{build_dir}')

    ensure_dirs(png)

    png_fname = f'{build_dir}/content.svg'
    cmd = f'sed -e "s/VERSION/{VERSION}/" {svg} > {png_fname}'
    run(cmd)

    cmd = f'inkscape --export-type=png --export-filename={png} --export-width={width} --export-height={height} {png_fname}'
    run(cmd)

def export_pdf(svg, pdf):
    ensure_dirs(pdf)

    cmd_fmt = 'inkscape --export-pdf=%s %s'
    cmd = cmd_fmt % (pdf, svg)
    run(cmd)

def export_square_png(svg, png):
    return export_png(svg, png, 825, 825)

def export_tall_png(svg, png, references=None):
    return export_png(svg, png, 825, 1125, references)

CHAR_WIDTHS = {
    '+': 2.2, '-': 2.2, '*': 2.2, '?': 2.0,
    'W': 2.1, 'M': 2.1,
    'Y': 2.0, 'A': 2.0, 'C': 2.0, 'D': 2.0, 'N': 2.0,
    'O': 2.0, 'U': 2.0, 'R': 2.0, 'H': 2.0,
    'w': 2.0, 'm': 2.0,
    'o': 1.2, 'b': 1.2, 'd': 1.2, 'p': 1.2, 'g': 1.2,
    'i': 0.5, 'l': 0.5, '|': 0.5, '!': 0.5,
    "'": 0.5, ',': 0.5, '.': 0.5, ';': 0.5, ':': 0.5,
    'f': 0.7, 'r': 0.7, 't': 0.7,
    ' ': 1.0,
}

def char_width(c):
    return CHAR_WIDTHS.get(c, 1.0)

def word_width(word):
    return sum(char_width(c) for c in word)

def analyze_text(newtext):
    """
    Analyze newtext for weighted visual width, one entry per line.

    Characters are assigned proportional weights: wide characters like 'W'
    and 'm' count as 2.0; narrow characters like 'i' and '.' count as 0.5;
    spaces count as 1.0; most characters count as 1.0. Hard newlines are
    respected as line boundaries.

    Returns a list of dicts, one per input line:
      - 'words':          list of (word_str, weighted_width) pairs
      - 'weighted_width': total weighted width (words + inter-word spaces)
      - 'word_count':     number of words on the line
      - 'char_count':     raw character count (excluding the newline itself)

    Examples:

        >>> analyze_text("Roll with advantage.")
        [{'words': [('Roll', 3.0), ('with', 4.2), ('advantage.', 9.2)],
          'weighted_width': 18.4, 'word_count': 3, 'char_count': 20}]

        >>> analyze_text("Mill")   # all wide/narrow chars
        [{'words': [('Mill', 3.5)], 'weighted_width': 3.5,
          'word_count': 1, 'char_count': 4}]

        >>> analyze_text("Illuminate the Wound\\nwith Willpower.")
        [{'words': [('Illuminate', 9.2), ('the', 2.7), ('Wound', 6.0)],
          'weighted_width': 19.9, 'word_count': 3, 'char_count': 20},
         {'words': [('with', 4.2), ('Willpower.', 9.7)],
          'weighted_width': 14.9, 'word_count': 2, 'char_count': 15}]
    """
    results = []
    for line in newtext.split('\n'):
        words = line.split()
        word_widths = [(w, word_width(w)) for w in words]
        space_total = char_width(' ') * max(0, len(words) - 1)
        weighted_width = sum(ww for _, ww in word_widths) + space_total
        results.append({
            'words': word_widths,
            'weighted_width': weighted_width,
            'word_count': len(words),
            'char_count': len(line),
        })
    return results

def wrap_text(newtext, capacity):
    """
    Split newtext into lines where each line's weighted_width <= capacity.
    Hard newlines in newtext are treated as mandatory line breaks.

    Returns a list of line strings.

    Examples:

        >>> wrap_text("Roll with advantage.", 20)
        ['Roll with advantage.']

        >>> wrap_text("When you Withdraw from a fight, say how you get away.", 20)
        ['When you Withdraw', 'from a fight, say', 'how you get away.']

        >>> wrap_text("Illuminate the Wound\\nwith Willpower.", 20)
        ['Illuminate the Wound', 'with Willpower.']
    """
    output_lines = []

    for input_line in analyze_text(newtext):
        current_words = []
        current_width = 0.0

        for word, ww in input_line['words']:
            space = char_width(' ') if current_words else 0.0
            if current_words and current_width + space + ww > capacity:
                output_lines.append(' '.join(current_words))
                current_words = [word]
                current_width = ww
            else:
                current_words.append(word)
                current_width += space + ww

        if current_words:
            output_lines.append(' '.join(current_words))

    return output_lines


def format_text_to_tspans(text, keywordFormats):
    """
    keywordFormats looks like this: {
        'Stamina': {'style': "font-weight:bold", 'dx': '3.0' },
        'Harm':    {'style': "font-weight:bold", 'dx': '4.0' },
    }
    """
    allTspans = []
    currentTspan = etree.fromstring('<tspan></tspan>')
    for word in text.split():

        head = ''
        for key in keywordFormats:
            if word[:len(key)] == key:
                head = word[:len(key)]
                tail = word[len(key):]
                break

        if not head:
            orig_text = currentTspan.text or ''
            currentTspan.text = orig_text + word + ' '
            continue

        allTspans.append(currentTspan)
        formattedTspan = etree.fromstring('<tspan></tspan>')
        formattedTspan.text = head
        for attrName, attrVal in keywordFormats[head].items():
            formattedTspan.attrib[attrName] = attrVal
        allTspans.append(formattedTspan)
        currentTspan = etree.fromstring('<tspan></tspan>')
        currentTspan.text = tail + ' '

    allTspans.append(currentTspan)
    return allTspans


def change_text_text(elem, newtext):
    #print('change text', newtext[:10], '...')
    tspan = [x for x in elem.iterchildren()
                if 'tspan' in x.tag][0]
    tspan.text = newtext

KEYWORD_FORMATS = {
    'Stamina':       {'style': 'text-decoration:underline;text-decoration-color:#e0e0e0', 'dx': '13.0 0 5'},
    'Harm':          {'style': 'text-decoration:underline;text-decoration-color:#c17cd5', 'dx': '4.0'},
    'Wound':         {'style': 'text-decoration:underline;text-decoration-color:#0f0000', 'dx': '4.0'},
    'Str':           {'style': 'font-family:OptimusPrinceps'},
    'Int':           {'style': 'font-family:OptimusPrinceps'},
    'Dex':           {'style': 'font-family:OptimusPrinceps'},
    'PACK':          {'style': 'font-family:OptimusPrinceps'},
    'advantage':     {'fill': '#003a00'},
    'Advantage':     {'fill': '#003a00'},
    'disadvantage':  {'fill': '#3f0000'},
    'Disadvantage':  {'fill': '#3f0000'},
    '____':          {'fill': '#ffffff', 'style': 'text-decoration:underline;text-decoration-color:#000000'},
    'More Power':    {'style': 'text-decoration:underline;text-decoration-color:#00a000'},
}

def flowroot_text_force_width(flowroot, text, style):
    print('----')
    print(text)
    print('----')
    raise ValueError('#'*50)

def change_flowroot_text(flowroot, newtext, style, max_lines=None, capacity=None):

    print(f'  MAXLINES {max_lines}   CAP {capacity}')

    def _font_size(style, flowpara):
        """Read font-size from flowPara style attribute. Returns float (px)."""
        m = re.search(r'([\d.]+)px', style.get('font-size', ''))
        if not m:
            print('no style font size')
            m = re.search(r'font-size:\s*([\d.]+)px', flowpara.attrib.get('style', ''))
        if m:
            print(f'font size {m.group(1)}')
            return float(m.group(1))
        raise ValueError("Could not get font size")

    flowpara = [x for x in flowroot.iterchildren() if 'flowPara' in x.tag][0]

    # Extract capacity and max lines from the placeholder text.
    placeholder = flowpara.text or ''
    if max_lines == None:
        lines_match = re.search(r'lines:(\d+)', placeholder)
        if lines_match:
            max_lines = int(lines_match.group(1))
        else:
            max_lines = 1
    if not capacity:
        capacity = len(placeholder)

    autowrap_text = wrap_text(newtext, capacity)
    print(autowrap_text)
    estimated_wraps = len(autowrap_text)
    if estimated_wraps > max_lines:
        FONT_SIZE_STEP = 2.0  # px reduction per retry
        current_size = _font_size(style, flowpara)
        next_size = current_size - FONT_SIZE_STEP
        if next_size <= 8.0:
            return flowroot_text_force_width(flowroot, autowrap_text, style)
        ratio = current_size / next_size
        next_max_lines = int(max_lines * (ratio + .1))
        next_capacity = int(capacity * (ratio + .12))
        msg = (
            f'\n===\n'
            f'Text too long: wraps to {estimated_wraps} lines\n'
            f'  font-size {current_size}px → next {next_size}px\n'
            f'  max lines {max_lines} → {next_max_lines}\n'
            f'  capacity {capacity} →  {next_capacity}'
        )
        print(msg)
        style.update({'font-size': f'{next_size}px'})
        return change_flowroot_text(flowroot, newtext, style,
            next_max_lines, next_capacity)

    flowroot.remove(flowpara)
    for line in newtext.split('\n'):
        paraclone = etree.fromstring(etree.tostring(flowpara))
        paraclone.text = ''
        for tspan in format_text_to_tspans(line, KEYWORD_FORMATS):
            paraclone.append(tspan)
        if style:
            for k, v in style.items():
                paraclone.attrib['style'] = re.sub(
                    f'{k}:[^;]+',
                    f'{k}:{v};',
                    paraclone.attrib['style']
                )
        flowroot.append(paraclone)

def x_change_flowroot_text(flowroot, newtext, style):

    #print('change_flowroot_text', f'{locals()}', len(newtext))

    if not style.get('font-size'):
        if ideal_num_chars and len(newtext) < (ideal_num_chars / 1.5):
            # Make it bigger
            style.update({'font-size': '11px'})
        if ideal_num_chars and len(newtext) > (ideal_num_chars):
            # Make it smaller
            style.update({'font-size': '9px'})
        if ideal_num_chars and len(newtext)*2 > (ideal_num_chars):
            # Make it EVEN SMALLER
            style.update({'font-size': '7px'})

    flowpara = [x for x in flowroot.iterchildren()
                if 'flowPara' in x.tag][0]
    flowroot.remove(flowpara)
    for i, line in enumerate(newtext.split('\n')):
        paraclone = etree.fromstring(etree.tostring(flowpara))
        paraclone.text = ''

        #for tspan in format_text_to_tspans(line, keywordFormats):
        for tspan in format_text_to_tspans(line, {
                'Stamina': {'style': "text-decoration:underline;text-decoration-color:#e0e0e0", 'dx': '13.0 0 5' },
                'Harm':    {'style': "text-decoration:underline;text-decoration-color:#c17cd5", 'dx': '4.0' },
                'Wound':   {'style': "text-decoration:underline", 'fill':"#0f0000", 'dx': '4.0' },
                'Str':   {'style': "font-family:OptimusPrinceps" },
                'Int':   {'style': "font-family:OptimusPrinceps" },
                'Dex':   {'style': "font-family:OptimusPrinceps" },
                'PACK':   {'style': "font-family:OptimusPrinceps" },
                'Encumbrance':   {'style': "text-decoration:underline" },
                'advantage':   {'fill': "#003a00" },
                'Advantage':   {'fill': "#003a00" },
                'disadvantage':   {'fill': "#3f0000" },
                'Disadvantage':   {'fill': "#3f0000" },
                '____':   {'fill': "#ffffff", 'style': "text-decoration:underline;text-decoration-color:#000000" },
                'More Power':   {'style': "text-decoration:underline;text-decoration-color:#00a000" },
                }):
            paraclone.append(tspan)
        if style:
            #print('got style', style)
            for k,v in style.items():
                #print('doing', k,v)
                paraclone.attrib['style'] = re.sub(
                  f'{k}:[^;]+',
                  f'{k}:{v};',
                  paraclone.attrib['style']
                )
                #print('pcs', paraclone.attrib['style'])

        flowroot.append(paraclone)
    num_lines = i


def get_attrib(node, attr, default=SINGLETON):
    for ns in [''] + list(node.nsmap.values()):
        key = '{%s}%s' % (ns, attr)
        try:
            x = node.attrib[key]
        except:
            continue
        return x
    if default == SINGLETON:
        raise Exception('attribute %s not found in node %s' % (attr, node))
    else:
        return default

def set_attrib(node, attr, val):
    for ns in [''] + node.nsmap.values():
        key = '{%s}%s' % (ns, attr)
        try:
            if val is None:
                del node.attrib[key]
            else:
                node.attrib[key] = val
            return
        except KeyError:
            continue
    if val != None:
        node.attrib[attr] = val

def get_elems(node, tag):
    for ns in [''] + node.nsmap.values():
        key = '{%s}%s' % (ns, tag)
        x = node.findall(key)
        if x:
            return x
    raise Exception('elements "%s" not found in node %s' % (attr, node))

class DOM(object):
    def __init__(self, svg_filename):
        self._local_dir = os.path.dirname(svg_filename) or '.'
        with open(svg_filename, 'rb') as fp:
          c = fp.read()
        c = c.replace(b'VERSION', bytes(VERSION, 'utf-8'))
        self.dom = etree.fromstring(c)
        self.titles = [x for x in self.dom.getiterator()
                       if x.tag == '{http://www.w3.org/2000/svg}title']
        self.title_to_elements = defaultdict(list)
        for t in self.titles:
            self.title_to_elements[t.text].append(t.getparent())
        self.layers = {
            x.attrib['{http://www.inkscape.org/namespaces/inkscape}label'] : x
            for x in self.dom.iter()
            if x.attrib.get('{http://www.inkscape.org/namespaces/inkscape}groupmode') == 'layer'
        }
        self.references = []

    def layer_hide(self, layer_label):
        if DEBUG:
            print( 'HIDING LAYER', layer_label, 'OF', self.layers.keys())
        self.layers[layer_label].attrib['style'] = 'display:none'

    def layer_show(self, layer_label):
        self.layers[layer_label].attrib['style'] = 'display:inline'

    def layer_only_show(self, layer_label):
        for current in self.layers:
            if current == layer_label:
                self.layers[current].attrib['style'] = 'display:inline'
            else:
                self.layers[current].attrib['style'] = 'display:none'

    def svg_to_symbol(self, symbol_id):
        svg_node = self.dom.getiterator().next()
        #print( 'defs', get_elems(svg_node, 'defs'))
        [ svg_node.remove(e) for e in get_elems(svg_node, 'defs') ]
        [ svg_node.remove(e) for e in get_elems(svg_node, 'namedview') ]
        [ svg_node.remove(e) for e in get_elems(svg_node, 'metadata') ]
        dom = etree.fromstring('<symbol x="0" y="0" width="10" height="10" />')
        for elem in svg_node.getchildren():
            svg_node.remove(elem)
            dom.append(elem)
        set_attrib(dom, 'id', symbol_id)
        for elem in dom.getiterator():
            old_id = get_attrib(elem, 'id', None)
            if old_id:
                set_attrib(elem, 'id', symbol_id + '_' + old_id)
        return dom

    def by_id(self, node_id):
        for elem in self.dom.getiterator():
            if get_attrib(elem, 'id', None) == node_id:
                return elem
        raise KeyError('ID not found: %s' % node_id)

    def insert_use_symbol(self, pos_elem_id, use_href):
        pos_elem = self.by_id(pos_elem_id)
        cx = float(pos_elem.get('cx')) - 10
        cy = float(pos_elem.get('cy')) - 10

        nsmap = {None: SVG_NS, 'xlink': XLINK_NS}
        use = etree.Element(f"{{{SVG_NS}}}use", nsmap=nsmap)
        use.set(f"{{{XLINK_NS}}}href", use_href)
        
        wrapper = etree.Element(f"{{{SVG_NS}}}g", nsmap=nsmap)
        wrapper.set("transform", f"translate({cx},{cy})")
        wrapper.append(use)

        pos_elem.addnext(wrapper)
        fname, anchor = use_href.split('#')
        self.references.append(fname)



    def insert_layer_as_symbol(self, layer_name):
        fpath, layer_label = uri.split('#')
        if not os.path.isabs(fpath):
            fpath = os.path.join(self._local_dir, fpath)
        s_dom = DOM(fpath)
        orig_width = get_attrib(s_dom.dom, 'viewBox').split()[2]
        orig_height = get_attrib(s_dom.dom, 'viewBox').split()[3]
        symbol = s_dom.layers[layer_label]
        print( '')
        print( 'symbol')
        print( '-------------------------')
        print( etree.tostring(symbol))
        symbol_id = layer_label
        symbol.attrib['id'] = symbol_id
        set_attrib(symbol, 'x', '0')
        set_attrib(symbol, 'y', '0')
        set_attrib(symbol, 'label', None)
        set_attrib(symbol, 'groupmode', None)
        set_attrib(symbol, 'data-orig-width', orig_width)
        set_attrib(symbol, 'data-orig-height', orig_height)
        self.layers['symbols'].append(symbol)
        return symbol_id

    def replace_nodes_with_symbols(self, symbol_id):
        symbol = self.by_id(symbol_id)
        #print( 'syid', symbol_id)
        #print( 'keys', self.title_to_elements.keys())
        for key in self.title_to_elements.keys():
            if not (key.startswith('use-') and key.endswith(symbol_id)):
                continue
            for node in self.title_to_elements[key]:
                #print( '')
                #print( key)
                #print( '-------------------------')
                #print( etree.tostring(node))
                old_width = float(get_attrib(node, 'width'))
                old_height = float(get_attrib(node, 'height'))
                symbol_width = float(get_attrib(symbol, 'data-orig-width'))
                symbol_height = float(get_attrib(symbol, 'data-orig-height'))
                #print( old_width, old_height, symbol_width, symbol_height)
                xpct = '%3.3f%%' % (symbol_width / old_width)
                ypct = '%3.3f%%' % (symbol_height / old_height)
                newnode = etree.SubElement(node.getparent(), 'use')
                #'<use x="0" y="0" width="100%" height="100%" xlink:href="" />'
                newnode.attrib['id'] = 'clone_' + symbol_id
                newnode.attrib['{%s}href' % XLINK_NS] = '#' + symbol_id
                set_attrib(newnode, 'x', get_attrib(node, 'x'))
                set_attrib(newnode, 'y', get_attrib(node, 'y'))
                set_attrib(newnode, 'width', xpct)
                set_attrib(newnode, 'height', ypct)
                node.getparent().replace(node, newnode)

    def cut_element(self, title):
        for e in self.title_to_elements[title]:
            e.getparent().remove(e)

    def cut_element_by_id(self, elem_id):
        e = self.by_id(elem_id)
        e.getparent().remove(e)

    def cut_layer(self, layer_label):
        e = self.layers[layer_label]
        if e.getparent() is not None:
            e.getparent().remove(e)

    def add_layer(self, layerNode):
        assert layerNode.tag == 'g'
        label = layerNode.attrib['{http://www.inkscape.org/namespaces/inkscape}label']
        self.dom.append(layerNode)
        self.layers[label] = layerNode

    def replace_text(
        self,
        title,
        newtext,
        style=None,
        keywordFormats=None
    ):
        if style is None:
            style = {}
        if keywordFormats is None:
            keywordFormats = {}

        for elem in self.title_to_elements[title]:
            if 'flowRoot' in elem.tag:
                change_flowroot_text(elem, newtext, style)
            elif 'text' in elem.tag:
                change_text_text(elem, newtext)
            else:
                raise Exception('what the fuc')

    def replace_h1(self, newtext, style=None):
        if style is None:
            style = {}
        if len(newtext) >= 17:
            words = newtext.split()
            midpoint = int(len(words)/2)
            line1 = ' '.join(words[:midpoint])
            line2 = ' '.join(words[midpoint:])
            newtext = line1 + '\n' + line2
            style = { 'font-size': '16px', 'line-height': '0.8' }
        return self.replace_text('h1', newtext, style=style)

    def write_file(self, svg_filename):
        dirname = os.path.dirname(svg_filename)
        if DEBUG:
            print('writing file(s)...')
            print(svg_filename)
            print(self.references)
        fp = open(svg_filename, 'w')
        fp.write(str(etree.tostring(self.dom), 'utf-8'))
        fp.close()
        for fname in self.references:
            shutil.copy(fname, f'{dirname}/{fname}')



if __name__ == '__main__':
    test()
