"""Legge txt/Inventore_*.txt (una riga per paragrafo) e produce inventore.json.
Uso: python3 sorgenti/parse_inventore.py
I testi vengono sempre dal manuale; le meccaniche che l'app calcola (nodi, stadi,
restrizioni, requisiti) sono ricavate dai titoli e dalle frasi standard del manuale.
Le decisioni di design non ancora riportate nel manuale sono in CORREZIONI (in fondo)."""
import json, os, re, glob, unicodedata

R = os.path.dirname(os.path.abspath(__file__))
TXT = sorted(glob.glob(os.path.join(R, 'txt', 'Inventore_*.txt')))[-1]
L = [l.strip() for l in open(TXT, encoding='utf8').read().split('\n')]


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')


def idx(testo, da=0):
    for i in range(da, len(L)):
        if L[i] == testo:
            return i
    raise SystemExit('Non trovo: ' + testo)


def e_titolo(s):
    """Un paragrafo è un titolo se è breve e non termina come una frase."""
    if not s or len(s) > 130:
        return False
    if s.startswith(('•', 'Nota:', 'Privilegio di classe', 'Requisiti:', 'Prerequisito', 'Abilità di classe', 'Competenze')):
        return False
    if re.match(r'^(Al |Funzioni|Caratteristiche:|Attacco)', s):
        return False
    return not s.endswith(('.', ':', ';'))


def blocchi(a, b):
    """Divide le righe [a,b) in (titolo, [paragrafi])."""
    out = []
    for s in L[a:b]:
        if not s:
            continue
        if e_titolo(s):
            out.append([s, []])
        elif out:
            out[-1][1].append(s)
    return out


def num(s):
    s = s.replace('+', '').replace('−', '-').strip()
    try:
        return int(s)
    except ValueError:
        return s


# ---------------- tabella di classe ----------------
i = idx('Tabella dell\'Inventore') + 7
tab = []
for r in range(20):
    c = L[i + r * 6: i + r * 6 + 6]
    tab.append({'liv': r + 1, 'bab': c[1], 'tempra': num(c[2]), 'rif': num(c[3]), 'vol': num(c[4]), 'privilegi': c[5]})

# ---------------- arnesi da inventore ----------------
i = idx('Arnesi da inventore') + 11
arnesi, cat = [], ''
while L[i]:
    if L[i].startswith('Armi da') and not L[i + 1].endswith('mo'):
        cat = L[i]; i += 1; continue
    c = L[i:i + 10]
    arnesi.append({'id': slug(c[0]), 'nome': c[0], 'cat': cat, 'costo': c[1], 'dP': c[2], 'dM': c[3], 'gittata': c[4],
                   'critico': c[5], 'tipo': c[6], 'speciale': c[7], 'eq': c[9]})
    i += 10

# ---------------- privilegi ----------------
a, b = idx('Privilegi di classe', idx('Arnesi da inventore')), idx('Da sapere prima di mettersi all\'opera')
privilegi = [{'nome': t, 'testo': '\n'.join(p)} for t, p in blocchi(a + 1, b)]
dasapere = [s for s in L[b + 1: b + 8] if re.match(r'^\d\.', s)]

# ---------------- mechanus ----------------
a = idx('Mechanus', b); b2 = idx('Tecno-armi', a)
intro_mech = [s for s in L[a + 1:b2] if s and not s.startswith('Mechanus di')][:2]
mechanus, lv = [], 0
for s in L[a + 1:b2]:
    m = re.match(r'^Mechanus di (\d)° livello$', s)
    if m:
        lv = int(m.group(1)); continue
    if not lv or not s or s.startswith('Nota:'):
        continue
    if e_titolo(s):
        nome = re.sub(r'\s*\(consumabile\)', '', s)
        mechanus.append({'id': slug(nome), 'nome': nome, 'liv': lv, 'consumabile': 'consumabile' in s, 'testo': []})
    else:
        mechanus[-1]['testo'].append(s)
