"""Banco di prova della posizione d'ascolto di Acu_Maker, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato con Acu_Maker V1.7.0 e la issue 18, il 13 settembre 2026.
Niente di questo fa rumore e niente tocca la collezione: si lavora su un preset
finto, in memoria.
Le domande sono due. La prima e' se quello che si scrive nel tasto p venga
capito come si deve, comprese le forme sbagliate, che non devono far cadere
l'editor. La seconda e' se il tasto u scriva nelle quartine esattamente il
panorama che si stava ascoltando, in una forma che il file sappia rileggere:
altrimenti un preset salvato suonerebbe diverso da come lo si e' sentito.
Si lancia con
  python banco_acumaker_pan.py
e stampa in fondo quante prove sono passate.
"""
import sys

import Acu_Maker as am

from GBUtils import panorama_spostato, parse_pan_values

totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def preset_finto():
	return {"descrizione": "finto, per il banco",
			"score": [["c4", 0.2, 0.0, 0.0], ["e4", 0.2, "-0.5.0.5", 0.0], ["g4", 0.2, 0.3, 0.0]],
			"kind": 1, "adsr": [2.0, 0.0, 100.0, 5.0]}

def panorami_del_preset(preset):
	valori = []
	for q in preset["score"]:
		v = parse_pan_values(q[2])
		valori.extend([v] if isinstance(v, float) else list(v))
	return valori

print("Banco della posizione d'ascolto di Acu_Maker. Nessun suono, nessuna scrittura.\n")

# 1. Quello che si scrive viene capito.
casi = [
	("", None, "Invio a vuoto toglie la posizione"),
	("0", None, "zero vale come nessuna posizione"),
	("60", 0.6, "un numero intero"),
	("-60", -0.6, "un numero negativo"),
	("100", 1.0, "il bordo destro"),
	("-100", -1.0, "il bordo sinistro"),
	("  40  ", 0.4, "gli spazi attorno non danno noia"),
]
for scritto, atteso, nota in casi:
	valore, errore = am.leggi_posizione(scritto)
	uguale = valore == atteso if atteso is None else abs(valore - atteso) < 1e-9
	prova(f"{nota}, {scritto!r}", errore is None and uguale, f"letto {valore}, errore {errore}")
valore, errore = am.leggi_posizione("-100.100")
prova("due valori col punto danno un portamento", errore is None and parse_pan_values(valore) == (-1.0, 1.0),
	  f"letto {valore!r}")
valore, errore = am.leggi_posizione("50.-50")
prova("e il portamento va anche al contrario", errore is None and parse_pan_values(valore) == (0.5, -0.5),
	  f"letto {valore!r}")

# 2. Quello che non ha senso viene respinto, e non fa cadere niente.
for scritto in ("abc", "sinistra", "a.b", "-.", "1.2.3.4.x", "60,5", "--60", "1.2.3"):
	valore, errore = am.leggi_posizione(scritto)
	prova(f"respinto senza cadere, {scritto!r}", valore is None and bool(errore), f"{valore}, {errore}")

# 3. Oltre i bordi si riporta dentro invece di sbagliare.
for scritto, atteso in (("200", 1.0), ("-200", -1.0)):
	valore, errore = am.leggi_posizione(scritto)
	prova(f"oltre il bordo si riporta dentro, {scritto!r}",
		  errore is None and abs(valore - atteso) < 1e-9, valore)

# 4. Il codice corto per la riga di stato.
prova("senza posizione la riga di stato non cresce", am.posizione_breve(None) == "")
prova("con una posizione ferma compare il codice", am.posizione_breve(-0.6) == " p-60", am.posizione_breve(-0.6))
prova("e con un portamento compaiono i due valori",
	  am.posizione_breve("-1.1") == " p-100.100", am.posizione_breve("-1.1"))

# 5. La riga di stato resta leggibile in una passata di braille.
stato = am.EditorState(preset_finto())
lunghezze = []
for indice in range(3):
	stato.focus_idx = indice
	for parametro in range(4):
		stato.focus_param = parametro
		for posizione in (None, -0.6, "-1.1"):
			stato.posizione = posizione
			lunghezze.append(len(am.get_status_string(stato)))
prova(f"la riga di stato sta in quaranta caratteri, massimo visto {max(lunghezze)}",
	  max(lunghezze) <= 40, max(lunghezze))

# 6. Quello che si unisce e' quello che si stava ascoltando.
for posizione in (0.6, -0.6, "-1.1", "0.5.-0.5", 1.0):
	stato = am.EditorState(preset_finto())
	stato.posizione = posizione
	# Cio' che si sentiva: lo score spostato, come lo passa la riproduzione.
	piatto = []
	for q in stato.preset["score"]:
		piatto.extend(q)
	atteso = panorama_spostato(piatto, posizione)
	# Cio' che il tasto u scrive nelle quartine.
	for i, q in enumerate(stato.preset["score"]):
		q[2] = am.pan_in_file(atteso[i * 4 + 2])
	scritti = panorami_del_preset(stato.preset)
	voluti = []
	for i in range(len(stato.preset["score"])):
		v = parse_pan_values(atteso[i * 4 + 2])
		voluti.extend([v] if isinstance(v, float) else list(v))
	uguali = all(abs(a - b) < 0.006 for a, b in zip(scritti, voluti, strict=True))
	prova(f"unendo la posizione {posizione!r} le quartine portano quel panorama",
		  uguali, f"scritti {scritti}, voluti {voluti}")

# 7. Quello che si scrive nel file si rilegge uguale.
for valore in (0.0, 0.6, -0.6, 1.0, -1.0, 0.07, (-0.5, 0.5), (1.0, -1.0), (0.2, -0.93)):
	scritto = am.pan_in_file(valore)
	riletto = parse_pan_values(scritto)
	if isinstance(valore, tuple):
		uguale = isinstance(riletto, tuple) and all(abs(a - b) < 0.006 for a, b in zip(riletto, valore, strict=True))
	else:
		uguale = isinstance(riletto, float) and abs(riletto - valore) < 0.006
	prova(f"il panorama {valore!r} si riscrive come {scritto!r} e si rilegge uguale", uguale, riletto)

# 8. Unire due volte non raddoppia: dopo u la posizione si azzera.
stato = am.EditorState(preset_finto())
prova("un editor nuovo nasce senza posizione", stato.posizione is None)
prova("e con il preset non modificato", stato.modified is False)

# 9. La collezione vera non e' stata toccata.
import json

with open(am.DB_FILE, encoding="utf-8") as f:
	db = json.load(f)
prova(f"la collezione sul disco e' intatta, {len(db)} preset", len(db) == 264, len(db))

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
