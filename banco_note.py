"""Banco di prova della lettura dei nomi di nota, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto).
Nato con la V161 e la issue 49 di Chitabry, il 14 settembre 2026.
Il nome di una nota si leggeva in due posti: in Chitabry, dove conosceva anche
i microtoni, e dentro Acusticator, dove non li conosceva e si fermava alle
ottave di una cifra. Adesso si legge in un posto solo, e la promessa fatta e'
che nessuno dei due chiamanti cambi risposta.
Il banco tiene qui dentro le due vecchie copie, ricopiate parola per parola da
come erano, e le confronta con la nuova su tutti i nomi che si possono
scrivere: dodici semitoni per dieci ottave, le alterazioni, i microtoni, il
trattino di music21, le maiuscole e una manciata di scritture sbagliate.
Dove le due vecchie rispondevano in modo diverso fra loro, il banco lo dice
esplicitamente invece di far finta di niente: sono le estensioni che
Acusticator guadagna passando alla funzione condivisa.
Si lancia con
  python banco_note.py
e stampa in fondo quante prove sono passate.
"""
import re
import sys

sys.path.insert(0, "E:/git/mine/GBUtils")
from GBUtils import frequenza_nota, scomponi_nota

passate = 0
totale = 0

def verifica(nome, condizione, ottenuto=None):
	global passate, totale
	totale += 1
	if condizione:
		passate += 1
		return
	print(f"SBAGLIATA: {nome}" + (f" -> {ottenuto!r}" if ottenuto is not None else ""))

# La copia che stava in Chitabry, GBAudio.py fino alla 8.1.0.
_SEMITONI = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
_MICROTONI = (("~~", 1.5), ("``", -1.5), ("~", 0.5), ("`", -0.5))
_RE_OTTAVA = re.compile(r"\d+$")
_RE_NOTA = re.compile(r"^([a-g])([#b]?)$")

def chitabry_scomponi(nome):
	if not isinstance(nome, str):
		return None
	testo = nome.strip().lower().replace('-', 'b')
	if testo == 'p':
		return None
	ottava = _RE_OTTAVA.search(testo)
	if not ottava:
		return None
	base = testo[:ottava.start()]
	micro = 0.0
	for simbolo, scostamento in _MICROTONI:
		if base.endswith(simbolo):
			micro = scostamento
			base = base[:-len(simbolo)]
			break
	lettera = _RE_NOTA.match(base)
	if not lettera:
		return None
	nota, alterazione = lettera.groups()
	semitono = _SEMITONI[nota] + {'#': 1, 'b': -1}.get(alterazione, 0)
	return 12 + semitono + 12 * int(ottava.group()), micro

def chitabry_frequenza(note):
	if isinstance(note, (int, float)) and not isinstance(note, bool):
		return float(note)
	scomposta = chitabry_scomponi(note)
	if scomposta is None:
		return 0.0
	midi_num, micro = scomposta
	return 440.0 * (2.0 ** ((midi_num + micro - 69) / 12.0))

# La copia che stava dentro _sintetizza di Acusticator fino alla V160, per la
# sola parte che leggeva un nome singolo.
def acusticator_nome(p):
	match = re.match(r"^([a-g])([#b]?)(\d)$", p)
	if not match:
		raise ValueError(f"Formato nota non valido: '{p}'.")
	note_letter, accidental, octave_str = match.groups()
	octave = int(octave_str)
	note_base = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
	semitone = note_base[note_letter]
	if accidental == '#':
		semitone += 1
	elif accidental == 'b':
		semitone -= 1
	midi_num = 12 + semitone + 12 * octave
	return 440.0 * (2.0 ** ((midi_num - 69) / 12.0))

def tutti_i_nomi():
	"""Ogni nome che si possa scrivere: lettere, alterazioni, microtoni e
	ottave, piu' le maiuscole e il trattino che music21 usa per il bemolle."""
	for lettera in "abcdefg":
		for alterazione in ("", "#", "b", "-"):
			for micro in ("", "~", "`", "~~", "``"):
				for ottava in range(10):
					yield f"{lettera}{alterazione}{micro}{ottava}"
	for lettera in "ABCDEFG":
		for ottava in (2, 4, 7):
			yield f"{lettera}{ottava}"
			yield f"{lettera}#{ottava}"

