"""Collaudo della tastiera a eventi, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto).
Nato con la V160 e la issue 37, il 14 settembre 2026.
banco_tastiera.py prova la Tastiera con eventi iniettati, e quello lo fa da
solo; questo chiede le mani di Gabriele, perche' c'e' una cosa che nessun
banco puo' misurare: quanti tasti la tastiera fisica riesca a mandare insieme.
Le tastiere a membrana di solito si fermano fra i due e i tre, ed e' un limite
del pezzo di plastica, non del programma. Finche' non lo si misura non si puo'
promettere un accordo di quattro note.
Tre prove, ognuna si chiude con Esc:
  i nomi, per sentire come si chiama ogni tasto che si preme;
  l'accordo, che conta quanti tasti risultano giu' nello stesso momento;
  la tenuta, che misura quanto dura un tasto tenuto e verifica che
    l'auto-ripetizione di Windows non produca una seconda nota.
Si lancia con
  python collaudo_tastiera.py
"""
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, "E:/git/mine/GBUtils")
from GBUtils import Tastiera

# Il riepilogo finisce anche qui, accanto al collaudo: a fine prova lo schermo
# e' pieno di righe e i numeri che contano sono le ultime cinque.
ESITI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collaudo_tastiera_esiti.txt")
verbale = []

def riferisci(riga):
	"""Stampa e mette da parte, per il file degli esiti."""
	print(riga)
	verbale.append(riga)

# I nomi che sono caratteri di controllo si leggono male con lo screen reader:
# qui prendono la loro parola.
PAROLE = {"\r": "invio", "\x1b": "esc", "\t": "tab", "\x08": "backspace", " ": "spazio"}

def leggibile(nome):
	return PAROLE.get(nome, nome)

def esci(nome, azione):
	return nome == "\x1b" and azione == "giu"

def prova_nomi(tastiera):
	print("\rPrima prova, i nomi. Premi i tasti che vuoi e ti dico come si chiamano. Esc per passare oltre.\r")
	tastiera.svuota()
	visti = set()
	eventi = 0
	while True:
		for nome, azione in tastiera.eventi(None):
			if esci(nome, azione):
				print(f"Tasti diversi {len(visti)}, eventi {eventi}.")
				return visti
			eventi += 1
			if azione == "giu":
				visti.add(nome)
			print(f"{azione} {leggibile(nome)}, giu' ora {len(tastiera.premuti)}")

def prova_accordo(tastiera):
	print("\rSeconda prova, l'accordo. Premi piu' tasti insieme, tenendoli giu', e prova a salire di numero. Esc per passare oltre.\r")
	tastiera.svuota()
	massimo = 0
	quando = ""
	while True:
		for nome, azione in tastiera.eventi(None):
			if esci(nome, azione):
				print(f"Massimo insieme {massimo}: {quando}")
				# I tasti che risultano ancora giu' quando hai gia' lasciato
				# tutto sono rilasci che non sono mai arrivati: una tastiera
				# spinta oltre il suo rollover si mangia anche quelli.
				appesi = sorted(leggibile(n) for n in tastiera.premuti if n != "\x1b")
				if appesi:
					print(f"Rilasci mai arrivati {len(appesi)}: {' '.join(appesi)}")
				return massimo, quando, appesi
			insieme = len(tastiera.premuti)
			if insieme > massimo:
				massimo = insieme
				quando = " ".join(sorted(leggibile(n) for n in tastiera.premuti))
				print(f"Insieme {insieme}: {quando}")

def prova_tenuta(tastiera):
	print("\rTerza prova, la tenuta. Tieni giu' un tasto qualche secondo, poi lascialo, e ripeti quanto vuoi. Esc per finire.\r")
	tastiera.svuota()
	inizi = {}
	durate = []
	ripetizioni = 0
	while True:
		for nome, azione in tastiera.eventi(None):
			if esci(nome, azione):
				if durate:
					media = sum(durate) / len(durate)
					print(f"Tenute {len(durate)}, media {media * 1000:.0f} ms,")
					print(f"la piu' corta {min(durate) * 1000:.0f} ms, la piu' lunga {max(durate) * 1000:.0f} ms.")
				print(f"Pressioni di troppo {ripetizioni}.")
				return durate, ripetizioni
			if azione == "giu":
				if nome in inizi:
					# Non dovrebbe mai succedere: l'auto-ripetizione e' gia'
					# stata scartata dalla Tastiera, e se una arriva qui vuol
					# dire che qualcosa non ha funzionato.
					ripetizioni += 1
					print(f"Seconda pressione di {leggibile(nome)} senza rilascio.")
				inizi[nome] = time.perf_counter()
				continue
			partito = inizi.pop(nome, None)
			if partito is None:
				continue
			durata = time.perf_counter() - partito
			durate.append(durata)
			print(f"{leggibile(nome)} tenuto {durata * 1000:.0f} ms.")

def main():
	print("\rCollaudo della tastiera a eventi. Tre prove, ognuna finisce con Esc.\r")
	try:
		tastiera = Tastiera()
	except (NotImplementedError, EOFError, RuntimeError) as errore:
		print(errore)
		return 1
	with tastiera:
		visti = prova_nomi(tastiera)
		massimo, insieme, appesi = prova_accordo(tastiera)
		durate, ripetizioni = prova_tenuta(tastiera)
	print("\rRiepilogo.")
	riferisci(f"Collaudo del {datetime.now():%d/%m/%Y alle %H:%M}.")  # noqa: DTZ005 - ora locale, la legge chi era davanti
	riferisci(f"Tasti diversi provati {len(visti)}.")
	riferisci(f"Massimo insieme {massimo}" + (f": {insieme}." if insieme else "."))
	if massimo >= 4:
		riferisci("La tastiera regge un accordo di quattro note.")
	elif massimo == 3:
		riferisci("Tre note insieme: e' il limite tipico delle tastiere a membrana.")
	elif massimo:
		riferisci("Meno di tre insieme: gli accordi su questa tastiera sono stretti.")
	if appesi:
		riferisci(f"Rilasci mai arrivati {len(appesi)}: {' '.join(appesi)}.")
		riferisci("Sono tasti che la tastiera non ha riferito di aver lasciato, non eventi persi dal programma.")
	else:
		riferisci("Nessun rilascio perso.")
	if durate:
		media = sum(durate) / len(durate)
		riferisci(f"Tenute misurate {len(durate)}, media {media * 1000:.0f} ms, la piu' lunga {max(durate) * 1000:.0f} ms.")
	riferisci("Auto-ripetizione trapelata: " + ("nessuna, come deve essere." if not ripetizioni else f"{ripetizioni}, da guardare."))
	try:
		with open(ESITI, "w", encoding="utf-8") as f:
			f.write("\n".join(verbale) + "\n")
		print(f"Riepilogo scritto in {os.path.basename(ESITI)}")
	except OSError as errore:
		print(f"Riepilogo non scritto: {errore}")
	return 0

if __name__ == "__main__":
	sys.exit(main())
