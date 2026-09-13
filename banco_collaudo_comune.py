"""Banco di prova del menu di fine gruppo, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 13 settembre 2026, quando il menu e' diventato comune a tutti i
collaudi d'ascolto.
Niente di questo fa rumore, niente aspetta la tastiera e niente scrive dove
scrivono i collaudi veri: al posto di key e dgt ci sono due finte che
rispondono da un copione, e il registro va in una cartella temporanea.
La domanda e' se il menu faccia esattamente quello che promette, perche' un
menu che registra la cosa sbagliata rovina un collaudo intero e ce ne si
accorge solo rileggendo gli esiti a freddo.
Si lancia con
  python banco_collaudo_comune.py
e stampa in fondo quante prove sono passate.
"""
import os
import sys
import tempfile

import collaudo_comune as comune
from collaudo_comune import Esiti

totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def copione(tasti, testi=()):
	"""Sostituisce key e dgt con due finte che rispondono da un elenco."""
	tasti, testi = list(tasti), list(testi)
	comune.key = lambda prompt="": tasti.pop(0)
	comune.dgt = lambda prompt="", **kw: testi.pop(0)

def leggi(percorso):
	if not os.path.exists(percorso):
		return ""
	with open(percorso, encoding="utf-8") as f:
		return f.read()

print("Banco del menu di fine gruppo. Nessun suono, nessuna tastiera, nessun file vero toccato.\n")

with tempfile.TemporaryDirectory() as cartella:
	# 1. Le quattro scelte.
	casi = [
		(["\r"], [], 0, ["test superato, nessun commento"], "Invio da solo da' per superato"),
		(["r", "r", "\r"], [], 2, ["test superato, nessun commento"], "r riascolta, due volte"),
		(["c", "\r"], ["c'e' uno schiocco"], 0, ["c'e' uno schiocco"], "c commenta, poi Invio chiude"),
		(["c", "r", "c", "\r"], ["primo", "secondo"], 1, ["primo", "secondo"], "commenta, riascolta, ricommenta"),
		(["\x1b"], [], 0, ["chiuso senza giudizio"], "Escape chiude senza giudizio"),
		(["x", "up", "f5", "\r"], [], 0, ["test superato, nessun commento"], "i tasti non previsti non fanno niente"),
		(["c", "\x1b"], ["detto tutto"], 0, ["detto tutto"], "dopo un commento, Escape non aggiunge niente"),
	]
	for indice, (tasti, testi, ripetizioni, attesi, nota) in enumerate(casi):
		percorso = os.path.join(cartella, f"esiti{indice}.txt")
		esiti = Esiti(percorso, "intestazione di prova")
		riascolti = []
		copione(tasti, testi)
		esiti.esito("il gruppo", lambda lista=riascolti: lista.append(1), "la domanda")
		scritto = leggi(percorso)
		trovati = [r.split(": ", 1)[1] for r in scritto.splitlines() if r.startswith("Commento di Gabriele: ")]
		prova(nota, len(riascolti) == ripetizioni and trovati == attesi,
			  f"ripetizioni {len(riascolti)}, registro {trovati}")

	# 2. Il registro: intestazione una volta sola, esiti in coda.
	percorso = os.path.join(cartella, "coda.txt")
	esiti = Esiti(percorso, "prima riga\nseconda riga")
	esiti.registra("uno", "commento uno")
	esiti.registra("due", "commento due")
	scritto = leggi(percorso)
	prova("l'intestazione compare una volta sola", scritto.count("prima riga") == 1)
	prova("gli esiti si accumulano senza sovrascriversi",
		  scritto.count("GRUPPO:") == 2 and "commento uno" in scritto and "commento due" in scritto)
	prova("un commento vuoto diventa nessuno", "nessuno" in (esiti.registra("tre", "") or leggi(percorso)))

	# 3. La misura, che accompagna il giudizio.
	percorso = os.path.join(cartella, "misura.txt")
	esiti = Esiti(percorso, "", etichetta="PROVA")
	copione(["c", "\r"], ["mi convince"])
	esiti.esito("la prova alla cieca", None, "la domanda", misura="7 giuste su 10")
	scritto = leggi(percorso)
	prova("l'etichetta si puo' cambiare", "PROVA: la prova alla cieca" in scritto, scritto[:60])
	prova("la misura finisce nel registro accanto al commento",
		  "Misura: 7 giuste su 10" in scritto and "mi convince" in scritto)

	# 4. Senza la funzione di riascolto, r lo dice invece di cadere.
	percorso = os.path.join(cartella, "senza.txt")
	esiti = Esiti(percorso, "")
	copione(["r", "\r"], [])
	esiti.esito("senza riascolto", None, "la domanda")
	prova("r senza riascolto non fa cadere niente", "test superato" in leggi(percorso))

	# 5. Cosa restituisce, che serve a chi vuole saperlo.
	percorso = os.path.join(cartella, "ritorni.txt")
	esiti = Esiti(percorso, "")
	for tasti, testi, atteso in ((["\r"], [], "superato"), (["c", "\r"], ["x"], "commentato"), (["\x1b"], [], "chiuso")):
		copione(tasti, testi)
		prova(f"chiudendo con {tasti[-1]!r} restituisce {atteso}",
			  esiti.esito("t", None, "") == atteso)

	# 6. Il file dei collaudi veri non e' stato toccato.
	qui = os.path.dirname(os.path.abspath(__file__))
	sporcati = [n for n in os.listdir(qui) if n.endswith("_esiti.txt") and os.path.getmtime(os.path.join(qui, n)) > os.path.getmtime(__file__)]
	prova("nessun registro vero e' stato scritto dal banco", not sporcati, sporcati)

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
