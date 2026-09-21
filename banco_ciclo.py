"""Banco di prova del suono in ciclo di Acusticator, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' auto).
Nato con la V165 e la issue 40, il 20 settembre 2026.
Il banco non apre la scheda audio: al posto del mixer condiviso mette un
mixer vero che scrive in un array invece che nelle casse, cosi' si possono
contare i campioni che sarebbero usciti. E' l'unico modo di misurare un fondo
continuo senza farlo sentire e senza dipendere dalla scheda di chi prova.
Le domande a cui il banco risponde sono cinque.
La prima e' se il ciclo sia davvero senza buchi: fra la fine di un giro e
l'inizio del seguente non deve restare un solo campione di silenzio, e i
campioni devono ripetersi esattamente con il periodo del buffer.
La seconda e' se il ciclo non finisca da solo: dopo molti giri deve essere
ancora li'.
La terza e' se stop fermi quello e soltanto quello: un altro suono che stava
suonando insieme deve proseguire.
La quarta e' se il ciclo non disturbi le voci normali, che devono finire
quando finiscono come hanno sempre fatto.
La quinta e' se la maniglia sia onesta: attivo dice la verita', e fermare due
volte non e' un errore.
Si lancia con
  python banco_ciclo.py
e stampa in fondo quante prove sono passate.
"""

import sys

import numpy as np

import GBUtils

totale = passate = 0


def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")


class MixerDiCarta(GBUtils._MixerCondiviso):
	"""Il mixer vero, che invece di scrivere nelle casse scrive in una lista.

	Si eredita da quello vero perche' e' il suo _prepara_blocco che si vuole
	collaudare: qui si salta soltanto l'apertura della scheda.
	"""

	def __init__(self):
		super().__init__()
		self._canali = 2
		self._fs = 44100
		self.uscita = []

	def _assicura_stream(self):
		return True

	def gira(self, blocchi):
		"""Fa girare il mixer per tanti blocchi e raccoglie cio' che uscirebbe."""
		for _ in range(blocchi):
			blocco = self._prepara_blocco()
			self.uscita.append(np.zeros((self._blocco, 2), dtype=np.float32) if blocco is None else blocco.copy())

	def suonato(self):
		return np.concatenate(self.uscita) if self.uscita else np.zeros((0, 2), dtype=np.float32)


mixer = MixerDiCarta()
BLOCCO = mixer._blocco
# Un buffer che non e' multiplo del blocco, proprio per mettere alla prova
# l'avvolgimento: se il ciclo funzionasse solo con i multipli non servirebbe.
PERIODO = BLOCCO * 3 + 137
# Una rampa che non tocca mai lo zero: cosi' un campione muto e' un buco
# del ciclo e non un campione del segnale.
onda = 0.25 + 0.5 * np.arange(PERIODO, dtype=np.float32) / PERIODO
buffer = np.stack([onda, onda], axis=1).astype(np.float32)

voce = mixer.suona(buffer, fs=44100, ciclo=True)
prova("il mixer accetta una voce in ciclo", voce is not None)
mixer.gira(20)
suonato = mixer.suonato()
prova("dopo venti blocchi il ciclo suona ancora", voce in mixer._voci)
muti = int(np.count_nonzero(np.abs(suonato).max(axis=1) == 0))
prova("non resta un solo campione muto fra un giro e il seguente", muti == 0, f"{muti} campioni muti")
# Il segnale deve ripetersi con il periodo del buffer, campione per campione.
quanti = suonato.shape[0] - PERIODO
scarto = np.abs(suonato[:quanti, 0] - suonato[PERIODO:PERIODO + quanti, 0]).max()
prova("il segnale si ripete esattamente con il periodo del buffer", scarto < 1e-6, f"scarto massimo {scarto}")

# Un suono normale che suona insieme, e che stop non deve toccare.
breve = np.ones((BLOCCO * 2, 2), dtype=np.float32) * 0.5
altra = mixer.suona(breve, fs=44100)
prova("una voce normale entra insieme al ciclo", altra is not None)
maniglia = GBUtils._CicloAcceso(mixer, voce)
prova("la maniglia dice che il ciclo e' attivo", maniglia.attivo)
prova("stop ferma il ciclo", maniglia.stop() is True)
mixer.gira(1)
prova("e il ciclo e' finito", not maniglia.attivo)
prova("mentre l'altra voce prosegue", altra in mixer._voci)
prova("fermare due volte non e' un errore", maniglia.stop() is False)