for m in mechanus:
    m['testo'] = '\n'.join(m['testo'])

# ---------------- modifiche (tecno-armi / esoscheletri) ----------------
RX_MOD = re.compile(r'^(.*?)\s*\((\d) nod[oi](?:,\s*([^)]*))?\)$')


def leggi_mod(titolo, testo, stadio, tipo=None):
    m = RX_MOD.match(titolo)
    nome, nodi, extra = m.group(1).strip(), int(m.group(2)), (m.group(3) or '')
    d = {'id': slug(nome) + ('_' + tipo if tipo in ('L', 'P') else ''), 'nome': nome, 'nodi': nodi, 'stadio': stadio,
         'passiva': 'passiva' in extra, 'sempre': 'sempre attiva' in extra, 'testo': testo}
    if tipo:
        d['tipo'] = tipo
    mm = re.match(r'^Solo ([^.]*)\.\s*', testo)
    if mm:
        d['solo'] = mm.group(1)
    mm = re.search(r'Richiede (?:la )?modifica ([^.]*?) installata', testo)
    if mm:
        d['richiede'] = [slug(mm.group(1))]
    mm = re.search(r'Incompatibile con (?:le|la) modific[ah]e? ([^.]*)\.', testo)
    if mm:
        d['incompat'] = [slug(x) for x in re.split(r',\s*|\s+e\s+', mm.group(1))]
    mm = re.search(r'Incompatibile con (?:la )?(capacità|proprietà) ([^.]*)\.', testo)
    if mm:
        d['incompatSpeciale'] = mm.group(2)
    return d


# tecno-armi
a = idx('Tecno-armi', b2); b3 = idx('Automaton', a)
STADI_T = {'Funzionalità di base': 0, 'Aggiornamento #1': 1, 'Aggiornamento #2': 2, 'Aggiornamento #3': 3, 'Aggiornamento finale': 4}
tecno_regole = []
tecno_mods, tecno_opt, stadio, fase = [], [], None, 'regole'
for t, ps in blocchi(a + 1, b3):
    st = next((v for k, v in STADI_T.items() if t.startswith(k) and '(' in t and 'livello' in t), None)
    if st is not None:
        stadio, fase = st, 'mod'; continue
    if t == 'Optional delle tecno-armi':
        fase = 'opt'; tecno_opt_intro = ' '.join(ps); continue
    if fase == 'regole':
        if t in ('Progressione degli aggiornamenti',):
            continue
        tecno_regole.append({'nome': t, 'testo': ' '.join(p for p in ps if not re.match(r'^[+\d°]', p))}) if ps and len(ps[0]) > 20 else None
    elif fase == 'mod':
        tecno_mods.append(leggi_mod(t, ' '.join(p for p in ps if not p.startswith('Nota:')), stadio))
    else:
        m = re.match(r'^(.*?)\s*\(requisito: (\d+)° livello\)$', t)
        nome, req = (m.group(1), int(m.group(2))) if m else (t, 1)
        tecno_opt.append({'id': slug(nome), 'nome': nome, 'req': req, 'testo': ' '.join(ps)})

# ---------------- automaton ----------------
a = b3; b4 = idx('Esoscheletri', a)
i = idx('Tabella degli automaton', a) + 12
aut_tab = []
for r in range(18):
    c = L[i + r * 11: i + r * 11 + 11]
    aut_tab.append({'liv': r + 3, 'dv': int(c[1]), 'bonusPF': 0 if c[2] in ('—', '-') else num(c[2]), 'forDes': num(c[3]),
                    'bab': c[4], 'tempra': num(c[5]), 'rif': num(c[6]), 'vol': num(c[7]),
                    'ca': {'destructor': int(c[8]), 'defensor': int(c[9]), 'sagittar': int(c[10])}})
