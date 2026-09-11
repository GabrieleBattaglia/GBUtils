"""Banco di prova di key su Windows, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, modalita' auto).
Nato con la revisione 1 di key, l'8 settembre 2026.
Inietta eventi di tastiera nel buffer della console con WriteConsoleInputW,
poi chiama key e stampa cosa restituisce, una riga per tasto. Gli eventi
passano dalla stessa tabella di traduzione che usa getwch, quindi la prova
dice la verita' sui codici della libreria di runtime di Windows, senza
bisogno di premere niente; cio' che non puo' dire e' quali eventi produca la
tastiera fisica, e per quello c'e' collaudo_key.py.
Si lancia con
  python banco_key.py
e stampa in fondo quante righe corrispondono all'etichetta. Le differenze
attese, cioe' i limiti della libreria di runtime e i tasti di servizio che
tornano come caratteri, sono elencate nella docstring di key.
"""
import ctypes
import ctypes.wintypes as w
import sys

from GBUtils import key

k = ctypes.windll.kernel32
u = ctypes.windll.user32
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
OPEN_EXISTING = 3
KEY_EVENT = 1
SHIFT = 0x10
CTRL = 0x08
ALT = 0x02
ENH = 0x100
VK = {"f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
	"f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
	"up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27, "home": 0x24, "end": 0x23,
	"pageup": 0x21, "pagedown": 0x22, "insert": 0x2D, "delete": 0x2E, "clear": 0x0C,
	"tab": 0x09, "back": 0x08, "enter": 0x0D, "esc": 0x1B, "space": 0x20}

class _UChar(ctypes.Union):
	_fields_ = [("UnicodeChar", w.WCHAR), ("AsciiChar", ctypes.c_char)]

class _KeyEvent(ctypes.Structure):
	_fields_ = [("bKeyDown", w.BOOL), ("wRepeatCount", w.WORD), ("wVirtualKeyCode", w.WORD),
		("wVirtualScanCode", w.WORD), ("uChar", _UChar), ("dwControlKeyState", w.DWORD)]

class _Event(ctypes.Union):
	_fields_ = [("KeyEvent", _KeyEvent), ("pad", ctypes.c_byte * 16)]

class _InputRecord(ctypes.Structure):
	_fields_ = [("EventType", w.WORD), ("Event", _Event)]

class Banco:
	def __init__(self):
		if k.GetConsoleCP() == 0:
			k.AllocConsole()
		self.hin = k.CreateFileW("CONIN$", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, 0, None)
		if self.hin == w.HANDLE(-1).value:
			raise OSError("CONIN$ non disponibile: serve una console")
		self.totale = 0
		self.uguali = 0

	def inietta(self, vk, stato=0, ch=0, premuto=True):
		"""Scrive un evento di tastiera: la pressione del tasto, o con premuto
		falso il suo rilascio. Il rilascio serve fra due pressioni identiche
		consecutive, perche' la console le fonderebbe in un record solo con il
		conteggio di ripetizione a due, che getwch legge una volta sola."""
		rec = _InputRecord()
		rec.EventType = KEY_EVENT
		ke = rec.Event.KeyEvent
		ke.bKeyDown = premuto
		ke.wRepeatCount = 1
		ke.wVirtualKeyCode = vk
		ke.wVirtualScanCode = u.MapVirtualKeyW(vk, 0)
		ke.uChar.UnicodeChar = chr(ch)
		ke.dwControlKeyState = stato
		scritti = w.DWORD(0)
		if not k.WriteConsoleInputW(self.hin, ctypes.byref(rec), 1, ctypes.byref(scritti)):
			raise OSError(f"WriteConsoleInput fallita, errore {ctypes.GetLastError()}")

	def prova(self, etichetta, vk, stato=0, ch=0):
		k.FlushConsoleInputBuffer(self.hin)
		self.inietta(vk, stato, ch)
		try:
			esito = key(attesa=0.3)
		except KeyboardInterrupt:
			esito = "KeyboardInterrupt"
		self.totale += 1
		if esito == etichetta:
			self.uguali += 1
		print(f"{etichetta}: {esito!r}")

	def serie(self, prefisso, nomi, stato):
		for nome in nomi:
			self.prova(f"{prefisso}{nome}", VK[nome], stato)

def main():
	b = Banco()
	print("Tasti funzione")
	fk = [f"f{i}" for i in range(1, 13)]
	b.serie("", fk, 0)
	b.serie("shift-", fk, SHIFT)
	b.serie("ctrl-", fk, CTRL)
	b.serie("alt-", fk, ALT)
	print("Navigazione dedicata, con il flag enhanced")
	nav = ["up", "down", "left", "right", "home", "end", "pageup", "pagedown", "insert", "delete"]
	b.serie("", nav, ENH)
	b.serie("ctrl-", nav, CTRL | ENH)
	b.serie("alt-", nav, ALT | ENH)
	b.serie("shift-", nav, SHIFT | ENH)
	print("Tastierino a blocco numerico spento, senza il flag enhanced")
	b.serie("pad-", nav + ["clear"], 0)
	b.serie("ctrl-pad-", nav + ["clear"], CTRL)
	b.serie("alt-pad-", nav + ["clear"], ALT)
	print("Altre combinazioni")
	b.prova("ctrl-tab", VK["tab"], CTRL)
	b.prova("ctrl-backspace", VK["back"], CTRL, 0x7F)
	b.prova("ctrl-j", VK["enter"], CTRL, 10)
	for lettera in "qazplm":
		b.prova(f"alt-{lettera}", ord(lettera.upper()), ALT)
	for cifra in "1590":
		b.prova(f"alt-{cifra}", ord(cifra), ALT)
	print("Tasti normali e di controllo")
	b.prova("\r", VK["enter"], 0, 13)
	b.prova("\x1b", VK["esc"], 0, 27)
	b.prova("\x08", VK["back"], 0, 8)
	b.prova("\t", VK["tab"], 0, 9)
	b.prova(" ", VK["space"], 0, 32)
	b.prova("ctrl-a", ord("A"), CTRL, 1)
	b.prova("ctrl-z", ord("Z"), CTRL, 26)
	b.prova("KeyboardInterrupt", ord("C"), CTRL, 3)
	b.prova("q", ord("Q"), 0, ord("q"))
	b.prova("", 0, 0, 0)
	print(f"Righe {b.totale}, uguali all'etichetta {b.uguali}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
