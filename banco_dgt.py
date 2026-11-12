"""Banco di prova di dgt, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 con la V3.0.0 di dgt, per la issue 45.
Non aspetta la tastiera: al posto di input e di getpass ci sono due finte
che rispondono da un copione, e cio' che dgt stampa si cattura.
Le domande sono tre. Un valore fuori dai limiti, o non del tipo chiesto, si
rifiuta e la domanda si ripete, invece di essere cambiato? dgt non dice piu'
parole sue, ma soltanto i limiti in cifre, oppure le frasi del chiamante? E il
predefinito si comporta come prima?
Si lancia con
  python banco_dgt.py
e stampa in fondo quante prove sono passate.
"""
import contextlib
import getpass
import io
import sys

import GBUtils
from GBUtils import dgt

# Le frasi che dgt diceva fino alla V2.0.0 e non deve dire piu'.
VIETATE = ("Serve", "Troppo", "accettat", "Lunghezza fuori", "Fuori dai limiti")
totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def chiedi(risposte, **argomenti):
	"""Chiama dgt con le risposte date in ordine. Restituisce il valore, le
	righe stampate e quante volte la domanda e' stata fatta."""
	coda = list(risposte)
	domande = []
	def finta(prompt=""):
		domande.append(prompt)
		if not coda:
			raise EOFError
		return coda.pop(0)
	GBUtils.input = finta
	getpass.getpass = finta
	uscita = io.StringIO()
	try:
		with contextlib.redirect_stdout(uscita):
			valore = dgt(**argomenti)
	except (ValueError, TypeError, EOFError) as errore:
		valore = type(errore).__name__
	finally:
		del GBUtils.input
	righe = [r for r in uscita.getvalue().split("\n") if r]
	return valore, righe, len(domande)

def senza_vietate(righe):
	return not any(v in r for r in righe for v in VIETATE)

print("Banco di dgt. Nessuna tastiera, nessun file.")

# 1. I numeri fuori dai limiti si rifiutano.
valore, righe, volte = chiedi(["0", "9", "3"], prompt="Quante? ", kind="i", imin=1, imax=5)
prova("un intero fuori dai limiti si rifiuta, due volte", valore == 3 and volte == 3, (valore, volte))
prova("e dgt dice soltanto i limiti in cifre", righe == ["1 - 5", "1 - 5"] and senza_vietate(righe), righe)
valore, righe, _ = chiedi(["tre", "2"], kind="i", imin=1, imax=5)
prova("un intero che non si legge si rifiuta, con i limiti", valore == 2 and righe == ["1 - 5"], (valore, righe))
valore, righe, _ = chiedi(["tre", "2"], kind="i")
prova("senza limiti dichiarati, la domanda si ripete e basta", valore == 2 and righe == [], (valore, righe))
valore, righe, _ = chiedi(["0", "4"], kind="i", imin=1)
prova("col solo minimo, le cifre dicono >= 1", valore == 4 and righe == [">= 1"], righe)
valore, righe, _ = chiedi(["11", "4"], kind="i", imax=10)
prova("col solo massimo, le cifre dicono <= 10", valore == 4 and righe == ["<= 10"], righe)
valore, righe, _ = chiedi(["99999999999", "4"], kind="i")
prova("oltre i limiti di serie, le cifre li nominano", valore == 4 and righe == ["-999999999 - 999999999"], righe)
prova("e un intero torna intero", isinstance(valore, int))

# 2. I decimali.
valore, righe, volte = chiedi(["nan", "inf", "mezzo", "1.5", "0.5"], kind="f", fmin=0, fmax=1)
prova("nan, inf e una parola non sono decimali", valore == 0.5 and volte == 5, (valore, volte))
prova("e le cifre dicono 0 - 1, senza il punto zero", righe == ["0 - 1"] * 4, righe)
valore, righe, _ = chiedi(["3", "1"], kind="f", fmin=0.5, fmax=2.5)
prova("i limiti decimali si scrivono come sono", valore == 1.0 and righe == ["0.5 - 2.5"], righe)

