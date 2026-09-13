"""Collaudo d'ascolto della continuita' di fase, issue 34.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 13 settembre 2026.
Fino a ieri ogni nota di un preset ripartiva da fase zero, e fra due note
contigue il segnale saltava dal valore a cui la prima era arrivata allo zero da
cui la seconda cominciava: e' il gradino che si sentiva come uno schiocco.
Adesso l'onda prosegue da dove era arrivata.
La misura dice che su 173 preset con almeno un confine fra due note che suonano,
32 sono migliorati, 126 non cambiano e 15 sono peggiorati. Non e' una vittoria
piena, ed e' per questo che si ascolta: i numeri dicono dove guardare, le
orecchie dicono se conviene.
Ogni prova e' una coppia: prima il preset come suonava ieri, preso da git, poi
come suona adesso.
Tutto al trenta per cento di volume.
In fondo a ogni gruppo: r riascolta il gruppo intero, c apre il posto dove
scrivere, Invio lo da' per superato, Escape lo chiude senza annotare.
Si lancia con
  python collaudo_fase.py
"""
import contextlib
import importlib.util
import os
import subprocess
import sys
import time

import numpy as np
from collaudo_comune import Esiti, gruppo

from GBUtils import Acusticator, _sintetizza, enter_escape

QUI = os.path.dirname(os.path.abspath(__file__))
FS = 44100
VOL = 0.30
# Scelti dalla misura del 13 settembre: il salto al confine in quante volte
# quello naturale dell'onda li' intorno.
GUARITI = [("spostamento_f6", "da 19,3 a 0,33 volte"),
		   ("successivo", "da 19,2 a 0,73"),
		   ("tripletta_su_tripletta_giu", "da 31,3 a 7,5"),
		   ("sirena_d_allarme_9", "da 32,7 a 9,1"),
		   ("vittoria", "da 24,5 a 9,8")]
PEGGIORATI = [("sirena_d_allarme_10", "da 7,8 a 19,4 volte"),
			  ("sirena_d_allarme_7", "da 0,5 a 10,9"),
			  ("scintilla_magica_2", "da 28,6 a 32,8"),
			  ("sirena_d_allarme_4", "da 4,0 a 10,7")]

esiti = Esiti(os.path.join(QUI, "collaudo_fase_esiti.txt"),
			  "Esiti del collaudo d'ascolto della continuita' di fase, issue 34\n"
			  "Scritti da collaudo_fase.py, che li aggiunge man mano.")

def carica_ieri():
	"""GBUtils com'era prima della continuita' di fase, preso dall'ultimo commit."""
	sorgente = subprocess.run(["git", "-C", QUI, "show", "HEAD:GBUtils.py"],
							  capture_output=True, check=True).stdout
	percorso = os.path.join(QUI, "_gbutils_di_ieri.py")
	with open(percorso, "wb") as f:
		f.write(sorgente)
	spec = importlib.util.spec_from_file_location("_gbutils_di_ieri", percorso)
	modulo = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(modulo)
	return modulo, percorso

def coppia(ieri, nome, nota=""):
	"""Prima come suonava ieri, poi come suona adesso."""
	score, kind, adsr = Acusticator.preset(nome)
	if not score:
		print(f"  {nome}: non lo trovo")
		return
	print(f"  {nome}, ieri{': ' + nota if nota else ''}")
	Acusticator.riproduci(ieri._sintetizza(score, kind, adsr, FS), fs=FS, sync=True)
	time.sleep(0.45)
	print(f"  {nome}, adesso")
	Acusticator.riproduci(_sintetizza(score, kind, adsr, FS), fs=FS, sync=True)
	time.sleep(0.8)

def trova_identici(ieri, quanti=4):
	"""I preset lunghi che le due versioni producono identici, per il controllo."""
	trovati = []
	for nome in Acusticator.list():
		score, kind, adsr = Acusticator.preset(nome)
		if not score or kind >= 5:
			continue
		vecchio = ieri._sintetizza(score, kind, adsr, FS)
		nuovo = _sintetizza(score, kind, adsr, FS)
		if vecchio is None or nuovo is None or vecchio.size == 0:
			continue
		if vecchio.shape[0] / FS > 0.7 and np.array_equal(vecchio, nuovo):
			trovati.append(nome)
		if len(trovati) >= quanti:
			break
	return trovati

def main():
	print("Collaudo d'ascolto della continuita' di fase.")
	print()
	print("Fino a ieri ogni nota ripartiva da fase zero, e al confine fra due note il segnale saltava.")
	print("Adesso l'onda prosegue da dove era arrivata. L'inviluppo non e' stato toccato: un attacco a")
	print("zero continua a fare lo schiocco che chi lo sceglie si aspetta, ed e' giusto cosi'.")
	print()
	print("Ogni prova e' una coppia: prima come suonava ieri, poi come suona adesso.")
	print("In fondo a ogni gruppo: r riascolta, c commenta, Invio lo da' per superato.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per uscire\r"):
		return 0
	prima_del_collaudo = Acusticator.stato()["volume"]
	Acusticator.setup(volume=VOL)
	ieri, temporaneo = carica_ieri()
	try:
		titolo = "quelli che la misura dice guariti"
		if gruppo(titolo, len(GUARITI)):
			print("  Su questi il salto al confine e' calato molto. Se la cura funziona, qui si deve sentire.")
			def ascolta_guariti():
				for nome, nota in GUARITI:
					coppia(ieri, nome, nota)
				print()
			ascolta_guariti()
			esiti.esito(titolo, ascolta_guariti,
						"  La domanda: nel secondo di ogni coppia lo schiocco fra una nota e l'altra e' sparito o attenuato?")
		titolo = "quelli che la misura dice peggiorati"
		if gruppo(titolo, len(PEGGIORATI)):
			print("  Su questi il salto e' cresciuto. Sono quasi tutte sirene, cioe' onde triangolari, dove")
			print("  entra in gioco un altro difetto piu' vecchio che non ho toccato: ogni nota viene")
			print("  ricampionata per conto suo e ai bordi il filtro la smorza. La domanda e' se il")
			print("  peggioramento si senta o resti sulla carta.")
			def ascolta_peggiorati():
				for nome, nota in PEGGIORATI:
					coppia(ieri, nome, nota)
				print()
			ascolta_peggiorati()
			esiti.esito(titolo, ascolta_peggiorati,
						"  La domanda: il secondo di ogni coppia e' peggiore del primo, o sono pari?")
		identici = trova_identici(ieri)
		titolo = "un ultimo gruppo"
		if identici and gruppo(titolo, len(identici)):
			print("  Quattro preset lunghi, stessa forma delle prove di prima.")
			def ascolta_identici():
				for nome in identici:
					coppia(ieri, nome)
				print()
			ascolta_identici()
			esiti.esito(titolo, ascolta_identici,
						"  La domanda: senti differenza fra le due di ogni coppia?")
			print("Una cosa che non ti avevo detto: in quest'ultimo gruppo le due versioni producono")
			print("campioni identici, verificato uno per uno. Se qui non hai sentito niente, le differenze")
			print("degli altri gruppi sono vere.")
			print()
	finally:
		with contextlib.suppress(OSError):
			os.remove(temporaneo)
	Acusticator.setup(volume=prima_del_collaudo)
	Acusticator.close()
	print("Collaudo finito. Grazie per le orecchie.")
	if os.path.exists(esiti.percorso):
		print(f"Gli esiti stanno in {os.path.basename(esiti.percorso)}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
