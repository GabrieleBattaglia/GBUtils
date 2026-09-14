"""Banco di prova della pulizia dei residui, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto).
Nato con la V158 e la issue 27, il 14 settembre 2026.
pulisci_residui cancella file, quindi e' la funzione di GBUtils che puo' fare
piu' danno di tutte: un manifesto sbagliato e un'installazione si svuota. Qui
non si tocca nessuna installazione vera. Il banco costruisce in una cartella
temporanea dei pacchetti finti, con dentro una _internal fatta come quella di
PyInstaller, li rovina come farebbe un aggiornamento a fusione e poi guarda
che cosa la pulizia toglie e, soprattutto, che cosa lascia.
Le prove piu' importanti non sono quelle in cui cancella, ma quelle in cui
rinuncia: senza manifesto, con un manifesto vuoto, con un manifesto che non
descrive quella installazione. In tutti quei casi non deve sparire niente.
C'e' anche il giro completo: crea_archivio_release scrive il manifesto,
l'archivio viene fuso sopra un'installazione vecchia come faceva lo script
fino alla V1.4, e la pulizia deve rimettere le cose a posto.
Si lancia con
  python banco_residui.py
e stampa in fondo quante prove sono passate.
"""
import os
import shutil
import sys
import tempfile
import zipfile

sys.path.insert(0, "E:/git/mine/GBUtils")
from GBUtils import crea_archivio_release, pulisci_residui

passate = 0
totale = 0

def verifica(nome, condizione, ottenuto=None):
	global passate, totale
	totale += 1
	if condizione:
		passate += 1
		return
	print(f"SBAGLIATA: {nome}" + (f" -> {ottenuto!r}" if ottenuto is not None else ""))

def scrivi(percorso, contenuto=""):
	os.makedirs(os.path.dirname(percorso), exist_ok=True)
	with open(percorso, "w", encoding="utf-8") as f:
		f.write(contenuto)

def albero(radice):
	"""Tutto quello che c'e' sotto la radice, file e cartelle, con la barra.
	Il log dell'aggiornamento resta fuori: lo scrive la pulizia stessa quando
	rinuncia, e comparirebbe come una differenza in ogni confronto."""
	trovato = set()
	for cartella, sottocartelle, file in os.walk(radice):
		dentro = os.path.relpath(cartella, radice)
		for nome in list(sottocartelle) + list(file):
			if nome == "auto_updater_error.log":
				continue
			relativo = nome if dentro == "." else os.path.join(dentro, nome)
			trovato.add(relativo.replace("\\", "/"))
	return trovato

# La _internal di un pacchetto qualunque: qualche libreria, un pacchetto con il
# suo binario, e i file che PyInstaller mette sempre.
PACCHETTO = {
	"base_library.zip": "finto",
	"python314.dll": "finto",
	"libcrypto-3.dll": "finto",
	"simplejson/__init__.py": "finto",
	"simplejson/_speedups.cp314-win_amd64.pyd": "finto",
	"requests/__init__.py": "finto",
	"requests/sessions.py": "finto",
	"certifi/cacert.pem": "finto",
}
# I file dell'utente, che vivono accanto all'eseguibile e non si toccano mai.
ACCANTO = {
	"App.exe": "finto",
	"settings.json": "i miei dati",
	"log/ieri.log": "la mia giornata",
}

def costruisci(dove, dentro=None, accanto=None, manifesto=None):
	"""Un'installazione finta: l'eseguibile, i dati dell'utente e _internal."""
	os.makedirs(dove, exist_ok=True)
	for nome, contenuto in (accanto if accanto is not None else ACCANTO).items():
		scrivi(os.path.join(dove, nome.replace("/", os.sep)), contenuto)
	for nome, contenuto in (dentro if dentro is not None else PACCHETTO).items():
		scrivi(os.path.join(dove, "_internal", nome.replace("/", os.sep)), contenuto)
	if manifesto is not None:
		scrivi(os.path.join(dove, "_internal", "manifesto.txt"), manifesto)
	return dove

