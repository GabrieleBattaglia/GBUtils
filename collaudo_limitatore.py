"""Collaudo d'ascolto del limitatore e del congedo, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 24 settembre 2026 per le issue 41 e 43 di GBUtils, che toccano tutte e
due cio' che esce dal mixer condiviso.
La 41: quando piu' voci suonano insieme la somma esce dal fondo scala, e fino
alla V167 il mixer la tagliava netto, con il suono duro e sporco che Gabriele
ha sentito nel pile-up del contest di cwapu. Dalla V168 la abbassa tutta
insieme, come l'AGC di una radio. banco_limitatore.py dice che i numeri
tornano; restano le domande a cui rispondono soltanto le orecchie: se la
differenza si sente, se il suono nuovo e' pulito, e se il respiro del
fruscio, cioe' il fondo che scende quando il pile-up e' fitto, e' naturale o
disturba.
La 43: CWzator con sync tornava prima che l'ultimo elemento fosse uscito
dalle casse, e chi salutava e chiudeva il programma se lo sentiva mozzare.
Qui il saluto si suona in un programma a parte che chiude subito dopo, come
fa cwapu, una volta senza l'attesa e una volta con.
Il pile-up si suona con il mixer vero: la versione di ieri e' lo stesso mixer
con il limitatore spento, quindi fra le due cambia soltanto quello.
Dopo ogni prova si puo' scrivere un commento a caldo: finisce in
collaudo_limitatore_esiti.txt, accanto a questo file, e il file si riempie man
mano senza sovrascriversi.
Si lancia con
  python collaudo_limitatore.py
Invio fa partire cio' che e' stato appena spiegato, Escape salta.
"""
import os
import random
import subprocess
import sys
import time

import GBUtils
from collaudo_comune import Esiti
from GBUtils import Acusticator, CWzator, dgt, enter_escape, key

ESITI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collaudo_limitatore_esiti.txt")
# Le stazioni del pile-up: messaggio, parole al minuto, tono, volume, e dopo
# quanti secondi dall'inizio comincia a chiamare. I volumi sono quelli della
# misura della issue 41, da 0,85 a 0,35. Tutte al centro, come con lo stereo a
# zero nel contest: e' il caso in cui le voci si sommano di piu'.
PILE_UP = (
	("iz4apu iz4apu", 28, 450, 0.85, 0.0),
	("k1abc k1abc", 30, 540, 0.70, 0.4),
	("dl5xyz dl5xyz", 26, 620, 0.60, 0.8),
	("ja1qrp ja1qrp", 32, 710, 0.45, 1.1),
	("vk2def vk2def", 27, 830, 0.35, 1.5),
)
# La stazione sola che risponde quando il pile-up si e' sfoltito.
SOLA = ("oe3abc oe3abc", 28, 600, 0.7)
# La coda del saluto con cui cwapu chiude: e' la fine che veniva mozzata.
SALUTO = "73 tu e e"

esiti = Esiti(ESITI, "Esiti del collaudo d'ascolto del limitatore e del congedo\n"
					 "Scritti da collaudo_limitatore.py, che li aggiunge man mano.",
			  etichetta="PROVA")


def limitatore(acceso):
	"""Accende o spegne il limitatore del mixer condiviso, e lo riporta a riposo.

	Spento vuol dire il mixer di ieri: somma e taglia netto. Si fa sull'istanza
	e non sulla classe, quindi riguarda soltanto questo programma.
	"""
	mixer = GBUtils._mixer_condiviso()
	if acceso:
		mixer.__dict__.pop("_nuovo_guadagno", None)
	else:
		mixer._nuovo_guadagno = lambda picco, quanti: (1.0, False)
	mixer._guadagno = 1.0
	mixer._tenuta_residua = 0


def suona_pile_up(con_sola=False):
	"""Le cinque stazioni che chiamano insieme, e se richiesto una sola alla fine."""
	maniglie = []
	inizio = time.monotonic()
	for messaggio, wpm, tono, volume, partenza in PILE_UP:
		attesa = partenza - (time.monotonic() - inizio)
		if attesa > 0:
			time.sleep(attesa)
		maniglia, _ = CWzator(messaggio, wpm=wpm, pitch=tono, vol=volume)
		if maniglia is not None:
			maniglie.append(maniglia)
	for maniglia in maniglie:
		maniglia.wait_done(15)
	if con_sola:
		time.sleep(0.4)
		messaggio, wpm, tono, volume = SOLA
		CWzator(messaggio, wpm=wpm, pitch=tono, vol=volume, sync=True)


def ieri_e_oggi(con_sola=False, con_fruscio=False):
	"""La stessa scena due volte, prima con il mixer di ieri e poi con quello di oggi."""
	fondo = None
	for etichetta, acceso in (("Ieri, con il taglio netto.", False), ("Oggi, con il limitatore.", True)):
		print(etichetta)
		limitatore(acceso)
		if con_fruscio:
			fondo = Acusticator.ciclo(["300-900", 10.0, 0.0, 0.5], kind=6, adsr=[0, 0, 100, 0])
			time.sleep(1.5)
		suona_pile_up(con_sola)
		if fondo is not None:
			time.sleep(1.5)
			fondo.stop()
			fondo = None
		time.sleep(1.5)
	limitatore(True)
	print()


