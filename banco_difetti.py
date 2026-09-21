"""Banco di prova del chirp e del vibrato di CWzator, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' ultracode).
Nato con la V167 e la issue 42, il 22 settembre 2026.
Niente di questo fa rumore: si genera con play=False e si misura la frequenza
istantanea dei campioni prodotti, contando i passaggi per lo zero.
Le domande a cui il banco risponde sono cinque.
La prima e' se senza chirp e senza vibrato non cambi niente: l'audio dev'essere
identico campione per campione a quello di sempre, perche' un parametro nuovo
che cambia il comportamento predefinito e' un difetto, non una funzionalita'.
La seconda e' se il chirp faccia quello che dice: dentro ogni elemento la
frequenza deve passare dal tono al tono piu' il chirp, e la differenza fra il
primo e l'ultimo quarto dell'elemento deve valere quanto si e' chiesto.
La terza e' se il vibrato segua il tempo del messaggio e non quello
dell'elemento: due punti distanti nel messaggio devono trovarsi in punti
diversi dell'oscillazione, altrimenti sarebbe lo stesso campione ripetuto.
La quarta e' se nessuno dei due tocchi cio' che non deve: durata, numero di
campioni e velocita' effettiva identici, perche' la velocita' si misura sulle
durate e non sulle frequenze.
La quinta e' se i valori sbagliati vengano rifiutati con un messaggio.
Si lancia con
  python banco_difetti.py
e stampa in fondo quante prove sono passate.
"""

import itertools
import sys

import numpy as np

from GBUtils import CWzator

FS = 44100
TONO = 600
totale = passate = 0


def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")


def genera(**kw):
	kw.setdefault("play", False)
	kw.setdefault("wpm", 20)
	kw.setdefault("pitch", TONO)
	kw.setdefault("fs", FS)
	kw.setdefault("ms", 0)
	return CWzator(**kw)


def frequenza(pezzo):
	"""La frequenza di un pezzo di tono, contando i passaggi per lo zero.

	Due passaggi per periodo: la frequenza e' meta' dei passaggi diviso la
	durata. Su un pezzo corto la misura e' grossolana, ma basta a distinguere
	uno scarto di decine di hertz.
	"""
	pezzo = pezzo.astype(np.float64)
	if pezzo.size < 8:
		return 0.0
	passaggi = np.count_nonzero(np.diff(np.signbit(pezzo)))
	return passaggi / 2.0 / (pezzo.size / FS)


def elementi(audio, pitch=TONO):
	"""Tutti i tratti accesi del messaggio, in ordine.

	I passaggi per lo zero dell'onda non sono silenzio: contando i campioni
	sopra una soglia, un elemento si spezzerebbe in decine di frammenti. Si
	chiudono con una chiusura morfologica lunga un periodo, che lascia intatti
	i bordi dei tratti veri. E' la tecnica di banco_farnsworth.
	"""
	finestra = int(FS / pitch) + 2
	acceso = np.abs(audio.astype(np.int32)) > 0
	dilatato = np.convolve(acceso.astype(np.int32), np.ones(finestra, np.int32), "same") > 0
	acceso = np.convolve((~dilatato).astype(np.int32), np.ones(finestra, np.int32), "same") == 0
	cambi = np.flatnonzero(np.diff(acceso.astype(np.int8))) + 1
	bordi = np.concatenate(([0], cambi, [acceso.size]))
	pezzi = []
	for a, b in itertools.pairwise(bordi):
		if acceso[a] and b - a > 16:
			pezzi.append(audio[a:b])
	return pezzi


def primo_elemento(audio, pitch=TONO):
	"""I campioni del primo tratto acceso del messaggio."""
	pezzi = elementi(audio, pitch)
	return pezzi[0] if pezzi else np.array([], dtype=np.int16)


# 1. Senza i due parametri non cambia niente.
liscio, rwpm_liscio = genera(msg="paris paris")
ancora, _ = genera(msg="paris paris")
prova("senza chirp e senza vibrato l'audio e' quello di sempre",
	  np.array_equal(liscio.audio_data, ancora.audio_data))

