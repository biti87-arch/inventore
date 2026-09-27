# Inventore — correzioni del 27/09/2026 (decisioni A–N)

Correzioni mirate applicate direttamente all'XML dei due .docx, senza rigenerare i file.

## Ordine di esecuzione
Manuale singolo (`Inventore_v2.4_FINALE.docx`):
    unzip -q Inventore.docx -d inv
    python3 patch_inventore.py inv/word/document.xml <vol2 estratto>/word/document.xml 0
    python3 patch2_skitari_tecnomante.py inv/word/document.xml 0
    ./pack.sh inv Inventore_v2.4_FINALE.docx

Vol. 2 2.5.1 (sezione Inventore, corpo 10347–11322 nella versione di partenza):
    unzip -q Vol2.docx -d vol2
    python3 rimuovi_riempitivi.py vol2/word/document.xml inv_ORIGINALE/word/document.xml 10359 11323
    python3 patch_inventore.py vol2/word/document.xml vol2/word/document.xml 10347
    python3 patch2_skitari_tecnomante.py vol2/word/document.xml 10347
    python3 aggiorna_indice.py vol2/word/document.xml "Archetipi dell'Inventore" -1
    ./pack.sh vol2 "Vol. 2 - Classi 2.5.1.docx"

## Script
- patch_inventore.py — tutte le modifiche, cercate per testo (vale per entrambi i file). Le tabelle
  Mechanus Conosciuti / Mechanus al Giorno sono clonate dallo stile canonico del Vol. 2 (tabelle tier 6 del Bardo),
  senza colonna 0 e senza R, larghezza adattata al formato pagina. Aggiunge keepNext ai titoli della sezione
  e tiene unite le tabelle di progressione e quella degli automaton.
- patch2_skitari_tecnomante.py — Skitari e Tecnomante a somma zero: Maestria I–VI unite in un privilegio progressivo
  (sostituisce Mechanus), Arma da fuoco + Addestramento + Riparazioni ridotte uniti (modifica Riparazioni),
  Odio per la magia sostituisce Fabbro esperto; vantaggio/svantaggio con lo stile di sistema.
- rimuovi_riempitivi.py — toglie i 99 paragrafi vuoti di riempimento che il Vol. 2 aveva nella sezione Inventore
  (con le aggiunte sarebbero finiti a metà pagina).
- aggiorna_indice.py — sposta i numeri di pagina dell'indice generale (−1 dalla voce Archetipi dell'Inventore in poi).
- pack.sh, dump.py, blocks.py — impacchettamento e dump testuale per i controlli.

Validazione: validate.py PASSED su entrambi; nel Vol. 2 nessuna modifica al testo fuori dalla sezione Inventore.
