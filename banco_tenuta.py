"""Banco della tenuta dei tasti, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 13 settembre 2026, per sapere se una tastiera musicale vera si possa
fare dentro una console.
key consegna un tasto per pressione e non dice mai quando il tasto viene
lasciato: va bene per un menu, non per una nota che deve durare finche' il
dito resta giu'. I record della console, che dalla V8.0.0 key legge, portano
pero' anche il rilascio e il conteggio delle ripetizioni; quello che nessuna
prova a tavolino puo' dire e' se la tastiera fisica e il terminale in cui il
programma gira li facciano davvero arrivare fin qui.
Questo banco legge i record grezzi, senza passare da key, e riferisce cosa e'
arrivato. Non modifica niente e non tocca il modo della console.
Si lancia con
  python banco_tenuta.py
"""
import ctypes
import ctypes.wintypes as w
import sys
import time

k = ctypes.windll.kernel32
KEY_EVENT = 1

class _UChar(ctypes.Union):
	_fields_ = [("UnicodeChar", w.WCHAR), ("AsciiChar", ctypes.c_char)]

class _KeyEvent(ctypes.Structure):
	_fields_ = [("bKeyDown", w.BOOL), ("wRepeatCount", w.WORD), ("wVirtualKeyCode", w.WORD),
		("wVirtualScanCode", w.WORD), ("uChar", _UChar), ("dwControlKeyState", w.DWORD)]

class _Event(ctypes.Union):
	_fields_ = [("KeyEvent", _KeyEvent), ("riempimento", ctypes.c_byte * 16)]

class _InputRecord(ctypes.Structure):
	_fields_ = [("EventType", w.WORD), ("Event", _Event)]

def apri():
	manico = k.CreateFileW("CONIN$", 0x80000000 | 0x40000000, 1 | 2, None, 3, 0, None)
	if manico == w.HANDLE(-1).value:
		raise SystemExit("Nessuna console da cui leggere.")
	return manico

def raccogli(manico, durata):
	"""Tutti i record di tastiera che arrivano entro la durata, con il momento
	in cui sono arrivati."""
	k.FlushConsoleInputBuffer(manico)
	record = _InputRecord()
	letti = ctypes.c_ulong(0)
	raccolti = []
	inizio = time.perf_counter()
	while True:
		residuo = durata - (time.perf_counter() - inizio)
		if residuo <= 0:
			return raccolti
		if k.WaitForSingleObject(manico, max(1, int(residuo * 1000))) != 0:
			continue
		if not k.ReadConsoleInputW(manico, ctypes.byref(record), 1, ctypes.byref(letti)) or not letti.value:
			continue
		if record.EventType != KEY_EVENT:
			continue
		e = record.Event.KeyEvent
		raccolti.append({"quando": time.perf_counter() - inizio, "giu": bool(e.bKeyDown),
			"vk": e.wVirtualKeyCode, "ripetizioni": e.wRepeatCount,
			"carattere": e.uChar.UnicodeChar})

def nome(vk, carattere):
	if carattere and carattere >= " ":
		return repr(carattere)
	return f"vk 0x{vk:02x}"

def riassumi(raccolti):
	giu = [r for r in raccolti if r["giu"]]
	su = [r for r in raccolti if not r["giu"]]
	print(f"   record arrivati: {len(raccolti)}, di cui {len(giu)} pressioni e {len(su)} rilasci")
	if not raccolti:
		print("   nessun record: la console non ha consegnato niente")
		return
	tasti = {}
	for r in raccolti:
		voce = tasti.setdefault(r["vk"], {"giu": 0, "su": 0, "ripetizioni": 0, "carattere": r["carattere"]})
		voce["giu" if r["giu"] else "su"] += 1
		voce["ripetizioni"] += r["ripetizioni"] if r["giu"] else 0
	for vk, voce in tasti.items():
		print(f"   {nome(vk, voce['carattere']):10} pressioni {voce['giu']:3}, "
			f"ripetizioni dichiarate {voce['ripetizioni']:3}, rilasci {voce['su']:2}")
	if len(giu) > 1:
		distanze = [giu[i]["quando"] - giu[i - 1]["quando"] for i in range(1, len(giu))]
		media = sum(distanze) / len(distanze) * 1000.0
		print(f"   fra una pressione e la seguente, in media {media:.0f} millesimi di secondo")
	if giu and su:
		print(f"   prima pressione a {giu[0]['quando'] * 1000:.0f} ms, "
			f"ultimo rilascio a {su[-1]['quando'] * 1000:.0f} ms")

def prova(manico, titolo, istruzioni, durata):
	print(titolo)
	for riga in istruzioni:
		print(f"   {riga}")
	print(f"\rInvio quando sei pronto, poi hai {durata:.0f} secondi\r", end="", flush=True)
	input()
	print(f"\rVai, {durata:.0f} secondi\r", end="", flush=True)
	raccolti = raccogli(manico, durata)
	print(" " * 50)
	riassumi(raccolti)
	print()
	return raccolti

def main():
	manico = apri()
	print("Banco della tenuta dei tasti.")
	print("Serve a sapere se la console consegni anche il")
	print("rilascio dei tasti, oltre alla pressione, e se")
	print("distingua piu' tasti tenuti giu' insieme.")
	print("Non serve premere Invio durante le prove: si")
	print("preme solo per cominciarle.")
	print()
	uno = prova(manico, "Prova 1, un tasto tenuto giu'.",
		["tieni premuta la lettera a per due secondi", "poi lasciala e non toccare altro"], 4.0)
	due = prova(manico, "Prova 2, tre tasti insieme, come un accordo.",
		["premi z, poi x, poi c, senza lasciare le prime",
		 "tienile tutte e tre per un secondo",
		 "poi lasciale tutte insieme"], 5.0)
	prova(manico, "Prova 3, due note in successione veloce.",
		["batti q e poi w, alternandole in fretta", "per un paio di secondi"], 4.0)
	print("Cosa se ne ricava.")
	rilasci_uno = sum(1 for r in uno if not r["giu"])
	if rilasci_uno:
		print("   Il rilascio arriva: una nota puo' durare")
		print("   quanto il dito resta giu'.")
	else:
		print("   Il rilascio NON arriva: dentro questo")
		print("   terminale una nota tenuta non si puo' fare,")
		print("   e va provato in una console propria.")
	tasti_due = {r["vk"] for r in due if r["giu"]}
	print(f"   Nella prova dell'accordo si sono distinti {len(tasti_due)} tasti.")
	if len(tasti_due) >= 3:
		print("   Tre tasti insieme si distinguono: la")
		print("   polifonia e' possibile.")
	elif tasti_due:
		print("   Meno di tre: puo' essere il limite della")
		print("   tastiera, che non registra piu' di due o tre")
		print("   tasti insieme, e non dipende dal programma.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
