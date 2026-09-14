"""Banco di prova della tastiera a eventi, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto).
Nato con la V160 e la issue 37, il 14 settembre 2026.
Inietta pressioni e rilasci nel buffer della console con WriteConsoleInputW,
come fa banco_key.py, e guarda che cosa la Tastiera ne ricava: quali eventi
riferisce, quali tace, e chi risulta premuto dopo. Non serve toccare niente e
non si sente nessun suono.
Le prove che contano di piu' sono tre, e sono quelle in cui la Tastiera deve
fare meno di quanto le arriva: l'auto-ripetizione di Windows, che non deve
diventare trentadue note al secondo; il rilascio di un tasto avvenuto mentre
un modificatore e' sceso, che deve portare il nome della pressione e non un
nome nuovo; e i due shift, che sono due tasti e un nome solo.
Cio' che il banco non puo' dire e' quanti tasti la tastiera fisica riesca a
mandare insieme, perche' quello dipende dalla tastiera e non dal programma.
Si lancia con
  python banco_tastiera.py
e stampa in fondo quante prove sono passate.
"""
import ctypes
import ctypes.wintypes as w
import sys
import time

sys.path.insert(0, "E:/git/mine/GBUtils")
from GBUtils import Tastiera, key

k = ctypes.windll.kernel32
u = ctypes.windll.user32
KEY_EVENT = 1
SHIFT = 0x10
CTRL = 0x08
ALT = 0x02
ENH = 0x100
# I codici dei tasti che servono qui. Le lettere e le cifre hanno il codice
# uguale al loro carattere maiuscolo, quindi non serve elencarle.
VK_UP = 0x26
VK_SHIFT = 0x10
VK_CTRL = 0x11
VK_F1 = 0x70
# I due shift sono lo stesso codice e due scansioni diverse: e' la scansione a
# dire quale dei due, e per questo il registro sta sul tasto fisico.
SCAN_SHIFT_SINISTRO = 0x2A
SCAN_SHIFT_DESTRO = 0x36

passate = 0
totale = 0

def verifica(nome, condizione, ottenuto=None):
	global passate, totale
	totale += 1
	if condizione:
		passate += 1
		return
	print(f"SBAGLIATA: {nome}" + (f" -> {ottenuto!r}" if ottenuto is not None else ""))

class _UChar(ctypes.Union):
	_fields_ = [("UnicodeChar", w.WCHAR), ("AsciiChar", ctypes.c_char)]

class _KeyEvent(ctypes.Structure):
	_fields_ = [("bKeyDown", w.BOOL), ("wRepeatCount", w.WORD), ("wVirtualKeyCode", w.WORD),
		("wVirtualScanCode", w.WORD), ("uChar", _UChar), ("dwControlKeyState", w.DWORD)]

class _Event(ctypes.Union):
	_fields_ = [("KeyEvent", _KeyEvent), ("pad", ctypes.c_byte * 16)]

class _InputRecord(ctypes.Structure):
	_fields_ = [("EventType", w.WORD), ("Event", _Event)]

class Console:
	"""Il buffer della console, dal lato di chi ci scrive dentro."""

	def __init__(self):
		if k.GetConsoleCP() == 0:
			k.AllocConsole()
		self.manico = k.CreateFileW("CONIN$", 0x80000000 | 0x40000000, 1 | 2, None, 3, 0, None)
		if self.manico == w.HANDLE(-1).value:
			raise OSError("CONIN$ non disponibile: serve una console")

	def scrivi(self, vk, giu=True, stato=0, carattere="", scansione=None):
		record = _InputRecord()
		record.EventType = KEY_EVENT
		evento = record.Event.KeyEvent
		evento.bKeyDown = giu
		evento.wRepeatCount = 1
		evento.wVirtualKeyCode = vk
		evento.wVirtualScanCode = u.MapVirtualKeyW(vk, 0) if scansione is None else scansione
		evento.uChar.UnicodeChar = carattere or "\x00"
		evento.dwControlKeyState = stato
		scritti = w.DWORD(0)
		if not k.WriteConsoleInputW(self.manico, ctypes.byref(record), 1, ctypes.byref(scritti)):
			raise OSError(f"WriteConsoleInput fallita, errore {ctypes.GetLastError()}")

	def lettera(self, ch, giu=True, stato=0):
		"""Una lettera, con il suo codice di tasto e il suo carattere."""
		self.scrivi(ord(ch.upper()), giu=giu, stato=stato, carattere=ch)

