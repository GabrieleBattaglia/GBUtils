"""Banco di prova di polipo, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
Nato con la V243, il 5 novembre 2026, con i parametri lingua e plurali che
servono a MeTeOra.
Ogni prova lavora in una cartella temporanea, con i cataloghi finti scritti
da polib, la lingua sorgente italiana e i percorsi assoluti: niente cambia
fuori da quella cartella, che alla fine si cancella.
Si lancia con
  python banco_polipo.py
e stampa in fondo quante prove sono passate.
"""
import json
import os
import shutil
import sys
import tempfile

import polib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from GBUtils import polipo

PLURALI_POLACCHI = "nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);"

def catalogo(cartella, lingua, voci, plurali="nplurals=2; plural=(n != 1);", plurale=None):
	"""Scrive locales/lingua/LC_MESSAGES/messages.mo con le voci date e, se
	c'e', una voce al plurale: (singolare, plurale, forme tradotte)."""
	po = polib.POFile()
	po.metadata = {"Content-Type": "text/plain; charset=UTF-8", "Plural-Forms": plurali}
	for originale, tradotto in voci.items():
		po.append(polib.POEntry(msgid=originale, msgstr=tradotto))
	if plurale:
		singolare, plurale_it, forme = plurale
		po.append(polib.POEntry(msgid=singolare, msgid_plural=plurale_it, msgstr_plural=dict(enumerate(forme))))
	destinazione = os.path.join(cartella, "locales", lingua, "LC_MESSAGES")
	os.makedirs(destinazione, exist_ok=True)
	po.save_as_mofile(os.path.join(destinazione, "messages.mo"))

class Banco:
	def __init__(self):
		self.totale = self.passate = 0

	def prova(self, titolo, visto, atteso):
		self.totale += 1
		if visto == atteso:
			self.passate += 1
			print(f"{titolo}: ok")
		else:
			print(f"{titolo}: {visto!r} invece di {atteso!r}")

def chiama(cartella, **opzioni):
	return polipo(source_language="it", localedir=os.path.join(cartella, "locales"), config_path=os.path.join(cartella, "impostazioni"),
		interattivo=False, **opzioni)

def salvata(cartella):
	with open(os.path.join(cartella, "impostazioni", "selected_language.json"), encoding="utf-8") as f:
		return json.load(f)["language_code"]

def prove(b, cartella):
	catalogo(cartella, "en", {"Ciao": "Hello"}, plurale=("{n} brano", "{n} brani", ["{n} track", "{n} tracks"]))
	catalogo(cartella, "pl", {"Ciao": "Cześć"}, PLURALI_POLACCHI, ("{n} brano", "{n} brani", ["{n} utwór", "{n} utwory", "{n} utworów"]))
	esito = chiama(cartella)
	b.prova("senza plurali la coppia di sempre", (len(esito), esito[0], esito[1]("Ciao")), (2, "it", "Ciao"))
	codice, _, ngettext = chiama(cartella, plurali=True)
	b.prova("lingua sorgente, plurale con uno", ngettext("{n} brano", "{n} brani", 1), "{n} brano")
	b.prova("lingua sorgente, plurale con zero", ngettext("{n} brano", "{n} brani", 0), "{n} brani")
	codice, _, ngettext = chiama(cartella, lingua="en", plurali=True)
	b.prova("lingua scelta, codice", codice, "en")
	b.prova("lingua scelta, traduzione", _("Ciao"), "Hello")
	b.prova("lingua scelta, plurale", [ngettext("{n} brano", "{n} brani", n) for n in (1, 2)], ["{n} track", "{n} tracks"])
	b.prova("lingua scelta, salvata", salvata(cartella), "en")
	codice, _ = chiama(cartella)
	b.prova("la scelta salvata vale anche senza passarla", (codice, _("Ciao")), ("en", "Hello"))
	codice, _ = chiama(cartella, lingua="xx")
	b.prova("una lingua senza catalogo non conta", (codice, salvata(cartella)), ("en", "en"))
	codice, _, ngettext = chiama(cartella, lingua="pl", plurali=True)
	b.prova("polacco, tre forme", [ngettext("{n} brano", "{n} brani", n) for n in (1, 3, 5, 22, 25)],
		["{n} utwór", "{n} utwory", "{n} utworów", "{n} utwory", "{n} utworów"])
	codice, _ = chiama(cartella, lingua="it")
	b.prova("si torna alla lingua sorgente", (codice, _("Ciao"), salvata(cartella)), ("it", "Ciao", "it"))
	shutil.rmtree(os.path.join(cartella, "locales"))
	esito = chiama(cartella, plurali=True)
	b.prova("senza cataloghi la terna della sorgente", (len(esito), esito[0], esito[2]("a", "b", 2)), (3, "it", "b"))

def principale():
	b = Banco()
	cartella = tempfile.mkdtemp(prefix="banco_polipo_")
	try:
		prove(b, cartella)
	finally:
		shutil.rmtree(cartella, ignore_errors=True)
	print(f"Prove passate: {b.passate} su {b.totale}.")
	return 0 if b.passate == b.totale else 1

if __name__ == "__main__":
	raise SystemExit(principale())
