"""Le parti comuni dei collaudi d'ascolto, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 13 settembre 2026, quando Gabriele ha chiesto lo stesso menu di fine
gruppo in tutti i collaudi.
Non fa parte di GBUtils: e' l'impalcatura delle prove d'ascolto, e sta accanto
a loro invece che dentro la libreria, che va nei pacchetti dei quindici
programmi e non ha ragione di portarsi dietro il banco di prova.
Cosa c'e' dentro:
  gruppo    annuncia un gruppo e aspetta il via, o il permesso di saltarlo.
  Esiti     il registro degli esiti e il menu che chiude ogni gruppo.
Il menu e' sempre lo stesso, perche' le dita imparino una volta sola: r
riascolta il gruppo intero, c apre il posto dove scrivere le impressioni,
Invio lo da' per superato senza far scrivere niente, Escape lo chiude senza
annotare. Dopo ogni scelta si torna al menu, cosi' si puo' riascoltare, poi
commentare, poi riascoltare ancora, e chiudere solo quando si e' pronti.
Si importa cosi', da un collaudo che sta nella stessa cartella:
  from collaudo_comune import Esiti, gruppo
"""
import os
import time

from GBUtils import dgt, enter_escape, key


def gruppo(titolo, quante=None, unita="coppie"):
	"""Annuncia un gruppo e aspetta il via. Falso se si vuole saltarlo."""
	if quante is None:
		print(f"Gruppo: {titolo}.")
	elif unita == "coppie":
		print(f"Gruppo: {titolo}. Sono {quante} coppie, cioe' {quante * 2} ascolti.")
	else:
		print(f"Gruppo: {titolo}. Sono {quante} {unita}.")
	return enter_escape("\rInvio per questo gruppo, Escape per saltarlo\r")

class Esiti:
	"""Il registro di un collaudo, e il menu che chiude ogni gruppo.

	percorso     il file dove gli esiti si accumulano, riga dopo riga.
	intestazione le due righe scritte in cima quando il file nasce.
	"""

	def __init__(self, percorso, intestazione="", etichetta="GRUPPO"):
		self.percorso = percorso
		self.intestazione = intestazione
		self.etichetta = etichetta

	def registra(self, titolo, commento, misura=""):
		"""Aggiunge un esito in fondo al file, creandolo se non c'e'.

		misura, quando c'e', e' il numero che la prova ha prodotto: si scrive
		accanto al commento, perche' un giudizio senza il dato a cui si
		riferisce, riletto fra un mese, non dice piu' niente.
		"""
		nuovo = not os.path.exists(self.percorso)
		with open(self.percorso, "a", encoding="utf-8") as f:
			if nuovo and self.intestazione:
				f.write(self.intestazione.rstrip("\n") + "\n")
			f.write(f"\n{self.etichetta}: {titolo}\n")
			f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M')}\n")
			if misura:
				f.write(f"Misura: {misura}\n")
			f.write(f"Commento di Gabriele: {commento if commento else 'nessuno'}\n")

	def esito(self, titolo, riproduci=None, domanda="", misura=""):
		"""Chiude un gruppo. Restituisce come si e' chiuso.

		riproduci e' la funzione che rifa' l'ascolto del gruppo: passandola,
		r lo riascolta. Senza, r dice che non si puo' e resta li'.
		Con Invio si registra il gruppo come superato soltanto se non si e'
		gia' commentato, altrimenti non si aggiunge niente: un "test ok" che
		segue un commento lo contraddirebbe.
		"""
		annotato = False
		while True:
			if domanda:
				print(domanda)
			scelta = key("\rr ripeti, c commenta, Invio ok\r")
			print()
			if scelta in ("r", "R"):
				if riproduci is None:
					print("Questa prova non si puo' riascoltare da qui.")
					print()
				else:
					riproduci()
			elif scelta in ("c", "C"):
				commento = dgt("\rImpressioni\r", kind="s", smin=0, smax=2000).strip()
				self.registra(titolo, commento, misura)
				annotato = True
				print("Annotato.")
				print()
			elif scelta == "\r":
				if not annotato:
					self.registra(titolo, "test superato, nessun commento", misura)
				print("Segnato come superato.")
				print()
				return "commentato" if annotato else "superato"
			elif scelta == "\x1b":
				if not annotato:
					self.registra(titolo, "chiuso senza giudizio", misura)
				print("Chiuso.")
				print()
				return "chiuso"
