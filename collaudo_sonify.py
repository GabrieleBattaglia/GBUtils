"""Collaudo d'ascolto di sonify, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, modalita' auto).
Nato con la revisione 1 di sonify, l'8 settembre 2026.
Conduce le prove d'ascolto una alla volta: spiega prima cosa si sta per
sentire e cosa osservare, aspetta un tasto, suona e aspetta la fine.
Si lancia con
  python collaudo_sonify.py
Invio suona la prova, Escape salta alla successiva o esce dall'ultima.
"""
import os
import sys
import tempfile

import sounddevice as sd

from GBUtils import enter_escape, sonify

# La stessa serie in tutte le prove di scala: sale con passo regolare, poi
# negli ultimi dieci valori si muove di poco vicino al massimo, che e' la
# zona in cui l'orecchio distingue peggio le altezze.
SERIE = list(range(0, 100, 2)) + [98, 100, 99, 100, 98, 101, 99, 100, 101, 100]
DURATA = 8.0

def prove():
	spiegazione = ("Scala intera, sei ottave dal fa2 al fa8, la predefinita. "
		"Osserva se gli ultimi dieci valori, vicini fra loro in cima "
		"alla scala, si distinguono l'uno dall'altro.")
	yield spiegazione, {"pan": True}
	spiegazione = ("La stessa serie su tre ottave, da 110 a 880 hertz. "
		"Confronta la coda con quella di prima: se qui i piccoli "
		"movimenti in cima si sentono meglio, la scala stretta e' "
		"piu' leggibile e conviene cambiare il predefinito.")
	yield spiegazione, {"freq_min": 110.0, "freq_max": 880.0}
	spiegazione = ("Scala intera, con il portamento: le note scivolano una "
		"nell'altra invece di stare ferme. Osserva se la coda resta "
		"leggibile.")
	yield spiegazione, {"ptm": True}
	spiegazione = ("Scala intera, senza panoramica: il suono resta al centro "
		"per tutta la durata, invece di correre da sinistra a destra.")
	yield spiegazione, {"pan": False}
	spiegazione = ("Scala intera, panoramica al contrario: il suono parte da "
		"destra e finisce a sinistra.")
	yield spiegazione, {"pan": (1, -1)}
	spiegazione = ("Scala intera, e in piu' il file: viene scritto un wav nella "
		"cartella temporanea di sistema e il percorso viene stampato. "
		"Aprilo con un lettore qualsiasi e verifica che sia lo stesso "
		"suono, stereo, senza schiocchi ai bordi.")
	yield spiegazione, {"file": os.path.join(tempfile.gettempdir(), "collaudo_sonify.wav")}

def main():
	print("Collaudo d'ascolto di sonify.")
	print(f"Sei prove, ognuna di {DURATA:.0f} secondi.")
	for numero, (spiegazione, parametri) in enumerate(prove(), 1):
		print(f"Prova {numero}. {spiegazione}")
		if not enter_escape("\rInvio per ascoltare, Escape per saltare.\r"):
			continue
		percorso = sonify(SERIE, DURATA, vol=0.4, **parametri)
		sd.wait()
		if percorso:
			print(f"File scritto: {percorso}")
	print("Collaudo terminato.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
