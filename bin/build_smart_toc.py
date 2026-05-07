#! /usr/bin/env python3

import sys
from pathlib import Path
from bs4 import BeautifulSoup


def transform_toc(soup):
    nav = soup.find('nav', id='TOC')
    if not nav:
        return

    for li in nav.find_all('li'):
        child_ul = li.find('ul', recursive=False)
        if not child_ul:
            continue

        a = li.find('a', recursive=False)
        if not a:
            continue

        details = soup.new_tag('details')
        summary = soup.new_tag('summary')

        a.extract()
        child_ul.extract()

        summary.append(a)
        details.append(summary)
        details.append(child_ul)

        li.append(details)


for path in sys.argv[1:]:
    p = Path(path)
    soup = BeautifulSoup(p.read_text(encoding='utf-8'), 'html.parser')
    transform_toc(soup)
    p.write_text(str(soup), encoding='utf-8')
    print(f'processed {path}')
