"""Banco di prova dell'evanescenza di CWzator, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' auto).
Nato con la V165 e la issue 39, il 20 settembre 2026.
Niente di questo fa rumore: si genera con play=False e si misurano i campioni.
Le domande a cui il banco risponde sono cinque.
La prima e' se senza qsb non cambi niente: l'audio dev'essere identico campione
per campione a quello di sempre, perche' un parametro nuovo che cambia il
comportamento predefinito e' un difetto, non una funzionalita'.
La seconda e' se l'evanescenza si senta: l'inviluppo del messaggio deve variare,
e variare lentamente con una banda bassa e in fretta con una alta. Si misura
contando quante volte l'inviluppo attraversa la propria media: e' la definizione
operativa di "quanto spesso va e viene".
La terza e' se tocchi soltanto l'ampiezza: la velocita' effettiva, il numero di
campioni e la durata devono restare identici, perche' la velocita' si misura
sulle durate e non sulle ampiezze.
La quarta e' se non saturi: il messaggio con evanescenza non deve mai superare
il livello che avrebbe senza, che e' la differenza voluta da cwsim.
La quinta e' se il seme renda le prove ripetibili, e se i valori sbagliati
vengano rifiutati con un messaggio invece che suonati.
Si lancia con
  python banco_qsb.py
e stampa in fondo quante prove sono passate.
"""

import sys

import numpy as np

from GBUtils import CWzator

FS = 44100
MESSAGGIO = "paris paris paris paris paris paris paris paris paris paris"
totale = passate = 0


def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")


def genera(**kw):
	kw.setdefault("play", False)
	kw.setdefault("msg", MESSAGGIO)
	kw.setdefault("wpm", 25)
	kw.setdefault("fs", FS)
	return CWzator(**kw)


def inviluppo(audio, finestra=2205):
	"""Il livello del messaggio mezzo decimo di secondo alla volta, silenzi esclusi.

	Serve a vedere l'evanescenza senza vedere il morse: si prende il massimo di
	ogni finestra, che dentro una finestra da cinquanta millesimi cade sempre su
	un tratto acceso a queste velocita'.
	"""
	quante = audio.size // finestra
	if quante == 0:
		return np.array([])
	tagliato = np.abs(audio[: quante * finestra].astype(np.float64)).reshape(quante, finestra)
	livelli = tagliato.max(axis=1)
	return livelli[livelli > 0]


def attraversamenti(livelli):
	"""Quante volte il livello passa da una parte all'altra della sua media."""
	if livelli.size < 2:
		return 0
	sopra = livelli > livelli.mean()
	return int(np.count_nonzero(np.diff(sopra.astype(np.int8))))


# 1. Senza qsb non cambia niente.
senza, rwpm_senza = genera()
ancora, _ = genera()
prova("senza qsb l'audio e' quello di sempre, campione per campione",
	  np.array_equal(senza.audio_data, ancora.audio_data))

# 2. Con qsb l'inviluppo varia, e varia con la velocita' che gli si chiede.
lento, rwpm_lento = genera(qsb=0.3, qsb_seme=11)
veloce, rwpm_veloce = genera(qsb=15, qsb_seme=11)
liv_senza = inviluppo(senza.audio_data)
liv_lento = inviluppo(lento.audio_data)
liv_veloce = inviluppo(veloce.audio_data)
prova("senza qsb l'inviluppo e' piatto",
	  liv_senza.std() / liv_senza.mean() < 0.02, f"variazione {liv_senza.std() / liv_senza.mean():.4f}")
prova("con qsb l'inviluppo varia",
	  liv_lento.std() / liv_lento.mean() > 0.1, f"variazione {liv_lento.std() / liv_lento.mean():.4f}")
lenti = attraversamenti(liv_lento)
veloci = attraversamenti(liv_veloce)
prova("il flutter va e viene piu' spesso dell'evanescenza lenta",
	  veloci > lenti, f"lento {lenti}, veloce {veloci}")

# 3. L'evanescenza tocca solo l'ampiezza.
prova("la velocita' effettiva non cambia", rwpm_lento == rwpm_senza, f"{rwpm_lento} contro {rwpm_senza}")
prova("il numero di campioni non cambia",
	  lento.audio_data.size == senza.audio_data.size, f"{lento.audio_data.size} contro {senza.audio_data.size}")
