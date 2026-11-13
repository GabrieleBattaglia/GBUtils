"""Banco di prova del conto dei buchi del mixer, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 13 novembre 2026, dalla revisione dei commit della issue 53, con
Acusticator 8.9.7. La simulazione viene dallo scettico della revisione.
Non apre la scheda audio e non suona niente: al posto della scheda c'e' una
finta con la sua coda, che consuma i campioni al ritmo del suo quarzo, e al
posto dell'orologio del processore il tempo della finta. Cosi' si sa quanto
silenzio la scheda ha suonato davvero, e lo si confronta con quello che il
mixer conta in silenzio_inserito.
Le domande sono tre. Un buco breve, da 12 a 40 millesimi, si vede, e con il
silenzio giusto? Una sessione lunga senza buchi, con il quarzo della scheda
un po' piu' lento o piu' veloce, resta senza buchi? E un ciclo fermato nel
punto in cui ricomincia si spegne sfumando?
Si lancia con
  python banco_conta_buchi.py
e stampa in fondo quante prove sono passate.
"""
import sys
import time

import numpy as np

import GBUtils

FS = 44100
BLOCCO = 1024
GBUtils._alza_timer = lambda: None
GBUtils._abbassa_timer = lambda periodo: None
totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

class MixerDiCarta(GBUtils._MixerCondiviso):
	def __init__(self):
		super().__init__()
		self._canali = 2
		self._fs = FS

	def _assicura_stream(self):
		return True

class SchedaFinta:
	"""Una coda di capienza campioni, che si svuota a FS per (1 + ppm)
	campioni al secondo; quando e' vuota la scheda suona silenzio. soste sono
	coppie (quando, quanto): la pompa resta ferma quanto, in secondi."""

	def __init__(self, mixer, capienza, soste, limite, ppm=0.0):
		self.mixer, self.t, self.dentro = mixer, 0.0, 0.0
		self.capienza, self.soste, self.limite = capienza, list(soste), limite
		self.ritmo = FS * (1.0 + ppm * 1e-6)
		self.secco_vero = 0.0
		self.latency = capienza / FS

	def _avanza(self, secondi):
		self.t += secondi
		self.dentro -= secondi * self.ritmo
		if self.dentro < 0:
			self.secco_vero += -self.dentro / self.ritmo
			self.dentro = 0.0

	def write(self, blocco):
		if self.soste and self.t >= self.soste[0][0]:
			self._avanza(self.soste.pop(0)[1])
		n = len(blocco)
		if self.dentro + n > self.capienza:
			self._avanza((self.dentro + n - self.capienza) / self.ritmo)
		self.dentro += n
		self._avanza(0.00005)
		if self.t > self.limite:
			self.mixer._ferma.set()
		return False

	def abort(self):
		pass

	def close(self):
		pass

def gira(soste, limite=60.0, ppm=0.0, capienza=3 * BLOCCO):
	mixer = MixerDiCarta()
	mixer._silenzio = 0.0
	mixer.suona(np.full((3000, 2), 0.01, dtype=np.float32), fs=FS, ciclo=True)
	scheda = SchedaFinta(mixer, capienza, soste, limite, ppm)
	mixer._stream = scheda
	vero = time.perf_counter
	time.perf_counter = lambda s=scheda: s.t
	mixer._orologio = lambda s=scheda: s.t
	try:
		mixer._pompa_audio()
	finally:
		time.perf_counter = vero
	return scheda.secco_vero, mixer.buchi, mixer.silenzio_inserito

print("Banco del conto dei buchi del mixer. Nessun suono, nessuna scheda audio.")
CODA = 3 * BLOCCO / FS

# 1. Un buco solo, da 12 a 100 millesimi di silenzio vero. Fino alla V8.9.4
#    quelli sotto i 35 millesimi non si contavano.
for silenzio in (0.012, 0.020, 0.030, 0.040, 0.100):
	vero, buchi, contato = gira([(5.0, CODA + silenzio)], limite=10.0)
	prova(f"una sosta che lascia {silenzio * 1000:.0f} ms di silenzio da' un buco, con il silenzio giusto",
		  buchi == 1 and abs(contato - vero) < 0.003, f"vero {vero * 1000:.1f} ms, buchi {buchi}, contato {contato * 1000:.1f} ms")

