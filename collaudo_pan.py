"""Collaudo d'ascolto dello spostamento di panorama di Acusticator.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 13 settembre 2026 con la issue 18.
Il banco dice che i conti tornano: con pan a zero non cambia un campione su 243
preset intonati, il panorama non esce mai dai bordi e il movimento si stringe
solo quanto serve. Cio' che il banco non sa dire e' se all'orecchio la cosa
funzioni, cioe' se un suono spostato si senta davvero dove lo si e' messo e se
un suono che si muove continui a muoversi invece di appiattirsi.
Tutto a coppie: prima si sente il suono com'e', poi lo stesso suono spostato.
Tutte le combinazioni fra il panorama interno alla quartina, che puo' essere
fermo al centro, fermo fuori centro o in portamento nei due versi, e lo
spostamento generale, che puo' essere fermo a sinistra o a destra o in
portamento nei due versi. Gli incroci contrari, cioe' quartina che va a destra
dentro un generale che va a sinistra, sono il caso piu' interessante.
Tutto suona al trenta per cento di volume.
Dopo ogni gruppo si scrive cosa si e' sentito, e finisce in
collaudo_pan_esiti.txt accanto a questo file.
Si lancia con
  python collaudo_pan.py
"""
import os
import sys
import time

from GBUtils import Acusticator, dgt, enter_escape

QUI = os.path.dirname(os.path.abspath(__file__))
ESITI = os.path.join(QUI, "collaudo_pan_esiti.txt")
VOL = 0.30
DURATA = 1.6
ADSR = [3.0, 0.0, 100.0, 8.0]
# Gli spostamenti generali su cui si ascolta, gli stessi per ogni quartina.
GENERALI = [
	(-0.7, "fermo a sinistra, -0,7"),
	(0.7, "fermo a destra, +0,7"),
	((-1.0, 1.0), "portamento da sinistra a destra"),
	((1.0, -1.0), "portamento da destra a sinistra"),
]
# Le quartine di partenza: il panorama che il suono ha di suo.
QUARTINE = [
	(0.0, "ferma al centro"),
	(-0.5, "ferma fuori centro, a -0,5"),
	((-1.0, 1.0), "in portamento da sinistra a destra"),
	((1.0, -1.0), "in portamento da destra a sinistra"),
]

def registra(titolo, commento):
	nuovo = not os.path.exists(ESITI)
	with open(ESITI, "a", encoding="utf-8") as f:
		if nuovo:
			f.write("Esiti del collaudo d'ascolto dello spostamento di panorama\n")
			f.write("Scritti da collaudo_pan.py, che li aggiunge man mano.\n")
		f.write(f"\nGRUPPO: {titolo}\n")
		f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M')}\n")
		f.write(f"Commento di Gabriele: {commento if commento else 'nessuno'}\n")

def chiedi_commento(titolo):
	print("Scrivi cosa hai sentito e batti Invio. Invio da solo se non hai niente da dire.")
	commento = dgt("\rImpressioni\r", kind="s", smin=0, smax=2000)
	registra(titolo, commento.strip())
	print("Annotato.")
	print()

def gruppo(titolo, quante):
	print(f"Gruppo: {titolo}. Sono {quante} coppie, cioe' {quante * 2} ascolti.")
	return enter_escape("\rInvio per questo gruppo, Escape per saltarlo\r")

def coppia(etichetta, score, spostamento, kind=1):
	"""Prima il suono com'e', poi lo stesso spostato."""
	print(f"  prima, senza spostamento: {etichetta}")
	Acusticator(score, kind=kind, adsr=ADSR, sync=True)
	time.sleep(0.35)
	print(f"  dopo, spostamento {spostamento}")
	Acusticator(score, kind=kind, adsr=ADSR, sync=True, pan=spostamento)
	time.sleep(0.7)

def coppia_preset(nome, spostamento):
	print(f"  prima, senza spostamento: {nome}")
	Acusticator.play(nome, sync=True, volume=VOL)
	time.sleep(0.35)
	print(f"  dopo, spostamento {spostamento}")
	Acusticator.play(nome, sync=True, volume=VOL, pan=spostamento)
	time.sleep(0.7)