def main():
	# 1. Chitabry non deve sentire nessuna differenza, su nessun nome.
	diverse = []
	quanti = 0
	for nome in tutti_i_nomi():
		quanti += 1
		uguale = (chitabry_scomponi(nome) == scomponi_nota(nome)
				  and abs(chitabry_frequenza(nome) - frequenza_nota(nome)) <= 1e-9)
		if not uguale:
			diverse.append(nome)
	verifica(f"i {quanti} nomi di Chitabry danno la stessa risposta", not diverse, diverse[:5])

	# 2. Acusticator: sui nomi che la sua copia accettava, stessa frequenza.
	quanti = 0
	diverse = []
	for lettera in "abcdefg":
		for alterazione in ("", "#", "b"):
			for ottava in range(10):
				nome = f"{lettera}{alterazione}{ottava}"
				quanti += 1
				if abs(acusticator_nome(nome) - frequenza_nota(nome)) > 1e-9:
					diverse.append(nome)
	verifica(f"i {quanti} nomi di Acusticator danno la stessa frequenza", not diverse, diverse[:5])

	# 3. Il la del diapason e le ottave intorno, a mano.
	verifica("il la centrale e' a 440", frequenza_nota("a4") == 440.0, frequenza_nota("a4"))
	verifica("un'ottava sotto e' la meta'", abs(frequenza_nota("a3") - 220.0) < 1e-9)
	verifica("un'ottava sopra e' il doppio", abs(frequenza_nota("a5") - 880.0) < 1e-9)
	verifica("il do centrale sta a 261,6", abs(frequenza_nota("c4") - 261.6255653) < 1e-6, frequenza_nota("c4"))
	verifica("il numero MIDI del la centrale e' 69", scomponi_nota("a4") == (69, 0.0))

	# 4. Le alterazioni, compreso il trattino che scrive music21.
	verifica("il diesis alza di un semitono", scomponi_nota("c#4")[0] == scomponi_nota("c4")[0] + 1)
	verifica("il bemolle abbassa di un semitono", scomponi_nota("db4")[0] == scomponi_nota("d4")[0] - 1)
	verifica("il trattino vale come il bemolle", scomponi_nota("d-4") == scomponi_nota("db4"))
	verifica("do diesis e re bemolle sono la stessa nota", scomponi_nota("c#4") == scomponi_nota("db4"))

	# 5. I microtoni, che Acusticator non conosceva.
	verifica("la tilde alza di un quarto di tono", scomponi_nota("f~5")[1] == 0.5)
	verifica("l'accento grave abbassa di un quarto", scomponi_nota("f`5")[1] == -0.5)
	verifica("la doppia tilde alza di tre quarti", scomponi_nota("f~~5")[1] == 1.5)
	verifica("il doppio accento abbassa di tre quarti", scomponi_nota("f``5")[1] == -1.5)
	verifica("il quarto di tono si sente nella frequenza",
			 frequenza_nota("a4") < frequenza_nota("a~4") < frequenza_nota("a#4"),
			 (frequenza_nota("a4"), frequenza_nota("a~4"), frequenza_nota("a#4")))
	verifica("la doppia tilde non viene letta come una singola",
			 scomponi_nota("f~~5")[1] != scomponi_nota("f~5")[1])

	# 6. Le maiuscole sono la stessa cosa delle minuscole.
	verifica("le maiuscole valgono uguale", scomponi_nota("C#4") == scomponi_nota("c#4"))
	verifica("gli spazi intorno non contano", scomponi_nota("  a4  ") == scomponi_nota("a4"))

	# 7. Quello che non e' una nota.
	for storto in ("", "p", "h4", "c", "4", "c#", "ciao", "c4x", None, [], "c##4"):
		verifica(f"{storto!r} non e' una nota", scomponi_nota(storto) is None, scomponi_nota(storto))
		verifica(f"{storto!r} non ha frequenza", frequenza_nota(storto) == 0.0, frequenza_nota(storto))

	# 8. I numeri sono gia' frequenze, i valori logici no.
	verifica("un intero e' una frequenza", frequenza_nota(880) == 880.0)
	verifica("un decimale resta com'e'", frequenza_nota(432.5) == 432.5)
	verifica("vero non e' un hertz", frequenza_nota(True) == 0.0, frequenza_nota(True))
	verifica("falso nemmeno", frequenza_nota(False) == 0.0)

	# 9. Le ottave a piu' cifre passano, dove la copia di Acusticator si
	# fermava a una sola: e' un'estensione, non un cambio di risposta.
	verifica("l'ottava a due cifre si legge", scomponi_nota("c10") is not None)
	verifica("e vale un'ottava sopra la nove",
			 scomponi_nota("c10")[0] == scomponi_nota("c9")[0] + 12)
	acusticator_la_rifiuta = False
	try:
		acusticator_nome("c10")
	except ValueError:
		acusticator_la_rifiuta = True
	verifica("la vecchia copia di Acusticator la rifiutava", acusticator_la_rifiuta)

	# 10. Una quartina con un nome illeggibile non deve suonare niente, e non
	# deve far cadere il programma: e' come Acusticator si e' sempre comportato.
	from GBUtils import _sintetizza
	buona = _sintetizza(["a4", 0.05, 0, 0.5])
	storta = _sintetizza(["h9", 0.05, 0, 0.5])
	verifica("una nota buona produce campioni", buona is not None and len(buona) > 0)
	# Niente campioni affatto: la quartina viene scartata e riferita a schermo.
	verifica("una illeggibile non ne produce nessuno",
			 storta is None or len(storta) == 0, storta)

	print()
	print(f"Prove {totale}, passate {passate}.")
	return 0 if passate == totale else 1

if __name__ == "__main__":
	sys.exit(main())
