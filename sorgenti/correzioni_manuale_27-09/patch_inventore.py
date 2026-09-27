# -*- coding: utf-8 -*-
"""Correzioni mirate all'Inventore (decisioni del 27/09/2026, A-N).

Uso: python3 patch_inventore.py <document.xml da modificare> <document.xml del Vol. 2 (modelli tabelle)> [inizio]
Lavora per testo, non per indice, quindi vale sia per il manuale singolo sia per la sezione nel Vol. 2.
[inizio] = indice del corpo da cui parte la sezione Inventore (0 per il manuale singolo).
"""
import sys, copy, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)

DOC, TPL = sys.argv[1], sys.argv[2]
START = int(sys.argv[3]) if len(sys.argv) > 3 else 0
tree = etree.parse(DOC)
body = tree.getroot().find('w:body', NS)
tpl_body = etree.parse(TPL).getroot().find('w:body', NS)
LOG = []

def tx(e): return ''.join(t.text or '' for t in e.iter(q('t')))
def els(): return list(body)

def find(text, after=None, mode='eq', tag='p'):
    """Primo elemento (dopo `after`) il cui testo corrisponde."""
    L = els()
    i0 = START if after is None else L.index(after) + 1
    for e in L[i0:]:
        if etree.QName(e).localname != tag:
            continue
        s = tx(e)
        if (mode == 'eq' and s == text) or (mode == 'start' and s.startswith(text)) or (mode == 'in' and text in s):
            return e
    raise SystemExit('NON TROVATO: %r (dopo %r)' % (text, tx(after)[:40] if after is not None else None))

def repl(e, old, new, desc=None):
    """Sostituzione che attraversa i run conservando la formattazione del primo run coinvolto."""
    ts = list(e.iter(q('t')))
    full = ''.join(t.text or '' for t in ts)
    k = full.find(old)
    if k < 0:
        raise SystemExit('TESTO NON TROVATO: %r in %r' % (old, full[:120]))
    end = k + len(old); pos = 0; placed = False
    for t in ts:
        s = t.text or ''; a, b = pos, pos + len(s); pos = b
        if b <= k or a >= end:
            continue
        lo, hi = max(k, a) - a, min(end, b) - a
        if not placed:
            t.text = s[:lo] + new + s[hi:]; placed = True
        else:
            t.text = s[:lo] + s[hi:]
        t.set(XML_SPACE, 'preserve')
    LOG.append(desc or ('%s → %s' % (old, new)))

def set_parts(p, parts):
    """Assegna i testi ai w:t nell'ordine; i run in eccesso vengono rimossi."""
    for bm in list(p.iter(q('bookmarkStart'), q('bookmarkEnd'))):
        bm.getparent().remove(bm)
    ts = list(p.iter(q('t')))
    if len(parts) > len(ts):  # modello con meno run (es. dicitura in un solo run nel Vol. 2)
        parts = parts[:len(ts) - 1] + [''.join(parts[len(ts) - 1:])]
    for i, t in enumerate(ts):
        if i < len(parts):
            t.text = parts[i]; t.set(XML_SPACE, 'preserve')
        else:
            r = t.getparent(); r.getparent().remove(r)
    assert len(parts) <= len(ts), 'troppe parti per il modello'
    return p

def clone_after(ref, template, parts):
    new = set_parts(copy.deepcopy(template), parts)
    ref.addnext(new)
    return new

def cell(tbl, r, c):
    return tbl.findall('w:tr', NS)[r].findall('w:tc', NS)[c]

# ------------------------------------------------------------------ tabella di classe
tab = find("Tabella dell'Inventore").getnext()
while etree.QName(tab).localname != 'tbl':
    tab = tab.getnext()