fine_tab = i + 18 * 11
aut_regole = [{'nome': t, 'testo': ' '.join(ps)} for t, ps in blocchi(a + 1, idx('Tabella degli automaton', a))]
aut_voci, aut_opt, stadio, fase = [], [], 0, 'voci'
STADI_A = {'Funzionalità di base (livello 3°)': 0, 'Aggiornamento #1 (livello 10°)': 1,
           'Aggiornamento #2 specialistico (livello 15°)': 2, 'Aggiornamento finale (livello 20°)': 3}
modelli = {}
for t, ps in blocchi(fine_tab, b4):
    if t in STADI_A:
        stadio = STADI_A[t]; continue
    if t == 'Optional degli automaton':
        fase = 'opt'; continue
    testo = ' '.join(p for p in ps if not p.startswith('Nota:'))
    if fase == 'voci':
        if t in ('Destructor', 'Defensor', 'Sagittar'):
            car = dict(re.findall(r'(For|Des|Cos|Int|Sag|Car) (\d+|—)', ps[0]))
            modelli[slug(t)] = {'nome': t, 'car': {k: (int(v) if v.isdigit() else None) for k, v in car.items()}, 'righe': ps}
            continue
        m = re.match(r'^(.*?)\s*\((tutti i modelli|opzionale, tutti i modelli|solo [^)]*)\)$', t)
        nome, chi = (m.group(1), m.group(2)) if m else (t, 'tutti i modelli')
        mod = [slug(x) for x in re.findall(r'Destructor|Defensor|Sagittar', chi)] or ['destructor', 'defensor', 'sagittar']
        mm = re.search(r'pari a \+(\d)', testo) if t.startswith('Incantamenti') else None
        aut_voci.append({'id': slug(nome), 'nome': nome, 'stadio': stadio, 'modelli': mod, 'opzionale': 'opzionale' in chi,
                         'incantamenti': int(mm.group(1)) if mm else None, 'testo': testo})
    else:
        m = re.match(r'^(.*?)\s*\((.*)\)$', t)
        nome, par = (m.group(1), m.group(2)) if m else (t, '')
        req = re.search(r'requisito: (\d+)° livello', par)
        pre = re.search(r'requisito: \d+° livello; ([^)]*)', par)
        mod = [slug(x) for x in re.findall(r'Destructor|Defensor|Sagittar', par)] or ['destructor', 'defensor', 'sagittar']
        aut_opt.append({'id': slug(nome), 'nome': nome, 'req': int(req.group(1)) if req else 1, 'modelli': mod,
                        'prereq': [slug(pre.group(1))] if pre else [], 'testo': testo})

# ---------------- esoscheletri ----------------
a = b4; b5 = idx('Gadget', a)
STADI_E = {'Funzionalità di base (2 nodi, livello 5°)': 0, 'Aggiornamento #1 (3 nodi, livello 10°)': 1,
           'Aggiornamento #2 specialistico (4 nodi, livello 15°)': 2, 'Aggiornamento finale (5 nodi, livello 20°)': 3}
