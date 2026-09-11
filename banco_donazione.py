"""Banco di prova di Donazione, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode).
Nato con la V2.1.0 di Donazione, l'11 settembre 2026.
Usa il corridore di banco_menu.py, che cattura l'uscita: Donazione non
aspetta tasti, quindi nessuna sequenza viene iniettata. Verifica il
sorteggio forzato e spento, la stampa che si puo' spegnere, le dieci lingue,
la normalizzazione del codice di lingua, la lingua salvata da polipo trovata
accanto all'eseguibile nel pacchetto congelato simulato, il file rovinato che
non ferma niente, il generatore casuale globale che non si sposta e la
probabilita' predefinita.
Si lancia con
  python banco_donazione.py
e stampa in fondo quante prove sono passate.
"""
import json
import os
import random
import sys
import tempfile

from banco_menu import BancoUscita

from GBUtils import Donazione

EMAIL = "gabriele.battaglia@gmail.com"
# Una parola per lingua, per riconoscere il messaggio senza ricopiarlo.
PAROLE = {"it": "caffè", "en": "coffee", "pt": "café", "fr": "café", "es": "café", "de": "Kaffee", "ru": "кофе", "zh": "咖啡", "ja": "コーヒー", "ar": "قهوة"}

class BancoDonazione(BancoUscita):
	funzione = staticmethod(Donazione)

def messaggio_in(lingua):
	"""Il controllo sull'esito: un testo con la parola della lingua e l'indirizzo."""
	return lambda esito: isinstance(esito, str) and PAROLE[lingua] in esito and EMAIL in esito

def un_messaggio(esito):
	"""Un messaggio qualsiasi, in qualunque lingua."""
	return isinstance(esito, str) and EMAIL in esito

def verifica(b, titolo, condizione):
	"""Una prova fatta fuori dal corridore, con lo stesso conteggio."""
	b.totale += 1
	if condizione:
		b.passate += 1
	print(f"{titolo}: {'ok' if condizione else 'fallita'}")

def main():
	b = BancoDonazione()
	b.prova("sorteggio forzato, italiano, stampato", [], messaggio_in("it"), contiene=["offrirmi un caffè", EMAIL], lang="it", probabilita=100)
	b.prova("sorteggio spento: None e silenzio", [], None, non_contiene=["\n"], lang="it", probabilita=0)
	b.prova("senza stampa: il testo torna e basta", [], messaggio_in("en"), non_contiene=["coffee"], lang="en", probabilita=100, stampa=False)
	for lingua in PAROLE:
		b.prova(f"lingua {lingua}", [], messaggio_in(lingua), lang=lingua, probabilita=100, stampa=False)
	b.prova("codice con paese, it_IT", [], messaggio_in("it"), lang="it_IT", probabilita=100, stampa=False)
	b.prova("codice con trattino e maiuscole, EN-us", [], messaggio_in("en"), lang="EN-us", probabilita=100, stampa=False)
	b.prova("lingua sconosciuta: inglese", [], messaggio_in("en"), lang="xx", probabilita=100, stampa=False)
	with tempfile.TemporaryDirectory() as cartella:
		# Pacchetto congelato simulato: la cartella di chi chiama e' quella
		# dell'eseguibile, e li' polipo ha salvato la lingua scelta.
		percorso = os.path.join(cartella, "selected_language.json")
		eseguibile_vero = sys.executable
		sys.frozen = True
		sys.executable = os.path.join(cartella, "programma.exe")
		try:
			with open(percorso, "w", encoding="utf-8") as f:
				json.dump({"language_code": "fr"}, f)
			b.prova("senza lang: la lingua salvata da polipo, francese", [], messaggio_in("fr"), probabilita=100, stampa=False)
			with open(percorso, "w", encoding="utf-8") as f:
				f.write("{ questo non e' json")
			b.prova("file rovinato: si passa oltre senza errori", [], un_messaggio, probabilita=100, stampa=False)
			with open(percorso, "w", encoding="utf-8") as f:
				json.dump([1, 2, 3], f)
			b.prova("file con la forma sbagliata: si passa oltre", [], un_messaggio, probabilita=100, stampa=False)
		finally:
			del sys.frozen
			sys.executable = eseguibile_vero
	random.seed(7)
	primo = random.random()
	random.seed(7)
	Donazione(lang="it", probabilita=100, stampa=False)
	verifica(b, "il generatore casuale globale non si sposta", random.random() == primo)
	comparse = sum(1 for _ in range(200) if Donazione(lang="it", stampa=False))
	verifica(b, f"probabilita' predefinita: comparso {comparse} volte su 200, atteso intorno a 40", 15 <= comparse <= 90)
	print(f"Prove {b.totale}, passate {b.passate}.")
	return 0 if b.passate == b.totale else 1

if __name__ == "__main__":
	sys.exit(main())
