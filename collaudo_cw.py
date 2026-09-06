# Collaudo guidato di CWzator, prove d'ascolto.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' auto).
# 06/09/2026: nato per il refactoring di fase 1, blocchi 1, 2 e 3.

"""Conduce le prove d'ascolto una alla volta e ne registra gli esiti.

Si lancia con python collaudo_cw.py e si guida con un tasto solo. Per ogni
prova spiega cosa si sta per sentire e cosa bisogna osservare, poi aspetta.
Dopo l'ascolto si puo' riascoltare quante volte si vuole, lasciare un
commento oppure dichiarare la prova superata. Gli esiti finiscono in
collaudo_cw_esiti.txt, accanto a questo file, e il lavoro si puo'
interrompere e riprendere: le prove gia' chiuse non vengono riproposte.

Le prove che chiedono velocita' oltre la soglia di lettura si ascoltano
rallentate: l'audio e' generato alla velocita' vera e riprodotto a una
frequenza di campionamento ridotta, quindi le proporzioni fra punto, linea
e spazi restano esatte e cambia soltanto l'altezza della nota.
"""

import os
import sys
import time

import numpy as np
import sounddevice as sd

from GBUtils import CWzator, dgt, key

CARTELLA = os.path.dirname(os.path.abspath(__file__))
ESITI = os.path.join(CARTELLA, "collaudo_cw_esiti.txt")
PESI_GABRIELE = {"l": 32, "s": 53, "p": 34}
VOLUME = 0.4


def suona(msg, attesa=0.35, **kw):
	"""Manda un messaggio e aspetta che finisca, poi lascia un respiro."""
	kw.setdefault("vol", VOLUME)
	_plo, rwpm = CWzator(msg=msg, sync=True, **kw)
	time.sleep(attesa)
	return rwpm


def riproduci(campioni, fs):
	"""Manda un array su uno stream aperto per l'occasione e aspetta che sia
	uscito davvero. Quando l'ultima scrittura ritorna, nel buffer del
	dispositivo resta ancora fino a un tempo pari alla latenza: chiudere li'
	taglia la coda. Con sd.play e l'attesa bloccante succedeva proprio questo,
	e a 120 wpm rallentato tre volte mangiava l'ultima linea, tanto che le
	kappa si sentivano come enne."""
	stream = sd.OutputStream(samplerate=fs, channels=1, dtype="int16",
							 blocksize=256, latency="low")
	stream.start()
	try:
		avvio = time.monotonic()
		for i in range(0, campioni.size, 256):
			stream.write(campioni[i:i + 256])
		fine = avvio + stream.latency + campioni.size / float(fs) + 0.005
		residuo = fine - time.monotonic()
		if residuo > 0:
			time.sleep(residuo)
		stream.abort()
	finally:
		stream.close()


def suona_rallentato(msg, fattore=3, **kw):
	"""Genera alla velocita' vera e riproduce rallentata di fattore volte.
	Le durate restano in proporzione fra loro, scende soltanto il tono."""
	kw.setdefault("vol", VOLUME)
	plo, rwpm = CWzator(msg=msg, play=False, **kw)
	if plo is None:
		return None
	fs = kw.get("fs", 44100)
	riproduci(plo.audio_data, int(fs / fattore))
	time.sleep(0.35)
	return rwpm


def prova_coda():
	print("Sei trasmissioni brevi, tutte con una linea in fondo tranne l'ultima.")
	for msg, spiega in (("k", "kappa, linea punto linea"),
						("t", "una linea sola"),
						("m", "emme, due linee"),
						("o", "o, tre linee"),
						("cq de iz4apu k", "un messaggio intero, finisce in kappa"),
						("e", "un punto solo, il suono piu' corto che ci sia")):
		print("   " + spiega)
		suona(msg, wpm=37, **PESI_GABRIELE)


def prova_schiocco():
	print("Lo stesso messaggio con dissolvenze sempre piu' lunghe, a 60 wpm.")
	print("Prima della correzione, dai 20 millesimi in su la dissolvenza")
	print("spariva del tutto e restava uno schiocco secco.")
	for ms in (1, 5, 20, 30):
		print(f"   dissolvenza da {ms} millesimi")
		suona("paris paris", wpm=60, ms=ms)