repl(cell(tab, 9, 5), 'Pensiero tecnologico', 'Gadget, Pensiero tecnologico', 'Tabella: Gadget al 9°')
repl(cell(tab, 5, 5), 'Aggiornamento #1 delle meraviglie', 'Aggiornamento delle meraviglie')
repl(cell(tab, 10, 5), 'Aggiornamento #2 delle meraviglie', 'Aggiornamento delle meraviglie')
repl(cell(tab, 15, 5), 'Aggiornamento #3 delle meraviglie', 'Aggiornamento delle meraviglie')
repl(cell(tab, 20, 5), 'Aggiornamento finale delle meraviglie', 'Aggiornamento delle meraviglie')

# ------------------------------------------------------------------ privilegi
h = find('Privilegi di classe')
p = find('Al 1° livello e ad ogni livello pari di inventore', h, 'start')
repl(p, tx(p),
     "Al 1°, 3°, 5°, 7°, 9° e 11° livello, un inventore impara a costruire un nuovo gadget a sua scelta tra quelli "
     "disponibili, di cui soddisfa i requisiti. Ai livelli pari dal 2° al 18°, invece, sceglie un gadget, un optional "
     "o una dote da inventore. Vedi sezione dedicata per le regole complete e l'elenco dei gadget.",
     'Privilegio Gadget riscritto')
p = find('Al 15° livello (in concomitanza', h, 'start')
repl(p, "(in concomitanza con l'Aggiornamento #3 delle meraviglie)", "(in concomitanza con l'aggiornamento delle meraviglie del 15° livello)")
repl(p, "beneficia degli Aggiornamenti #3 (15° livello) e finale (20° livello); le altre meraviglie rimangono fissate all'Aggiornamento #2.",
     "beneficia degli aggiornamenti del 15° e del 20° livello; le altre meraviglie restano all'aggiornamento del 10° livello.")
p = find('Ai livelli 5°, 10°, 15° e 20°, un inventore migliora', h, 'start')
repl(p, "Gli Aggiornamenti #3 (15° livello) e finale (20° livello) si applicano solo alla meraviglia scelta come Specializzazione.",
     "Ogni meraviglia si aggiorna ai livelli indicati nella propria sezione: tecno-armi al 5°, 10°, 15° e 20°; automaton "
     "ed esoscheletri al 10°, 15° e 20°. Gli aggiornamenti del 15° e del 20° livello si applicano solo alla meraviglia "
     "scelta come Specializzazione.")
p = find('1. Brevetti:', h, 'start')
repl(p, "Le creazioni vengono apprese automaticamente al raggiungere il livello appropriato.",
     "Le creazioni vengono apprese automaticamente al raggiungere il livello appropriato. Fanno eccezione i mechanus: "
     "quelli conosciuti sono limitati dalla tabella Mechanus Conosciuti e si scelgono liberamente tra i livelli disponibili.")
p = find('2. Tipi di meraviglia:', h, 'start')
repl(p, 'per accedere agli Aggiornamenti #3 e finale.', 'per accedere agli aggiornamenti del 15° e del 20° livello.')

# ------------------------------------------------------------------ mechanus
hm = find('Mechanus', find('5. Aggiornamenti:', h, 'start'))
p = find("L'inventore segue la progressione standard", hm, 'start')
repl(p, tx(p),
     "Un inventore crea i mechanus come un incantatore fino al 6° livello: il numero di mechanus di ciascun livello che "
     "conosce e che può creare ogni giorno è indicato nelle tabelle Mechanus Conosciuti e Mechanus al Giorno. I mechanus "
     "conosciuti si scelgono liberamente tra quelli dei livelli disponibili, entro i limiti della tabella. Come per gli "
     "incantesimi bonus, un inventore con un alto punteggio di Intelligenza crea ogni giorno mechanus bonus, secondo la "
     "tabella Modificatori di caratteristica e incantesimi bonus del Vol. 1. I mechanus di 6° livello si ottengono al 16° livello.",
     'Mechanus: progressione del tier 6 e mechanus bonus')

