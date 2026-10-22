"""Banco di prova della rilettura delle schede audio, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
Nato con la V216 e rileggi_dispositivi_audio, il 22 ottobre 2026, per le
cuffie Bluetooth di MeTeOra.
Niente di questo fa rumore: il mixer suona soltanto silenzio, per avere uno
stream aperto da chiudere.
Le domande sono quattro. Se dopo la rilettura l'elenco e' lo stesso, quando
nessuno ha toccato le schede; se il mixer ritrova la sua scheda con
l'indice nuovo e torna a suonare; se una scelta che non c'e' piu' torna a
nessuna scelta; se costa quello che la docstring promette.
Le cuffie che arrivano e se ne vanno davvero il banco non le puo' fingere:
quella prova si fa a mano, connettendo e spegnendo un dispositivo vero.
Si lancia con
  python banco_rilettura_audio.py
e stampa in fondo quante prove sono passate.
"""
import sys
import time

import numpy as np
import sounddevice as sd

import GBUtils
from GBUtils import Acusticator, elenco_dispositivi_audio, rileggi_dispositivi_audio

totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def coppie():
	return sorted((v["dispositivo"], v["interfaccia"]) for v in elenco_dispositivi_audio(prova="nessuno"))

def nome_di(indice):
	d = sd.query_devices(indice)
	return d["name"], sd.query_hostapis(d["hostapi"])["name"]

mixer = GBUtils._mixer_condiviso()
silenzio = np.zeros((4410, 2), dtype=np.float32)
prima = coppie()
print(f"Questa macchina: {len(prima)} uscite.\n")

esito = rileggi_dispositivi_audio()
prova("le chiavi del risultato", set(esito) == {"prima", "dopo", "arrivate", "sparite", "mixer"}, esito)
prova("senza cambi l'elenco e' lo stesso", coppie() == prima)
prova("nessuna arrivata e nessuna sparita", not esito["arrivate"] and not esito["sparite"], esito)
prova("prima e dopo contano le uscite", esito["prima"] == esito["dopo"] == len(prima), esito)

# Il mixer sceglie e apre: poi la rilettura deve chiuderlo e ritrovargli la
# stessa scheda.
prova("il mixer apre con il silenzio", mixer.suona(silenzio) is not None, mixer.ultimo_errore)
indice = Acusticator.stato()["device"]
prova("il mixer ha una scelta", indice is not None)
scheda = nome_di(indice) if indice is not None else None
tempi = []
for _ in range(5):
	partenza = time.perf_counter()
	esito = rileggi_dispositivi_audio()
	tempi.append((time.perf_counter() - partenza) * 1000)
prova("la rilettura chiude il mixer", not Acusticator.stato()["stream_aperto"])
prova("il mixer ritrova la sua scheda", esito["mixer"] == "ritrovata", esito["mixer"])
nuovo = Acusticator.stato()["device"]
prova("l'indice porta alla stessa scheda", nuovo is not None and nome_di(nuovo) == scheda, (scheda, nuovo))
prova("dopo la rilettura il mixer torna a suonare", mixer.suona(silenzio, sync=True) is not None, mixer.ultimo_errore)
prova("e lo stream e' aperto", Acusticator.stato()["stream_aperto"])
tempi.sort()
print(f"  rilettura: mediana {tempi[2]:.0f} ms, la piu' lenta {tempi[-1]:.0f} ms")
prova("costa meno di mezzo secondo", tempi[2] < 500, f"{tempi[2]:.0f} ms")

# Una scelta che non porta a niente: un indice oltre l'ultimo dispositivo
# fa le veci di una scheda sparita.
mixer.chiudi()
with mixer._avvio:
	mixer._device = len(sd.query_devices()) + 10
esito = rileggi_dispositivi_audio()
prova("una scheda sparita e' persa", esito["mixer"] == "persa", esito["mixer"])
prova("e il mixer torna a nessuna scelta", Acusticator.stato()["device"] is None and Acusticator.stato()["interfaccia"] is None)
prova("da nessuna scelta sceglie da se'", mixer.suona(silenzio, sync=True) is not None and Acusticator.stato()["device"] is not None,
	  mixer.ultimo_errore)
mixer.chiudi()
esito = rileggi_dispositivi_audio()
# CWzator e' una funzione, non una classe: l'attributo resta un staticmethod,
# che si chiama lo stesso.
alias = GBUtils.CWzator.rileggi_dispositivi
prova("CWzator ha la stessa funzione", getattr(alias, "__func__", alias) is rileggi_dispositivi_audio and callable(alias))

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
