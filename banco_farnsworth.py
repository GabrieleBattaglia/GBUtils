"""Banco di prova del Farnsworth di CWzator, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato con la V148 e la issue 16, il 12 settembre 2026.
Niente di questo fa rumore: si genera con play=False e si misurano i campioni.
Le domande a cui il banco risponde sono tre.
La prima e' se il conto sia esatto: la parola campione PARIS, con il suo spazio
finale, deve durare esattamente 1,2 per cinquanta diviso la velocita' effettiva
chiesta, con qualunque combinazione di pesi. E' la definizione stessa di
velocita' nel Morse, e la si misura per differenza fra due messaggi.
La seconda e' se le spaziature siano quelle che il mondo si aspetta: a pesi
standard devono coincidere con la formula ARRL, e non devono dipendere da cosa
il messaggio contiene.
La terza e' se il Farnsworth lasci in pace i pesi l, s e p: il carattere
prodotto con e senza dev'essere lo stesso, campione per campione.
La quarta e' se la velocita' restituita sia quella giusta: con il Farnsworth
e' l'effettiva, cioe' la stessa su qualunque testo, mentre la velocita' del
singolo testo resta leggibile nel PlaybackHandle.
Si lancia con
  python banco_farnsworth.py
e stampa in fondo quante prove sono passate.
"""
import contextlib
import importlib.util
import itertools
import os
import subprocess
import sys
import tempfile

import numpy as np

from GBUtils import CWzator

QUI = os.path.dirname(os.path.abspath(__file__))
FS = 44100
CODA = round(FS * 0.005)  # il silenzio di cinque millesimi che chiude ogni messaggio
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
	return CWzator(**kw)

def durata(handle):
	"""I secondi di suono, coda esclusa."""
	return (handle.audio_data.size - CODA) / FS

def blocchi(audio, pitch=550):
	"""Toni e silenzi del messaggio, in ordine, come coppie acceso e durata.
	I passaggi per lo zero dell'onda non sono silenzio: si chiudono con una
	chiusura morfologica lunga un periodo, che lascia intatti i bordi dei
	tratti veri."""
	if audio.size == 0:
		return []
	finestra = int(FS / pitch) + 2
	acceso = np.abs(audio.astype(np.int32)) > 0
	dilatato = np.convolve(acceso.astype(np.int32), np.ones(finestra, np.int32), "same") > 0
	acceso = np.convolve((~dilatato).astype(np.int32), np.ones(finestra, np.int32), "same") == 0
	cambi = np.flatnonzero(np.diff(acceso.astype(np.int8))) + 1
	bordi = np.concatenate(([0], cambi, [acceso.size]))
	return [(bool(acceso[a]), (b - a) / FS) for a, b in itertools.pairwise(bordi)]

def silenzi(audio, pitch=550):
	"""Le durate dei soli silenzi interni, coda esclusa."""
	tratti = blocchi(audio, pitch)
	return [d for i, (acceso, d) in enumerate(tratti) if not acceso and 0 < i < len(tratti) - 1]

def conta(msg):
	"""Punti, linee, spazi fra simboli, fra lettere e fra parole del messaggio,
	con le stesse regole che usa CWzator, piu' le unita' standard."""
	mappa = CWzator(get_map=True)
	parole = msg.lower().split()
	def suona(parola):
		return any(mappa.get(ch) for ch in parola)
	n_punti = n_linee = n_intra = n_lettere = n_parole = 0
	for i, parola in enumerate(parole):
		sonore = [ch for ch in parola if mappa.get(ch)]
		for lettera in sonore:
			codice = mappa[lettera]
			n_punti += codice.count(".")
			n_linee += codice.count("-")
			n_intra += len(codice) - 1
		if sonore:
			n_lettere += len(sonore) - 1
		if suona(parola) and any(suona(w) for w in parole[i + 1:]):
			n_parole += 1
	unita = n_punti + 3 * n_linee + n_intra + 3 * n_lettere + 7 * n_parole
	return n_punti, n_linee, n_intra, n_lettere, n_parole, unita

