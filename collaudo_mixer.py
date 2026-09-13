"""Collaudo d'ascolto del mixer, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 12 settembre 2026 per le issue 8, 30 e 1 di GBUtils.
Le misure hanno detto che il mixer condiviso va a scrittura bloccante con un
blocco di 2048 campioni invece di 256. Restano due domande a cui rispondono
soltanto le orecchie, e sono le prove di questo strumento.
La prima: il blocco piu' grande porta la latenza da 6 a 46 millisecondi, cioe'
il ritardo fra il momento in cui si preme un tasto e il momento in cui si sente
il suono. Quel ritardo si nota? Prima si ascolta sapendo cosa si sta sentendo,
poi alla cieca, perche' l'orecchio sa ingannarsi quando conosce la risposta.
La seconda: i buchi nel suono sotto carico spariscono davvero con la cura?
Si ascolta lo stesso suono mentre il programma calcola, prima come fa
Acusticator oggi e poi come farebbe il mixer nuovo.
Dopo ogni prova si puo' scrivere un commento a caldo: finisce in
collaudo_mixer_esiti.txt, accanto a questo file, insieme ai numeri che la
prova ha prodotto. Il file si riempie man mano e non si sovrascrive, quindi
le prove si possono rifare senza perdere cio' che si e' detto prima.
Si lancia con
  python collaudo_mixer.py
Invio fa partire cio' che e' stato appena spiegato, Escape salta.
"""
import os
import random
import sys
import threading
import time

import numpy as np
import sounddevice as sd
from collaudo_comune import Esiti

from GBUtils import dgt, enter_escape, key

ESITI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collaudo_mixer_esiti.txt")
FS = 44100
BLOCCO_PICCOLO = 256
BLOCCO_GRANDE = 2048
FILI_DI_CARICO = 4
# I due ritardi messi a confronto, in millesimi di secondo: quello di oggi,
# con il blocco da 256 campioni, e quello del mixer nuovo con 1024. Il blocco
# minimo che regge e' 768, cioe' diciassette millesimi, misurato anche con il
# triplo del carico; 1024 e' il passo successivo e da' il margine per i
# carichi che non sono stati provati.
SILENZIO_CORTO_MS = 6
SILENZIO_LUNGO_MS = 23

esiti = Esiti(ESITI, "Esiti del collaudo d'ascolto del mixer\n"
					 "Scritti da collaudo_mixer.py, che li aggiunge man mano.",
			  etichetta="PROVA")

def suono_breve(durata=0.12, frequenza=880.0):
	"""Un bip corto e netto, quello che serve per sentire un ritardo."""
	t = np.linspace(0, durata, int(durata * FS), endpoint=False, dtype=np.float32)
	onda = np.sin(2 * np.pi * frequenza * t).astype(np.float32)
	# Attacco e coda molto brevi, per non avere schiocchi ai bordi.
	rampa = int(0.002 * FS)
	onda[:rampa] *= np.linspace(0, 1, rampa, dtype=np.float32)
	onda[-rampa:] *= np.linspace(1, 0, rampa, dtype=np.float32)
	return np.column_stack((onda, onda)) * 0.5

def suono_lungo(durata=2.5, frequenza=440.0):
	"""Una nota tenuta: e' su questa che i buchi si sentono."""
	t = np.linspace(0, durata, int(durata * FS), endpoint=False, dtype=np.float32)
	onda = np.sin(2 * np.pi * frequenza * t).astype(np.float32)
	rampa = int(0.01 * FS)
	onda[:rampa] *= np.linspace(0, 1, rampa, dtype=np.float32)
	onda[-rampa:] *= np.linspace(1, 0, rampa, dtype=np.float32)
	return np.column_stack((onda, onda)) * 0.4

def riproduci(buffer, blocco):
	"""Scrittura bloccante, la forma scelta per il mixer nuovo."""
	stream = sd.OutputStream(samplerate=FS, channels=2, dtype="float32",
							 blocksize=blocco, latency="low")
	with stream:
		for inizio in range(0, len(buffer), blocco):
			pezzo = buffer[inizio:inizio + blocco]
			if len(pezzo) < blocco:
				pezzo = np.vstack((pezzo, np.zeros((blocco - len(pezzo), 2), dtype=np.float32)))
			stream.write(pezzo)