def prova_elementi_corti():
	print("Punti sempre piu' corti, ottenuti abbassando il peso del punto")
	print("a 50 wpm. L'ultimo dura meno di un millesimo e mezzo.")
	for p, durata in ((50, "12,0"), (20, "4,8"), (10, "2,4"), (5, "1,2")):
		print(f"   peso del punto {p}, cioe' {durata} millesimi")
		suona("hi hi", wpm=50, p=p)


def prova_forma():
	print("Lo stesso messaggio con la rampa dritta e poi con quella morbida.")
	print("Tolgono all'elemento la stessa durata: cambia solo la pulizia.")
	for ms in (2, 5):
		for forma, nome in (("lineare", "dritta"), ("coseno", "morbida")):
			print(f"   dissolvenza da {ms} millesimi, rampa {nome}")
			suona("cq de iz4apu k", wpm=35, ms=ms, fade_shape=forma)


def prova_rapporto():
	print("Lo stesso messaggio nei tre modi di dissolvenza, a 50 wpm con")
	print("dissolvenza da 2 millesimi, dove la differenza e' piu' netta.")
	print("Nel modo fisso il rapporto fra linea e punto vale 3,17 invece di 3.")
	for modo, nome in (("fisso", "fisso, com'era prima"),
					   ("proporzionale", "proporzionale"),
					   ("compensato", "compensato")):
		print(f"   modo {nome}")
		suona("paris paris", wpm=50, ms=2, fade_mode=modo)


def prova_velocita_annunciata():
	print("Quattro coppie. In ogni coppia lo stesso messaggio arriva prima")
	print("con i tuoi pesi e poi a pesi standard alla velocita' che CWzator")
	print("dichiara. Le due meta' devono avere lo stesso passo.")
	for msg in ("cq de iz4apu k", "paris", "abc", "ab"):
		rwpm = suona(msg, wpm=37, **PESI_GABRIELE)
		print(f"   {msg}: dichiarata {rwpm:.1f} wpm, ora la stessa a pesi standard")
		suona(msg, wpm=round(rwpm), attesa=0.8)


def prova_ritmo():
	print("Otto messaggi corti di fila, come in un esercizio serrato.")
	print("Ognuno finisce ora una trentina di millesimi prima di ieri.")
	for msg in ("test", "de", "iz4apu", "5nn", "r", "tu", "73", "e e"):
		suona(msg, wpm=37, attesa=0.15, **PESI_GABRIELE)


def prova_alte_velocita():
	print("Velocita' oltre la soglia di lettura, ascoltate rallentate tre")
	print("volte: le proporzioni restano esatte, scende solo il tono.")
	print("Serve a giudicare la pulizia degli elementi, non a leggerli.")
	for wpm in (80, 100, 120):
		print(f"   {wpm} wpm, rallentato tre volte")
		suona_rallentato("cq de iz4apu k", fattore=3, wpm=wpm, ms=1)
	print("   ora 120 wpm nei due modi di dissolvenza, sempre rallentato")
	for modo in ("fisso", "proporzionale"):
		print(f"   modo {modo}")
		suona_rallentato("paris paris", fattore=3, wpm=120, ms=1, fade_mode=modo)


def prova_alte_velocita_vere():
	print("Le stesse velocita' a tempo pieno. Non devi leggerle: ascolta")
	print("soltanto se il suono resta pulito o comincia a impastarsi.")
	for wpm in (60, 80, 100, 120):
		print(f"   {wpm} wpm")
		suona("cq de iz4apu k", wpm=wpm, ms=1)


def _chiudi_con(campioni, fs, modo):
	"""Riproduce chiudendo lo stream in tre modi diversi, per capire da dove
	arriva lo schiocco che si sente poco dopo la fine del messaggio."""
	stream = sd.OutputStream(samplerate=fs, channels=1, dtype="int16",
							 blocksize=256, latency="low")
	stream.start()
	try:
		avvio = time.monotonic()
		for i in range(0, campioni.size, 256):
			stream.write(campioni[i:i + 256])
		fine = avvio + stream.latency + campioni.size / float(fs) + 0.005
		residuo = fine - time.monotonic()
		if residuo > 0:
			time.sleep(residuo)
		if modo == "abort":
			stream.abort()
		else:
			stream.stop()
	finally:
		stream.close()


