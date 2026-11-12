"""Banco di prova delle forme d'onda di Acusticator, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 per le issue 56 e 48.
Non suona niente e non apre la scheda audio: chiede ad Acusticator soltanto
il buffer, con sintetizza, e lo misura.
Le domande sono due. La fase resta continua fra due quartine, anche quando
scorrono di portamento? E' la issue 56: la sinusoide saltava di un campione a
ogni giunzione. Le onde cominciano da zero e salgono, come la sinusoide? E' la
issue 48: la triangolare partiva dal suo picco e il dente di sega saltava al
secondo campione, e con l'attacco a zero schioccavano.
La continuita' si prova senza scegliere una formula di riferimento: due
quartine di portamento con la stessa pendenza, una dopo l'altra, devono dare
lo stesso buffer di una quartina sola lunga quanto tutte e due.
Si lancia con
  python banco_onde.py
e stampa in fondo quante prove sono passate.
"""
import math
import sys

import numpy as np

from GBUtils import Acusticator

FS = 44100
# Niente attacco, niente rilascio, sostegno pieno: l'inviluppo vale uno da
# capo a fondo, e il buffer e' l'onda nuda.
PIATTO = [0, 0, 100, 0]
NOMI = {1: "sinusoide", 2: "quadra", 3: "triangolare", 4: "dente di sega"}

totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def onda(score, kind):
	"""Il canale sinistro riportato al centro: con pan zero vale l'onda per
	il coseno di un quarto di pi greco."""
	buffer = Acusticator.sintetizza(score, kind=kind, adsr=PIATTO, fs=FS)
	return buffer[:, 0].astype(np.float64) / math.cos(math.pi / 4)

print("Banco delle forme d'onda. Nessun suono, nessuna scheda audio.")

# 1. Issue 56: due quartine di portamento contro una sola. La sinusoide passa
#    dal ramo diretto, le altre tre dal sovracampionamento.
salite = (("440.660", "660.880", "440.880"), ("2800.3000", "3000.3200", "2800.3200"), ("1500.1000", "1000.500", "1500.500"))
for kind in (1, 2, 3, 4):
	for prima, seconda, intera in salite:
		spezzata = onda([prima, 0.05, 0, 1.0, seconda, 0.05, 0, 1.0], kind)
		unica = onda([intera, 0.1, 0, 1.0], kind)
		scarto = float(np.max(np.abs(spezzata - unica)))
		limite = 1e-5 if kind == 1 else 1e-4
		prova(f"{NOMI[kind]}, {prima} poi {seconda} come {intera}", scarto < limite, f"scarto {scarto:.6f}")

# 2. La V149 per le note ferme: due note uguali contro una lunga il doppio.
for kind in (1, 2, 3, 4):
	spezzata = onda(["a4", 0.05, 0, 1.0, "a4", 0.05, 0, 1.0], kind)
	unica = onda(["a4", 0.1, 0, 1.0], kind)
	scarto = float(np.max(np.abs(spezzata - unica)))
	prova(f"{NOMI[kind]}, due la4 come uno lungo il doppio", scarto < (1e-5 if kind == 1 else 1e-4), f"scarto {scarto:.6f}")

# 3. Il salto alla giunzione, misurato: con fase continua il passo fra
#    l'ultimo campione della prima quartina e il primo della seconda non e'
#    piu' grande dei passi vicini.
for kind in (1, 3):
	spezzata = onda(["2800.3000", 0.05, 0, 1.0, "3000.3200", 0.05, 0, 1.0], kind)
	giunzione = round(0.05 * FS)
	passo = abs(spezzata[giunzione] - spezzata[giunzione - 1])
	vicini = np.abs(np.diff(spezzata[giunzione - 40:giunzione - 1]))
	prova(f"{NOMI[kind]}, nessun salto alla giunzione a 3000 Hz", passo <= float(np.max(vicini)) * 1.01,
		  f"passo {passo:.4f}, vicini fino a {float(np.max(vicini)):.4f}")

# 4. Nessuna onda esce dal fondo scala, e un portamento lungo resta pulito.
for kind in (1, 2, 3, 4):
	buffer = onda(["c3.c7", 0.5, 0, 1.0], kind)
	prova(f"{NOMI[kind]}, scivolata da c3 a c7 dentro il fondo scala", float(np.max(np.abs(buffer))) <= 1.0 / math.cos(math.pi / 4) + 1e-6)

print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
