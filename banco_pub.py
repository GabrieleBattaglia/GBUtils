"""Banco di prova delle utilita' del PUB, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalità auto).
Nato con la V221 di GBUtils e la 1.1.0 di GBwx, il 23 ottobre 2026, per la
issue 57.
Non e' distruttivo: os.startfile, gli appunti, il registro, i processi e il
segnale dello screen reader sono sostituiti, e nessuna mail si apre ne' si
spedisce. Le sole letture vere sono quelle di informazioni_di_sistema e di
programma_di_posta, che interrogano il sistema senza cambiarne niente, per
vedere che sul computer vero rispondano senza errori e senza dati personali.
La finestra di GBwx si costruisce senza mostrarla, e i pulsanti si premono
mandando i loro eventi. Cio' che il banco non puo' dire e' come suona a NVDA
e sul display braille, e se la bozza arriva integra nel programma di posta:
per quello c'e' la prova con Gabriele.
Si lancia con
  python banco_pub.py
e stampa in fondo quante prove sono passate.
"""
import os
import re
import sys

import GBwx
import wx

import GBUtils
from GBUtils import (
	PUB_GRUPPO,
	PUB_ISCRIZIONE,
	apri_mail,
	indirizzo_mailto,
	informazioni_di_sistema,
	programma_di_posta,
	righe_informazioni,
)

CHIAVI = ("windows", "windows_versione", "windows_build", "architettura", "processore", "nuclei", "memoria_totale",
	"memoria_libera", "lingua", "screen_reader", "schermo", "scala", "python", "compilato")
PULSANTI = {"apri": "&Apri nel programma di posta", "passi": "&Passo per passo", "ok": "&OK", "chiudi": "&Chiudi", "annulla": "&Annulla"}
SPIEGAZIONE = "Preparo una bozza in {programma}. Spediscila tu."
SENZA_POSTA = "Il programma di posta non parte."
PASSI = (("Incolla l'indirizzo nel campo A, poi premi OK.", PUB_GRUPPO), ("Incolla l'oggetto, poi premi OK.", "Aiuto con MESS"),
	("Incolla il testo, poi premi OK.", "Riga uno\nRiga due"), ("Ora spedisci la mail.", None))

class Banco:
	"""Il conteggio delle prove, una riga per prova."""

	def __init__(self):
		self.totale = 0
		self.passate = 0

	def verifica(self, titolo, condizione):
		self.totale += 1
		if condizione:
			self.passate += 1
		print(f"{titolo}: {'ok' if condizione else 'fallita'}")

class Sostituto:
	"""Prende il posto di una funzione, ricorda come e' stato chiamato e
	risponde il valore dato, o solleva l'eccezione data."""

	def __init__(self, risposta=None, eccezione=None):
		self.risposta = risposta
		self.eccezione = eccezione
		self.chiamate = []

	def __call__(self, *argomenti):
		self.chiamate.append(argomenti)
		if self.eccezione is not None:
			raise self.eccezione
		return self.risposta

class Sostituzioni:
	"""Sostituisce attributi di moduli per la durata di un blocco with, e li
	rimette com'erano anche se una prova solleva."""

	def __init__(self, *terne):
		self.terne = terne
		self.originali = []

	def __enter__(self):
		for modulo, nome, valore in self.terne:
			self.originali.append((modulo, nome, getattr(modulo, nome)))
			setattr(modulo, nome, valore)
		return self

	def __exit__(self, *errore):
		for modulo, nome, valore in reversed(self.originali):
			setattr(modulo, nome, valore)

def prova_costanti(b):
	b.verifica("indirizzo del gruppo", PUB_GRUPPO == "prg-user-blind@googlegroups.com")
	b.verifica("indirizzo dell'iscrizione", PUB_ISCRIZIONE == "prg-user-blind+subscribe@googlegroups.com")

