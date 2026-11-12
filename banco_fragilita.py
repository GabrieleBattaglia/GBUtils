"""Banco di prova delle fragilita' di Acusticator, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 per la issue 54.
Non suona niente e non apre la scheda audio: la sintesi si misura sul buffer,
il mixer gira su carta, cioe' scrive in una lista invece che nelle casse, e
play consegna il suono a una finta invece che al mixer.
Le domande sono sei, una per punto della issue. Le costanti che nessuno
leggeva sono sparite? Un volume dato come coppia avvisa invece di cadere? Il
rumore con una durata scomoda costa quanto quello con una durata tonda? Una
voce fermata si spegne in pochi millesimi invece di troncarsi? Un kind e un
adsr fuori dalla grammatica avvisano invece di far cadere play?
Si lancia con
  python banco_fragilita.py
e stampa in fondo quante prove sono passate.
"""
import contextlib
import io
import json
import math
import os
import sys
import tempfile
import time

import numpy as np

import GBUtils
from GBUtils import Acusticator

FS = 44100
totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def con_avviso(funzione, *argomenti, **chiavi):
	"""Chiama funzione e restituisce il risultato, l'eccezione se c'e' stata,
	e cio' che ha scritto su stderr."""
	errori = io.StringIO()
	risultato = eccezione = None
	with contextlib.redirect_stderr(errori):
		try:
			risultato = funzione(*argomenti, **chiavi)
		except Exception as e:  # noqa: BLE001 - il banco vuole vedere qualunque caduta
			eccezione = e
	return risultato, eccezione, errori.getvalue()

class MixerDiCarta(GBUtils._MixerCondiviso):
	"""Il mixer vero, che invece di scrivere nelle casse restituisce i blocchi."""

	def __init__(self):
		super().__init__()
		self._canali = 2
		self._fs = FS

	def _assicura_stream(self):
		return True

	def blocco(self):
		uscito = self._prepara_blocco()
		return np.zeros((self._blocco, 2), dtype=np.float32) if uscito is None else uscito.copy()

print("Banco delle fragilita' di Acusticator. Nessun suono, nessuna scheda audio.")

# 1. Le costanti della classe che il mixer non leggeva.
for nome in ("BLOCCO", "VOCI_MAX", "SILENZIO_MAX", "MARGINE_ATTESA"):
	prova(f"Acusticator non ha piu' {nome}", not hasattr(Acusticator, nome))
prova("il blocco vero sta nel mixer, 1024 campioni", GBUtils._MixerCondiviso.BLOCCO == 1024)
prova("la base del volume resta 0.5", Acusticator.BASE_VOL == 0.5)

# 2. Il volume come coppia, in preset e in play. Una collezione di prova
#    accanto, in una cartella temporanea: la collezione vera non si tocca.
consegnati = []
Acusticator.riproduci = lambda buffer, fs=None, sync=False: consegnati.append(buffer) or True
with tempfile.TemporaryDirectory() as cartella:
	percorso = os.path.join(cartella, "prova.json")
	with open(percorso, "w", encoding="utf-8") as f:
		json.dump({"banco_fragile": {"descrizione": "prova", "score": [["a4", 0.05, 0, 0.1], ["c5", 0.05, 0, -0.1]],
									 "kind": 1, "adsr": [1, 0, 100, 1]}}, f)
	Acusticator.collezione(percorso)
	for volume in ((1.0, 0.2), [0.3, 0.6], "forte", True, float("nan")):
		score = None
		risultato, errore, avviso = con_avviso(Acusticator.preset, "banco_fragile", volume=volume)
		if risultato:
			score, kind, adsr = risultato
		prova(f"preset con volume {volume!r} non cade e avvisa", errore is None and "non valido" in avviso and score is not None,
			  f"{errore!r} {avviso!r}")
		prova("e suona alla base 0.5", score is not None and abs(score[3] - 0.6) < 1e-9 and abs(score[7] - 0.4) < 1e-9, score)
	risultato, errore, avviso = con_avviso(Acusticator.play, "banco_fragile", volume=(1.0, 0.2))
	prova("play con il volume come coppia suona lo stesso", errore is None and risultato is True and len(consegnati) == 1,
		  f"{errore!r} {risultato!r}")
	score, _, _ = Acusticator.preset("banco_fragile", volume=0.8)
	prova("un volume numero sostituisce la base come prima", abs(score[3] - 0.9) < 1e-9 and abs(score[7] - 0.7) < 1e-9, score)
	score, _, _ = Acusticator.preset("banco_fragile", volume="0.8")
	prova("un volume scritto come numero vale come il numero", abs(score[3] - 0.9) < 1e-9, score)
	Acusticator._locali.remove(os.path.normpath(percorso))
	Acusticator.reload()

# 3. Il rumore con una lunghezza scomoda. 44101 e' primo: prima della V8.6.4
#    la trasformata era lunga quanto il suono, e costava molto di piu'.
def costo(campioni, prove=5):
	migliore = math.inf
	for _ in range(prove):
		inizio = time.perf_counter()
		GBUtils._genera_rumore(6, (None, None, None, None), campioni, FS)
		migliore = min(migliore, time.perf_counter() - inizio)
	return migliore