# 2. Il chirp fa scorrere la frequenza dentro l'elemento.
salita, rwpm_salita = genera(msg="t t t", chirp=120)
discesa, _ = genera(msg="t t t", chirp=-120)
for nome, handle, atteso in (("in salita", salita, 120), ("in discesa", discesa, -120)):
	linea = primo_elemento(handle.audio_data)
	quarto = linea.size // 4
	scarto = frequenza(linea[-quarto:]) - frequenza(linea[:quarto])
	# I due quarti stanno a meta' elemento l'uno dall'altro, quindi vedono
	# tre quarti dello scarto totale.
	prova(f"il chirp {nome} sposta la frequenza dentro l'elemento",
		  abs(scarto - atteso * 0.75) < abs(atteso) * 0.35, f"misurato {scarto:.0f} su {atteso * 0.75:.0f} attesi")
liscia = primo_elemento(genera(msg="t t t")[0].audio_data)
quarto = liscia.size // 4
prova("senza chirp la frequenza dentro l'elemento non si muove",
	  abs(frequenza(liscia[-quarto:]) - frequenza(liscia[:quarto])) < 20,
	  f"{frequenza(liscia[:quarto]):.0f} contro {frequenza(liscia[-quarto:]):.0f}")
prova("e senza chirp l'elemento suona al tono chiesto",
	  abs(frequenza(liscia) - TONO) < 15, f"{frequenza(liscia):.0f} invece di {TONO}")

# 3. Il vibrato segue il tempo del messaggio, non quello dell'elemento.
vibrato, rwpm_vibrato = genera(msg="eeeeeeeeeeeeeeee", vibrato=(40, 3.0))
punti = elementi(vibrato.audio_data)
prova("il messaggio di prova produce molti punti", len(punti) >= 12, len(punti))
frequenze = [frequenza(p) for p in punti]
prova("con il vibrato i punti non hanno tutti la stessa frequenza",
	  max(frequenze) - min(frequenze) > 20, f"da {min(frequenze):.0f} a {max(frequenze):.0f}")
senza = [frequenza(p) for p in elementi(genera(msg="eeeeeeeeeeeeeeee")[0].audio_data)]
prova("senza vibrato i punti hanno tutti la stessa frequenza",
	  max(senza) - min(senza) < 15, f"da {min(senza):.0f} a {max(senza):.0f}")
prova("e i punti non sono piu' lo stesso campione ripetuto",
	  not np.array_equal(punti[0], punti[len(punti) // 2]))

# 4. Nessuno dei due tocca le durate.
prova("il chirp non cambia la velocita' effettiva", rwpm_salita == genera(msg="t t t")[1])
prova("il vibrato non cambia la velocita' effettiva", rwpm_vibrato == genera(msg="eeeeeeeeeeeeeeee")[1])
prova("il chirp non cambia il numero di campioni",
	  salita.audio_data.size == genera(msg="t t t")[0].audio_data.size)
prova("il vibrato non cambia il numero di campioni",
	  vibrato.audio_data.size == genera(msg="eeeeeeeeeeeeeeee")[0].audio_data.size)

# 5. I valori sbagliati.
for valore in (300, -300, "tanto", True):
	handle, _ = genera(msg="test", chirp=valore)
	prova(f"chirp {valore!r} viene rifiutato", handle is None and "chirp" in (CWzator.ultimo_errore or ""), CWzator.ultimo_errore)
for valore in (0, 200, (5,), "tanto", (5, 100), (0, 6)):
	handle, _ = genera(msg="test", vibrato=valore)
	prova(f"vibrato {valore!r} viene rifiutato", handle is None and "vibrato" in (CWzator.ultimo_errore or ""), CWzator.ultimo_errore)
prova("il vibrato accetta anche un numero solo, con la sua frequenza di serie",
	  genera(msg="test", vibrato=8)[0] is not None)

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