def prova_schiocco_chiusura():
	print("Lo schiocco che senti poco dopo la fine non e' nell'audio: l'ho")
	print("verificato, gli ultimi campioni scendono dolcemente e poi ci sono")
	print("cinque millesimi di silenzio esatti. Nasce quando lo stream si apre")
	print("o si chiude. Qui si prova a capire quale delle due cose sia.")
	msg = "paris paris"
	plo, _r = CWzator(msg=msg, wpm=50, ms=2, vol=VOLUME, play=False)
	a = plo.audio_data
	print("   primo gruppo: sei volte, chiudendo con abort, cioe' come adesso")
	for _ in range(6):
		_chiudi_con(a, 44100, "abort")
		time.sleep(0.5)
	time.sleep(1.0)
	print("   secondo gruppo: sei volte, chiudendo con stop, come nella V9.1")
	for _ in range(6):
		_chiudi_con(a, 44100, "stop")
		time.sleep(0.5)
	time.sleep(1.0)
	print("   terzo gruppo: sei volte di fila su un solo stream mai chiuso")
	stream = sd.OutputStream(samplerate=44100, channels=1, dtype="int16",
							 blocksize=256, latency="low")
	stream.start()
	try:
		pausa = np.zeros(int(44100 * 0.5), dtype="int16")
		for _ in range(6):
			for i in range(0, a.size, 256):
				stream.write(a[i:i + 256])
			for i in range(0, pausa.size, 256):
				stream.write(pausa[i:i + 256])
		time.sleep(stream.latency + 0.05)
		stream.abort()
	finally:
		stream.close()


def prova_forma_corta():
	print("La forma della rampa con la dissolvenza da un millesimo, che e' il")
	print("valore che cwapu usa davvero. Nella prova 4 avevi sentito due e")
	print("cinque millesimi, dove la morbida ti era sembrata migliore, ma la")
	print("misura dello spettro dice che a un millesimo la dritta e' uguale o")
	print("un filo meglio, e a 120 wpm meglio di quasi 9 dB. Serve il tuo")
	print("orecchio proprio sul valore che si usa.")
	for wpm in (37, 60):
		for forma, nome in (("lineare", "dritta"), ("coseno", "morbida")):
			print(f"   {wpm} wpm, dissolvenza 1 millesimo, rampa {nome}")
			suona("cq de iz4apu k", wpm=wpm, ms=1, fade_shape=forma)


def prova_schiocco_dopo():
	print("La stessa materia della prova 10, ma adesso lo stream resta aperto.")
	print("Nella prova 10 il primo gruppo schioccava nel 95 per cento dei casi.")
	print("Primo gruppo: sei volte lo stesso messaggio, mezzo secondo di pausa.")
	for _ in range(6):
		suona("paris paris", wpm=50, ms=2, attesa=0.5)
	time.sleep(1.2)
	print("Secondo gruppo: otto messaggi corti ravvicinati, come nella prova 7,")
	print("dove gli schiocchi erano stati piu' numerosi che altrove.")
	for msg in ("test", "de", "iz4apu", "5nn", "r", "tu", "73", "e e"):
		suona(msg, wpm=37, attesa=0.15, **PESI_GABRIELE)
	time.sleep(1.2)
	print("Terzo gruppo: un messaggio solo dopo qualche secondo di silenzio,")
	print("che e' il caso in cui il codec potrebbe essersi addormentato.")
	vero_silenzio = 4.0
	for _ in range(3):
		time.sleep(vero_silenzio)
		suona("cq de iz4apu k", wpm=37, **PESI_GABRIELE)


def prova_sovrapposte():
	print("Cambia un comportamento e va sentito. Prima ogni messaggio apriva")
	print("il proprio canale audio e i suoni si sovrapponevano; adesso il")
	print("canale e' uno solo, quindi un messaggio nuovo ferma quello in corso.")
	print("Non era una scelta, era come veniva, e due messaggi Morse")
	print("sovrapposti non si leggono. Ma in cwapu c'e' un posto dove la cosa")
	print("si nota: la scelta dei caratteri del gruppo personalizzato, dove")
	print("ogni tasto che batti suona la sua lettera.")
	print("Primo gruppo: sei lettere battute piano, una ogni sei decimi.")
	for c in "abcdef":
		suona(c, wpm=37, attesa=0.6, **PESI_GABRIELE)
	time.sleep(1.2)
	print("Secondo gruppo: le stesse sei battute in fretta, una ogni decimo,")
	print("come quando si scorre veloci con le dita. Prima si accavallavano,")
	print("adesso ognuna interrompe la precedente.")
	for c in "abcdef":
		CWzator(msg=c, wpm=37, vol=VOLUME, sync=False, **PESI_GABRIELE)
		time.sleep(0.1)
	time.sleep(1.5)


