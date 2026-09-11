"""Banco di prova di enter_escape su Windows, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode).
Nato con la V2.0.0 di enter_escape, l'11 settembre 2026.
Inietta i tasti nel buffer della console con la tecnica di banco_key.py e usa
il corridore di banco_menu.py: chiama enter_escape con l'uscita catturata e
confronta cio' che restituisce e cio' che stampa con cio' che ci si aspetta,
una riga per prova. Verifica che un tasto speciale faccia ripetere il prompt
una volta sola, che la guida si dica solo se il chiamante la passa, che la
scadenza restituisca None e riparta dopo un tasto sbagliato, e che Ctrl+C
interrompa.
Si lancia con
  python banco_enter_escape.py
e stampa in fondo quante prove sono passate.
"""
import sys
import threading

from banco_menu import (
	ALT_Q,
	CTRL_A,
	CTRL_C,
	ESC,
	F1,
	INVIO,
	SU,
	TAB,
	BancoUscita,
	tasto,
)

from GBUtils import enter_escape


class BancoEnterEscape(BancoUscita):
	funzione = staticmethod(enter_escape)
	# La frase che enter_escape diceva di suo fino alla V1.1.
	parole_vietate = ("Conferma con invio",)

def main():
	b = BancoEnterEscape()
	b.prova("invio conferma", [INVIO], True, contiene=["Domanda? \n"], prompt="Domanda? ")
	b.prova("esc annulla", [ESC], False, contiene=["Domanda? \n"], prompt="Domanda? ")
	b.prova("freccia su: il prompt si ripete una volta sola", [SU, INVIO], True, contiene=["Domanda? \nDomanda? \n"], non_contiene=["up", "Domanda? \nDomanda? \nDomanda?"], prompt="Domanda? ")
	b.prova("f1, tab, ctrl+a, alt+q, poi esc", [F1, TAB, CTRL_A, ALT_Q, ESC], False, contiene=["Domanda? \n" * 5], non_contiene=["f1", "\t", "ctrl-a", "alt-q"], prompt="Domanda? ")
	b.prova("lettera, poi invio", ["q", INVIO], True, contiene=["Domanda? \nDomanda? \n"], non_contiene=["q"], prompt="Domanda? ")
	b.prova("la guida del chiamante, prima del prompt ripetuto", [SU, INVIO], True, contiene=["Domanda? \nSolo Invio o Esc\nDomanda? \n"], prompt="Domanda? ", guida="Solo Invio o Esc")
	b.prova("senza prompt: solo gli a capo", [SU, ESC], False, contiene=["\n\n"], non_contiene=["Domanda"])
	b.prova("scadenza senza risposta: None", [], None, contiene=["Domanda? \n"], prompt="Domanda? ", attesa=0.3)
	# La scadenza riparte dopo un tasto sbagliato: q a sei decimi e Invio a
	# tredici, con un secondo di attesa. Senza la ripartenza l'attesa scadrebbe
	# al secondo, prima dell'Invio, e tornerebbe None.
	threading.Timer(0.6, b.inietta, tasto("q")).start()
	threading.Timer(1.3, b.inietta, INVIO).start()
	b.prova("un tasto sbagliato fa ripartire l'attesa", [], True, contiene=["Domanda? \nDomanda? \n"], prompt="Domanda? ", attesa=1)
	b.prova("ctrl c interrompe", [CTRL_C], "KeyboardInterrupt", prompt="Domanda? ")
	print(f"Prove {b.totale}, passate {b.passate}.")
	return 0 if b.passate == b.totale else 1

if __name__ == "__main__":
	sys.exit(main())
