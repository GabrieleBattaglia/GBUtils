"""Collaudo d'ascolto del tuono che distorce, issue 23.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato il 13 settembre 2026.
Questo collaudo non tocca niente: la collezione resta com'e'. Le varianti
nascono qui dentro nel momento in cui le senti e spariscono appena finite.
Cosa dice la misura. Il preset tuono_lontano e' rumore marrone con la banda
che scende da 40-900 a 40-260 hertz, cioe' quasi tutta la sua energia sta
sotto i 260. Il motore pareggia i rumori su quanto si sentono e non su quanta
energia hanno, perche' l'orecchio e' molto meno sensibile ai bassi; per far
sentire questa banda come si sente un rumore largo deve moltiplicarla per tre,
e a quel punto il limitatore comprime il quaranta per cento dei campioni. Fra
gli altri venti rumori della collezione il peggiore ne comprime il sei, e
diciassette stanno sotto l'uno.
Il tuono chiede una cosa che non si puo' avere: una banda di soli bassi forte
come un rumore largo. Il motore arriva onestamente al suo tetto, e il tetto si
sente. Qui si prova a chiedergli qualcosa di possibile.
Tutto al trenta per cento di volume.
In fondo a ogni gruppo: r riascolta il gruppo intero, c apre il posto dove
scrivere, Invio lo da' per superato, Escape lo chiude senza annotare.
Si lancia con
  python collaudo_tuono.py
"""
import os
import sys
import time

from collaudo_comune import Esiti, gruppo

from GBUtils import Acusticator, enter_escape

QUI = os.path.dirname(os.path.abspath(__file__))
VOL = 0.30
# Il preset com'e' scritto in collezione, con il volume gia' assoluto: base
# 0,5 piu' lo scarto 0,1 che il file porta.
DURATA = 1.8
PANORAMA = "0.2.-0.2"
VOLUME = 0.6
ADSR = [2.0, 0.0, 100.0, 55.0]
MARRONE, ROSA = 7, 6

esiti = Esiti(os.path.join(QUI, "collaudo_tuono_esiti.txt"),
			  "Esiti del collaudo d'ascolto del tuono che distorce, issue 23\n"
			  "Scritti da collaudo_tuono.py, che li aggiunge man mano.")

def tuono(banda, kind=MARRONE, volume=VOLUME, etichetta=""):
	print(f"  {etichetta}")
	Acusticator([banda, DURATA, PANORAMA, volume], kind=kind, adsr=ADSR, sync=True)
	time.sleep(0.7)

def main():
	print("Collaudo d'ascolto del tuono che distorce.")
	print()
	print("Niente viene modificato: la collezione resta come e'. Le varianti nascono qui dentro e")
	print("spariscono appena finite.")
	print()
	print("Il tuono comprime il quaranta per cento dei suoi campioni contro il tetto del limitatore.")
	print("Fra gli altri venti rumori della collezione il peggiore ne comprime il sei, e diciassette")
	print("stanno sotto l'uno per cento. E' quel tetto che si sente come distorsione.")
	print()
	print("In fondo a ogni gruppo: r riascolta, c commenta, Invio lo da' per superato.")
	print()
	if not enter_escape("\rInvio per cominciare, Escape per uscire\r"):
		return 0
	prima_del_collaudo = Acusticator.stato()["volume"]
	Acusticator.setup(volume=VOL)
	titolo = "la via del volume, che la issue proponeva"
	if gruppo(titolo, 3, unita="ascolti"):
		print("  La issue proponeva di abbassare lo scarto di volume del preset. Ma il volume si applica")
		print("  dopo il limitatore, quindi dovrebbe rendere il tuono piu' piano senza renderlo piu' pulito.")
		print("  Questa e' la verifica: se ho ragione, il terzo suona come il primo, solo piu' basso.")
		def ascolta_volume():
			tuono("40-900.40-260", etichetta="com'e' adesso, volume 0,6")
			tuono("40-900.40-260", volume=0.35, etichetta="stesso tuono, volume 0,35")
			tuono("40-900.40-260", volume=0.2, etichetta="stesso tuono, volume 0,2")
		ascolta_volume()
		esiti.esito(titolo, ascolta_volume,
					"  La domanda: abbassando il volume la distorsione se ne va, oppure si sente uguale piu' piano?")
	titolo = "alzare il taglio basso"
	if gruppo(titolo, 4, unita="ascolti"):
		print("  Togliendo i bassi piu' profondi il motore non deve piu' spingere tanto, e il limitatore")
		print("  lavora meno. Ma un tuono vive dei suoi bassi: il punto e' fino a dove si puo' salire")
		print("  senza che smetta di essere un tuono.")
		def ascolta_taglio():
			for taglio, quanto in ((40, "com'e' adesso, comprime il 40 per cento"),
								   (60, "comprime il 26"),
								   (100, "comprime il 15"),
								   (160, "comprime il 7, come gli altri marroni")):
				tuono(f"{taglio}-900.{taglio}-260", etichetta=f"taglio basso a {taglio} hertz, {quanto}")
		ascolta_taglio()
		esiti.esito(titolo, ascolta_taglio,
					"  La domanda: da quale taglio in poi la distorsione sparisce, e da quale in poi non e' piu' un tuono?")
	titolo = "cambiare colore al rumore"
	if gruppo(titolo, 3, unita="ascolti"):
		print("  Il marrone concentra l'energia sui bassi piu' di ogni altro colore, ed e' per questo che")
		print("  il motore deve spingerlo tanto. Il rosa scende meno ripido: stessa banda, meno energia")
		print("  accumulata in fondo, e il limitatore comprime il quindici per cento invece del quaranta.")
		def ascolta_colore():
			tuono("40-900.40-260", etichetta="marrone, com'e' adesso")
			tuono("40-900.40-260", kind=ROSA, etichetta="rosa, stessa banda")
			tuono("100-900.100-260", kind=ROSA, etichetta="rosa con il taglio a 100")
		ascolta_colore()
		esiti.esito(titolo, ascolta_colore,
					"  La domanda: il rosa e' ancora un tuono, o diventa un fruscio?")
	titolo = "un ultimo confronto, il migliore contro l'originale"
	if gruppo(titolo, 3):
		print("  Le tre candidate piu' promettenti, ognuna subito dopo l'originale, per decidere.")
		def ascolta_finale():
			for banda, kind, come in (("100-900.100-260", MARRONE, "marrone con taglio a 100"),
									  ("160-900.160-260", MARRONE, "marrone con taglio a 160"),
									  ("40-900.40-260", ROSA, "rosa con la banda di sempre")):
				tuono("40-900.40-260", etichetta="originale")
				tuono(banda, kind=kind, etichetta=come)
				print()
		ascolta_finale()
		esiti.esito(titolo, ascolta_finale,
					"  La domanda: quale delle tre tieni? Scrivilo con c, cosi' lo applico.")
	Acusticator.setup(volume=prima_del_collaudo)
	Acusticator.close()
	print("Collaudo finito. Grazie per le orecchie.")
	print("Non e' stato modificato niente: la collezione e' come prima.")
	if os.path.exists(esiti.percorso):
		print(f"Gli esiti stanno in {os.path.basename(esiti.percorso)}.")
	return 0

if __name__ == "__main__":
	sys.exit(main())
