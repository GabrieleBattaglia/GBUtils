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
		# atteso e' il valore che la funzione deve restituire, oppure un
		# controllo, cioe' una funzione che riceve l'esito e dice se va bene:
		# serve quando il valore e' un testo lungo che il banco non ricopia.
		if callable(atteso):
			if not atteso(esito):
				problemi.append(f"esito rifiutato dal controllo: {esito!r}")
		elif esito != atteso:
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
	# V5.2.0, issue 52: il completamento si lascia ricopiare, e fra le chiavi
	# uguali a meno delle maiuscole vince quella identica.
	SCALE = {"blues": "", "blues_maggiore": "", "bebop": ""}
	b.prova("la parola intera dopo il completamento", ["b", "l", "u", "e", "s", INVIO], "blues", non_contiene=["bluesues"], d=SCALE)
	b.prova("la parola intera, maiuscole a caso", ["B", "L", "U", "e", "S", INVIO], "blues", d=SCALE)
	b.prova("ricopiare e poi proseguire", ["s", "u", "s", "4"], "sus4", d={"sus2": "", "sus4": "", "maj": ""})
	b.prova("una lettera diversa si aggiunge in coda come prima", ["b", "l", "_"], "blues_maggiore", d=SCALE)
	b.prova("backspace dopo il completamento, poi la lettera tolta", ["b", "l", BACKSPACE, "s", INVIO], "blues", d=SCALE)
	SIGLE = {"M9": "maggiore nona", "m9": "minore nona", "M11": "", "m11": "", "7": ""}
	b.prova("m9 sceglie la minuscola", ["m", "9", INVIO], "m9", d=SIGLE)
	b.prova("M9 sceglie la maiuscola", ["M", "9", INVIO], "M9", d=SIGLE)
	b.prova("m e il completamento tengono la minuscola", ["m", INVIO], "m11", d={"M11": "", "m11": ""})
	b.prova("M e il completamento tengono la maiuscola", ["M", INVIO], "M11", d={"M11": "", "m11": ""})
	b.prova("ricopiando, la minuscola digitata conta", ["x", "a", "b", INVIO], "xab", d={"xAB": "", "xab": ""})
	b.prova("senza ricopiare vince il completamento", ["x", INVIO], "xAB", d={"xAB": "", "xab": ""})
	b.prova("senza una chiave identica vince la prima come prima", ["A", "B", INVIO], "ab", d={"ab": "", "abc": ""})
	# V5.2.2, dalla revisione: una lettera che vale sia come ricopiata sia come
	# seguito del completamento apre due letture, e le separa il tasto dopo.
	NUMERI = {"10": "", "100": "", "1000": "", "2": ""}
	b.prova("chi scrive 10 per intero riceve 10", ["1", "0", INVIO], "10", d=NUMERI)
	b.prova("chi scrive 100 per intero riceve 100", ["1", "0", "0", INVIO], "100", d=NUMERI)
	b.prova("chi scrive 1000 per intero riceve 1000", ["1", "0", "0", "0"], "1000", d=NUMERI)
	MAMME = {"mamma": "", "mammut": ""}
	b.prova("m e a scelgono subito mamma", ["m", "a"], "mamma", d=MAMME)
	b.prova("m e u scelgono mammut", ["m", "u"], "mammut", d=MAMME)
	PRESET = {"Laser_destra_sinistra": "", "laser_da_gioco_1": "", "lampo": ""}
	b.prova("las ed e scelgono subito Laser_destra_sinistra", ["l", "a", "s", "e"], "Laser_destra_sinistra", d=PRESET)
	b.prova("las ed a scelgono subito laser_da_gioco_1", ["l", "a", "s", "a"], "laser_da_gioco_1", d=PRESET)
	b.prova("chi ricopia laser_da, alla e, finisce su Laser_destra_sinistra", ["l", "a", "s", "e", "r", "_", "d", "a"], "Laser_destra_sinistra", d=PRESET)
	b.prova("chi ricopia laser_de arriva a Laser_destra_sinistra", ["l", "a", "s", "e", "r", "_", "d", "e"], "Laser_destra_sinistra", d=PRESET)
	b.prova("con aab e aaab, b sceglie subito aab", ["b"], "aab", d={"aab": "", "aaab": ""})
	b.prova("e a, che il prompt (A, B)>aa suggerisce, sceglie subito aaab", ["a"], "aaab", d={"aab": "", "aaab": ""})
	# V5.2.3, dalla seconda revisione: le letture restano aperte anche quando
	# coincidono per piu' di un tasto. Nella V5.2.2 la seconda si perdeva, e
	# c i s p u n t a lasciava il filtro vuoto.
	CASELLE = {"cas_disponibili_spunta": "", "cas_disponibili_tolta": "", "cas_due": ""}
	b.prova("c, i, s, p, u arrivano a cas_disponibili_spunta", ["c", "i", "s", "p", "u"], "cas_disponibili_spunta", d=CASELLE)
	b.prova("c, i, t arrivano a cas_disponibili_tolta", ["c", "i", "t"], "cas_disponibili_tolta", d=CASELLE)
	b.prova("chi ricopia cas_dis, alla s, finisce su cas_disponibili_spunta", ["c", "a", "s", "_", "d", "i", "s"], "cas_disponibili_spunta", d=CASELLE)
	# V5.2.4, dalla terza revisione: Invio su un prefisso ambiguo non sceglie
	# da una lettura nata tasti prima, che lo schermo non mostra. Nella V5.2.3
	# a, b, _ e Invio davano ab_b_c. Una lettura sorella, nata all'ultimo
	# tasto, sceglie ancora la sua unica voce.
	b.prova("a, b, _ e Invio non scelgono da una lettura nascosta", ["a", "b", "_", INVIO, ESC], None, d={"ab_b": "", "ab_b_c": "", "ab_d": ""})
	# V5.2.5, dal collaudo di Gabriele del 14 novembre 2026: la lettera
	# aggiunta a cio' che il prompt mostra sceglie subito, quando lascia una
	# voce sola, anche se vale come ricopiata. La ricopiatura resta dove la
	# lettera non e' un seguito, o dove il seguito lascia piu' voci.
	b.prova("la e suggerita sceglie senza un altro tasto", ["l", "a", "s", "e"], "Laser_destra_sinistra",
			contiene=[">laser_d"], d={"Laser_destra_sinistra": "", "laser_da_gioco_1": "", "laser_da_gioco_2": ""})
	b.prova("il seguito che lascia due voci non sceglie", ["l", "a", "s", "a", INVIO, ESC], None,
			d={"Laser_destra_sinistra": "", "laser_da_gioco_1": "", "laser_da_gioco_2": ""})
	b.prova("una lettura nascosta non sceglie subito", ["a", "b", "_", ESC], None, d={"ab_b": "", "ab_b_c": "", "ab_d": ""})
	b.prova("numerato: la cifra che lascia un numero solo sceglie", ["1", "2"], "v12", d=LUNGO, numbered=True, show=False)
	# V5.2.2, dalla revisione: Invio a vuoto restituisce empty_enter anche
	# quando il completamento ha gia' scritto l'inizio comune delle voci.
	b.prova("Invio a vuoto con un inizio comune restituisce empty_enter", [INVIO], "vuoto", d={"mess_albo_che_scorre": "", "mess_albo_d_oro": ""}, empty_enter="vuoto")
	b.prova("e con 10, 100 e 1000 non sceglie 10", [INVIO], "vuoto", d={"10": "", "100": "", "1000": ""}, empty_enter="vuoto", show=False)
	b.prova("senza empty_enter Invio a vuoto restituisce None", [INVIO], None, d={"fiches_100000": "", "fiches_1000000": ""})
	b.prova("dopo backspace fino a vuoto, Invio restituisce empty_enter", ["x", BACKSPACE, INVIO], "vuoto", d={"xa": "", "xb": "", "ya": "", "yb": ""}, empty_enter="vuoto")
	# V5.2.0, issue 62: l'intestazione prima di ogni elenco.
	RIGA = "Nome, spiegazione, numero DL."
	b.prova("l'intestazione sta prima dell'elenco", [], None, contiene=[f"{RIGA}\nalfa: Primo\n"], d=TRE, show_only=True, intestazione=RIGA)
	b.prova("e torna prima di ogni elenco", ["?", "b"], "beta", contiene=[f"(A, B, G)>\n{RIGA}\nalfa: Primo"], d=TRE, show=False, intestazione=RIGA)
	b.prova("anche prima dell'elenco filtrato", ["a", "e"], "abete", contiene=[f"(A, C)>a\n{RIGA}\nabaco: 2\nabete: 1\n(2 / 2)\n"],
			d=AMBIGUE, intestazione=RIGA)
	b.prova("senza voci da mostrare l'intestazione non c'e'", ["z", ESC], None, non_contiene=[RIGA], d=TRE, intestazione=RIGA, show=False)
	b.prova("senza intestazione l'elenco e' quello di prima", [], None, contiene=["(3 / 3)\n"], non_contiene=[RIGA], d=TRE, show_only=True)
	# V5.2.6, dal collaudo di Gabriele del 14 novembre 2026: ordered non
	# distingue le maiuscole. Fino alla V5.2.5 Alfa e Delta venivano prima
	# di beta.
	MISTE = {"beta": "", "Delta": "", "alfa": "", "Gamma": "", "+": "nuovo"}
	b.prova("l'ordine non distingue le maiuscole", [], None, contiene=["+: nuovo\nalfa\nbeta\nDelta\nGamma\n(5 / 5)\n"], d=MISTE, show_only=True)
	b.prova("e le lettere suggerite lo seguono", [ESC], None, contiene=["(+, A, B, D, G)>"], d=MISTE)
	b.prova("numerato, lo stesso ordine", ["2"], "beta", contiene=["1. a\n2. b\n3. d\n4. g\n"], d={"beta": "b", "Alfa": "a", "Gamma": "g", "delta": "d"}, numbered=True)
	b.prova("a parita' la maiuscola prima", [], None, contiene=["M9: maggiore\nm9: minore\n"], d={"m9": "minore", "M9": "maggiore"}, show_only=True)
	b.prova("chiavi che non sono testo, numerate, in ordine di numero", [], None, contiene=["1. due\n2. dieci\n3. cento\n"],
			d={100: "cento", 2: "due", 10: "dieci"}, numbered=True, show_only=True)
	b.prova("ordered falso lascia l'ordine del dizionario", [], None, contiene=["beta\nDelta\nalfa\n"], d={"beta": "", "Delta": "", "alfa": ""}, show_only=True, ordered=False)
	print(f"Prove {b.totale}, passate {b.passate}.")
	return 0 if b.passate == b.totale else 1

if __name__ == "__main__":
	sys.exit(main())
