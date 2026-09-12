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
Dopo ogni gruppo si scrive cosa si e' sentito, e finisce in
collaudo_acusticator_esiti.txt accanto a questo file.
Si lancia con
  python collaudo_acusticator.py
"""
import importlib.util
import os
import subprocess
import sys
import time

from GBUtils import Acusticator, dgt, enter_escape

QUI = os.path.dirname(os.path.abspath(__file__))
ESITI = os.path.join(QUI, "collaudo_acusticator_esiti.txt")
# I preset che i programmi di Gabriele usano davvero, raccolti dai loro
# dizionari dei suoni: due giochi, un'utilita' e il feedback dei tasti.
GRUPPI = {
	"i suoni di batnav": ["partenza", "passaggio_veloce", "volo_radente", "scudisciata",
						   "respiro_di_vapore", "jingle_livello_superato", "fanfara_retro"],
	"i suoni di Terminal Beast e dei giochi": ["apertura", "terminata", "errore_secco",
											   "rifiutato", "written_ok", "doppio_tic_conferma"],
	"i suoni lunghi, dove un buco si sente": ["gabryscola_sconfitta", "jingle_missione_fallita"],
}

def riga(testo, larghezza=40):
	"""Il testo in righe da quaranta caratteri, per la lettura sul braille."""
	parole, corrente = testo.split(), ""
	for parola in parole:
		if not corrente:
			corrente = parola
		elif len(corrente) + 1 + len(parola) <= larghezza:
			corrente += " " + parola
		else:
			print(corrente)
			corrente = parola
	if corrente:
		print(corrente)

def registra(titolo, commento):
	nuovo = not os.path.exists(ESITI)
	with open(ESITI, "a", encoding="utf-8") as f:
		if nuovo:
			f.write("Esiti del collaudo d'ascolto di Acusticator col mixer condiviso\n")
			f.write("Scritti da collaudo_acusticator.py, che li aggiunge man mano.\n")
		f.write(f"\nGRUPPO: {titolo}\n")
		f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M')}\n")
		f.write(f"Commento di Gabriele: {commento if commento else 'nessuno'}\n")

def chiedi_commento(titolo):
	riga("Scrivi cosa hai sentito e batti Invio. Invio da solo se non hai niente da dire.")
	commento = dgt("\rImpressioni\r", kind="s", smin=0, smax=2000)
	registra(titolo, commento.strip())
	riga("Annotato.")
	print()

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
	riga("Collaudo d'ascolto di Acusticator.")
	print()
	riga("Acusticator adesso suona con il mixer condiviso, a scrittura, invece del suo mixer a callback. I suoni dovrebbero essere identici: questo serve a sentire se lo sono davvero.")
	print()
	riga("Ogni preset si sente due volte di fila: prima come suonava stamattina, poi come suona adesso. Fra le due c'e' mezzo secondo. Ascolta se cambia qualcosa, in particolare l'attacco, il volume e la posizione fra i due altoparlanti.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per uscire\r"):
		return 0
	vecchio, temporaneo = carica_vecchio()
	try:
		for titolo, preset in GRUPPI.items():
			riga(f"Gruppo: {titolo}. Sono {len(preset)} suoni, ognuno due volte.")
			print()
			if not enter_escape("\rInvio per questo gruppo, Escape per saltarlo\r"):
				continue
			for nome in preset:
				riga(f"{nome}: prima.")
				vecchio.Acusticator.play(nome, sync=True)
				time.sleep(0.5)
				riga(f"{nome}: adesso.")
				Acusticator.play(nome, sync=True)
				time.sleep(0.9)
			vecchio.Acusticator.close()
			Acusticator.close()
			print()
			chiedi_commento(titolo)
		riga("Ultimo ascolto: molti suoni insieme, come in una battaglia. Prima con il motore di stamattina, poi con quello nuovo.")
		print()
		if enter_escape("\rInvio per l'ultimo ascolto, Escape per saltare\r"):
			for etichetta, motore in (("prima", vecchio.Acusticator), ("adesso", Acusticator)):
				riga(f"Raffica, {etichetta}.")
				for nome in ("passaggio_veloce", "scudisciata", "doppio_tic_conferma",
							 "errore_secco", "written_ok", "apertura"):
					motore.play(nome)
					time.sleep(0.12)
				time.sleep(2.0)
				motore.close()
				time.sleep(0.8)
			print()
			chiedi_commento("la raffica di suoni ravvicinati")
	finally:
		with __import__("contextlib").suppress(OSError):
			os.remove(temporaneo)
	riga("Collaudo finito. Grazie per le orecchie.")
	if os.path.exists(ESITI):
		riga(f"Gli esiti stanno in {os.path.basename(ESITI)}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
