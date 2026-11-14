"""Banco di prova di Acu_Maker che segue il motore, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 per la issue 59, con Acu_Maker 1.11.0.
Niente di questo suona e niente tocca la collezione vera: l'editor si guida
con tasti finti, al posto del motore c'e' una finta che raccoglie cio' che
suonerebbe, e le collezioni stanno in una cartella temporanea.
Le domande sono quelle della issue: le perdite di dati che succedevano
toccando un valore, le funzioni che mancavano rispetto al motore, e le
scomodita'. Ogni sezione dice quale punto prova.
Si lancia con
  python banco_acumaker_motore.py
e stampa in fondo quante prove sono passate.
"""
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile

import Acu_Maker as am

import GBUtils
from GBUtils import Acusticator, parse_pan_values

QUI = os.path.dirname(os.path.abspath(__file__))
VERA = os.path.join(QUI, "Acu_Collection.json")
totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def impronta(percorso):
	with open(percorso, "rb") as f:
		return hashlib.sha256(f.read()).hexdigest()

def leggi(percorso):
	with open(percorso, encoding="utf-8") as f:
		return json.load(f)

def zitto(funzione, *argomenti, **chiavi):
	uscita = io.StringIO()
	with contextlib.redirect_stdout(uscita), contextlib.redirect_stderr(uscita):
		risultato = funzione(*argomenti, **chiavi)
	return risultato, uscita.getvalue()

class MotoreFinto:
	"""Al posto di Acusticator: prepara e' quello vero, il resto raccoglie."""
	def __init__(self):
		self.suonati, self.fermati, self.cicli = [], 0, []
	prepara = staticmethod(Acusticator.prepara)
	aggiorna = staticmethod(Acusticator.aggiorna)
	def __call__(self, score, kind=1, adsr=None, sync=False, pan=None):
		self.suonati.append((score, kind, adsr))
		return True
	def stop(self):
		self.fermati += 1
		return 0
	def ciclo(self, score, kind=1, adsr=None, dissolvenza=0.05, **chiavi):
		motore = self
		class Maniglia:
			attivo = True
			def stop(self):
				self.attivo = False
				motore.fermati += 1
		self.cicli.append((score, dissolvenza))
		return Maniglia()

def tasti(sequenza, scritti=()):
	"""Sostituisce la tastiera dell'editor e input con un copione."""
	coda, righe = list(sequenza), list(scritti)
	am.get_keypress = lambda: coda.pop(0) if coda else "esc"
	am.input = lambda prompt="": righe.pop(0) if righe else ""
	GBUtils.input = am.input

ULTIMA_USCITA = [""]

def editor(preset, sequenza, scritti=()):
	"""Fa girare il giro dei tasti su un preset, e restituisce lo stato. Cio'
	che ha stampato resta in ULTIMA_USCITA."""
	stato = am.EditorState(preset)
	tasti(sequenza, scritti)
	_, ULTIMA_USCITA[0] = zitto(am.modifica, stato)
	return stato

PRIMA = impronta(VERA)
# Nessuna scrittura sul percorso vero: dalla revisione del 13 novembre 2026,
# come in banco_firme e banco_salvataggio_collezione. Prima il ritorno alla
# collezione condivisa poteva riscriverla, togliendo un doppione.
scrivi_vero = GBUtils._Acusticator._scrivi_atomico
def scrivi_sorvegliato(self, percorso, dati):
	if os.path.normcase(os.path.abspath(percorso)) == os.path.normcase(VERA):
		raise RuntimeError("il banco ha tentato di scrivere la collezione vera")
	return scrivi_vero(self, percorso, dati)
GBUtils._Acusticator._scrivi_atomico = scrivi_sorvegliato
DB_VERO = am.DB_FILE
motore = MotoreFinto()
am.Acusticator = motore
print("Banco di Acu_Maker che segue il motore. Nessun suono, la collezione vera non si tocca.")

