"""Banco di prova del salvataggio della collezione, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 per la issue 58, con Acusticator 8.7.0 e Acu_Maker 1.9.0.
Niente di questo suona, e niente tocca la collezione vera: si lavora su copie
in una cartella temporanea, la collezione vera ha la sua impronta sha256 al
principio e alla fine, e ogni scrittura sul suo percorso viene rifiutata.
Le domande sono quelle della issue. Chi salva perde cio' che un altro ha
scritto nel frattempo? Un file illeggibile, a meta', vuoto o con un conflitto
di git, viene azzerato? Chi legge mentre un altro scrive trova il file a meta'?
Quattro processi che salvano insieme si perdono qualcosa? Il formato resta
identico al byte? E Acu_Maker, che teneva la copia letta all'avvio e la
riscriveva intera, rispetta cio' che altri hanno scritto?
Si lancia con
  python banco_salvataggio_collezione.py
e dura una ventina di secondi. Stampa in fondo quante prove sono passate.
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import Acu_Maker as am

import GBUtils
from GBUtils import Acusticator

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
	"""Chiama funzione senza lasciarla scrivere in console; restituisce il
	risultato e cio' che ha scritto su stdout e stderr."""
	uscita, errori = io.StringIO(), io.StringIO()
	with contextlib.redirect_stdout(uscita), contextlib.redirect_stderr(errori):
		risultato = funzione(*argomenti, **chiavi)
	return risultato, uscita.getvalue() + errori.getvalue()

PRIMA = impronta(VERA)
# Nessuna scrittura sul percorso vero: se il banco ci provasse, cadrebbe qui.
scrivi_vero = GBUtils._Acusticator._scrivi_atomico
def scrivi_sorvegliato(self, percorso, dati):
	if os.path.normcase(os.path.abspath(percorso)) == os.path.normcase(VERA):
		raise RuntimeError("il banco ha tentato di scrivere la collezione vera")
	return scrivi_vero(self, percorso, dati)
GBUtils._Acusticator._scrivi_atomico = scrivi_sorvegliato

LAVORATORE = '''import os, sys, time
sys.path.insert(0, sys.argv[1])
import GBUtils
percorso, prefisso, quanti, via = sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
while not os.path.exists(via):
	time.sleep(0.005)
riusciti = 0
for i in range(quanti):
	if GBUtils.Acusticator.save(f"{prefisso}_{i}", ["c4", 0.1, 0, 0.5], descrizione="prova del banco", percorso=percorso):
		riusciti += 1
print(riusciti)
'''
LETTORE = '''import json, os, sys, time
percorso, basta = sys.argv[1], sys.argv[2]
letture = vuoti = rotti = occupati = 0
while not os.path.exists(basta):
	try:
		with open(percorso, "rb") as f:
			dati = f.read()
	except PermissionError:
		occupati += 1
		continue
	except FileNotFoundError:
		rotti += 1
		continue
	letture += 1
	if not dati:
		vuoti += 1
		continue
	try:
		json.loads(dati.decode("utf-8"))
	except ValueError:
		rotti += 1
print(json.dumps({"letture": letture, "vuoti": vuoti, "rotti": rotti, "occupati": occupati}))
'''
TENITORE = '''import sys, time
with open(sys.argv[1], "rb") as f:
	print("aperto", flush=True)
	time.sleep(float(sys.argv[2]))
'''