def prova_pile_up():
	print("Prova 1, il pile-up ieri e oggi. Cinque stazioni che chiamano quasi insieme, tutte al centro, con i volumi della misura della issue. Prima come suonava fino a ieri, con il taglio netto, poi con il limitatore. Ti dico ogni volta quale stai per sentire.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per saltare\r"):
		return
	ieri_e_oggi()
	esiti.esito("1, il pile-up ieri e oggi", ieri_e_oggi,
				"Cosa dirmi: se nella prima senti lo sporco duro quando le stazioni si sovrappongono, e se nella seconda le stazioni sovrapposte restano pulite. E se nella seconda senti che tutto si abbassa quando le voci si accumulano, e quanto ti disturba.")


def prova_alla_cieca():
	print("Prova 2, la stessa cosa alla cieca. Sei ascolti del pile-up, tre di ieri e tre di oggi mescolati, e dopo ognuno dici se ti e' sembrato sporco o pulito: s per sporco, p per pulito, r per risentirlo. Non ti dico la risposta fino alla fine.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per saltare\r"):
		return
	ordine = [False] * 3 + [True] * 3
	random.Random().shuffle(ordine)
	risposte = []
	for numero, acceso in enumerate(ordine, 1):
		print(f"Ascolto {numero} di 6.")
		while True:
			limitatore(acceso)
			suona_pile_up()
			risposta = key("\rSporco, pulito o risenti? s p r\r").lower()
			print()
			if risposta in ("s", "p"):
				break
		risposte.append((acceso, risposta, (risposta == "p") == acceso))
		time.sleep(0.5)
	limitatore(True)
	giuste = sum(1 for _, _, g in risposte if g)
	print(f"Risultato: {giuste} giuste su 6.")
	dettaglio = []
	for numero, (acceso, risposta, giusta) in enumerate(risposte, 1):
		print(f"{numero}: era {'oggi' if acceso else 'ieri'}, hai detto {'pulito' if risposta == 'p' else 'sporco'}, {'giusta' if giusta else 'sbagliata'}")
		dettaglio.append(f"{numero}:{'oggi' if acceso else 'ieri'}/{'pulito' if risposta == 'p' else 'sporco'}/{'ok' if giusta else 'no'}")
	print()
	esiti.esito("2, il pile-up alla cieca", None,
				"La domanda: il risultato ti convince?", misura=f"{giuste} giuste su 6. Dettaglio, era/detto/esito: " + " ".join(dettaglio))


def prova_fruscio():
	print("Prova 3, il respiro del fruscio. Sotto il pile-up c'e' un fondo di QRN come quello del contest. Quando le stazioni si accumulano il limitatore abbassa tutto insieme, fruscio compreso, e quando si sfoltiscono lascia risalire in un paio di secondi: e' l'effetto che una radio vera ha con l'AGC. Alla fine del pile-up risponde una stazione sola. Anche qui prima ieri, poi oggi.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per saltare\r"):
		return
	def ascolta():
		ieri_e_oggi(con_sola=True, con_fruscio=True)
	ascolta()
	esiti.esito("3, il respiro del fruscio", ascolta,
				"Cosa dirmi: se nella seconda senti il fruscio scendere quando il pile-up e' fitto, e se ti sembra l'AGC di una radio o un difetto. Se la stazione sola alla fine arriva al suo livello pieno o la senti ancora salire. E se preferiresti che il livello risalisse piu' in fretta o piu' piano.")


def suona_congedo(con_attesa):
	"""Il programma a parte: suona il saluto con sync e chiude subito, come cwapu."""
	if not con_attesa:
		GBUtils._mixer_condiviso().aspetta_uscita = lambda: None
	CWzator(SALUTO, wpm=25, pitch=600, vol=0.6, sync=True)
	return 0


def prova_congedo():
	print(f"Prova 4, il congedo. La coda del saluto con cui cwapu chiude, cioe' {SALUTO}, suonata da un programma che si chiude appena CWzator con sync gli restituisce il controllo. Prima senza l'attesa delle casse, come fino alla V166; poi con l'attesa della V168. Fai attenzione alle due e finali.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per saltare\r"):
		return
	def ascolta():
		for etichetta, modo in (("Senza l'attesa.", "senza"), ("Con l'attesa.", "con")):
			print(etichetta)
			subprocess.run([sys.executable, os.path.abspath(__file__), "--congedo", modo], check=False)
			time.sleep(1.5)
		print()
	ascolta()
	esiti.esito("4, il congedo", ascolta,
				"Cosa dirmi: nella prima se l'ultima e manca o arriva mozzata. Nella seconda se l'ultima e arriva intera, uguale alla e che la precede.")


PROVE = {
	"1": ("il pile-up ieri e oggi", prova_pile_up),
	"2": ("il pile-up alla cieca", prova_alla_cieca),
	"3": ("il respiro del fruscio", prova_fruscio),
	"4": ("il congedo", prova_congedo),
}


def main():
	if len(sys.argv) == 3 and sys.argv[1] == "--congedo":
		return suona_congedo(sys.argv[2] == "con")
	print("Collaudo d'ascolto del limitatore e del congedo.")
	print("Quattro prove, spiegate una per una. Nessuna parte prima del tuo Invio.")
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
	print("Prima di cominciare, metti il volume come lo tieni di solito quando fai il contest, e se puoi usa la cuffia.")
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
