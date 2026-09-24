"""Banco di prova del limitatore del mixer, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).
Nato con la V168 e la issue 41, il 24 settembre 2026.
Come banco_ciclo, non apre la scheda audio: al posto del mixer condiviso mette
il mixer vero che scrive in un array invece che nelle casse, e accanto a lui
il mixer di ieri, identico ma senza limitatore, che taglia netto come faceva
fino alla V167. Si suonano le stesse voci nei due e si confronta cio' che
sarebbe uscito.
Le domande a cui il banco risponde sono quattro.
La prima e' se il limitatore sia trasparente finche' non serve: una voce sola,
o piu' voci che insieme stanno dentro il fondo scala, devono uscire identiche
a ieri campione per campione.
La seconda e' se faccia il suo mestiere sul pile-up della issue, cinque
stazioni CW da un lato: nessun campione deve arrivare alla rete di sicurezza,
e la sporcizia sopra i duemila hertz, dove i toni non ne hanno, deve restare
quella della somma ideale invece di salire come con il taglio.
La terza e' se rispetti i suoi tempi: la tenuta nei silenzi brevi, la
risalita dopo, il ritorno a uno anche quando nel frattempo non suona niente.
La quarta e' se non sposti lo stereo e non costi troppo.
Si lancia con
  python banco_limitatore.py
e stampa in fondo quante prove sono passate.
"""

import math
import sys
import time
from itertools import pairwise

import numpy as np

import GBUtils

totale = passate = 0
FS = 44100


def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok {visto}".rstrip())
	else:
		print(f"{titolo}: FALLITA {visto}")


class MixerDiCarta(GBUtils._MixerCondiviso):
	"""Il mixer vero, che invece di scrivere nelle casse scrive in una lista.

	Tiene anche due registri per blocco: il guadagno con cui il blocco e'
	uscito e il suo picco prima della rete di sicurezza, cioe' cio' che il
	taglio netto avrebbe trovato da tagliare.
	"""

	def __init__(self):
		super().__init__()
		self._canali = 2
		self._fs = FS
		self.uscita = []
		self.guadagni = []
		self.picchi = []

	def _assicura_stream(self):
		return True

	def _limita(self, somma):
		super()._limita(somma)
		self.picchi.append(float(np.max(np.abs(somma))))

	def gira(self, blocchi):
		"""Fa girare il mixer per tanti blocchi e raccoglie cio' che uscirebbe."""
		for _ in range(blocchi):
			registrati = len(self.picchi)
			blocco = self._prepara_blocco()
			# Un blocco di silenzio non passa da _limita: gli si segna un
			# picco nullo, cosi' i registri restano allineati ai blocchi.
			if len(self.picchi) == registrati:
				self.picchi.append(0.0)
			self.uscita.append(np.zeros((self._blocco, 2), dtype=np.float32) if blocco is None else blocco.copy())
			self.guadagni.append(self._guadagno)

	def suonato(self):
		return np.concatenate(self.uscita) if self.uscita else np.zeros((0, 2), dtype=np.float32)


class MixerDiIeri(MixerDiCarta):
	"""Lo stesso mixer senza limitatore: somma e taglia netto, come fino alla V167."""

	def _limita(self, somma):
		self.picchi.append(float(np.max(np.abs(somma))))

	def _nuovo_guadagno(self, picco, quanti):
		return 1.0, False


BLOCCO = MixerDiCarta()._blocco


def cw(messaggio, tono, volume):
	"""Un messaggio CW come arriva al mixer: CWzator lo fa in sedici bit, il mixer lo vuole fra meno uno e uno."""
	maniglia, _ = GBUtils.CWzator(messaggio, wpm=28, pitch=tono, vol=volume, play=False)
	return maniglia.audio_data.astype(np.float32) / 32768.0


def suona_in(mixer, programma, coda):
	"""Suona un programma di voci, ognuna al suo blocco di partenza, poi lascia girare la coda.

	programma: lista di (blocco di partenza, buffer, pan), in ordine di partenza.
	coda: quanti blocchi far girare dopo l'ultima partenza.
	"""
	adesso = 0
	for partenza, buffer, pan in programma:
		if partenza > adesso:
			mixer.gira(partenza - adesso)
			adesso = partenza
		mixer.suona(buffer, fs=FS, pan=pan)
	mixer.gira(coda)