def manifesto_di(nomi, commento=True):
	"""Il manifesto come lo scrive crea_archivio_release: commenti e un file
	per riga, se stesso compreso."""
	testa = "# Elenco dei file di _internal che questo pacchetto contiene.\n# Righe di commento come questa non contano.\n" if commento else ""
	return testa + "\n".join(sorted([*nomi, "manifesto.txt"], key=str.lower)) + "\n"

def log_di(dove):
	percorso = os.path.join(dove, "auto_updater_error.log")
	if not os.path.isfile(percorso):
		return ""
	with open(percorso, encoding="utf-8") as f:
		return f.read()

def main():
	base = tempfile.mkdtemp(prefix="banco_residui_")
	try:
		prove(base)
	finally:
		shutil.rmtree(base, ignore_errors=True)
	print()
	print(f"Prove {totale}, passate {passate}.")
	return 0 if passate == totale else 1

def prove(base):
	# 1. Da sorgente, senza indicare la cartella: non c'e' niente da pulire e
	# soprattutto non si va a indovinare quale sia l'installazione.
	verifica("da sorgente non fa niente", pulisci_residui() == 0)

	# 2. Il pacchetto in un pezzo solo non ha _internal: la pulizia non deve
	# nemmeno provarci, perche' li' accanto ci sono solo i dati dell'utente.
	dove = costruisci(os.path.join(base, "un_pezzo_solo"), dentro={})
	shutil.rmtree(os.path.join(dove, "_internal"), ignore_errors=True)
	prima = albero(dove)
	verifica("senza _internal non tocca niente", pulisci_residui(dove) == 0)
	verifica("senza _internal l'albero e' intatto", albero(dove) == prima)

	# 3. Un pacchetto anteriore al manifesto: la pulizia rinuncia in silenzio,
	# perche' non ha modo di sapere che cosa sia legittimo.
	dove = costruisci(os.path.join(base, "senza_manifesto"))
	scrivi(os.path.join(dove, "_internal", "residuo.pyd"), "avanzo")
	prima = albero(dove)
	verifica("senza manifesto non tocca niente", pulisci_residui(dove) == 0)
	verifica("senza manifesto l'albero e' intatto", albero(dove) == prima)
	verifica("senza manifesto non scrive nel log", log_di(dove) == "")

	# 4. Un manifesto di soli commenti elencherebbe zero file, e prendendolo
	# alla lettera si cancellerebbe tutta la _internal.
	dove = costruisci(os.path.join(base, "manifesto_vuoto"),
					  manifesto="# solo commenti\n#\n\n")
	prima = albero(dove)
	verifica("manifesto vuoto: non cancella", pulisci_residui(dove) == 0)
	verifica("manifesto vuoto: albero intatto", albero(dove) == prima)
	verifica("manifesto vuoto: lo scrive nel log", "senza nemmeno un file" in log_di(dove))

	# 5. Il manifesto di un altro pacchetto: elenca file che qui non ci sono,
	# quindi non descrive questa installazione e non se ne fa niente.
	dove = costruisci(os.path.join(base, "manifesto_altrui"),
					  manifesto=manifesto_di([*PACCHETTO, "roba_che_non_ce.dll"]))
	scrivi(os.path.join(dove, "_internal", "residuo.pyd"), "avanzo")
	prima = albero(dove)
	verifica("manifesto altrui: non cancella", pulisci_residui(dove) == 0)
	verifica("manifesto altrui: albero intatto", albero(dove) == prima)
	verifica("manifesto altrui: lo scrive nel log", "non descrive questa installazione" in log_di(dove))
	verifica("manifesto altrui: dice quale file manca", "roba_che_non_ce.dll" in log_di(dove))

	# 6. L'installazione a posto: c'e' il manifesto e non c'e' niente in piu'.
	dove = costruisci(os.path.join(base, "gia_pulita"), manifesto=manifesto_di(PACCHETTO))
	prima = albero(dove)
	verifica("niente da togliere: zero", pulisci_residui(dove) == 0)
	verifica("niente da togliere: albero intatto", albero(dove) == prima)
	verifica("niente da togliere: log muto", log_di(dove) == "")

	# 7. Il caso che ha rotto Dadillo: la versione nuova non porta simplejson,
	# la fusione lascia la cartella con dentro il solo binario, e Python la
	# importa come pacchetto namespace facendo ombra al modulo vero.
	pacchetto_nuovo = {k: v for k, v in PACCHETTO.items() if not k.startswith("simplejson/")}
	dove = costruisci(os.path.join(base, "simplejson"), dentro=PACCHETTO,
					  manifesto=manifesto_di(pacchetto_nuovo))
	# Come dopo la fusione: il .py non c'e' piu', il .pyd si', perche' la
	# versione nuova non ha sovrascritto niente in quella cartella.
	os.remove(os.path.join(dove, "_internal", "simplejson", "__init__.py"))
	tolti = pulisci_residui(dove)
	dopo = albero(dove)
	verifica("simplejson: due elementi tolti", tolti == 2, tolti)
	verifica("simplejson: il binario e' sparito", "_internal/simplejson/_speedups.cp314-win_amd64.pyd" not in dopo)
	verifica("simplejson: la cartella vuota e' sparita", "_internal/simplejson" not in dopo)
	verifica("simplejson: requests e' rimasto", "_internal/requests/sessions.py" in dopo)
	verifica("simplejson: il manifesto e' rimasto", "_internal/manifesto.txt" in dopo)

	# 8. I residui di un ambiente di compilazione diverso: moduli di un altro
	# Python, cartelle dist-info, e cio' che sta in fondo a un ramo.
	extra = {
		"python313.dll": "vecchio",
		"_ctypes.cp313-win_amd64.pyd": "vecchio",
		"cryptography-42.0.0.dist-info/METADATA": "vecchio",
		"cryptography-42.0.0.dist-info/RECORD": "vecchio",
		"dateutil/zoneinfo/dateutil-zoneinfo.tar.gz": "vecchio",
	}
	dove = costruisci(os.path.join(base, "ambiente_diverso"),
					  dentro={**PACCHETTO, **extra}, manifesto=manifesto_di(PACCHETTO))
	accanto_prima = {v for v in albero(dove) if not v.startswith("_internal")}
	tolti = pulisci_residui(dove)
	dopo = albero(dove)
	# Cinque file e tre cartelle rimaste vuote: dist-info, zoneinfo e dateutil.
	verifica("ambiente diverso: otto elementi tolti", tolti == 8, tolti)
	verifica("ambiente diverso: i residui sono spariti",
			 not [v for v in dopo if "313" in v or "dist-info" in v or "dateutil" in v])
	verifica("ambiente diverso: il pacchetto buono e' intero",
			 all(f"_internal/{n}" in dopo for n in PACCHETTO))
	verifica("ambiente diverso: fuori da _internal non si tocca niente",
			 {v for v in dopo if not v.startswith("_internal")} == accanto_prima)
	verifica("ambiente diverso: log muto", log_di(dove) == "")

	# 9. Windows non distingue le maiuscole nei nomi: un manifesto scritto con
	# le minuscole non deve far sembrare residuo un file scritto altrimenti.
	dove = costruisci(os.path.join(base, "maiuscole"),
					  dentro={"Python314.DLL": "finto", "Lib/Site.py": "finto"},
					  manifesto=manifesto_di(["python314.dll", "lib/site.py"]))
	tolti = pulisci_residui(dove)
	verifica("maiuscole: niente tolto", tolti == 0, tolti)
	verifica("maiuscole: i file ci sono ancora", "_internal/Lib/Site.py" in albero(dove))

	# 10. Un file che non si puo' cancellare perche' e' aperto non ferma la
	# pulizia: gli altri se ne vanno lo stesso e il guaio finisce nel log.
	dove = costruisci(os.path.join(base, "file_in_uso"),
					  dentro={**PACCHETTO, "occupato.dll": "aperto", "libero.dll": "chiuso"},
					  manifesto=manifesto_di(PACCHETTO))
	# Windows non lascia cancellare un file aperto: tenerlo aperto qui e' il
	# modo di provare il caso senza dover caricare davvero una libreria.
	with open(os.path.join(dove, "_internal", "occupato.dll"), "rb"):
		tolti = pulisci_residui(dove)
	dopo = albero(dove)
	verifica("file in uso: l'altro residuo se ne va", "_internal/libero.dll" not in dopo)
	verifica("file in uso: quello aperto resta", "_internal/occupato.dll" in dopo)
	verifica("file in uso: conta solo quelli tolti", tolti == 1, tolti)
	verifica("file in uso: lo scrive nel log", "non rimossi" in log_di(dove))

	# 11. Il giro completo, dal pacchetto all'installazione rovinata: e' la
	# prova che manifesto e pulizia parlino davvero la stessa lingua.
	dist = os.path.join(base, "dist", "App")
	# Accanto all'eseguibile ci va soltanto l'eseguibile: i file dell'utente
	# nella dist finirebbero nell'archivio e l'aggiornamento li riporterebbe
	# indietro sopra quelli veri, che e' un guaio diverso da questo.
	costruisci(dist, dentro=pacchetto_nuovo, accanto={"App.exe": "finto"})
	archivio = os.path.join(base, "App.zip")
	quanti, _lasciati = crea_archivio_release("App", cartella_dist=dist, archivio=archivio, silenzioso=True)
	with zipfile.ZipFile(archivio) as zip_in:
		dentro_archivio = set(zip_in.namelist())
	verifica("giro completo: il manifesto e' nell'archivio", "_internal/manifesto.txt" in dentro_archivio)
	verifica("giro completo: il conto comprende il manifesto", quanti == len(dentro_archivio), quanti)

	installazione = costruisci(os.path.join(base, "installata"), dentro=PACCHETTO)
	os.remove(os.path.join(installazione, "_internal", "simplejson", "__init__.py"))
	scrivi(os.path.join(installazione, "settings.json"), "le mie impostazioni")
	# La fusione dello script vecchio: copia sopra senza cancellare niente.
	with zipfile.ZipFile(archivio) as zip_in:
		zip_in.extractall(installazione)
	dopo_fusione = albero(installazione)
	verifica("giro completo: la fusione lascia il residuo",
			 "_internal/simplejson/_speedups.cp314-win_amd64.pyd" in dopo_fusione)
	tolti = pulisci_residui(installazione)
	dopo = albero(installazione)
	verifica("giro completo: la pulizia lo toglie", tolti == 2, tolti)
	verifica("giro completo: simplejson non c'e' piu'", "_internal/simplejson" not in dopo)
	verifica("giro completo: il pacchetto nuovo e' intero",
			 all(f"_internal/{n}" in dopo for n in pacchetto_nuovo))
	with open(os.path.join(installazione, "settings.json"), encoding="utf-8") as f:
		verifica("giro completo: le impostazioni sono quelle", f.read() == "le mie impostazioni")
	verifica("giro completo: al secondo avvio non c'e' piu' niente da fare",
			 pulisci_residui(installazione) == 0)
	verifica("giro completo: log muto", log_di(installazione) == "")

	# 12. Chi non vuole il manifesto non se lo ritrova, e la dist non cambia in
	# nessuno dei due casi: il file nasce nell'archivio.
	archivio_senza = os.path.join(base, "App_senza.zip")
	dist_prima = albero(dist)
	crea_archivio_release("App", cartella_dist=dist, archivio=archivio_senza,
						  silenzioso=True, manifesto=False)
	with zipfile.ZipFile(archivio_senza) as zip_in:
		verifica("senza manifesto: l'archivio non ce l'ha",
				 "_internal/manifesto.txt" not in zip_in.namelist())
	verifica("la cartella dist non viene toccata", albero(dist) == dist_prima)

if __name__ == "__main__":
	sys.exit(main())
