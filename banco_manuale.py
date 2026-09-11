"""Banco di prova di manuale su Windows, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode).
Nato con la V2.1.0 di manuale, l'11 settembre 2026.
Inietta i tasti nel buffer della console con la tecnica di banco_key.py e usa
il corridore di banco_menu.py: chiama manuale con l'uscita catturata e
confronta cio' che restituisce e cio' che stampa con cio' che ci si aspetta,
una riga per prova. Verifica il prompt di fine pagina fra due ritorni
carrello, Esc che interrompe, il nome del chiamante, la ricerca del file nel
pacchetto congelato, simulato con sys.frozen e sys._MEIPASS, l'indifferenza
alla directory di lavoro e la codifica.
Si lancia con
  python banco_manuale.py
e stampa in fondo quante prove sono passate.
"""
import os
import sys
import tempfile

from banco_menu import ESC, INVIO, SU, BancoUscita

from GBUtils import manuale

TESTO = "\n".join(f"riga {i}" for i in range(1, 26))
CORTO = "\n".join(f"riga {i}" for i in range(1, 6))

class BancoManuale(BancoUscita):
	funzione = staticmethod(manuale)
	# Pezzi della domanda italiana che manuale faceva fino alla V2.0.0.
	parole_vietate = ("pagina", "Invio o")

def prove_sui_file(b, cartella):
	"""Le prove che leggono da un file: percorso assoluto, pacchetto congelato
	simulato, directory di lavoro ignorata, codifica."""
	guida = os.path.join(cartella, "guida_prova.txt")
	with open(guida, "w", encoding="utf-8") as f:
		f.write("prima riga della guida\nseconda riga\n")
	b.prova("percorso assoluto", [], True, contiene=["prima riga della guida\nseconda riga\n"], nf=guida, nome="Guida")
	# Pacchetto congelato simulato: le risorse stanno in sys._MEIPASS e
	# l'eseguibile sta altrove, dove la guida non c'e'.
	altrove = os.path.join(cartella, "altrove")
	os.mkdir(altrove)
	eseguibile_vero = sys.executable
	sys.frozen = True
	sys._MEIPASS = cartella
	sys.executable = os.path.join(altrove, "programma.exe")
	try:
		b.prova("congelato: il file relativo si trova in sys._MEIPASS", [], True, contiene=["prima riga della guida\n"], nf="guida_prova.txt", nome="Guida")
		b.prova("congelato: da nessuna parte, FileNotFoundError", [], "FileNotFoundError", nf="non_esiste.txt", nome="Guida")
		del sys._MEIPASS
		sys.executable = os.path.join(cartella, "programma.exe")
		b.prova("congelato senza _MEIPASS: accanto all'eseguibile", [], True, contiene=["prima riga della guida\n"], nf="guida_prova.txt", nome="Guida")
	finally:
		del sys.frozen
		if hasattr(sys, "_MEIPASS"):
			del sys._MEIPASS
		sys.executable = eseguibile_vero
	# Da sorgente il file relativo si cerca accanto a chi chiama, cioe' in
	# questa cartella, e non nella directory di lavoro, anche se li' ce n'e'
	# uno con lo stesso nome.
	lavoro = os.getcwd()
	os.chdir(cartella)
	try:
		b.prova("la directory di lavoro non conta", [], "FileNotFoundError", nf="guida_prova.txt", nome="Guida")
	finally:
		os.chdir(lavoro)
	accenti = os.path.join(cartella, "accenti.txt")
	with open(accenti, "w", encoding="cp1252") as f:
		f.write("caffè e perché\n")
	b.prova("codifica esplicita cp1252", [], True, contiene=["caffè e perché\n"], nf=accenti, nome="Guida", codifica="cp1252")
	with open(accenti, "w", encoding="utf-8") as f:
		f.write("caffè e perché\n")
	b.prova("utf-8 per predefinito", [], True, contiene=["caffè e perché\n"], nf=accenti, nome="Guida")

def main():
	b = BancoManuale()
	b.prova("tre pagine, invio e invio: fino in fondo", [INVIO, INVIO], True, contiene=["riga 10\n\rGuida (1 / 3)\r\nriga 11", "riga 20\n\rGuida (2 / 3)\r\nriga 21", "riga 25\n"], non_contiene=["(3 / 3)"], testo=TESTO, nome="Guida", righe_pagina=10)
	b.prova("esc alla prima pagina interrompe", [ESC], False, contiene=["\rGuida (1 / 3)\r\n"], non_contiene=["riga 11"], testo=TESTO, nome="Guida", righe_pagina=10)
	b.prova("un tasto qualsiasi continua", ["q", SU], True, contiene=["riga 25\n"], non_contiene=["q\n", "up"], testo=TESTO, nome="Guida", righe_pagina=10)
	b.prova("senza nome: solo il conteggio", [INVIO, INVIO], True, contiene=["riga 10\n\r(1 / 3)\r\n"], non_contiene=["Guida", " (1"], testo=TESTO, righe_pagina=10)
	b.prova("una pagina sola: nessun prompt", [], True, contiene=["riga 5\n"], non_contiene=["\r"], testo=CORTO, nome="Guida", righe_pagina=10)
	b.prova("testo vuoto: vero e silenzio", [], True, non_contiene=["\n"], testo="", nome="Guida")
	b.prova("ne' file ne' testo: ValueError", [], "ValueError", nome="Guida")
	b.prova("file e testo insieme: ValueError", [], "ValueError", nf="x.txt", testo="a", nome="Guida")
	with tempfile.TemporaryDirectory() as cartella:
		prove_sui_file(b, cartella)
	print(f"Prove {b.totale}, passate {b.passate}.")
	return 0 if b.passate == b.totale else 1

if __name__ == "__main__":
	sys.exit(main())
