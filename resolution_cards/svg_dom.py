#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from lxml import etree
from collections import defaultdict

sys.path.append('/usr/share/inkscape/extensions/')
from version import VERSION

DEBUG = int(os.environ.get('DEBUG', 0))
SINGLETON = object()
XLINK='http://www.w3.org/1999/xlink'

def run(cmd):
    if DEBUG:
        print cmd
    os.system(cmd)

def just_basename(fpath):
    return os.path.splitext(os.path.basename(fpath))[0]

def ensure_dirs(filepath):
    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

def export_png(svg, png, width, height):
    ensure_dirs(png)

    cmd = 'sed -e "s/VERSION/%s/" %s > /tmp/content.svg' % (VERSION, svg)
    run(cmd)

    cmd_fmt = 'inkscape --export-png=%s --export-width=%s --export-height=%s %s'
    cmd = cmd_fmt % (png, width, height, '/tmp/content.svg')
    run(cmd)

def export_pdf(svg, pdf):
    ensure_dirs(pdf)

    cmd_fmt = 'inkscape --export-pdf=%s %s'
    cmd = cmd_fmt % (pdf, svg)
    run(cmd)

def export_square_png(svg, png):
    return export_png(svg, png, 825, 825)

def export_tall_png(svg, png):
    return export_png(svg, png, 825, 1125)

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
    tspan = [x for x in elem.iterchildren()
                if 'tspan' in x.tag][0]
    tspan.text = newtext

def change_flowroot_text(flowroot, newtext, style, ideal_num_chars):
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
                'Wound':   {'style': "text-decoration:underline;text-decoration-color:#0f0000", 'dx': '4.0' },
                'Str':   {'style': "font-family:OptimusPrinceps" },
                'Int':   {'style': "font-family:OptimusPrinceps" },
                'Dex':   {'style': "font-family:OptimusPrinceps" },
                'PACK':   {'style': "font-family:OptimusPrinceps" },
                'advantage':   {'fill': "#003a00" },
                'Advantage':   {'fill': "#003a00" },
                'disadvantage':   {'fill': "#3f0000" },
                'Disadvantage':   {'fill': "#3f0000" },
                '____':   {'fill': "#ffffff", 'style': "text-decoration:underline;text-decoration-color:#000000" },
                'More Power':   {'style': "text-decoration:underline;text-decoration-color:#00a000" },
                }):
            paraclone.append(tspan)

        flowroot.append(paraclone)
    num_lines = i

    if ideal_num_chars and len(newtext) < (ideal_num_chars / 1.5):
        # Make it bigger
        style.update({'font-size': '11px'})
    if ideal_num_chars and len(newtext) > (ideal_num_chars - num_lines*20):
        # Make it smaller
        style.update({'font-size': '9px'})

    if style:
        for k,v in style.items():
            flowroot.attrib['style'] = re.sub(
              k+':[^;]+;',
              k+':'+v+';',
              flowroot.attrib['style']
            )

def get_attrib(node, attr, default=SINGLETON):
    for ns in [''] + node.nsmap.values():
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
    def __init__(self, svg_file):
        self._local_dir = os.path.dirname(svg_file) or '.'
        fp = file(svg_file)
        c = fp.read()
        c = c.replace('VERSION', VERSION)
        fp.close()
        self.dom = etree.fromstring(c)
        self.titles = [x for x in self.dom.getiterator()
                       if x.tag == '{http://www.w3.org/2000/svg}title']
        self.title_to_elements = defaultdict(list)
        for t in self.titles:
            self.title_to_elements[t.text].append(t.getparent())
        self.layers = {
            x.attrib['{http://www.inkscape.org/namespaces/inkscape}label'] : x
            for x in self.dom.getchildren()
            if x.attrib.get('{http://www.inkscape.org/namespaces/inkscape}groupmode') == 'layer'
        }

    def layer_hide(self, layer_label):
        if DEBUG:
            print 'HIDING LAYER', layer_label, 'OF', self.layers.keys()
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
        print 'defs', get_elems(svg_node, 'defs')
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

    def insert_layer_as_symbol(self, layer_name):
        fpath, layer_label = uri.split('#')
        if not os.path.isabs(fpath):
            fpath = os.path.join(self._local_dir, fpath)
        s_dom = DOM(fpath)
        orig_width = get_attrib(s_dom.dom, 'viewBox').split()[2]
        orig_height = get_attrib(s_dom.dom, 'viewBox').split()[3]
        symbol = s_dom.layers[layer_label]
        print ''
        print 'symbol'
        print '-------------------------'
        print etree.tostring(symbol)
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
        print 'syid', symbol_id
        print 'keys', self.title_to_elements.keys()
        for key in self.title_to_elements.keys():
            if not (key.startswith('use-') and key.endswith(symbol_id)):
                continue
            for node in self.title_to_elements[key]:
                print ''
                print key
                print '-------------------------'
                print etree.tostring(node)
                old_width = float(get_attrib(node, 'width'))
                old_height = float(get_attrib(node, 'height'))
                symbol_width = float(get_attrib(symbol, 'data-orig-width'))
                symbol_height = float(get_attrib(symbol, 'data-orig-height'))
                print '3333333333333'
                print old_width, old_height, symbol_width, symbol_height
                xpct = '%3.3f%%' % (symbol_width / old_width)
                ypct = '%3.3f%%' % (symbol_height / old_height)
                newnode = etree.SubElement(node.getparent(), 'use')
                #'<use x="0" y="0" width="100%" height="100%" xlink:href="" />'
                newnode.attrib['id'] = 'clone_' + symbol_id
                newnode.attrib['{%s}href' % XLINK] = '#' + symbol_id
                set_attrib(newnode, 'x', get_attrib(node, 'x'))
                set_attrib(newnode, 'y', get_attrib(node, 'y'))
                set_attrib(newnode, 'width', xpct)
                set_attrib(newnode, 'height', ypct)
                node.getparent().replace(node, newnode)

    def cut_element(self, title):
        for e in self.title_to_elements[title]:
            e.getparent().remove(e)

    def cut_layer(self, layer_label):
        e = self.layers[layer_label]
        if e.getparent():
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
        ideal_num_chars=None,
        style=None,
        keywordFormats=None
    ):
        if style is None:
            style = {}
        if keywordFormats is None:
            keywordFormats = {}

        for elem in self.title_to_elements[title]:
            if 'flowRoot' in elem.tag:
                change_flowroot_text(elem, newtext, style, ideal_num_chars)
            elif 'text' in elem.tag:
                change_text_text(elem, newtext)
            else:
                raise Exception('what the fuc')

    def replace_h1(self, newtext):
        style = {}
        if len(newtext) >= 17:
            words = newtext.split()
            midpoint = len(words)/2
            line1 = ' '.join(words[:midpoint])
            line2 = ' '.join(words[midpoint:])
            newtext = line1 + '\n' + line2
            style = { 'font-size': '16px', 'line-height': '90%' }
        return self.replace_text('h1', newtext, style=style)

    def write_file(self, svg_filename):
        if DEBUG:
            print 'writing file...'
            print svg_filename
        fp = file(svg_filename, 'w')
        fp.write(etree.tostring(self.dom))
        fp.close()



if __name__ == '__main__':
    test()