def prova_mixer():
	print("Quattro gruppi. Lo schiocco nasceva dal buffer che si svuotava fra")
	print("un messaggio e l'altro, non dall'apertura dello stream: adesso c'e'")
	print("un mixer che scrive sempre, silenzio compreso.")
	print("Primo gruppo: sei volte lo stesso messaggio, come nella prova 12.")
	for _ in range(6):
		suona("paris paris", wpm=50, ms=2, attesa=0.5)
	time.sleep(1.2)
	print("Secondo gruppo: otto messaggi corti ravvicinati.")
	for msg in ("test", "de", "iz4apu", "5nn", "r", "tu", "73", "e e"):
		suona(msg, wpm=37, attesa=0.15, **PESI_GABRIELE)
	time.sleep(1.2)
	print("Terzo gruppo: tre messaggi separati da quattro secondi di silenzio,")
	print("che e' il caso in cui il dispositivo potrebbe addormentarsi.")
	for _ in range(3):
		time.sleep(4.0)
		suona("cq de iz4apu k", wpm=37, **PESI_GABRIELE)
	time.sleep(1.2)
	print("Quarto gruppo: le sei lettere battute in fretta della prova 13.")
	print("Adesso si sommano invece di interrompersi.")
	for c in "abcdef":
		CWzator(msg=c, wpm=37, vol=VOLUME, sync=False, **PESI_GABRIELE)
		time.sleep(0.1)
	time.sleep(2.0)


def prova_pileup():
	print("Il pile-up. Fino a trentadue stazioni possono chiamare insieme,")
	print("ognuna con la sua velocita' e il suo tono, e il mixer le somma.")
	print("Prima tre stazioni, poi otto, poi sedici. Il volume di ognuna e'")
	print("abbassato, altrimenti sommandole si saturerebbe.")
	import random
	random.seed(4)
	nominativi = ["iz4apu", "dl4mm", "ik1ojm", "w9cf", "ea3abc", "ja1xyz",
				  "vk2pq", "g3wxy", "lu5db", "on4kt", "sm3cer", "yo3fca",
				  "9a1aa", "pa0rdt", "ur5eqf", "ve7sl"]
	for quante in (3, 8, 16):
		print(f"   {quante} stazioni insieme")
		volume = max(0.05, 0.55 / quante ** 0.5)
		for i in range(quante):
			CWzator(msg=nominativi[i], wpm=random.randint(22, 34),
					pitch=random.randint(420, 820), vol=volume, sync=False)
			time.sleep(random.uniform(0.02, 0.16))
		time.sleep(3.5)
	print("   e adesso una sola stazione, per riferimento")
	suona("iz4apu", wpm=28)


def prova_panning():
	print("Il panning, chiesto da te dopo il pile-up. Ogni stazione puo' stare")
	print("dove vuole fra i due altoparlanti, da meno cento a piu' cento.")
	print("Primo gruppo: la stessa stazione in cinque posizioni.")
	for pan, dove in ((-100, "tutto a sinistra"), (-50, "mezzo a sinistra"),
					  (0, "al centro"), (50, "mezzo a destra"), (100, "tutto a destra")):
		print(f"   {dove}")
		suona("iz4apu", wpm=28, pan=pan, attesa=0.5)
	time.sleep(1.0)
	print("Secondo gruppo: la stessa stazione al centro e poi tutta a sinistra,")
	print("una dopo l'altra, per sentire se il volume cambia. Non dovrebbe: la")
	print("legge e' a potenza costante e l'ho verificato sui numeri.")
	for _ in range(2):
		suona("iz4apu", wpm=28, pan=0, attesa=0.4)
		suona("iz4apu", wpm=28, pan=-100, attesa=0.8)
	time.sleep(1.0)
	print("Terzo gruppo: sedici stazioni sparse su tutto il fronte.")
	import random
	random.seed(11)
	call = ["dl4mm", "ik1ojm", "w9cf", "on4kt", "ea3abc", "ja1xyz", "vk2pq",
			"sm3cer", "g3wxy", "lu5db", "9a1aa", "pa0rdt", "ur5eqf", "ve7sl",
			"yo3fca", "oz1abc"]
	for i, c in enumerate(call):
		CWzator(msg=c, wpm=random.randint(22, 34), pitch=random.randint(420, 820),
				vol=0.14, pan=-100 + i * 13, sync=False)
		time.sleep(random.uniform(0.02, 0.15))
	time.sleep(4.5)
	print("Quarto gruppo: le stesse sedici tutte al centro, per confronto.")
	random.seed(11)
	for c in call:
		CWzator(msg=c, wpm=random.randint(22, 34), pitch=random.randint(420, 820),
				vol=0.14, pan=0, sync=False)
		time.sleep(random.uniform(0.02, 0.15))
	time.sleep(4.5)


