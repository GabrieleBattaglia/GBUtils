"""Banco di prova del volume come lista di scarti, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 per la issue 47, con Acusticator 8.8.0 e Acu_Maker 1.10.0.
Non suona niente e non scrive niente: la collezione vera si legge soltanto,
quella di prova sta in una cartella temporanea, e al posto del motore che
suona c'e' una finta che raccoglie gli score.
Le domande sono tre. Il motore legge la scivolata di volume scritta come
lista di scarti dalla base, e il testo ancora come volume assoluto? Acu_Maker
mostra e scrive i volumi come le app li suonano, e suona lui stesso come le
app? E gli undici preset di PokerMachine con il volume scritto come testo
sono diventati liste che danno gli stessi volumi di prima?
Si lancia con
  python banco_volume_lista.py
e stampa in fondo quante prove sono passate.
"""
import contextlib
import io
import json
import os
import sys
import tempfile

import Acu_Maker as am

import GBUtils
from GBUtils import Acusticator, parse_vol_values

QUI = os.path.dirname(os.path.abspath(__file__))
totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def vicini(a, b):
	if isinstance(a, tuple) or isinstance(b, tuple):
		return isinstance(a, tuple) and isinstance(b, tuple) and all(abs(x - y) < 1e-9 for x, y in zip(a, b))
	return abs(a - b) < 1e-9

def volumi(score):
	return [score[i + 3] for i in range(0, len(score), 4)]

print("Banco del volume come lista. Nessun suono, nessuna scrittura sulla collezione vera.")

# 1. Il motore.
preset = {"score": [["c4", 0.1, 0, [0.0, 0.3]], ["e4", 0.1, 0, 0.1], ["g4", 0.1, 0, "0.55.0.25"], ["c5", 0.1, 0, [-0.5, 0.9]]],
		  "kind": 1, "adsr": [1, 0, 100, 1]}
score, kind, adsr = Acusticator.prepara(preset)
v = volumi(score)
prova("la lista [0.0, 0.3] va da 0,5 a 0,8", vicini(v[0], (0.5, 0.8)), v[0])
prova("un numero resta uno scarto dalla base", vicini(v[1], 0.6), v[1])
prova("il testo resta un volume assoluto, come prima", parse_vol_values(v[2]) == (0.55, 0.25), v[2])
prova("e la lista resta fra 0 e 1", vicini(v[3], (0.0, 1.0)), v[3])
score, _, _ = Acusticator.prepara(preset, volume=0.8)
prova("con un'altra base la lista la segue", vicini(volumi(score)[0], (0.8, 1.0)), volumi(score)[0])
errori = io.StringIO()
with contextlib.redirect_stderr(errori):
	score, _, _ = Acusticator.prepara({"score": [["c4", 0.1, 0, [1, 2, 3]], ["c4", 0.1, 0, ["x", 0]], ["c4", 0.1, 0, True]]})
prova("una lista sbagliata vale la base, con un avviso, senza cadere", volumi(score) == [0.5, 0.5, 0.5] and errori.getvalue().count("non valido") == 3,
	  (volumi(score), errori.getvalue()))
buffer = Acusticator.sintetizza(Acusticator.prepara(preset)[0])
prova("e il motore la suona", buffer is not None and len(buffer) > 0)

# 2. save scrive la coppia del motore come lista di scarti, e preset la rilegge.
with tempfile.TemporaryDirectory() as cartella:
	percorso = os.path.join(cartella, "prova.json")
	with contextlib.redirect_stderr(io.StringIO()):
		scritto = Acusticator.save("banco_lista", ["c4", 0.1, 0, (0.5, 0.8)], descrizione="prova", percorso=percorso)
	with open(percorso, encoding="utf-8") as f:
		nel_file = json.load(f)["banco_lista"]["score"][0][3]
	prova("save scrive la coppia come lista di scarti", scritto and nel_file == [0.0, 0.3], nel_file)
	ripreso = Acusticator.prepara({"score": [["c4", 0.1, 0, nel_file]]})[0][3]
	prova("e rilegge gli stessi volumi", vicini(ripreso, (0.5, 0.8)), ripreso)
	# Dalla revisione del 13 novembre 2026: anche il testo del motore diventa
	# scarti, e un testo che non si legge si rifiuta.
	for testo, atteso in (("0.5.0.8", [0.0, 0.3]), ("0.7", 0.2), ("1.0.0.0", [0.5, -0.5])):
		with contextlib.redirect_stderr(io.StringIO()):
			scritto = Acusticator.save("banco_testo", ["c4", 0.1, 0, testo], descrizione="prova", percorso=percorso)
		with open(percorso, encoding="utf-8") as f:
			nel_file = json.load(f)["banco_testo"]["score"][0][3]
		uguale = (nel_file == atteso) if isinstance(atteso, list) else (isinstance(nel_file, float) and abs(nel_file - atteso) < 1e-9)
		prova(f"save scrive il testo {testo!r} come scarti, {atteso}", scritto and uguale, nel_file)
	errori = io.StringIO()
	with contextlib.redirect_stderr(errori):
		scritto = Acusticator.save("banco_forte", ["c4", 0.1, 0, "forte"], descrizione="prova", percorso=percorso)
	prova("un volume testo che non si legge si rifiuta, con l'avviso", scritto is False and "non valido" in errori.getvalue())