# tabelle del tier 6 (colonne 1-6, senza colonna 0 e senza R) clonate dallo stile canonico del Vol. 2 (Bardo)
TL = list(tpl_body)
def tpl_find(text):
    for i, e in enumerate(TL):
        if tx(e) == text and i + 2 < len(TL) and etree.QName(TL[i + 2]).localname == 'tbl' \
                and len(TL[i + 2].findall('w:tblGrid/w:gridCol', NS)) == 8:
            return TL[i], TL[i + 1], TL[i + 2]
    raise SystemExit('modello tabella non trovato')

CONOSCIUTI = [[4], [6], [8], [8, 4], [10, 6], [10, 8], [10, 8, 4], [10, 10, 6], [10, 10, 8], [10, 10, 8, 4],
              [10, 10, 10, 6], [10, 10, 10, 8], [10, 10, 10, 8, 4], [10, 10, 10, 10, 6], [10, 10, 10, 10, 8],
              [10, 10, 10, 10, 8, 2], [10, 10, 10, 10, 8, 2], [10, 10, 10, 10, 8, 4], [10, 10, 10, 10, 8, 4],
              [10, 10, 10, 10, 8, 6]]
AL_GIORNO = [[1], [2], [3], [3, 1], [4, 2], [4, 3], [4, 3, 1], [4, 4, 2], [5, 4, 3], [5, 4, 3, 1], [5, 4, 4, 2],
             [5, 5, 4, 3], [5, 5, 4, 3, 1], [5, 5, 4, 4, 2], [5, 5, 5, 4, 3], [5, 5, 5, 4, 3, 1], [5, 5, 5, 4, 4, 2],
             [5, 5, 5, 5, 4, 2], [5, 5, 5, 5, 5, 3], [5, 5, 5, 5, 5, 3]]
_sp = body.find('w:sectPr', NS)
_pw = int(_sp.find('w:pgSz', NS).get(q('w'))); _pm = _sp.find('w:pgMar', NS)
CONTENT = _pw - int(_pm.get(q('left'))) - int(_pm.get(q('right')))   # 9360 (Letter) o 10206 (A4)
_c = (CONTENT - 706) // 6
WIDTHS = [706] + [_c] * 5 + [CONTENT - 706 - 5 * _c]

def keep_next(p):
    ppr = p.find('w:pPr', NS)
    if ppr is None:
        ppr = etree.SubElement(p, q('pPr')); p.insert(0, ppr)
    if ppr.find('w:keepNext', NS) is None:
        kn = etree.Element(q('keepNext'))
        st = ppr.find('w:pStyle', NS)
        if st is not None: st.addnext(kn)
        else: ppr.insert(0, kn)

def build_table(src, data):
    t = copy.deepcopy(src)
    grid = t.find('w:tblGrid', NS)
    cols = grid.findall('w:gridCol', NS)
    grid.remove(cols[1])
    for gc, wv in zip(grid.findall('w:gridCol', NS), WIDTHS):
        gc.set(q('w'), str(wv))
    tw = t.find('w:tblPr/w:tblW', NS)
    if tw is not None:
        tw.set(q('w'), str(sum(WIDTHS))); tw.set(q('type'), 'dxa')
    for r, tr in enumerate(t.findall('w:tr', NS)):
        tcs = tr.findall('w:tc', NS)
        tr.remove(tcs[1])
        for c, tc in enumerate(tr.findall('w:tc', NS)):
            w_ = tc.find('w:tcPr/w:tcW', NS)
            if w_ is not None:
                w_.set(q('w'), str(WIDTHS[c])); w_.set(q('type'), 'dxa')
            if r == 0:
                val = 'Liv.' if c == 0 else str(c)
            elif c == 0:
                val = '%d°' % r
            else:
                row = data[r - 1]
                val = str(row[c - 1]) if c - 1 < len(row) else '—'
            ts = list(tc.iter(q('t')))
            ts[0].text = val
            for extra in ts[1:]:
                extra.text = ''
    return t

