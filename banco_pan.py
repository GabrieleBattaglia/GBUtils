"""Banco di prova dello spostamento di panorama, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato con la V149 e la issue 18, il 13 settembre 2026.
Niente di questo fa rumore: si sintetizza senza riprodurre e si guardano i
campioni e i panorami.
Le domande sono tre. La prima e' se con pan a zero, o senza pan, il suono resti
identico campione per campione su tutti i preset della collezione, perche' da
questo dipende che nessun programma esistente si accorga del cambiamento.
La seconda e' se il panorama esca mai dai bordi, che era il difetto della somma
con taglio proposta nella issue.
La terza e' se il movimento del preset si conservi: deve stringersi soltanto
quanto serve, e per niente quando c'e' posto.
Si lancia con
  python banco_pan.py
e stampa in fondo quante prove sono passate.
"""
import sys

import numpy as np

from GBUtils import Acusticator, _panorama_spostato, _sintetizza, parse_pan_values

totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def panorami(score):
	"""Tutti i valori di panorama di uno score piatto, estremi compresi."""
	valori = []
	for i in range(0, len(score) - 3, 4):
		v = parse_pan_values(score[i + 2])
		valori.extend([v] if isinstance(v, float) else list(v))
	return valori

def suono(nome, **kw):
	score, kind, adsr = Acusticator.preset(nome, **kw)
	return _sintetizza(score, kind, adsr, 44100) if score else None

def e_rumore(nome):
	"""I preset a rumore, cioe' i kind da 5 a 8, nascono da numeri casuali e
	sono diversi a ogni sintesi: si confrontano sui panorami, non sui
	campioni, altrimenti risulterebbero sempre diversi anche senza toccare
	niente."""
	return Acusticator.preset(nome)[1] >= 5

NOMI = Acusticator.list()
# Gli spostamenti su cui si prova: fermi e in portamento, nei due versi.
SPOSTAMENTI = [-1.0, -0.6, -0.25, 0.0, 0.25, 0.6, 1.0,
			   (-1.0, 1.0), (1.0, -1.0), (-0.5, 0.5), (0.5, -0.5), (0.3, 0.3)]

print(f"Banco dello spostamento di panorama. Preset in collezione: {len(NOMI)}.\n")

# 1. Con pan a zero, o senza, non cambia un campione.
intonati = [n for n in NOMI if not e_rumore(n)]
rumori = [n for n in NOMI if e_rumore(n)]
diversi_zero, diversi_none, diversi_coppia = [], [], []
for nome in intonati:
	base = suono(nome)
	if base is None:
		continue
	if not np.array_equal(base, suono(nome, pan=0)):
		diversi_zero.append(nome)
	if not np.array_equal(base, suono(nome, pan=None)):
		diversi_none.append(nome)
	if not np.array_equal(base, suono(nome, pan=(0, 0))):
		diversi_coppia.append(nome)
prova(f"con pan a zero non cambia un campione, su {len(intonati)} preset intonati",
	  not diversi_zero, f"{len(diversi_zero)} diversi, il primo {diversi_zero[:1]}")
prova("con pan a None non cambia un campione", not diversi_none, diversi_none[:1])
prova("con pan a una coppia di zeri non cambia un campione", not diversi_coppia, diversi_coppia[:1])
diversi_rumore = [n for n in rumori
				  if panorami(Acusticator.preset(n)[0]) != panorami(Acusticator.preset(n, pan=0)[0])]
prova(f"e sui {len(rumori)} rumori il panorama resta identico",
	  not diversi_rumore, diversi_rumore[:1])

# 2. Il panorama non esce mai dai bordi, con nessuno spostamento.
fuori = []
for nome in NOMI:
	for spostamento in SPOSTAMENTI:
		score, _, _ = Acusticator.preset(nome, pan=spostamento)
		if not score:
			continue
		for v in panorami(score):
			if v < -1.0 - 1e-9 or v > 1.0 + 1e-9:
				fuori.append((nome, spostamento, v))
prova(f"il panorama resta sempre fra -1 e 1, su {len(NOMI)} preset per {len(SPOSTAMENTI)} spostamenti",
	  not fuori, f"{len(fuori)} fuori, il primo {fuori[:1]}")

# 3. Quanto costerebbe invece sommare e tagliare, che e' cio' che si e' evitato.
sbattuti = 0
mossi = 0
for nome in NOMI:
	score, _, _ = Acusticator.preset(nome)
	valori = panorami(score)
	if not valori or max(valori) - min(valori) <= 1e-9:
		continue
	mossi += 1
	if max(valori) + 0.6 > 1.0 + 1e-9:
		sbattuti += 1
