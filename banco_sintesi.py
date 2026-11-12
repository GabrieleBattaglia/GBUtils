"""Banco di prova della voce di Windows di GBsintesi, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 per la issue 61.
Non fa parlare niente. Le prime prove sostituiscono COM e accessible_output2
con delle finte; l'ultima apre la voce di Windows vera, senza farla parlare,
in un processo a parte che tiene la cache gen_py di win32com in una cartella
temporanea, cosi' quella vera non si tocca.
La domanda e' se la voce di Windows si apra senza passare dalla cache dei
moduli generati: quando una generazione resta a meta', per un programma chiuso
mentre generava, a ogni apertura win32com lo diceva in console.
Si lancia con
  python banco_sintesi.py
e stampa in fondo quante prove sono passate.
"""
import json
import os
import subprocess
import sys
import tempfile

import GBsintesi
import win32com.client.dynamic

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

print("Banco della voce di Windows di GBsintesi. Nessuna voce parla.")

# 1. La voce di Windows non passa da accessible_output2.
caricati = []
importa_vero = GBsintesi.importlib.import_module
dispatch_vero = win32com.client.dynamic.Dispatch
detti = []

class VoceFinta:
	def Speak(self, testo, segni):
		detti.append((testo, segni))

def importa_finto(nome):
	caricati.append(nome)
	raise RuntimeError("accessible_output2 finto, che non si apre")

GBsintesi.importlib.import_module = importa_finto
win32com.client.dynamic.Dispatch = lambda nome: VoceFinta() if nome == "SAPI.SpVoice" else None
try:
	voce = GBsintesi._crea("sapi5")
	prova("la voce di Windows si apre con _VoceDiWindows", type(voce).__name__ == "_VoceDiWindows", type(voce).__name__)
	prova("senza chiedere niente ad accessible_output2", caricati == [], caricati)
	voce.speak("ciao")
	voce.speak("basta", interrupt=True)
	prova("parla in modo asincrono, e con interrupt svuota prima", detti == [("ciao", 1), ("basta", 3)], detti)
	prova("non ha il braille ed e' sempre attiva", voce.braille("x") is False and voce.is_active())
	prova("le altre uscite passano ancora da accessible_output2", GBsintesi._crea("nvda") is None and caricati == ["accessible_output2.outputs.nvda"],
		  caricati)
	win32com.client.dynamic.Dispatch = lambda nome: (_ for _ in ()).throw(OSError("niente SAPI"))
	prova("se SAPI non risponde, nessuna uscita invece di una caduta", GBsintesi._crea("sapi5") is None)
	uscita = object()
	GBsintesi.importlib.import_module = lambda nome: type("Modulo", (), {"Jaws": lambda: uscita})
	prova("uno screen reader che si apre torna com'e'", GBsintesi._crea("jaws") is uscita)
finally:
	GBsintesi.importlib.import_module = importa_vero
	win32com.client.dynamic.Dispatch = dispatch_vero

# 2. La voce vera, in un processo a parte, con la cache gen_py in una
#    cartella vuota: dopo l'apertura deve essere ancora vuota.
PROVA = '''import json, os, sys
cartella = sys.argv[1]
sys.path.insert(0, sys.argv[2])
import win32com
win32com.__gen_path__ = cartella
import win32com.gen_py
win32com.gen_py.__path__ = [cartella]
import GBsintesi
voce = GBsintesi._crea("sapi5")
contenuto = sorted(n for n in os.listdir(cartella) if n not in ("dicts.dat", "__init__.py"))
print(json.dumps({"tipo": type(voce).__name__, "contenuto": contenuto}))
'''
with tempfile.TemporaryDirectory() as cartella:
	cache = os.path.join(cartella, "gen_py")
	os.makedirs(cache)
	script = os.path.join(cartella, "apri_la_voce.py")
	with open(script, "w", encoding="utf-8") as f:
		f.write(PROVA)
	esito = subprocess.run([sys.executable, script, cache, QUI], capture_output=True, text=True, timeout=120,
						   stdin=subprocess.DEVNULL, check=False)
	try:
		visto = json.loads(esito.stdout.strip().splitlines()[-1])
	except (IndexError, ValueError):
		visto = {"tipo": None, "contenuto": None, "errore": esito.stderr[-400:]}
	prova("la voce vera si apre", visto["tipo"] == "_VoceDiWindows", visto)
	# __init__.py e dicts.dat li crea win32com da se', appena lo si importa:
	# non sono moduli generati. Il modulo della voce si chiamerebbe con il
	# codice della sua libreria dei tipi, C866CA3A-32F7-11D2-9602-00C04F8EE628.
	prova("e nella cache gen_py non nasce nessun modulo", visto["contenuto"] == [], visto)
	prova("e in console non scrive niente della cache", "Rebuilding cache" not in esito.stdout + esito.stderr, esito.stdout[-200:])

print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