def main():
	print("Collaudo d'ascolto dello spostamento di panorama.")
	print()
	print("Lo spostamento non cancella il panorama che il suono ha di suo: lo sposta, e lo stringe soltanto")
	print("quanto serve a non uscire dai bordi. Un suono che vola da sinistra a destra, spostato a destra,")
	print("deve continuare a volare in uno spazio piu' stretto, non appiattirsi contro il bordo.")
	print()
	print("Tutto a coppie: prima il suono com'e', poi lo stesso spostato. Volume al trenta per cento.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per uscire\r"):
		return 0
	# I quattro gruppi della matrice: ogni panorama di quartina contro ogni
	# spostamento generale.
	for interno, come in QUARTINE:
		titolo = f"quartina {come}"
		if not gruppo(titolo, len(GENERALI)):
			continue
		print(f"  Il suono di partenza e' un la tenuto, con panorama {come}.")
		for spostamento, descrizione in GENERALI:
			print(f"  {descrizione}")
			coppia(f"quartina {come}", ["a4", DURATA, interno, VOL], spostamento)
		print()
		if interno == 0.0:
			print("  La domanda: il suono va dove dice lo spostamento, e nei due portamenti attraversa tutto il fronte?")
		elif isinstance(interno, tuple):
			print("  La domanda: il volo si sente ancora come un volo, anche quando lo spazio si stringe?")
			print("  E negli incroci contrari, cioe' quartina e generale che vanno da parti opposte, cosa succede?")
		else:
			print("  La domanda: il suono si sposta di quanto si e' chiesto, partendo da dove stava?")
		print()
		chiedi_commento(titolo)
	# I preset veri della collezione, quelli la cui identita' e' il movimento.
	if gruppo("i preset veri, quelli che si muovono", 6):
		print("  volo_radente e passaggio_veloce percorrono tutto il fronte: spostarli e' il caso difficile.")
		for nome in ("volo_radente", "passaggio_veloce"):
			for spostamento in (0.6, -0.6, (1.0, -1.0)):
				print(f"  {nome}, spostamento {spostamento}")
				coppia_preset(nome, spostamento)
		print()
		print("  La domanda: il volo resta un volo, spostato di lato? E il verso e' quello che ti aspetti?")
		print()
		chiedi_commento("i preset veri che si muovono")
	# Un preset fermo al centro, che e' il caso d'uso di gabryscola.
	if gruppo("un preset fermo, messo a sinistra e a destra", 3):
		print("  E' il caso per cui la issue e' nata: lo stesso suono a sinistra quando lo fa il giocatore")
		print("  e a destra quando lo fa il calcolatore. gabryscola userebbe piu' o meno 0,6.")
		for spostamento in (-0.6, 0.6, (-1.0, 1.0)):
			print(f"  spostamento {spostamento}")
			coppia_preset("conferma", spostamento)
		print()
		print("  La domanda: i due lati si distinguono bene senza che il suono perda corpo?")
		print()
		chiedi_commento("un preset fermo messo di lato")
	# I casi limite, dove lo spazio finisce.
	if gruppo("i casi limite, dove lo spazio finisce", 3):
		print("  Con lo spostamento al bordo esatto non resta spazio per il movimento, che si annulla:")
		print("  il suono si sente tutto da un lato. E' voluto, ma va sentito.")
		print("  spostamento +1, tutto a destra")
		coppia("quartina che vola da sinistra a destra", ["a4", DURATA, (-1.0, 1.0), VOL], 1.0)
		print("  spostamento -1, tutto a sinistra")
		coppia("quartina che vola da sinistra a destra", ["a4", DURATA, (-1.0, 1.0), VOL], -1.0)
		print("  Due portamenti uguali e opposti si annullano: il suono resta fermo al centro.")
		print("  quartina da sinistra a destra, generale da +0,5 a -0,5")
		coppia("quartina che vola da sinistra a destra", ["a4", DURATA, (-1.0, 1.0), VOL], (0.5, -0.5))
		print()
		print("  La domanda: nei primi due il suono sta davvero tutto da un lato, e nel terzo sta fermo al centro?")
		print()
		chiedi_commento("i casi limite")
	Acusticator.close()
	print("Collaudo finito. Grazie per le orecchie.")
	if os.path.exists(ESITI):
		print(f"Gli esiti stanno in {os.path.basename(ESITI)}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