def ideale(programma, blocchi):
	"""La somma senza ne' limitatore ne' taglio, fatta con la stessa panoramica del mixer."""
	somma = np.zeros((blocchi * BLOCCO, 2), dtype=np.float32)
	for partenza, buffer, pan in programma:
		angolo = (max(-1.0, min(1.0, float(pan))) + 1.0) * math.pi / 4.0
		inizio = partenza * BLOCCO
		fine = min(len(somma), inizio + len(buffer))
		somma[inizio:fine, 0] += buffer[:fine - inizio] * math.cos(angolo)
		somma[inizio:fine, 1] += buffer[:fine - inizio] * math.sin(angolo)
	return somma


def sopra_2000(segnale):
	"""L'energia sopra i duemila hertz, in decibel sotto il totale: dove i toni del pile-up non ne hanno."""
	mono = segnale.mean(axis=1)
	spettro = np.abs(np.fft.rfft(mono * np.hanning(len(mono)))) ** 2
	frequenze = np.fft.rfftfreq(len(mono), 1 / FS)
	return 10 * math.log10(spettro[frequenze > 2000].sum() / spettro.sum())


def in_decibel(guadagno):
	return 20 * math.log10(max(guadagno, 1e-9))


print(f"tempi del limitatore: attacco {GBUtils._MixerCondiviso.ATTACCO * 1000:.1f} millesimi, tenuta {GBUtils._MixerCondiviso.TENUTA:.2f} secondi, risalita {GBUtils._MixerCondiviso.RILASCIO:.2f} secondi, soglia di tenuta {GBUtils._MixerCondiviso.SOGLIA_TENUTA}\n")

# Prima domanda: trasparente finche' non serve.
voce_forte = cw("cq test iz4apu", 600, 0.85)
programma = [(0, voce_forte, -1.0)]
oggi, ieri = MixerDiCarta(), MixerDiIeri()
blocchi = len(voce_forte) // BLOCCO + 4
suona_in(oggi, programma, blocchi)
suona_in(ieri, programma, blocchi)
prova("una voce sola forte esce identica a ieri, campione per campione", np.array_equal(oggi.suonato(), ieri.suonato()))
prova("e il guadagno resta a uno per tutto il tempo", all(g == 1.0 for g in oggi.guadagni))

tenui = [(0, cw("k1abc k1abc", 500, 0.3), -1.0), (3, cw("dl5xyz dl5xyz", 650, 0.3), -1.0), (6, cw("ja1qrp ja1qrp", 780, 0.3), -1.0)]
blocchi = max(p * BLOCCO + len(b) for p, b, _ in tenui) // BLOCCO + 4
oggi, ieri = MixerDiCarta(), MixerDiIeri()
suona_in(oggi, tenui, blocchi)
suona_in(ieri, tenui, blocchi)
prova("tre voci che insieme stanno dentro il fondo scala escono identiche", np.array_equal(oggi.suonato(), ieri.suonato()),
	f"(picco {max(ieri.picchi):.2f})")

due = [(0, cw("k1abc k1abc k1abc", 500, 0.85), -1.0), (2, cw("dl5xyz dl5xyz dl5xyz", 650, 0.7), -1.0)]
blocchi = max(p * BLOCCO + len(b) for p, b, _ in due) // BLOCCO + 4
oggi, ieri = MixerDiCarta(), MixerDiIeri()
oggi._volume = ieri._volume = 0.5
suona_in(oggi, due, blocchi)
suona_in(ieri, due, blocchi)
prova("con il volume generale a meta' due voci forti che dentro ci stanno non vengono toccate",
	np.array_equal(oggi.suonato(), ieri.suonato()), f"(picco {max(ieri.picchi):.2f})")

