"""Collaudo d'ascolto dei bordi smorzati dal ricampionamento, issue 35.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto).
Nato il 15 settembre 2026.
Le tre onde non sinusoidali nascono sovracampionate otto volte e vengono
riportate alla frequenza normale nota per nota. Il filtro che lo fa e' lungo
161 campioni, e ai due capi della nota non aveva segnale da cui prendere: vedeva
zeri, e ogni nota cominciava e finiva smorzata per una decina di campioni,
qualunque cosa dicesse l'inviluppo. Adesso si sintetizza un margine di ottanta
campioni prima e dopo, preso dalla continuazione naturale dell'onda, e lo si
butta via dopo il ricampionamento.
La misura dice che il difetto e' sparito del tutto: su una nota nuda, senza
inviluppo, lo scarto ai bordi passa da 0,44 a zero esatto. Ma dice anche che
nei preset veri l'inviluppo smorzava gia' i bordi per conto suo: su
centonove preset a onda ricampionata, ottantuno non cambiano di un solo
campione e soltanto dieci cambiano piu' di un millesimo. Sono i colpi
d'impatto, tutti a dente di sega, ed e' su quelli che ha senso ascoltare.
Quindi la domanda di questo collaudo non e' "e' meglio?" ma "si sente?". Se non
si sente niente e' un esito buono: vuol dire che la cura non ha fatto danni in
un posto dove il difetto, all'orecchio, non c'era.
Ogni prova e' una coppia: prima il preset come suonava ieri, preso da git, poi
come suona adesso. Tutto al trenta per cento di volume.
In fondo a ogni gruppo: r riascolta il gruppo intero, c apre il posto dove
scrivere, Invio lo da' per superato, Escape lo chiude senza annotare.
Si lancia con
  python collaudo_bordi.py
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
# I dieci preset in cui la misura vede la differenza piu' grande, 0,0447 su
# segnali che arrivano a uno. Sono tutti a dente di sega.
CAMBIANO = ["colpo_d_impatto_1", "colpo_d_impatto_2", "colpo_d_impatto_3",
			"colpo_d_impatto_5", "colpo_d_impatto_6", "colpo_d_impatto_7",
			"colpo_d_impatto_8", "colpo_d_impatto_9", "colpo_d_impatto_10",
			"grosse_biglie"]

esiti = Esiti(os.path.join(QUI, "collaudo_bordi_esiti.txt"),
			  "Esiti del collaudo d'ascolto dei bordi smorzati, issue 35\n"
			  "Scritti da collaudo_bordi.py, che li aggiunge man mano.")


def carica_ieri():
	"""GBUtils com'era prima del margine, preso dall'ultimo commit."""
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
	"""Preset che le due versioni producono identici, campione per campione:
	servono da controllo, perche' il secondo suono di una coppia viene
	preferito anche quando e' lo stesso."""
	trovati = []
	for nome in Acusticator.list():
		score, kind, adsr = Acusticator.preset(nome)
		if not score or kind >= 5:
			continue
		vecchio = ieri._sintetizza(score, kind, adsr, FS)
		nuovo = _sintetizza(score, kind, adsr, FS)
		if vecchio is None or nuovo is None or vecchio.size == 0:
			continue
		if vecchio.shape[0] / FS > 0.5 and np.array_equal(vecchio, nuovo):
			trovati.append(nome)
		if len(trovati) >= quanti:
			break
	return trovati


def main():
	print("Collaudo d'ascolto dei bordi smorzati dal ricampionamento.")
	print()
	print("Ogni nota di un'onda quadra, triangolare o a dente di sega veniva riportata alla")
	print("frequenza normale per conto suo, e ai due capi il filtro non aveva segnale da cui")
	print("prendere: vedeva zeri, e la nota cominciava e finiva smorzata per una decina di")
	print("campioni. Adesso il filtro ha il contesto che gli mancava.")
	print()
	print("Su una nota nuda il difetto e' sparito del tutto, misurato. Nei preset veri pero'")
	print("l'inviluppo smorzava gia' i bordi da se': su 109 preset a onda ricampionata, 81")
	print("non cambiano di un campione e solo 10 cambiano piu' di un millesimo.")
	print("Sono questi dieci, e la domanda non e' se sia meglio ma se si senta.")
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
		titolo = "i dieci che cambiano"
		if gruppo(titolo, len(CAMBIANO)):
			print("  Colpi d'impatto e biglie, tutti a dente di sega. La differenza misurata e' di")
			print("  0,0447 su segnali che arrivano a uno, e sta tutta nei primi e negli ultimi")
			print("  dieci campioni di ogni nota.")

			def ascolta_cambiano():
				for nome in CAMBIANO:
					coppia(ieri, nome)
				print()

			ascolta_cambiano()
			esiti.esito(titolo, ascolta_cambiano,
						"  La domanda: senti differenza fra le due di ogni coppia? Se si', quale preferisci?")
		identici = trova_identici(ieri)
		titolo = "un ultimo gruppo"
		if identici and gruppo(titolo, len(identici)):
			print("  Altri preset, stessa forma delle prove di prima.")

			def ascolta_identici():
				for nome in identici:
					coppia(ieri, nome)
				print()

			ascolta_identici()
			esiti.esito(titolo, ascolta_identici,
						"  La domanda: senti differenza fra le due di ogni coppia?")
			print("Una cosa che non ti avevo detto: in quest'ultimo gruppo le due versioni producono")
			print("campioni identici, verificato uno per uno. Se qui hai sentito una differenza, allora")
			print("anche quelle del primo gruppo vanno prese con prudenza.")
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