def riproduci_a_callback(buffer, blocco):
	"""La forma di Acusticator oggi, che serve solo come termine di paragone."""
	stato = {"pos": 0, "fine": threading.Event()}
	def callback(outdata, frames, tempo, stato_audio):
		da, a = stato["pos"], min(stato["pos"] + frames, len(buffer))
		outdata.fill(0.0)
		if a > da:
			outdata[:a - da] = buffer[da:a]
		stato["pos"] = a
		if a >= len(buffer):
			stato["fine"].set()
	stream = sd.OutputStream(samplerate=FS, channels=2, dtype="float32",
							 blocksize=blocco, latency="low", callback=callback)
	with stream:
		stato["fine"].wait(timeout=len(buffer) / FS + 2.0)

def carico(secondi, quanti=FILI_DI_CARICO):
	"""Il programma che calcola mentre suona, come fa Terminal Beast."""
	fine = time.monotonic() + secondi
	def lavora():
		while time.monotonic() < fine:
			sum(i * i for i in range(2000))
	for _ in range(quanti):
		threading.Thread(target=lavora, daemon=True).start()

def aspetta_tasto_e_suona(blocco):
	"""Aspetta un tasto e suona subito dopo: e' la prova della latenza."""
	key("\rPremi un tasto\r")
	# Nessuna stampa fra il tasto e il suono: qualunque cosa aggiungerebbe
	# ritardo a carico della prova invece che del mixer.
	riproduci(suono_breve(), blocco)

def prova_latenza_dichiarata():
	print("Prova 1, la latenza dichiarata. Premerai un tasto sei volte. Le prime tre suonano con il ritardo di oggi, sei millesimi di secondo. Le altre tre con quello nuovo, quarantasei millesimi. Ogni volta ti dico prima quale stai per sentire.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per saltare\r"):
		return
	def ascolta():
		for etichetta, blocco in (("oggi, sei millesimi", BLOCCO_PICCOLO), ("nuovo, quarantasei millesimi", BLOCCO_GRANDE)):
			for numero in (1, 2, 3):
				print(f"{etichetta}, {numero} di 3.")
				aspetta_tasto_e_suona(blocco)
				time.sleep(0.4)
		print()
	ascolta()
	esiti.esito("1, la latenza dichiarata", ascolta,
				"Se non hai sentito differenza, la latenza nuova va bene e la prova alla cieca lo confermera'.")

def prova_latenza_alla_cieca():
	print("Prova 2, la stessa cosa alla cieca. Dieci volte: premi un tasto, senti il bip, e subito dopo dici se era il ritardo corto o quello lungo. Premi c per corto, l per lungo. Non ti dico la risposta fino alla fine.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per saltare\r"):
		return
	# Cinque corte e cinque lunghe, mescolate: con il sorteggio libero poteva
	# capitarne sette di un tipo, e allora chi rispondeva sempre allo stesso
	# modo faceva sette su dieci senza aver distinto niente. E' successo il
	# 12 settembre 2026, ed e' il motivo per cui questa prova e' cambiata.
	ordine = [True] * 5 + [False] * 5
	random.Random().shuffle(ordine)
	giusti, sbagliati = 0, 0
	risposte = []
	for numero, corto in enumerate(ordine, 1):
		print(f"Prova {numero} di 10.")
		aspetta_tasto_e_suona(BLOCCO_PICCOLO if corto else BLOCCO_GRANDE)
		while True:
			risposta = key("\rCorto o lungo? c oppure l\r")
			if risposta in ("c", "l", "C", "L"):
				break
		print()
		indovinato = (risposta.lower() == "c") == corto
		giusti += indovinato
		sbagliati += not indovinato
		risposte.append((corto, risposta.lower(), indovinato))
		time.sleep(0.3)
	print()
	# Il totale da solo inganna: chi risponde sempre allo stesso modo prende il
	# punteggio che il sorteggio gli regala. Cio' che conta e' se ha
	# riconosciuto le corte quando erano corte e le lunghe quando erano lunghe,
	# e le due cose vanno guardate separate.
	corte_giuste = sum(1 for c, r, _ in risposte if c and r == "c")
	lunghe_giuste = sum(1 for c, r, _ in risposte if not c and r == "l")
	dette_corte = sum(1 for _, r, _ in risposte if r == "c")
	print(f"Risultato: {giusti} giuste su 10.")
	print(f"Corte riconosciute {corte_giuste} su 5, lunghe riconosciute {lunghe_giuste} su 5.")
	if dette_corte in (0, 10):
		print("Hai risposto sempre allo stesso modo, quindi non hai distinto niente: il ritardo nuovo non si sente, e il punteggio qui sopra e' solo il conto di come e' caduto il sorteggio.")
	elif corte_giuste + lunghe_giuste >= 9:
		print("Li distingui davvero: il ritardo nuovo si sente, e va deciso cosa farne.")
	elif corte_giuste >= 4 and lunghe_giuste >= 4:
		print("Li distingui quasi sempre: conviene rifare la prova per esserne sicuri.")
	else:
		print("Sei nel caso: il ritardo nuovo non si sente, e il blocco grande si puo' adottare senza pensieri.")
	print()
	dettaglio = []
	for numero, (corto, risposta, indovinato) in enumerate(risposte, 1):
		print(f"{numero}: era {'corto' if corto else 'lungo'}, hai detto {'corto' if risposta == 'c' else 'lungo'}, {'giusta' if indovinato else 'sbagliata'}")
		dettaglio.append(f"{numero}:{'corto' if corto else 'lungo'}/{'corto' if risposta == 'c' else 'lungo'}/{'ok' if indovinato else 'no'}")
	print()
	esiti.esito("2, la latenza alla cieca", None,
		"La domanda: il risultato ti convince?", misura=
		f"{giusti} giuste su 10, corte riconosciute {corte_giuste} su 5, lunghe {lunghe_giuste} su 5. "
		f"Dettaglio, era/detto/esito: " + " ".join(dettaglio))