(k_t, k_s, k_tb) = tpl_find('Incantesimi Conosciuti')
(g_t, g_s, g_tb) = tpl_find('Incantesimi Lanciabili al Giorno')
anchor = p
for tit, sub, tb, titolo, sottotitolo, data in [
        (g_t, k_s, k_tb, 'Mechanus Conosciuti',
         "Il numero accanto a ciascun livello di mechanus indica quanti mechanus di quel livello un inventore conosce a quel livello di classe.",
         CONOSCIUTI),
        (g_t, g_s, g_tb, 'Mechanus al Giorno',
         "Il numero accanto a ciascun livello di mechanus indica quanti mechanus di quel livello un inventore può creare ogni giorno, esclusi i mechanus bonus da Intelligenza.",
         AL_GIORNO)]:
    a = set_parts(copy.deepcopy(tit), [titolo]); anchor.addnext(a)
    b = set_parts(copy.deepcopy(sub), [sottotitolo]); a.addnext(b)
    c = build_table(tb, data); b.addnext(c)
    keep_next(a); keep_next(b)
    rows = c.findall('w:tr', NS)
    for tr in rows[:-1]:
        for cp in tr.iter(q('p')):
            keep_next(cp)
    anchor = c
LOG.append('Mechanus: aggiunte le tabelle Mechanus Conosciuti e Mechanus al Giorno')

p = find('Nota: I mechanus di 6° livello vengono sbloccati al 17°', hm, 'start')
repl(p, 'al 17° livello di inventore', 'al 16° livello di inventore', 'Mechanus di 6° livello: 17° → 16°')

# ------------------------------------------------------------------ tecno-armi
ht = find('Tecno-armi', p)
p = find('Le tecno-armi sono armi convenzionali', ht, 'start')
repl(p, "e gli incantamenti che possiede", "e le capacità speciali che possiede")
p_costr = find('Costruire una tecno-arma richiede', ht, 'start')
repl(p_costr, "un'arma di buona fattura, perfetta o magica", "un'arma di buona fattura o perfetta")
repl(p_costr, "inclusi eventuali incantamenti che possedeva", "con le capacità speciali che possedeva")
h_costr = p_costr.getprevious()
p = find('Ogni modifica necessita di un numero definito di nodi', ht, 'start')
repl(p, "Un inventore non può installare su una tecno-arma più nodi del proprio bonus di Intelligenza.",
     "Il totale dei nodi installati su una tecno-arma non può superare il più basso tra i nodi installabili "
     "dell'ultimo aggiornamento raggiunto (vedi tabella seguente) e il bonus di Intelligenza dell'inventore.",
     'Tecno-armi: limite dei nodi')
hs = clone_after(p, h_costr, ['Sintonia'])
clone_after(hs, p_costr, [
    "Una tecno-arma si sintonizza come qualsiasi altra arma, secondo le regole del manuale Armi, armature e scudi: "
    "riceve il bonus di potenziamento dalla sintonia dell'inventore, che può distribuirlo anche su una seconda arma come "
    "di consueto. Le capacità speciali si applicano con le parti di potenziamento, scegliendole dall'elenco delle armi "
    "da mischia o da quello delle armi a distanza in base all'arma base; la somma dei loro valori non può superare il "
    "bonus di potenziamento. Le modifiche della tecno-arma sono un sistema separato: non contano come capacità speciali "
    "e non sono limitate dal bonus di potenziamento."])
