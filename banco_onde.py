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

# 4. Issue 48: dal silenzio, con l'attacco a zero, ogni onda comincia da zero
#    e sale. Per la quadra non vale: comincia per forza da un gradino.
for kind in (1, 3, 4):
	buffer = onda(["a4", 0.05, 0, 1.0], kind)
	prova(f"{NOMI[kind]} comincia da zero", abs(buffer[0]) < 0.03, f"primo campione {buffer[0]:.4f}")
	prova(f"{NOMI[kind]} sale dal primo campione", buffer[1] > buffer[0] and buffer[2] > buffer[1],
		  f"primi tre {buffer[:3].round(4).tolist()}")
	salto = float(np.max(np.abs(np.diff(buffer[:20]))))
	prova(f"{NOMI[kind]} senza salti nei primi venti campioni", salto < 0.1, f"salto massimo {salto:.4f}")

# 5. Le onde hanno la fase della sinusoide: il picco a un quarto di periodo,
#    lo zero a mezzo periodo. Il dente di sega sale per mezzo periodo e li'
#    torna giu'.
periodo = FS / 440.0
quarto, mezzo = round(periodo / 4), round(periodo / 2)
triangolo = onda(["a4", 0.05, 0, 1.0], 3)
prova("triangolare al picco dopo un quarto di periodo", triangolo[quarto] > 0.95, f"{triangolo[quarto]:.4f}")
prova("triangolare a zero dopo mezzo periodo", abs(triangolo[mezzo]) < 0.05, f"{triangolo[mezzo]:.4f}")
sega = onda(["a4", 0.05, 0, 1.0], 4)
prova("dente di sega in salita fino a mezzo periodo", sega[mezzo - 3] > 0.85, f"{sega[mezzo - 3]:.4f}")
prova("dente di sega torna giu' a mezzo periodo", sega[mezzo + 3] < -0.85, f"{sega[mezzo + 3]:.4f}")

# 6. Nessuna onda esce dal fondo scala, e un portamento lungo resta pulito.
for kind in (1, 2, 3, 4):
	buffer = onda(["c3.c7", 0.5, 0, 1.0], kind)
	prova(f"{NOMI[kind]}, scivolata da c3 a c7 dentro il fondo scala", float(np.max(np.abs(buffer))) <= 1.0 / math.cos(math.pi / 4) + 1e-6)

# 7. Note ferme con una durata che non fa un numero intero di campioni. Fino
#    alla V8.9.7 i campioni stavano su dur / N, la fase che passava alla nota
#    seguente su 1 / fs, e alla giunzione la fase saltava fino a mezzo
#    campione: a 3000 Hz, con 0,015 secondi, 36,7 gradi invece di 24,5.
#    Come nella prova 2, due note contro una lunga il doppio, sulla lunghezza
#    comune: le due spezzate e la lunga differiscono di un campione. Dalla
#    seconda revisione: la prima stesura guardava il passo alla giunzione, e
#    con 0,0123 secondi o col dente di sega passava anche sul motore di prima.
for kind in (1, 2, 3, 4):
	for durata in (0.015, 0.0123):
		spezzata = onda([3000, durata, 0, 1.0, 3000, durata, 0, 1.0], kind)
		unica = onda([3000, 2 * durata, 0, 1.0], kind)
		comune = min(len(spezzata), len(unica))
		scarto = float(np.max(np.abs(spezzata[:comune] - unica[:comune])))
		prova(f"{NOMI[kind]}, due note da {durata} s a 3000 Hz come una lunga il doppio", scarto < (1e-5 if kind == 1 else 1e-4),
			  f"scarto {scarto:.6f}")

# 8. Dopo una nota a volume zero, o una scivolata di volume che finisce a
#    zero, la nota seguente comincia da zero come dopo una pausa. Fino alla
#    V8.9.7 la fase si portava avanti, e cominciava a meta' onda.
for kind in (1, 3, 4):
	muta = onda([900, 0.2013, 0, 0.5, 900, 0.2013, 0, 0.0, 900, 0.2013, 0, 0.5], kind)
	inizio = 2 * round(0.2013 * FS)
	prova(f"{NOMI[kind]}, dopo una nota a volume zero si comincia da zero", abs(muta[inizio]) < 0.03, f"primo campione {muta[inizio]:.4f}")
	sfumata = onda([900, 0.2013, 0, (0.5, 0.0), 900, 0.2013, 0, 0.5], kind)
	inizio = round(0.2013 * FS)
	prova(f"{NOMI[kind]}, dopo una scivolata di volume a zero si comincia da zero", abs(sfumata[inizio]) < 0.03,
		  f"primo campione {sfumata[inizio]:.4f}")
	accesa = onda([900, 0.2013, 0, 0.5, 900, 0.2013, 0, 0.5], kind)
	sola = onda([900, 2 * 0.2013, 0, 0.5], kind)
	scarto = float(np.max(np.abs(accesa[:len(sola)] - sola[:len(accesa)])))
	prova(f"{NOMI[kind]}, fra due note accese la fase continua ancora", scarto < (1e-5 if kind == 1 else 1e-4), f"scarto {scarto:.6f}")

print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