def prova_mailto(b):
	b.verifica("spazi come %20, mai come +", indirizzo_mailto("a@b.it", "uno due", "tre quattro") == "mailto:a@b.it?subject=uno%20due&body=tre%20quattro")
	attesi = {indirizzo_mailto("a@b.it", corpo=testo) for testo in ("a\nb", "a\r\nb", "a\rb")}
	b.verifica("ogni a capo diventa %0D%0A", attesi == {"mailto:a@b.it?body=a%0D%0Ab"})
	b.verifica("accenti in UTF-8", indirizzo_mailto("a@b.it", "è") == "mailto:a@b.it?subject=%C3%A8")
	b.verifica("segni riservati codificati", indirizzo_mailto("a@b.it", "&?#=+%") == "mailto:a@b.it?subject=%26%3F%23%3D%2B%25")
	b.verifica("iscrizione: il piu' resta, niente oggetto ne' corpo", indirizzo_mailto(PUB_ISCRIZIONE) == "mailto:prg-user-blind+subscribe@googlegroups.com")
	b.verifica("oggetto su due righe: una riga sola", indirizzo_mailto("a@b.it", "uno\r\ndue") == "mailto:a@b.it?subject=uno%20due")
	b.verifica("solo il corpo", indirizzo_mailto("a@b.it", "", "x") == "mailto:a@b.it?body=x")
	b.verifica("due destinatari con la virgola", indirizzo_mailto("a@b.it,c@d.it") == "mailto:a@b.it,c@d.it")

def prova_apri_mail(b):
	avvio = Sostituto()
	with Sostituzioni((os, "startfile", avvio), (GBUtils, "programma_di_posta", Sostituto("Thunderbird"))):
		esito = apri_mail(PUB_GRUPPO, "Aiuto", "Riga uno\nRiga due")
	b.verifica("con la posta: vero, e un avvio solo con l'indirizzo giusto",
		esito is True and avvio.chiamate == [(indirizzo_mailto(PUB_GRUPPO, "Aiuto", "Riga uno\nRiga due"),)])
	avvio = Sostituto()
	with Sostituzioni((os, "startfile", avvio), (GBUtils, "programma_di_posta", Sostituto(None))):
		esito = apri_mail(PUB_GRUPPO, "Aiuto", "x")
	b.verifica("senza posta associata: falso, e nessun avvio", esito is False and not avvio.chiamate)
	with Sostituzioni((os, "startfile", Sostituto(eccezione=OSError("finto"))), (GBUtils, "programma_di_posta", Sostituto("Thunderbird"))):
		esito = apri_mail(PUB_GRUPPO, "Aiuto", "x")
	b.verifica("avvio che fallisce: falso", esito is False)
	avvio = Sostituto()
	lungo = "è" * 400
	with Sostituzioni((os, "startfile", avvio), (GBUtils, "programma_di_posta", Sostituto("Thunderbird"))):
		oltre = apri_mail(PUB_GRUPPO, "Aiuto", lungo)
		chiamate_oltre = len(avvio.chiamate)
		senza_limite = apri_mail(PUB_GRUPPO, "Aiuto", lungo, lunghezza_massima=None)
	b.verifica("oltre duemila caratteri: falso, e nessun avvio", oltre is False and chiamate_oltre == 0)
	b.verifica("senza limite: si apre", senza_limite is True and len(avvio.chiamate) == 1)
	nome = programma_di_posta()
	b.verifica(f"programma di posta vero, in sola lettura: {nome}", nome is None or (isinstance(nome, str) and nome))
	b.verifica("protocollo senza programma: None", GBUtils._programma_associato("protocollo-inesistente-del-banco-pub") is None)