def prova_buchi():
	print("Prova 3, i buchi nel suono. Una nota tenuta di due secondi e mezzo, mentre il programma calcola come fa Terminal Beast quando annuncia una scuderia nuova. La sentirai tre volte come funziona oggi e tre volte come funzionerebbe dopo la cura, alternate a coppie.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per saltare\r"):
		return
	def ascolta():
		for giro in (1, 2, 3):
			for etichetta, funzione, blocco in (("oggi", riproduci_a_callback, BLOCCO_PICCOLO), ("dopo la cura", riproduci, BLOCCO_GRANDE)):
				print(f"Coppia {giro} di 3, {etichetta}.")
				nota = suono_lungo()
				carico(len(nota) / FS + 0.5)
				time.sleep(0.4)
				funzione(nota, blocco)
				time.sleep(1.2)
		print()
	ascolta()
	esiti.esito("3, i buchi sotto carico", ascolta,
				"Nella prima di ogni coppia dovresti sentire il suono spezzettarsi. Nella seconda no.")

PROVE = {
	"1": ("la latenza dichiarata", None),
	"2": ("la latenza alla cieca", None),
	"3": ("i buchi sotto carico", None),
	"4": ("il ritardo come silenzio fra due note", None),
}


def coppia_di_note(silenzio_ms, durata_nota=0.1, frequenza=880.0):
	"""Due bip separati da un silenzio della lunghezza voluta."""
	nota = suono_breve(durata_nota, frequenza)
	quiete = np.zeros((int(silenzio_ms / 1000 * FS), 2), dtype=np.float32)
	return np.vstack((nota, quiete, nota))

