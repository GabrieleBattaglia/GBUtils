"""Collaudo d'ascolto del Farnsworth di CWzator.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 12 settembre 2026 con la issue 16.
Il banco dice che i conti tornano: la parola campione dura quello che deve con
qualunque peso, le spaziature coincidono con ARRL e il carattere e' identico
campione per campione. Cio' che il banco non sa dire e' se all'orecchio il
Farnsworth sia quello vero, cioe' se la lettera suoni sempre allo stesso modo
mentre attorno a lei si fa spazio. E' quello che si prova qui.
Tutto suona al tre per cento di volume, come chiesto: si sente senza disturbare.
Dopo ogni gruppo si scrive cosa si e' sentito, e finisce in
collaudo_farnsworth_esiti.txt accanto a questo file.
Si lancia con
  python collaudo_farnsworth.py
"""
import os
import sys
import time

from GBUtils import CWzator, dgt, enter_escape

QUI = os.path.dirname(os.path.abspath(__file__))
ESITI = os.path.join(QUI, "collaudo_farnsworth_esiti.txt")
VOL = 0.03
# I pesi su cui si ascolta: gli standard, quelli che Gabriele usa davvero e
# due combinazioni che tirano da parti opposte.
PESI = [(30, 50, 50, "standard"), (32, 53, 34, "i tuoi"),
		(30, 70, 50, "s largo"), (45, 50, 30, "linea lunga, punto corto")]

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
			f.write("Esiti del collaudo d'ascolto del Farnsworth di CWzator\n")
			f.write("Scritti da collaudo_farnsworth.py, che li aggiunge man mano.\n")
		f.write(f"\nGRUPPO: {titolo}\n")
		f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M')}\n")
		f.write(f"Commento di Gabriele: {commento if commento else 'nessuno'}\n")

def chiedi_commento(titolo):
	riga("Scrivi cosa hai sentito e batti Invio. Invio da solo se non hai niente da dire.")
	commento = dgt("\rImpressioni\r", kind="s", smin=0, smax=2000)
	registra(titolo, commento.strip())
	riga("Annotato.")
	print()

def suona(msg, **kw):
	"""Manda il messaggio e dice la velocita' che CWzator ha restituito."""
	kw.setdefault("vol", VOL)
	kw.setdefault("sync", True)
	handle, rwpm = CWzator(msg=msg, **kw)
	if handle is None:
		riga(f"respinto: {CWzator.ultimo_errore}")
		return None
	return rwpm

def gruppo(titolo, quante):
	riga(f"Gruppo: {titolo}. Sono {quante} ascolti.")
	return enter_escape("\rInvio per questo gruppo, Escape per saltarlo\r")

