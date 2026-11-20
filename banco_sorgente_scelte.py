"""Banco di prova di sorgente_delle_scelte, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato con la V1.0.0 di sorgente_delle_scelte, la V5.3.0 di menu e la V2.1.0 di
enter_escape, il 21 novembre 2026, per la plancia di Orologic 9.
Registra una sorgente delle scelte finta e controlla che menu le consegni le
voci invece di stamparle e di leggere tasti, e che enter_escape la avvisi
della domanda e legga il tasto come sempre, con l'uscita catturata e i tasti
da sorgente_dei_tasti: niente console, niente finestre.
Si lancia con
  python banco_sorgente_scelte.py
e stampa in fondo quante prove sono passate.
"""
import contextlib
import io
import sys

from GBUtils import enter_escape, menu, sorgente_dei_tasti, sorgente_delle_scelte

risultati = []


def prova(nome, ottenuto, atteso):
	esito = ottenuto == atteso
	risultati.append(esito)
	print(f"{'ok' if esito else 'NO'} {nome}: {ottenuto!r}" + ("" if esito else f", atteso {atteso!r}"))


class Scelte:
	"""La sorgente delle scelte: risponde con le risposte in fila e ricorda
	le chiamate."""

	def __init__(self, *risposte):
		self.risposte = list(risposte)
		self.chiamate = []

	def __call__(self, tipo, voci, prompt, vuoto):
		self.chiamate.append((tipo, voci, prompt, vuoto))
		if tipo != "menu":
			return "ignorato"
		risposta = self.risposte.pop(0)
		if risposta == "ctrl-c":
			raise KeyboardInterrupt
		return risposta


class Tasti:
	def __init__(self, *tasti):
		self.tasti = list(tasti)

	def __call__(self, _attesa):
		return self.tasti.pop(0)


def catturato(funzione, *argomenti, **opzioni):
	uscita = io.StringIO()
	with contextlib.redirect_stdout(uscita):
		valore = funzione(*argomenti, **opzioni)
	return valore, uscita.getvalue()


VOCI = {"beta": "La seconda voce", "Alfa": "La prima voce", ".": "Esci"}


def main():
	prova("nessuna sorgente all'inizio", sorgente_delle_scelte(None), None)
	scelte = Scelte("beta")
	prova("la prima registrazione restituisce None", sorgente_delle_scelte(scelte), None)
	valore, stampato = catturato(menu, VOCI, p="Scegli: ", empty_enter="avanti")
	prova("menu restituisce la scelta della sorgente", valore, "beta")
	prova("menu non stampa niente", stampato, "")
	prova("le voci in ordine, col prompt e Invio a vuoto", scelte.chiamate,
		[("menu", [(".", "Esci"), ("Alfa", "La prima voce"), ("beta", "La seconda voce")], "Scegli: ", "avanti")])
	scelte = Scelte(None)
	sorgente_delle_scelte(scelte)
	prova("Esc dalla sorgente", catturato(menu, VOCI, ordered=False)[0], None)
	prova("senza ordinare, l'ordine del dizionario", [k for k, _d in scelte.chiamate[0][1]], ["beta", "Alfa", "."])
	scelte = Scelte("Alfa")
	sorgente_delle_scelte(scelte)
	prova("con numbered le chiavi vere", catturato(menu, VOCI, numbered=True)[0], "Alfa")
	prova("con numbered la sorgente vede le chiavi vere", [k for k, _d in scelte.chiamate[0][1]], [".", "Alfa", "beta"])
	scelte = Scelte()
	sorgente_delle_scelte(scelte)
	prova("una voce sola torna subito", catturato(menu, {"solo": "L'unica"})[0], "solo")
	prova("il dizionario vuoto torna None", catturato(menu, {})[0], None)
	valore, stampato = catturato(menu, VOCI, show_only=True)
	prova("show_only stampa ancora l'elenco", "La prima voce" in stampato, True)
	prova("senza mai chiamare la sorgente", scelte.chiamate, [])
	sorgente_delle_scelte(Scelte("ctrl-c"))
	try:
		catturato(menu, VOCI)
		prova("l'interruzione dalla sorgente", "nessuna", "KeyboardInterrupt")
	except KeyboardInterrupt:
		prova("l'interruzione dalla sorgente", "KeyboardInterrupt", "KeyboardInterrupt")
	scelte = Scelte()
	sorgente_delle_scelte(scelte)
	sorgente_dei_tasti(Tasti("x", "\r"))
	valore, stampato = catturato(enter_escape, "Confermi? ")
	prova("enter_escape legge il tasto come sempre", valore, True)
	prova("enter_escape avvisa a ogni attesa", scelte.chiamate,
		[("enter_escape", None, "Confermi? ", None), ("enter_escape", None, "Confermi? ", None)])
	sorgente_dei_tasti(Tasti("\x1b"))
	prova("enter_escape con Esc", catturato(enter_escape, "Confermi? ")[0], False)
	sorgente_dei_tasti(None)
	try:
		sorgente_delle_scelte("non una funzione")
		prova("una sorgente che non e' una funzione", "accettata", "TypeError")
	except TypeError:
		prova("una sorgente che non e' una funzione", "TypeError", "TypeError")
	prova("togliere la sorgente restituisce l'ultima", sorgente_delle_scelte(None) is scelte, True)
	sorgente_dei_tasti(Tasti("b"))
	valore, stampato = catturato(menu, VOCI, p="> ")
	prova("senza sorgente menu legge i tasti", valore, "beta")
	prova("e stampa le voci", "La seconda voce" in stampato, True)
	sorgente_dei_tasti(None)
	passate = sum(risultati)
	print(f"Prove passate: {passate} di {len(risultati)}.")
	return 0 if passate == len(risultati) else 1


if __name__ == "__main__":
	sys.exit(main())