print(f"  preset che si muovono nel panorama: {mossi}")
print(f"  di questi, quanti sbatterebbero contro il bordo sommando 0,6: {sbattuti}")
prova("il confronto con la somma e taglio e' significativo", sbattuti > 0, sbattuti)

# 4. Su un preset fermo al centro, lo spostamento e' esattamente quello chiesto.
centrati = [n for n in NOMI if max(map(abs, panorami(Acusticator.preset(n)[0]))) < 1e-9]
prova(f"ci sono preset tutti al centro su cui misurare: {len(centrati)}", len(centrati) > 50, len(centrati))
esatti = True
for nome in centrati[:40]:
	for spostamento in (-1.0, -0.6, 0.0, 0.25, 1.0):
		score, _, _ = Acusticator.preset(nome, pan=spostamento)
		if any(abs(v - spostamento) > 1e-9 for v in panorami(score)):
			esatti = False
prova("un preset centrato si sposta esattamente dove si chiede", esatti)

# 5. Quando c'e' posto, il movimento non si stringe affatto.
#    Un preset che sta fra -0,2 e 0,2 spostato di 0,3 ha ancora posto.
score_stretto = ["c4", 0.1, -0.2, 0.5, "e4", 0.1, 0.0, 0.5, "g4", 0.1, 0.2, 0.5]
spostato = _panorama_spostato(score_stretto, 0.3)
larghezza_prima = max(panorami(score_stretto)) - min(panorami(score_stretto))
larghezza_dopo = max(panorami(spostato)) - min(panorami(spostato))
prova("con posto a sufficienza il movimento non si stringe",
	  abs(larghezza_prima - larghezza_dopo) < 1e-9, f"{larghezza_prima:.3f} contro {larghezza_dopo:.3f}")
prova("e si sposta tutto di quanto si e' chiesto",
	  abs(min(panorami(spostato)) - 0.1) < 1e-9 and abs(max(panorami(spostato)) - 0.5) < 1e-9,
	  panorami(spostato))

# 6. Quando non c'e' posto, si stringe quel tanto e non di piu'.
#    volo_radente va da -1 a 1: spostato di 0,6 deve stare fra 0,2 e 1.
score_largo = ["c4", 0.1, -1.0, 0.5, "e4", 0.1, 0.0, 0.5, "g4", 0.1, 1.0, 0.5]
spostato = _panorama_spostato(score_largo, 0.6)
prova("senza posto il movimento si stringe fino al bordo, non oltre",
	  abs(max(panorami(spostato)) - 1.0) < 1e-9 and abs(min(panorami(spostato)) - 0.2) < 1e-9,
	  panorami(spostato))
prova("e il movimento resta un movimento, non si appiattisce",
	  max(panorami(spostato)) - min(panorami(spostato)) > 0.7,
	  max(panorami(spostato)) - min(panorami(spostato)))
spostato = _panorama_spostato(score_largo, 1.0)
prova("al bordo esatto il movimento si annulla, tutto da un lato",
	  all(abs(v - 1.0) < 1e-9 for v in panorami(spostato)), panorami(spostato))

# 7. La coppia fa scorrere il centro lungo tutto il suono, non dentro ogni nota.
score_centrato = ["c4", 0.1, 0, 0.5, "e4", 0.1, 0, 0.5, "g4", 0.1, 0, 0.5, "b4", 0.1, 0, 0.5]
spostato = _panorama_spostato(score_centrato, (-1.0, 1.0))
valori = panorami(spostato)
prova("la coppia parte dal primo valore", abs(valori[0] + 1.0) < 1e-9, valori[0])
prova("la coppia arriva al secondo", abs(valori[-1] - 1.0) < 1e-9, valori[-1])
prova("e in mezzo cresce senza tornare indietro",
	  all(valori[i] <= valori[i + 1] + 1e-9 for i in range(len(valori) - 1)), valori)
prova("le note di mezzo stanno dove il tempo dice",
	  abs(valori[2] + 0.5) < 1e-9 and abs(valori[4] - 0.0) < 1e-9, valori)

# 8. I portamenti contrari si sommano invece di annullarsi a caso.
score_lr = ["c4", 0.4, (-1.0, 1.0), 0.5]
contrario = _panorama_spostato(score_lr, (1.0, -1.0))
prova("quartina che va a destra dentro un generale che va a sinistra: resta dentro i bordi",
	  all(-1.0 - 1e-9 <= v <= 1.0 + 1e-9 for v in panorami(contrario)), panorami(contrario))
# Con il generale ai due estremi non c'e' spazio in nessun istante, quindi il
# movimento della quartina si annulla e resta solo quello generale: e' la
# conseguenza voluta di un fattore unico calcolato sul caso peggiore.
prova("con il generale ai bordi resta solo il movimento generale",
	  abs(panorami(contrario)[0] - 1.0) < 1e-9 and abs(panorami(contrario)[1] + 1.0) < 1e-9,
	  panorami(contrario))