# Seconda domanda: il pile-up della issue, cinque stazioni tutte da un lato.
PILE_UP = [
	(0, cw("iz4apu iz4apu iz4apu 5nn 001", 450, 0.85), -1.0),
	(11, cw("k1abc k1abc k1abc 5nn 002", 540, 0.70), -1.0),
	(22, cw("dl5xyz dl5xyz dl5xyz 5nn 003", 620, 0.60), -1.0),
	(32, cw("ja1qrp ja1qrp ja1qrp 5nn 004", 710, 0.45), -1.0),
	(43, cw("vk2def vk2def vk2def 5nn 005", 830, 0.35), -1.0),
]
fine_pile_up = max(p * BLOCCO + len(b) for p, b, _ in PILE_UP) // BLOCCO + 1
coda = fine_pile_up - PILE_UP[-1][0] + int(4 * FS / BLOCCO)
blocchi = PILE_UP[-1][0] + coda
oggi, ieri = MixerDiCarta(), MixerDiIeri()
suona_in(oggi, PILE_UP, coda)
suona_in(ieri, PILE_UP, coda)
somma = ideale(PILE_UP, blocchi)
uscita_oggi, uscita_ieri = oggi.suonato(), ieri.suonato()
picco_ideale = float(np.max(np.abs(somma)))
tagliati_ieri = np.count_nonzero(np.abs(somma[:, 0]) > 1.0) / len(somma) * 100
prova("ieri il taglio lavorava davvero", tagliati_ieri > 5, f"(picco della somma {picco_ideale:.2f}, campioni tagliati {tagliati_ieri:.1f} per cento)")
oltre = sum(1 for p in oggi.picchi if p > 1.0 + 1e-6)
prova("oggi nessun blocco arriva alla rete di sicurezza", oltre == 0, f"(blocchi oltre il fondo scala {oltre}, picco piu' alto {max(oggi.picchi):.4f})")
sporco_ideale, sporco_oggi, sporco_ieri = sopra_2000(somma), sopra_2000(uscita_oggi), sopra_2000(uscita_ieri)
prova("la sporcizia sopra i 2000 hertz resta quella della somma ideale, entro un decibel", abs(sporco_oggi - sporco_ideale) < 1.0,
	f"(ideale {sporco_ideale:.1f} dB, oggi {sporco_oggi:.1f})")
prova("mentre con il taglio saliva di almeno quindici decibel", sporco_ieri - sporco_ideale > 15, f"(ieri {sporco_ieri:.1f} dB)")
minimo = min(oggi.guadagni)
prova("il guadagno scende quanto serve e non di piu'", abs(in_decibel(minimo) + in_decibel(picco_ideale)) < 0.2,
	f"(minimo {in_decibel(minimo):.1f} dB, il picco chiedeva {-in_decibel(picco_ideale):.1f})")

# Terza domanda: i tempi. Dopo il pile-up il mixer ha girato quattro secondi,
# gli ultimi a vuoto, cioe' senza voci: il guadagno deve essere tornato a uno.
prova("dopo il pile-up e il silenzio il guadagno e' tornato a uno", oggi._guadagno == 1.0, f"(guadagno {oggi._guadagno})")
ultimo_giu = max(i for i, g in enumerate(oggi.guadagni) if g < 1.0)
ultimo_forte = max(i for i, p in enumerate(ieri.picchi) if p > 1.0) if max(ieri.picchi) > 1.0 else 0
risalita = (ultimo_giu - ultimo_forte) * BLOCCO / FS
prova("e ci e' tornato in un paio di secondi dall'ultimo blocco forte", 1.0 < risalita < 3.5, f"({risalita:.2f} secondi)")
salendo = oggi.guadagni[ultimo_forte + 1:]
prova("salendo non torna mai indietro e non supera uno", all(b >= a for a, b in pairwise(salendo)) and max(salendo) <= 1.0)

