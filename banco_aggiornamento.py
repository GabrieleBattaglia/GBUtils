"""Banco di prova di gestisci_aggiornamento, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto).
Nato con la V159 e la issue 21, il 14 settembre 2026.
La funzione conduce da sola la conversazione dell'aggiornamento, e dalla V1.2.0
sa anche tacere: quando il chiamante passa proponi, cioe' quando ha una
finestra sua, spariscono le frasi di cortesia che in un'interfaccia grafica
diventerebbero tre o quattro finestre modali a ogni avvio.
Qui non si aggiorna niente e non si tocca la rete: update_checker e
perform_update vengono sostituite da due finte che rispondono quello che serve
alla prova e segnano come sono state chiamate. Cosi' si guarda la cosa che
conta davvero, cioe' chi parla, quando, e quante volte.
La meta' delle prove verifica il silenzio: sono quelle che contano, perche' un
messaggio di troppo in una interfaccia grafica e' una finestra da chiudere.
L'altra meta' verifica che la conversazione da console sia rimasta identica a
prima, perche' sei applicazioni la usano cosi'.
Si lancia con
  python banco_aggiornamento.py
e stampa in fondo quante prove sono passate.
"""
import sys

sys.path.insert(0, "E:/git/mine/GBUtils")
import GBUtils
from GBUtils import gestisci_aggiornamento

passate = 0
totale = 0

def verifica(nome, condizione, ottenuto=None):
	global passate, totale
	totale += 1
	if condizione:
		passate += 1
		return
	print(f"SBAGLIATA: {nome}" + (f" -> {ottenuto!r}" if ottenuto is not None else ""))

NOTE = "Prima novita'.\nSeconda novita'."
API = "https://api.github.com/repos/GabrieleBattaglia/Finta/releases/latest"

class Scena:
	"""Il mondo finto in cui la funzione si muove: che cosa risponde il
	controllo, se lo scaricamento riesce, e il registro di chi ha parlato."""

	def __init__(self, esito_controllo, scaricamento=True, blocchi=()):
		self.esito_controllo = esito_controllo
		self.scaricamento = scaricamento
		self.blocchi = blocchi
		self.detti = []
		self.proposte = []
		self.avanzamenti = []
		self.avanzamento_ricevuto = "mai chiamata"
		self.scaricato = False

	def __enter__(self):
		self.vero_controllo = GBUtils.update_checker
		self.vero_scarico = GBUtils.perform_update
		GBUtils.update_checker = self.finto_controllo
		GBUtils.perform_update = self.finto_scarico
		return self

	def __exit__(self, *_guai):
		GBUtils.update_checker = self.vero_controllo
		GBUtils.perform_update = self.vero_scarico
		return False

	def finto_controllo(self, *_argomenti, **_chiavi):
		return self.esito_controllo

	def finto_scarico(self, _indirizzo, _app, avanzamento=None, **_chiavi):
		self.scaricato = True
		self.avanzamento_ricevuto = avanzamento
		for preso, quanti in self.blocchi:
			if avanzamento:
				avanzamento(preso, quanti)
		return self.scaricamento

	# Le tre porte che il chiamante puo' passare.
	def avvisa(self, testo):
		self.detti.append(testo)

	def proponi_si(self, attuale, nuova, note):
		self.proposte.append((attuale, nuova, note))
		return True

	def proponi_no(self, attuale, nuova, note):
		self.proposte.append((attuale, nuova, note))
		return False

	def avanzamento(self, preso, quanti):
		self.avanzamenti.append((preso, quanti))

# Un megabyte alla volta fino a cinque: quel che basta a far scattare gli
# annunci a percentuale, che vengono uno ogni venti.
BLOCCHI = tuple((n * 1048576, 5 * 1048576) for n in range(1, 6))
CE_NE_UNO = (True, "2.0.0", "https://esempio/App.zip", NOTE)
NIENTE_DA_FARE = (False, "1.0.0", None, None)
CONTROLLO_FALLITO = (False, None, None, None)
SENZA_PACCHETTO = (True, "2.0.0", None, NOTE)