LOG.append('Tecno-armi: nuovo paragrafo Sintonia')
tt = find('Progressione degli aggiornamenti', ht).getnext()
repl(cell(tt, 2, 0), 'Aggiornamento #1', 'Aggiornamento del 5° livello')
repl(cell(tt, 3, 0), 'Aggiornamento #2', 'Aggiornamento del 10° livello')
repl(cell(tt, 4, 0), 'Aggiornamento #3 (specializzazione)', 'Aggiornamento del 15° livello (specializzazione)')
repl(cell(tt, 5, 0), 'Aggiornamento finale (specializzazione)', 'Aggiornamento del 20° livello (specializzazione)')
for old, new in [('Aggiornamento #1 (2 nodi, livello 5°)', 'Aggiornamento del 5° livello (2 nodi)'),
                 ('Aggiornamento #2 (3 nodi, livello 10°)', 'Aggiornamento del 10° livello (3 nodi)'),
                 ('Aggiornamento #3 specialistico (4 nodi, livello 15°)', 'Aggiornamento del 15° livello, specialistico (4 nodi)'),
                 ('Aggiornamento finale specialistico (5 nodi, livello 20°)', 'Aggiornamento del 20° livello, specialistico (5 nodi)')]:
    repl(find(old, ht), old, new)
repl(find('Nota: Le modifiche di Aggiornamento #3', ht, 'start'), 'Le modifiche di Aggiornamento #3', "Le modifiche dell'aggiornamento del 15° livello")
repl(find("Nota: Le modifiche dell'Aggiornamento finale", ht, 'start'), "Le modifiche dell'Aggiornamento finale", "Le modifiche dell'aggiornamento del 20° livello")

# ------------------------------------------------------------------ automaton
ha = find('Automaton', find('Optional delle tecno-armi', ht))
p_car = find('Gli automaton non sono intelligenti e non parlano', ha, 'start')
h_istr = find("Istruzioni per l'uso", ha)
hn = clone_after(p_car, h_istr, ['Punti Ferita e attacchi'])
clone_after(hn, p_car, [
    "Un automaton ha 10 Punti Ferita al 1° Dado Vita e 6 per ogni Dado Vita successivo, più la somma dei Bonus PF "
    "indicati nella tabella degli automaton (cumulativi), +10 se l'Aumento di taglia lo rende Grande (+20 con la scocca "
    "«Optimus prime» dell'automaton alpha, al posto dei +10). Non aggiunge la Costituzione e non ha Punti Fatica. "
    "Gli attacchi dell'automaton funzionano come attacchi con armi: quando il bonus di attacco base lo consente, con "
    "un'azione di attacco completo effettua attacchi multipli."])
LOG.append('Automaton: nuovo paragrafo Punti Ferita e attacchi')
h_inc = find('Incantare armi e scocca', ha)
repl(h_inc, 'Incantare armi e scocca', 'Sintonia meccanica')
p = h_inc.getnext()
repl(p, tx(p),
     "L'arma e la scocca di un automaton (la scocca conta come un'armatura pesante) non usano la sintonia dell'inventore: "
     "ottengono automaticamente un bonus di potenziamento, anche se non sono perfette. Il bonus è +1 dal 3° livello e +2 "
     "dal 10°; se l'inventore ha scelto gli automaton come specializzazione, diventa +3 dal 15°, +4 dal 17° e +5 al 20°. "
     "L'inventore può applicare all'arma e alla scocca capacità speciali con le parti di potenziamento, secondo le regole "
     "del manuale Armi, armature e scudi: lo schianto del Destructor e quello del Defensor usano l'elenco delle armi da "
     "mischia, lo sparaculei del Sagittar quello delle armi a distanza e la scocca quello delle armature. La somma dei "
     "valori delle capacità speciali non può superare il bonus di potenziamento. Quando smantella l'automaton, "
     "l'inventore recupera le parti di potenziamento applicate all'arma e alla scocca.",
     'Automaton: Incantare armi e scocca → Sintonia meccanica')
