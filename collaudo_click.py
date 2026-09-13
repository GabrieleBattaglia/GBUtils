"""Collaudo d'ascolto dei click nella collezione, issue 34.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 13 settembre 2026.
Questo collaudo non tocca niente: GBUtils resta com'e', la collezione resta
com'e'. La versione corretta viene costruita qui dentro, nel momento in cui la
si ascolta, e sparisce appena finita.
La misura dice che 173 preset intonati su 243 hanno almeno una delle due cause
del click: il gradino, cioe' l'inviluppo che non arriva a zero al confine, e la
pendenza, cioe' l'inviluppo che a zero ci arriva ma troppo in fretta. Quello
che la misura non sa dire e' se questo si senta, e se valga la pena curarlo.
Lo decide l'orecchio, e per questo si ascolta prima di decidere.
La correzione provata qui e' la minima possibile: un inviluppo che chiede meno
di N millesimi di rampa ne riceve N, e il minimo si accorcia da solo quando la
nota e' troppo breve, esattamente come gia' fa la sfumatura di quattro
millesimi dei rumori. I preset con un inviluppo gia' gentile non vengono
toccati.
Verificato prima di scrivere questo: ricostruire il suono nota per nota, che e'
come la versione corretta viene costruita, da un risultato identico campione
per campione alla sintesi normale su tutti e 243 i preset intonati. Quindi
l'unica differenza che si sente e' la rampa, e non il modo di costruirlo.
Tutto al trenta per cento di volume.
In fondo a ogni gruppo si sceglie con un tasto: r riascolta il gruppo intero,
c apre il posto dove scrivere le impressioni, Invio lo da' per superato, Escape
lo chiude senza annotare niente. Quello che si scrive finisce in
collaudo_click_esiti.txt accanto a questo file.
Si lancia con
  python collaudo_click.py
"""
import os
import sys
import time

import numpy as np

from GBUtils import Acusticator, _sintetizza, dgt, enter_escape, key

QUI = os.path.dirname(os.path.abspath(__file__))
ESITI = os.path.join(QUI, "collaudo_click_esiti.txt")
FS = 44100
VOL = 0.30
# I gruppi, scelti dalla misura del 13 settembre 2026.
GRADINI = ["sirena_d_allarme_9", "vittoria", "gabryscola_sconfitta", "star_trek_call", "morto"]
SECCHI = ["colpo_d_impatto_1", "il_gioco_alto", "espelli", "eliminato", "gabryscola_gioca_carta", "fide_pronto"]
PENDENZE = ["melodia_del_campanello_1", "jingle_perde_1", "lista"]
CONTROLLO = ["jingle_missione_fallita", "arpeggio_pensoso", "super_salita", "pokermachine_record_perdita"]

def registra(titolo, commento):
	nuovo = not os.path.exists(ESITI)
	with open(ESITI, "a", encoding="utf-8") as f:
		if nuovo:
			f.write("Esiti del collaudo d'ascolto dei click, issue 34\n")
			f.write("Scritti da collaudo_click.py, che li aggiunge man mano.\n")
		f.write(f"\nGRUPPO: {titolo}\n")
		f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M')}\n")
		f.write(f"Commento di Gabriele: {commento if commento else 'nessuno'}\n")

def esito(titolo, riproduci, domanda):
	"""Chiude un gruppo: si riascolta, si commenta o si passa oltre.

	Torna al menu dopo ogni scelta, cosi' si puo' riascoltare, poi commentare,
	poi riascoltare ancora, e chiudere solo quando si e' pronti.
	"""
	annotato = False
	while True:
		print(domanda)
		scelta = key("\rr ripeti, c commenta, Invio ok\r")
		print()
		if scelta in ("r", "R"):
			riproduci()
		elif scelta in ("c", "C"):
			commento = dgt("\rImpressioni\r", kind="s", smin=0, smax=2000).strip()
			registra(titolo, commento)
			annotato = True
			print("Annotato.")
			print()
		elif scelta == "\r":
			if not annotato:
				registra(titolo, "test superato, nessun commento")
			print("Segnato come superato.")
			print()
			return
		elif scelta == "\x1b":
			if not annotato:
				registra(titolo, "chiuso senza giudizio")
			print("Chiuso.")
			print()
			return

