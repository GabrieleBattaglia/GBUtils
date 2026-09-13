"""Collaudo d'ascolto di sonify, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, modalita' auto).
Nato con la revisione 1 di sonify, l'8 settembre 2026.
Conduce le prove d'ascolto una alla volta: spiega prima cosa si sta per
sentire e cosa osservare, aspetta un tasto, suona e aspetta la fine.
In fondo a ogni prova: r la riascolta, c apre il posto dove scrivere, Invio la
da' per superata, Escape la chiude senza annotare. Quello che si scrive
finisce in collaudo_sonify_esiti.txt accanto a questo file.
Si lancia con
  python collaudo_sonify.py
"""
import os
import sys
import tempfile

import sounddevice as sd
from collaudo_comune import Esiti, gruppo

from GBUtils import sonify

QUI = os.path.dirname(os.path.abspath(__file__))
# La stessa serie in tutte le prove di scala: sale con passo regolare, poi
# negli ultimi dieci valori si muove di poco vicino al massimo, che e' la
# zona in cui l'orecchio distingue peggio le altezze.
SERIE = list(range(0, 100, 2)) + [98, 100, 99, 100, 98, 101, 99, 100, 101, 100]
DURATA = 8.0

esiti = Esiti(os.path.join(QUI, "collaudo_sonify_esiti.txt"),
			  "Esiti del collaudo d'ascolto di sonify\n"
			  "Scritti da collaudo_sonify.py, che li aggiunge man mano.",
			  etichetta="PROVA")

def prove():
	titolo = "la scala intera, quella predefinita"
	spiegazione = ("Scala intera, sei ottave dal fa2 al fa8, la predefinita. Osserva se gli ultimi dieci "
		"valori, vicini fra loro in cima alla scala, si distinguono l'uno dall'altro.")
	yield titolo, spiegazione, {"pan": True}
	titolo = "la scala stretta, tre ottave"
	spiegazione = ("La stessa serie su tre ottave, da 110 a 880 hertz. Confronta la coda con quella di "
		"prima: se qui i piccoli movimenti in cima si sentono meglio, la scala stretta e' piu' leggibile "
		"e conviene cambiare il predefinito.")
	yield titolo, spiegazione, {"freq_min": 110.0, "freq_max": 880.0}
	titolo = "il portamento"
	spiegazione = ("Scala intera, con il portamento: le note scivolano una nell'altra invece di stare "
		"ferme. Osserva se la coda resta leggibile.")
	yield titolo, spiegazione, {"ptm": True}
	titolo = "senza panoramica"
	spiegazione = ("Scala intera, senza panoramica: il suono resta al centro per tutta la durata, invece "
		"di correre da sinistra a destra.")
	yield titolo, spiegazione, {"pan": False}
	titolo = "la panoramica al contrario"
	spiegazione = "Scala intera, panoramica al contrario: il suono parte da destra e finisce a sinistra."
	yield titolo, spiegazione, {"pan": (1, -1)}
	titolo = "il file wav"
	spiegazione = ("Scala intera, e in piu' il file: viene scritto un wav nella cartella temporanea di "
		"sistema e il percorso viene stampato. Aprilo con un lettore qualsiasi e verifica che sia lo "
		"stesso suono, stereo, senza schiocchi ai bordi.")
	yield titolo, spiegazione, {"file": os.path.join(tempfile.gettempdir(), "collaudo_sonify.wav")}

def main():
	print("Collaudo d'ascolto di sonify.")
	print(f"Sei prove, ognuna di {DURATA:.0f} secondi.")
	print("In fondo a ogni prova: r la riascolta, c commenta, Invio la da' per superata.")
	print()
	for numero, (titolo, spiegazione, parametri) in enumerate(prove(), 1):
		if not gruppo(f"{numero}, {titolo}", unita=None):
			continue
		print(f"  {spiegazione}")
		def ascolta(parametri=parametri):
			percorso = sonify(SERIE, DURATA, vol=0.4, **parametri)
			sd.wait()
			if percorso:
				print(f"  File scritto: {percorso}")
		ascolta()
		esiti.esito(f"{numero}, {titolo}", ascolta, "  La domanda: e' come deve essere?")
	print("Collaudo terminato.")
	if os.path.exists(esiti.percorso):
		print(f"Gli esiti stanno in {os.path.basename(esiti.percorso)}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