tb_aut = find('Tabella degli automaton', ha).getnext()
p_note = clone_after(tb_aut, p_car, [
    "La CA indicata nella tabella è già totale: vi si aggiungono solo i modificatori di taglia, il bonus di "
    "potenziamento della scocca e gli eventuali bonus dell'automaton alpha e di Overdrive Beta. Ai Tiri Salvezza su "
    "Riflessi si aggiunge il modificatore di Destrezza. Il Bonus For/Des si somma sia alla Forza sia alla Destrezza del "
    "modello. BMC = bonus di attacco base + modificatore di Forza + modificatore di taglia; DMC = 10 + bonus di attacco "
    "base + modificatori di Forza e di Destrezza + modificatore di taglia."])
LOG.append('Automaton: nota di lettura della tabella (CA, Riflessi, For/Des, BMC/DMC)')
repl(find('Schianto idraulico (1d10', ha, 'in'), "L'arma può essere incantata smantellando armi magiche da mischia a due mani.",
     "Conta come un'arma da mischia a due mani (aggiunge 1 volta e ½ il bonus di Forza ai danni) e riceve la sintonia meccanica.")
repl(find('Schianto meccanico (1d6', ha, 'in'), "L'arma può essere incantata smantellando armi magiche da mischia a una mano.",
     "Conta come un'arma da mischia a una mano (aggiunge il bonus di Forza ai danni) e riceve la sintonia meccanica.")
repl(find('Schianto (1d3', ha, 'in'), "Lo schianto del Sagittar non può ricevere incantamenti.",
     "Aggiunge il bonus di Forza ai danni. Lo schianto del Sagittar non riceve la sintonia meccanica né capacità speciali.")
repl(find('Sparaculei (1d8', ha, 'in'), "L'arma può essere incantata smantellando armi magiche da tiro.",
     "Conta come un'arma a distanza e riceve la sintonia meccanica.")
for old, new, body_old, body_new in [
        ('Incantamenti (Funzionalità di base)', 'Sintonia meccanica (funzionalità di base)',
         "L'arma e la scocca dell'automaton possono ottenere ciascuna un massimo di incantamenti pari a +1.",
         "L'arma e la scocca dell'automaton hanno bonus di potenziamento +1."),
        ('Incantamenti (Aggiornamento #1)', 'Sintonia meccanica (aggiornamento del 10° livello)',
         "Le armi e la scocca dell'automaton possono ottenere ciascuna un massimo di incantamenti pari a +2.",
         "L'arma e la scocca dell'automaton hanno bonus di potenziamento +2."),
        ('Incantamenti (Aggiornamento #2)', 'Sintonia meccanica (aggiornamento del 15° livello)',
         "Le armi e la scocca dell'automaton possono ottenere ciascuna un massimo di incantamenti pari a +3.",
         "L'arma e la scocca dell'automaton hanno bonus di potenziamento +3, che diventa +4 dal 17° livello."),
        ('Incantamenti (Aggiornamento finale)', 'Sintonia meccanica (aggiornamento del 20° livello)',
         "Le armi e la scocca dell'automaton possono ottenere ciascuna un massimo di incantamenti pari a +5.",
         "L'arma e la scocca dell'automaton hanno bonus di potenziamento +5.")]:
    hh = find(old, ha); repl(hh, old, new)
    repl(hh.getnext(), body_old, body_new)
for old, new in [('Aggiornamento #1 (livello 10°)', 'Aggiornamento del 10° livello'),
                 ('Aggiornamento #2 specialistico (livello 15°)', 'Aggiornamento del 15° livello, specialistico'),
                 ('Aggiornamento finale (livello 20°)', 'Aggiornamento del 20° livello, specialistico')]:
    repl(find(old, ha), old, new)