PROVE = [
	("La coda dei messaggi",
	 "Verifica che l'ultimo elemento di ogni trasmissione si senta intero. Era il difetto che ti ha fatto sentire kappa come d: la linea finale veniva tagliata e restava della lunghezza di un punto.",
	 "Che ogni lettera annunciata sia quella che senti, e che non ci sia nessuno schiocco secco alla fine.",
	 prova_coda),
	("Lo schiocco sugli elementi corti",
	 "Fino alla V9.1 una dissolvenza piu' lunga di meta' elemento veniva scartata invece che accorciata, quindi chiedere una dissolvenza piu' dolce dava l'effetto opposto. Adesso viene accorciata.",
	 "Che alzando i millesimi il suono diventi via via piu' morbido, e mai piu' secco.",
	 prova_schiocco),
	("Gli elementi cortissimi",
	 "Il caso limite della correzione precedente. Sull'ultimo punto, che dura poco piu' di un millesimo, la rampa piu' lunga possibile e' di mezzo elemento e un gradino resta per forza.",
	 "Fino a dove il suono resta pulito, e da dove comincia a sporcarsi. Se l'ultimo e' sporco e' un limite fisico, non un difetto: dillo comunque.",
	 prova_elementi_corti),
	("La forma della dissolvenza",
	 "Due forme di rampa. La dritta e' quella storica, la morbida e' un mezzo coseno rialzato. Tolgono all'elemento esattamente la stessa durata, l'ho misurato, quindi la differenza e' soltanto di timbro. Il valore predefinito e' ancora la dritta.",
	 "Quale delle due preferisci, e se la preferenza cambia fra le due lunghezze di dissolvenza. Se preferisci la morbida cambio il predefinito.",
	 prova_forma),
	("Il rapporto fra punto e linea",
	 "La dissolvenza toglie a ogni elemento la stessa quantita' assoluta, quindi alle alte velocita' allontana da tre il rapporto fra linea e punto. I modi proporzionale e compensato lo riportano a tre esatto, per strade diverse. Il predefinito e' ancora il modo fisso.",
	 "In quale dei tre distingui meglio i punti dalle linee, e se il compensato ti sembra alterare il ritmo, visto che ruba tempo al silenzio.",
	 prova_rapporto),
	("La velocita' annunciata",
	 "La velocita' effettiva ora si ricava dalla durata davvero prodotta. Prima, sotto i quattro caratteri, il calcolo veniva saltato e ti veniva annunciata quella nominale: le ultime due coppie sono proprio quei casi.",
	 "Che dentro ogni coppia le due meta' scorrano alla stessa andatura. Non saranno identiche, perche' i pesi cambiano la forma dei caratteri e la seconda meta' e' arrotondata al wpm intero.",
	 prova_velocita_annunciata),
	("Il ritmo fra un messaggio e l'altro",
	 "Ogni messaggio adesso finisce una trentina di millesimi prima. Sui messaggi lunghi non si nota, dove sono ravvicinati il ritmo puo' essere cambiato.",
	 "Se fra un messaggio e il successivo hai ancora il tempo che ti serve, o se adesso ti incalza.",
	 prova_ritmo),
	("Le alte velocita', rallentate",
	 "Velocita' che non si leggono, ascoltate a un terzo. L'audio e' generato alla velocita' vera e riprodotto piu' lentamente, quindi punto, linea e spazi restano nelle stesse proporzioni e cambia solo l'altezza della nota. Serve a giudicare la forma degli elementi senza doverli leggere.",
	 "Se gli elementi restano netti e distinguibili, se senti click all'attacco o alla chiusura, e se il rapporto fra punto e linea ti sembra tenere.",
	 prova_alte_velocita),
	("Le alte velocita', a tempo pieno",
	 "Le stesse velocita' senza rallentamento, fino al tetto nuovo di 120 wpm. Non serve leggerle.",
	 "Da quale velocita' il suono comincia a impastarsi o a sporcarsi. Quello e' il tetto vero, e ci va messo il limite.",
	 prova_alte_velocita_vere),
	("Da dove arriva lo schiocco in chiusura",
	 "Nata dal tuo primo collaudo. Tre gruppi da sei ripetizioni dello stesso messaggio, che si distinguono solo per come lo stream viene chiuso: prima con abort come adesso, poi con stop come nella V9.1, poi sei volte di fila su un solo stream mai chiuso. Fra un gruppo e l'altro c'e' un secondo di pausa.",
	 "In quale dei tre gruppi lo schiocco compare, quante volte su sei, e se nel terzo gruppo sparisce del tutto. Se sparisce solo nel terzo, la causa e' l'apertura e la chiusura dello stream e la cura e' tenerlo aperto.",
	 prova_schiocco_chiusura),
	("La forma della rampa sul valore vero",
	 "Nata dal tuo primo collaudo. Nella prova 4 avevi sentito la dissolvenza da due e da cinque millesimi e la morbida ti era sembrata migliore. Ma cwapu usa un millesimo, e li' la misura dello spettro dice il contrario. Quattro ascolti, due velocita' per due forme.",
	 "Quale delle due preferisci a un millesimo, e se la preferenza cambia fra 37 e 60 wpm. E' la decisione che fissa il valore predefinito.",
	 prova_forma_corta),
	("Lo schiocco dopo la cura",
	 "La prova 10 ha stabilito che lo schiocco nasce dall'apertura e dalla chiusura dello stream: chiudendo con abort compariva nel 95 per cento dei messaggi, con stop nel 100, e su uno stream mai chiuso zero. Adesso lo stream resta aperto. Questa prova ripete la stessa materia, piu' un terzo gruppo con pause lunghe, che e' il caso peggiore perche' il codec potrebbe addormentarsi.",
	 "Se lo schiocco e' sparito del tutto, e se per caso ricompare nel terzo gruppo, cioe' dopo i silenzi lunghi. Se ricompare solo li', vuol dire che si addormenta il codec e non lo stream, ed e' un'altra cura.",
	 prova_schiocco_dopo),
	("Le lettere battute in fretta",
	 "Con un canale audio solo, un messaggio nuovo ferma quello in corso invece di sovrapporsi. Prima si accavallavano. In cwapu il posto dove si nota e' la scelta dei caratteri del gruppo personalizzato, dove ogni tasto suona la sua lettera. Sei lettere piano e poi le stesse sei in fretta.",
	 "Se battendo in fretta il comportamento nuovo ti sembra meglio o peggio di prima. Se preferivi sentirle accavallate, si puo' rimettere: si accodano invece di interrompersi, e si sente ogni lettera per intero ma in ritardo.",
	 prova_sovrapposte),
	("Il mixer, cioe' la cura vera",
	 "Il tuo collaudo precedente ha smentito la diagnosi e ha portato a quella giusta. Nella prova 10 il terzo gruppo era pulito perche' li' scrivevo nello stream anche le pause, quindi il flusso di campioni non si interrompeva mai; nella prova 12 lo stream restava aperto ma fra un messaggio e l'altro nessuno scriveva, e il dispositivo andava in underrun. E' il buffer che si svuota a schioccare, non l'apertura. Adesso c'e' un mixer che scrive sempre. Quattro gruppi, gli stessi di prima piu' le lettere in fretta, che ora si sommano invece di interrompersi.",
	 "Se lo schiocco e' sparito, e in quale gruppo eventualmente resta. Il terzo, con i silenzi lunghi, e' il piu' severo. Nel quarto dimmi se sentire le lettere sommate ti sembra meglio dell'interruzione.",
	 prova_mixer),
	("Il pile-up",
	 "La capacita' che avevo tolto senza accorgermene e che tu hai difeso. Fino a trentadue stazioni possono chiamare insieme, ognuna con la sua velocita' e il suo tono. Tre gruppi, da tre, otto e sedici stazioni, e alla fine una sola per riferimento. Il volume di ognuna scende al crescere del numero, altrimenti la somma satura.",
	 "Se il mucchio si sente come un pile-up vero, se riesci a estrarre qualche nominativo, e soprattutto se senti distorsione o saturazione quando sono in sedici. Se satura, il volume automatico va abbassato ancora.",
	 prova_pileup),
	("Il panning",
	 "Il mixer e' diventato stereo e ogni stazione ha la sua posizione, da meno cento tutto a sinistra a piu' cento tutto a destra. La legge e' a potenza costante, quindi al centro i due lati stanno a meno tre decibel ciascuno e il volume non cambia spostandosi. La sintesi resta monofonica: il pan vale solo in riproduzione, i file WAV non cambiano.",
	 "Se le posizioni si sentono dove devono, se il volume resta uguale spostando la stazione, e soprattutto se nel terzo gruppo, sedici stazioni sparse, riesci a estrarne piu' facilmente che nel quarto, dove sono tutte al centro. Se la differenza si sente, il panning vale la pena.",
	 prova_panning),
]


