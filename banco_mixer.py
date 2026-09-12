"""Banco di prova del mixer condiviso, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato con la V142 e la issue 8, il 12 settembre 2026.
Niente di questo fa rumore: il volume del mixer resta a zero, e cio' che si
controlla e' il comportamento, cioe' quante voci ci sono, quando finiscono,
quanti buchi, come si chiude e come si riapre. La prova nove e' la ragione per
cui il mixer e' fatto cosi': sotto il carico che fa spezzettare il suono con
il callback, scrivendo non si perde un campione.
Si lancia con
  python banco_mixer.py
e stampa in fondo quante prove sono passate.
"""
import threading
import time

import numpy as np

from GBUtils import _MixerCondiviso

totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def onda(durata, frequenza=440.0, canali=2, fs=44100):
	t = np.linspace(0, durata, int(durata * fs), endpoint=False, dtype=np.float32)
	suono = (np.sin(2 * np.pi * frequenza * t) * 0.3).astype(np.float32)
	return np.column_stack((suono, suono)) if canali == 2 else suono

def carico(secondi, quanti=4):
	fine = time.monotonic() + secondi
	def lavora():
		while time.monotonic() < fine:
			sum(i * i for i in range(2000))
	for _ in range(quanti):
		threading.Thread(target=lavora, daemon=True).start()

m = _MixerCondiviso()
m._volume = 0.0
print(f"blocco {m.BLOCCO} campioni, cioe' {m.BLOCCO / m.FS * 1000:.0f} millesimi\n")

# 1. Un suono solo, aspettato.
inizio = time.monotonic()
voce = m.suona(onda(0.4), sync=True)
durata = time.monotonic() - inizio
prova("un suono aspettato torna una voce", voce is not None)
prova("l'attesa dura quanto il suono", 0.35 <= durata <= 0.9, f"{durata:.2f} s")
prova("la voce risulta finita", voce.fine.is_set())
prova("il mixer resta aperto dopo il suono", m.stato()["aperto"])

# 2. Piu' voci insieme.
voci = [m.suona(onda(0.5), pan=p) for p in (-1.0, 0.0, 1.0)]
prova("tre voci accettate", all(v is not None for v in voci))
time.sleep(0.1)
prova("tre voci risultano attive", m.stato()["voci"] == 3, m.stato()["voci"])
for v in voci:
	v.fine.wait(timeout=2.0)
prova("le tre voci finiscono tutte", all(v.fine.is_set() for v in voci))
time.sleep(0.2)
prova("a suoni finiti non restano voci", m.stato()["voci"] == 0, m.stato()["voci"])

# 3. La panoramica.
sinistra = m.suona(onda(0.05), pan=-1.0)
centro = m.suona(onda(0.05), pan=0.0)
destra = m.suona(onda(0.05), pan=1.0)
prova("tutta a sinistra: destra muta", abs(sinistra.destra) < 0.01, sinistra.destra)
prova("tutta a destra: sinistra muta", abs(destra.sinistra) < 0.01, destra.sinistra)
prova("al centro i due lati sono pari", abs(centro.sinistra - centro.destra) < 0.01)
prova("al centro la potenza e' conservata", abs(centro.sinistra ** 2 + centro.destra ** 2 - 1.0) < 0.01)
prova("la panoramica fuori scala viene riportata dentro", m.suona(onda(0.05), pan=-9.0).sinistra > 0.99)
time.sleep(0.3)

# 4. Fermare una voce.
lunga = m.suona(onda(3.0))
time.sleep(0.2)
m.ferma(lunga)
finita = lunga.fine.wait(timeout=1.5)
prova("una voce fermata finisce subito", finita)
prova("e sparisce dalle attive", m.stato()["voci"] == 0, m.stato()["voci"])

# 5. Fermare tutto.
for _ in range(4):
	m.suona(onda(3.0))
time.sleep(0.15)
quante = m.ferma()
prova("ferma tutte le voci", quante == 4, quante)
time.sleep(0.3)
prova("dopo il fermo non restano voci", m.stato()["voci"] == 0, m.stato()["voci"])

# 6. Il limite di voci: la piu' vecchia lascia il posto.
m._voci_max = 3
vecchie = [m.suona(onda(2.0)) for _ in range(3)]
nuova = m.suona(onda(2.0))
time.sleep(0.1)
prova("oltre il limite si resta al limite", m.stato()["voci"] <= 3, m.stato()["voci"])
prova("la piu' vecchia viene svegliata", vecchie[0].fine.is_set())
prova("la nuova e' entrata", nuova is not None and not nuova.fine.is_set())
m.ferma()
m._voci_max = m.VOCI_MAX
time.sleep(0.3)

# 7. Mono e stereo.
prova("un buffer mono viene accettato", m.suona(onda(0.2, canali=1), sync=True) is not None)
prova("un buffer stereo viene accettato", m.suona(onda(0.2, canali=2), sync=True) is not None)
prova("un buffer vuoto non fa niente", m.suona(np.zeros((0, 2), dtype=np.float32)) is None)
prova("un buffer inesistente non fa niente", m.suona(None) is None)

# 8. Il ricampionamento.
a_22050 = onda(0.3, fs=22050)
voce = m.suona(a_22050, fs=22050, sync=True)
prova("un buffer a frequenza diversa viene accettato", voce is not None)
prova("e viene riportato alla frequenza dello stream", voce is not None and abs(len(voce.buffer) - len(a_22050) * 2) < 100,
	  f"{len(voce.buffer)} campioni da {len(a_22050)}")

# 9. I buchi sotto carico: e' la ragione per cui il mixer e' fatto cosi'.
m.buchi = 0
carico(2.5, 4)
time.sleep(0.3)
m.suona(onda(1.5), sync=True)
prova("sotto carico nessun buco", m.buchi == 0, f"{m.buchi} buchi")

# 10. La chiusura.
m.suona(onda(2.0))
time.sleep(0.2)
m.chiudi()
prova("dopo la chiusura il mixer e' chiuso", not m.stato()["aperto"])
prova("e non restano voci", m.stato()["voci"] == 0, m.stato()["voci"])
prova("il filo della pompa e' uscito", m._pompa is None or not m._pompa.is_alive())

# 11. Si riapre da solo quando serve.
voce = m.suona(onda(0.2), sync=True)
prova("dopo la chiusura si riapre da solo", voce is not None and m.stato()["aperto"])
m.chiudi()

# 12. Nessun errore per strada.
prova("nessun errore registrato", m.ultimo_errore is None, m.ultimo_errore)

# 13. La scelta dell'uscita, che la issue 8 chiedeva.
m2 = _MixerCondiviso()
m2._volume = 0.0
device, nome_api = m2.scegli_uscita()
prova("la scelta dell'uscita risponde", device is not None or nome_api is not None, f"device {device}, api {nome_api}")
voce = m2.suona(onda(0.2), sync=True)
prova("e con quella si suona", voce is not None and voce.fine.is_set())
print(f"uscita scelta: dispositivo {device}, interfaccia {nome_api}")
try:
	m2.scegli_uscita(api="interfaccia che non esiste")
	prova("un'interfaccia inventata solleva", False)
except ValueError:
	prova("un'interfaccia inventata solleva ValueError", True)
m2.chiudi()
print(f"\nProve {totale}, passate {passate}.")