def gruppo(titolo, quante):
	print(f"Gruppo: {titolo}. Sono {quante} coppie, cioe' {quante * 2} ascolti.")
	return enter_escape("\rInvio per questo gruppo, Escape per saltarlo\r")

def corretto(nome, minimo_ms):
	"""Il preset con la rampa minima, costruito qui e non salvato da nessuna
	parte. Con minimo a zero non cambia niente: serve alla prova di controllo."""
	score, kind, adsr = Acusticator.preset(nome)
	if not score:
		return None
	a_pct, _, _, r_pct = adsr if adsr else [0.002, 0.0, 100.0, 0.002]
	minimo = round(FS * minimo_ms / 1000.0)
	pezzi = []
	for i in range(0, len(score) - 3, 4):
		pezzo = _sintetizza(score[i:i + 4], kind, adsr, FS)
		if pezzo is None or pezzo.size == 0:
			continue
		quanti = min(minimo, pezzo.shape[0] // 4)
		if quanti > 0:
			# La rampa si allunga solo dove l'inviluppo e' piu' corto del
			# minimo: dove e' gia' gentile, non si tocca niente.
			if round(a_pct / 100.0 * pezzo.shape[0]) < quanti:
				pezzo[:quanti] *= np.linspace(0.0, 1.0, quanti, dtype=np.float32)[:, None]
			if round(r_pct / 100.0 * pezzo.shape[0]) < quanti:
				pezzo[-quanti:] *= np.linspace(1.0, 0.0, quanti, dtype=np.float32)[:, None]
		pezzi.append(pezzo)
	return np.concatenate(pezzi) if pezzi else None

def coppia(nome, minimo_ms, etichetta_dopo=None):
	print(f"  {nome}, com'e' adesso")
	Acusticator.play(nome, sync=True)
	time.sleep(0.45)
	print(f"  {nome}, {etichetta_dopo or f'con la rampa da {minimo_ms} millesimi'}")
	buffer = corretto(nome, minimo_ms)
	if buffer is None:
		print("  non riesco a costruirlo")
	else:
		Acusticator.riproduci(buffer, fs=FS, sync=True)
	time.sleep(0.8)

def scala(nome):
	"""Lo stesso suono com'e' e poi con tre rampe diverse."""
	print(f"  {nome}, com'e' adesso")
	Acusticator.play(nome, sync=True)
	time.sleep(0.45)
	for minimo in (0.5, 1.0, 2.0):
		print(f"  {nome}, rampa da {minimo} millesimi")
		buffer = corretto(nome, minimo)
		if buffer is not None:
			Acusticator.riproduci(buffer, fs=FS, sync=True)
		time.sleep(0.45)
	print()

def main():
	print("Collaudo d'ascolto dei click nella collezione.")
	print()
	print("Niente viene modificato: GBUtils e la collezione restano come sono. La versione corretta")
	print("nasce qui dentro nel momento in cui la senti e sparisce appena finita.")
	print()
	print("Ogni prova e' una coppia: prima il preset com'e' adesso, poi lo stesso con la rampa minima.")
	print("La domanda e' sempre la stessa: senti una differenza, e se la senti, quale delle due preferisci?")
	print()
	print("In fondo a ogni gruppo: r riascolta tutto il gruppo, c apre il posto dove scrivere,")
	print("Invio lo da' per superato, Escape lo chiude senza annotare.")
	print()
	print("Tutto al trenta per cento di volume.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per uscire\r"):
		return 0
	# Il volume si abbassa sul mixer e non passandolo a play: quello
	# sostituirebbe la base su cui si applicano gli scarti scritti nei preset,
	# e i sette che hanno uno scarto di -0,3 o piu' basso diventerebbero muti.
	prima_del_collaudo = Acusticator.stato()["volume"]
	Acusticator.setup(volume=VOL)
	titolo = "i gradini grossi sui suoni lunghi"
	if gruppo(titolo, len(GRADINI)):
		print("  Questi cinque hanno un gradino vero: il segnale salta da un valore pieno al silenzio in un")
		print("  campione solo. Se il click esiste, e' qui che si deve sentire.")
		def ascolta_gradini():
			for nome in GRADINI:
				coppia(nome, 1.0)
			print()
		ascolta_gradini()
		esito(titolo, ascolta_gradini,
			  "  La domanda: nella prima di ogni coppia senti uno schiocco che nella seconda non c'e'?")
	titolo = "i colpi secchi e i tic corti"
	if gruppo(titolo, len(SECCHI)):
		print("  Qui il rischio e' l'opposto: questi suoni devono essere secchi, e la rampa potrebbe")
		print("  ammorbidirli. Sono brevi, da cinquanta a cento millesimi, quindi un millesimo di rampa")
		print("  pesa fra l'uno e il due per cento della loro durata.")
		def ascolta_secchi():
			for nome in SECCHI:
				coppia(nome, 1.0)
			print()
		ascolta_secchi()
		esito(titolo, ascolta_secchi,
			  "  La domanda: la seconda di ogni coppia ha perso mordente, o e' identica?")
	titolo = "i lunghi con pendenza ripida"
	if gruppo(titolo, len(PENDENZE)):
		print("  Questi non hanno nessun gradino: l'inviluppo arriva a zero. Ma ci arriva in meno di un")
		print("  decimo di millesimo, e secondo la misura anche quello si sente.")
		def ascolta_pendenze():
			for nome in PENDENZE:
				coppia(nome, 1.0)
			print()
		ascolta_pendenze()
		esito(titolo, ascolta_pendenze,
			  "  La domanda: qui una differenza c'e', oppure e' solo matematica?")
	titolo = "quanto deve essere lunga la rampa"
	if gruppo(titolo, 3):
		print("  Due suoni, uno con il gradino piu' grosso della collezione e uno che deve restare secco,")
		print("  sentiti com'e' adesso e poi con tre rampe diverse: mezzo millesimo, uno e due.")
		print("  Serve a scegliere il valore, se decidiamo di metterlo.")
		def ascolta_scala():
			for nome in ("sirena_d_allarme_9", "colpo_d_impatto_1"):
				scala(nome)
		ascolta_scala()
		esito(titolo, ascolta_scala,
			  "  La domanda: da quale valore in poi il click sparisce, e da quale in poi il colpo si ammorbidisce?")
	titolo = "l'ultimo gruppo"
	if gruppo(titolo, len(CONTROLLO)):
		print("  Quattro preset lunghi. Stessa forma delle prove di prima: prima e dopo.")
		def ascolta_controllo():
			for nome in CONTROLLO:
				coppia(nome, 0.0, etichetta_dopo="la seconda volta")
			print()
		ascolta_controllo()
		esito(titolo, ascolta_controllo,
			  "  La domanda: senti differenza fra le due di ogni coppia?")
		print("Una cosa che non ti avevo detto: in quest'ultimo gruppo le due di ogni coppia erano")
		print("identiche. Nessuna rampa, nessuna correzione, lo stesso suono due volte, e la seconda")
		print("passata per la stessa strada che costruisce le versioni corrette degli altri gruppi.")
		print("Serviva a sapere quanto fidarsi delle differenze sentite prima. Se qui non hai sentito")
		print("niente, allora le differenze degli altri gruppi sono vere.")
		print()
		commento = dgt("\rVuoi aggiungere qualcosa\r", kind="s", smin=0, smax=2000)
		registra("l'ultimo gruppo, dopo aver saputo che era di controllo", commento.strip())
		print()
	Acusticator.setup(volume=prima_del_collaudo)
	Acusticator.close()
	print("Collaudo finito. Grazie per le orecchie.")
	print("Non e' stato modificato niente: la collezione e GBUtils sono come prima.")
	if os.path.exists(ESITI):
		print(f"Gli esiti stanno in {os.path.basename(ESITI)}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