def main():
	console = Console()
	tastiera = Tastiera()
	try:
		prove(console, tastiera)
	finally:
		tastiera.chiudi()
	print()
	print(f"Prove {totale}, passate {passate}.")
	return 0 if passate == totale else 1

def prove(console, tastiera):
	# 1. Il caso piu' semplice: un tasto scende e risale.
	tastiera.svuota()
	console.lettera("a")
	verifica("una pressione", tastiera.eventi(0.5) == [("a", "giu")], tastiera.premuti)
	verifica("dopo la pressione risulta premuto", tastiera.premuti == frozenset({"a"}), tastiera.premuti)
	console.lettera("a", giu=False)
	verifica("un rilascio", tastiera.eventi(0.5) == [("a", "su")])
	verifica("dopo il rilascio non risulta piu' premuto", tastiera.premuti == frozenset())

	# 2. L'auto-ripetizione di Windows: dopo mezzo secondo di tenuta arrivano
	# trentadue record al secondo, tutti pressioni. Devono valere per una sola.
	tastiera.svuota()
	for _volta in range(20):
		console.lettera("s")
	verifica("venti ripetizioni fanno un evento solo", tastiera.eventi(0.5) == [("s", "giu")])
	console.lettera("s", giu=False)
	verifica("e il rilascio arriva una volta sola", tastiera.eventi(0.5) == [("s", "su")])

	# 3. Il trabocchetto del nome: z scende da sola, poi scende ctrl, poi z
	# risale mentre ctrl e' ancora giu'. Accoppiando per nome, il rilascio si
	# chiamerebbe ctrl-z, che nessuno aveva mai acceso, e la nota resterebbe
	# accesa per sempre.
	tastiera.svuota()
	console.lettera("z")
	console.scrivi(VK_CTRL, stato=CTRL)
	console.lettera("z", giu=False, stato=CTRL)
	arrivati = tastiera.eventi(0.5)
	verifica("z scende, ctrl scende, z risale",
			 arrivati == [("z", "giu"), ("ctrl", "giu"), ("z", "su")], arrivati)
	verifica("resta giu' il solo ctrl", tastiera.premuti == frozenset({"ctrl"}), tastiera.premuti)
	console.scrivi(VK_CTRL, giu=False)
	verifica("e poi risale anche lui", tastiera.eventi(0.5) == [("ctrl", "su")])

	# 4. L'accordo: tre tasti insieme, ognuno con la sua pressione e il suo
	# rilascio. E' il caso della tastiera musicale.
	tastiera.svuota()
	for lettera in "zxc":
		console.lettera(lettera)
	arrivati = tastiera.eventi(0.5)
	verifica("tre tasti danno tre pressioni",
			 arrivati == [("z", "giu"), ("x", "giu"), ("c", "giu")], arrivati)
	verifica("e risultano premuti tutti e tre",
			 tastiera.premuti == frozenset({"z", "x", "c"}), tastiera.premuti)
	for lettera in "xzc":
		console.lettera(lettera, giu=False)
	arrivati = tastiera.eventi(0.5)
	verifica("i rilasci arrivano nel loro ordine",
			 arrivati == [("x", "su"), ("z", "su"), ("c", "su")], arrivati)
	verifica("e non resta premuto niente", tastiera.premuti == frozenset())

	# 5. I due shift sono due tasti fisici e un nome solo: il nome scende con
	# il primo e risale con il secondo, non prima.
	tastiera.svuota()
	console.scrivi(VK_SHIFT, stato=SHIFT, scansione=SCAN_SHIFT_SINISTRO)
	console.scrivi(VK_SHIFT, stato=SHIFT, scansione=SCAN_SHIFT_DESTRO)
	verifica("due shift, una sola pressione", tastiera.eventi(0.5) == [("shift", "giu")])
	console.scrivi(VK_SHIFT, giu=False, scansione=SCAN_SHIFT_SINISTRO)
	verifica("lasciandone uno non risale niente", tastiera.eventi(0.2) == [])
	verifica("shift risulta ancora premuto", tastiera.premuti == frozenset({"shift"}))
	console.scrivi(VK_SHIFT, giu=False, scansione=SCAN_SHIFT_DESTRO)
	verifica("lasciando il secondo risale", tastiera.eventi(0.5) == [("shift", "su")])

	# 6. I modificatori premuti da soli sono tasti a tutti gli effetti, che e'
	# la differenza voluta con key.
	tastiera.svuota()
	console.scrivi(VK_CTRL, stato=CTRL)
	console.scrivi(VK_CTRL, giu=False)
	verifica("ctrl da solo scende e risale",
			 tastiera.eventi(0.5) == [("ctrl", "giu"), ("ctrl", "su")])

	# 7. I nomi sono quelli di key, tastierino compreso.
	tastiera.svuota()
	console.scrivi(VK_UP, stato=ENH)
	console.scrivi(VK_UP, giu=False, stato=ENH)
	verifica("la freccia dedicata si chiama up",
			 tastiera.eventi(0.5) == [("up", "giu"), ("up", "su")])
	tastiera.svuota()
	console.scrivi(VK_UP)
	console.scrivi(VK_UP, giu=False)
	verifica("quella del tastierino si chiama pad-up",
			 tastiera.eventi(0.5) == [("pad-up", "giu"), ("pad-up", "su")])
	tastiera.svuota()
	console.scrivi(VK_F1)
	console.scrivi(VK_F1, giu=False)
	verifica("il tasto funzione si chiama f1",
			 tastiera.eventi(0.5) == [("f1", "giu"), ("f1", "su")])

	# 8. Un rilascio di cui non si e' vista la pressione, per esempio un tasto
	# che era gia' giu' quando la tastiera si e' aperta: non c'e' niente da
	# spegnere e non si inventa niente.
	tastiera.svuota()
	console.lettera("q", giu=False)
	verifica("un rilascio orfano non dice niente", tastiera.eventi(0.2) == [])
	verifica("e non lascia traccia", tastiera.premuti == frozenset())

	# 9. Le tre forme dell'attesa.
	tastiera.svuota()
	verifica("con zero torna subito e a mani vuote", tastiera.eventi() == [])
	inizio = time.perf_counter()
	vuoto = tastiera.eventi(0.2)
	durata = time.perf_counter() - inizio
	verifica("con un numero aspetta e poi rinuncia", vuoto == [])
	verifica("e aspetta piu' o meno quello che gli si dice",
			 0.15 <= durata <= 0.6, round(durata, 3))
	console.lettera("m")
	inizio = time.perf_counter()
	arrivati = tastiera.eventi(None)
	verifica("con None aspetta il primo evento", arrivati == [("m", "giu")], arrivati)
	verifica("e non aspetta oltre", time.perf_counter() - inizio < 0.5)
	console.lettera("m", giu=False)
	tastiera.eventi(0.5)

	# 10. Quello che arriva dietro al primo evento viene raccolto lo stesso,
	# senza aspettare oltre: e' cosi' che un accordo arriva tutto insieme.
	tastiera.svuota()
	console.lettera("a")
	console.lettera("b")
	console.lettera("c")
	inizio = time.perf_counter()
	arrivati = tastiera.eventi(5)
	verifica("il seguito arriva con il primo",
			 arrivati == [("a", "giu"), ("b", "giu"), ("c", "giu")], arrivati)
	verifica("senza consumare l'attesa", time.perf_counter() - inizio < 1.0)
	for lettera in "abc":
		console.lettera(lettera, giu=False)
	tastiera.eventi(0.5)

	# 11. tasto(), cioe' key per chi ha aperto la tastiera a eventi.
	tastiera.svuota()
	console.lettera("k")
	verifica("tasto da' il nome del tasto premuto", tastiera.tasto(attesa=0.5) == "k")
	console.lettera("k", giu=False)
	tastiera.eventi(0.5)
	verifica("tasto rinuncia alla scadenza",
			 tastiera.tasto(attesa=0.2, alla_scadenza=None) is None)
	# Il rilascio che precede il tasto non viene riferito, ma il registro lo
	# vede: dopo, quel tasto non risulta piu' premuto.
	tastiera.svuota()
	console.lettera("p")
	tastiera.eventi(0.5)
	console.lettera("p", giu=False)
	console.lettera("w")
	verifica("tasto salta i rilasci", tastiera.tasto(attesa=0.5) == "w")
	verifica("ma li ha registrati", tastiera.premuti == frozenset({"w"}), tastiera.premuti)
	# Quello che stava dietro al tasto non si perde: lo prende la prossima
	# eventi, nell'ordine in cui era arrivato.
	console.lettera("w", giu=False)
	tastiera.eventi(0.5)
	tastiera.svuota()
	console.lettera("e")
	console.lettera("r")
	verifica("tasto prende il primo", tastiera.tasto(attesa=0.5) == "e")
	verifica("e lascia il secondo alla prossima eventi",
			 tastiera.eventi(0.5) == [("r", "giu")])
	for lettera in "er":
		console.lettera(lettera, giu=False)
	tastiera.eventi(0.5)

	# 12. Chi perde il fuoco non sentira' mai quei rilasci: rilascia_tutto li
	# consegna, cosi' le note si spengono.
	tastiera.svuota()
	for lettera in "do":
		console.lettera(lettera)
	tastiera.eventi(0.5)
	verifica("prima sono giu' tutti e due", tastiera.premuti == frozenset({"d", "o"}))
	lasciati = tastiera.rilascia_tutto()
	verifica("rilascia_tutto li consegna", sorted(lasciati) == [("d", "su"), ("o", "su")], lasciati)
	verifica("e non resta niente di premuto", tastiera.premuti == frozenset())
	for lettera in "do":
		console.lettera(lettera, giu=False)
	tastiera.eventi(0.5)

	# 13. Finche' la Tastiera e' aperta, la console e' sua.
	try:
		key(attesa=0.1)
		verifica("key si ferma se c'e' una Tastiera aperta", False, "non ha sollevato niente")
	except RuntimeError as errore:
		verifica("key si ferma se c'e' una Tastiera aperta", "Tastiera" in str(errore))
	try:
		Tastiera()
		verifica("due Tastiera insieme non si possono aprire", False, "non ha sollevato niente")
	except RuntimeError:
		verifica("due Tastiera insieme non si possono aprire", True)

	# 14. Chiusa la tastiera, la console torna a key, e la tastiera chiusa non
	# si usa piu'.
	tastiera.svuota()
	tastiera.chiudi()
	try:
		tastiera.eventi()
		verifica("una tastiera chiusa non legge piu'", False, "non ha sollevato niente")
	except RuntimeError:
		verifica("una tastiera chiusa non legge piu'", True)
	console.lettera("y")
	verifica("e key torna a leggere", key(attesa=0.5) == "y")
	# key non riferisce i modificatori da soli, che era il motivo per cui la
	# tastiera a eventi serviva.
	console.scrivi(VK_SHIFT, stato=SHIFT)
	console.scrivi(VK_SHIFT, giu=False)
	verifica("key continua a non vedere lo shift da solo",
			 key(attesa=0.2, alla_scadenza=None) is None)

	# 15. Il blocco with chiude da solo, anche quando qualcosa va storto.
	with Tastiera() as dentro:
		console.lettera("n")
		verifica("dentro il with funziona", dentro.tasto(attesa=0.5) == "n")
		console.lettera("n", giu=False)
		dentro.eventi(0.5)
	console.lettera("t")
	verifica("uscendo dal with la console e' di nuovo di key", key(attesa=0.5) == "t")

	# Una misura, non una prova: quanto costa il giro completo di cento eventi
	# iniettati e riletti, per sapere che la tastiera non sara' mai il collo di
	# bottiglia di niente.
	with Tastiera() as cronometro:
		cronometro.svuota()
		for _volta in range(50):
			console.lettera("g")
			console.lettera("g", giu=False)
		inizio = time.perf_counter()
		quanti = len(cronometro.eventi(1))
		durata = (time.perf_counter() - inizio) * 1000
	print(f"Cento eventi letti in {durata:.1f} millesimi di secondo, {quanti} riferiti.")

if __name__ == "__main__":
	sys.exit(main())