# Il primo suono dopo una pausa non deve partire abbassato: il silenzio fa
# passare il tempo del limitatore come ogni altro blocco.
oggi, ieri = MixerDiCarta(), MixerDiIeri()
forte = [(0, cw("k1abc k1abc", 500, 0.85), -1.0), (1, cw("dl5xyz dl5xyz", 650, 0.85), -1.0)]
blocchi = max(p * BLOCCO + len(b) for p, b, _ in forte) // BLOCCO + 1
suona_in(oggi, forte, blocchi)
giu = min(oggi.guadagni)
oggi.gira(int(3 * FS / BLOCCO))
inizio = len(oggi.uscita)
oggi.suona(voce_forte, fs=FS, pan=-1.0)
oggi.gira(len(voce_forte) // BLOCCO + 2)
ieri.suona(voce_forte, fs=FS, pan=-1.0)
ieri.gira(len(voce_forte) // BLOCCO + 2)
dopo_la_pausa = np.concatenate(oggi.uscita[inizio:])
prova("dopo tre secondi di silenzio il suono seguente parte pieno, identico a ieri", giu < 1.0 and np.array_equal(dopo_la_pausa, ieri.suonato()),
	f"(il pile-up aveva lasciato il guadagno a {in_decibel(giu):.1f} dB)")

# La tenuta: un colpo forte, poi un silenzio piu' corto della tenuta, e il
# guadagno non si muove; passata la tenuta, risale.
oggi = MixerDiCarta()
colpo = np.full((BLOCCO * 4, 1), 0.5, dtype=np.float32) * np.sin(2 * np.pi * 600 * np.arange(BLOCCO * 4) / FS).reshape(-1, 1).astype(np.float32)
oggi.suona(colpo * 3.0, fs=FS, pan=-1.0)
oggi.gira(4)
dopo_il_colpo = oggi._guadagno
quanti_tenuta = int(GBUtils._MixerCondiviso.TENUTA * FS / BLOCCO)
oggi.gira(quanti_tenuta - 1)
prova("nei silenzi piu' corti della tenuta il guadagno resta fermo", dopo_il_colpo < 1.0 and oggi._guadagno == dopo_il_colpo,
	f"({in_decibel(dopo_il_colpo):.1f} dB dopo il colpo, {in_decibel(oggi._guadagno):.1f} dopo {quanti_tenuta - 1} blocchi)")
oggi.gira(4)
prova("passata la tenuta comincia a risalire", oggi._guadagno > dopo_il_colpo, f"({in_decibel(oggi._guadagno):.1f} dB)")

# Quarta domanda: lo stereo e il costo.
oggi = MixerDiCarta()
stereo = [(0, cw("k1abc k1abc k1abc", 500, 0.9), -0.7), (0, cw("dl5xyz dl5xyz dl5xyz", 650, 0.8), 0.6), (2, cw("ja1qrp ja1qrp", 780, 0.8), -0.2)]
blocchi = max(p * BLOCCO + len(b) for p, b, _ in stereo) // BLOCCO + 2
suona_in(oggi, stereo, blocchi)
somma = ideale(stereo, stereo[-1][0] + blocchi)
uscita = oggi.suonato()
# Campione per campione, dove tutti e due i canali hanno segnale, il rapporto
# fra uscita e somma ideale deve essere lo stesso a sinistra e a destra: e'
# la definizione di un guadagno uguale sui due canali.
pieni = (np.abs(somma[:, 0]) > 0.05) & (np.abs(somma[:, 1]) > 0.05)
scarto = np.max(np.abs(uscita[pieni, 0] / somma[pieni, 0] - uscita[pieni, 1] / somma[pieni, 1]))
prova("lo stereo non si sposta: il guadagno e' lo stesso sui due canali", scarto < 1e-4 and min(oggi.guadagni) < 1.0,
	f"(scarto massimo {scarto:.1e} su {np.count_nonzero(pieni)} campioni, guadagno minimo {in_decibel(min(oggi.guadagni)):.1f} dB)")

oggi = MixerDiCarta()
rumore = np.random.default_rng(1).uniform(-1.5, 1.5, (BLOCCO, 2)).astype(np.float32)
ripetizioni = 2000
inizio = time.perf_counter()
for _ in range(ripetizioni):
	oggi._limita(rumore.copy())
costo = (time.perf_counter() - inizio) / ripetizioni * 1000
prova("il limitatore costa poco rispetto al tempo di un blocco", costo < 0.5, f"({costo:.3f} millesimi per blocco, su {BLOCCO / FS * 1000:.0f} disponibili)")

oggi = MixerDiCarta()
guasto = np.zeros((BLOCCO, 2), dtype=np.float32)
guasto[10, 0] = np.nan
oggi._limita(guasto)
prova("un blocco con un non-numero non tocca il guadagno", oggi._guadagno == 1.0)
prova("il guadagno del momento si legge in stato()", "guadagno" in GBUtils._mixer_condiviso().stato() and "guadagno" in GBUtils.Acusticator.stato())

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