primo, tondo = 44101, 44100
rapporto = costo(primo) / costo(tondo)
prova("un rumore di 44101 campioni costa quanto uno di 44100", rapporto < 2.0, f"rapporto {rapporto:.1f}")
for kind in (5, 6, 7, 8):
	for banda in ((None, None, None, None), (200.0, 200.0, 2000.0, 2000.0), (200.0, 600.0, 2000.0, 1200.0)):
		onda = GBUtils._genera_rumore(kind, banda, primo, FS)
		prova(f"rumore {kind}, banda {banda[0]}-{banda[2]}, lungo esattamente {primo}", len(onda) == primo and bool(np.all(np.isfinite(onda))),
			  len(onda))
livelli = [GBUtils._livello_ponderato(GBUtils._genera_rumore(6, (200.0, 200.0, 2000.0, 2000.0), n, FS), FS) for n in (primo, tondo)]
prova("e si sente forte uguale, entro mezzo decibel", abs(20 * math.log10(livelli[0] / livelli[1])) < 0.5, livelli)
bianco = np.random.default_rng(7).standard_normal(primo)
diretto = GBUtils._livello_ponderato(bianco, FS)
imbottito = GBUtils._livello_ponderato(bianco, FS, 2 * primo + 5)
prova("il livello ponderato con l'imbottitura e' quello vero, entro l'uno per cento", abs(imbottito / diretto - 1) < 0.01,
	  f"{diretto:.5f} contro {imbottito:.5f}")

# 4. Una voce fermata si spegne in cinque millesimi.
mixer = MixerDiCarta()
sfuma = round(mixer.SFUMATURA_STOP * FS)
chiamate = []
costante = np.full((FS, 2), 0.5, dtype=np.float32)
voce = mixer.suona(costante, fs=FS, a_fine=lambda: chiamate.append(1))
primo_blocco = mixer.blocco()
prova("la voce suona piena", float(np.min(primo_blocco)) > 0.49)
mixer.ferma(voce)
dopo = mixer.blocco()[:, 0]
prova("fermata, comincia ancora quasi piena", dopo[0] > 0.48, dopo[0])
prova(f"scende senza gradini fino a zero in {sfuma} campioni", float(np.max(np.abs(np.diff(dopo[:sfuma + 1])))) < 0.01 and abs(dopo[sfuma - 1]) < 1e-6,
	  dopo[sfuma - 3:sfuma + 1])
prova("dopo e' silenzio", float(np.max(np.abs(dopo[sfuma:]))) == 0.0)
prova("la voce e' finita e la funzione di fine e' chiamata una volta", voce.fine.is_set() and chiamate == [1], chiamate)
prova("e il mixer e' vuoto", mixer._voci == [])
giro = np.stack([np.full(3000, 0.4, dtype=np.float32)] * 2, axis=1)
ciclo = mixer.suona(giro, fs=FS, ciclo=True)
mixer.blocco()
maniglia = GBUtils._CicloAcceso(mixer, ciclo)
maniglia.stop()
dopo = mixer.blocco()[:, 0]
prova("anche il ciclo fermato dalla maniglia si spegne sfumando", dopo[0] > 0.38 and abs(dopo[sfuma - 1]) < 1e-6 and not maniglia.attivo, dopo[:3])
mai = mixer.suona(costante, fs=FS)
mixer.ferma(mai)
dopo = mixer.blocco()
prova("una voce fermata prima di suonare non manda niente", float(np.max(np.abs(dopo))) == 0.0 and mai.fine.is_set())

# 5. Il kind fuori dalla grammatica.
riferimento = Acusticator.sintetizza(["a4", 0.05, 0, 0.5], kind=1)
for kind in (0, 9, "x", None, True, 2.5):
	buffer, errore, avviso = con_avviso(Acusticator.sintetizza, ["a4", 0.05, 0, 0.5], kind=kind)
	prova(f"kind {kind!r} non fa cadere e avvisa", errore is None and "kind" in avviso and buffer is not None, f"{errore!r}")
	prova("e suona come la sinusoide", buffer is not None and np.array_equal(buffer, riferimento))
for kind, atteso in (("3", 3), (2.0, 2)):
	buffer, errore, avviso = con_avviso(Acusticator.sintetizza, ["a4", 0.05, 0, 0.5], kind=kind)
	prova(f"kind {kind!r} vale {atteso}, senza avvisi", errore is None and avviso == "" and np.array_equal(buffer, Acusticator.sintetizza(["a4", 0.05, 0, 0.5], kind=atteso)))

# 6. L'adsr fuori dalla grammatica.
riferimento = Acusticator.sintetizza(["a4", 0.05, 0, 0.5], kind=1, adsr=None)
for adsr in ([1, 2, 3], [0, 0, 150, 0], [60, 0, 100, 60], "abcd", [None] * 4, 7):
	buffer, errore, avviso = con_avviso(Acusticator.sintetizza, ["a4", 0.05, 0, 0.5], kind=1, adsr=adsr)
	prova(f"adsr {adsr!r} non fa cadere e avvisa", errore is None and "adsr" in avviso and buffer is not None, f"{errore!r}")
	prova("e usa quello predefinito", buffer is not None and np.array_equal(buffer, riferimento))
_, errore, avviso = con_avviso(Acusticator.sintetizza, ["a4", 0.05, 0, 0.5], kind=1, adsr=(10, 10, 80, 10))
prova("un adsr giusto, anche come tupla, passa senza avvisi", errore is None and avviso == "")
_, errore, _ = con_avviso(Acusticator.play, "preset_che_non_esiste_davvero")
prova("e play di un preset che non c'e' non cade, come prima", errore is None)

print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