def leggi_fatte():
	"""I titoli delle prove gia' registrate. Si riconoscono dal titolo e non
	dal numero, altrimenti aggiungerne una in mezzo farebbe saltare tutte
	quelle che vengono dopo."""
	fatte = set()
	if os.path.exists(ESITI):
		with open(ESITI, "r", encoding="utf-8") as f:
			for riga in f:
				if riga.startswith("PROVA ") and ":" in riga:
					fatte.add(riga.split(":", 1)[1].strip())
	return fatte


def registra(numero, titolo, esito, commento):
	nuovo = not os.path.exists(ESITI)
	with open(ESITI, "a", encoding="utf-8") as f:
		if nuovo:
			f.write("Esiti del collaudo d'ascolto di CWzator\n")
			f.write("Scritti da collaudo_cw.py, che li aggiunge man mano.\n")
		f.write(f"PROVA {numero}: {titolo}\n")
		f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M')}\n")
		f.write(f"Esito: {esito}\n")
		if commento:
			f.write(f"Commento di Gabriele: {commento}\n")


def conduci(numero, titolo, spiegazione, osservare, funzione):
	print(f"Prova {numero} di {len(PROVE)}: {titolo}")
	print(spiegazione)
	print(f"Cosa osservare: {osservare}")
	while True:
		scelta = key(prompt="Invio per ascoltare, s per saltare, q per uscire: ")
		if scelta in ("\r", "\n"):
			break
		if scelta.lower() == "s":
			return "saltata"
		if scelta.lower() == "q":
			return "uscita"
		print("Tasto non valido.")
	while True:
		funzione()
		print("Ascolto finito.")
		scelta = key(prompt="r per riascoltare, b se va bene, c per commentare, q per uscire: ")
		s = scelta.lower()
		if s == "r":
			continue
		if s == "b":
			registra(numero, titolo, "superata", "")
			print("Prova superata, registrata.")
			return "superata"
		if s == "c":
			commento = dgt(prompt="Dimmi cosa hai sentito: ", kind="s", smin=0, smax=800)
			registra(numero, titolo, "da rivedere", commento)
			print("Commento registrato.")
			return "commentata"
		if s == "q":
			return "uscita"
		print("Tasto non valido.")


