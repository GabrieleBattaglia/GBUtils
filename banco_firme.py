"""Banco di prova delle firme dei preset, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato il 12 novembre 2026 per la issue 60, con Acusticator 8.9.0 e Acu_Maker 1.13.0.
Niente di questo suona, e la collezione vera si legge soltanto: le firme si
scrivono su copie in una cartella temporanea, e la collezione vera ha la sua
impronta sha256 al principio e alla fine.
Le domande sono tre. La collezione ha le firme nel campo usato_da, nella forma
decisa, e nessuna piu' nella descrizione? I metodi di Acusticator leggono,
aggiungono, tolgono e cambiano le firme in modo sicuro e veloce, anche con
piu' processi insieme? E Acu_Maker mostra le firme come prima, le cerca in
modo esatto e non le copia ne' le perde?
Si lancia con
  python banco_firme.py
e dura una decina di secondi. Stampa in fondo quante prove sono passate.
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
	uscita = io.StringIO()
	with contextlib.redirect_stdout(uscita), contextlib.redirect_stderr(uscita):
		risultato = funzione(*argomenti, **chiavi)
	return risultato, uscita.getvalue()

PRIMA = impronta(VERA)
scritture = []
scrivi_vero = GBUtils._Acusticator._scrivi_atomico
def scrivi_contato(self, percorso, dati):
	if os.path.normcase(os.path.abspath(percorso)) == os.path.normcase(VERA):
		raise RuntimeError("il banco ha tentato di scrivere la collezione vera")
	scritture.append(percorso)
	return scrivi_vero(self, percorso, dati)
GBUtils._Acusticator._scrivi_atomico = scrivi_contato

FIRMATORE = '''import os, sys, time
sys.path.insert(0, sys.argv[1])
import GBUtils
percorso, app, via = sys.argv[2], sys.argv[3], sys.argv[4]
nomi = sys.argv[5].split(",")
while not os.path.exists(via):
	time.sleep(0.005)
riusciti = 0
for nome in nomi:
	if GBUtils.Acusticator.firma(nome, app, percorso=percorso):
		riusciti += 1
print(riusciti)
'''

print("Banco delle firme dei preset. Nessun suono, la collezione vera non si tocca.")
collezione = leggi(VERA)

# 1. La forma della collezione.
con_testo = [n for n, v in collezione.items() if "Usato da:" in str(v.get("descrizione", ""))]
prova("nessuna descrizione porta piu' la firma Usato da", con_testo == [], con_testo[:5])
storte = [n for n, v in collezione.items() if "usato_da" in v and (
	not isinstance(v["usato_da"], list) or not v["usato_da"] or v["usato_da"] != sorted({str(a).lower() for a in v["usato_da"]}))]
prova("ogni usato_da e' una lista non vuota, in minuscolo, in ordine e senza ripetizioni", storte == [], storte[:5])
fuori_posto = [n for n, v in collezione.items() if "usato_da" in v and list(v)[list(v).index("usato_da") - 1] != "descrizione"]
prova("e sta subito dopo la descrizione", fuori_posto == [], fuori_posto[:5])
firmati = sum(1 for v in collezione.values() if "usato_da" in v)
print(f"  {firmati} preset firmati su {len(collezione)}")

# 2. La lettura con Acusticator.
Acusticator.reload()
firme = Acusticator.firme()
prova("firme conta le app come il file", firme == {a: sum(1 for v in collezione.values() if a in v.get("usato_da", [])) for a in firme}, firme)
for app in list(firme)[:5]:
	prova(f"usati_da({app!r}) sono i preset con {app} in usato_da",
		  Acusticator.usati_da(app) == sorted(n for n, v in collezione.items() if app in v.get("usato_da", [])))
nome_firmato = next(n for n, v in collezione.items() if "usato_da" in v)
prova("usato_da di un preset e' la sua lista", Acusticator.usato_da(nome_firmato) == collezione[nome_firmato]["usato_da"])
prova("usato_da di un preset che non c'e' e' vuoto, con l'avviso", zitto(Acusticator.usato_da, "preset_inesistente_davvero")[0] == [])
prova("la descrizione e' testo puro", "Usato da" not in Acusticator.descrizione(nome_firmato))
app_piu = next(iter(firme))
prova("list con app= e' un filtro esatto", Acusticator.list(app=app_piu) == Acusticator.usati_da(app_piu))
prova("list con un filtro trova anche le app", set(Acusticator.usati_da(app_piu)) <= set(Acusticator.list(app_piu)))

with tempfile.TemporaryDirectory() as cartella:
	copia = os.path.join(cartella, "Acu_Collection.json")
	shutil.copyfile(VERA, copia)

	# 3. Il formato al byte, con le firme.
	zitto(Acusticator.aggiorna, lambda dati: None, copia)
	prova("riscritta com'era, la collezione con le firme e' identica al byte", impronta(copia) == PRIMA)

	# 4. Firmare, togliere, cambiare: una scrittura per chiamata.
	nomi = [n for n, v in collezione.items() if "usato_da" not in v][:3]
	scritture.clear()
	esito, _ = zitto(Acusticator.firma, nomi[:2], "Banco", percorso=copia)
	dati = leggi(copia)
	prova("firma due preset in una chiamata e una scrittura", esito == 2 and len(scritture) == 1 and all(dati[n]["usato_da"] == ["banco"] for n in nomi[:2]),
		  (esito, len(scritture)))
	prova("e la firma nuova sta subito dopo la descrizione", list(dati[nomi[0]])[:2] == ["descrizione", "usato_da"], list(dati[nomi[0]]))
	scritture.clear()
	esito, _ = zitto(Acusticator.firma, nomi[:2], "banco", percorso=copia)
	prova("firmare di nuovo non cambia niente e non scrive", esito == 0 and scritture == [])
	zitto(Acusticator.firma, nomi[0], "altra", percorso=copia)
	prova("le firme restano in ordine", leggi(copia)[nomi[0]]["usato_da"] == ["altra", "banco"])
	esito, _ = zitto(Acusticator.togli_firma, nomi[0], "banco", percorso=copia)
	prova("togli_firma toglie soltanto quella", esito == 1 and leggi(copia)[nomi[0]]["usato_da"] == ["altra"])
	zitto(Acusticator.togli_firma, nomi[0], "altra", percorso=copia)
	prova("tolta l'ultima, il campo sparisce", "usato_da" not in leggi(copia)[nomi[0]])
	esito, _ = zitto(Acusticator.cambia_firma, "banco", "banco_nuovo", percorso=copia)
	prova("cambia_firma rinomina un'app in tutta la collezione", esito == 1 and leggi(copia)[nomi[1]]["usato_da"] == ["banco_nuovo"], esito)
	esito, testo = zitto(Acusticator.firma, ["preset_inesistente_davvero"], "banco", percorso=copia)
	prova("un preset che non c'e' si salta, con l'avviso", esito == 0 and "sconosciuto" in testo)
	for sbagliata in ("", "a,b", "a.b"):
		try:
			Acusticator.firma(nomi[2], sbagliata, percorso=copia)
			errore = None
		except ValueError as e:
			errore = e
		prova(f"un identificativo d'app come {sbagliata!r} e' un errore di chi programma", errore is not None)
	inizio = time.perf_counter()
	zitto(Acusticator.firma, list(collezione)[:200], "veloce", percorso=copia)
	durata = time.perf_counter() - inizio
	prova(f"firmare duecento preset costa una scrittura, {durata * 1000:.0f} ms", durata < 1.5 and all("veloce" in leggi(copia)[n]["usato_da"] for n in list(collezione)[:200]))
	prova("e i suoni non cambiano", all(leggi(copia)[n]["score"] == collezione[n]["score"] for n in collezione))

	# 5. Quattro processi che firmano insieme, sotto il lucchetto.
	shutil.copyfile(VERA, copia)
	via = os.path.join(cartella, "via")
	gruppi = [list(collezione)[i * 25:(i + 1) * 25] for i in range(4)]
	script = os.path.join(cartella, "firmatore.py")
	with open(script, "w", encoding="utf-8") as f:
		f.write(FIRMATORE)
	processi = [subprocess.Popen([sys.executable, script, QUI, copia, f"app{i}", via, ",".join(g)], stdin=subprocess.DEVNULL,
								 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for i, g in enumerate(gruppi)]
	time.sleep(0.5)
	open(via, "w").close()
	riusciti = [int(p.communicate(timeout=120)[0].strip() or 0) for p in processi]
	dati = leggi(copia)
	mancanti = [(i, n) for i, g in enumerate(gruppi) for n in g if f"app{i}" not in dati[n].get("usato_da", [])]
	prova("quattro processi per venticinque firme ciascuno: ci sono tutte", mancanti == [] and riusciti == [25] * 4, (riusciti, mancanti[:3]))
	prova("e le firme di prima pure", all(set(collezione[n].get("usato_da", [])) <= set(dati[n].get("usato_da", [])) for n in collezione))

	# 5 bis. Dalla revisione del 13 novembre 2026: una selezione vuota non
	#        tocca niente. Fino alla V8.9.0 valeva tutta la collezione.
	shutil.copyfile(VERA, copia)
	prima_del_vuoto = impronta(copia)
	scritture.clear()
	vuoti = [
		zitto(Acusticator.firma, (n for n in collezione if n.startswith("nessuno_comincia_cosi")), "banco", percorso=copia)[0],
		zitto(Acusticator.firma, filter(lambda n: False, collezione), "banco", percorso=copia)[0],
		zitto(Acusticator.togli_firma, iter([]), "mess", percorso=copia)[0],
		zitto(Acusticator.cambia_firma, "mess", "banco", [], percorso=copia)[0],
		zitto(Acusticator.firma, None, "banco", percorso=copia)[0],
	]
	prova("un generatore, un filtro, un iteratore o un elenco vuoti, e None, non firmano niente",
		  vuoti == [0, 0, 0, 0, 0] and scritture == [] and impronta(copia) == prima_del_vuoto, vuoti)
	esito, _ = zitto(Acusticator.cambia_firma, "batnav", "batnav_banco", percorso=copia)
	prova("cambia_firma senza nomi cambia l'app in tutta la collezione", esito == firme.get("batnav") and
		  all("batnav" not in v.get("usato_da", []) for v in leggi(copia).values()), esito)

	# 6. Acu_Maker.
	shutil.copyfile(VERA, copia)
	coll = am.Collezione(copia)
	zitto(coll.apri)
	v = coll.dati[nome_firmato]
	prova("Acu_Maker mostra la descrizione con le firme ricomposte in coda",
		  am.descrizione_mostrata(v) == f"{v['descrizione']} Usato da: {', '.join(v['usato_da'])}.", am.descrizione_mostrata(v)[-60:])
	senza = next(n for n, x in coll.dati.items() if "usato_da" not in x)
	prova("e senza firme la descrizione e' quella", am.descrizione_mostrata(coll.dati[senza]) == coll.dati[senza]["descrizione"])
	trovati = am.cerca(coll.dati, f"@{app_piu}")
	prova(f"la ricerca @{app_piu} trova esattamente i preset che l'app usa", sorted(trovati) == Acusticator.usati_da(app_piu), len(trovati))
	prova("e un'app che non c'e' non trova niente", am.cerca(coll.dati, "@app_che_non_esiste") == {})
	prova("app_che_usano legge usato_da, e il prefisso non conta piu'",
		  am.app_che_usano({"mess_x": {"descrizione": "x"}}, "mess_x") == [] and am.app_che_usano(coll.dati, nome_firmato) == v["usato_da"])
	stato = am.EditorState(coll.dati[nome_firmato])
	stato.preset["score"][0][1] = round(float(stato.preset["score"][0][1]) + 0.013, 3)
	stato.modified = True
	am.menu = lambda *argomenti, **chiavi: "2"
	am.input = lambda prompt="": ""
	risposte = [f"{nome_firmato}_copia", ""]
	GBUtils.input = lambda prompt="": risposte.pop(0) if risposte else ""
	zitto(am.salva_preset, coll, nome_firmato, stato, False)
	dati = leggi(copia)
	prova("Salva come non copia le firme nel preset nuovo",
		  f"{nome_firmato}_copia" in dati and "usato_da" not in dati[f"{nome_firmato}_copia"] and dati[nome_firmato].get("usato_da") == v["usato_da"])
	# Un suono diverso dalla copia appena salvata, che altrimenti sarebbe un
	# doppione, e Acu_Maker non lo salverebbe nemmeno.
	stato.preset["score"][0][1] = round(float(stato.preset["score"][0][1]) + 0.007, 3)
	am.menu = lambda *argomenti, **chiavi: "1"
	am.input = lambda prompt="": "n"
	prima_del_no = impronta(copia)
	_, testo = zitto(am.salva_preset, coll, nome_firmato, stato, False)
	prova("sovrascrivere un preset usato avverte e chiede, e con no non scrive", "Lo usano" in testo and impronta(copia) == prima_del_no, testo[-120:])
	am.menu = GBUtils.menu
	scelte = ["a", None]
	am.menu = lambda *argomenti, **chiavi: scelte.pop(0) if scelte else None
	am.input = lambda prompt="": "banco"
	zitto(am.gestisci_firme, coll, senza)
	prova("dal menu delle firme si aggiunge un'app", leggi(copia)[senza].get("usato_da") == ["banco"])
	scelte = ["t", None]
	zitto(am.gestisci_firme, coll, senza)
	prova("e la si toglie", "usato_da" not in leggi(copia)[senza])
	# Dalla revisione del 13 novembre 2026: il menu delle firme si chiude anche
	# su un preset senza firme. Il menu finto qui sotto si comporta come quello
	# vero con una voce sola, che la restituisce senza leggere tasti; fino alla
	# 1.13.0 la voce era una sola, e Invio a vuoto ricominciava all'infinito.
	voci_viste, chiamate = [], [0]
	def menu_come_il_vero(voci, *argomenti, **chiavi):
		chiamate[0] += 1
		voci_viste.append(sorted(voci))
		if chiamate[0] > 3:
			raise RuntimeError("il menu delle firme non si chiude")
		return next(iter(voci)) if len(voci) == 1 else "a"
	am.menu = menu_come_il_vero
	am.input = lambda prompt="": ""
	try:
		zitto(am.gestisci_firme, coll, senza)
		chiuso = True
	except RuntimeError:
		chiuso = False
	prova("su un preset senza firme il menu ha sempre almeno due voci, e Invio a vuoto torna indietro",
		  chiuso and chiamate[0] == 1 and "." in voci_viste[0], (chiuso, chiamate[0], voci_viste))
	am.menu = GBUtils.menu
	_, testo = zitto(am.statistiche, coll.dati)
	prova("le statistiche contano anche le app", "Usati dalle app:" in testo and app_piu in testo, testo[-200:])
	db = {"uno": {"descrizione": "lunga lunga lunga", "score": [["c4", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]},
		  "due": {"descrizione": "corta", "usato_da": ["mess"], "score": [["c4", 0.1, 0, 0.0]], "kind": 1, "adsr": [1, 0, 100, 1]}}
	zitto(am.togli_doppioni, db)
	prova("dei doppioni resta quello firmato, con le sue firme", list(db) == ["due"] and db["due"]["usato_da"] == ["mess"])
	# Dal collaudo di Gabriele del 14 novembre 2026: il menu del preset resta
	# aperto dopo le firme, la descrizione e la rinomina, e lo si lascia con il
	# punto. Fino alla 1.13.18 ogni azione tornava all'elenco dei preset.
	chiesti, copione = [], ["f", ".", "d", "r", "."]
	def menu_del_copione(*_argomenti, p="", **_chiavi):
		chiesti.append(p)
		if len(chiesti) > 8:
			raise RuntimeError("il menu del preset non si chiude")
		return copione.pop(0) if copione else None
	am.menu = menu_del_copione
	rinominato = f"{senza}_rinominato"
	righe = ["descrizione dal menu", rinominato]
	GBUtils.input = lambda prompt="": righe.pop(0) if righe else ""
	am.input = GBUtils.input
	menu_del_preset = getattr(am, "menu_del_preset", None)
	testo, chiuso = "", False
	if menu_del_preset is not None:
		try:
			_, testo = zitto(menu_del_preset, coll, senza)
			chiuso = True
		except RuntimeError:
			pass
	am.menu = GBUtils.menu
	dati = leggi(copia)
	prova("dopo le firme, la descrizione e la rinomina si torna al menu del preset",
		  chiuso and chiesti == ["Azione> ", "Firme> ", "Azione> ", "Azione> ", "Azione> "], chiesti)
	prova("e il menu prosegue con il nome nuovo",
		  dati.get(rinominato, {}).get("descrizione") == "descrizione dal menu" and senza not in dati
		  and f"Di nuovo al preset '{rinominato}'." in testo, testo[-300:])

am.Acusticator = Acusticator
prova("la collezione vera non e' stata toccata", impronta(VERA) == PRIMA)
print(f"Prove {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
