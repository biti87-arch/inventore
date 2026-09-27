# -*- coding: utf-8 -*-
"""Skitari e Tecnomante a somma zero (confermato il 27/09/2026 sera).
Si applica DOPO patch_inventore.py.
Uso: python3 patch2_skitari_tecnomante.py <document.xml> <inizio sezione Inventore>
"""
import sys, copy, re
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
XS = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def tx(e): return ''.join(t.text or '' for t in e.iter(q('t')))

DOC = sys.argv[1]; START = int(sys.argv[2])
tree = etree.parse(DOC); body = tree.getroot().find('w:body', NS)
def els(): return list(body)
def find(text, after=None, mode='eq'):
    L = els(); i0 = START if after is None else L.index(after) + 1
    for e in L[i0:]:
        if etree.QName(e).localname != 'p': continue
        s = tx(e)
        if (mode == 'eq' and s == text) or (mode == 'start' and s.startswith(text)):
            return e
    raise SystemExit('NON TROVATO: %r' % text)
def set_text(p, s):
    ts = list(p.iter(q('t')))
    ts[0].text = s; ts[0].set(XS, 'preserve')
    for t in ts[1:]:
        r = t.getparent(); r.getparent().remove(r)
def drop(*ps):
    for p in ps: p.getparent().remove(p)

def shade(p, word, fill):
    """Mette `word` in bianco su `fill` (vantaggio/svantaggio), spezzando il run."""
    for r in list(p.findall('w:r', NS)):
        t = r.find('w:t', NS)
        if t is None or not t.text: continue
        m = re.search(r'\b%s\b' % word, t.text)
        if not m: continue
        before, mid, after = t.text[:m.start()], m.group(0), t.text[m.end():]
        parts = []
        for s, hl in ((before, False), (mid, True), (after, False)):
            if not s: continue
            nr = copy.deepcopy(r); nt = nr.find('w:t', NS); nt.text = s; nt.set(XS, 'preserve')
            if hl:
                rpr = nr.find('w:rPr', NS)
                if rpr is None: rpr = etree.SubElement(nr, q('rPr')); nr.insert(0, rpr)
                c = rpr.find('w:color', NS)
                if c is None: c = etree.SubElement(rpr, q('color'))
                c.set(q('val'), 'FFFFFF')
                shd = etree.SubElement(rpr, q('shd')); shd.set(q('val'), 'clear'); shd.set(q('fill'), fill)
            parts.append(nr)
        for nr in parts: r.addprevious(nr)
        r.getparent().remove(r)
        return True
    return False

LOG = []
# ------------------------------------------------------------------ Tecnomante
ht = find('Tecnomante')
h_odio = find('Odio per la magia', ht); b_odio = h_odio.getnext()
set_text(b_odio, "Al 1° livello, un tecnomante considera Sapienza magica come abilità di classe al posto di Utilizzare "
                 "congegni magici. Inoltre, non può mai lanciare incantesimi, neanche come capacità magica. Infine, ottiene "
                 "+1 ai tiri per colpire e +2 ai danni contro gli incantatori, comprese le creature che lanciano "
                 "incantesimi come capacità magica.")
dic_tpl = find('Privilegio di classe sostituito: Tecno-armi al 1° livello.', ht)
d = copy.deepcopy(dic_tpl); ts = list(d.iter(q('t')))
if len(ts) == 2: ts[1].text = 'Fabbro esperto al 1° livello.'
else: ts[0].text = 'Privilegio di classe sostituito: Fabbro esperto al 1° livello.'
b_odio.addnext(d)
LOG.append('Tecnomante: Odio per la magia sostituisce Fabbro esperto al 1°; Utilizzare congegni magici')

