"""Banco di prova di menu su Windows, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode).
Nato con la V5.1.0 di menu, l'11 settembre 2026.
Inietta i tasti nel buffer della console con la tecnica di banco_key.py, chiama
menu con l'uscita catturata e confronta cio' che restituisce e cio' che stampa
con cio' che ci si aspetta, una riga per prova. Verifica che menu non pronunci
parole di sua iniziativa, che il conteggio abbia la forma (viste / totale) e
- (pagina / pagine), che il prompt di fine pagina stia fra due ritorni
carrello, che i tasti speciali vengano ignorati e che Ctrl+C interrompa.
Cio' che non puo' dire e' come suona tutto questo a NVDA e sul display
braille: per quello c'e' la prova in collaudo.txt.
Si lancia con
  python banco_menu.py
e stampa in fondo quante prove sono passate.
"""
import contextlib
import io
import sys
import threading

from banco_key import ALT, CTRL, ENH, VK, Banco, k

from GBUtils import menu

# Parole che menu diceva fino alla V5.0.0 e non deve dire piu'.
PAROLE_VIETATE = ("Viste", "Voci", "Scelta", "Esc per")
INVIO = (VK["enter"], 0, 13)
ESC = (VK["esc"], 0, 27)
BACKSPACE = (VK["back"], 0, 8)
CTRL_BACKSPACE = (VK["back"], CTRL, 0x7F)
TAB = (VK["tab"], 0, 9)
SU = (VK["up"], ENH, 0)
F1 = (VK["f1"], 0, 0)
CTRL_A = (ord("A"), CTRL, 1)
CTRL_C = (ord("C"), CTRL, 3)
ALT_Q = (ord("Q"), ALT, 0)
TRE = {"alfa": "Primo", "beta": "Secondo", "gamma": "Terzo"}
AMBIGUE = {"abete": "1", "abaco": "2", "cedro": "3"}
LUNGO = {f"v{i:02d}": f"voce {i}" for i in range(1, 46)}

def tasto(c):
	"""L'evento di un carattere stampabile: il codice virtuale e' la lettera
	maiuscola o la cifra, e per gli altri segni uno qualsiasi, perche' getwch
	guarda soltanto il carattere Unicode."""
	return (ord(c.upper()) if c.isalnum() else 0xBF, 0, ord(c))

class BancoUscita(Banco):
	"""Corridore per una funzione che aspetta tasti e stampa: inietta la
	sequenza, cattura l'uscita e confronta esito e testo con le attese. Le
	sottoclassi dicono quale funzione provare e quali parole non deve dire."""
	funzione = None
	parole_vietate = ()

	def __init__(self):
		super().__init__()
		self.passate = 0

	def prova(self, titolo, sequenza, atteso, contiene=(), non_contiene=(), **argomenti):
		k.FlushConsoleInputBuffer(self.hin)
		# Ogni tasto viene premuto e rilasciato, come dalla tastiera vera: senza
		# il rilascio la console fonde due pressioni identiche consecutive, per
		# esempio due Invio, in un record solo, e la seconda sparirebbe.
		for t in sequenza:
			vk, stato, ch = t if isinstance(t, tuple) else tasto(t)
			self.inietta(vk, stato, ch)
			self.inietta(vk, stato, ch, premuto=False)
		# Se menu aspetta un tasto che nessuno ha iniettato, dopo tre secondi
		# arriva un Ctrl+C: la prova fallisce invece di fermare il banco.
		guardia = threading.Timer(3.0, self.inietta, CTRL_C)
		guardia.start()
		uscita = io.StringIO()
		try:
			with contextlib.redirect_stdout(uscita):
				esito = self.funzione(**argomenti)
		except (KeyboardInterrupt, ValueError, OSError, EOFError, TypeError) as errore:
			# Le eccezioni attese si riferiscono con il loro nome, cosi' una
			# prova puo' aspettarsele come esito.
			esito = type(errore).__name__
		scaduta = not guardia.is_alive()
		guardia.cancel()
		testo = uscita.getvalue()
		problemi = []
		if scaduta and atteso != "KeyboardInterrupt":
			problemi.append("attesa scaduta, mancava un tasto")
		if esito != atteso:
			problemi.append(f"restituito {esito!r} invece di {atteso!r}")
		for pezzo in contiene:
			if pezzo not in testo:
				problemi.append(f"manca {pezzo!r}")
		for pezzo in tuple(non_contiene) + tuple(self.parole_vietate):
			if pezzo in testo:
				problemi.append(f"stampa {pezzo!r}")
		self.totale += 1
		if problemi:
			print(f"{titolo}: {'; '.join(problemi)}")
			print(f"  uscita: {testo!r}")
		else:
			self.passate += 1
			print(f"{titolo}: ok")

