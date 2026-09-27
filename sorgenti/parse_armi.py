"""Legge txt/armi_armature_scudi_Definitivo.txt e produce armi.json (capacità speciali per valore).
Uso: python3 sorgenti/parse_armi.py"""
import json, os, re, unicodedata
R = os.path.dirname(os.path.abspath(__file__))
L = [l.strip() for l in open(os.path.join(R, 'txt', 'armi_armature_scudi_Definitivo.txt'), encoding='utf8').read().split('\n')]
def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')
SEZ = {'Capitolo 4': 'armatura', 'Capitolo 5': 'scudo', 'Capitolo 6': 'mischia', 'Capitolo 7': 'distanza'}
out = {k: [] for k in SEZ.values()}
cat, val, cur = None, 0, None
for i, s in enumerate(L):
    if i < 20:
        continue
    m = re.match(r'^(Capitolo \d):', s)
    if m:
        cat = SEZ.get(m.group(1)); continue
    m = re.match(r'^Capacità (?:Equivalenti a|Scudi|Armi da Mischia|Armi a Distanza) \+(\d)$', s)
    if m:
        val = int(m.group(1)); cur = None; continue
    if not cat or not val or s in ('Capacità', 'Effetto', ''):
        continue
    if s.startswith(('Note e Avvertenze', '★ Nuove', 'Compatibilità', 'CD variabili', '★ =')):
        cat = None; continue
    m = re.match(r'^\d+\.\s+(.*)$', s)
    if m and len(s) < 90:
        nome = m.group(1).replace('★', '').strip()
        cur = {'id': slug(nome) + '_' + str(val), 'nome': nome, 'val': val, 'nuova': '★' in s, 'testo': ''}
        out[cat].append(cur); continue
    if cur:
        cur['testo'] = (cur['testo'] + ' ' + s).strip()
out['costi'] = {'arma': [0, 2000, 8000, 18000, 32000, 50000], 'armatura': [0, 1000, 4000, 9000, 16000, 25000]}
out['cd'] = {'arma': {2: 16, 3: 19, 4: 22, 5: 25, 6: 26, 7: 27, 8: 28, 9: 29, 10: 29}, 'armatura': {2: 15, 3: 18, 4: 21, 5: 24, 6: 26, 7: 27, 8: 28, 9: 29, 10: 29}}
# Tabella di sintonia per livello (uguale per armi e per armatura/scudo): opzioni [un oggetto] o [due oggetti]
out['sintonia'] = [[1, [[0]]], [4, [[1]]], [8, [[1], [1, 1]]], [9, [[2], [1, 1]]], [12, [[3], [2, 2]]], [15, [[4], [3, 3]]], [17, [[5], [4, 3]]], [20, [[5], [5, 4]]]]
json.dump(out, open(os.path.join(R, 'armi.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print({k: (len(v), [len([x for x in v if x['val'] == n]) for n in range(1, 6)]) for k, v in out.items() if k in SEZ.values()})