# La voce normale finisce quando finisce, come ha sempre fatto.
mixer.gira(3)
prova("la voce normale finisce da sola", altra not in mixer._voci)
prova("e nessuna voce resta appesa", mixer._voci == [], mixer._voci)

# La sintesi pubblica, che serve a preparare il fondo una volta sola.
fondo = GBUtils.Acusticator.sintetizza(["200-2000", 0.5, 0.0, 1.0], kind=6, fs=44100)
prova("sintetizza restituisce un buffer stereo", fondo is not None and fondo.ndim == 2 and fondo.shape[1] == 2,
	  None if fondo is None else fondo.shape)
prova("lungo quanto lo score chiede", fondo is not None and abs(fondo.shape[0] - 22050) < 100, None if fondo is None else fondo.shape[0])
prova("uno score vuoto non produce niente", GBUtils.Acusticator.sintetizza([]) is None)

# La cucitura del ciclo. Gabriele, provando il fondo di QRN del contest, ha
# sentito un colpetto ogni dieci secondi, cioe' a ogni giro del buffer. Non e'
# uno scalino: il salto di ampiezza alla cucitura e' zero, perche' i due capi
# del buffer partono e finiscono da zero. E' un avvallamento, e su una sola
# sintesi la varianza del rumore rosa lo nasconde del tutto: si misura su
# molte, e li' i numeri parlano chiaro.
def livello_alla_cucitura(giro, finestra):
	"""Il livello nella finestra a cavallo della cucitura, diviso quello del corpo."""
	doppio = np.concatenate([giro, giro])[:, 0]
	centro = len(giro)
	attorno = doppio[centro - finestra // 2 : centro + finestra // 2]
	return float(np.sqrt((attorno**2).mean()) / np.sqrt((giro[:, 0] ** 2).mean()))


FS = 44100
DISSOLVENZA = int(0.05 * FS)
FINESTRA = int(0.005 * FS)
senza, con, rapporti = [], [], []
for _ in range(16):
	rumore = GBUtils.Acusticator.sintetizza(["300-800", 2.0, 0.0, 0.5], kind=6, adsr=[0, 0, 100, 0], fs=FS)
	prima = livello_alla_cucitura(rumore, FINESTRA)
	dopo = livello_alla_cucitura(GBUtils._incrocia_ciclo(rumore, DISSOLVENZA), FINESTRA)
	senza.append(prima)
	con.append(dopo)
	rapporti.append(dopo / prima)
media_senza, media_con = float(np.mean(senza)), float(np.mean(con))
# Il rapporto si misura sulla stessa sintesi: le due misure vedono lo stesso
# rumore, quindi la varianza si semplifica e la prova non dipende dal giro.
guadagno = float(np.median(rapporti))
prova("l'incrocio alza il livello alla cucitura di almeno meta'",
	  guadagno > 1.5, f"da {media_senza:.3f} a {media_con:.3f}, rapporto mediano {guadagno:.2f}")
prova("senza incrocio la cucitura e' un avvallamento",
	  media_senza < 0.7, f"livello {media_senza:.3f} del corpo")
prova("con l'incrocio la cucitura non si sente piu'",
	  media_con > 0.75, f"livello {media_con:.3f} del corpo")
rumore = GBUtils.Acusticator.sintetizza(["300-800", 2.0, 0.0, 0.5], kind=6, adsr=[0, 0, 100, 0], fs=FS)
incrociato = GBUtils._incrocia_ciclo(rumore, DISSOLVENZA)
prova("il giro e' piu' corto di tre dissolvenze",
	  len(incrociato) == len(rumore) - 3 * DISSOLVENZA, f"{len(rumore)} diventano {len(incrociato)}")
prova("con dissolvenza zero il buffer non si tocca", GBUtils._incrocia_ciclo(rumore, 0) is rumore)
corto = rumore[: 2 * DISSOLVENZA]
prova("un buffer troppo corto per l'incrocio resta com'e'", len(GBUtils._incrocia_ciclo(corto, DISSOLVENZA)) == len(corto))
# E la strada per chi il buffer se lo prepara da se', con i due canali diversi.
sinistra = rumore[:, 0]
destra = GBUtils.Acusticator.sintetizza(["300-800", 2.0, 0.0, 0.5], kind=6, adsr=[0, 0, 100, 0], fs=FS)[:, 0]
largo = np.stack([sinistra, destra], axis=1).astype(np.float32)
prova("i due canali di due sintesi diverse sono scorrelati",
	  abs(float(np.corrcoef(sinistra, destra)[0, 1])) < 0.1)

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
