"""Collaudo a mano di key, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato con la revisione 1 di key l'8 settembre 2026, rifatto il 13 settembre
2026 per la V8.0.0, che su Windows legge i record della console invece di
passare da getwch.
Il banco a iniezione, banco_key.py, dice se la traduzione dei codici e'
giusta, ma non sa quali codici produca la tastiera che si ha sotto le dita,
e nemmeno se la console li consegni tutti quando il programma gira dentro un
terminale invece che in una finestra sua. Per quello serve premere davvero,
ed e' cio' che questo collaudo chiede.
Ogni prova dice quale tasto premere e cosa key dovrebbe rispondere. Se la
risposta e' quella, si passa avanti da soli. Se e' diversa, il collaudo si
ferma e offre di ripetere, di saltare o di annotare.
Si lancia con
  python collaudo_key.py
"""
import sys

from collaudo_comune import Esiti

from GBUtils import key

ESITI = Esiti("collaudo_key_esiti.txt",
	"Collaudo di key V8.0.0, la lettura dei record della console.\n"
	"Ogni riga e' una prova in cui la tastiera ha detto qualcosa di diverso da cio' che ci si aspettava.",
	etichetta="PROVA")

# Le prove riparate dalla V8.0.0: prima di lei queste combinazioni arrivavano
# confuse con altre, o non arrivavano affatto. Accanto, cosa rispondeva la
# V7.0.0, cosi' che una risposta vecchia si riconosca subito.
RIPARATE = [
	("Ctrl e PagSu del blocco dedicato", "ctrl-pageup", "f12"),
	("F12", "f12", "f12"),
	("Maiusc e freccia sinistra", "shift-left", "left"),
	("Maiusc e Canc del blocco dedicato", "shift-delete", "delete"),
	("Maiusc e Tab", "shift-tab", "\t"),
	("Ctrl, Maiusc e freccia destra", "shift-ctrl-right", "ctrl-right"),
	("Alt e Home del tastierino, con il blocco numerico spento", "alt-pad-home", "niente"),
]
# Le prove di controllo: qui la V8.0.0 non deve aver cambiato niente, perche'
# sono i nomi che i quaranta programmi che chiamano key confrontano davvero.
INVARIATE = [
	("la freccia su del blocco dedicato", "up"),
	("Ctrl e freccia sinistra", "ctrl-left"),
	("Home del tastierino, con il blocco numerico spento", "pad-home"),
	("il 5 del tastierino, con il blocco numerico spento", "pad-center"),
	("Ctrl e A", "ctrl-a"),
	("Ctrl e Backspace", "ctrl-backspace"),
	("Invio", "\r"),
	("Tab", "\t"),
	("F10", "f10"),
	("Alt e Q", "alt-q"),
	("la lettera e accentata", "è"),
	("AltGr e o accentata, che fa la chiocciola", "@"),
]

def leggibile(nome):
	"""I quattro tasti di servizio hanno un nome, non un carattere."""
	return {"\r": "Invio", "\x1b": "Escape", "\x08": "Backspace", "\t": "Tab"}.get(nome, nome)

def prova(richiesta, atteso, vecchio=""):
	"""Chiede un tasto e confronta. Vero se la risposta e' quella attesa o se
	si e' scelto di darla per buona, falso se si e' saltata."""
	while True:
		print(f"\rPremi {richiesta}\r", end="", flush=True)
		try:
			avuto = key()
		except KeyboardInterrupt:
			print("\rCtrl+C: collaudo interrotto\r")
			raise
		if avuto == atteso:
			print(f"{richiesta}: {leggibile(atteso)}, giusto")
			return True
		print(f"{richiesta}: atteso {leggibile(atteso)}, avuto {leggibile(avuto)}")
		if vecchio and avuto == vecchio:
			print("   e' la risposta della V7.0.0: qui la console non consegna il modificatore")
		scelta = key("\rr ripeti, s salta, c commenta, Invio ok\r")
		print()
		if scelta == "r":
			continue
		if scelta == "s":
			ESITI.registra(richiesta, f"saltata, aveva risposto {leggibile(avuto)}", f"atteso {leggibile(atteso)}")
			return False
		if scelta == "c":
			from GBUtils import dgt
			commento = dgt("\rCosa e' successo?\r", kind="s", smin=0, smax=300)
			ESITI.registra(richiesta, commento or "senza commento", f"atteso {leggibile(atteso)}, avuto {leggibile(avuto)}")
			return False
		ESITI.registra(richiesta, "data per buona", f"atteso {leggibile(atteso)}, avuto {leggibile(avuto)}")
		return True

def main():
	print("Collaudo di key V8.0.0.")
	print("Serve una tastiera con il blocco dedicato di")
	print("navigazione e il tastierino numerico. Dove un")
	print("tasto non c'e', si preme qualunque cosa e poi")
	print("si sceglie s per saltare la prova.")
	print()
	print("Parte 1, le combinazioni che la V8.0.0 ripara.")
	giuste = saltate = 0
	for richiesta, atteso, vecchio in RIPARATE:
		if prova(richiesta, atteso, vecchio):
			giuste += 1
		else:
			saltate += 1
	print()
	print("Parte 2, cio' che non deve essere cambiato.")
	for richiesta, atteso in INVARIATE:
		if prova(richiesta, atteso):
			giuste += 1
		else:
			saltate += 1
	print()
	print("Parte 3, i tasti che non sono un tasto.")
	print("Premi e rilascia Maiusc tre volte, poi Ctrl due")
	print("volte, poi il tasto Windows: key non deve")
	print("rispondere. Quando hai finito, premi la lettera a.")
	avuto = key()
	if avuto == "a":
		print("i modificatori da soli non svegliano key, giusto")
		giuste += 1
	else:
		print(f"qualcosa ha svegliato key: ha risposto {leggibile(avuto)}")
		ESITI.registra("modificatori premuti da soli", "hanno svegliato key", f"risposta {leggibile(avuto)}")
	print()
	print("Parte 4, Ctrl+C durante l'attesa.")
	print("E' la prova piu' importante della riscrittura:")
	print("la V8.0.0 dorme dentro il sistema, e deve")
	print("accorgersi lo stesso di Ctrl+C. Premilo adesso.")
	try:
		avuto = key()
		print(f"Ctrl+C non ha interrotto: key ha risposto {leggibile(avuto)}")
		ESITI.registra("Ctrl+C durante l'attesa", "non ha interrotto", f"risposta {leggibile(avuto)}")
	except KeyboardInterrupt:
		print("Ctrl+C ha interrotto l'attesa, giusto")
		giuste += 1
	print()
	totale = len(RIPARATE) + len(INVARIATE) + 2
	print(f"Prove {totale}, giuste {giuste}, saltate {saltate}.")
	if saltate or giuste < totale:
		print("Le differenze sono in collaudo_key_esiti.txt.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