def prova_silenzio_alla_cieca():
	print("Prova 4, il ritardo come silenzio. La proposta e' tua: invece di premere un tasto e aspettare il suono, senti due note separate da un silenzio, e dici se il silenzio era corto o lungo. Il corto vale sei millesimi, cioe' il ritardo di oggi, e il lungo ventitre', che e' quello del mixer nuovo: sono meno della meta' della differenza di prima, perche' le misure hanno detto che non serve arrivare a quarantasei. Messi in fila fra due note il confronto e' piu' facile che con il tasto.")
	print()
	print("Prima tre coppie dichiarate, per farti l'orecchio: corto, lungo, corto. Poi dieci alla cieca, cinque per parte mescolate.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per saltare\r"):
		return
	for etichetta, silenzio in (("corto", SILENZIO_CORTO_MS), ("lungo", SILENZIO_LUNGO_MS), ("corto", SILENZIO_CORTO_MS)):
		print(f"Silenzio {etichetta}.")
		riproduci(coppia_di_note(silenzio), BLOCCO_GRANDE)
		time.sleep(0.8)
	print()
	print("Ora le dieci alla cieca. Premi c per corto, l per lungo. Se vuoi risentire la coppia prima di rispondere, premi r.")
	print()
	if not enter_escape("\rInvio quando sei pronto, Escape per saltare\r"):
		return
	ordine = [True] * 5 + [False] * 5
	random.Random().shuffle(ordine)
	risposte = []
	for numero, corto in enumerate(ordine, 1):
		print(f"Coppia {numero} di 10.")
		while True:
			riproduci(coppia_di_note(SILENZIO_CORTO_MS if corto else SILENZIO_LUNGO_MS), BLOCCO_GRANDE)
			risposta = key("\rCorto, lungo o risenti? c l r\r")
			print()
			if risposta.lower() in ("c", "l"):
				break
		indovinato = (risposta.lower() == "c") == corto
		risposte.append((corto, risposta.lower(), indovinato))
		time.sleep(0.4)
	giusti = sum(1 for _, _, i in risposte if i)
	corte_giuste = sum(1 for c, r, _ in risposte if c and r == "c")
	lunghe_giuste = sum(1 for c, r, _ in risposte if not c and r == "l")
	dette_corte = sum(1 for _, r, _ in risposte if r == "c")
	print()
	print(f"Risultato: {giusti} giuste su 10.")
	print(f"Corte riconosciute {corte_giuste} su 5, lunghe riconosciute {lunghe_giuste} su 5.")
	if dette_corte in (0, 10):
		print("Hai risposto sempre allo stesso modo, quindi non hai distinto niente.")
	elif corte_giuste + lunghe_giuste >= 9:
		print("Li distingui anche cosi': diciassette millesimi di silenzio sono dentro la tua risoluzione, e allora conviene scendere al blocco piu' piccolo che regge.")
	elif corte_giuste >= 4 and lunghe_giuste >= 4:
		print("Li distingui quasi sempre.")
	else:
		print("Sei nel caso: nemmeno nel confronto diretto la differenza si coglie.")
	print()
	dettaglio = []
	for numero, (corto, risposta, indovinato) in enumerate(risposte, 1):
		print(f"{numero}: era {'corto' if corto else 'lungo'}, hai detto {'corto' if risposta == 'c' else 'lungo'}, {'giusta' if indovinato else 'sbagliata'}")
		dettaglio.append(f"{numero}:{'corto' if corto else 'lungo'}/{'corto' if risposta == 'c' else 'lungo'}/{'ok' if indovinato else 'no'}")
	print()
	esiti.esito("4, il ritardo come silenzio fra due note", None,
		"La domanda: il risultato ti convince?", misura=
		f"{giusti} giuste su 10, corte riconosciute {corte_giuste} su 5, lunghe {lunghe_giuste} su 5. "
		f"Dettaglio, era/detto/esito: " + " ".join(dettaglio))

def main():
	PROVE["1"] = (PROVE["1"][0], prova_latenza_dichiarata)
	PROVE["2"] = (PROVE["2"][0], prova_latenza_alla_cieca)
	PROVE["3"] = (PROVE["3"][0], prova_buchi)
	PROVE["4"] = (PROVE["4"][0], prova_silenzio_alla_cieca)
	print("Collaudo d'ascolto del mixer.")
	print("Tre prove, spiegate una per una. Nessuna parte prima del tuo Invio.")
	print()
	for numero, (titolo, _) in PROVE.items():
		print(f"{numero}: {titolo}")
	print()
	print("Scegli quali fare: i numeri attaccati, per esempio 14 per la prima e la quarta, oppure Invio per tutte.")
	scelta = dgt("\rQuali prove\r", kind="s", smin=0, smax=10).strip()
	volute = [n for n in PROVE if n in scelta] if scelta else list(PROVE)
	if not volute:
		print("Nessuna prova scelta, esco.")
		return 0
	print()
	print("Prima di cominciare, alza il volume come lo tieni di solito: le differenze da sentire sono piccole.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per uscire\r"):
		return 0
	for numero in volute:
		PROVE[numero][1]()
	print("Collaudo finito. Grazie per le orecchie.")
	if os.path.exists(ESITI):
		print(f"Gli esiti stanno in {os.path.basename(ESITI)}, accanto a questo programma.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
