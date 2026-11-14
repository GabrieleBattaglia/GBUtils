"""Banco di prova del player di Acu_Maker, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 per la issue 51, con Acu_Maker 1.12.0.
Niente di questo suona e niente tocca la collezione vera: i tasti arrivano
da un copione al posto di key, il motore e' una finta che raccoglie cio' che
suonerebbe, e la collezione e' di quattro preset in una cartella temporanea.
La domanda e' se il player faccia quello che la issue chiede: avanti e
indietro, il numero, il nome alla prima occorrenza, la sequenza che si ferma
al primo tasto, l'uscita, e il prompt con il numero e il nome fra due ritorni
carrello.
Si lancia con
  python banco_player.py
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
from GBUtils import Acusticator

totale = passate = 0
SCADE = object()

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

class MotoreFinto:
	def __init__(self):
		self.suonati, self.fermati = [], 0
	prepara = staticmethod(Acusticator.prepara)
	aggiorna = staticmethod(Acusticator.aggiorna)
	def __call__(self, score, kind=1, adsr=None, sync=False, pan=None):
		self.suonati.append(score[0])
		return True
	def stop(self):
		self.fermati += 1
		return 0

def gioca(coll, copione, scritti=()):
	"""Fa girare il player con i tasti del copione. Restituisce le note
	suonate, cioe' quale preset, i prompt e cio' che ha stampato."""
	coda, righe, prompt = list(copione), list(scritti), []
	def tasto_finto(testo="", attesa=None, alla_scadenza=""):
		prompt.append((testo, attesa))
		passo = coda.pop(0) if coda else "\x1b"
		return alla_scadenza if passo is SCADE else passo
	am.key = tasto_finto
	am.input = lambda testo="": righe.pop(0) if righe else ""
	GBUtils.input = am.input
	motore.suonati.clear()
	uscita = io.StringIO()
	with contextlib.redirect_stdout(uscita):
		am.player(coll)
	return [NOTE[n] for n in motore.suonati], prompt, uscita.getvalue()

motore = MotoreFinto()
am.Acusticator = motore
# Ogni preset ha la sua nota, cosi' dallo score si sa quale e' suonato.
NOTE = {"c4": "alfa", "d4": "beta", "e4": "delta", "f4": "gamma"}
print("Banco del player di Acu_Maker. Nessun suono, la collezione vera non si tocca.")
with tempfile.TemporaryDirectory() as cartella:
	percorso = os.path.join(cartella, "quattro.json")
	dati = {nome: {"descrizione": nome, "score": [[nota, 0.2, 0, 0.0], ["p", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}
			for nota, nome in NOTE.items()}
	with open(percorso, "w", encoding="utf-8") as f:
		json.dump(dati, f)
	coll = am.Collezione(percorso)
	with contextlib.redirect_stdout(io.StringIO()):
		coll.apri()

	# 1. Avanti, indietro, i bordi, l'inizio e la fine.
	suonati, prompt, testo = gioca(coll, ["right", "right", "left", "end", "right", "home", "\x1b"])
	prova("all'ingresso suona il primo, poi a ogni passo quello su cui arriva",
		  suonati == ["alfa", "beta", "delta", "beta", "gamma", "gamma", "alfa"], suonati)
	prova("al bordo non si gira e lo si dice", "Ultimo preset." in testo)
	prova("il prompt dice il numero e il nome fra due ritorni carrello",
		  [p for p, _ in prompt[:3]] == ["\r1 alfa\r", "\r2 beta\r", "\r3 delta\r"], prompt[:3])
	prova("l'ordine e' quello del menu, alfabetico", "Player, 4 preset." in testo)

	# 2. Il numero e il nome.
	suonati, prompt, testo = gioca(coll, ["n", "/", "/", " ", "/", "\x1b"], ["3", "gam", "ta", "zeta"])
	prova("n porta al numero scritto", suonati[1] == "delta", suonati)
	prova("/ porta alla prima occorrenza, prima per inizio di nome", suonati[2] == "gamma", suonati)
	prova("e poi per parte del nome", suonati[3] == "beta", suonati)
	prova("Spazio riascolta", suonati[4] == "beta", suonati)
	prova("un nome che non c'e' si dice e non si muove", "Nessun preset con quel nome." in testo and len(suonati) == 5, suonati)

	# 3. La sequenza: suona uno dopo l'altro finche' non si preme un tasto.
	suonati, prompt, testo = gioca(coll, ["right", "\r", SCADE, SCADE, SCADE, "\x1b"])
	prova("Invio suona in sequenza dal preset attuale fino all'ultimo", suonati == ["alfa", "beta", "beta", "delta", "gamma"], suonati)
	prova("e dice quando la collezione e' finita", "Fine della collezione." in testo)
	attese = [a for _, a in prompt if a is not None]
	prova("ogni preset aspetta la sua durata, poco piu' di tre decimi", attese and all(0.6 < a < 0.8 for a in attese), attese)
	fermati = motore.fermati
	suonati, prompt, testo = gioca(coll, ["\r", SCADE, "x", "right", "\x1b"])
	prova("un tasto ferma la sequenza dove e' arrivata", suonati == ["alfa", "alfa", "beta", "delta"], suonati)
	prova("e zittisce", motore.fermati > fermati)

	# 4. L'aiuto, il silenzio e l'uscita.
	suonati, prompt, testo = gioca(coll, ["?", "k", "\x1b"])
	prova("? ripete i tasti", testo.count("Destra e Sinistra") == 2)
	prova("Esc torna al menu", len(prompt) == 3)

	# 6. L'ordine non distingue le maiuscole, come quello di menu: fino alla
	# 1.13.16 i preset con l'iniziale maiuscola venivano tutti prima della a
	# (collaudo di Gabriele del 14 novembre 2026).
	percorso_misto = os.path.join(cartella, "misto.json")
	misti = {nome: {"descrizione": nome, "score": [[nota, 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}
			 for nota, nome in (("c4", "beta"), ("d4", "Delta"), ("e4", "alfa"), ("f4", "Gamma"))}
	with open(percorso_misto, "w", encoding="utf-8") as f:
		json.dump(misti, f)
	coll_mista = am.Collezione(percorso_misto)
	with contextlib.redirect_stdout(io.StringIO()):
		coll_mista.apri()
	suonati, prompt, testo = gioca(coll_mista, ["right", "right", "right", "\x1b"])
	prova("l'ordine non distingue le maiuscole",
		  [p for p, _ in prompt[:4]] == ["\r1 alfa\r", "\r2 beta\r", "\r3 Delta\r", "\r4 Gamma\r"], prompt[:4])

	# 7. c carica nell'editor il preset su cui si e', e uscendo si torna al
	# player sullo stesso preset, anche se intanto la collezione e' cambiata.
	# Dalla 1.14.0, dal collaudo di Gabriele del 14 novembre 2026. L'editor
	# finto salva un preset nuovo, che nell'ordine viene prima di beta.
	editati = []
	def editor_finto(collezione, nome, nuovo=None):
		editati.append(nome)
		with contextlib.redirect_stdout(io.StringIO()):
			collezione.salva_nuovo("aaa_nuovo", {"descrizione": "nuovo", "score": [["g4", 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]})
	vero_editor = am.edit_mode
	am.edit_mode = editor_finto
	try:
		suonati, prompt, testo = gioca(coll, ["right", "c", "right", "\x1b"])
	finally:
		am.edit_mode = vero_editor
	prova("c carica nell'editor il preset su cui si e'", editati == ["beta"], editati)
	prova("e uscendo si torna al player sullo stesso preset",
		  [p for p, _ in prompt[:4]] == ["\r1 alfa\r", "\r2 beta\r", "\r3 beta\r", "\r4 delta\r"], prompt[:4])
	prova("l'aiuto dice il tasto c", "c lo carica nell'editor" in testo)

	# 8. Dalla quarta revisione: se dall'editor il preset esce tolto, per
	# esempio con Sovrascrivi e Lascialo tolto, il player resta allo stesso
	# posto; se la collezione resta vuota lo dice e torna al menu.
	def collezione_di(nome_file, nomi):
		percorso_nuovo = os.path.join(cartella, nome_file)
		with open(percorso_nuovo, "w", encoding="utf-8") as f:
			json.dump({n: {"descrizione": n, "score": [[nota, 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}
					   for nota, n in nomi}, f)
		nuova = am.Collezione(percorso_nuovo)
		with contextlib.redirect_stdout(io.StringIO()):
			nuova.apri()
		return nuova
	def editor_che_toglie(collezione, nome, nuovo=None):
		with contextlib.redirect_stdout(io.StringIO()):
			collezione.elimina(nome)
	am.edit_mode = editor_che_toglie
	try:
		tre = collezione_di("tre.json", (("c4", "alfa"), ("d4", "beta"), ("f4", "gamma")))
		suonati, prompt, testo = gioca(tre, ["right", "c", "\x1b"])
		sola = collezione_di("sola.json", (("c4", "alfa"),))
		_, prompt_sola, testo_sola = gioca(sola, ["c", "right"])
	finally:
		am.edit_mode = vero_editor
	prova("tolto dall'editor, il player resta allo stesso posto", [p for p, _ in prompt[:3]] == ["\r1 alfa\r", "\r2 beta\r", "\r2 gamma\r"], prompt[:3])
	prova("e con la collezione vuota lo dice e torna al menu", "La collezione e' vuota." in testo_sola and len(prompt_sola) == 1, (testo_sola[-80:], prompt_sola))

	# 9. Dalla quarta revisione: dopo n e / il player non lascia una riga
	# vuota. Qui la tastiera e input finti scrivono come la console vera:
	# il prompt, e la risposta con il suo a capo.
	coda_console = ["n", "/", "\x1b"]
	risposte_console = ["3", "gam"]
	def tasto_console(testo="", attesa=None, alla_scadenza=""):
		print(testo, end="")
		return coda_console.pop(0) if coda_console else "\x1b"
	def input_console(testo=""):
		risposta = risposte_console.pop(0) if risposte_console else ""
		print(testo + risposta)
		return risposta
	am.key = tasto_console
	am.input = input_console
	GBUtils.input = input_console
	uscita = io.StringIO()
	with contextlib.redirect_stdout(uscita):
		am.player(coll)
	righe_viste = [r.replace("\r", "") for r in uscita.getvalue().split("\n")]
	vuote = [i for i, r in enumerate(righe_viste[:-1]) if not r.strip()]
	prova("dopo n e / nessuna riga vuota", vuote == [], [righe_viste[i - 1:i + 2] for i in vuote])

# 5. La ricerca e la durata, da sole.
prova("cerca_nome trova per inizio di nome", am.cerca_nome(["alfa", "beta", "betulla"], "BET") == 1)
prova("e per parte del nome", am.cerca_nome(["alfa", "beta", "delta"], "lta") == 2)
prova("e risponde None se non c'e'", am.cerca_nome(["alfa"], "zeta") is None and am.cerca_nome(["alfa"], " ") is None)
prova("la durata somma le quartine, anche quelle strane", abs(am.durata_preset({"score": [["c4", 0.2], ["p", "0.3"], ["x", "?"], []]}) - 0.5) < 1e-9)
am.Acusticator = Acusticator

print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