eso_regole, eso_mods, eso_opt, stadio, tipo, fase = [], [], [], None, 'C', 'regole'
for t, ps in blocchi(a + 1, b5):
    if t in STADI_E:
        stadio, fase, tipo = STADI_E[t], 'mod', 'C'; continue
    if t == 'Optional degli esoscheletri':
        fase = 'opt'; continue
    if t in ('Modifiche per esoscheletro leggero', 'Solo esoscheletro leggero'):
        tipo = 'L'; continue
    if t in ('Modifiche per esoscheletro pesante', 'Solo esoscheletro pesante'):
        tipo = 'P'; continue
    if t.startswith('Modifiche comuni'):
        tipo = 'C'; continue
    testo = ' '.join(p for p in ps if not p.startswith('Nota:'))
    if fase == 'regole':
        if ps and len(ps[0]) > 20 and t != 'Progressione degli aggiornamenti':
            eso_regole.append({'nome': t, 'testo': testo})
    elif fase == 'mod':
        if t.startswith('Armatura migliorata'):
            eso_mods.append({'id': 'armatura_migliorata', 'nome': 'Armatura migliorata', 'nodi': 0, 'stadio': 0, 'tipo': 'C',
                             'sempre': True, 'passiva': False, 'auto': True, 'testo': testo}); continue
        if 'entrambi i tipi' in t:
            t = t.replace(', entrambi i tipi', ''); tt = 'C'
        else:
            tt = tipo
        if testo.startswith('Come per esoscheletro leggero') and tt == 'P':
            continue  # Galleggianti del pesante: stessa modifica del leggero, la rendo comune
        d = leggi_mod(t, testo, stadio, tt)
        if d['nome'] in ('Galleggianti', 'Campo anti-contatto'):
            d['tipo'] = 'C'; d['id'] = slug(d['nome'])
            if any(x['id'] == d['id'] for x in eso_mods):
                continue
        eso_mods.append(d)
    else:
        m = re.match(r'^(.*?)\s*\((.*)\)$', t)
        nome, par = (m.group(1), m.group(2)) if m else (t, '')
        req = re.search(r'requisito: (\d+)° livello', par)
        pre = re.search(r'(Rinforzi salvavita F\d)', par)
        mm = re.search(r'richiede modifica ([^)]*?) installata', par)
        solo = 'P' if 'solo pesante' in par else None
        eso_opt.append({'id': slug(nome), 'nome': nome, 'req': int(req.group(1)) if req else 1, 'solo': solo,
                        'prereq': [slug(pre.group(1))] if pre else [], 'richiedeMod': slug(mm.group(1)) if mm else None,
                        'testo': testo})

# ---------------- gadget ----------------
a = b5; b6 = idx('Doti da inventore', a)
gad_regole, gadget, cat, sub, fase = [], [], '', '', 'regole'
for t, ps in blocchi(a + 1, b6):
    m = re.match(r'^Categoria (\d): (.*)$', t)
    if m:
        cat, sub, fase = m.group(2), '', 'g'; continue
    if fase == 'regole':
        gad_regole.append({'nome': t, 'testo': ' '.join(ps)}); continue
    if not ps:
        sub = t; continue
    if t == 'Armi sperimentali':
        sub = t; continue
    m = re.match(r'^(.*?)\s*\((.*)\)$', t)
    nome, par = t, ''
    if m and 'requisito' in m.group(2):
        nome, par = m.group(1), m.group(2)
    req = re.search(r'requisito: (\d+)° livello', par)
    g = {'id': slug(nome), 'nome': nome, 'cat': cat, 'sub': sub, 'req': int(req.group(1)) if req else 1,
         'reqExtra': re.sub(r'^requisito: \d+° livello\s*[;+]?\s*', '', par) or None, 'testo': '\n'.join(ps)}
    g['sperimentale'] = sub == 'Armi sperimentali' or nome.startswith('Lanciagranate')
    mig = set(int(x) for x in re.findall(r"Miglioria all?'?\s*(\d+)° livello", g['testo']))
    k = g['testo'].find('Migliorie progressive')
    if k >= 0:
        mig |= set(int(x) for x in re.findall(r"(\d+)° livello", g['testo'][k:]))
    g['migliorie'] = sorted(mig)
    mm = re.search(r'Cariche: ([^.]*)\.', g['testo'])
    if mm:
        g['cariche'] = mm.group(1)
    mm = re.search(r'(\d+) attivazioni al giorno', g['testo'])
    if mm:
        g['usi'] = int(mm.group(1))
    gadget.append(g)
    if nome == 'Sega circolare / Motosega “Xecchon GT 23 Demolisher”':
        g['id'] = 'sega_circolare'

