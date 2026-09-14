"""Banco di prova delle tre formattazioni di GBUtils, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto).
Nato con la V156 e la issue 9, il 14 settembre 2026.
formatta_dimensione, formatta_durata e accorcia prendono il posto delle copie
che scriba e Cartella avevano in casa, e la promessa fatta a Gabriele e' che
nessuno dei due cambi aspetto. Il banco tiene qui dentro le vecchie copie,
ricopiate parola per parola da come erano, e le confronta con le nuove su
qualche migliaio di valori: se una sola risposta differisce, la promessa e'
rotta e il banco lo dice. Poi verifica i parametri nuovi, che nessuno dei due
programmi usava, e i casi di bordo.
Non tocca niente: le funzioni restituiscono stringhe e non guardano il
sistema, quindi non c'e' nulla da sostituire.
Si lancia con
  python banco_formattazioni.py
e stampa in fondo quante prove sono passate.
"""
import sys

sys.path.insert(0, "E:/git/mine/GBUtils")
from GBUtils import accorcia, formatta_dimensione, formatta_durata

passate = 0
totale = 0

def verifica(nome, condizione, ottenuto=None):
	global passate, totale
	totale += 1
	if condizione:
		passate += 1
		return
	print(f"SBAGLIATA: {nome}" + (f" -> {ottenuto!r}" if ottenuto is not None else ""))

# Le copie che scriba aveva in casa fino alla V3.0.1, ricopiate come erano.
def scriba_dimensione(byte):
	sign = ""
	if byte < 0:
		sign = "-"
		byte = abs(byte)
	if byte == 0:
		return "0.00 B"
	for unit in ["B", "KB", "MB", "GB", "TB"]:
		if byte < 1024.0:
			return f"{sign}{byte:.2f} {unit}"
		byte /= 1024.0
	return f"{sign}{byte:.2f} PB"

def scriba_durata(seconds):
	if seconds is None or seconds <= 0:
		return "--:--"
	m, s = divmod(int(seconds), 60)
	h, m = divmod(m, 60)
	return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

def scriba_accorcia(text, max_len=45):
	if len(text) <= max_len:
		return text
	meta_lunghezza = (max_len - 3) // 2
	testa = text[:meta_lunghezza]
	coda = text[-meta_lunghezza:]
	return f"{testa}...{coda}"

lungo_di_prova = "E:/git/mine/GBUtils/documenti/una relazione molto lunga.txt"

# La copia che Cartella aveva in casa fino alla V5.0.1.
UNITA = ["byte", "KB", "MB", "GB", "TB"]

def cartella_dimensione(byte):
	valore = float(byte)
	unita = UNITA[0]
	for unita in UNITA:
		if valore < 1024 or unita == UNITA[-1]:
			break
		valore /= 1024
	if unita == UNITA[0]:
		return f"{int(valore)} byte"
	return f"{valore:.1f}".replace(".", ",") + f" {unita}"

