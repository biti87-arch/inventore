import sys, re
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ns={'w':W}
def txt(el): return ''.join(el.itertext()) if False else ''.join(t.text or '' for t in el.iter('{%s}t'%W))
tree=etree.parse(sys.argv[1]); body=tree.getroot().find('w:body',ns)
for i,el in enumerate(body):
    tag=etree.QName(el).localname
    if tag=='p':
        print(i,'P',txt(el))
    elif tag=='tbl':
        rows=el.findall('w:tr',ns)
        print(i,'TBL',len(rows),'rows')
        for r in rows:
            print('    |',' | '.join(txt(c) for c in r.findall('w:tc',ns)))
    else: print(i,tag)
