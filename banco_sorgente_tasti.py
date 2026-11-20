"""Banco di prova di sorgente_dei_tasti, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato con la V1.0.0 di sorgente_dei_tasti e la V8.1.0 di key, il 20 novembre
2026, per Orologic 9 e il suo strato unico (punto 74 di idee.txt).
Registra una sorgente che da' i tasti da una lista, invece della console, e
controlla che key, enter_escape e menu li leggano da li', con l'uscita
catturata: niente console, niente finestre, niente tasti premuti davvero.
Si lancia con
  python banco_sorgente_tasti.py
e stampa in fondo quante prove sono passate.
"""
import contextlib
import io
import sys

from GBUtils import enter_escape, key, menu, sorgente_dei_tasti

risultati = []


def prova(nome, ottenuto, atteso):
	esito = ottenuto == atteso
	risultati.append(esito)
	print(f"{'ok' if esito else 'NO'} {nome}: {ottenuto!r}" + ("" if esito else f", atteso {atteso!r}"))


class Lista:
	"""La sorgente: i tasti in fila; None nella fila fa scadere l'attesa.
	Ricorda le attese ricevute."""

	def __init__(self, *tasti):
		self.tasti = list(tasti)
		self.attese = []

	def __call__(self, attesa):
		self.attese.append(attesa)
		if not self.tasti:
			raise AssertionError("la sorgente e' rimasta senza tasti")
		tasto = self.tasti.pop(0)
		if tasto == "ctrl-c":
			raise KeyboardInterrupt
		return tasto


def catturato(funzione, *argomenti, **opzioni):
	uscita = io.StringIO()
	with contextlib.redirect_stdout(uscita):
		valore = funzione(*argomenti, **opzioni)
	return valore, uscita.getvalue()


def main():
	prova("nessuna sorgente all'inizio", sorgente_dei_tasti(None), None)
	sorgente = Lista("a")
	prova("la prima registrazione restituisce None", sorgente_dei_tasti(sorgente), None)
	valore, stampato = catturato(key, "Scegli: ")
	prova("key restituisce il tasto della sorgente", valore, "a")
	prova("key stampa il prompt", stampato, "Scegli: ")
	prova("key passa l'attesa senza limite", sorgente.attese, [None])
	sorgente = Lista("up", "f5", "\r", "\x1b", "\x08")
	sorgente_dei_tasti(sorgente)
	prova("i nomi speciali passano com'e'", [key() for _ in range(5)], ["up", "f5", "\r", "\x1b", "\x08"])
	sorgente = Lista(None, None)
	sorgente_dei_tasti(sorgente)
	prova("alla scadenza il predefinito", key(attesa=0.5), "")
	prova("alla scadenza il valore scelto", key(attesa=2, alla_scadenza=None), None)
	prova("l'attesa arriva come numero", sorgente.attese, [0.5, 2.0])
	sorgente_dei_tasti(Lista("ctrl-c"))
	try:
		key()
		prova("Ctrl+C dalla sorgente", "nessuna interruzione", "KeyboardInterrupt")
	except KeyboardInterrupt:
		prova("Ctrl+C dalla sorgente", "KeyboardInterrupt", "KeyboardInterrupt")
	sorgente_dei_tasti(Lista("\r"))
	valore, stampato = catturato(enter_escape, "Confermi? ")
	prova("enter_escape con Invio", valore, True)
	prova("enter_escape stampa il prompt", "Confermi? " in stampato, True)
	sorgente_dei_tasti(Lista("\x1b"))
	prova("enter_escape con Esc", catturato(enter_escape, "Confermi? ")[0], False)
	sorgente_dei_tasti(Lista("b"))
	valore, stampato = catturato(menu, {"alfa": "La prima voce", "beta": "La seconda voce"}, p="> ")
	prova("menu sceglie dalla sorgente", valore, "beta")
	prova("menu mostra le voci", "La seconda voce" in stampato, True)
	try:
		sorgente_dei_tasti("non una funzione")
		prova("una sorgente che non e' una funzione", "accettata", "TypeError")
	except TypeError:
		prova("una sorgente che non e' una funzione", "TypeError", "TypeError")
	ultima = Lista()
	sorgente_dei_tasti(ultima)
	prova("togliere la sorgente restituisce l'ultima", sorgente_dei_tasti(None) is ultima, True)
	prova("dopo, nessuna sorgente", sorgente_dei_tasti(None), None)
	passate = sum(risultati)
	print(f"Prove passate: {passate} di {len(risultati)}.")
	return 0 if passate == len(risultati) else 1


if __name__ == "__main__":
	sys.exit(main())
