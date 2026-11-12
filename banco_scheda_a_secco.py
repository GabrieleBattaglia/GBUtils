"""Banco di prova della scheda a secco, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 per la issue 53.
Apre la scheda audio vera, quella che il mixer sceglie da se', ma le scrive
soltanto zeri: non si sente niente, e il volume generale non si tocca.
Le domande sono tre. Il mixer si accorge quando la scheda resta senza
campioni, anche su WASAPI, dove il segnale di write non scatta mai? Mentre la
pompa gira, il timer di Windows sta a un millesimo, e torna com'era quando si
ferma? E con un filo in Python puro che calcola senza mai fermarsi, quanto
silenzio finisce in mezzo al suono? Prima della correzione era quasi la
meta'.
Si lancia con
  python banco_scheda_a_secco.py
e dura una ventina di secondi. Stampa in fondo quante prove sono passate.
"""
import ctypes
import sys
import threading
import time

import numpy as np

import GBUtils

totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def risoluzione_attuale():
	"""Il periodo del timer di Windows in millesimi, o None se non si legge."""
	minimo, massimo, attuale = ctypes.c_ulong(), ctypes.c_ulong(), ctypes.c_ulong()
	try:
		ctypes.windll.ntdll.NtQueryTimerResolution(ctypes.byref(minimo), ctypes.byref(massimo), ctypes.byref(attuale))
	except (AttributeError, OSError):
		return None
	return attuale.value / 10000.0

# Il timer si chiede e si rende in coppia: lo si conta avvolgendo le due
# funzioni del pacchetto, che la pompa chiama per nome.
richieste = []
alza, abbassa = GBUtils._alza_timer, GBUtils._abbassa_timer
GBUtils._alza_timer = lambda: richieste.append("alza") or alza()
GBUtils._abbassa_timer = lambda periodo: richieste.append("abbassa") or abbassa(periodo)

class MixerCheSiFerma(GBUtils._MixerCondiviso):
	"""Il mixer vero, che una volta sola, quando glielo si chiede, si ferma
	per un tempo dato prima di preparare il blocco: e' la pompa tenuta lontana
	dalla scheda, come la teneva il filo di calcolo."""

	def __init__(self):
		super().__init__()
		self.sosta = 0.0

	def _prepara_blocco(self):
		if self.sosta:
			attesa, self.sosta = self.sosta, 0.0
			time.sleep(attesa)
		return super()._prepara_blocco()

def zeri(secondi, fs=44100):
	return np.zeros((int(secondi * fs), 2), dtype=np.float32)

def calcola(fine):
	conto = 0
	while time.monotonic() < fine:
		conto += 1

print("Banco della scheda a secco. Si scrivono soltanto zeri: nessun suono.")
if sys.platform != "win32":
	print("Il banco misura Windows: qui non c'e' niente da provare.")
	sys.exit(0)

mixer = MixerCheSiFerma()
voce = mixer.suona(zeri(30.0))
if voce is None:
	print(f"La scheda non si apre: {mixer.ultimo_errore}")
	sys.exit(1)
print(f"Interfaccia {mixer._nome_api}, dispositivo {mixer._device}, latenza {mixer._stream.latency * 1000:.1f} ms.")
time.sleep(1.0)

# 1. Il timer a un millesimo mentre la pompa gira.
periodo = risoluzione_attuale()
prova("mentre la pompa gira il timer di Windows sta a un millesimo o meno", periodo is not None and periodo <= 1.01, periodo)
prova("e la pompa l'ha chiesto una volta", richieste == ["alza"], richieste)

# 2. A riposo, niente silenzio inserito.
prima = mixer.silenzio_inserito
time.sleep(3.0)
a_riposo = mixer.silenzio_inserito - prima
prova("a riposo, in tre secondi, nessun silenzio inserito", a_riposo < 0.01, f"{a_riposo * 1000:.1f} ms")

# 3. La pompa ferma per tre decimi: la scheda va a secco, e il mixer se ne
#    accorge da solo, senza contare sul segnale di write.
buchi, prima = mixer.buchi, mixer.silenzio_inserito
mixer.sosta = 0.3
time.sleep(1.0)
mancato = mixer.silenzio_inserito - prima
prova("con la pompa ferma tre decimi il buco si conta", mixer.buchi > buchi, f"buchi da {buchi} a {mixer.buchi}")
prova("e il silenzio inserito vale quasi tutta la sosta", 0.15 <= mancato <= 0.35, f"{mancato * 1000:.0f} ms")
stato = GBUtils.Acusticator.stato()
prova("stato di Acusticator riporta il silenzio inserito", "silenzio_inserito" in stato)

# 4. Uno e poi quattro fili in Python puro che calcolano senza mai fermarsi,
#    sei secondi ciascuno. Prima della V8.6.5 il silenzio arrivava al 54 per
#    cento con quattro fili, e write non lo diceva.
prova("mentre la pompa gira il lucchetto passa ogni millesimo", sys.getswitchinterval() == GBUtils._SCAMBIO_MIXER,
	  sys.getswitchinterval())
for fili in (1, 4):
	prima = mixer.silenzio_inserito
	inizio = time.monotonic()
	lavori = [threading.Thread(target=calcola, args=(inizio + 6.0,), daemon=True) for _ in range(fili)]
	for lavoro in lavori:
		lavoro.start()
	for lavoro in lavori:
		lavoro.join()
	quota = (mixer.silenzio_inserito - prima) / (time.monotonic() - inizio)
	quanti = "un filo" if fili == 1 else f"{fili} fili"
	print(f"Con {quanti} di calcolo in Python puro: silenzio inserito {quota * 100:.1f} per cento.")
	prova(f"con {quanti} di calcolo il silenzio inserito resta sotto il due per cento", quota < 0.02, f"{quota * 100:.1f} per cento")

# 5. Chiuso il mixer, il timer e il lucchetto tornano come prima.
mixer.chiudi()
time.sleep(0.3)
prova("chiuso il mixer, il timer chiesto e' stato reso", richieste == ["alza", "abbassa"], richieste)
prova("e il lucchetto torna a passare ogni cinque millesimi", sys.getswitchinterval() == 0.005, sys.getswitchinterval())
prova("e la voce aperta e' stata svegliata", voce.fine.is_set())

print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