# 1 bis. Lo stesso con code piu' corte e piu' lunghe: da 2 blocchi, come su
#        WASAPI, a 6, come sulle schede lente in MME.
for blocchi in (2, 6):
	coda = blocchi * BLOCCO / FS
	vero, buchi, contato = gira([(5.0, coda + 0.020)], limite=10.0, capienza=blocchi * BLOCCO)
	prova(f"con una coda di {blocchi} blocchi un buco da 20 ms si conta giusto", buchi == 1 and abs(contato - vero) < 0.003,
		  f"vero {vero * 1000:.1f} ms, buchi {buchi}, contato {contato * 1000:.1f} ms")

# 1 ter. Una sosta che la coda della scheda copre non e' un buco: e' il
#        sobbalzo di una scrittura tornata tardi, frequente su WASAPI. La
#        prima stesura di questo conto li contava, e sulla scheda vera dava
#        dodici buchi a riposo.
for sosta in (0.015, 0.030, CODA - 0.005):
	vero, buchi, contato = gira([(5.0 + i, sosta) for i in range(10)], limite=20.0)
	prova(f"dieci soste da {sosta * 1000:.0f} ms, coperte dalla coda, non danno buchi", vero == 0 and buchi == 0 and contato == 0,
		  f"vero {vero * 1000:.1f} ms, buchi {buchi}, contato {contato * 1000:.1f} ms")

# 2. Venti buchi da 15 millesimi, come quelli della contesa del lucchetto.
vero, buchi, contato = gira([(5.0 + i, CODA + 0.015) for i in range(20)], limite=30.0)
prova("venti soste da 15 ms danno venti buchi e il silenzio vero", buchi == 20 and abs(contato - vero) < 0.01,
	  f"vero {vero * 1000:.0f} ms, buchi {buchi}, contato {contato * 1000:.0f} ms")

# 3. Senza buchi, nemmeno con un quarzo che va un po' piu' piano o piu' in
#    fretta, per mezz'ora. Fino alla V8.9.4 a -50 parti per milione si
#    contavano buchi mai avvenuti.
for ppm in (0.0, -100.0, 100.0):
	vero, buchi, contato = gira([], limite=1800.0, ppm=ppm)
	prova(f"mezz'ora senza buchi, con il quarzo a {ppm:+.0f} ppm, non conta niente", vero == 0 and buchi == 0, (vero, buchi, contato))

# 4. E con la deriva il buco vero si vede ancora, dopo venticinque minuti.
for ppm in (-100.0, 100.0):
	vero, buchi, contato = gira([(1500.0, CODA + 0.030)], limite=1600.0, ppm=ppm)
	prova(f"a {ppm:+.0f} ppm un buco da 30 ms dopo venticinque minuti si conta, con il silenzio giusto",
		  buchi == 1 and abs(contato - vero) < 0.004, f"vero {vero * 1000:.1f} ms, buchi {buchi}, contato {contato * 1000:.1f} ms")

# 5. Un ciclo fermato nel punto in cui ricomincia, con un buffer di 2048
#    campioni: fino alla V8.9.4 si troncava, perche' la posizione era zero.
mixer = MixerDiCarta()
giro = np.full((2048, 2), 0.4, dtype=np.float32)
voce = mixer.suona(giro, fs=FS, ciclo=True)
mixer._prepara_blocco()
mixer._prepara_blocco()
prova("dopo due blocchi la posizione del ciclo e' tornata a zero", voce.pos == 0, voce.pos)
GBUtils._CicloAcceso(mixer, voce).stop()
dopo = mixer._prepara_blocco()[:, 0]
prova("fermato li', il ciclo si spegne sfumando invece di troncarsi", dopo[0] > 0.38 and abs(dopo[219]) < 1e-6, dopo[:3])
mai = mixer.suona(giro, fs=FS, ciclo=True)
GBUtils._CicloAcceso(mixer, mai).stop()
dopo = mixer._prepara_blocco()
prova("un ciclo fermato prima di suonare non manda niente", dopo is None or float(np.max(np.abs(dopo))) == 0.0)

print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