def prova_informazioni_vere(b):
	informazioni = informazioni_di_sistema()
	for chiave, valore in informazioni:
		print(f"  {chiave}: {valore!r}")
	b.verifica("le chiavi, nell'ordine", tuple(chiave for chiave, _valore in informazioni) == CHIAVI)
	b.verifica("i valori sono testi, numeri, vero o falso, o None", all(valore is None or isinstance(valore, (str, int, bool)) for _chiave, valore in informazioni))
	personali = [os.environ.get("USERNAME", ""), os.environ.get("COMPUTERNAME", ""), os.path.expanduser("~")]
	personali = [voce.lower() for voce in personali if len(voce) >= 4]
	testo = " ".join(str(valore) for _chiave, valore in informazioni).lower()
	b.verifica("niente nome utente, nome del computer o cartella personale", not any(voce in testo for voce in personali))
	valori = dict(informazioni)
	b.verifica("compilato falso dai sorgenti", valori["compilato"] is False)
	b.verifica("python con versione e bit", re.fullmatch(r"\d+\.\d+\.\d+\S* (32|64) bit", valori["python"] or "") is not None)
	if sys.platform == "win32":
		b.verifica("build con l'aggiornamento cumulativo", re.fullmatch(r"\d+\.\d+", valori["windows_build"] or "") is not None)
		b.verifica("Windows 11 dalla build 22000", int(valori["windows_build"].split(".")[0]) < 22000 or valori["windows"].startswith("Windows 11"))
		b.verifica("memoria in GB col punto", re.fullmatch(r"\d+\.\d GB", valori["memoria_totale"] or "") is not None)
		b.verifica("schermo larghezza per altezza", re.fullmatch(r"\d+x\d+", valori["schermo"] or "") is not None)
		b.verifica("scala in percento", re.fullmatch(r"\d+%", valori["scala"] or "") is not None)
	virgola = dict(informazioni_di_sistema(","))
	b.verifica("separatore virgola per le memorie", virgola["memoria_totale"] is None or "," in virgola["memoria_totale"])
	sys.frozen = True
	try:
		congelato = dict(informazioni_di_sistema())["compilato"]
	finally:
		del sys.frozen
	b.verifica("compilato vero nel pacchetto simulato", congelato is True)

def prova_windows_simulato(b):
	def registro(valori):
		return lambda radice, percorso, nomi: {nome: valori.get(nome) for nome in nomi}

	undici = {"ProductName": "Windows 10 Pro", "DisplayVersion": "23H2", "CurrentBuildNumber": "22631", "UBR": 4317}
	with Sostituzioni((GBUtils, "_valori_registro", registro(undici))):
		esito = GBUtils._windows()
	b.verifica("ProductName dice 10, la build dice 11", esito == ("Windows 11 Pro", "23H2", "22631.4317"))
	dieci = {"ProductName": "Windows 10 Home", "ReleaseId": "2009", "CurrentBuildNumber": "19045", "UBR": 5011}
	with Sostituzioni((GBUtils, "_valori_registro", registro(dieci))):
		esito = GBUtils._windows()
	b.verifica("Windows 10 resta 10, versione da ReleaseId", esito == ("Windows 10 Home", "2009", "19045.5011"))
	with Sostituzioni((GBUtils, "_valori_registro", registro({}))):
		esito = GBUtils._windows()
	b.verifica("registro vuoto: il nome del sistema, il resto None", bool(esito[0]) and esito[1:] == (None, None))
	with Sostituzioni((GBUtils, "_valori_registro", registro({"ProcessorNameString": "  Intel(R)   Core   i7  "}))):
		esito = GBUtils._processore()
	b.verifica("processore con gli spazi ripuliti", esito == "Intel(R) Core i7")

def prova_screen_reader_simulato(b):
	def con(processi, versione, segnale):
		return Sostituzioni((GBUtils, "_processi", processi), (GBUtils, "_versione_processo", versione), (GBUtils, "_segnale_screen_reader", Sostituto(segnale)))

	versione = Sostituto("2026.3.1")
	with con(Sostituto([("explorer.exe", 1), ("nvda.exe", 2)]), versione, True):
		esito = GBUtils._screen_reader()
	b.verifica("NVDA con la versione", esito == "NVDA 2026.3.1" and versione.chiamate == [(2,)])
	versione = Sostituto("2026.3.1")
	with con(Sostituto([("nvda.exe", 2), ("narrator.exe", 3)]), versione, True):
		esito = GBUtils._screen_reader()
	b.verifica("NVDA e Narrator, senza versione per Narrator", esito == "NVDA 2026.3.1, Narrator" and versione.chiamate == [(2,)])
	with con(Sostituto([("jfw.exe", 4)]), Sostituto(None), True):
		esito = GBUtils._screen_reader()
	b.verifica("JAWS senza versione leggibile", esito == "JAWS")
	with con(Sostituto([("nvda.exe", 2)]), Sostituto(eccezione=OSError("finto")), True):
		esito = GBUtils._screen_reader()
	b.verifica("versione che solleva: il nome soltanto", esito == "NVDA")
	with con(Sostituto([("explorer.exe", 1)]), Sostituto(None), True):
		esito = GBUtils._screen_reader()
	b.verifica("nessuno riconosciuto, segnale acceso: vero", esito is True)
	with con(Sostituto([]), Sostituto(None), False):
		esito = GBUtils._screen_reader()
	b.verifica("nessuno e segnale spento: falso", esito is False)
	with con(Sostituto(eccezione=OSError("finto")), Sostituto(None), True):
		esito = GBUtils._screen_reader()
	b.verifica("processi illeggibili: vale il segnale", esito is True)