prova("il pan resta quello chiesto", genera(qsb=0.3, pan=-40)[0].pan == -40)

# 4. Non satura: il livello non supera mai quello senza evanescenza.
picco_senza = int(np.abs(senza.audio_data.astype(np.int32)).max())
peggiore = 0
for seme in range(8):
	handle, _ = genera(qsb=0.3, qsb_seme=seme)
	peggiore = max(peggiore, int(np.abs(handle.audio_data.astype(np.int32)).max()))
prova("il messaggio con evanescenza non supera mai quello senza",
	  peggiore <= picco_senza, f"picco {peggiore} contro {picco_senza}")
prova("e resta dentro gli interi a sedici bit", peggiore <= 32767, peggiore)

# 5. Il seme e i valori sbagliati.
primo, _ = genera(qsb=0.3, qsb_seme=5)
secondo, _ = genera(qsb=0.3, qsb_seme=5)
diverso, _ = genera(qsb=0.3, qsb_seme=6)
prova("lo stesso seme da' lo stesso inviluppo", np.array_equal(primo.audio_data, secondo.audio_data))
prova("un seme diverso da' un inviluppo diverso", not np.array_equal(primo.audio_data, diverso.audio_data))
for valore in (0, -1, 200, "tanto", True):
	handle, _ = genera(qsb=valore)
	prova(f"qsb {valore!r} viene rifiutato con un messaggio",
		  handle is None and "qsb" in (CWzator.ultimo_errore or ""), CWzator.ultimo_errore)

# 6. Anche il file WAV riceve l'evanescenza, che e' cio' che l'orecchio sente.
prova("l'evanescenza e' nei campioni, quindi anche nel WAV di to_file",
	  not np.array_equal(lento.audio_data, senza.audio_data))

# 7. La profondita', V169 e issue 44: quanto l'evanescenza puo' scendere.
piena, _ = genera(qsb=0.3, qsb_seme=11, qsb_profondita=100)
prova("a profondita' cento l'audio e' quello di prima, campione per campione",
	  np.array_equal(piena.audio_data, lento.audio_data))
nulla, _ = genera(qsb=0.3, qsb_seme=11, qsb_profondita=0)
prova("a profondita' zero l'evanescenza sparisce", np.array_equal(nulla.audio_data, senza.audio_data))
sola, _ = genera(qsb_profondita=40)
prova("senza qsb la profondita' non ha effetto", np.array_equal(sola.audio_data, senza.audio_data))
leggera, rwpm_leggera = genera(qsb=0.3, qsb_seme=11, qsb_profondita=40)
liv_leggera = inviluppo(leggera.audio_data)
rapporto_leggera = liv_leggera / liv_senza
rapporto_piena = liv_lento / liv_senza
prova("a quaranta il segnale non scende mai sotto il sessanta per cento",
	  liv_leggera.size == liv_senza.size and rapporto_leggera.min() >= 0.595, f"minimo {rapporto_leggera.min():.3f}")
prova("a cento scende piu' in basso che a quaranta",
	  rapporto_piena.min() < rapporto_leggera.min(), f"cento {rapporto_piena.min():.3f}, quaranta {rapporto_leggera.min():.3f}")
prova("a quaranta l'inviluppo varia meno che a cento",
	  liv_leggera.std() / liv_leggera.mean() < liv_lento.std() / liv_lento.mean())
prova("a quaranta l'evanescenza c'e' ancora",
	  liv_leggera.std() / liv_leggera.mean() > 0.02, f"variazione {liv_leggera.std() / liv_leggera.mean():.4f}")
prova("con la profondita' velocita' e campioni non cambiano",
	  rwpm_leggera == rwpm_senza and leggera.audio_data.size == senza.audio_data.size)
prova("e il livello non supera mai quello senza evanescenza",
	  int(np.abs(leggera.audio_data.astype(np.int32)).max()) <= picco_senza)
for valore in (-1, 101, "molta", True):
	handle, _ = genera(qsb=0.3, qsb_profondita=valore)
	prova(f"qsb_profondita {valore!r} viene rifiutata con un messaggio",
		  handle is None and "qsb_profondita" in (CWzator.ultimo_errore or ""), CWzator.ultimo_errore)

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
