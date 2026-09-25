"""Banco di prova della pulizia dei doppioni di Acu_Maker, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
Nato con Acu_Maker V1.8.0, il 25 settembre 2026.
Niente di questo fa rumore e niente tocca la collezione: si lavora su una
collezione finta, in memoria.
La domanda e' una: togli_doppioni toglie esattamente i preset che suonano
identici a un altro, cioe' stesso score, stessa forma d'onda e stesso
inviluppo, tiene quello con la descrizione piu' lunga, a parita' il primo,
e lascia stare tutti i suoni diversi, anche se si somigliano.
Si lancia con
  python banco_acumaker_doppioni.py
e stampa in fondo quante prove sono passate.
"""
import contextlib
import io
import json
import sys

import Acu_Maker as am

with open(am.DB_FILE, encoding="utf-8") as f:
	COLLEZIONE_PRIMA = json.load(f)
totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def suono(nota="c4", kind=1, adsr=None, descrizione="un suono"):
	return {"descrizione": descrizione, "score": [[nota, 0.2, 0.0, 0.0]], "kind": kind,
			"adsr": adsr or [2.0, 0.0, 100.0, 5.0]}

def pulisci(db):
	uscita = io.StringIO()
	with contextlib.redirect_stdout(uscita):
		tolti = am.togli_doppioni(db)
	return tolti, uscita.getvalue()

# 1. Tre suoni identici con descrizioni diverse: resta la descrizione piu' lunga.
db = {"corto": suono(descrizione="breve"), "lungo": suono(descrizione="la descrizione piu' lunga di tutte"),
	"medio": suono(descrizione="una media"), "altro": suono("e4")}
tolti, testo = pulisci(db)
prova("dei tre identici resta quello con la descrizione piu' lunga", sorted(db) == ["altro", "lungo"], sorted(db))
prova("i tolti sono detti con chi resta al loro posto", sorted(tolti) == [("corto", "lungo"), ("medio", "lungo")], tolti)
prova("una riga a console per ogni tolto", testo.count("Doppione tolto:") == 2 and "'corto'" in testo and "'lungo'" in testo, testo)

# 2. A parita' di descrizione resta il primo della collezione: e' il caso dei preset vuoti del tasto piu'.
vuoto = {"descrizione": "Nuovo preset vuoto", "score": [["c4", 0.5, 0.0, 0.0]], "kind": 1, "adsr": [0.002, 0.0, 100.0, 0.002]}
db = {"nuovo_preset": dict(vuoto), "nuovo_preset0": dict(vuoto), "nuovo_preset1": dict(vuoto)}
tolti, _ = pulisci(db)
prova("dei preset vuoti ne resta uno, il primo", list(db) == ["nuovo_preset"], list(db))

# 3. Basta una differenza per restare: forma d'onda, inviluppo, nota, durata, panorama, volume.
db = {
	"base": suono(),
	"onda": suono(kind=3),
	"inviluppo": suono(adsr=[3.0, 0.0, 100.0, 5.0]),
	"nota": suono("c#4"),
	"durata": {**suono(), "score": [["c4", 0.21, 0.0, 0.0]]},
	"panorama": {**suono(), "score": [["c4", 0.2, 0.1, 0.0]]},
	"volume": {**suono(), "score": [["c4", 0.2, 0.0, 0.05]]},
}
tolti, testo = pulisci(db)
prova("i suoni che differiscono in qualcosa restano tutti", len(db) == 7 and tolti == [], (len(db), tolti))
prova("e senza doppioni la console tace", testo == "", testo)

# 4. Il nome e la descrizione non bastano a fare un suono diverso.
db = {"alfa": suono(descrizione="sveglia"), "beta": suono(descrizione="allarme!")}
tolti, _ = pulisci(db)
prova("nomi e descrizioni diversi, suono identico: uno solo", len(db) == 1 and len(tolti) == 1, db)

# 5. La collezione vera non e' stata toccata.
with open(am.DB_FILE, encoding="utf-8") as f:
	db = json.load(f)
prova(f"la collezione sul disco e' intatta, {len(db)} preset", db == COLLEZIONE_PRIMA, len(db))

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