# ------------------------------------------------------------------ esoscheletri
he = find('Esoscheletri', find('Optional degli automaton', ha))
p = find('Costruire un esoscheletro richiede', he, 'start')
repl(p, "un'armatura leggera perfetta o magica", "un'armatura leggera perfetta")
repl(p, "un'armatura pesante perfetta o magica", "un'armatura pesante perfetta")
repl(p, "si recupera automaticamente l'armatura base.", "si recupera automaticamente l'armatura base, con le capacità speciali che possedeva.")
p_costr_e = p; h_costr_e = p.getprevious()
p = find('Ogni modifica necessita di un numero definito di nodi', he, 'start')
repl(p, "Un inventore non può installare su un esoscheletro più nodi del proprio bonus di Intelligenza.",
     "Il totale dei nodi installati su un esoscheletro non può superare il più basso tra i nodi installabili "
     "dell'ultimo aggiornamento raggiunto (vedi tabella seguente) e il bonus di Intelligenza dell'inventore.",
     'Esoscheletri: limite dei nodi')
hs = clone_after(p, h_costr_e, ['Sintonia'])
clone_after(hs, p_costr_e, [
    "Un esoscheletro si sintonizza come un'armatura, secondo le regole del manuale Armi, armature e scudi: riceve il "
    "bonus di potenziamento dalla sintonia dell'inventore, che può dividerlo con uno scudo come di consueto. Le capacità "
    "speciali si applicano con le parti di potenziamento, scegliendole dall'elenco delle armature; la somma dei loro "
    "valori non può superare il bonus di potenziamento. Il +1 dell'Armatura migliorata è un bonus separato e si somma a "
    "quello della sintonia. Le modifiche dell'esoscheletro sono un sistema separato."])
LOG.append('Esoscheletri: nuovo paragrafo Sintonia')
te = find('Progressione degli aggiornamenti', he).getnext()
repl(cell(te, 2, 0), 'Aggiornamento #1', 'Aggiornamento del 10° livello')
repl(cell(te, 3, 0), 'Aggiornamento #2 specialistico', 'Aggiornamento del 15° livello')
repl(cell(te, 4, 0), 'Aggiornamento finale', 'Aggiornamento del 20° livello')
for old, new in [('Aggiornamento #1 (3 nodi, livello 10°)', 'Aggiornamento del 10° livello (3 nodi)'),
                 ('Aggiornamento #2 specialistico (4 nodi, livello 15°)', 'Aggiornamento del 15° livello, specialistico (4 nodi)'),
                 ('Aggiornamento finale (5 nodi, livello 20°)', 'Aggiornamento del 20° livello, specialistico (5 nodi)')]:
    repl(find(old, he), old, new)

# ------------------------------------------------------------------ gadget e archetipi
p = find('Ingombro 2 (o arma a due mani con la miglioria)', he, 'start')
repl(p, 'danno 1d12 in taglia media, 3d6 minaccia di critico, x3 moltiplicatore', 'danno 3d6 in taglia media, critico 18-20/x2',
     'Motosega Demolisher: 3d6, 18-20/x2')
har = find("Archetipi dell'Inventore", p)
repl(find('Al 1° livello, le tecno-armi di un ingegnere da campo', har, 'start'), 'hanno il 50% di ignorare', 'hanno il 50% di probabilità di ignorare')
# mechautarca
hmc = find('Mechautarca', har)
repl(find('Mechanus potenziati', hmc), 'Mechanus potenziati', 'Mechanus perfezionati')
repl(find('Scocca “Optimus prime”', hmc, 'start'), "ottenibili con l'Aggiornamento #1 (Aumento di taglia)", "ottenibili con l'aggiornamento del 10° livello (Aumento di taglia)")
ds = find('Privilegio di classe sostituito: Esoscheletri al 5° livello.', hmc)
mod = copy.deepcopy(ds); set_parts(mod, ['Privilegio di classe modificato: ', 'Automaton al 3° livello.'])
ds.addprevious(mod); LOG.append('Mechautarca: Automaton alpha modifica Automaton al 3°')
# skitari
hsk = find('Skitari', hmc)
repl(find('Abilità di classe:', hsk, 'start'), 'può utilizzare Professione (fabbro) al posto di Professione (ingegnere bellico)',
     'può utilizzare Professione (ingegnere bellico) al posto di Professione (fabbro)')