# ---------------- doti ----------------
a = b6; b7 = idx('Archetipi dell\'Inventore', a)
doti, cat = [], ''
intro_doti = L[a + 1]
for t, ps in blocchi(a + 2, b7):
    if not ps:
        cat = t; continue
    req, pre, testo = 1, [], []
    for p in ps:
        m = re.match(r'^Requisiti: (.*)\.$', p)
        if m:
            r = m.group(1)
            mm = re.search(r'Inventore di (\d+)° livello', r)
            if mm:
                req = int(mm.group(1))
            mm = re.search(r'Dote da inventore (.*)$', r)
            if mm:
                pre.append(slug(mm.group(1)))
        else:
            testo.append(p)
    doti.append({'id': slug(t), 'nome': t, 'cat': cat, 'req': req, 'prereq': pre, 'testo': ' '.join(testo)})

# ---------------- archetipi ----------------
a = b7
archetipi, cur, cap = [], None, None
intro_arch = L[a + 1]
NOMI_ARCH = ['Ingegnere da campo', 'Mechautarca', 'Tecnomante', 'Skitari', 'Androide (solo forgiati)', 'Cibernetico', 'Tecno-infiltratore']
for s in L[a + 2:]:
    if not s or re.fullmatch(r'\d+', s):
        continue
    if s in NOMI_ARCH:
        cur = {'id': slug(s.replace(' (solo forgiati)', '')), 'nome': s.replace(' (solo forgiati)', ''), 'desc': '', 'note': [], 'capacita': []}
        if 'forgiati' in s:
            cur['soloForgiati'] = True
        archetipi.append(cur); cap = None; continue
    if cur is None:
        continue
    if not cur['desc']:
        cur['desc'] = s; continue
    m = re.match(r'^Privilegio di classe (sostituito|modificato): (.*)\.$', s)
    if m:
        cap[('sost' if m.group(1) == 'sostituito' else 'mod')] = m.group(2); continue
    if s.startswith(('Prerequisito', 'Abilità di classe', 'Competenze')):
        cur['note'].append(s); continue
    if e_titolo(s) and not s.startswith('Al '):
        cap = {'nome': s, 'testo': []}; cur['capacita'].append(cap); continue
    if cap is None:
        cur['note'].append(s); continue
    cap['testo'].append(s)
for ar in archetipi:
    for c in ar['capacita']:
        c['testo'] = '\n'.join(c['testo'])
        m = re.search(r'^(?:Al|All\')\s*(\d+)° livello', c['testo'])
        c['liv'] = int(m.group(1)) if m else (3 if c['nome'] == 'Automaton alpha' else 1)

# ---------------- tabelle dei mechanus (tier 6, colonne 1–6) ----------------
# Decisione A/F: progressione standard del tier 6 (Tabelle_incantesimi_Vol2_riferimento_v3), senza colonna 0 e senza "R".
CONOSCIUTI = [[4], [6], [8], [8, 4], [10, 6], [10, 8], [10, 8, 4], [10, 10, 6], [10, 10, 8], [10, 10, 8, 4], [10, 10, 10, 6],
              [10, 10, 10, 8], [10, 10, 10, 8, 4], [10, 10, 10, 10, 6], [10, 10, 10, 10, 8], [10, 10, 10, 10, 8, 2],
              [10, 10, 10, 10, 8, 2], [10, 10, 10, 10, 8, 4], [10, 10, 10, 10, 8, 4], [10, 10, 10, 10, 8, 6]]
AL_GIORNO = [[1], [2], [3], [3, 1], [4, 2], [4, 3], [4, 3, 1], [4, 4, 2], [5, 4, 3], [5, 4, 3, 1], [5, 4, 4, 2], [5, 5, 4, 3],
             [5, 5, 4, 3, 1], [5, 5, 4, 4, 2], [5, 5, 5, 4, 3], [5, 5, 5, 4, 3, 1], [5, 5, 5, 4, 4, 2], [5, 5, 5, 5, 4, 2],
             [5, 5, 5, 5, 5, 3], [5, 5, 5, 5, 5, 3]]