def main():
	print("Collaudo d'ascolto di CWzator")
	print("Ogni prova ti dice prima cosa sentirai e cosa osservare, poi aspetta")
	print("che tu prema Invio. Dopo l'ascolto puoi riascoltare quante volte")
	print("vuoi, dichiarare che va bene, oppure lasciare un commento.")
	print(f"Gli esiti finiscono in {ESITI}")
	fatte = leggi_fatte()
	if fatte:
		print(f"Prove gia' registrate in una sessione precedente: {len(fatte)}. Le salto.")
	print(f"Volume delle prove: {int(VOLUME * 100)} per cento.")
	rimaste = 0
	for i, (titolo, spiegazione, osservare, funzione) in enumerate(PROVE, start=1):
		if titolo in fatte:
			continue
		rimaste += 1
		esito = conduci(i, titolo, spiegazione, osservare, funzione)
		if esito == "uscita":
			print("Uscita. Le prove non ancora registrate ti verranno riproposte.")
			return 0
	if rimaste == 0:
		print("Tutte le prove erano gia' state fatte. Per rifarle, cancella il file degli esiti.")
	else:
		print("Collaudo finito. Il file degli esiti e' pronto da leggere.")
	return 0


if __name__ == "__main__":
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		print("Interrotto.")
		sys.exit(1)