# I pesi su cui si prova: gli standard, quelli che Gabriele usa davvero e una
# manciata di combinazioni sparse, comprese quelle che rallentano tanto.
PESI = [(30, 50, 50), (32, 53, 34), (30, 50, 30), (45, 50, 50), (30, 70, 50),
		(20, 40, 60), (40, 60, 40), (60, 90, 70), (25, 45, 55), (35, 55, 45)]
MESSAGGI = ["paris", "cq cq de iz4apu k", "e", "ee", "e e", "test di velocita 599",
			"the quick brown fox jumps over the lazy dog", "5nn tu 73"]

print("Banco del Farnsworth. Nessun suono: si generano i campioni e si misurano.\n")

# 1. Senza il parametro non cambia un campione: confronto con la versione di git.
sorgente = subprocess.run(["git", "-C", QUI, "show", "HEAD:GBUtils.py"],
						  capture_output=True, check=True).stdout
temporaneo = os.path.join(QUI, "_gbutils_di_prima.py")
with open(temporaneo, "wb") as f:
	f.write(sorgente)
spec = importlib.util.spec_from_file_location("_gbutils_di_prima", temporaneo)
prima = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prima)
diversi = []
for l, s, p in PESI:
	for msg in MESSAGGI:
		for wpm in (12, 25, 60):
			vecchio, rv = prima.CWzator(msg=msg, wpm=wpm, l=l, s=s, p=p, play=False)
			nuovo, rn = genera(msg=msg, wpm=wpm, l=l, s=s, p=p)
			if not np.array_equal(vecchio.audio_data, nuovo.audio_data) or abs(rv - rn) > 1e-9:
				diversi.append(f"{msg!r} {wpm} wpm pesi {l} {s} {p}")
prova(f"senza farnsworth nulla cambia, su {len(PESI) * len(MESSAGGI) * 3} combinazioni",
	  not diversi, f"{len(diversi)} diverse, la prima {diversi[0] if diversi else ''}")
with contextlib.suppress(OSError):
	os.remove(temporaneo)

# 2. Il conto e' esatto: la parola campione dura quello che deve, con ogni peso.
#    "paris paris" meno "paris" lascia esattamente una PARIS con il suo spazio
#    finale, cioe' cinquanta unita', che alla velocita' effettiva X devono
#    durare 1,2 per cinquanta diviso X. E' la definizione, misurata sui
#    campioni davvero generati e non ricalcolata a parte.
peggiore, dove, quante, rifiutate = 0.0, "", 0, 0
for l, s, p in PESI:
	for wpm in (10, 18, 25, 40, 80, 120):
		for effettiva in (5, 8, 12, 18, 25, 40):
			if effettiva > wpm:
				continue
			una, _ = genera(msg="paris", wpm=wpm, l=l, s=s, p=p, farnsworth=effettiva, ms=0)
			due, _ = genera(msg="paris paris", wpm=wpm, l=l, s=s, p=p, farnsworth=effettiva, ms=0)
			if una is None:
				rifiutate += 1
				continue
			quante += 1
			misurata = durata(due) - durata(una)
			attesa = 1.2 * 50.0 / effettiva
			errore = abs(misurata - attesa) / attesa
			if errore > peggiore:
				peggiore, dove = errore, f"{wpm}/{effettiva} pesi {l} {s} {p}: {misurata:.5f} contro {attesa:.5f} s"
prova(f"la parola campione dura il dovuto, su {quante} combinazioni",
	  peggiore < 0.001, f"scarto massimo {peggiore * 100:.4f} per cento in {dove}")
print(f"  scarto massimo {peggiore * 100:.4f} per cento, cioe' la quantizzazione in campioni")
print(f"  respinte {rifiutate} combinazioni in cui i pesi non arrivano alla velocita' chiesta")