# ---------------- correzioni decise in chat (27/09/2026), da riportare nel manuale ----------------
CORREZIONI = []
def corr(desc):
    CORREZIONI.append(desc)

# D: gadget a tutti i livelli dispari fino all'11° (manca il 9° in tabella)
if 'Gadget' not in tab[8]['privilegi']:
    tab[8]['privilegi'] = 'Gadget, ' + tab[8]['privilegi']; corr('Tabella di classe: aggiunto Gadget al 9° livello')
AR = {a['id']: a for a in archetipi}
def cap_(ar, nome):
    return next(c for c in AR[ar]['capacita'] if c['nome'] == nome)
# E: sostituzioni degli archetipi riferite agli slot "Gadget, optional o dote"
c = cap_('androide', 'Sub-routine di emergenza')
if c.get('sost') == 'Gadget al 10° livello':
    c['sost'] = 'Gadget, optional o dote da inventore al 10° livello'; corr('Androide: Sub-routine sostituisce Gadget, optional o dote al 10°')
c = cap_('androide', 'Coscienza distribuita')
if c['liv'] == 15:
    c['liv'] = 14; c['testo'] = c['testo'].replace('Al 15° livello', 'Al 14° livello')
    c['sost'] = 'Gadget, optional o dote da inventore al 14° livello'; corr('Androide: Coscienza distribuita al 14°, sostituisce Gadget, optional o dote al 14°')
c = cap_('skitari', 'Armi sperimentali progressive')
if c.get('sost', '').startswith('Gadget al 4°'):
    c['sost'] = 'Gadget, optional o dote da inventore al 4°, al 6°, all\'8°, al 10° e al 12° livello'; corr('Skitari: Armi sperimentali progressive sostituiscono Gadget, optional o dote')
# Mechautarca
c = cap_('mechautarca', 'Automaton alpha')
if 'mod' not in c:
    c['mod'] = 'Automaton al 3° livello'; corr('Mechautarca: Automaton alpha modifica Automaton al 3°')
c = cap_('mechautarca', 'Mechanus potenziati')
c['nome'] = 'Mechanus perfezionati'; corr('Mechautarca: capacità rinominata Mechanus perfezionati')
# I: cibernetico, esoscheletri al 3°
if not any(x['nome'] == 'Esoscheletri precoci' for x in AR['cibernetico']['capacita']):
    AR['cibernetico']['capacita'].insert(1, {'nome': 'Esoscheletri precoci', 'liv': 3, 'mod': 'Esoscheletri al 5° livello',
        'testo': 'Al 3° livello, un cibernetico impara a costruire gli esoscheletri (Funzionalità di base).'})
    corr('Cibernetico: Esoscheletri precoci al 3° (modifica Esoscheletri al 5°)')
# D: testo del privilegio Gadget
for pv in privilegi:
    if pv['nome'] == 'Gadget' and 'ad ogni livello pari' in pv['testo']:
        pv['testo'] = ("Al 1°, 3°, 5°, 7°, 9° e 11° livello, un inventore impara a costruire un nuovo gadget a sua scelta tra quelli disponibili, "
                       "di cui soddisfa i requisiti. Ai livelli pari dal 2° al 18° sceglie invece un gadget, un optional o una dote da inventore. "
                       "Vedi sezione dedicata per le regole complete e l'elenco dei gadget.")
        corr('Privilegio Gadget riscritto (dispari fino all\'11°, pari: gadget, optional o dote)')
# refusi
for g in gadget:
    if g['id'] == 'sega_circolare' and '3d6 minaccia di critico' in g['testo']:
        g['testo'] = g['testo'].replace('danno 1d12 in taglia media, 3d6 minaccia di critico, x3 moltiplicatore', 'danno 3d6 in taglia media, critico 18-20/x2')
        corr('Motosega Demolisher: danno 3d6, critico 18-20/x2')