# Con un generale piu' mite i due movimenti si incontrano a meta' strada e,
# essendo uguali e opposti, si annullano: il suono resta fermo al centro. Non
# e' un caso trattato a parte, e' la somma che viene zero.
mite = _panorama_spostato(score_lr, (0.5, -0.5))
valori_mite = panorami(mite)
prova("due portamenti uguali e opposti si annullano in un panorama fermo",
	  len(valori_mite) == 1 and abs(valori_mite[0]) < 1e-9, valori_mite)
# Se invece il generale e' meno ampio del movimento interno, vince il movimento
# interno e il verso resta il suo.
meno_ampio = _panorama_spostato(score_lr, (0.25, -0.25))
valori_meno = panorami(meno_ampio)
prova("con un generale meno ampio vince il verso della quartina",
	  len(valori_meno) == 2 and valori_meno[0] < valori_meno[1], valori_meno)
solo_generale = _panorama_spostato(["c4", 0.4, 0, 0.5], (0.5, -0.5))
prova("e da soli il generale fa quello che dice",
	  panorami(solo_generale) == [0.5, -0.5], panorami(solo_generale))
score_rl = ["c4", 0.4, (1.0, -1.0), 0.5]
concorde = _panorama_spostato(score_rl, (1.0, -1.0))
prova("quartina e generale che vanno dalla stessa parte restano dentro i bordi",
	  all(-1.0 - 1e-9 <= v <= 1.0 + 1e-9 for v in panorami(concorde)), panorami(concorde))

# 9. Le tre porte danno lo stesso risultato.
nome = "conferma" if "conferma" in NOMI else NOMI[0]
da_preset, kind, adsr = Acusticator.preset(nome, pan=0.6)
da_mano = _panorama_spostato(Acusticator.preset(nome)[0], 0.6)
prova("preset e la funzione danno lo stesso score", panorami(da_preset) == panorami(da_mano))
buffer_preset = _sintetizza(da_preset, kind, adsr, 44100)
score_base, kind_base, adsr_base = Acusticator.preset(nome)
buffer_chiamabile = _sintetizza(_panorama_spostato(score_base, 0.6), kind_base, adsr_base, 44100)
prova("e l'oggetto chiamabile produce lo stesso suono",
	  np.array_equal(buffer_preset, buffer_chiamabile))

# 10. Un pan senza senso non zittisce il suono.
for sbagliato in ("", None, [], [1, 2, 3], {"a": 1}, True):
	if sbagliato is None:
		continue
	score, _, _ = Acusticator.preset(nome, pan=sbagliato)
	prova(f"un pan sbagliato, {sbagliato!r}, lascia comunque lo score",
		  bool(score), score)

# 11. Il suono cambia davvero: spostato non e' uguale a fermo.
largo = [n for n in intonati
		 if max(panorami(Acusticator.preset(n)[0])) - min(panorami(Acusticator.preset(n)[0])) > 1.5]
prova(f"ci sono preset intonati a escursione piena su cui provare: {len(largo)}", len(largo) >= 5, len(largo))
cambiati = 0
for nome in largo:
	if not np.array_equal(suono(nome), suono(nome, pan=0.6)):
		cambiati += 1
prova("spostare un preset a escursione piena cambia davvero il suono",
	  cambiati == len(largo), f"{cambiati} su {len(largo)}")

# 12. L'energia finisce dove deve: spostando a destra il canale destro cresce.
nome = centrati[0]
base = suono(nome)
destra = suono(nome, pan=0.9)
sinistra = suono(nome, pan=-0.9)
def peso(buffer):
	sx = float(np.sum(np.abs(buffer[:, 0])))
	dx = float(np.sum(np.abs(buffer[:, 1])))
	return sx, dx
sx_b, dx_b = peso(base)
sx_d, dx_d = peso(destra)
sx_s, dx_s = peso(sinistra)
prova("al centro i due canali pesano uguale", abs(sx_b - dx_b) / max(sx_b, dx_b) < 0.01)
prova("spostato a destra pesa il canale destro", dx_d > sx_d * 5, f"sx {sx_d:.0f}, dx {dx_d:.0f}")
prova("spostato a sinistra pesa il canale sinistro", sx_s > dx_s * 5, f"sx {sx_s:.0f}, dx {dx_s:.0f}")
prova("la potenza complessiva non cambia spostando",
	  abs((sx_d**2 + dx_d**2) - (sx_b**2 + dx_b**2)) / (sx_b**2 + dx_b**2) < 0.3,
	  f"centro {sx_b**2 + dx_b**2:.0f}, destra {sx_d**2 + dx_d**2:.0f}")

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