class BancoMenu(BancoUscita):
	funzione = staticmethod(menu)
	parole_vietate = PAROLE_VIETATE

def main():
	b = BancoMenu()
	b.prova("scelta diretta con elenco", ["b"], "beta", contiene=["alfa: Primo", "beta: Secondo", "gamma: Terzo", "(3 / 3)\n", "(A, B, G)>"], d=TRE)
	b.prova("esc annulla", [ESC], None, d=TRE)
	b.prova("invio senza niente restituisce empty_enter", [INVIO], "vuoto", d=TRE, empty_enter="vuoto")
	b.prova("filtro vuoto: conteggio zero, poi backspace", ["z", BACKSPACE, "g"], "gamma", contiene=["(0 / 0)\n", "(3 / 3)\n"], d=TRE)
	b.prova("filtro vuoto con ntf: la parola del chiamante", ["z", ESC], None, contiene=["Niente\n"], non_contiene=["(0 / 0)"], d=TRE, ntf="Niente")
	b.prova("prefisso ambiguo: invio tace, i candidati tornano", ["a", INVIO, "e"], "abete", contiene=["(A, E)>ab\nabaco: 2\nabete: 1\n(2 / 2)\n(A, E)>abe\n"], d=AMBIGUE)
	b.prova("prefisso ambiguo senza rielenco: solo il prompt", ["a", INVIO, "e"], "abete", contiene=["(A, E)>ab\n(A, E)>ab"], non_contiene=["(2 / 2)"], d=AMBIGUE, show=False)
	b.prova("tasti speciali ignorati", [SU, F1, TAB, CTRL_A, ALT_Q, "g"], "gamma", non_contiene=["ctrl-a", "alt-q", "up", "f1", "\t"], d=TRE)
	b.prova("ctrl backspace cancella come backspace", ["z", CTRL_BACKSPACE, "g"], "gamma", non_contiene=["ctrl-backspace"], d=TRE)
	b.prova("pagine: invio continua, conteggio con le pagine", [INVIO, INVIO, ESC], None, contiene=["v20: voce 20\n\r(20 / 45) - (1 / 3)\r\nv21: voce 21", "\r(40 / 45) - (2 / 3)\r", "v45: voce 45\n(45 / 45) - (3 / 3)\n"], d=LUNGO, pager=20)
	b.prova("pagine: esc interrompe l'elenco", [ESC, ESC], None, contiene=["\r(20 / 45) - (1 / 3)\r"], non_contiene=["(40 / 45)", "(45 / 45)", "v21"], d=LUNGO, pager=20)
	b.prova("pager spento: nessuna pagina nel conteggio", [], None, contiene=["(45 / 45)\n"], non_contiene=[" - ("], d=LUNGO, pager=0, show_only=True)
	b.prova("numerato", ["2"], "beta", contiene=["1. Primo\n2. Secondo\n3. Terzo\n(3 / 3)\n(1-3)> "], d=TRE, numbered=True)
	b.prova("numerato: le lettere non entrano", ["x", "3"], "gamma", non_contiene=["x"], d=TRE, numbered=True)
	b.prova("solo elenco", [], None, contiene=["(3 / 3)\n"], d=TRE, show_only=True)
	b.prova("punto interrogativo rielenca", ["?", "b"], "beta", contiene=["(A, B, G)>\nalfa: Primo\nbeta: Secondo\ngamma: Terzo\n(3 / 3)\n"], d=TRE, show=False)
	b.prova("una voce sola torna subito e in silenzio", [], "unica", non_contiene=["unica", "("], d={"unica": "x"})
	b.prova("dizionario vuoto torna None in silenzio", [], None, non_contiene=["("], d={})
	b.prova("ctrl c interrompe", [CTRL_C], "KeyboardInterrupt", d=TRE)
	print(f"Prove {b.totale}, passate {b.passate}.")
	return 0 if b.passate == b.totale else 1

if __name__ == "__main__":
	sys.exit(main())