# Perdita 3: le scivolate di pan si scrivono come lista, e il pan si legge
# come lo legge il motore.
prova("una scivolata di pan da 0 a 100 si scrive come lista", am.user_to_pan("0.100") == [0.0, 1.0], am.user_to_pan("0.100"))
prova("da 100 a 0", am.user_to_pan("100.0") == [1.0, 0.0])
prova("da 10 a 0", am.user_to_pan("10.0") == [0.1, 0.0])
prova("il testo '0.1' si mostra fermo a 10, come lo suona il motore", am.pan_to_user("0.1") == "10", am.pan_to_user("0.1"))
prova("il testo '-0.6.0.6' si mostra come scivolata", am.pan_to_user("-0.6.0.6") == "-60.60")
prova("pan_in_file scrive la coppia come lista", am.pan_in_file((-1.0, 0.1)) == [-1.0, 0.1])
stato = editor({"descrizione": "x", "score": [["c4", 0.2, 0.0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["x", "x", ".", "1", "v", "esc"])
prova("premendo v sul primo capo di una scivolata nata da 0 il secondo resta a 0",
	  stato.preset["score"][0][2] == [-0.1, 0.0], stato.preset["score"][0][2])
stato = am.EditorState({"descrizione": "x", "score": [["c4", 0.2, 0, 0.0], ["e4", 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]})
stato.posizione = am.user_to_pan("-100.100")
tasti(["u", "esc"])
zitto(am.modifica, stato)
pan = [q[2] for q in stato.preset["score"]]
prova("la posizione -100.100 unita a due quartine centrate le fa scorrere davvero",
	  all(isinstance(parse_pan_values(p), tuple) for p in pan), pan)

# Perdita 5: il cambio d'onda non guasta il primo campo.
originali = ["p.2847", "c~4", "g5.c6", "440.880", "c10"]
stato = editor({"descrizione": "x", "score": [[n, 0.1, 0, 0.0] for n in originali], "kind": 3, "adsr": [1, 0, 100, 1]},
			   ["w", "w", "w", "w", "w", "w", "esc"])
prova("con w dalla triangolare alla sinusoide, passando dai rumori, il primo campo torna com'era",
	  stato.preset["kind"] == 1 and [q[0] for q in stato.preset["score"]] == originali, [q[0] for q in stato.preset["score"]])
GBUtils_menu = am.menu
am.menu = lambda *argomenti, **chiavi: "1"
stato = editor({"descrizione": "x", "score": [[n, 0.1, 0, 0.0] for n in originali], "kind": 3, "adsr": [1, 0, 100, 1]}, ["W", "esc"])
am.menu = GBUtils_menu
prova("con W si sceglie la sinusoide diretta, senza conversioni", stato.preset["kind"] == 1 and [q[0] for q in stato.preset["score"]] == originali)
stato = editor({"descrizione": "x", "score": [["c4", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["w", "w", "w", "w", "c", "w", "w", "w", "w", "esc"])
prova("una banda toccata non torna indietro com'era: si converte", stato.preset["kind"] == 1 and stato.preset["score"][0][0] != "c4",
	  stato.preset["score"][0][0])

# Perdita 6: i doppioni usati dalle app non spariscono da soli.
suono = {"score": [["c4", 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}
db = {"apertura": {**suono, "descrizione": "Apre. Usato da: mess, meteora."},
	  "apertura_gemella": {**suono, "descrizione": "Apre, con una frase in piu' che la fa piu' lunga di tutte."}}
tolti, _ = zitto(am.togli_doppioni, db)
prova("del gemello non usato resta il preset firmato, anche con la descrizione piu' corta", list(db) == ["apertura"] and tolti == [("apertura_gemella", "apertura")])
db = {"uno": {**suono, "descrizione": "x. Usato da: mess."}, "due": {**suono, "descrizione": "x. Usato da: tornello."}}
tolti, testo = zitto(am.togli_doppioni, db)
prova("due gemelli usati da app diverse restano tutti e due, e lo si dice", len(db) == 2 and tolti == [] and "restano tutti" in testo, testo)
# Dalla 1.13.0, issue 60, conta il campo usato_da, e il prefisso non piu'.
db = {"mess_suono": {**suono, "descrizione": "breve"}, "altro": {**suono, "descrizione": "breve", "usato_da": ["mess"]}}
zitto(am.togli_doppioni, db)
prova("conta usato_da: resta il preset firmato, anche senza il prefisso", list(db) == ["altro"], list(db))

# Perdite 4 e 7, e la descrizione: con una collezione di prova.
with tempfile.TemporaryDirectory() as cartella:
	copia = os.path.join(cartella, "Acu_Collection.json")
	shutil.copyfile(VERA, copia)
	# La collezione condivisa, per Acu_Maker, e' la copia.
	am.DB_FILE = copia
	coll = am.Collezione(copia)
	zitto(coll.apri)
	lungo = max(coll.dati, key=lambda n: len(str(coll.dati[n].get("descrizione", ""))))
	descrizione = coll.dati[lungo]["descrizione"]
	stato = am.EditorState(coll.dati[lungo])
	stato.preset["score"][0][1] = round(float(stato.preset["score"][0][1]) + 0.01, 3)
	stato.modified = True
	am.menu = lambda *argomenti, **chiavi: "2"
	tasti([], ["", ""])
	zitto(am.salva_preset, coll, lungo, stato, False)
	prova(f"Salva come con Invio non tronca la descrizione di {len(descrizione)} caratteri",
		  len(descrizione) > 256 and leggi(copia)[lungo]["descrizione"] == descrizione, len(leggi(copia)[lungo]["descrizione"]))
	prima_di_esc = impronta(copia)
	am.menu = lambda *argomenti, **chiavi: None
	esito, _ = zitto(am.salva_preset, coll, lungo, stato, False)
	prova("Esc nel menu di salvataggio torna all'editor e non scarta niente", esito == "torna" and impronta(copia) == prima_di_esc)
	am.menu = GBUtils_menu

	# Rinomina e descrizione, funzioni nuove.
	nomi = list(coll.dati)
	libero = nomi[5]
	tasti([], ["rinominato_dal_banco"])
	if am.app_che_usano(coll.dati, libero):
		am.input = lambda prompt="": "s" if "(s/n)" in prompt else "rinominato_dal_banco"
		GBUtils.input = am.input
	zitto(am.rinomina, coll, libero)
	nomi_dopo = list(leggi(copia))
	prova("la rinomina cambia il nome al suo posto", nomi_dopo[5] == "rinominato_dal_banco" and libero not in nomi_dopo)
	tasti([], ["s", nomi[6]])
	am.input = lambda prompt="": "s" if "(s/n)" in prompt else nomi[6]
	GBUtils.input = am.input
	riuscito, testo = zitto(am.rinomina, coll, nomi[7])
	prova("un nome gia' preso si rifiuta", riuscito is False and "c'e' gia'" in testo, testo[-80:])
	firmato = next((n for n in coll.dati if am.app_che_usano(coll.dati, n)), None)
	am.input = lambda prompt="": "n"
	GBUtils.input = am.input
	riuscito, testo = zitto(am.rinomina, coll, firmato)
	prova("rinominare un preset usato avverte, e senza conferma non rinomina", riuscito is False and "Attenzione" in testo and firmato in leggi(copia))
	tasti([], ["Una descrizione nuova, dal banco."])
	zitto(am.cambia_descrizione, coll, nomi[8])
	prova("la descrizione si cambia senza entrare nell'editor", leggi(copia)[nomi[8]]["descrizione"] == "Una descrizione nuova, dal banco.")

	# Un'altra collezione, funzione nuova.
	progetto = os.path.join(cartella, "suoni_del_progetto.json")
	with open(progetto, "w", encoding="utf-8") as f:
		json.dump({"suono_del_progetto": {"descrizione": "x", "score": [["c4", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}}, f)
	tasti([], [progetto])
	zitto(am.apri_collezione, coll)
	prova("si apre la collezione di un progetto", coll.percorso == progetto and list(coll.dati) == ["suono_del_progetto"], coll.percorso)
	tasti([], [""])
	zitto(am.apri_collezione, coll)
	prova("e con Invio si torna a quella condivisa", coll.percorso == am.DB_FILE)

	# Dalla revisione del 13 novembre 2026, Acu_Maker 1.13.10.
	# 1. Il salvataggio che non avviene torna all'editor.
	usato = next(n for n in coll.dati if am.app_che_usano(coll.dati, n))
	stato = am.EditorState(coll.dati[usato])
	stato.preset["score"][0][1] = round(float(stato.preset["score"][0][1]) + 0.017, 3)
	stato.modified = True
	am.menu = lambda *argomenti, **chiavi: "1"
	am.input = lambda prompt="": "n"
	prima_del_no = impronta(copia)
	esito, testo = zitto(am.salva_preset, coll, usato, stato, False)
	prova("un no alla sovrascrittura di un preset usato torna all'editor, senza scrivere",
		  esito == "torna" and impronta(copia) == prima_del_no and "Le modifiche restano" in testo, (esito, testo[-120:]))
	def cambia_fuori(dati):
		dati[usato]["descrizione"] = "cambiata da un'altra sessione"
	zitto(Acusticator.aggiorna, cambia_fuori, copia)
	zitto(coll.ricarica)
	stato.preset["descrizione"] = "cambiata nell'editor"
	am.input = lambda prompt="": "s"
	am.chiedi_conflitto_vero = am.chiedi_conflitto
	am.chiedi_conflitto = lambda conflitti: None
	esito, _ = zitto(am.salva_preset, coll, usato, stato, False)
	prova("anche un conflitto annullato torna all'editor", esito == "torna" and leggi(copia)[usato]["descrizione"] == "cambiata da un'altra sessione")
	zitto(coll.elimina, usato)
	am.chiedi_conflitto = lambda conflitti: "disco"
	esito, testo = zitto(am.salva_preset, coll, usato, stato, False)
	prova("lasciare tolto un preset tolto da un altro esce, senza tornare all'editor", esito is None and "resta tolto" in testo and usato not in leggi(copia),
		  (esito, testo[-120:]))
	am.chiedi_conflitto = am.chiedi_conflitto_vero
	giri = []
	stato_vero = am.modifica
	am.modifica = lambda st: giri.append(1)
	risposte = iter(["1", "3"])
	am.menu = lambda *argomenti, **chiavi: next(risposte)
	am.input = lambda prompt="": "n"
	altro = next(n for n in coll.dati if am.app_che_usano(coll.dati, n))
	vero_editor_state = am.EditorState
	def stato_cambiato(preset):
		nuovo = vero_editor_state(preset)
		nuovo.preset["score"][0][1] = round(float(nuovo.preset["score"][0][1]) + 0.019, 3)
		nuovo.modified = True
		return nuovo
	am.EditorState = stato_cambiato
	zitto(am.edit_mode, coll, altro)
	am.EditorState = vero_editor_state
	am.modifica = stato_vero
	prova("e l'editor riparte davvero, finche' non si sceglie Esci senza salvare", len(giri) == 2, len(giri))
	# Dalla 1.14.1, scelta di Gabriele del 14 novembre 2026: un suono identico
	# a un preset che c'e' gia' non si salva, ma si sceglie se tornare
	# all'editor con le modifiche o uscire. Fino alla 1.14.0 l'editor si
	# chiudeva, e le modifiche si perdevano.
	nomi_ora = list(coll.dati)
	originale, gemello = nomi_ora[10], nomi_ora[11]
	stato = am.EditorState(coll.dati[originale])
	for campo in ("score", "kind", "adsr"):
		if campo in coll.dati[gemello]:
			stato.preset[campo] = json.loads(json.dumps(coll.dati[gemello][campo]))
	stato.modified = True
	prima_del_doppione = impronta(copia)
	esiti_doppione, chiesti_doppione = [], []
	for risposta in ("t", None, "e"):
		am.menu = lambda *_argomenti, p="", _r=risposta, **_chiavi: (chiesti_doppione.append(p), _r)[1]
		esito, testo = zitto(am.salva_preset, coll, originale, stato, False)
		esiti_doppione.append(esito)
	prova("un doppione chiede dove andare, e non salva", chiesti_doppione == ["Doppione> "] * 3 and impronta(copia) == prima_del_doppione
		  and "doppione" in testo, chiesti_doppione)
	prova("t ed Esc tornano all'editor con le modifiche, e esce senza salvare", esiti_doppione == ["torna", "torna", None], esiti_doppione)
	am.menu = GBUtils_menu

	# 3 e 4. Una collezione nuova in una cartella che non c'e', e un JSON che
	#        non e' una collezione.
	nuova = os.path.join(cartella, "progetto_nuovo", "suoni.json")
	risposte = iter([nuova, "s"])
	am.input = lambda prompt="": next(risposte)
	zitto(am.apri_collezione, coll)
	prova("una collezione nuova si crea, con la sua cartella", coll.percorso == nuova and os.path.exists(nuova), coll.percorso)
	impostazioni = os.path.join(cartella, "impostazioni.json")
	with open(impostazioni, "w", encoding="utf-8") as f:
		json.dump({"lingua": "it", "volume": 5}, f)
	am.input = lambda prompt="": impostazioni
	esito, testo = zitto(am.apri_collezione, coll)
	prova("un JSON che non e' una collezione si rifiuta, e si resta su quella di prima",
		  coll.percorso == nuova and "non e' una collezione" in testo, (coll.percorso, testo[-120:]))
	# Dalla 1.13.14, dalla seconda revisione: un file di impostazioni a
	# sezioni, come projects.json, passava il controllo, e i doppioni lo
	# riscrivevano lasciandone una sezione sola.
	sezioni = os.path.join(cartella, "impostazioni_a_sezioni.json")
	with open(sezioni, "w", encoding="utf-8") as f:
		json.dump({"finestra": {"larghezza": 800}, "audio": {"volume": 5}, "lingua": {"codice": "it"}}, f)
	prima_delle_sezioni = impronta(sezioni)
	am.input = lambda prompt="": sezioni
	esito, testo = zitto(am.apri_collezione, coll)
	prova("un file a sezioni si rifiuta, resta identico, e si resta sulla collezione di prima",
		  coll.percorso == nuova and "non e' una collezione" in testo and impronta(sezioni) == prima_delle_sezioni, (coll.percorso, testo[-160:]))
	esito, testo = zitto(am.Collezione(sezioni).apri)
	prova("anche passato da riga di comando si rifiuta, senza riscriverlo", esito is False and impronta(sezioni) == prima_delle_sezioni, testo[-160:])
	am.DB_FILE = DB_VERO

db = {"finestra": {"larghezza": 800}, "audio": {"volume": 5}, "uno": {"descrizione": "x", "score": [["c4", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}}
zitto(am.togli_doppioni, db)
prova("i doppioni non toccano le voci che non sono preset", list(db) == ["finestra", "audio", "uno"], list(db))

# Perdita 9 e le note del motore.
prova("c0 in giu' si ferma invece di scrivere b-1", am.transpose_note("c0", -1) is None)
prova("g#9 in su va avanti invece di tornare a g9", am.transpose_note("g#9", 1) == "a9", am.transpose_note("g#9", 1))
prova("un microtono si sposta e resta microtono", am.transpose_note("c~4", 1) == "c#~4", am.transpose_note("c~4", 1))
prova("il trattino si legge come bemolle", am.transpose_note("e-4", 1) == "e4", am.transpose_note("e-4", 1))
prova("le ottave da 10 in su si spostano", am.transpose_note("c10", 1) == "c#10", am.transpose_note("c10", 1))
prova("e la nota in Hz la legge il motore", abs(am.nota_in_hz("c~4") - GBUtils.frequenza_nota("c~4")) < 1e-9)
stato = editor({"descrizione": "x", "score": [["c0", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["v", "esc"])
prova("con v su c0 l'editor resta fermo e non segna il preset come cambiato", stato.preset["score"][0][0] == "c0" and not stato.modified)

# Le forme a lista e i campi assenti.
stato = am.EditorState({"descrizione": "x", "score": [["c4", 0.1, [-1.0, 1.0], [0.0, 0.3]]]})
prova("un preset senza kind e senza adsr li riceve dal motore", stato.preset["kind"] == 1 and stato.preset["adsr"] == [0.002, 0.0, 100.0, 0.002])
righe = []
for parametro in range(4):
	stato.focus_param = parametro
	righe.append(am.get_status_string(stato))
prova("pan e volume a lista si mostrano senza cadere", righe[2].endswith("<-100>.<100>") and righe[3].endswith("<50>.<80>"), righe)
prova("un kind scritto come testo diventa il numero", am.EditorState({"score": [["c4", 0.1, 0, 0.0]], "kind": "3"}).preset["kind"] == 3)

# L'ascolto: base di volume, ciclo, silenzio, Spazio che non sovrappone.
motore.suonati.clear()
stato = editor({"descrizione": "x", "score": [["c4", 0.1, 0, 0.1]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["o", "esc"], ["80"])
prova("il volume d'ascolto cambia la base, come preset(volume=)", stato.base_ascolto == 0.8 and abs(motore.suonati[-1][0][3] - 0.9) < 1e-9,
	  motore.suonati[-1][0] if motore.suonati else None)
fermati = motore.fermati
editor({"descrizione": "x", "score": [["c4", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["space", "space", "esc"])
prova("lo Spazio zittisce prima di suonare", motore.fermati - fermati == 2)
stato = editor({"descrizione": "x", "score": [["c4", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["t", "esc"])
prova("t accende il ciclo, senza dissolvenza", len(motore.cicli) == 1 and motore.cicli[0][1] == 0 and stato.ciclo is not None)
editor({"descrizione": "x", "score": [["c4", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["t", "t", "k", "esc"])
prova("t lo spegne, e k zittisce", motore.fermati >= fermati + 4)

# Le scomodita': Invio controllato, il valore riconfermato non cambia, j sui
# rumori, i separatori grafici.
prova("h4 non e' una nota", am.nota_scritta("h4") is None and am.nota_scritta("c4") == "c4")
# Dalla 1.13.10, scelta di Gabriele del 13 novembre 2026: nel campo della nota
# il punto separa sempre i capi, e gli Hertz non hanno decimali.
prova("440.880 e' una scivolata da 440 a 880, come per il motore", am.nota_scritta("440.880") == "440.880")
prova("e 440 una frequenza intera", am.nota_scritta("440") == 440 and am.nota_scritta("0") is None)
prova("dentro una scivolata un decimale non e' un capo", not am.capo_valido("440.5") and am.capo_valido("440") and am.capo_valido("c#4"))
stato = editor({"descrizione": "x", "score": [[261.63, 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, [".", "esc"])
prova("il punto su una frequenza con i decimali la arrotonda all'Hertz", stato.preset["score"][0][0] == "262.262", stato.preset["score"][0][0])
stato = editor({"descrizione": "x", "score": [["440.880", 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["b", "c", "esc"], ["0.5"])
prova("dentro una scivolata in Hertz i capi restano interi, anche con un passo decimale", stato.preset["score"][0][0] == "441.881",
	  stato.preset["score"][0][0])
# 5. Il passo che non si puo' usare si rifiuta.
stato = editor({"descrizione": "x", "score": [["200-3000", 0.2, 0, 0.0]], "kind": 6, "adsr": [1, 0, 100, 1]}, ["b", "v", "esc"], ["0"])
prova("un passo di banda a zero si rifiuta, e v funziona ancora", stato.steps["banda"] == am.PASSO_BANDA and stato.preset["score"][0][0] != "200-3000",
	  stato.preset["score"][0][0])
# 6. Il fuoco da 4 a 7 torna a 3 lasciata la banda.
# Il pan va da -0,5 a 0,5, lontano dai bordi: col fuoco su un capo solo c
# darebbe [-0.4, 0.5] o [-0.5, 0.6], e cosi' la prova li distingue.
stato = editor({"descrizione": "x", "score": [["200-3000.400-2000", 0.2, [-0.5, 0.5], 0.0]], "kind": 6, "adsr": [1, 0, 100, 1]},
			   ["5", "x", "x", "c", "esc"])
prova("dopo il 5 sulla banda, c sul pan che scorre muove tutti e due i capi",
	  stato.preset["score"][0][2] == [-0.4, 0.6] and stato.port_focus == 3, (stato.preset["score"][0][2], stato.port_focus))
# Dalla 1.13.14: anche la riga di stato mostra il fuoco riportato a 3.
stato = am.EditorState({"descrizione": "x", "score": [["200-3000", 0.2, 0, [-0.3, 0.3]]], "kind": 6, "adsr": [1, 0, 100, 1]})
stato.focus_type, stato.focus_param, stato.port_focus = "score", 3, 5
_, riga = zitto(am.handle_print, stato)
prova("lasciata la banda, la prima riga di stato segna gia' tutti e due i capi", "<" in riga and stato.port_focus == 3, (riga.strip(), stato.port_focus))
# Dalla 1.13.14: c e v su una nota in Hertz la tengono intera.
stato = editor({"descrizione": "x", "score": [[440, 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["c", "esc"])
prova("c su 440 Hertz da' 450, intero", stato.preset["score"][0][0] == 450 and isinstance(stato.preset["score"][0][0], int),
	  repr(stato.preset["score"][0][0]))
stato = editor({"descrizione": "x", "score": [[440, 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["b", "c", "esc"], ["0.5"])
prova("con un passo di mezzo Hertz c da' 441, almeno un Hertz per passo", stato.preset["score"][0][0] == 441, repr(stato.preset["score"][0][0]))
stato = editor({"descrizione": "x", "score": [[1, 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["v", "esc"])
prova("v su 1 Hertz si ferma", stato.preset["score"][0][0] == 1 and not stato.modified, repr(stato.preset["score"][0][0]))
# Dalla 1.13.16, dalla terza revisione: una nota che non e' un numero finito,
# scritta a mano nel file, ferma c invece di far cadere l'editor. Nella
# 1.13.14 i numeri davano ValueError o OverflowError, e dalla 1.13.10 i testi.
for nota in (float("nan"), float("inf"), float("-inf"), "nan", "inf", "nan.880"):
	try:
		stato = editor({"descrizione": "x", "score": [[nota, 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["c", "esc"])
		visto = (repr(stato.preset["score"][0][0]), stato.modified)
		fermo = visto == (repr(nota), False)
	except (ValueError, OverflowError) as errore:
		visto, fermo = type(errore).__name__, False
	prova(f"c su una nota {nota!r} si ferma, senza cadere", fermo, visto)
# 7. n riporta i passi di partenza.
stato = editor({"descrizione": "x", "score": [["c4", 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["a", "b", "n", "esc"], ["5"])
prova("n sull'attacco riporta il passo a 0,001, quello di partenza", stato.steps["a"] == 0.001, stato.steps["a"])
stato = editor({"descrizione": "x", "score": [["c4", 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["enter", "esc"], ["h4"])
prova("Invio rifiuta h4", stato.preset["score"][0][0] == "c4" and not stato.modified)
stato = editor({"descrizione": "x", "score": [["c4", 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["x", "enter", "esc"], ["-1"])
prova("Invio rifiuta una durata negativa", stato.preset["score"][0][1] == 0.2 and not stato.modified)
stato = editor({"descrizione": "x", "score": [["c4", 0.2, 0, 0.7]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["x", "x", "x", "enter", "esc"], ["100"])
prova("riconfermare 100 su uno scarto di 0,7 non lo cambia", stato.preset["score"][0][3] == 0.7 and not stato.modified, stato.preset["score"][0][3])
stato = editor({"descrizione": "x", "score": [["200-3000", 0.2, 0, 0.0]], "kind": 6, "adsr": [1, 0, 100, 1]}, ["j", "esc"])
prova("j su un rumore inserisce una banda", stato.preset["score"][1][0] == am.BANDA_DEFAULT, stato.preset["score"])
with open(os.path.join(QUI, "Acu_Maker.py"), encoding="utf-8") as f:
	sorgente = f.read()
prova("nei testi di Acu_Maker non ci sono piu' righe di trattini", '"---' not in sorgente and "--- " not in sorgente and '"->"' not in sorgente)
# 8. Le richieste di una riga finiscono con i due punti, come nel resto del
# parco: il cursore resta dopo la domanda, e cio' che si scrive non la
# copre. Fino alla 1.13.17 finivano con un ritorno carrello, come i prompt
# che aspettano un tasto solo, e il cursore tornava a inizio riga (collaudo
# di Gabriele del 14 novembre 2026, prova 4).
con_ritorno = re.findall(r'(?:input|dgt)\(f?"[^"\n]*\\r"', sorgente)
prova("nessuna richiesta di una riga finisce con un ritorno carrello", con_ritorno == [], con_ritorno)
prompt = ['"Lo sovrascrivo? (s/n): "', '"Lo rinomino lo stesso? (s/n): "', 'f"Nome nuovo per {nome}: "',
		  'non esiste. La creo? (s/n): "', 'f"Nome breve [{preset_name}]: "', 'f"Descrizione [{desc}]: "',
		  '"Volume d\'ascolto: "', '"Posizione: "', '"Nome o parte del nome: "', 'f"Numero, da 1 a {len(nomi)}: "',
		  '"App che lo usa, Invio per tornare: "', '"Nome nuovo dell\'app: "', '"Descrizione nuova, Invio la lascia: "',
		  '"Percorso della collezione, Invio per quella condivisa: "']
mancano = [p for p in prompt if p not in sorgente]
prova("le richieste di Acu_Maker finiscono con i due punti", mancano == [], mancano)
# Dopo una richiesta il cursore e' gia' a capo: andarci ancora lasciava una
# riga vuota prima della riga di stato, con o, p e W.
stato = editor({"descrizione": "x", "score": [["c4", 0.2, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}, ["o", "esc"], ["80"])
prova("o non lascia una riga vuota dopo la richiesta", "\n\n" not in ULTIMA_USCITA[0], ULTIMA_USCITA[0][-200:])

am.Acusticator = Acusticator
prova("la collezione vera non e' stata toccata", impronta(VERA) == PRIMA)
print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