# ------------------------------------------------------------------ Skitari
hs = find('Skitari', ht)
h_af = find('Arma da fuoco', hs); b_af = h_af.getnext()
h_ad = find('Addestramento con le armi da fuoco', hs); b_ad = h_ad.getnext()
h_rr = find('Riparazioni ridotte', hs); b_rr = h_rr.getnext()
assert tx(b_rr.getnext()) == 'Privilegio di classe modificato: Riparazioni al 1° livello.'
set_text(b_ad, "Al 1° livello, uno skitari ottiene un fucile o un revolver malconcio con 50 proiettili, che non può essere "
               "venduto, e il talento Ricarica rapida (armi da fuoco arcaiche, fucile, revolver). Quando usa le palle di "
               "carta come munizioni, il valore di inceppamento dell'arma non aumenta. Di contro, può usare riparazioni un "
               "numero di volte al giorno pari al bonus di Intelligenza, anziché 2 + bonus di Intelligenza.")
drop(h_af, b_af, h_rr, b_rr)
LOG.append('Skitari: Arma da fuoco + Addestramento + Riparazioni ridotte → Addestramento con le armi da fuoco (modifica Riparazioni)')

h_m1 = find('Maestria di armi sperimentali I', hs); b_m1 = h_m1.getnext(); d_m1 = b_m1.getnext()
assert tx(d_m1) == 'Privilegio di classe sostituito: Mechanus al 1° livello.'
bullet_tpl = find('• Al 5° livello, il raggio', ht, 'start')
h_m1.find('.//w:t', NS).text = 'Maestria di armi sperimentali'
set_text(b_m1, "Uno skitari affina l'uso delle armi sperimentali man mano che avanza di livello.")
BUL = [
    "1° livello: conta come di un livello superiore per l'attivazione delle armi sperimentali. Può attivare ciascuna "
    "arma sperimentale in suo possesso due volte al giorno, attendendo almeno 1 ora tra un utilizzo e l'altro.",
    "4° livello: la CD dei Tiri Salvezza provocati dalle sue armi sperimentali aumenta di 1. Ottiene bonus +2 ai tiri "
    "per colpire con l'elettro-carabina.",
    "7° livello: la CD aumenta ancora di 1 (totale +2).",
    "10° livello: conta come di due livelli superiore, anziché di uno, per l'attivazione delle armi sperimentali. Ciò "
    "aumenta di 2 anche il livello massimo dei danni inflitti dalle armi sperimentali.",
    "13° livello: tre volte al giorno, per quel turno, ottiene vantaggio ai tiri per colpire con l'elettro-carabina, "
    "oppure impone svantaggio ai Tiri Salvezza contro una sua arma sperimentale a scelta.",
    "16° livello: può attivare ciascuna arma sperimentale in suo possesso tre volte al giorno, attendendo almeno 1 ora "
    "tra un utilizzo e l'altro.",
]
anchor = b_m1
for s in BUL:
    p = copy.deepcopy(bullet_tpl); ts = list(p.iter(q('t')))
    ts[-1].text = s; ts[-1].set(XS, 'preserve')
    anchor.addnext(p); anchor = p
    if s.startswith('13°'):
        shade(p, 'vantaggio', '1E7A1E'); shade(p, 'svantaggio', 'C00000')
anchor.addnext(d_m1)   # la dicitura va dopo l'elenco
# rimuovo Maestria II–VI
for n in ['II', 'III', 'IV', 'V', 'VI']:
    h = find('Maestria di armi sperimentali ' + n, hs); drop(h.getnext(), h)
LOG.append('Skitari: Maestria I–VI unite in un solo privilegio progressivo (sostituisce Mechanus al 1°)')

# vantaggio dell'Androide (Coscienza distribuita) nello stile di sistema
p = find('Al 14° livello, la coscienza di un androide', hs, 'start')
if shade(p, 'vantaggio', '1E7A1E'): LOG.append('Androide: «vantaggio» in bianco su verde')

tree.write(DOC, xml_declaration=True, encoding='UTF-8', standalone=True)
print('\n'.join('✓ ' + l for l in LOG))
