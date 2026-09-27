# -*- coding: utf-8 -*-
"""Vol. 2: sposta di DELTA i numeri di pagina dell'indice generale dalla voce indicata in poi.
Uso: python3 aggiorna_indice.py <document.xml> "<prima voce da spostare>" <delta>
"""
import sys
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
tree = etree.parse(sys.argv[1]); body = tree.getroot().find('w:body', NS)
first, delta = sys.argv[2], int(sys.argv[3])
sdt = next(e for e in body if etree.QName(e).localname == 'sdt'
           and 'TOC' in ''.join(x.text or '' for x in e.iter('{%s}instrText' % W)))
on = False; n = 0
for p in sdt.iter('{%s}p' % W):
    ts = list(p.iter('{%s}t' % W))
    if not ts:
        continue
    if ''.join(t.text or '' for t in ts).startswith(first):
        on = True
    if on and ts[-1].text and ts[-1].text.strip().isdigit():
        old = ts[-1].text; ts[-1].text = str(int(old) + delta); n += 1
tree.write(sys.argv[1], xml_declaration=True, encoding='UTF-8', standalone=True)
print('voci dell\'indice aggiornate:', n)