def main():
	riga("Collaudo d'ascolto del Farnsworth.")
	print()
	riga("Il Farnsworth manda i caratteri gia' alla velocita' a cui vuoi arrivare e ti da' tempo allargando soltanto lo spazio fra una lettera e l'altra. Dentro il carattere non tocca niente, quindi i tuoi pesi restano quelli.")
	print()
	riga("Tutto suona al tre per cento di volume. Ogni ascolto dice prima cosa manda e poi che velocita' CWzator ha restituito.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per uscire\r"):
		return 0
	# 1. La prova che chiude la issue: il carattere non cambia.
	if gruppo("il carattere non cambia, pesi standard", 4):
		for etichetta, kw in (("20 wpm, senza Farnsworth", {"wpm": 20}),
							  ("20 wpm, effettivi 12", {"wpm": 20, "farnsworth": 12}),
							  ("20 wpm, effettivi 8", {"wpm": 20, "farnsworth": 8}),
							  ("20 wpm, effettivi 5", {"wpm": 20, "farnsworth": 5})):
			riga(f"{etichetta}: cq de iz4apu")
			r = suona("cq de iz4apu", **kw)
			riga(f"CWzator ha restituito {r:.2f} wpm." if r else "niente.")
			time.sleep(0.4)
		print()
		riga("La domanda: la singola lettera e' sempre la stessa, e a cambiare e' solo lo spazio fra una e l'altra?")
		print()
		chiedi_commento("il carattere non cambia, pesi standard")
	# 2. I tuoi pesi si sentono ancora.
	if gruppo("i pesi restano i tuoi, con e senza Farnsworth", len(PESI) * 2):
		for l, s, p, nome in PESI:
			for etichetta, extra in (("senza", {}), ("con effettivi 8", {"farnsworth": 8})):
				riga(f"pesi {l} {s} {p}, {nome}, {etichetta}: paris paris")
				r = suona("paris paris", wpm=20, l=l, s=s, p=p, **extra)
				riga(f"restituito {r:.2f} wpm." if r else "niente.")
				time.sleep(0.4)
			print()
		riga("La domanda: la firma dei tuoi pesi si riconosce anche con il Farnsworth acceso?")
		print()
		chiedi_commento("i pesi restano i tuoi")
	# 3. Le due velocita', come le usa chi impara.
	if gruppo("le due velocita', la scala didattica", 4):
		for wpm, eff in ((18, 5), (20, 8), (25, 12), (30, 18)):
			riga(f"caratteri {wpm}, effettivi {eff}: 5nn tu 73")
			r = suona("5nn tu 73", wpm=wpm, farnsworth=eff)
			riga(f"restituito {r:.2f} wpm." if r else "niente.")
			time.sleep(0.4)
		print()
		riga("La domanda: salendo con i caratteri e tenendo bassi gli effettivi, la lettera resta comoda da riconoscere?")
		print()
		chiedi_commento("le due velocita'")
	# 4. Le spaziature non dipendono dal messaggio.
	if gruppo("la stessa distanza, qualunque testo", 4):
		riga("Stessa impostazione per tutti, 20 caratteri e 8 effettivi. Lo spazio fra le lettere deve suonare identico.")
		for msg in ("e e e e e", "0 0 0", "cq cq cq", "paris paris"):
			riga(f"manda: {msg}")
			r = suona(msg, wpm=20, farnsworth=8)
			riga(f"restituito {r:.2f} wpm." if r else "niente.")
			time.sleep(0.4)
		print()
		riga("La domanda: la distanza fra le lettere e' la stessa in tutti e quattro, anche se i testi sono diversi?")
		print()
		chiedi_commento("la stessa distanza, qualunque testo")
	# 5. Il confronto che la issue 16 chiedeva: s non e' Farnsworth.
	if gruppo("il peso s contro il Farnsworth", 3):
		riga("Tre modi di andare piano, tutti intorno agli 8 wpm d'insieme. Il primo rallenta tutto, il secondo allarga anche dentro la lettera, il terzo e' il Farnsworth.")
		print()
		riga("primo: 8 wpm secchi, pesi standard")
		r = suona("paris paris", wpm=8)
		riga(f"restituito {r:.2f} wpm." if r else "niente.")
		time.sleep(0.6)
		riga("secondo: 20 wpm con s a 100, che allarga anche dentro la lettera")
		r = suona("paris paris", wpm=20, s=100)
		riga(f"restituito {r:.2f} wpm." if r else "niente.")
		time.sleep(0.6)
		riga("terzo: 20 wpm di carattere ed effettivi 8, cioe' il Farnsworth")
		r = suona("paris paris", wpm=20, farnsworth=8)
		riga(f"restituito {r:.2f} wpm." if r else "niente.")
		print()
		riga("La domanda: nel terzo le lettere suonano veloci come a 20 wpm mentre negli altri due si sfaldano?")
		print()
		chiedi_commento("il peso s contro il Farnsworth")
	# 6. Gli errori, che non devono suonare.
	if gruppo("cosa CWzator rifiuta", 2):
		riga("Effettivi piu' alti dei caratteri: non deve suonare niente.")
		suona("paris", wpm=15, farnsworth=25)
		time.sleep(0.4)
		riga("Effettivi 20 con s a 100: i pesi non ci arrivano, non deve suonare niente.")
		suona("paris", wpm=25, s=100, farnsworth=20)
		print()
		chiedi_commento("cosa CWzator rifiuta")
	CWzator.chiudi_riproduzioni()
	riga("Collaudo finito. Grazie per le orecchie.")
	if os.path.exists(ESITI):
		riga(f"Gli esiti stanno in {os.path.basename(ESITI)}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