# 3. A pesi standard le spaziature coincidono con la formula ARRL.
#    ARRL: il tempo totale delle spaziature in una PARIS vale
#    ta = 60/effettiva - 37,2/caratteri secondi, diviso in diciannove quote,
#    tre per ogni spazio fra lettere e sette per quello fra parole.
#    Fonte: morsecode.world/international/timing/farnsworth.html
scarti = []
for wpm in (13, 18, 20, 25, 35):
	for effettiva in (5, 8, 10, 13, 15):
		if effettiva > wpm:
			continue
		handle, _ = genera(msg="paris x", wpm=wpm, farnsworth=effettiva, ms=0)
		# "paris x" ha quattro spazi fra lettere dentro paris e uno fra parole.
		durate = sorted(silenzi(handle.audio_data))
		ta = 60.0 / effettiva - 37.2 / wpm
		scarti.append(max(abs(durate[-2] - 3.0 * ta / 19.0) / (3.0 * ta / 19.0),
						  abs(durate[-1] - 7.0 * ta / 19.0) / (7.0 * ta / 19.0)))
prova(f"a pesi standard coincide con ARRL su {len(scarti)} coppie di velocita'",
	  max(scarti) < 0.002, f"scarto massimo {max(scarti) * 100:.3f} per cento")
print(f"  scarto massimo dalla formula ARRL {max(scarti) * 100:.3f} per cento")

# 4. Le spaziature non dipendono dal messaggio: e' il punto del metodo.
#    Chi impara deve sentire sempre la stessa distanza fra le lettere,
#    qualunque cosa gli si mandi.
for l, s, p in PESI:
	larghi = []
	for msg in ("paris x", "e e e e e", "0 0", "cq cq de iz4apu", "the quick brown fox"):
		handle, _ = genera(msg=msg, wpm=25, l=l, s=s, p=p, farnsworth=10, ms=0)
		larghi.append(max(silenzi(handle.audio_data)))
	if (l, s, p) == (30, 50, 50):
		print(f"  spazio fra parole a pesi standard, cinque messaggi: {min(larghi) * 1000:.0f} ms")
	prova(f"  le spaziature non cambiano col messaggio, pesi {l} {s} {p}",
		  max(larghi) - min(larghi) < 1e-3, f"da {min(larghi) * 1000:.1f} a {max(larghi) * 1000:.1f} ms")

# 5. Il carattere non cambia: campione per campione.
uguali, dettaglio = True, ""
for l, s, p in PESI:
	sola, _ = genera(msg="c", wpm=25, l=l, s=s, p=p)
	dentro, _ = genera(msg="cq de k", wpm=25, l=l, s=s, p=p, farnsworth=8)
	quanti = sola.audio_data.size - CODA
	if not np.array_equal(sola.audio_data[:quanti], dentro.audio_data[:quanti]):
		uguali, dettaglio = False, f"pesi {l} {s} {p}"
prova(f"il carattere e' identico campione per campione, su {len(PESI)} combinazioni di pesi",
	  uguali, dettaglio)

# 6. Dentro il carattere nessuna spaziatura si allarga.
identici, dettaglio = True, ""
for l, s, p in PESI:
	for effettiva in (5, 10, 15):
		senza, _ = genera(msg="paris paris", wpm=20, l=l, s=s, p=p, ms=0)
		con, _ = genera(msg="paris paris", wpm=20, l=l, s=s, p=p, ms=0, farnsworth=effettiva)
		if con is None:
			continue
		scarto = abs(min(silenzi(senza.audio_data)) - min(silenzi(con.audio_data)))
		if scarto > 1e-4:
			identici, dettaglio = False, f"pesi {l} {s} {p} a {effettiva}: {scarto * 1000:.3f} ms di differenza"
prova("lo spazio fra simboli dentro la lettera non cambia mai", identici, dettaglio)

# 7. Le spaziature restano in proporzione tre a sette.
rapporti = []
for l, s, p in PESI:
	handle, _ = genera(msg="paris x", wpm=25, l=l, s=s, p=p, ms=0, farnsworth=10)
	if handle is None:
		continue
	durate = sorted(silenzi(handle.audio_data))
	rapporti.append(durate[-1] / durate[-2])
prova("lo spazio fra parole resta sette terzi di quello fra lettere",
	  all(abs(r - 7.0 / 3.0) < 0.01 for r in rapporti),
	  f"rapporti da {min(rapporti):.4f} a {max(rapporti):.4f}")

