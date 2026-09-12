"""Banco di prova di lingua_di_sistema, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato con la V139 e la issue 32, il 12 settembre 2026.
La funzione guarda l'ambiente e il sistema, cioe' cose che il banco non puo'
cambiare davvero senza toccare la macchina: le variabili d'ambiente si
sostituiscono in un processo figlio, che le riceve e poi muore, e la risposta
di Windows si sostituisce con una finta, rimettendo a posto l'originale.
Nessuna prova cambia qualcosa fuori dal processo che la esegue.
Si lancia con
  python banco_lingua.py
e stampa in fondo quante prove sono passate.
"""
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
# Le quattro variabili che la funzione guarda, in ordine di precedenza.
VARIABILI = ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")
CODICE = (
	"import sys; sys.path.insert(0, r'" + QUI + "'); "
	"from GBUtils import lingua_di_sistema; print(repr(lingua_di_sistema()))"
)

def con_ambiente(**variabili):
	"""Chiama la funzione in un processo figlio con l'ambiente che si vuole:
	le variabili passate a None spariscono, le altre valgono quel che si dice."""
	ambiente = dict(os.environ)
	for var in VARIABILI:
		ambiente.pop(var, None)
	for nome, valore in variabili.items():
		if valore is None:
			ambiente.pop(nome, None)
		else:
			ambiente[nome] = valore
	esito = subprocess.run([sys.executable, "-B", "-c", CODICE], capture_output=True, text=True, env=ambiente, check=True)
	# Il figlio stampa il repr del risultato, cioe' None o una stringa corta:
	# si rilegge con ast, che valuta i soli valori costanti e non esegue nulla.
	import ast
	return ast.literal_eval(esito.stdout.strip())

class Banco:
	def __init__(self):
		self.totale = self.passate = 0

	def prova(self, titolo, visto, atteso):
		self.totale += 1
		if visto == atteso:
			self.passate += 1
			print(f"{titolo}: ok")
		else:
			print(f"{titolo}: {visto!r} invece di {atteso!r}")

def prove_ambiente(b):
	b.prova("LANG semplice", con_ambiente(LANG="it"), "it")
	b.prova("LANG con paese e codifica", con_ambiente(LANG="it_IT.UTF-8"), "it")
	b.prova("LANG con il trattino", con_ambiente(LANG="pt-BR"), "pt")
	b.prova("LANG maiuscolo", con_ambiente(LANG="FR_FR"), "fr")
	b.prova("codice di tre lettere", con_ambiente(LANG="ast_ES"), "ast")
	b.prova("LANGUAGE vince su LANG", con_ambiente(LANGUAGE="es", LANG="de"), "es")
	b.prova("LC_ALL vince su LC_MESSAGES e LANG", con_ambiente(LC_ALL="en", LC_MESSAGES="de", LANG="fr"), "en")
	b.prova("LC_MESSAGES vince su LANG", con_ambiente(LC_MESSAGES="ru", LANG="fr"), "ru")
	b.prova("LANGUAGE con piu' lingue, conta la prima", con_ambiente(LANGUAGE="pt:en:it"), "pt")
	b.prova("una variabile vuota non conta", con_ambiente(LANGUAGE="", LANG="ja"), "ja")
	# Italian_Italy e' cio' che locale.getlocale risponde su Windows, e non e'
	# un codice di lingua: tagliato al trattino basso darebbe italian, con cui
	# nessuna traduzione verrebbe trovata. Va scartato, e allora risponde il
	# passaggio successivo, che su Windows e' l'API di sistema.
	b.prova("Italian_Italy non diventa italian", con_ambiente(LANG="Italian_Italy") != "italian", True)
	b.prova("una cifra non e' una lingua", con_ambiente(LANG="12", LANGUAGE="de"), "de")
	b.prova("C non e' una lingua, e' una sola lettera", con_ambiente(LANG="C", LANGUAGE="nl"), "nl")

def prove_windows(b):
	"""Senza variabili d'ambiente, su Windows risponde l'API di sistema: qui si
	sostituisce con una finta, per sapere che il codice numerico viene tradotto
	nel nome della lingua e poi ripulito."""
	if sys.platform != "win32":
		print("prove dell'API di Windows saltate: non siamo su Windows")
		return
	import ctypes

	from GBUtils import lingua_di_sistema
	originale = ctypes.windll.kernel32.GetUserDefaultUILanguage
	vecchie = {v: os.environ.pop(v, None) for v in VARIABILI}
	try:
		for numero, atteso, nome in ((1040, "it", "italiano"), (1033, "en", "inglese"), (1046, "pt", "portoghese brasiliano"), (0, None, "codice che non esiste")):
			ctypes.windll.kernel32.GetUserDefaultUILanguage = lambda n=numero: n
			visto = lingua_di_sistema()
			# Senza variabili e con un codice ignoto resta l'ultimo passaggio,
			# cioe' il locale del processo: qui basta che non inventi niente.
			if atteso is None:
				b.prova(f"API di Windows, {nome}", visto in (None, "it", "en"), True)
			else:
				b.prova(f"API di Windows, {nome}", visto, atteso)
	finally:
		ctypes.windll.kernel32.GetUserDefaultUILanguage = originale
		for var, valore in vecchie.items():
			if valore is not None:
				os.environ[var] = valore

def main():
	b = Banco()
	prove_ambiente(b)
	prove_windows(b)
	from GBUtils import _lingua_di_sistema, lingua_di_sistema
	b.prova("il nome storico e quello pubblico sono la stessa funzione", _lingua_di_sistema is lingua_di_sistema, True)
	risposta = lingua_di_sistema()
	b.prova("su questa macchina risponde un codice o None", risposta is None or (risposta.isalpha() and 2 <= len(risposta) <= 3), True)
	print(f"su questa macchina la lingua e': {risposta!r}")
	print(f"Prove {b.totale}, passate {b.passate}.")
	return 0 if b.passate == b.totale else 1

if __name__ == "__main__":
	sys.exit(main())
