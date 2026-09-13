"""Collaudo d'ascolto del Farnsworth di CWzator.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 12 settembre 2026 con la issue 16.
Il banco dice che i conti tornano: la parola campione dura quello che deve con
qualunque peso, le spaziature coincidono con ARRL e il carattere e' identico
campione per campione. Cio' che il banco non sa dire e' se all'orecchio il
Farnsworth sia quello vero, cioe' se la lettera suoni sempre allo stesso modo
mentre attorno a lei si fa spazio. E' quello che si prova qui.
Tutto suona al venti per cento di volume.
In fondo a ogni gruppo: r riascolta il gruppo intero, c apre il posto dove
scrivere, Invio lo da' per superato, Escape lo chiude senza annotare. Quello
che si scrive finisce in collaudo_farnsworth_esiti.txt accanto a questo file.
Si lancia con
  python collaudo_farnsworth.py
"""
import os
import sys
import time

from collaudo_comune import Esiti, gruppo

from GBUtils import CWzator, enter_escape

QUI = os.path.dirname(os.path.abspath(__file__))
VOL = 0.20
# I pesi su cui si ascolta: gli standard, quelli che Gabriele usa davvero e
# due combinazioni che tirano da parti opposte.
PESI = [(30, 50, 50, "standard"), (32, 53, 34, "i tuoi"),
		(30, 70, 50, "s largo"), (45, 50, 30, "linea lunga, punto corto")]

esiti = Esiti(os.path.join(QUI, "collaudo_farnsworth_esiti.txt"),
			  "Esiti del collaudo d'ascolto del Farnsworth di CWzator\n"
			  "Scritti da collaudo_farnsworth.py, che li aggiunge man mano.")

def suona(msg, **kw):
	"""Manda il messaggio e dice la velocita' che CWzator ha restituito."""
	kw.setdefault("vol", VOL)
	kw.setdefault("sync", True)
	handle, rwpm = CWzator(msg=msg, **kw)
	if handle is None:
		print(f"respinto: {CWzator.ultimo_errore}")
		return None
	return rwpm

def dire(etichetta, msg, **kw):
	print(f"  {etichetta}: {msg}")
	r = suona(msg, **kw)
	print(f"  restituito {r:.2f} wpm." if r else "  niente.")
	time.sleep(0.4)

def main():
	print("Collaudo d'ascolto del Farnsworth.")
	print()
	print("Il Farnsworth manda i caratteri gia' alla velocita' a cui vuoi arrivare e ti da' tempo")
	print("allargando soltanto lo spazio fra una lettera e l'altra. Dentro il carattere non tocca")
	print("niente, quindi i tuoi pesi restano quelli.")
	print()
	print("Tutto al venti per cento di volume. Ogni ascolto dice prima cosa manda e poi che velocita'")
	print("CWzator ha restituito.")
	print()
	print("In fondo a ogni gruppo: r riascolta, c commenta, Invio lo da' per superato.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per uscire\r"):
		return 0
	titolo = "il carattere non cambia, pesi standard"
	if gruppo(titolo, 4, unita="ascolti"):
		def ascolta():
			for etichetta, kw in (("20 wpm, senza Farnsworth", {"wpm": 20}),
								  ("20 wpm, effettivi 12", {"wpm": 20, "farnsworth": 12}),
								  ("20 wpm, effettivi 8", {"wpm": 20, "farnsworth": 8}),
								  ("20 wpm, effettivi 5", {"wpm": 20, "farnsworth": 5})):
				dire(etichetta, "cq de iz4apu", **kw)
			print()
		ascolta()
		esiti.esito(titolo, ascolta,
					"  La domanda: la singola lettera e' sempre la stessa, e a cambiare e' solo lo spazio fra una e l'altra?")
	titolo = "i pesi restano i tuoi"
	if gruppo(titolo, len(PESI) * 2, unita="ascolti"):
		def ascolta():
			for l, s, p, nome in PESI:
				for etichetta, extra in (("senza", {}), ("con effettivi 8", {"farnsworth": 8})):
					dire(f"pesi {l} {s} {p}, {nome}, {etichetta}", "paris paris",
						 wpm=20, l=l, s=s, p=p, **extra)
				print()
		ascolta()
		esiti.esito(titolo, ascolta,
					"  La domanda: la firma dei tuoi pesi si riconosce anche con il Farnsworth acceso?")
	titolo = "le due velocita'"
	if gruppo(titolo, 4, unita="ascolti"):
		def ascolta():
			for wpm, eff in ((18, 5), (20, 8), (25, 12), (30, 18)):
				dire(f"caratteri {wpm}, effettivi {eff}", "5nn tu 73", wpm=wpm, farnsworth=eff)
			print()
		ascolta()
		esiti.esito(titolo, ascolta,
					"  La domanda: salendo con i caratteri e tenendo bassi gli effettivi, la lettera resta comoda da riconoscere?")
	titolo = "la stessa distanza, qualunque testo"
	if gruppo(titolo, 4, unita="ascolti"):
		print("  Stessa impostazione per tutti, 20 caratteri e 8 effettivi. Lo spazio fra le lettere deve")
		print("  suonare identico.")
		def ascolta():
			for msg in ("e e e e e", "0 0 0", "cq cq cq", "paris paris"):
				dire("manda", msg, wpm=20, farnsworth=8)
			print()
		ascolta()
		esiti.esito(titolo, ascolta,
					"  La domanda: la distanza fra le lettere e' la stessa in tutti e quattro, anche se i testi sono diversi?")
	titolo = "il peso s contro il Farnsworth"
	if gruppo(titolo, 3, unita="ascolti"):
		print("  Tre modi di andare piano, tutti intorno agli 8 wpm d'insieme. Il primo rallenta tutto,")
		print("  il secondo allarga anche dentro la lettera, il terzo e' il Farnsworth.")
		def ascolta():
			dire("primo: 8 wpm secchi, pesi standard", "paris paris", wpm=8)
			time.sleep(0.3)
			dire("secondo: 20 wpm con s a 100, che allarga anche dentro la lettera", "paris paris", wpm=20, s=100)
			time.sleep(0.3)
			dire("terzo: 20 wpm di carattere ed effettivi 8, cioe' il Farnsworth", "paris paris", wpm=20, farnsworth=8)
			print()
		ascolta()
		esiti.esito(titolo, ascolta,
					"  La domanda: nel terzo le lettere suonano veloci come a 20 wpm mentre negli altri due si sfaldano?")
	titolo = "cosa CWzator rifiuta"
	if gruppo(titolo, 2, unita="ascolti"):
		def ascolta():
			print("  Effettivi piu' alti dei caratteri: non deve suonare niente.")
			suona("paris", wpm=15, farnsworth=25)
			time.sleep(0.4)
			print("  Effettivi 20 con s a 100: i pesi non ci arrivano, non deve suonare niente.")
			suona("paris", wpm=25, s=100, farnsworth=20)
			print()
		ascolta()
		esiti.esito(titolo, ascolta, "  La domanda: hai sentito silenzio tutte e due le volte?")
	CWzator.chiudi_riproduzioni()
	print("Collaudo finito. Grazie per le orecchie.")
	if os.path.exists(esiti.percorso):
		print(f"Gli esiti stanno in {os.path.basename(esiti.percorso)}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
