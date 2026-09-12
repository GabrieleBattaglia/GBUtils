"""Collaudo a mano di key, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, modalita' auto).
Nato con la revisione 1 di key, l'8 settembre 2026.
Stampa cio' che key restituisce per ogni tasto premuto, una riga per
tasto, cosi' che la tabella si possa verificare con la tastiera vera, che
e' l'unico modo di sapere se corrisponde a quella che si ha sotto le dita.
Si lancia con
  python collaudo_key.py
e si esce premendo Escape tre volte di seguito.
"""
import sys

from GBUtils import key

NOMI_SERVIZIO = {"\r": "Invio", "\x1b": "Escape", "\x08": "Backspace", "\t": "Tab", " ": "Spazio"}

def descrivi(tasto):
	"""Riga corta e leggibile per cio' che key ha restituito."""
	if tasto in NOMI_SERVIZIO:
		return f"tasto di servizio: {NOMI_SERVIZIO[tasto]}"
	if len(tasto) == 1:
		return f"carattere: {tasto}"
	return f"nome: {tasto}"

def main():
	print("Collaudo di key. Premi i tasti da verificare:")
	print("frecce dedicate e sul tastierino a blocco")
	print("numerico spento, il 5 del tastierino, Home,")
	print("Fine, le pagine, Ins e Canc, da soli e con")
	print("Ctrl e Alt; F1 fino a F12 nudi e con Maiusc,")
	print("Ctrl e Alt; Ctrl+Tab, Backspace e")
	print("Ctrl+Backspace; Alt con lettere e cifre;")
	print("infine Ctrl+C, che deve fermare il programma.")
	print("Escape tre volte di seguito per uscire.")
	escape_di_fila = 0
	while True:
		try:
			tasto = key()
		except KeyboardInterrupt:
			# key solleva l'interruzione come qualunque programma da console.
			# Qui la si raccoglie per uscire dicendolo, invece di lasciare la
			# traccia dell'errore, che a Gabriele non diceva niente.
			print("Ctrl+C: collaudo interrotto.")
			return 0
		print(descrivi(tasto))
		escape_di_fila = escape_di_fila + 1 if tasto == "\x1b" else 0
		if escape_di_fila == 3:
			print("Collaudo terminato.")
			return 0

if __name__ == "__main__":
	sys.exit(main())