def valori_di_prova():
	"""Le quantita' su cui confrontare vecchio e nuovo: i bordi di ogni unita',
	i dintorni dei bordi, e una manciata di numeri sparsi fino ai petabyte."""
	valori = [0, 1, 2, 3, 512, 1023]
	for potenza in range(7):
		base = 1024 ** potenza
		for scarto in (-2, -1, 0, 1, 2, 3, 999, 1000):
			valori.append(base + scarto)
		valori.append(base * 3 // 2)
		valori.append(base * 1023)
	valori.extend([1234567, 98765432109, 1.5, 0.4, 1023.9, 1024.1])
	return [v for v in valori if v >= 0]

def main():
	print("Banco delle formattazioni, issue 9")
	print()

	print("Cio' che scriba vedeva prima, e deve continuare a vedere")
	diverse = [v for v in valori_di_prova()
			   if formatta_dimensione(v) != scriba_dimensione(v)]
	verifica("la dimensione risponde come la copia di scriba, valori positivi",
			 not diverse, diverse[:5])
	diverse = [v for v in valori_di_prova()
			   if formatta_dimensione(-v) != scriba_dimensione(-v)]
	verifica("la dimensione risponde come la copia di scriba, valori negativi",
			 not diverse, diverse[:5])
	verifica("lo zero resta 0.00 B", formatta_dimensione(0) == "0.00 B", formatta_dimensione(0))
	verifica("il negativo tiene il meno davanti",
			 formatta_dimensione(-1536) == "-1.50 KB", formatta_dimensione(-1536))
	secondi = [None, -5, 0, 0.4, 1, 59, 60, 61, 599, 600, 3599, 3600, 3601,
			   86399, 86400, 90061, 123456.9]
	diverse = [s for s in secondi if formatta_durata(s) != scriba_durata(s)]
	verifica("la durata risponde come la copia di scriba", not diverse, diverse)
	testi = ["", "a", "abc", "abcd", "corto",
			 "E:/git/mine/GBUtils/un nome di file abbastanza lungo da tagliare.txt",
			 "x" * 200]
	diverse = [(t, n) for t in testi for n in range(5, 60)
			   if accorcia(t, n) != scriba_accorcia(t, n)]
	verifica("accorcia risponde come la copia di scriba da cinque caratteri in su",
			 not diverse, diverse[:3])
	# A quattro caratteri e meno la copia di scriba si rompeva: meta_lunghezza
	# veniva zero, e text[-0:] e' il testo intero, quindi tornava i puntini
	# seguiti da tutto. Non si vedeva perche' chi la chiamava tagliava
	# comunque la riga, e le chiamate erano protette da un if spazio > 2.
	verifica("a quattro caratteri la vecchia copia sforava",
			 len(scriba_accorcia(lungo_di_prova, 4)) > 4,
			 scriba_accorcia(lungo_di_prova, 4))
	verifica("la nuova no", len(accorcia(lungo_di_prova, 4)) == 4,
			 accorcia(lungo_di_prova, 4))

	print("Cio' che Cartella vedeva prima, e deve continuare a vedere")
	come_cartella = {"decimali": 1, "separatore": ",",
					 "unita": ("byte", "KB", "MB", "GB", "TB"), "byte_interi": True}
	diverse = [v for v in valori_di_prova()
			   if formatta_dimensione(v, **come_cartella) != cartella_dimensione(v)]
	verifica("la dimensione risponde come la copia di Cartella", not diverse, diverse[:5])
	verifica("i byte restano interi",
			 formatta_dimensione(980, **come_cartella) == "980 byte",
			 formatta_dimensione(980, **come_cartella))
	verifica("il megabyte prende la virgola",
			 formatta_dimensione(12902460, **come_cartella) == "12,3 MB",
			 formatta_dimensione(12902460, **come_cartella))

	print("I parametri che nessuno dei due usava")
	verifica("senza decimali", formatta_dimensione(1536, decimali=0) == "2 KB",
			 formatta_dimensione(1536, decimali=0))
	verifica("oltre l'ultima unita' non si sale",
			 formatta_dimensione(1024 ** 6, unita=("B", "KB")) == "1125899906842624.00 KB",
			 formatta_dimensione(1024 ** 6, unita=("B", "KB")))
	verifica("le unita' vuote sollevano",
			 solleva(ValueError, formatta_dimensione, 10, unita=()))
	verifica("i decimali negativi sollevano",
			 solleva(ValueError, formatta_dimensione, 10, decimali=-1))
	verifica("byte_interi non tocca il chilo",
			 formatta_dimensione(1536, byte_interi=True) == "1.50 KB",
			 formatta_dimensione(1536, byte_interi=True))
	verifica("le ore sempre, anche a zero",
			 formatta_durata(65, compatta=False) == "00:01:05",
			 formatta_durata(65, compatta=False))
	verifica("le ore non si fermano a ventiquattro",
			 formatta_durata(172800) == "48:00:00", formatta_durata(172800))
	verifica("il vuoto si sceglie",
			 formatta_durata(None, vuoto="00:00") == "00:00",
			 formatta_durata(None, vuoto="00:00"))
	verifica("i decimi si scartano",
			 formatta_durata(59.9) == "00:59", formatta_durata(59.9))
	lungo = lungo_di_prova
	verifica("accorcia dalla fine",
			 accorcia(lungo, 20, "fine") == lungo[:17] + "...",
			 accorcia(lungo, 20, "fine"))
	verifica("accorcia dall'inizio",
			 accorcia(lungo, 20, "inizio") == "..." + lungo[-17:],
			 accorcia(lungo, 20, "inizio"))
	verifica("la posizione sconosciuta solleva",
			 solleva(ValueError, accorcia, lungo, 20, "meta'"))

	print("I bordi")
	verifica("il testo che ci sta torna intatto", accorcia("corto", 20) == "corto")
	verifica("lunghezza zero da' la stringa vuota", accorcia(lungo, 0) == "")
	verifica("lunghezza negativa da' la stringa vuota", accorcia(lungo, -5) == "")
	troppo_stretti = [n for n in range(1, 6) if len(accorcia(lungo, n)) > n]
	verifica("il risultato non supera mai la lunghezza chiesta, nemmeno da 1 a 5",
			 not troppo_stretti, troppo_stretti)
	lunghi = [(n, p) for n in range(1, 120) for p in ("centro", "inizio", "fine")
			  if len(accorcia(lungo, n, p)) > n]
	verifica("e nemmeno nelle altre due posizioni", not lunghi, lunghi[:5])
	verifica("i puntini non mangiano tutto il testo",
			 accorcia(lungo, 4) == lungo[:1] + "...", accorcia(lungo, 4))
	verifica("la durata di zero e' vuota", formatta_durata(0) == "--:--")
	verifica("una durata negativa e' vuota", formatta_durata(-1) == "--:--")

	print()
	print(f"Prove {totale}, passate {passate}.")
	return 0 if passate == totale else 1

def solleva(eccezione, funzione, *argomenti, **chiavi):
	try:
		funzione(*argomenti, **chiavi)
	except eccezione:
		return True
	except Exception:  # noqa: BLE001
		return False
	return False

if __name__ == "__main__":
	sys.exit(main())