# 8. Gli errori.
casi = [
	({"farnsworth": 30, "wpm": 25}, "piu' veloce dei caratteri"),
	({"farnsworth": 3, "wpm": 25}, "sotto il minimo"),
	({"farnsworth": 130, "wpm": 120}, "sopra il massimo"),
	({"farnsworth": "otto", "wpm": 25}, "tipo non valido"),
	({"farnsworth": True, "wpm": 25}, "un booleano non e' un numero"),
	({"farnsworth": 20, "wpm": 25, "l": 60, "s": 100, "p": 100}, "i pesi non ci arrivano"),
]
for kw, nota in casi:
	handle, rwpm = genera(msg="paris", **kw)
	prova(f"errore respinto, {nota}", (handle, rwpm) == (None, None), f"tornato {handle}")
	prova(f"  e il motivo e' scritto, {nota}", bool(CWzator.ultimo_errore), CWzator.ultimo_errore)
print(f"  esempio di messaggio: {CWzator.ultimo_errore}")

# 9. I casi di confine.
solo_senza, r_senza = genera(msg="e", wpm=25)
solo_con, r_con = genera(msg="e", wpm=25, farnsworth=5)
prova("un carattere solo con farnsworth non e' un errore", solo_con is not None)
prova("un carattere solo non cambia di un campione",
	  np.array_equal(solo_senza.audio_data, solo_con.audio_data))
prova("e la velocita' effettiva annunciata e' quella impostata", abs(r_con - 5) / 5 < 0.001, r_con)
prova("mentre quella del testo resta quella dei caratteri",
	  abs(solo_con.wpm_del_messaggio - r_senza) / r_senza < 0.001,
	  f"{solo_con.wpm_del_messaggio:.4f} contro {r_senza}")
pari_senza, _ = genera(msg="cq de iz4apu", wpm=20)
pari_con, rp = genera(msg="cq de iz4apu", wpm=20, farnsworth=20)
prova("farnsworth uguale a wpm e' ammesso", pari_con is not None)
prova("e a pesi standard non allarga niente",
	  np.array_equal(pari_senza.audio_data, pari_con.audio_data))
prova("e la velocita' resta quella", abs(rp - 20) < 0.05, rp)

# 10. Convive con gli altri parametri.
con_pausa, _ = genera(msg="paris _ paris", wpm=25, farnsworth=10, pausa=800)
senza_pausa, _ = genera(msg="paris paris", wpm=25, farnsworth=10)
delta = (con_pausa.audio_data.size - senza_pausa.audio_data.size) / FS
prova("la pausa in millesimi si somma", abs(delta - 0.8) < 0.02, f"{delta:.3f} s")
r_con_pausa = genera(msg="paris _ paris", wpm=25, farnsworth=10, pausa=800)[1]
r_senza_pausa = genera(msg="paris paris", wpm=25, farnsworth=10)[1]
prova("e non tocca la velocita' annunciata", abs(r_con_pausa - r_senza_pausa) < 1e-9,
	  f"{r_con_pausa:.4f} contro {r_senza_pausa:.4f}")
for modo in ("fisso", "proporzionale", "compensato"):
	una, _ = genera(msg="paris", wpm=25, farnsworth=10, fade_mode=modo, ms=2)
	due, _ = genera(msg="paris paris", wpm=25, farnsworth=10, fade_mode=modo, ms=2)
	misurata = durata(due) - durata(una)
	prova(f"la parola campione dura il dovuto con dissolvenza {modo}",
		  abs(misurata - 6.0) / 6.0 < 0.005, f"{misurata:.4f} contro 6.0000 s")
for forma in (1, 2, 3, 4):
	una, _ = genera(msg="paris", wpm=20, farnsworth=9, wv=forma)
	due, _ = genera(msg="paris paris", wpm=20, farnsworth=9, wv=forma)
	misurata = durata(due) - durata(una)
	prova(f"la parola campione dura il dovuto con l'onda {forma}",
		  abs(misurata - 60.0 / 9.0) / (60.0 / 9.0) < 0.002, f"{misurata:.4f} s")