def main():
	# 1. Da sorgente non si fa niente, ed e' il caso di tutte le prove che
	# seguono: passano solo_se_compilato=False per poter andare avanti.
	with Scena(CE_NE_UNO) as scena:
		esito = gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa)
	verifica("da sorgente: risponde di no", esito is False)
	verifica("da sorgente: non dice niente", scena.detti == [], scena.detti)

	# 2. La conversazione da console, quella di sempre: annuncio, versioni,
	# novita', domanda. Qui la domanda risponde sempre di si'.
	with Scena(CE_NE_UNO, blocchi=BLOCCHI) as scena:
		esito = gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa,
									   chiedi=lambda _t: True, solo_se_compilato=False)
	verifica("console: risponde di si'", esito is True)
	verifica("console: annuncia il controllo", scena.detti[0] == "Controllo aggiornamenti.")
	verifica("console: dice la versione nuova", "2.0.0" in scena.detti[1])
	verifica("console: dice quella attuale", "1.0.0" in scena.detti[2])
	verifica("console: mostra le novita'", NOTE in scena.detti)
	verifica("console: annuncia lo scaricamento", "Scarico l'aggiornamento." in scena.detti)
	verifica("console: gli annunci a percentuale ci sono",
			 [d for d in scena.detti if " MB su " in d] != [], scena.detti)
	verifica("console: uno ogni venti per cento",
			 [d.split("%")[0] for d in scena.detti if "%" in d] == ["20", "40", "60", "80", "100"],
			 [d for d in scena.detti if "%" in d])
	verifica("console: chiude dicendo che si chiude",
			 scena.detti[-1] == "Aggiornamento pronto, il programma si chiude per applicarlo.")

	# 3. Da console, senza niente da fare, si parla lo stesso: e' una console,
	# e chi ha lanciato il programma sta guardando.
	with Scena(NIENTE_DA_FARE) as scena:
		esito = gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa, solo_se_compilato=False)
	verifica("console: senza aggiornamenti risponde di no", esito is False)
	verifica("console: senza aggiornamenti dice due cose", len(scena.detti) == 2, scena.detti)
	verifica("console: dice che sei aggiornato", "Hai gia' l'ultima versione, 1.0.0." in scena.detti)

	# 4. Con proponi e niente da fare: silenzio assoluto, che e' la ragione per
	# cui la issue 21 esiste.
	with Scena(NIENTE_DA_FARE) as scena:
		esito = gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa,
									   proponi=scena.proponi_si, solo_se_compilato=False)
	verifica("finestra: senza aggiornamenti risponde di no", esito is False)
	verifica("finestra: senza aggiornamenti non apre niente", scena.detti == [], scena.detti)
	verifica("finestra: senza aggiornamenti non propone niente", scena.proposte == [])

	# 5. Nemmeno quando il controllo fallisce si disturba l'utente: e' un guaio
	# di rete, e finisce nel log.
	with Scena(CONTROLLO_FALLITO) as scena:
		esito = gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa,
									   proponi=scena.proponi_si, solo_se_compilato=False)
	verifica("finestra: controllo fallito, risponde di no", esito is False)
	verifica("finestra: controllo fallito, non apre niente", scena.detti == [], scena.detti)

	# 6. C'e' un aggiornamento: una proposta sola, con dentro i tre dati, e
	# nessuna finestra prima di lei.
	with Scena(CE_NE_UNO, blocchi=BLOCCHI) as scena:
		esito = gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa,
									   proponi=scena.proponi_si, solo_se_compilato=False)
	verifica("finestra: risponde di si'", esito is True)
	verifica("finestra: una proposta sola", len(scena.proposte) == 1, scena.proposte)
	verifica("finestra: la proposta porta i tre dati",
			 scena.proposte[0] == ("1.0.0", "2.0.0", NOTE), scena.proposte)
	verifica("finestra: una sola cosa detta, l'esito", len(scena.detti) == 1, scena.detti)
	verifica("finestra: l'esito e' quello giusto",
			 scena.detti[0] == "Aggiornamento pronto, il programma si chiude per applicarlo.")
	verifica("finestra: senza avanzamento lo scaricamento e' muto",
			 scena.avanzamento_ricevuto is None, scena.avanzamento_ricevuto)

	# 7. L'utente dice non adesso: si smette, senza commentare la sua scelta.
	with Scena(CE_NE_UNO) as scena:
		esito = gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa,
									   proponi=scena.proponi_no, solo_se_compilato=False)
	verifica("non adesso: risponde di no", esito is False)
	verifica("non adesso: non commenta", scena.detti == [], scena.detti)
	verifica("non adesso: non scarica niente", scena.scaricato is False)

	# 8. Lo scaricamento non riesce: questo si' che va detto, ed e' l'unica
	# cosa detta.
	with Scena(CE_NE_UNO, scaricamento=False) as scena:
		esito = gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa,
									   proponi=scena.proponi_si, solo_se_compilato=False)
	verifica("scaricamento fallito: risponde di no", esito is False)
	verifica("scaricamento fallito: lo dice una volta sola",
			 scena.detti == ["Aggiornamento non riuscito, si prosegue con questa versione."], scena.detti)

	# 9. La release c'e' ma il pacchetto non e' ancora stato caricato: si dice
	# anche a chi ha la finestra, perche' senza spiegazione l'utente resterebbe
	# con una versione vecchia e nessuna idea del perche'.
	with Scena(SENZA_PACCHETTO) as scena:
		esito = gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa,
									   proponi=scena.proponi_si, solo_se_compilato=False)
	verifica("pacchetto assente: risponde di no", esito is False)
	verifica("pacchetto assente: lo dice una volta sola", len(scena.detti) == 1, scena.detti)
	verifica("pacchetto assente: non propone niente", scena.proposte == [])

	# 10. Chi vuole seguire lo scaricamento a modo suo passa avanzamento, e le
	# percentuali a parole non si fanno vedere.
	with Scena(CE_NE_UNO, blocchi=BLOCCHI) as scena:
		gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa,
							   proponi=scena.proponi_si, avanzamento=scena.avanzamento,
							   solo_se_compilato=False)
	verifica("avanzamento: arriva tutto e in ordine", scena.avanzamenti == list(BLOCCHI), scena.avanzamenti)
	verifica("avanzamento: niente percentuali a parole",
			 [d for d in scena.detti if "%" in d] == [], scena.detti)

	# 11. Anche da console si puo' passare avanzamento: prende il posto degli
	# annunci, non si aggiunge a loro.
	with Scena(CE_NE_UNO, blocchi=BLOCCHI) as scena:
		gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa, chiedi=lambda _t: True,
							   avanzamento=scena.avanzamento, solo_se_compilato=False)
	verifica("console con avanzamento: arriva tutto", scena.avanzamenti == list(BLOCCHI))
	verifica("console con avanzamento: niente percentuali a parole",
			 [d for d in scena.detti if "%" in d] == [], scena.detti)

	# 12. traduci vale anche per le frasi che restano, e non tocca le novita'
	# della release, che sono il testo scritto da chi ha pubblicato.
	with Scena(CE_NE_UNO) as scena:
		gestisci_aggiornamento("App", "1.0.0", API, avvisa=scena.avvisa, proponi=scena.proponi_si,
							   traduci=lambda t: f"[{t}]", solo_se_compilato=False)
	verifica("traduci: l'esito passa di li'", scena.detti[0].startswith("["), scena.detti)
	verifica("traduci: le note restano quelle dell'autore", scena.proposte[0][2] == NOTE)

	print()
	print(f"Prove {totale}, passate {passate}.")
	return 0 if passate == totale else 1

if __name__ == "__main__":
	sys.exit(main())
