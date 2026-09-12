"""Banco di prova dei percorsi di GBUtils, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato con la V138 e la issue 20, il 12 settembre 2026.
cartella_applicazione e percorso_risorsa rispondono guardando chi le ha
chiamate, risalendo la pila: il punto in cui si sbaglia e' proprio di quanti
livelli salire, e un errore non si vede finche' i moduli stanno tutti nella
stessa cartella. Il banco costruisce percio' un finto progetto in una
cartella temporanea, con un modulo in una sottocartella, e verifica che ogni
chiamata risponda la cartella giusta, da sorgente e da eseguibile simulato.
Si lancia con
  python banco_percorsi.py
e stampa in fondo quante prove sono passate.
"""
import os
import shutil
import subprocess
import sys
import tempfile

# Il finto progetto: il programma principale in cima, e un modulo dei percorsi
# in una sottocartella, come Tornello con src/config.py. Il modulo avvolge le
# funzioni con risalita 1, cosi' risponde per il programma intero invece che
# per se stesso.
PROGRAMMA = '''\
import os, sys
sys.path.insert(0, {gbutils!r})
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from GBUtils import cartella_applicazione, percorso_risorsa
import moduli.percorsi as percorsi

print("diretta:", cartella_applicazione())
print("risorsa diretta:", percorso_risorsa("guida.txt"))
print("da modulo:", percorsi.cartella_dati())
print("risorsa da modulo:", percorsi.risorsa("guida.txt"))
print("dentro il modulo:", percorsi.cartella_del_modulo())
'''
MODULO = '''\
from GBUtils import cartella_applicazione, percorso_risorsa

def cartella_dati():
	"""Risponde per il programma che ha chiamato: risalita 1."""
	return cartella_applicazione(1)

def risorsa(nome):
	return percorso_risorsa(nome, 1)

def cartella_del_modulo():
	"""Risponde per se stesso: risalita 0."""
	return cartella_applicazione()
'''

def prepara(radice, gbutils):
	os.makedirs(os.path.join(radice, "moduli"), exist_ok=True)
	with open(os.path.join(radice, "programma.py"), "w", encoding="utf-8") as f:
		f.write(PROGRAMMA.format(gbutils=gbutils))
	with open(os.path.join(radice, "moduli", "__init__.py"), "w", encoding="utf-8") as f:
		f.write("")
	with open(os.path.join(radice, "moduli", "percorsi.py"), "w", encoding="utf-8") as f:
		f.write(MODULO)
	with open(os.path.join(radice, "guida.txt"), "w", encoding="utf-8") as f:
		f.write("guida\n")

def esegui(radice, da_dove):
	"""Lancia il finto programma da una directory di lavoro qualsiasi e
	raccoglie le risposte in un dizionario."""
	esito = subprocess.run([sys.executable, "-B", os.path.join(radice, "programma.py")],
		capture_output=True, text=True, cwd=da_dove, check=True)
	risposte = {}
	for riga in esito.stdout.splitlines():
		chiave, _, valore = riga.partition(": ")
		risposte[chiave] = valore
	return risposte

def main():
	gbutils = os.path.dirname(os.path.abspath(__file__))
	totale = passate = 0
	def verifica(titolo, condizione, visto=""):
		nonlocal totale, passate
		totale += 1
		if condizione:
			passate += 1
			print(f"{titolo}: ok")
		else:
			print(f"{titolo}: fallita {visto}")
	with tempfile.TemporaryDirectory() as radice:
		radice = os.path.realpath(radice)
		prepara(radice, gbutils)
		moduli = os.path.join(radice, "moduli")
		altrove = os.path.join(radice, "altrove")
		os.makedirs(altrove, exist_ok=True)
		# Lanciato dalla sua cartella e da una qualsiasi: le risposte non
		# devono cambiare, perche' la directory di lavoro non conta.
		for da_dove, come in ((radice, "dalla sua cartella"), (altrove, "da un'altra cartella")):
			r = esegui(radice, da_dove)
			verifica(f"chiamata diretta, {come}", r["diretta"] == radice, r["diretta"])
			verifica(f"dal modulo con risalita 1, {come}", r["da modulo"] == radice, r["da modulo"])
			verifica(f"il modulo per se stesso, {come}", r["dentro il modulo"] == moduli, r["dentro il modulo"])
			verifica(f"risorsa che esiste, {come}", r["risorsa diretta"] == os.path.join(radice, "guida.txt"), r["risorsa diretta"])
			verifica(f"risorsa dal modulo, {come}", r["risorsa da modulo"] == os.path.join(radice, "guida.txt"), r["risorsa da modulo"])
		# Eseguibile simulato: frozen vero, _MEIPASS con dentro la guida, e
		# l'eseguibile in un'altra cartella ancora. Tutto deve puntare li'.
		finto_exe = os.path.join(altrove, "programma.exe")
		meipass = os.path.join(radice, "meipass")
		os.makedirs(meipass, exist_ok=True)
		shutil.copy(os.path.join(radice, "guida.txt"), meipass)
		sys.path.insert(0, gbutils)
		from GBUtils import cartella_applicazione, percorso_risorsa
		vero_exe = sys.executable
		sys.frozen = True
		sys.executable = finto_exe
		sys._MEIPASS = meipass
		try:
			verifica("compilato: la cartella e' quella dell'eseguibile", cartella_applicazione() == altrove, cartella_applicazione())
			verifica("compilato: la risorsa si trova in _MEIPASS", percorso_risorsa("guida.txt") == os.path.join(meipass, "guida.txt"), percorso_risorsa("guida.txt"))
			verifica("compilato: la risorsa che non c'e' punta accanto all'eseguibile", percorso_risorsa("assente.txt") == os.path.join(altrove, "assente.txt"), percorso_risorsa("assente.txt"))
			assoluto = os.path.join(radice, "guida.txt")
			verifica("il percorso assoluto torna com'e'", percorso_risorsa(assoluto) == assoluto, percorso_risorsa(assoluto))
		finally:
			del sys.frozen, sys._MEIPASS
			sys.executable = vero_exe
	print(f"Prove {totale}, passate {passate}.")
	return 0 if passate == totale else 1

if __name__ == "__main__":
	sys.exit(main())