mappa = CWzator(get_map=True, farnsworth=5)
prova("get_map risponde lo stesso", isinstance(mappa, dict) and mappa["a"] == ".-")
with tempfile.TemporaryDirectory() as cartella:
	salvato, _ = genera(msg="cq de k", wpm=25, farnsworth=10, to_file=True,
						wave_output_path_file=os.path.join(cartella, "prova.wav"))
	prova("il file wav si salva lo stesso",
		  salvato.file_salvato is not None and os.path.getsize(salvato.file_salvato) > 1000)

# 11. Il PlaybackHandle porta tutte le velocita'.
handle, rwpm = genera(msg="cq de iz4apu k", wpm=18, farnsworth=5)
prova("il handle porta la velocita' dei caratteri", handle.wpm_caratteri == 18, handle.wpm_caratteri)
prova("il handle porta la velocita' effettiva", abs(handle.wpm_effettiva - rwpm) < 1e-9)
prova("il handle porta il farnsworth chiesto", handle.farnsworth == 5, handle.farnsworth)
prova("il handle porta anche la velocita' di quel testo",
	  handle.wpm_del_messaggio is not None and handle.wpm_del_messaggio != rwpm,
	  handle.wpm_del_messaggio)
senza_f, r_senza_f = genera(msg="cq de iz4apu k", wpm=18)
prova("senza farnsworth il campo resta vuoto", senza_f.farnsworth is None, senza_f.farnsworth)
prova("e senza farnsworth le due velocita' coincidono",
	  abs(senza_f.wpm_del_messaggio - r_senza_f) < 1e-9)

# 11 bis. La velocita' restituita e' l'effettiva, e non dipende dal testo.
peggiore, dove, quante = 0.0, "", 0
for l, s, p in PESI:
	for wpm in (18, 25, 40, 80):
		for effettiva in (5, 8, 12, 18):
			if effettiva > wpm:
				continue
			letti = []
			for msg in MESSAGGI:
				handle, rwpm = genera(msg=msg, wpm=wpm, l=l, s=s, p=p, farnsworth=effettiva)
				if handle is None:
					break
				letti.append(rwpm)
			if len(letti) < len(MESSAGGI):
				continue
			quante += 1
			errore = max(abs(r - effettiva) / effettiva for r in letti)
			if errore > peggiore:
				peggiore, dove = errore, f"{wpm}/{effettiva} pesi {l} {s} {p}: da {min(letti):.4f} a {max(letti):.4f}"
prova(f"la velocita' restituita e' l'effettiva su qualunque testo, {quante} impostazioni per {len(MESSAGGI)} messaggi",
	  peggiore < 0.001, f"scarto massimo {peggiore * 100:.4f} per cento in {dove}")
print(f"  scarto massimo dal valore impostato {peggiore * 100:.4f} per cento")

# 12. L'identita' interna: la velocita' del testo e' 1,2 per le unita' diviso
#     la durata, con e senza Farnsworth, ed e' la definizione che la docstring
#     promette. Senza Farnsworth e' anche quella restituita. Le unita' si
#     contano qui da capo, con le stesse regole.
peggiore, dove, scostamento = 0.0, "", 0.0
for l, s, p in PESI:
	for msg in MESSAGGI:
		for effettiva in (None, 5, 10):
			handle, rwpm = genera(msg=msg, wpm=25, l=l, s=s, p=p, farnsworth=effettiva)
			if handle is None:
				continue
			unita = conta(msg)[5]
			if unita == 0:
				continue
			atteso = 1.2 * unita / durata(handle)
			errore = abs(handle.wpm_del_messaggio - atteso) / atteso
			if errore > peggiore:
				peggiore, dove = errore, f"{msg!r} pesi {l} {s} {p} farnsworth {effettiva}: {handle.wpm_del_messaggio:.4f} contro {atteso:.4f}"
			if effettiva is None:
				scostamento = max(scostamento, abs(rwpm - handle.wpm_del_messaggio))
prova("la velocita' del testo e' sempre 1,2 per le unita' diviso la durata prodotta",
	  peggiore < 0.001, f"scarto massimo {peggiore * 100:.4f} per cento in {dove}")
prova("e senza Farnsworth e' anche quella restituita", scostamento < 1e-9, scostamento)

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
