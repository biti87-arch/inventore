# Officina dell'Inventore

App per l'Inventore della Collana (Vol. 2 - Classi): mechanus conosciuti e al giorno, tecno-arma con modifiche e nodi, automaton (Destructor, Defensor, Sagittar, alpha del mechautarca), esoscheletri leggero e pesante, gadget, optional e doti per livello, tutti i 7 archetipi, contatori di gioco.

## Scaricare l'app
Nella pagina **Releases** del repository:
- **Android**: il file `Inventore-N.apk` (release `v1.0.N`). Scaricalo dal telefono e aprilo per installarlo.
- **Windows**: release `win-1.0.N`, versione *portatile* (doppio clic, niente installazione) o *installazione*.

Le app si ricompilano da sole a ogni aggiornamento del ramo `main`.

## Come si aggiorna quando cambia il manuale
1. Metti il .docx aggiornato dell'Inventore in `sorgenti/docx/` (togli il vecchio).
2. `python3 sorgenti/estrai_testo.py` → testo in `sorgenti/txt/`
3. `python3 sorgenti/parse_inventore.py` → `sorgenti/inventore.json`
4. `python3 sorgenti/build.py` → `www/index.html`

Le decisioni prese in chat e non ancora riportate nel manuale sono applicate da `CORREZIONI` in fondo a `parse_inventore.py`: quando il manuale viene corretto, quelle righe non fanno più nulla.
Le icone si rigenerano con `python3 sorgenti/icone.py`.

## Decisioni di design
Vedi `Inventore_app_design_v1.md`.