c = cap_('ingegnere_da_campo', 'Batterie migliorate')
c['testo'] = c['testo'].replace('hanno il 50% di ignorare', 'hanno il 50% di probabilità di ignorare')
for ar in archetipi:
    ar['note'] = [n.replace('può utilizzare Professione (fabbro) al posto di Professione (ingegnere bellico)',
                            'può utilizzare Professione (ingegnere bellico) al posto di Professione (fabbro)') for n in ar['note']]

# campi meccanici degli archetipi (cosa perdono/cambiano), usati dal motore dell'app
PERDE = {'ingegnere_da_campo': ['riparazioni', 'automaton'], 'mechautarca': ['tecno', 'eso'], 'tecnomante': ['tecno'],
         'skitari': ['mechanus', 'fabbro'], 'androide': ['fabbro'], 'cibernetico': ['mechanus', 'automaton'],
         'tecno_infiltratore': ['tecno', 'automaton', 'eso']}
for ar in archetipi:
    ar['perde'] = PERDE.get(ar['id'], [])
    ar['slot'] = []  # slot di gadget/optional/dote sostituiti
    for c in ar['capacita']:
        s = c.get('sost', '')
        for part in re.split(r';', s):
            if part.startswith('Gadget, optional o dote') or part.startswith('Gadget al') or part.startswith('Gadget ,'):
                for n in re.findall(r'(\d+)°', part):
                    ar['slot'].append(int(n))

# armature base degli esoscheletri (Vol. 3 Miscellanea 2.5.1, tabella Armature e scudi)
ARMATURE = [
    ('L', 'Corpetto imbottito', 1, 6, 0, ''), ('L', 'Corpetto di cuoio', 2, 5, 0, ''), ('L', 'Corpetto di legno', 3, 3, -2, 'Galleggiante'),
    ('L', 'Corpetto di cuoio borchiato', 3, 5, -1, ''), ('L', 'Giaco di maglia', 4, 4, -2, ''),
    ('P', 'Corazza a strisce', 8, 0, -7, 'Scomoda'), ('P', 'Corazza di bande', 9, 0, -6, 'Scomoda'), ('P', 'Mezza armatura', 9, 1, -7, 'Scomoda'),
    ('P', 'Mezza armatura flessibile', 9, 1, -7, 'Scomoda, Flessibile'), ('P', 'Armatura completa', 10, 1, -6, 'Scomoda')]
armature = [{'id': slug(n), 'tipo': t, 'nome': n, 'ca': ca, 'maxDes': md, 'pen': pe, 'speciale': sp} for t, n, ca, md, pe, sp in ARMATURE]

out = {'fonte': os.path.basename(TXT), 'tabella': tab, 'privilegi': privilegi, 'daSapere': dasapere, 'arnesi': arnesi,
       'mechanus': {'intro': intro_mech, 'elenco': mechanus, 'conosciuti': CONOSCIUTI, 'alGiorno': AL_GIORNO},
       'tecno': {'regole': [r for r in tecno_regole if r], 'mods': tecno_mods, 'optional': tecno_opt},
       'automaton': {'regole': aut_regole, 'tabella': aut_tab, 'modelli': modelli, 'voci': aut_voci, 'optional': aut_opt},
       'eso': {'armature': armature, 'regole': eso_regole, 'mods': eso_mods, 'optional': eso_opt},
       'gadget': {'regole': gad_regole, 'elenco': gadget}, 'doti': doti, 'archetipi': archetipi, 'correzioni': CORREZIONI}
json.dump(out, open(os.path.join(R, 'inventore.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('mechanus', len(mechanus), '| tecno', len(tecno_mods), '+', len(tecno_opt), 'opt | automaton voci', len(aut_voci),
      'opt', len(aut_opt), '| eso', len(eso_mods), 'opt', len(eso_opt), '| gadget', len(gadget), '| doti', len(doti),
      '| archetipi', len(archetipi), '| correzioni', len(CORREZIONI))
