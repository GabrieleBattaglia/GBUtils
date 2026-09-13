"""Collaudo d'ascolto di Acusticator dopo il passaggio al mixer condiviso.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 12 settembre 2026, tappa 2 della issue 8.
Acusticator suonava con un mixer suo, a callback; adesso usa quello
condiviso, a scrittura. I banchi dicono che il contratto e' intatto e che
sotto carico non si perde piu' un campione; cio' che i banchi non sanno dire
e' se i suoni siano rimasti gli stessi all'orecchio, ed e' quello che si
prova qui.
Ogni preset si sente due volte di fila, prima con il motore di prima, preso
da git, e poi con quello di adesso. Sono gli stessi suoni che i programmi
usano davvero, non note di prova.
In fondo a ogni gruppo: r riascolta il gruppo intero, c apre il posto dove
scrivere, Invio lo da' per superato, Escape lo chiude senza annotare. Quello
che si scrive finisce in collaudo_acusticator_esiti.txt accanto a questo file.
Si lancia con
  python collaudo_acusticator.py
"""
import contextlib
import importlib.util
import os
import subprocess
import sys
import time

from collaudo_comune import Esiti, gruppo

from GBUtils import Acusticator, enter_escape

QUI = os.path.dirname(os.path.abspath(__file__))
# I preset che i programmi di Gabriele usano davvero, raccolti dai loro
# dizionari dei suoni: due giochi, un'utilita' e il feedback dei tasti.
GRUPPI = {
	"i suoni di batnav": ["partenza", "passaggio_veloce", "volo_radente", "scudisciata",
						   "respiro_di_vapore", "jingle_livello_superato", "fanfara_retro"],
	"i suoni di Terminal Beast e dei giochi": ["apertura", "terminata", "errore_secco",
											   "rifiutato", "written_ok", "doppio_tic_conferma"],
	"i suoni lunghi, dove un buco si sente": ["gabryscola_sconfitta", "jingle_missione_fallita"],
}

esiti = Esiti(os.path.join(QUI, "collaudo_acusticator_esiti.txt"),
			  "Esiti del collaudo d'ascolto di Acusticator col mixer condiviso\n"
			  "Scritti da collaudo_acusticator.py, che li aggiunge man mano.")

def carica_vecchio():
	"""Acusticator com'era prima del mixer condiviso, preso dall'ultimo commit."""
	sorgente = subprocess.run(["git", "-C", QUI, "show", "HEAD:GBUtils.py"],
							  capture_output=True, check=True).stdout
	percorso = os.path.join(QUI, "_acusticator_di_prima.py")
	with open(percorso, "wb") as f:
		f.write(sorgente)
	spec = importlib.util.spec_from_file_location("_acusticator_di_prima", percorso)
	modulo = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(modulo)
	return modulo, percorso

def main():
	print("Collaudo d'ascolto di Acusticator.")
	print()
	print("Acusticator adesso suona con il mixer condiviso, a scrittura, invece del suo mixer a callback.")
	print("I suoni dovrebbero essere identici: questo serve a sentire se lo sono davvero.")
	print()
	print("Ogni preset si sente due volte di fila: prima come suonava stamattina, poi come suona adesso.")
	print("Fra le due c'e' mezzo secondo. Ascolta se cambia qualcosa, in particolare l'attacco, il volume")
	print("e la posizione fra i due altoparlanti.")
	print()
	print("In fondo a ogni gruppo: r riascolta, c commenta, Invio lo da' per superato.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per uscire\r"):
		return 0
	vecchio, temporaneo = carica_vecchio()
	try:
		for titolo, preset in GRUPPI.items():
			if not gruppo(titolo, len(preset)):
				continue
			def ascolta(preset=preset):
				for nome in preset:
					print(f"  {nome}: prima.")
					vecchio.Acusticator.play(nome, sync=True)
					time.sleep(0.5)
					print(f"  {nome}: adesso.")
					Acusticator.play(nome, sync=True)
					time.sleep(0.9)
				vecchio.Acusticator.close()
				Acusticator.close()
				print()
			ascolta()
			esiti.esito(titolo, ascolta,
						"  La domanda: il secondo di ogni coppia suona identico al primo?")
		titolo = "la raffica di suoni ravvicinati"
		if gruppo(titolo, 2):
			print("  Molti suoni insieme, come in una battaglia. Prima con il motore di stamattina, poi con")
			print("  quello nuovo.")
			def ascolta_raffica():
				for etichetta, motore in (("prima", vecchio.Acusticator), ("adesso", Acusticator)):
					print(f"  Raffica, {etichetta}.")
					for nome in ("passaggio_veloce", "scudisciata", "doppio_tic_conferma",
								 "errore_secco", "written_ok", "apertura"):
						motore.play(nome)
						time.sleep(0.12)
					time.sleep(2.0)
					motore.close()
					time.sleep(0.8)
				print()
			ascolta_raffica()
			esiti.esito(titolo, ascolta_raffica,
						"  La domanda: nella seconda raffica senti buchi, scatti o suoni che mancano?")
	finally:
		with contextlib.suppress(OSError):
			os.remove(temporaneo)
	print("Collaudo finito. Grazie per le orecchie.")
	if os.path.exists(esiti.percorso):
		print(f"Gli esiti stanno in {os.path.basename(esiti.percorso)}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