def prova_righe(b):
	informazioni = [("windows", "Windows 11 Pro"), ("nuclei", 1), ("screen_reader", True), ("scala", None), ("compilato", False)]
	etichette = {"compilato": "Compilato", "windows": "Sistema", "nuclei": "Nuclei", "manca": "Manca", "scala": "Scala"}
	righe = righe_informazioni(etichette, informazioni, {True: "sì", False: "no"})
	b.verifica("ordine delle etichette, chiavi senza etichetta o senza valore fuori",
		righe == ["Compilato: no", "Sistema: Windows 11 Pro", "Nuclei: 1"])
	righe = righe_informazioni({"screen_reader": "Screen reader", "compilato": "Compilato"}, informazioni)
	b.verifica("vero e falso senza parole: fuori", righe == [])
	righe = righe_informazioni({"nuclei": "Nuclei", "scala": "Scala"}, informazioni, {True: "sì", None: "non letto"}, " = ")
	b.verifica("un nucleo non diventa si', None con la sua parola, separatore dato", righe == ["Nuclei = 1", "Scala = non letto"])
	righe = righe_informazioni({"python": "Python", "lingua": "Lingua"})
	b.verifica("senza informazioni: quelle del sistema", len(righe) >= 1 and righe[0].startswith("Python: "))

def dialogo(posta, **altro):
	"""Una finestra_mail costruita senza mostrarla, con la posta data."""
	with Sostituzioni((GBUtils, "programma_di_posta", Sostituto(posta))):
		return GBwx._FinestraMail(None, "Chiedi aiuto al PUB", (PUB_GRUPPO, "Aiuto con MESS", "Riga uno\nRiga due"),
			SPIEGAZIONE, altro.get("passi", PASSI), PULSANTI, SENZA_POSTA, (560, 420))

def premi(pulsante):
	evento = wx.CommandEvent(wx.EVT_BUTTON.typeId, pulsante.GetId())
	evento.SetEventObject(pulsante)
	pulsante.GetEventHandler().ProcessEvent(evento)

def predefinito(finestra, pulsante):
	attuale = finestra.GetDefaultItem()
	return attuale is not None and attuale.GetId() == pulsante.GetId()

