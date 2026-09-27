# -*- coding: utf-8 -*-
"""Vol. 2: toglie dalla sezione Inventore i paragrafi vuoti di riempimento (quelli che il manuale singolo non ha).
Servivano a spingere i titoli a inizio pagina; dopo le aggiunte finirebbero a metà pagina creando buchi.
Uso: python3 rimuovi_riempitivi.py <document.xml Vol.2> <document.xml manuale singolo originale> <inizio Vol.2> <fine Vol.2>
"""
import sys, difflib
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
def tx(e): return ''.join(t.text or '' for t in e.iter('{%s}t' % W))
def key(e): return etree.QName(e).localname + ':' + tx(e)

vt = etree.parse(sys.argv[1]); vb = vt.getroot().find('w:body', NS)
sb = etree.parse(sys.argv[2]).getroot().find('w:body', NS)
a, b = int(sys.argv[3]), int(sys.argv[4])
V = list(vb)[a:b]; S = list(sb)[19:887]
sm = difflib.SequenceMatcher(None, [key(e) for e in S], [key(e) for e in V], autojunk=False)
rm = []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op in ('insert', 'replace'):
        for e in V[j1:j2]:
            if etree.QName(e).localname == 'p' and not tx(e).strip() \
                    and e.find('.//w:br', NS) is None and e.find('.//w:sectPr', NS) is None \
                    and e.find('.//w:drawing', NS) is None:
                rm.append(e)
for e in rm:
    vb.remove(e)
vt.write(sys.argv[1], xml_declaration=True, encoding='UTF-8', standalone=True)
print('paragraphs di riempimento rimossi:', len(rm))