# 3. Le stringhe non si tagliano piu'.
valore, righe, volte = chiedi(["no", "n"], prompt="Raddoppi? ", kind="s", smax=1)
prova("il no di PokerMachine si rifiuta invece di diventare n", valore == "n" and volte == 2, (valore, volte))
prova("e dgt dice la lunghezza e quella ammessa", righe == ["2 / 1"], righe)
valore, righe, _ = chiedi(["123456", "12345"], kind="s", smax=5)
prova("le carte di PokerMachine non si tagliano", valore == "12345" and righe == ["6 / 5"], (valore, righe))
valore, righe, _ = chiedi(["ab", "abc"], kind="s", smin=3)
prova("una stringa troppo corta si rifiuta, con la sua lunghezza", valore == "abc" and righe == ["2 / 3"], righe)
valore, righe, _ = chiedi(["  spazi  "], kind="s")
prova("cio' che si digita torna fedele, spazi compresi", valore == "  spazi  " and righe == [])

# 4. La password: stessa regola, e cio' che si digita non compare mai.
valore, righe, _ = chiedi(["segretissima", "abcd"], kind="s", smax=4, pwd=True)
prova("una password troppo lunga si rifiuta", valore == "abcd" and righe == ["12 / 4"], righe)
prova("e non compare in quello che dgt stampa", not any("segret" in r for r in righe))

# 5. Le frasi del chiamante.
italiano = {"non_intero": "Serve un numero.", "troppo_basso": "Almeno {minimo}.", "troppo_alto": "Al massimo {massimo}."}
valore, righe, _ = chiedi(["x", "0", "6", "5"], kind="i", imin=1, imax=5, avvisi=italiano)
prova("le frasi del chiamante prendono il posto delle cifre", valore == 5 and righe == ["Serve un numero.", "Almeno 1.", "Al massimo 5."], righe)
valore, righe, _ = chiedi(["troppo", "ok"], kind="s", smax=3, avvisi={"troppo_lunga": "{lunghezza} caratteri, al massimo {massimo}."})
prova("nelle stringhe minimo e massimo sono lunghezze", righe == ["6 caratteri, al massimo 3."], righe)
valore, righe, _ = chiedi(["0", "2"], kind="i", imin=1, imax=5, avvisi={"troppo_basso": ""})
prova("una frase vuota fa tacere quella situazione", valore == 2 and righe == [], righe)
valore, righe, _ = chiedi(["9", "2"], kind="i", imin=1, imax=5, avvisi={"troppo_basso": "Almeno {minimo}."})
prova("dove manca la frase restano le cifre", righe == ["1 - 5"], righe)
prova("una chiave sconosciuta e' un errore di chi programma", chiedi(["1"], kind="i", avvisi={"basso": "x"})[0] == "ValueError")
prova("e cosi' un segno fra graffe sconosciuto", chiedi(["1"], kind="i", avvisi={"troppo_alto": "{limite}"})[0] == "ValueError")
prova("e una frase che non e' una stringa, con TypeError", chiedi(["1"], kind="i", avvisi={"troppo_alto": 3})[0] == "TypeError")

# 6. Il predefinito si comporta come prima.
prova("Invio con il predefinito lo restituisce", chiedi([""], kind="i", imin=1, imax=9, default=4)[0] == 4)
prova("un predefinito fuori dai limiti torna dentro, come prima", chiedi([""], kind="i", imin=1, imax=5, default=7)[0] == 5)
prova("un predefinito lungo si taglia a smax, come prima", chiedi([""], kind="s", smax=3, default="lunghissimo")[0] == "lun")
prova("con smax alto il predefinito lungo resta intero", chiedi([""], kind="s", smax=5000, default="x" * 1000)[0] == "x" * 1000)
prova("un predefinito non convertibile e' un errore di chi programma", chiedi([""], kind="i", default="sette")[0] == "ValueError")
prova("senza terminale si riceve EOFError", chiedi([], kind="s")[0] == "EOFError")
prova("i limiti incoerenti restano un errore", chiedi(["1"], kind="i", imin=5, imax=1)[0] == "ValueError")

print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