def avvia(cartella, nome, testo, *argomenti):
	script = os.path.join(cartella, nome)
	with open(script, "w", encoding="utf-8") as f:
		f.write(testo)
	return subprocess.Popen([sys.executable, script, *argomenti], stdin=subprocess.DEVNULL,
							stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

print("Banco del salvataggio della collezione. Nessun suono, la collezione vera non si tocca.")
with tempfile.TemporaryDirectory() as cartella:
	copia = os.path.join(cartella, "Acu_Collection.json")
	shutil.copyfile(VERA, copia)
	originale = leggi(copia)

	# 1. Il formato: riscritta senza cambiare niente, e' identica al byte.
	_, testo = zitto(Acusticator.aggiorna, lambda dati: None, copia)
	prova(f"riscritta com'era, la collezione di {len(originale)} preset e' identica al byte", impronta(copia) == PRIMA, testo)
	prova("e il lucchetto e i provvisori non restano", sorted(os.listdir(cartella)) == ["Acu_Collection.json"], os.listdir(cartella))

	# 2. Un preset nuovo va in coda, uno esistente resta al suo posto e tiene
	#    i campi che save non conosce.
	primo = next(iter(originale))
	def con_firma(dati):
		dati[primo]["usato_da"] = ["banco"]
	zitto(Acusticator.aggiorna, con_firma, copia)
	riuscito, _ = zitto(Acusticator.save, primo, ["c4", 0.1, 0, 0.5], descrizione="rifatto dal banco", percorso=copia)
	dati = leggi(copia)
	prova("save sostituisce un preset esistente", riuscito and dati[primo]["descrizione"] == "rifatto dal banco")
	prova("e lo lascia al suo posto", list(dati) == list(originale))
	prova("e gli lascia i campi che non conosce", dati[primo].get("usato_da") == ["banco"], dati[primo])
	zitto(Acusticator.save, "banco_in_coda", ["c4", 0.1, 0, 0.5], descrizione="nuovo", percorso=copia)
	prova("un preset nuovo va in coda", list(leggi(copia))[-1] == "banco_in_coda")
	shutil.copyfile(VERA, copia)

	# 3. Due programmi con la cache: il primo ha letto, il secondo salva, poi
	#    salva il primo. Prima della V8.7.0 il preset del secondo spariva.
	uno, due = GBUtils._Acusticator(), GBUtils._Acusticator()
	uno.collezione(copia)
	zitto(uno.list)
	zitto(due.save, "banco_dal_secondo", ["e4", 0.1, 0, 0.5], descrizione="dal secondo", percorso=copia)
	zitto(uno.save, "banco_dal_primo", ["g4", 0.1, 0, 0.5], descrizione="dal primo", percorso=copia)
	dati = leggi(copia)
	prova("con la cache piena il primo non cancella il preset del secondo", "banco_dal_secondo" in dati and "banco_dal_primo" in dati)
	prova("e i preset di prima ci sono tutti", all(n in dati for n in originale))

	# 4. Il file illeggibile non si azzera.
	with open(VERA, "rb") as f:
		bytes_veri = f.read()
	guasti = {
		"a meta'": bytes_veri[:len(bytes_veri) // 2],
		"vuoto": b"",
		"con un conflitto di git": b"<<<<<<< HEAD\n" + bytes_veri[:2000] + b"\n=======\n" + bytes_veri[:1000] + b"\n>>>>>>> altro\n",
	}
	for descrizione, contenuto in guasti.items():
		with open(copia, "wb") as f:
			f.write(contenuto)
		riuscito, testo = zitto(Acusticator.save, "banco_su_guasto", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=copia)
		with open(copia, "rb") as f:
			dopo = f.read()
		prova(f"con il file {descrizione} save risponde di no", riuscito is False and "illeggibile" in testo, (riuscito, testo[-120:]))
		prova(f"e il file {descrizione} resta com'era", dopo == contenuto)
	shutil.copyfile(VERA, copia)

	# 5. Un lettore che legge di continuo mentre si salva quaranta volte.
	basta = os.path.join(cartella, "basta")
	lettore = avvia(cartella, "lettore.py", LETTORE, copia, basta)
	time.sleep(0.3)
	for i in range(40):
		zitto(Acusticator.save, f"banco_quaranta_{i}", ["c4", 0.05, 0, 0.5], descrizione="quaranta", percorso=copia)
	open(basta, "w").close()
	conti = json.loads(lettore.communicate(timeout=60)[0])
	os.remove(basta)
	prova(f"in {conti['letture']} letture durante 40 salvataggi il file non e' mai vuoto ne' a meta'",
		  conti["vuoti"] == 0 and conti["rotti"] == 0 and conti["letture"] > 40, conti)
	prova("e i quaranta preset ci sono tutti", all(f"banco_quaranta_{i}" in leggi(copia) for i in range(40)))

	# 6. Quattro processi, venticinque salvataggi ciascuno, un lettore attivo.
	#    Su una collezione di cento preset, perche' il banco duri poco.
	piccola = os.path.join(cartella, "piccola.json")
	with open(piccola, "w", encoding="utf-8") as f:
		json.dump(dict(list(originale.items())[:100]), f, indent=4, ensure_ascii=False)
		f.write("\n")
	via = os.path.join(cartella, "via")
	lavoratori = [avvia(cartella, f"lavoratore{n}.py", LAVORATORE, QUI, piccola, f"p{n}", "25", via) for n in range(4)]
	lettore = avvia(cartella, "lettore.py", LETTORE, piccola, basta)
	time.sleep(0.5)
	open(via, "w").close()
	riusciti = [int(p.communicate(timeout=120)[0].strip() or 0) for p in lavoratori]
	open(basta, "w").close()
	conti = json.loads(lettore.communicate(timeout=60)[0])
	dati = leggi(piccola)
	scritti = sum(1 for n in range(4) for i in range(25) if f"p{n}_{i}" in dati)
	prova("quattro processi per venticinque salvataggi: ci sono tutti e cento", scritti == 100 and riusciti == [25] * 4, (scritti, riusciti))
	prova("e i cento di prima pure", all(n in dati for n in list(originale)[:100]))
	prova("e il lettore non ha mai visto il file rotto", conti["vuoti"] == 0 and conti["rotti"] == 0, conti)
	os.remove(basta)

	# 7. La sostituzione con un lettore che tiene il file aperto: su Windows
	#    fallisce finche' quello non chiude, e si riprova.
	tenitore = avvia(cartella, "tenitore.py", TENITORE, copia, "0.6")
	tenitore.stdout.readline()
	inizio = time.monotonic()
	riuscito, testo = zitto(Acusticator.save, "banco_col_file_aperto", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=copia)
	attesa = time.monotonic() - inizio
	tenitore.communicate(timeout=30)
	prova("con il file tenuto aperto da un altro, save aspetta e scrive", riuscito and "banco_col_file_aperto" in leggi(copia), testo)
	print(f"  attesa per la sostituzione: {attesa:.2f} s")

	# 8. Il lucchetto orfano si toglie, quello vivo si rispetta.
	lucchetto = copia + ".lock"
	with open(lucchetto, "w") as f:
		f.write("99999")
	vecchio = time.time() - 60
	os.utime(lucchetto, (vecchio, vecchio))
	riuscito, _ = zitto(Acusticator.save, "banco_dopo_l_orfano", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=copia)
	prova("un lucchetto di un processo morto si toglie, e si scrive", riuscito and not os.path.exists(lucchetto))
	with open(lucchetto, "w") as f:
		f.write("99999")
	frettoloso = GBUtils._Acusticator()
	frettoloso.LUCCHETTO_ATTESA = 0.3
	prima_del_vivo = impronta(copia)
	riuscito, testo = zitto(frettoloso.save, "banco_col_vivo", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=copia)
	prova("un lucchetto vivo si rispetta: save risponde di no e non scrive", riuscito is False and "occupata" in testo and impronta(copia) == prima_del_vivo,
		  testo[-100:])
	os.remove(lucchetto)

	# 9. Da eseguibile non si scrive.
	sys.frozen = True
	try:
		riuscito, testo = zitto(Acusticator.save, "banco_congelato", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=copia)
		aggiornato, _ = zitto(Acusticator.aggiorna, lambda dati: None, copia)
	finally:
		del sys.frozen
	prova("da eseguibile save e aggiorna non scrivono", riuscito is False and aggiornato is None and "banco_congelato" not in leggi(copia))

	# 10. Acu_Maker aperto mentre un'altra sessione aggiunge e firma.
	shutil.copyfile(VERA, copia)
	am.DB_FILE = copia
	coll = am.Collezione(copia)
	_, testo = zitto(coll.apri)
	secondo, terzo = list(originale)[1], list(originale)[2]
	def altra_sessione(dati):
		dati["banco_altra_sessione"] = {"descrizione": "aggiunto da fuori", "score": [["c5", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}
		dati[secondo]["descrizione"] += " Usato da: banco."
		del dati[terzo]
	zitto(Acusticator.aggiorna, altra_sessione, copia)
	novita, testo = zitto(coll.ricarica)
	prova("Acu_Maker si accorge che il file e' cambiato e conta nuovi, cambiati e tolti",
		  novita is not None and [len(x) for x in novita] == [1, 1, 1] and "1 preset nuovi, 1 cambiati, 1 tolti" in testo, testo)
	quarto = list(originale)[3]
	eliminato, _ = zitto(coll.elimina, quarto)
	dati = leggi(copia)
	prova("Elimina toglie soltanto il preset scelto", eliminato and quarto not in dati and len(dati) == len(originale) - 1)
	prova("e il preset aggiunto e la firma dell'altra sessione restano",
		  "banco_altra_sessione" in dati and dati[secondo]["descrizione"].endswith("Usato da: banco."))

	# 11. Sovrascrivi: la fusione a tre.
	base = am.copia(dati[secondo])
	mio = am.copia(base)
	mio["score"] = [["a4", 0.2, 0, 0.0]]
	def firma_ancora(dati):
		dati[secondo]["descrizione"] += " Usato da: altro."
	zitto(Acusticator.aggiorna, firma_ancora, copia)
	domande = []
	def chiedi(conflitti, risposta=None):
		domande.append(list(conflitti))
		return risposta
	scritto, _ = zitto(coll.sovrascrivi, secondo, base, mio, chiedi)
	dati = leggi(copia)
	prova("il suono rifatto e la firma arrivata intanto si fondono da soli",
		  scritto and domande == [] and dati[secondo]["score"] == [["a4", 0.2, 0, 0.0]] and dati[secondo]["descrizione"].endswith("Usato da: altro."),
		  (domande, dati[secondo]))
	base = am.copia(dati[secondo])
	for risposta, attesa in (("mio", "la mia"), ("disco", "quella del disco"), (None, "quella del disco")):
		mio = am.copia(base)
		mio["descrizione"] = "la mia"
		def cambia_fuori(dati):
			dati[secondo]["descrizione"] = "quella del disco"
		zitto(Acusticator.aggiorna, cambia_fuori, copia)
		domande.clear()
		zitto(coll.sovrascrivi, secondo, base, mio, lambda conflitti, r=risposta: chiedi(conflitti, r))
		prova(f"un conflitto sulla descrizione si chiede, e con {risposta!r} resta {attesa}",
			  domande == [["descrizione"]] and leggi(copia)[secondo]["descrizione"] == attesa, (domande, leggi(copia)[secondo]["descrizione"]))
		zitto(Acusticator.aggiorna, lambda dati, b=base: dati[secondo].update(am.copia(b)), copia)
	zitto(coll.elimina, secondo)
	domande.clear()
	scritto, _ = zitto(coll.sovrascrivi, secondo, base, base, lambda conflitti: chiedi(conflitti, "mio"))
	prova("un preset tolto da un altro si puo' rimettere", scritto and domande == [["tolto"]] and secondo in leggi(copia))

	# 12. Salva come sceglie il nome libero sul disco di adesso.
	usato, _ = zitto(coll.salva_nuovo, secondo, base)
	prova("Salva come con un nome preso aggiunge un numero", usato == secondo + "0" and usato in leggi(copia), usato)

	# 13. Il preset del tasto piu' non arriva sul disco se non lo si salva.
	# Il nome e' quello che Acu_Maker sceglie: nella collezione vera c'e' gia'
	# un nuovo_preset, rimasto da prima della 1.9.0.
	prima_del_piu = impronta(copia)
	segnaposto = am.get_unique_name(coll.dati, "nuovo_preset")
	am.get_keypress = lambda: "esc"
	zitto(am.edit_mode, coll, segnaposto, nuovo={"descrizione": "Nuovo preset vuoto", "score": [["c4", 0.5, 0.0, 0.0]],
												 "kind": 1, "adsr": [0.002, 0.0, 100.0, 0.002]})
	prova(f"un preset nuovo lasciato com'era non entra nella collezione, {segnaposto}",
		  impronta(copia) == prima_del_piu and segnaposto not in leggi(copia))

	# 14. Uscire da Acu_Maker non riscrive niente, e Ctrl+C non perde niente.
	#    Prima si tolgono i doppioni, perche' la prova 12 ne ha creato uno, e
	#    l'uscita lo toglierebbe, giustamente.
	zitto(coll.togli_doppioni)
	prima_dell_uscita = impronta(copia)
	am.menu = lambda *argomenti, **chiavi: None
	_, testo = zitto(am.main)
	prova("uscendo, Acu_Maker non riscrive la collezione", impronta(copia) == prima_dell_uscita and "Arrivederci" in testo, testo[-200:])
	def interrompi(*argomenti, **chiavi):
		raise KeyboardInterrupt
	am.menu = interrompi
	_, testo = zitto(am.main)
	prova("con Ctrl+C esce dicendo che il salvato e' gia' sul disco", "Interrotto" in testo and impronta(copia) == prima_dell_uscita, testo[-200:])

	# 15. Dalla revisione del 13 novembre 2026: una cartella che non c'e'.
	#     Fino alla V8.9.0 aggiorna, save e firma sollevavano FileNotFoundError.
	assente = os.path.join(cartella, "cartella_che_non_c_e", "suoni.json")
	esiti = []
	for funzione, argomenti in ((Acusticator.aggiorna, (lambda dati: None, assente)),
								(Acusticator.save, ("x", ["c4", 0.1, 0, 0.5], 1, None, "x", assente)),
								(Acusticator.firma, ("x", "banco", assente))):
		try:
			esito, testo = zitto(funzione, *argomenti)
			esiti.append((esito, "lucchetto" in testo))
		except OSError as errore:
			esiti.append(("solleva", type(errore).__name__))
	prova("con la cartella che non c'e' aggiorna, save e firma rispondono senza cadere, e lo dicono",
		  esiti == [(None, True), (False, True), (None, True)], esiti)

	# 16. Un lucchetto vecchio che non si lascia togliere: si aspetta fino alla
	#     scadenza, con le pause. Fino alla V8.9.0 il ciclo girava a vuoto per
	#     sempre, su un core pieno.
	import stat
	import threading
	lucchetto = copia + ".lock"
	with open(lucchetto, "w") as f:
		f.write("99999")
	vecchio = time.time() - 120
	os.utime(lucchetto, (vecchio, vecchio))
	os.chmod(lucchetto, stat.S_IREAD)
	paziente = GBUtils._Acusticator()
	paziente.LUCCHETTO_ATTESA = 0.5
	contati, esito = [0], []
	vero_getmtime = os.path.getmtime
	def conta_getmtime(percorso):
		contati[0] += 1
		return vero_getmtime(percorso)
	os.path.getmtime = conta_getmtime
	filo = threading.Thread(target=lambda: esito.append(zitto(paziente.save, "x", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=copia)),
							daemon=True)
	filo.start()
	filo.join(5.0)
	appeso = filo.is_alive()
	os.chmod(lucchetto, stat.S_IWRITE)
	filo.join(5.0)
	os.path.getmtime = vero_getmtime
	if os.path.exists(lucchetto):
		os.remove(lucchetto)
	prova("con un lucchetto vecchio in sola lettura save aspetta la scadenza e risponde di no, senza girare a vuoto",
		  not appeso and [e for e, _ in esito] == [False] and contati[0] < 100, (appeso, esito, contati[0]))
	# Dalla V8.9.11 l'avviso nomina il lucchetto vecchio, invece di dire la
	# collezione occupata da un altro programma.
	detto = esito[0][1] if esito else ""
	prova("e l'avviso nomina il lucchetto vecchio, non un altro programma",
		  "lucchetto vecchio" in detto and os.path.basename(lucchetto) in detto and "altro programma" not in detto, detto)
	# Dalla terza revisione: il percorso una volta sola, e il motivo in
	# chiaro. Fino alla V8.9.16 lo ripeteva con le barre doppie.
	prova("e lo nomina una volta sola, senza barre doppie",
		  detto.count(os.path.basename(lucchetto)) == 1 and "\\\\" not in detto, detto)
	# Un lucchetto vecchio che si toglie, invece, si toglie e la firma si
	# scrive. Fino alla V278 la prova firmava un preset che non c'e'.
	firmato = next(iter(originale))
	with open(lucchetto, "w") as f:
		f.write("99999")
	os.utime(lucchetto, (vecchio, vecchio))
	esito, detto = zitto(paziente.firma, firmato, "banco", copia)
	prova("un lucchetto vecchio che si lascia togliere si toglie, e la firma si scrive",
		  esito == 1 and "banco" in GBUtils._firme_di(leggi(copia)[firmato]) and not os.path.exists(lucchetto), (esito, detto))

	# 17. Dalla terza revisione: il lucchetto che cambia durante l'attesa.
	attento = GBUtils._Acusticator()
	attento.LUCCHETTO_ATTESA = 1.0
	def vecchio_in_sola_lettura():
		with open(lucchetto, "w") as f:
			f.write("99999")
		os.utime(lucchetto, (vecchio, vecchio))
		os.chmod(lucchetto, stat.S_IREAD)
	def fra(secondi, azione):
		def corpo():
			time.sleep(secondi)
			azione()
		filo = threading.Thread(target=corpo, daemon=True)
		filo.start()
		return filo
	vecchio_in_sola_lettura()
	filo = fra(0.2, lambda: os.chmod(lucchetto, stat.S_IWRITE))
	riuscito, detto = zitto(attento.save, "banco_dopo_la_sola_lettura", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=copia)
	filo.join(5.0)
	prova("un lucchetto vecchio che torna scrivibile durante l'attesa si toglie, e save scrive",
		  riuscito and "banco_dopo_la_sola_lettura" in leggi(copia) and not os.path.exists(lucchetto), detto)
	vecchio_in_sola_lettura()
	fresco = lucchetto + ".fresco"
	def sostituisci():
		# Prima diventa fresco, poi si sostituisce in un colpo: chi aspetta
		# non trova mai un buco in cui prendersi il lucchetto.
		os.utime(lucchetto, None)
		os.chmod(lucchetto, stat.S_IWRITE)
		with open(fresco, "w") as f:
			f.write("12345")
		os.replace(fresco, lucchetto)
	filo = fra(0.2, sostituisci)
	prima_del_fresco = impronta(copia)
	riuscito, detto = zitto(attento.save, "banco_col_fresco", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=copia)
	filo.join(5.0)
	if os.path.exists(lucchetto):
		os.chmod(lucchetto, stat.S_IWRITE)
		os.remove(lucchetto)
	prova("un lucchetto vecchio sostituito da uno fresco durante l'attesa si rispetta, e l'avviso dice occupata",
		  riuscito is False and "occupata" in detto and "lucchetto vecchio" not in detto and impronta(copia) == prima_del_fresco, detto)

	# 18. Dalla terza revisione: l'accesso negato. Una cartella al posto del
	#     lucchetto lo da' sempre, come una cartella in sola lettura. Fino alla
	#     V8.9.16 save aspettava e diceva la collezione occupata da un altro
	#     programma.
	negata = os.path.join(cartella, "negata.json")
	os.mkdir(negata + ".lock")
	frettoloso.LUCCHETTO_ATTESA = 0.3
	riuscito, detto = zitto(frettoloso.save, "banco_negato", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=negata)
	os.rmdir(negata + ".lock")
	prova("con l'accesso negato save risponde di no e dice che il lucchetto non si crea, non un altro programma",
		  riuscito is False and "non riesco a creare il lucchetto" in detto and "occupata" not in detto
		  and detto.count("negata.json.lock") == 1 and "\\\\" not in detto and not os.path.exists(negata), detto)
	# Un accesso negato di passaggio, come quello di un lucchetto in via di
	# cancellazione, si aspetta, e poi si scrive.
	vero_open, negati = os.open, [0]
	def open_negato(percorso, *argomenti, **chiavi):
		if str(percorso).endswith(".lock") and negati[0] < 5:
			negati[0] += 1
			raise PermissionError(13, "Accesso negato", percorso)
		return vero_open(percorso, *argomenti, **chiavi)
	os.open = open_negato
	try:
		riuscito, detto = zitto(frettoloso.save, "banco_dopo_i_negati", ["c4", 0.1, 0, 0.5], descrizione="x", percorso=copia)
	finally:
		os.open = vero_open
	prova("cinque accessi negati di passaggio si aspettano, e poi save scrive senza avvisi",
		  riuscito and negati[0] == 5 and "banco_dopo_i_negati" in leggi(copia) and not detto, (negati[0], detto))

prova("la collezione vera non e' stata toccata", impronta(VERA) == PRIMA)
print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