# 3. Acu_Maker mostra e scrive i volumi come le app.
prova("Acu_Maker mostra la lista nella sua scala", am.vol_to_user([0.0, 0.3]) == "50.80", am.vol_to_user([0.0, 0.3]))
prova("e scrive la scivolata come lista", am.user_to_vol("50.80") == [0.0, 0.3], am.user_to_vol("50.80"))
prova("da 20 a 80", am.user_to_vol("20.80") == [-0.3, 0.3], am.user_to_vol("20.80"))
prova("un volume fermo resta un numero", am.user_to_vol("80") == 0.3, am.user_to_vol("80"))
prova("il testo di prima si mostra assoluto, come lo suonano le app", am.vol_to_user("0.55.0.25") == "55.25", am.vol_to_user("0.55.0.25"))
prova("e una lista e' una scivolata per l'editor", am.scivola([0.0, 0.3]) and am.scivola("0.1.0.5") and not am.scivola(0.2))

# 4. L'editor suona come le app, su tutta la collezione.
suonati = []
class MotoreFinto:
	prepara = staticmethod(Acusticator.prepara)
	def __call__(self, score, kind=1, adsr=None, sync=False, pan=None):
		suonati.append((score, kind, adsr))
am.Acusticator = MotoreFinto()
with open(os.path.join(QUI, "Acu_Collection.json"), encoding="utf-8") as f:
	collezione = json.load(f)
diversi = []
errori = io.StringIO()
with contextlib.redirect_stderr(errori):
	for nome, dati in collezione.items():
		suonati.clear()
		am.play_preset(am.EditorState(dati))
		if suonati[0] != Acusticator.prepara(dati, nome=nome):
			diversi.append(nome)
prova(f"l'editor suona come le app tutti i {len(collezione)} preset", diversi == [], diversi[:5])
stato = am.EditorState(collezione[next(iter(collezione))])
suonati.clear()
am.play_quad(stato)
prova("e la quartina sola passa dalla stessa lettura", len(suonati) == 1 and len(suonati[0][0]) == 4)
am.Acusticator = Acusticator

# 5. Gli undici preset di PokerMachine, con i volumi che avevano come testo.
PRIMA = {
	"pokermachine_chiusura": "0.55.0.25", "pokermachine_scala_reale": "0.5.0.65", "pokermachine_killer_hand": "0.45.0.6",
	"kh_penalita": "0.55.0.4", "pokermachine_record_vincita": "0.45.0.55", "pokermachine_record_perdita": "0.5.0.4",
	"pokermachine_game_over": "0.5.0.2", "pokermachine_cinque_gemelle": "0.5.0.65",
	"pokermachine_sorpresa_tutto_o_niente": "0.45.0.6", "pokermachine_trofeo_rimonta": "0.4.0.6",
	"pokermachine_trofeo_tutto_vinto": "0.5.0.7",
}
testi = [n for n, d in collezione.items() for q in d.get("score", []) if isinstance(q[3], str)]
prova("nella collezione non resta nessun volume scritto come testo", testi == [], testi)
for nome, vecchio in PRIMA.items():
	adesso = [q[3] for q in collezione[nome]["score"] if isinstance(q[3], list)]
	assoluto = Acusticator.prepara({"score": [["c4", 0.1, 0, adesso[0]]]})[0][3] if adesso else None
	prova(f"{nome} da {vecchio} a {adesso[0] if adesso else None}, stessi volumi nelle app",
		  len(adesso) == 1 and assoluto is not None and vicini(assoluto, parse_vol_values(vecchio)), assoluto)

print(f"Prove {totale}, passate {passate}.")
del GBUtils
sys.exit(0 if passate == totale else 1)