repl(find("Privilegio di classe sostituito: Gadget al 4°, al 6°, all'8°, al 10° e al 12° livello.", hsk),
     "Gadget al 4°", "Gadget, optional o dote da inventore al 4°")
# androide
han = find('Androide (solo forgiati)', hsk)
repl(find('Privilegio di classe sostituito: Gadget al 10° livello.', han), 'Gadget al 10°', 'Gadget, optional o dote da inventore al 10°')
repl(find('Al 15° livello, la coscienza di un androide', han, 'start'), 'Al 15° livello', 'Al 14° livello')
repl(find('Privilegio di classe sostituito: Gadget al 15° livello.', han), 'Gadget al 15°', 'Gadget, optional o dote da inventore al 14°')
repl(find('Privilegio di classe sostituito: Aggiornamento finale delle meraviglie al 20° livello.', han),
     'Aggiornamento finale delle meraviglie', 'Aggiornamento delle meraviglie')
# cibernetico
hc = find('Cibernetico', han)
p = find('Al 1° livello, un cibernetico può costruire', hc, 'start')
repl(p, 'deve scegliere quale usare cambiando equipaggiamento.',
     'deve scegliere quale usare cambiando equipaggiamento. Ai fini della sintonia, i due esoscheletri contano come una sola armatura.')
h_dm = p.getprevious(); d_dm = p.getnext()
h1 = clone_after(d_dm, h_dm, ['Esoscheletri precoci'])
b1 = clone_after(h1, p, ["Al 3° livello, un cibernetico impara a costruire gli esoscheletri (funzionalità di base) anziché al "
                         "5° livello; gli aggiornamenti degli esoscheletri restano ai livelli consueti. Per questo le "
                         "scoperte sugli esoscheletri partono dal 3° livello."])
d1 = copy.deepcopy(d_dm); set_parts(d1, ['Privilegio di classe modificato: ', 'Esoscheletri al 5° livello.']); b1.addnext(d1)
LOG.append('Cibernetico: nuova capacità Esoscheletri precoci (3°)')

# controllo finale: nessun residuo
END = els().index(find('Camuffamento tecnologico', hc)) + 3
def keep_table(t):
    rows = t.findall('w:tr', NS)
    for tr in rows:
        trpr = tr.find('w:trPr', NS)
        if trpr is None:
            trpr = etree.Element(q('trPr')); tr.insert(0, trpr)
        if trpr.find('w:cantSplit', NS) is None:
            trpr.insert(0, etree.Element(q('cantSplit')))
    for tr in rows[:-1]:
        for cp in tr.iter(q('p')):
            keep_next(cp)
keep_table(tt); keep_table(te); keep_table(tb_aut); keep_next(find("Tabella degli automaton", ha))

# titoli tenuti con il paragrafo successivo (evita titoli orfani a fondo pagina)
def is_bold(r):
    b = r.find('w:rPr/w:b', NS)
    return b is not None and b.get(q('val')) not in ('false', '0')
nk = 0
for e in els()[START:END]:
    if etree.QName(e).localname != 'p': continue
    s_ = tx(e).strip()
    runs = [r for r in e.findall('w:r', NS) if (''.join(t.text or '' for t in r.findall('w:t', NS))).strip()]
    if s_ and len(s_) < 120 and runs and all(is_bold(r) for r in runs) and not s_.startswith('Privilegio di classe'):
        if e.find('w:pPr/w:keepNext', NS) is None:
            keep_next(e); nk += 1
LOG.append('keepNext aggiunto a %d titoli' % nk)
rest = [tx(e) for e in els()[START:END] if re.search(r'Aggiornamento #|incantament|perfetta o magica|Aggiornamento finale', tx(e))]
tree.write(DOC, xml_declaration=True, encoding='UTF-8', standalone=True)
print('\n'.join('✓ ' + l for l in LOG))
print('Residui:', rest)