def prova_finestra(b):
	appunti = Sostituto(True)
	avvio = Sostituto()
	with Sostituzioni((GBwx, "_negli_appunti", appunti), (os, "startfile", avvio), (GBUtils, "programma_di_posta", Sostituto("Thunderbird"))):
		d = dialogo("Thunderbird")
		b.verifica("con la posta: la spiegazione col nome del programma", d.testo.GetValue() == "Preparo una bozza in Thunderbird. Spediscila tu.")
		b.verifica("con la posta: Apri, Passo per passo e Chiudi, Apri predefinito",
			d.apri.IsShown() and d.passo_per_passo.IsShown() and not d.ok.IsShown() and predefinito(d, d.apri))
		premi(d.apri)
		b.verifica("Apri: la bozza parte, una volta, con l'indirizzo giusto",
			avvio.chiamate == [(indirizzo_mailto(PUB_GRUPPO, "Aiuto con MESS", "Riga uno\nRiga due"),)] and d.riuscita)
		b.verifica("Apri: la finestra resta aperta, e Invio ora chiude", d.GetReturnCode() == 0 and predefinito(d, d.chiudi))
		b.verifica("Apri: niente negli appunti", not appunti.chiamate)
		premi(d.passo_per_passo)
		b.verifica("Passo per passo: l'indirizzo negli appunti", appunti.chiamate == [(PUB_GRUPPO,)])
		b.verifica("primo passo: istruzione e indirizzo, senza premessa", d.testo.GetValue() == f"{PASSI[0][0]}\n{PUB_GRUPPO}")
		b.verifica("nei passi: OK predefinito, Annulla al posto di Chiudi, Apri nascosto",
			d.ok.IsShown() and not d.apri.IsShown() and not d.passo_per_passo.IsShown() and predefinito(d, d.ok) and d.chiudi.GetLabel() == "&Annulla")
		b.verifica("l'area di testo e' una sola, e viene prima dei pulsanti",
			sum(isinstance(figlio, wx.TextCtrl) for figlio in d.pannello.GetChildren()) == 1 and d.pannello.GetChildren()[0] is d.testo)
		premi(d.ok)
		b.verifica("secondo passo: l'oggetto negli appunti", appunti.chiamate[-1] == ("Aiuto con MESS",) and d.testo.GetValue().endswith("\nAiuto con MESS"))
		premi(d.ok)
		b.verifica("terzo passo: il corpo negli appunti", appunti.chiamate[-1] == ("Riga uno\nRiga due",))
		premi(d.ok)
		b.verifica("passo senza testo: niente negli appunti, solo l'istruzione", len(appunti.chiamate) == 3 and d.testo.GetValue() == PASSI[3][0])
		premi(d.ok)
		b.verifica("ultimo OK: chiude con OK", d.GetReturnCode() == wx.ID_OK and d.riuscita)
		d.Destroy()
	appunti = Sostituto(True)
	with Sostituzioni((GBwx, "_negli_appunti", appunti)):
		d = dialogo(None)
		b.verifica("senza posta: subito al primo passo, con la premessa",
			d.testo.GetValue() == f"{SENZA_POSTA}\n{PASSI[0][0]}\n{PUB_GRUPPO}" and appunti.chiamate == [(PUB_GRUPPO,)] and not d.apri.IsShown())
		premi(d.chiudi)
		b.verifica("senza posta, chiusa prima della fine: non riuscita", not d.riuscita)
		d.Destroy()
	appunti = Sostituto(True)
	with Sostituzioni((GBwx, "_negli_appunti", appunti), (os, "startfile", Sostituto(eccezione=OSError("finto"))), (GBUtils, "programma_di_posta", Sostituto("Thunderbird"))):
		d = dialogo("Thunderbird")
		premi(d.apri)
		b.verifica("Apri che fallisce: ai passi da se', con la premessa",
			d.testo.GetValue().startswith(f"{SENZA_POSTA}\n") and appunti.chiamate == [(PUB_GRUPPO,)] and not d.riuscita)
		d.Destroy()
	try:
		dialogo("Thunderbird", passi=())
		vuoti = False
	except ValueError:
		vuoti = True
	b.verifica("senza passi: ValueError", vuoti)

def prova_finestra_mail(b):
	modale = GBwx._FinestraMail.ShowModal
	avvio = Sostituto()
	try:
		with Sostituzioni((os, "startfile", avvio), (GBUtils, "programma_di_posta", Sostituto("Thunderbird"))):
			GBwx._FinestraMail.ShowModal = lambda finestra: (finestra._apri(), wx.ID_CANCEL)[1]
			aperta = GBwx.finestra_mail(None, "Titolo", PUB_ISCRIZIONE, "", "Testo", SPIEGAZIONE, PASSI[:1], PULSANTI, SENZA_POSTA)
			GBwx._FinestraMail.ShowModal = lambda finestra: wx.ID_CANCEL
			chiusa = GBwx.finestra_mail(None, "Titolo", PUB_ISCRIZIONE, "", "Testo", SPIEGAZIONE, PASSI[:1], PULSANTI, SENZA_POSTA)
	finally:
		GBwx._FinestraMail.ShowModal = modale
	b.verifica("finestra_mail: vero se la bozza si e' aperta", aperta is True and len(avvio.chiamate) == 1)
	b.verifica("finestra_mail: falso se si chiude e basta", chiusa is False)

def main():
	b = Banco()
	app = wx.App(False)
	prova_costanti(b)
	prova_mailto(b)
	prova_apri_mail(b)
	prova_informazioni_vere(b)
	prova_windows_simulato(b)
	prova_screen_reader_simulato(b)
	prova_righe(b)
	prova_finestra(b)
	prova_finestra_mail(b)
	del app
	print(f"Prove {b.totale}, passate {b.passate}.")
	return 0 if b.passate == b.totale else 1

if __name__ == "__main__":
	sys.exit(main())
