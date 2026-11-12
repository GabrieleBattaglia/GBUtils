import json
import math
import os
import re
import sys
import textwrap

# Aggiungo la cartella corrente al path per importare GBUtils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from GBUtils import (
    Acusticator,
    dgt,
    frequenza_nota,
    menu,
    panorama_spostato,
    parse_pan_parts,
    parse_pan_values,
    parse_vol_values,
    scomponi_nota,
)

VERSION = "1.11.0" # Acu_Maker segue il motore: note, pan a lista, ascolto, collezioni, rinomina
APP_NAME = "Acu_Maker"
APP_AUTHOR = "Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalità auto)"
RELEASE_DATE = "12 novembre 2026"
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Acu_Collection.json")
DEFAULT_VOL = 0.5

# Le forme d'onda, comprese le quattro di rumore introdotte in Acusticator V7.2
ONDE = {1: 'Sinusoide', 2: 'Quadra', 3: 'Triangolare', 4: 'DenteSega',
        5: 'Rumore bianco', 6: 'Rumore rosa', 7: 'Rumore marrone',
        8: 'Rumore azzurro'}
KIND_RUMORE = (5, 6, 7, 8)
BANDA_DEFAULT = "200-3000"
# Un passo di banda e' un rapporto, non una quantita' di Hertz: cosi' vale
# lo stesso in ogni punto dello spettro. 2 elevato a un dodicesimo e' il
# rapporto di un semitono, circa il sei per cento.
PASSO_BANDA = 2 ** (1 / 12)
# I nomi delle dodici note, con cui si riscrive una nota spostata o nata da
# una frequenza. Leggerle invece e' compito di scomponi_nota di GBUtils.
NOMI_NOTE = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
# Quanto e' larga la banda che nasce da una nota quando si passa a un
# rumore: mezza ottava sotto e mezza ottava sopra, cioe' una banda larga
# un'ottava che si sente intonata su quella nota.
MEZZA_OTTAVA = 2 ** 0.5


def is_portamento(val):
    return isinstance(val, str) and '.' in val


def scivola(val):
	"""Vero se un valore della quartina scorre: il testo con il punto, o dalla
	1.10.0 la lista di due valori, che e' la forma con cui Acu_Maker scrive le
	scivolate di volume (issue 47 di GBUtils)."""
	return is_portamento(val) or (isinstance(val, (list, tuple)) and len(val) == 2)


def scorre(param, val):
	"""Vero se il campo param della quartina scorre, come lo legge il motore.

	Per il pan e il volume decide la lettura del motore e non il punto: dalla
	1.11.0 un pan scritto '0.1' e' fermo a 0,1, com'e' per le app, e non piu'
	una scivolata da 0 a 100 come lo mostrava l'editor (issue 59)."""
	if param == 2:
		return isinstance(parse_pan_values(val), tuple)
	if param == 3:
		if isinstance(val, str):
			return isinstance(parse_vol_values(val), tuple)
		return scivola(val)
	return is_portamento(val)


def is_rumore(kind):
    """Vero se questa forma d'onda vuole una banda al posto della nota."""
    return kind in KIND_RUMORE


def banda_pezzi(val):
    """I quattro valori di una banda, come stringhe.

    Restituisce (basso_inizio, alto_inizio, basso_fine, alto_fine). Gli
    ultimi due sono vuoti se la banda e' ferma. Per la pausa e per la banda
    assente il primo contiene il testo e gli altri sono vuoti.
    """
    testo = str(val).strip()
    if testo.lower() in ('p', 'n', ''):
        return testo.lower(), '', '', ''
    momenti = testo.split('.')
    if len(momenti) > 2:
        return testo, '', '', ''
    tagli = []
    for momento in momenti:
        if '-' not in momento:
            return testo, '', '', ''
        basso, _, alto = momento.partition('-')
        tagli.append((basso.strip(), alto.strip()))
    if len(tagli) == 1:
        return tagli[0][0], tagli[0][1], '', ''
    return tagli[0][0], tagli[0][1], tagli[1][0], tagli[1][1]


def banda_componi(basso_in, alto_in, basso_fi='', alto_fi=''):
    """Rimette insieme i quattro valori, o solo i due se la banda e' ferma."""
    if not alto_in:
        return basso_in
    if basso_fi and alto_fi:
        return f"{basso_in}-{alto_in}.{basso_fi}-{alto_fi}"
    return f"{basso_in}-{alto_in}"


# Quale valore muove ciascun selettore. Gli indici sono nell'ordine
# restituito da banda_pezzi: basso all'inizio, alto all'inizio, basso alla
# fine, alto alla fine.
SCELTA_BANDA = {
    1: (0,),           # taglio basso, dove parte
    2: (1,),           # taglio alto, dove parte
    3: (0, 1),         # tutta la banda di partenza
    4: (2,),           # taglio basso, dove arriva
    5: (3,),           # taglio alto, dove arriva
    6: (2, 3),         # tutta la banda d'arrivo
    7: (0, 1, 2, 3),   # tutto insieme, trasla la scivolata intera
}
NOMI_SCELTA = {
    1: "taglio basso alla partenza",
    2: "taglio alto alla partenza",
    3: "banda di partenza",
    4: "taglio basso all'arrivo",
    5: "taglio alto all'arrivo",
    6: "banda d'arrivo",
    7: "tutti e quattro i valori",
}


def banda_ordinata(pezzi):
    """Vero se in ogni momento il taglio basso sta sotto quello alto.

    Una banda rovesciata non e' un effetto ma un incidente: il motore
    spegne tutto sotto il taglio basso e tutto sopra quello alto, e cio'
    che sopravvive e' solo la sfumatura di un bordo, una fettina di
    spettro che non ha piu' niente a che vedere con i due valori scritti.
    Tagli uguali invece vanno bene: danno una campana stretta.
    """
    coppie = [(pezzi[0], pezzi[1])]
    if pezzi[2] or pezzi[3]:
        coppie.append((pezzi[2], pezzi[3]))
    for basso, alto in coppie:
        try:
            if float(basso) > float(alto):
                return False
        except (TypeError, ValueError):
            return False
    return True


def alterna_scivolata(val):
    """Accende o spegne la scivolata di una banda.

    Una banda ferma, per esempio 200-3000, si sdoppia in 200-3000.200-3000 e
    comincia a poter scorrere; una che gia' scorre torna ferma sulla sua
    banda di partenza.
    """
    b_in, a_in, b_fi, _ = banda_pezzi(val)
    if not a_in:
        return str(val).strip()
    if b_fi:
        return banda_componi(b_in, a_in)
    return banda_componi(b_in, a_in, b_in, a_in)


# I tagli non escono da questi limiti: sotto e sopra non si sente niente e
# non ha senso continuare a spostarli. Il motore poi restringe ancora, fra 40
# Hz e 12 kHz, che e' la fascia in cui l'orecchio e le casse lavorano davvero.
BANDA_MINIMA = 20.0
BANDA_MASSIMA = 20000.0


def normalizza_banda(testo):
    """Controlla e riordina una banda scritta a mano.

    Restituisce la banda ripulita, con i valori riportati dentro i limiti
    udibili, oppure None se non e' leggibile. Serve a non lasciare entrare
    nel preset una banda che poi farebbe cadere l'editor.
    """
    from GBUtils import parse_banda

    grezzo = str(testo).strip().lower()
    if grezzo in ('p', 'n'):
        return grezzo
    try:
        parse_banda(grezzo)
    except (ValueError, TypeError):
        return None

    def limita(pezzo):
        try:
            v = float(pezzo)
        except ValueError:
            return None
        return str(round(max(BANDA_MINIMA, min(BANDA_MASSIMA, v))))

    pezzi = banda_pezzi(grezzo)
    if not pezzi[1]:
        return None
    limitati = [limita(p) if p else '' for p in pezzi]
    if any(x is None for x in limitati):
        return None
    if not banda_ordinata(limitati):
        return None
    return banda_componi(*limitati)


def scala_taglio(taglio, direzione, passo=PASSO_BANDA):
    """Sposta un taglio per rapporto, rispettando il suo portamento.

    Un taglio puo' essere un solo valore, per esempio 200, oppure due uniti
    da un punto, per esempio 200.400, e allora si spostano tutti e due
    insieme cosi' la scivolata resta quella che era.
    """
    def uno(testo):
        try:
            valore = float(testo)
        except ValueError:
            return testo
        nuovo = valore * (passo if direzione > 0 else 1.0 / passo)
        nuovo = max(BANDA_MINIMA, min(BANDA_MASSIMA, nuovo))
        return str(round(nuovo))

    testo = str(taglio).strip()
    if not testo or testo.lower() in ('p', 'n'):
        return testo
    if '.' in testo:
        pezzi = testo.split('.')
        if len(pezzi) == 2:
            return f"{uno(pezzi[0])}.{uno(pezzi[1])}"
    return uno(testo)


def nota_in_hz(val):
    """La frequenza di una nota singola, o None se non e' leggibile.

    Accetta il nome della nota, per esempio c4, d#4, e-4 o c~4, e anche il
    numero, che nel campo della nota e' gia' una frequenza in Hertz. Dalla
    1.11.0 il nome lo legge frequenza_nota di GBUtils, l'unico punto del
    parco software che legge i nomi di nota: fino alla 1.10.0 qui ce n'era
    una seconda copia, che non sapeva di microtoni, ottave a piu' cifre e
    trattino (issue 59).
    """
    if isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        return float(val) if val > 0 else None
    grezzo = str(val).strip().lower()
    if grezzo.isdigit():
        return float(grezzo) if float(grezzo) > 0 else None
    frequenza = frequenza_nota(grezzo)
    return frequenza if frequenza > 0 else None


# Fin dove arrivano c e v sulle note: dal do dell'ottava zero, 16 Hz, al re
# diesis dell'ottava dieci, poco sotto i 20000 Hz, dove l'orecchio smette.
MIDI_MINIMO = 12
MIDI_MASSIMO = 135
# I simboli dei microtoni, come li legge scomponi_nota.
SIMBOLI_MICRO = {0.5: "~", 1.5: "~~", -0.5: "`", -1.5: "``"}


def nome_nota(midi, micro=0.0):
    """Il nome di una nota dal suo numero MIDI, con il microtono se c'e'."""
    return f"{NOMI_NOTE[midi % 12]}{SIMBOLI_MICRO.get(micro, '')}{midi // 12 - 1}"


def hz_in_nota(freq):
    """Il nome della nota piu' vicina a una frequenza.

    Resta fra c0 e d#10, cioe' dentro l'udibile: dalla 1.11.0 il motore legge
    anche le ottave a piu' cifre, e la nota non si ferma piu' a g9.
    """
    if not freq or freq <= 0:
        return 'c4'
    midi = round(69 + 12 * math.log2(freq / 440.0))
    return nome_nota(max(MIDI_MINIMO, min(MIDI_MASSIMO, midi)))


def banda_da_hz(freq):
    """I due tagli della banda larga un'ottava centrata su una frequenza."""
    basso = max(BANDA_MINIMA, min(BANDA_MASSIMA, freq / MEZZA_OTTAVA))
    alto = max(BANDA_MINIMA, min(BANDA_MASSIMA, freq * MEZZA_OTTAVA))
    return str(round(basso)), str(round(alto))


def hz_da_banda(basso, alto):
    """Il centro di una banda, cioe' la frequenza che vi si sente intonata.

    E' la media geometrica dei due tagli e non quella aritmetica: in musica
    conta il rapporto, quindi il centro fra 200 e 3000 sta a meta' strada
    contando le ottave e non gli Hertz.
    """
    try:
        return (float(basso) * float(alto)) ** 0.5
    except (TypeError, ValueError):
        return None


def nota_in_banda(val):
    """Traduce il primo campo dalla nota alla banda, scivolata compresa.

    Una nota diventa la banda larga un'ottava che le sta intorno, e una
    nota che scivola diventa una banda che scorre fra le bande delle due
    note, cosi' passando a un rumore la scivolata resta quella che era.
    """
    if isinstance(val, (int, float)):
        momenti = [val]
    else:
        testo = str(val).strip().lower()
        if testo == 'p':
            return 'p'
        momenti = testo.split('.')
        if len(momenti) != 2:
            momenti = [testo]
    frequenze = [nota_in_hz(m) for m in momenti]
    if frequenze[0] is None:
        return BANDA_DEFAULT
    basso_in, alto_in = banda_da_hz(frequenze[0])
    if len(frequenze) == 1 or frequenze[1] is None:
        return banda_componi(basso_in, alto_in)
    basso_fi, alto_fi = banda_da_hz(frequenze[1])
    return banda_componi(basso_in, alto_in, basso_fi, alto_fi)


def banda_in_nota(val):
    """Traduce il primo campo dalla banda alla nota, scivolata compresa.

    La nota e' quella piu' vicina al centro della banda, e una banda che
    scorre diventa una nota che scivola fra i centri delle due bande, cosi'
    passando a un'onda intonata la scivolata resta quella che era.
    """
    b_in, a_in, b_fi, a_fi = banda_pezzi(val)
    if not a_in:
        return 'p' if str(b_in).strip().lower() == 'p' else 'c4'
    centro_in = hz_da_banda(b_in, a_in)
    if centro_in is None:
        return 'c4'
    nota_in = hz_in_nota(centro_in)
    if not b_fi:
        return nota_in
    centro_fi = hz_da_banda(b_fi, a_fi)
    if centro_fi is None:
        return nota_in
    return f"{nota_in}.{hz_in_nota(centro_fi)}"


def get_keypress():
    """Legge un singolo tasto, gestendo le frecce direzionali in modo nativo e sicuro."""
    if os.name == 'nt':
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):
            ch2 = msvcrt.getwch()
            if ch2 == 'H': return 'up'
            if ch2 == 'P': return 'down'
            if ch2 == 'K': return 'left'
            if ch2 == 'M': return 'right'
            return ch + ch2
        if ch == '\r': return 'enter'
        if ch == '\x1b': return 'esc'
        if ch == ' ': return 'space'
        return ch
    else:
        import select
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b': # Escape sequence (potrebbe essere una freccia)
                r, _, _ = select.select([sys.stdin], [], [], 0.05)
                if r:
                    sys.stdin.read(1) # scarta '['
                    ch2 = sys.stdin.read(1)
                    if ch2 == 'A': return 'up'
                    if ch2 == 'B': return 'down'
                    if ch2 == 'C': return 'right'
                    if ch2 == 'D': return 'left'
                return 'esc'
            if ch == '\n' or ch == '\r': return 'enter'
            if ch == ' ': return 'space'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Quanto puo' essere lunga una descrizione scritta nell'editor: la piu' lunga
# della collezione, il 23 ottobre 2026, passava i mille caratteri.
LUNGHEZZA_DESCRIZIONE = 5000


# La collezione d'esempio, scritta quando il file non c'e'.
ESEMPIO = {
	"do_re_mi": {
		"descrizione": "Tre note C D E ascendenti",
		"score": [["c4", 0.5, -1.0, 0.0], ["d4", 0.5, 0.0, 0.0], ["e4", 0.5, 1.0, 0.0]],
		"kind": 1,
		"adsr": [0.002, 0.0, 100.0, 0.002],
	}
}


def copia(dati):
	"""Una copia profonda di dati del JSON, che si puo' cambiare senza toccare l'originale."""
	return json.loads(json.dumps(dati))


class Collezione:
	"""La collezione sul disco, letta e scritta soltanto attraverso Acusticator.aggiorna.

	Dalla 1.9.0, per la issue 58 di GBUtils: fino alla 1.8.1 Acu_Maker teneva
	in memoria la copia letta all'avvio e la riscriveva intera a ogni Elimina e
	all'uscita, cancellando cio' che altri programmi, altre sessioni o un git
	pull vi avevano scritto nel frattempo; e le modifiche di una sessione
	restavano in memoria fino all'uscita, cosi' che un Ctrl+C le perdeva tutte.
	Adesso ogni cambiamento si scrive subito, da solo, fuso con il disco di
	quel momento: sotto lucchetto si rilegge il file, si cambia soltanto il
	preset toccato, e il file si sostituisce in un colpo.
	dati e' la collezione com'era all'ultima lettura o scrittura: serve a
	mostrare e a cercare, mai a riscrivere.
	"""

	def __init__(self, percorso):
		self.percorso = percorso
		self.dati = {}
		self.impronta = None

	def _impronta_file(self):
		"""Data e misura del file: quando cambiano, qualcuno l'ha scritto."""
		try:
			stato = os.stat(self.percorso)
		except OSError:
			return None
		return (stato.st_mtime_ns, stato.st_size)

	def leggi(self):
		"""Rilegge il disco. Falso se il file non si lascia leggere: allora
		resta la copia di prima, e niente si scrive."""
		dati = Acusticator.aggiorna(lambda _dati: False, self.percorso)
		if dati is None:
			print("La collezione non si lascia leggere adesso: forse e' a meta' di un salvataggio, o ha un conflitto di git.")
			return False
		self.dati = copia(dati)
		self.impronta = self._impronta_file()
		return True

	def cambiata(self):
		"""Vero se dall'ultima lettura qualcun altro ha scritto il file."""
		return self._impronta_file() != self.impronta

	def ricarica(self):
		"""Se il file e' cambiato lo rilegge, e dice quanti preset sono nuovi,
		cambiati e tolti. Restituisce le tre liste, o None se non c'era niente."""
		if not self.cambiata():
			return None
		prima = self.dati
		if not self.leggi():
			return None
		nuovi, cambiati, tolti = differenze(prima, self.dati)
		if nuovi or cambiati or tolti:
			print(f"La collezione e' cambiata sul disco: {len(nuovi)} preset nuovi, "
				  f"{len(cambiati)} cambiati, {len(tolti)} tolti.")
		return nuovi, cambiati, tolti

	def scrivi(self, cambia):
		"""Cambia il disco con cambia(dati), attraverso Acusticator.aggiorna.

		Vero se ha scritto, o se cambia ha detto che non c'era niente da
		scrivere; falso se il file era illeggibile o occupato."""
		dati = Acusticator.aggiorna(cambia, self.percorso)
		if dati is None:
			print("Non ho potuto scrivere la collezione: il file e' illeggibile o occupato da un altro programma. Non ho cambiato niente.")
			return False
		self.dati = copia(dati)
		self.impronta = self._impronta_file()
		return True

	def apri(self):
		"""La prima lettura: se il file non c'e' nasce con l'esempio, e i
		doppioni si cercano sul disco di adesso. Falso se non si legge."""
		if not os.path.exists(self.percorso):
			self.scrivi(lambda dati: dati.update(copia(ESEMPIO)) if not dati else False)
		if not self.leggi():
			return False
		self.togli_doppioni()
		return True

	def togli_doppioni(self):
		"""Toglie i doppioni dal disco di adesso, e scrive solo se ne ha tolti."""
		self.scrivi(lambda dati: bool(togli_doppioni(dati)))

	def elimina(self, nome):
		"""Toglie dal disco soltanto quel preset. Vero se c'era."""
		trovato = []
		def togli(dati):
			if nome not in dati:
				return False
			del dati[nome]
			trovato.append(nome)
			return True
		return self.scrivi(togli) and bool(trovato)

	def salva_nuovo(self, voluto, preset):
		"""Scrive il preset sotto un nome libero sul disco di adesso, voluto se
		c'e' posto, altrimenti voluto seguito da un numero. Restituisce il
		nome usato, o None se non ha scritto."""
		usato = []
		def metti(dati):
			nome = get_unique_name(dati, voluto)
			dati[nome] = copia(preset)
			usato.append(nome)
		if self.scrivi(metti) and usato:
			return usato[0]
		return None

	def sovrascrivi(self, nome, base, mio, chiedi):
		"""Scrive il preset nome fondendo cio' che si e' cambiato con cio' che
		nel frattempo e' cambiato sul disco.

		base e' il preset com'era all'apertura, mio com'e' adesso nell'editor.
		La fusione e' campo per campo, vedi fondi: senza conflitti scrive
		subito. Un campo cambiato da tutte e due le parti, o il preset tolto da
		un altro programma, si chiede con chiedi(conflitti), che risponde mio,
		disco oppure None per annullare; il lucchetto non si tiene mai mentre
		si aspetta la risposta. Restituisce vero se ha scritto."""
		scelta = None
		for _ in range(5):
			esito = {}
			def fondi_qui(dati, scelta=scelta, esito=esito):
				disco = dati.get(nome)
				if disco is None:
					if scelta == "disco":
						# Tolto da un altro, e si accetta che resti tolto.
						esito["accettato"] = True
						return False
					if scelta != "mio":
						esito["conflitti"] = ["tolto"]
						return False
					dati[nome] = copia(mio)
					return True
				fuso, conflitti = fondi(base, mio, disco, scelta)
				if conflitti:
					esito["conflitti"] = conflitti
					return False
				if fuso == disco:
					return False
				dati[nome] = fuso
				return True
			if not self.scrivi(fondi_qui):
				return False
			if "accettato" in esito:
				return False
			if "conflitti" not in esito:
				return True
			scelta = chiedi(esito["conflitti"])
			if scelta is None:
				return False
		return False


# Il segnaposto di un campo che in un preset non c'e'.
_ASSENTE = object()
# I campi di un preset come li dice Acu_Maker, per i conflitti.
NOMI_CAMPI = {"descrizione": "la descrizione", "score": "le quartine", "kind": "la forma d'onda",
			  "adsr": "l'inviluppo", "usato_da": "le firme", "tolto": "il preset, tolto da un altro programma"}


def fondi(base, mio, disco, scelta=None):
	"""La fusione a tre di un preset, campo per campo.

	Un campo che ho cambiato solo io prende il mio valore; uno cambiato solo
	sul disco prende quello del disco; uno cambiato da tutte e due le parti in
	modo diverso e' un conflitto, che scelta risolve: mio, disco, oppure None
	per lasciarlo da risolvere. Restituisce il preset fuso e la lista dei
	campi in conflitto rimasti. Il caso tipico, il suono rifatto nell'editor
	e la firma aggiunta da un'altra sessione, si fonde da solo.
	"""
	campi = list(disco) + [c for c in mio if c not in disco] + [c for c in base if c not in disco and c not in mio]
	fuso = {}
	conflitti = []
	for campo in campi:
		b, m, d = base.get(campo, _ASSENTE), mio.get(campo, _ASSENTE), disco.get(campo, _ASSENTE)
		if m == d or d == b:
			valore = m
		elif m == b:
			valore = d
		elif scelta == "mio":
			valore = m
		elif scelta == "disco":
			valore = d
		else:
			conflitti.append(campo)
			valore = d
		if valore is not _ASSENTE:
			fuso[campo] = copia(valore)
	return fuso, conflitti


def rinomina(coll, nome):
	"""Cambia il nome di un preset, al suo posto nella collezione.

	Dalla 1.11.0: fino alla 1.10.0 la rinomina non c'era, e Salva come con un
	nome nuovo lasciava anche il vecchio, che all'uscita i doppioni potevano
	togliere proprio quando era quello che le app chiamavano (issue 59)."""
	app = app_che_usano(coll.dati, nome)
	if app:
		print(f"Attenzione: lo usano {', '.join(app)}, che lo chiamano per nome. Dopo la rinomina vanno cambiate anche loro.")
		if input("Lo rinomino lo stesso? (s/n): ").strip().lower() != "s":
			return False
	nuovo = dgt(f"Nome nuovo per {nome}: ", kind="s", smax=50,
				avvisi={"troppo_lunga": "Al massimo {massimo} caratteri, ne hai scritti {lunghezza}."})
	nuovo = nuovo.strip().replace(" ", "")
	if not nuovo or nuovo == nome:
		print("Nome non cambiato.")
		return False
	esito = []
	def cambia(dati):
		if nome not in dati:
			esito.append("tolto")
			return False
		if nuovo in dati:
			esito.append("preso")
			return False
		voci = list(dati.items())
		dati.clear()
		dati.update((nuovo if n == nome else n, v) for n, v in voci)
		esito.append("fatto")
		return True
	if not coll.scrivi(cambia):
		return False
	if esito == ["preso"]:
		print(f"Il nome {nuovo} c'e' gia': non rinomino.")
	elif esito == ["tolto"]:
		print(f"Il preset {nome} non c'e' piu': l'ha tolto un altro programma.")
	else:
		print(f"Rinominato da {nome} a {nuovo}.")
	return esito == ["fatto"]


def cambia_descrizione(coll, nome):
	"""Cambia soltanto la descrizione di un preset, senza entrare nell'editor.
	Fino alla 1.10.0 la si cambiava soltanto dentro Salva come, dopo una
	modifica (issue 59)."""
	vecchia = str(coll.dati[nome].get("descrizione", ""))
	print(f"Descrizione di adesso: {vecchia}")
	nuova = dgt("\rDescrizione nuova, Invio la lascia\r", kind="s", smax=LUNGHEZZA_DESCRIZIONE, default=vecchia,
				avvisi={"troppo_lunga": "Al massimo {massimo} caratteri, ne hai scritti {lunghezza}."}).strip()
	if not nuova or nuova == vecchia:
		print("Descrizione non cambiata.")
		return False
	def cambia(dati):
		if nome not in dati:
			return False
		dati[nome]["descrizione"] = nuova
		return True
	if coll.scrivi(cambia) and coll.dati.get(nome, {}).get("descrizione") == nuova:
		print("Descrizione cambiata.")
		return True
	print("Descrizione non cambiata.")
	return False


def scegli_scheda():
	"""Sceglie il dispositivo su cui Acu_Maker suona. Fino alla 1.10.0 non si
	poteva scegliere (issue 59)."""
	from GBUtils import elenco_dispositivi_audio
	dispositivi = elenco_dispositivi_audio(prova="nessuno")
	if not dispositivi:
		print("Nessun dispositivo di uscita trovato.")
		return
	voci = {str(d["indice"]): f"{d['dispositivo']}, {d['breve']}" for d in dispositivi}
	scelta = menu(voci, p="Scheda> ", show=True, ordered=False)
	if scelta is None:
		return
	try:
		Acusticator.setup(device=int(scelta))
	except (ValueError, OSError) as errore:
		print(f"Non riesco a usare quel dispositivo: {errore}")
		return
	print(f"Suono su {voci[scelta]}.")
	Acusticator(["c5", 0.12, 0, 0.4])


def apri_collezione(coll):
	"""Apre un'altra collezione, per esempio quella di un progetto. Fino alla
	1.10.0 Acu_Maker apriva soltanto quella condivisa (issue 59)."""
	scritto = input("\rPercorso della collezione, Invio per quella condivisa\r").strip().strip('"')
	percorso = os.path.abspath(scritto) if scritto else DB_FILE
	if not os.path.exists(percorso) and input(f"{percorso} non esiste. La creo? (s/n): ").strip().lower() != "s":
		return
	coll.percorso = percorso
	coll.dati, coll.impronta = {}, None
	if coll.apri():
		print(f"Collezione {percorso}, {len(coll.dati)} preset.")


def differenze(prima, dopo):
	"""I preset nuovi, cambiati e tolti fra due letture della collezione."""
	nuovi = [n for n in dopo if n not in prima]
	tolti = [n for n in prima if n not in dopo]
	cambiati = [n for n in dopo if n in prima and dopo[n] != prima[n]]
	return nuovi, cambiati, tolti

def get_unique_name(db, base_name):
    if base_name not in db:
        return base_name
    i = 0
    while f"{base_name}{i}" in db:
        i += 1
    return f"{base_name}{i}"

def impronta_suono(preset):
    """Cio' che rende due preset lo stesso suono: score, kind e adsr.

    Il nome e la descrizione non contano: due preset che suonano identici
    sono un doppione anche se si chiamano in modo diverso.
    """
    return json.dumps([preset.get("score"), preset.get("kind"),
                       preset.get("adsr")], sort_keys=True)


def togli_doppioni(db):
    """Toglie dalla collezione i preset che suonano identici a un altro, e dice quali.

    Due preset sono lo stesso suono quando hanno la stessa impronta, cioe' lo
    stesso score, la stessa forma d'onda e lo stesso inviluppo: il nome e la
    descrizione non contano. Di ogni gruppo di suoni identici resta quello
    con la descrizione piu' lunga, che e' la piu' utile a chi cerca un suono;
    a parita' di lunghezza resta il primo che compare nella collezione.
    Stampa una riga per ogni preset tolto e restituisce le coppie
    (tolto, tenuto). La collezione serve tutto il parco software: i suoni
    diversi restano tutti, anche quelli che oggi nessuno usa.
    Dalla 1.11.0 un preset che un'app usa non sparisce mai da solo: le app lo
    chiamano per nome, e resterebbero mute. Fino alla 1.10.0 restava la
    descrizione piu' lunga senza guardare altro, e un gemello di apertura,
    firmato da sette app, con una frase in piu', l'avrebbe fatta sparire
    (issue 59). Se nel gruppo un solo preset e' usato, resta lui; se lo sono
    due o piu', il gruppo resta com'e', e lo si dice: per unirli bisogna
    prima cambiare le app.
    """
    gruppi = {}
    for nome, preset in db.items():
        gruppi.setdefault(impronta_suono(preset), []).append(nome)
    tolti = []
    for nomi in gruppi.values():
        if len(nomi) < 2:
            continue
        usati = [n for n in nomi if app_che_usano(db, n)]
        if len(usati) >= 2:
            print(f"Suonano identici ma li usano le app, quindi restano tutti: {', '.join(usati)}.")
            continue
        if usati:
            tenuto = usati[0]
        else:
            tenuto = max(nomi, key=lambda n: (len(str(db[n].get("descrizione", ""))), -nomi.index(n)))
        for nome in nomi:
            if nome != tenuto:
                tolti.append((nome, tenuto))
    for nome, tenuto in tolti:
        del db[nome]
        print(f"Doppione tolto: '{nome}' suonava identico a '{tenuto}', che resta.")
    return tolti


# La firma delle app in fondo alla descrizione: "Usato da: meteora, mess."
FIRMA = re.compile(r"\s*Usato da: ([^.]*)\.\s*$")


def app_che_usano(db, nome):
	"""Le app che usano un preset: quelle della sua firma, e quella del suo
	prefisso, quando il prefisso e' il nome di un'app che firma altrove."""
	firme = set()
	for preset in db.values():
		trovata = FIRMA.search(str(preset.get("descrizione", "")))
		if trovata:
			firme.update(a.strip().lower() for a in trovata.group(1).split(",") if a.strip())
	trovata = FIRMA.search(str(db[nome].get("descrizione", "")))
	sue = {a.strip().lower() for a in trovata.group(1).split(",") if a.strip()} if trovata else set()
	prefisso = nome.split("_", 1)[0].lower() if "_" in nome else ""
	if prefisso in firme:
		sue.add(prefisso)
	return sorted(sue)


def trova_gemello(db, preset, escludi=None):
    """Il nome del primo preset che suona identico a questo, o None."""
    cercata = impronta_suono(preset)
    for nome, dati in db.items():
        if nome == escludi:
            continue
        if impronta_suono(dati) == cercata:
            return nome
    return None


def transpose_note(note_str, semitones):
    """La nota spostata di tanti semitoni, microtono compreso.

    Restituisce la pausa com'e', il nome nuovo, oppure None quando la nota
    uscirebbe da c0 o da d#10, o quando il nome non si legge: allora c e v
    restano fermi e lo dicono. Fino alla 1.10.0 un passo in giu' da c0
    scriveva b-1, che il motore legge come si bemolle 1, e oltre g#9 la nota
    tornava indietro; i microtoni, le ottave da 10 in su e il trattino
    restavano fermi senza avviso (issue 59)."""
    if str(note_str).strip().lower() == 'p':
        return note_str
    scomposta = scomponi_nota(note_str)
    if scomposta is None:
        return None
    midi, micro = scomposta
    nuovo = midi + semitones
    if not MIDI_MINIMO <= nuovo <= MIDI_MASSIMO:
        return None
    return nome_nota(nuovo, micro)

class EditorState:
    def __init__(self, preset_data):
        self.preset = json.loads(json.dumps(preset_data))
        # Il preset com'era all'apertura: Sovrascrivi lo confronta con il
        # proprio e con quello del disco, per fondere senza perdere niente.
        self.originale = json.loads(json.dumps(preset_data))
        # Dalla 1.11.0 i campi che il motore lascia facoltativi, onda e
        # inviluppo, si riempiono con i suoi predefiniti, e un kind scritto
        # come testo o come decimale diventa il numero: fino alla 1.10.0 un
        # preset senza di loro faceva cadere l'editor (issue 59).
        try:
            kind = float(self.preset.get('kind', 1))
            self.preset['kind'] = int(kind) if kind.is_integer() and int(kind) in ONDE else 1
        except (TypeError, ValueError):
            self.preset['kind'] = 1
        if not isinstance(self.preset.get('adsr'), list) or len(self.preset['adsr']) != 4:
            self.preset['adsr'] = [0.002, 0.0, 100.0, 0.002]
        # Cio' che la conversione fra note e rumori ha cambiato, per
        # rimetterlo com'era al ritorno: vedi cambia_onda.
        self.memoria_onde = {}
        # Il volume d'ascolto, cioe' la base su cui si sente il preset, come
        # la sceglie un programma: None e' la base 0,5 del file.
        self.base_ascolto = None
        # La maniglia del preset che suona in ciclo, se ce n'e' uno.
        self.ciclo = None
        self.focus_type = 'score'
        self.focus_idx = 0
        self.focus_param = 0
        self.port_focus = 3
        
        self.steps = {
            'banda': PASSO_BANDA,
            'note': 10.0,
            'dur': 0.02,
            'pan': 10,
            'vol': 10,
            'a': 0.001,
            'd': 0.001,
            's': 1.0,
            'r': 0.001
        }
        self.modified = False
        self.running = True
        # La posizione d'ascolto: lo spostamento generale di panorama con cui
        # si sente il preset, come farebbe il programma che lo suona. Non fa
        # parte del preset e non viene salvata: serve a sentire se il suono
        # regge quando qualcuno lo mette di lato. Con u si puo' pero' unire
        # alle quartine, e allora diventa parte del preset.
        self.posizione = None

def pan_to_user(val):
    """Il panorama nella scala dell'editor, da -100 a 100, letto come lo legge
    il motore: dalla 1.11.0 parse_pan_values, la stessa lettura delle app.
    Fino alla 1.10.0 l'editor spezzava sul punto, e un '0.1' fermo a 0,1
    nelle app appariva come una scivolata da 0 a 100 (issue 59)."""
    letto = parse_pan_values(val)
    if isinstance(letto, tuple):
        return f"{round(letto[0] * 100)}.{round(letto[1] * 100)}"
    return str(round(letto * 100))

def user_to_pan(val_str):
    """Dalla scala dell'editor al file: un numero quando il panorama sta
    fermo, e per la scivolata scritta con il punto, come -100.100, la lista
    dei due valori. Fino alla 1.10.0 la scivolata si scriveva come testo con i
    capi senza decimali, e il motore la leggeva come un valore solo quando il
    testo era un decimale valido: da 0 a 100 diventava '0.1', fermo a 0,1
    (issue 59)."""
    val_str = str(val_str).strip()
    if is_portamento(val_str):
        parts = parse_pan_parts(val_str)
        p1 = max(-1.0, min(1.0, float(parts[0]) / 100.0))
        p2 = max(-1.0, min(1.0, float(parts[1]) / 100.0))
        return [round(p1, 2), round(p2, 2)]
    else:
        fval = float(val_str) / 100.0
        return max(-1.0, min(1.0, round(fval, 2)))

def leggi_posizione(scritto):
    """Traduce in posizione d'ascolto cio' che si e' scritto.

    Restituisce la coppia (valore, errore). Valore None vuol dire nessuna
    posizione, cioe' il preset si sente dov'e' scritto.
    """
    scritto = str(scritto).strip()
    if not scritto:
        return None, None
    # La forma si controlla prima di tradurre: parse_pan_parts, quando non
    # riconosce niente, spezza sul primo punto e restituisce comunque due
    # pezzi, cosi' che 1.2.3.4.x diventava una posizione da 1 a 2 senza che
    # nessuno protestasse. Qui il punto vuol dire sempre scivolata, mai
    # decimale, come nel campo del panorama e in quello della banda.
    if not re.fullmatch(r"-?\d+(\.-?\d+)?", scritto):
        return None, ("Non l'ho capito. Serve un numero da -100 a 100, oppure due numeri "
                      "uniti dal punto come -100.100 per farlo scorrere.")
    try:
        valore = user_to_pan(scritto)
    except (TypeError, ValueError):
        return None, ("Non l'ho capito. Serve un numero da -100 a 100, oppure due numeri "
                      "uniti dal punto come -100.100 per farlo scorrere.")
    if isinstance(valore, float) and abs(valore) < 1e-9:
        return None, None
    return valore, None

def posizione_breve(valore):
    """La posizione d'ascolto come codice corto per la riga di stato."""
    return "" if valore is None else f" p{pan_to_user(valore)}"

def pan_in_file(valore):
    """Il panorama nella forma con cui il file lo scrive: un numero quando sta
    fermo, e dalla 1.11.0 la lista dei due valori quando scorre. Fino alla
    1.10.0 erano due numeri uniti dal punto, e -1.0 con 0.1 diventava '-1.0'
    e '0.1', fermi (issue 59)."""
    if isinstance(valore, (tuple, list)):
        return [round(float(valore[0]), 2), round(float(valore[1]), 2)]
    return round(float(valore), 2)

def vol_to_user(val):
    """Il volume di una quartina nella scala dell'editor, da 0 a 100.

    Uno scarto dalla base, numero o lista di due per la scivolata, si somma
    alla base 0,5. Il testo, la forma dei file di prima, e' un volume
    assoluto: dalla 1.10.0 si legge cosi', come lo leggono le app, mentre
    fino alla 1.9.0 l'editor lo prendeva per scarti (issue 47 di GBUtils)."""
    if isinstance(val, (list, tuple)) and len(val) == 2:
        v1 = max(0, min(100, round((DEFAULT_VOL + float(val[0])) * 100)))
        v2 = max(0, min(100, round((DEFAULT_VOL + float(val[1])) * 100)))
        return f"{v1}.{v2}"
    if isinstance(val, str):
        assoluto = parse_vol_values(val)
        if isinstance(assoluto, tuple):
            return f"{round(assoluto[0] * 100)}.{round(assoluto[1] * 100)}"
        return str(round(assoluto * 100))
    v = round((DEFAULT_VOL + float(val)) * 100)
    return str(max(0, min(100, v)))

def user_to_vol(val_str):
    """Dalla scala dell'editor al file: uno scarto dalla base 0,5, oppure,
    per la scivolata scritta con il punto, come 20.80, la lista dei due
    scarti. Fino alla 1.9.0 la scivolata si scriveva come testo, '0.0.3', che
    le app leggevano come volume assoluto, da 0 a 0,3 invece che da 0,5 a 0,8
    (issue 47 di GBUtils)."""
    val_str = str(val_str).strip()
    if is_portamento(val_str):
        parts = parse_pan_parts(val_str)
        d1 = max(-0.5, min(0.5, (float(parts[0]) / 100.0) - DEFAULT_VOL))
        d2 = max(-0.5, min(0.5, (float(parts[1]) / 100.0) - DEFAULT_VOL))
        return [round(d1, 2), round(d2, 2)]
    else:
        v = float(val_str) / 100.0
        d = v - DEFAULT_VOL
        return max(-0.5, min(0.5, round(d, 2)))

def get_status_string(state):
    if state.focus_type == 'score':
        quad = state.preset['score'][state.focus_idx]
        param_names = ["Nota", "Durata", "Pan", "Volume"]
        if state.focus_param == 0 and is_rumore(state.preset.get('kind', 1)):
            pezzi = list(banda_pezzi(quad[0]))
            scelti = SCELTA_BANDA.get(state.port_focus, ())
            if pezzi[1]:
                mostrati = [f"<{p}>" if i in scelti else p
                            for i, p in enumerate(pezzi) if p]
                if len(mostrati) == 4:
                    val_str = f"{mostrati[0]}-{mostrati[1]}.{mostrati[2]}-{mostrati[3]}"
                else:
                    val_str = f"{mostrati[0]}-{mostrati[1]}"
            else:
                val_str = pezzi[0]
            s = f"Sc.{state.focus_idx+1} Banda: {val_str}"
        elif state.focus_param == 0:
            val = quad[0]
            if is_portamento(val):
                parts = val.split('.')
                p1 = f"<{parts[0]}>" if state.port_focus in (1, 3) else parts[0]
                p2 = f"<{parts[1]}>" if state.port_focus in (2, 3) else parts[1]
                val_str = f"{p1}.{p2}"
            else:
                val_str = str(val)
            s = f"Sc.{state.focus_idx+1} {param_names[0]}: {val_str}"
        elif state.focus_param == 2:
            val_user = pan_to_user(quad[2])
            if is_portamento(val_user):
                parts = val_user.split('.')
                p1 = f"<{parts[0]}>" if state.port_focus in (1, 3) else parts[0]
                p2 = f"<{parts[1]}>" if state.port_focus in (2, 3) else parts[1]
                val_str = f"{p1}.{p2}"
            else:
                val_str = str(val_user)
            s = f"Sc.{state.focus_idx+1} {param_names[2]}: {val_str}"
        elif state.focus_param == 3:
            val_user = vol_to_user(quad[3])
            if is_portamento(val_user):
                parts = val_user.split('.')
                p1 = f"<{parts[0]}>" if state.port_focus in (1, 3) else parts[0]
                p2 = f"<{parts[1]}>" if state.port_focus in (2, 3) else parts[1]
                val_str = f"{p1}.{p2}"
            else:
                val_str = str(val_user)
            s = f"Sc.{state.focus_idx+1} {param_names[3]}: {val_str}"
        else:
            s = f"Sc.{state.focus_idx+1} {param_names[state.focus_param]}: {quad[state.focus_param]}"
    else:
        adsr = list(state.preset['adsr'])
        adsr[state.focus_param] = f"<{adsr[state.focus_param]}>"
        s = f"ADSR: {adsr[0]} {adsr[1]} {adsr[2]} {adsr[3]}"
    return s + posizione_breve(state.posizione) + ascolto_breve(state)

def cambia_onda(state, nuova):
	"""Passa il preset all'onda nuova, e dice com'e' andata.

	Passando fra note e rumore il primo campo cambia significato: si converte
	quello che c'e', scivolata compresa. La conversione pero' perde qualcosa,
	dissolvenze, bande, microtoni, scivolate in Hz, e fino alla 1.10.0 andata
	e ritorno guastavano il primo campo: 82 preset su 652, e il fischio di
	MESS da 2847 Hz finiva a 784 (issue 59). Dalla 1.11.0 l'editor ricorda il
	valore di prima di ogni quartina convertita, e se al ritorno la quartina
	non e' stata toccata lo rimette com'era."""
	prima_rumore = is_rumore(state.preset.get('kind', 1))
	state.preset['kind'] = nuova
	state.modified = True
	adesso_rumore = is_rumore(nuova)
	if prima_rumore != adesso_rumore:
		ricordati = 0
		for quartina in state.preset['score']:
			if str(quartina[0]).strip().lower() == 'p':
				continue
			memoria = state.memoria_onde.get(id(quartina))
			if memoria is not None and memoria[0] is quartina and memoria[2] == quartina[0]:
				# Torna com'era, perche' da allora nessuno l'ha toccata.
				quartina[0] = memoria[1]
				del state.memoria_onde[id(quartina)]
				ricordati += 1
				continue
			convertito = nota_in_banda(quartina[0]) if adesso_rumore else banda_in_nota(quartina[0])
			state.memoria_onde[id(quartina)] = (quartina, quartina[0], convertito)
			quartina[0] = convertito
		state.port_focus = 3
		testo = f"Onda: {ONDE[nuova]}, il primo campo ora e' {'la banda' if adesso_rumore else 'la nota'}"
		if ricordati:
			testo += ", tornato com'era"
	else:
		testo = f"Onda: {ONDE[nuova]}"
	print(f"\r{' ' * 60}\r{testo}", end="", flush=True)


def handle_print(state, force_newline=False):
    s = get_status_string(state)
    if force_newline:
        print()
    # Sessanta e non cinquanta: con la posizione d'ascolto in coda la riga
    # puo' arrivare piu' in la', e quel che resta della precedente si legge
    # sul display braille come se fosse ancora li'.
    clear_line = " " * 60
    print(f"\r{clear_line}\r{s}", end="", flush=True)

def play_preset(state):
    """Suona il preset come lo suonano le app: dalla 1.10.0 passa da
    Acusticator.prepara, la stessa lettura di Acusticator.preset, invece che
    da una conversione sua, cosi' editor e app non possono piu' divergere
    (issue 47 di GBUtils)."""
    score, kind, adsr = Acusticator.prepara(state.preset, volume=state.base_ascolto, pan=state.posizione)
    Acusticator(score, kind=kind, adsr=adsr, sync=False)

def play_quad(state):
    """Suona la sola quartina corrente, con la stessa lettura delle app."""
    quartina = {"score": [state.preset['score'][state.focus_idx]],
                "kind": state.preset.get('kind', 1), "adsr": state.preset.get('adsr')}
    score, kind, adsr = Acusticator.prepara(quartina, volume=state.base_ascolto, pan=state.posizione)
    Acusticator(score, kind=kind, adsr=adsr, sync=False)


def zittisci(state):
	"""Ferma tutto quello che l'editor sta suonando, ciclo compreso. Dalla
	1.11.0 lo Spazio zittisce prima di suonare: ripetuto, sovrapponeva fino a
	trentadue voci (issue 59)."""
	if state.ciclo is not None:
		state.ciclo.stop()
		state.ciclo = None
	Acusticator.stop()


def alterna_ciclo(state):
	"""Accende o spegne l'ascolto in ciclo del preset. Restituisce cosa dire."""
	if state.ciclo is not None and state.ciclo.attivo:
		zittisci(state)
		return "Ciclo fermato"
	zittisci(state)
	score, kind, adsr = Acusticator.prepara(state.preset, volume=state.base_ascolto, pan=state.posizione)
	# Senza dissolvenza: si sente il preset come suona, giro dopo giro.
	state.ciclo = Acusticator.ciclo(score, kind=kind, adsr=adsr, dissolvenza=0)
	return "In ciclo, t lo ferma" if state.ciclo is not None else "Il ciclo non parte"


def ascolto_breve(state):
	"""Il volume d'ascolto come codice corto per la riga di stato."""
	return "" if state.base_ascolto is None else f" o{round(state.base_ascolto * 100)}"

AVVISO_NOTA = ("Nota non valida: un nome come c4, f#3, e-4 o c~4, una frequenza in Hz, "
			   "oppure p per la pausa.")
AVVISO_CAPO = ("Capo non valido: un nome come c4 o f#3, una frequenza in Hz senza decimali, "
			   "perche' il punto separa i due capi, oppure p.")


def capo_valido(testo):
	"""Vero se testo puo' stare in un capo di una scivolata di note."""
	return testo == 'p' or (testo.isdigit() and int(testo) > 0) or scomponi_nota(testo) is not None


def nota_scritta(testo):
	"""Cio' che si scrive per una nota digitata con Invio, o None se non va.

	Un numero e' una frequenza in Hz, anche con i decimali; un nome lo deve
	saper leggere scomponi_nota; due capi uniti dal punto sono una scivolata,
	e ognuno deve andar bene da se'."""
	if testo == 'p':
		return 'p'
	try:
		numero = float(testo)
	except ValueError:
		numero = None
	if numero is not None:
		return numero if math.isfinite(numero) and numero > 0 else None
	if '.' in testo:
		parti = testo.split('.')
		return testo if len(parti) == 2 and all(capo_valido(p) for p in parti) else None
	return testo if scomponi_nota(testo) is not None else None


def valori_mostrati(state):
	"""Le parti del valore selezionato come le mostra la riga di stato: una,
	o le due della scivolata quando il fuoco e' su tutte e due."""
	if state.focus_type == 'adsr':
		return [str(state.preset['adsr'][state.focus_param])]
	param = state.focus_param
	quad = state.preset['score'][state.focus_idx]
	if param == 0 and is_rumore(state.preset.get('kind', 1)):
		return []
	if param == 1:
		return [str(quad[1])]
	if param == 0:
		testo = str(quad[0]).lower()
	elif param == 2:
		testo = pan_to_user(quad[2])
	else:
		testo = vol_to_user(quad[3])
	if not scorre(param, quad[param]):
		return [testo]
	parti = testo.split('.')
	return [parti[i] for i in {1: (0,), 2: (1,)}.get(state.port_focus, (0, 1))]


def riconferma(state, scritto):
	"""Vero se cio' che si e' scritto con Invio e' proprio il valore mostrato."""
	parti = valori_mostrati(state)
	return bool(parti) and all(parte == scritto for parte in parti)


def transpose_single(val_str, direction, step):
    """Un capo della scivolata spostato di un passo: i nomi di un semitono,
    gli Hertz di step. None se non si puo' muovere, vedi transpose_note."""
    if val_str.lower() == 'p': return 'p'
    try:
        fval = float(val_str)
    except ValueError:
        return transpose_note(val_str, direction)
    nuovo = fval + direction * step
    if nuovo < 1:
        return None
    if fval.is_integer() and float(step).is_integer():
        return str(int(nuovo))
    return str(round(nuovo, 2))

def inc_dec_value(state, direction):
    """Muove il valore corrente di un passo.

    Restituisce None se si e' mosso, altrimenti la ragione per cui e'
    rimasto fermo, che il chiamante mostra al posto della riga di stato.
    """
    era_modificato = state.modified
    state.modified = True
    if state.focus_type == 'score':
        quad = state.preset['score'][state.focus_idx]
        param = state.focus_param
        if param == 0 and is_rumore(state.preset.get('kind', 1)):
            pezzi = list(banda_pezzi(quad[0]))
            if not pezzi[1]:
                # pausa oppure nessuna banda: non c'e' niente da spostare
                state.modified = era_modificato
                return "Qui non c'e' una banda da spostare"
            passo = state.steps.get('banda', PASSO_BANDA)
            nuovi = list(pezzi)
            for i in SCELTA_BANDA.get(state.port_focus, (0, 1)):
                if nuovi[i]:
                    nuovi[i] = scala_taglio(nuovi[i], direction, passo)
            if not banda_ordinata(nuovi):
                # Il taglio basso finirebbe sopra quello alto: la banda
                # non lascerebbe passare piu' niente di sensato.
                state.modified = era_modificato
                return 'I tagli si incrocerebbero, fermo qui'
            quad[0] = banda_componi(*nuovi)
        elif param == 0:
            val = quad[0]
            fermo = "La nota uscirebbe dalla scala, o non si legge: fermo qui"
            if is_portamento(val):
                parts = val.split('.')
                if state.port_focus in (1, 3):
                    parts[0] = transpose_single(parts[0], direction, state.steps['note'])
                if state.port_focus in (2, 3):
                    parts[1] = transpose_single(parts[1], direction, state.steps['note'])
                if None in parts:
                    state.modified = era_modificato
                    return fermo
                quad[0] = f"{parts[0]}.{parts[1]}"
            else:
                if isinstance(val, str) and val.lower() != 'p':
                    nuova = transpose_single(val, direction, state.steps['note'])
                    if nuova is None:
                        state.modified = era_modificato
                        return fermo
                    quad[0] = nuova
                elif isinstance(val, (int, float)) and not isinstance(val, bool):
                    nuova = round(val + direction * state.steps['note'], 2)
                    if nuova < 1:
                        state.modified = era_modificato
                        return fermo
                    quad[0] = nuova
        elif param == 1:
            quad[1] = max(0.0, round(quad[1] + direction * state.steps['dur'], 3))
        elif param == 2:
            val_user = pan_to_user(quad[2])
            step_val = int(state.steps['pan'])
            if is_portamento(val_user):
                parts = val_user.split('.')
                p1, p2 = int(parts[0]), int(parts[1])
                if state.port_focus in (1, 3):
                    p1 = max(-100, min(100, p1 + direction * step_val))
                if state.port_focus in (2, 3):
                    p2 = max(-100, min(100, p2 + direction * step_val))
                quad[2] = user_to_pan(f"{p1}.{p2}")
            else:
                p = int(val_user)
                p = max(-100, min(100, p + direction * step_val))
                quad[2] = user_to_pan(str(p))
        elif param == 3:
            val_user = vol_to_user(quad[3])
            step_val = int(state.steps['vol'])
            if is_portamento(val_user):
                parts = val_user.split('.')
                v1, v2 = int(parts[0]), int(parts[1])
                if state.port_focus in (1, 3):
                    v1 = max(0, min(100, v1 + direction * step_val))
                if state.port_focus in (2, 3):
                    v2 = max(0, min(100, v2 + direction * step_val))
                quad[3] = user_to_vol(f"{v1}.{v2}")
            else:
                v = int(val_user)
                v = max(0, min(100, v + direction * step_val))
                quad[3] = user_to_vol(str(v))
    elif state.focus_type == 'adsr':
        param = state.focus_param
        val = state.preset['adsr'][param]
        step_key = ['a', 'd', 's', 'r'][param]
        step = state.steps[step_key]
        new_val = round(val + direction * step, 3)
        
        if param in (0, 1, 3):
            new_val = max(0.0, new_val)
            others = sum([state.preset['adsr'][i] for i in (0,1,3) if i != param])
            if new_val + others > 100.0:
                new_val = round(100.0 - others, 3)
        elif param == 2:
            new_val = max(0.0, min(100.0, new_val))
            
        state.preset['adsr'][param] = new_val

def edit_mode(coll, preset_name, nuovo=None):
    """L'editor di un preset. nuovo e' il preset appena nato dal tasto piu':
    non sta nella collezione, e ci entra soltanto se lo si salva."""
    state = EditorState(nuovo if nuovo is not None else coll.dati[preset_name])
    print(f"\nEditor del preset {preset_name}.")
    handle_print(state, force_newline=True)
    while True:
        modifica(state)
        print()
        if state.ciclo is not None:
            zittisci(state)
        # Esc nel menu di salvataggio torna all'editor: fino alla 1.10.0
        # scartava il lavoro senza chiedere, e Esc e' il tasto con cui si
        # era appena usciti dal preset (issue 59).
        if salva_preset(coll, preset_name, state, nuovo is not None) != "torna":
            return
        state.running = True
        print("Torno all'editor.")
        handle_print(state, force_newline=True)


def modifica(state):
    """Il giro dei tasti dell'editor, finche' non si esce con Esc."""
    while state.running:
        key = get_keypress()

        if key == 'space':
            zittisci(state)
            play_preset(state)
        elif key == 'k':
            zittisci(state)
            print(f"\r{' ' * 60}\rSilenzio", end="", flush=True)
            continue
        elif key == 't':
            print(f"\r{' ' * 60}\r{alterna_ciclo(state)}", end="", flush=True)
            continue
        elif key == 'o':
            # Il volume d'ascolto: la base su cui si sente il preset, come la
            # sceglie un programma con preset(volume=...). Fino alla 1.10.0
            # l'editor suonava sempre alla base 0,5 (issue 59).
            print("\nVolume d'ascolto, da 0 a 100: la base su cui si sente il preset, come la sceglie un programma.")
            print("Il preset non cambia. Invio senza scrivere niente torna a 50, la base del file.")
            scritto = input("\rVolume d'ascolto\r").strip()
            if not scritto:
                state.base_ascolto = None
            else:
                try:
                    state.base_ascolto = max(0.0, min(1.0, float(scritto) / 100.0))
                except ValueError:
                    print("Valore non valido.")
            play_preset(state)
            handle_print(state, force_newline=True)
            continue
        elif key == 'enter':
            param_name = ["Nota", "Durata", "Pan (-100..100)", "Volume (0..100)"][state.focus_param] if state.focus_type == 'score' else ["A", "D", "S", "R"][state.focus_param]
            if state.focus_type == 'score':
                if state.focus_param == 0 and is_rumore(state.preset.get('kind', 1)):
                    scelti = SCELTA_BANDA.get(state.port_focus, ())
                    if len(scelti) == 1:
                        param_name = f"{NOMI_SCELTA[state.port_focus]}, in Hz"
                    else:
                        param_name = ("Banda intera, per esempio 200-3000 oppure "
                                      "100-1000.800-1800, n, p")
                elif state.focus_param == 0:
                    current_val = state.preset['score'][state.focus_idx][0]
                    if is_portamento(current_val):
                        if state.port_focus == 1: param_name = "Nota (partenza)"
                        elif state.port_focus == 2: param_name = "Nota (arrivo)"
                        else: param_name = "Nota (entrambe)"
                elif state.focus_param == 2:
                    current_val = state.preset['score'][state.focus_idx][2]
                    if scorre(2, current_val):
                        if state.port_focus == 1: param_name = "Pan partenza (-100..100)"
                        elif state.port_focus == 2: param_name = "Pan arrivo (-100..100)"
                        else: param_name = "Pan entrambi (-100..100)"
                elif state.focus_param == 3:
                    current_val = state.preset['score'][state.focus_idx][3]
                    if scorre(3, current_val):
                        if state.port_focus == 1: param_name = "Volume partenza (0..100)"
                        elif state.port_focus == 2: param_name = "Volume arrivo (0..100)"
                        else: param_name = "Volume entrambi (0..100)"
                    
            val = input(f"\nInserisci nuovo valore per {param_name}: ")
            if val.strip() and riconferma(state, val.strip().lower()):
                # Riconfermare il valore mostrato non cambia niente: fino alla
                # 1.10.0 lo riscriveva arrotondato o riportato dentro la scala
                # dell'editor, e lo scarto 0,7 di un volume diventava 0,5
                # (issue 59).
                print("Valore invariato.")
            elif val.strip():
                try:
                    if state.focus_type == 'score':
                        if state.focus_param == 0 and is_rumore(state.preset.get('kind', 1)):
                            pezzi = list(banda_pezzi(state.preset['score'][state.focus_idx][0]))
                            scritto = val.strip()
                            scelti = SCELTA_BANDA.get(state.port_focus, ())
                            if not pezzi[1] or len(scelti) > 1 or '-' in scritto:
                                # Si sta scrivendo la banda intera
                                candidata = scritto
                            else:
                                pezzi[scelti[0]] = scritto
                                candidata = banda_componi(*pezzi)
                            # Si controlla prima di scrivere: una banda illeggibile
                            # resterebbe nel preset e farebbe cadere l'editor dopo.
                            pulita = normalizza_banda(candidata)
                            if pulita is None:
                                print("\nBanda non valida. Il trattino separa il "
                                      "taglio basso da quello alto, per esempio "
                                      "200-3000. Il punto separa la banda di "
                                      "partenza da quella d'arrivo, per esempio "
                                      "100-1000.800-1800. Vale anche n per nessuna "
                                      "banda e p per pausa. Il taglio basso deve "
                                      "restare sotto quello alto.")
                            else:
                                state.preset['score'][state.focus_idx][0] = pulita
                                state.modified = True
                        elif state.focus_param == 0:
                            # Dalla 1.11.0 una nota si controlla prima di entrare
                            # nel preset: un nome che non esiste, come h4, o un
                            # decimale dentro una scivolata, dove il punto separa
                            # i due capi, restavano nel file (issue 59).
                            current_val = state.preset['score'][state.focus_idx][0]
                            scritto = val.strip().lower()
                            if is_portamento(current_val):
                                if not capo_valido(scritto):
                                    print(AVVISO_CAPO)
                                else:
                                    parts = current_val.split('.')
                                    if state.port_focus in (1, 3): parts[0] = scritto
                                    if state.port_focus in (2, 3): parts[1] = scritto
                                    state.preset['score'][state.focus_idx][0] = f"{parts[0]}.{parts[1]}"
                                    state.modified = True
                            else:
                                nota = nota_scritta(scritto)
                                if nota is None:
                                    print(AVVISO_NOTA)
                                else:
                                    state.preset['score'][state.focus_idx][0] = nota
                                    state.modified = True
                        elif state.focus_param == 2:
                            current_val = state.preset['score'][state.focus_idx][2]
                            if scorre(2, current_val):
                                parts_user = pan_to_user(current_val).split('.')
                                if state.port_focus in (1, 3): parts_user[0] = val
                                if state.port_focus in (2, 3): parts_user[1] = val
                                state.preset['score'][state.focus_idx][2] = user_to_pan(f"{parts_user[0]}.{parts_user[1]}")
                            else:
                                state.preset['score'][state.focus_idx][2] = user_to_pan(val)
                            state.modified = True
                        elif state.focus_param == 3:
                            current_val = state.preset['score'][state.focus_idx][3]
                            if scorre(3, current_val):
                                parts_user = vol_to_user(current_val).split('.')
                                if state.port_focus in (1, 3): parts_user[0] = val
                                if state.port_focus in (2, 3): parts_user[1] = val
                                state.preset['score'][state.focus_idx][3] = user_to_vol(f"{parts_user[0]}.{parts_user[1]}")
                            else:
                                state.preset['score'][state.focus_idx][3] = user_to_vol(val)
                            state.modified = True
                        else:
                            durata = float(val)
                            if not durata > 0 or not math.isfinite(durata):
                                # Una durata negativa o nulla il motore la salta:
                                # la quartina sparirebbe senza che nessuno lo dica.
                                print("La durata e' in secondi, e serve piu' di zero.")
                            else:
                                state.preset['score'][state.focus_idx][1] = durata
                                state.modified = True
                    elif state.focus_type == 'adsr':
                        param = state.focus_param
                        new_val = float(val)
                        if param in (0, 1, 3):
                            new_val = max(0.0, new_val)
                            others = sum([state.preset['adsr'][i] for i in (0,1,3) if i != param])
                            if new_val + others > 100.0:
                                new_val = round(100.0 - others, 3)
                        elif param == 2:
                            new_val = max(0.0, min(100.0, new_val))
                        state.preset['adsr'][param] = new_val
                        state.modified = True
                except ValueError:
                    print("Valore non valido.")
            handle_print(state, force_newline=True)
            
        elif key == '.':
            if state.focus_type == 'score' and state.focus_param in (0, 2, 3):
                param_idx = state.focus_param
                val = state.preset['score'][state.focus_idx][param_idx]
                if param_idx == 0 and is_rumore(state.preset.get('kind', 1)):
                    # Su una banda il punto sdoppia la banda in partenza e
                    # arrivo, o la richiude. Senza questo ramo la banda
                    # verrebbe presa per un valore singolo e duplicata.
                    nuova = alterna_scivolata(val)
                    if nuova != str(val).strip():
                        state.preset['score'][state.focus_idx][0] = nuova
                        state.port_focus = 3
                        state.modified = True
                elif scorre(param_idx, val):
                    if param_idx == 0:
                        parts = val.split('.')
                        new_val = parts[0] if state.port_focus in (1, 3) else parts[1]
                        if new_val.replace('-', '').replace('.', '', 1).isdigit():
                            fval = float(new_val)
                            new_val = int(fval) if fval.is_integer() else fval
                        state.preset['score'][state.focus_idx][0] = new_val
                    elif param_idx == 2:
                        user_parts = pan_to_user(val).split('.')
                        new_val_str = user_parts[0] if state.port_focus in (1, 3) else user_parts[1]
                        state.preset['score'][state.focus_idx][2] = user_to_pan(new_val_str)
                    elif param_idx == 3:
                        user_parts = vol_to_user(val).split('.')
                        new_val_str = user_parts[0] if state.port_focus in (1, 3) else user_parts[1]
                        state.preset['score'][state.focus_idx][3] = user_to_vol(new_val_str)
                else:
                    if param_idx == 0:
                        if isinstance(val, float) and val.is_integer(): val = int(val)
                        state.preset['score'][state.focus_idx][0] = f"{val}.{val}"
                    elif param_idx == 2:
                        u_val = pan_to_user(val)
                        state.preset['score'][state.focus_idx][2] = user_to_pan(f"{u_val}.{u_val}")
                    elif param_idx == 3:
                        u_val = vol_to_user(val)
                        state.preset['score'][state.focus_idx][3] = user_to_vol(f"{u_val}.{u_val}")
                    state.port_focus = 3
                state.modified = True
        elif key in ('1', '2', '3', '4', '5', '6', '7') and \
                state.focus_type == 'score' and state.focus_param == 0 and \
                is_rumore(state.preset.get('kind', 1)):
            # Sulla banda i numeri scelgono quale dei quattro valori muovere.
            # Da 4 in su hanno senso solo se la banda scorre davvero.
            scelta = int(key)
            pezzi = banda_pezzi(state.preset['score'][state.focus_idx][0])
            if scelta <= 3 or pezzi[2]:
                state.port_focus = scelta
                print(f"\r{' ' * 60}\r{NOMI_SCELTA[scelta]}", end="", flush=True)
            else:
                print(f"\r{' ' * 60}\rLa banda e' ferma: premi il punto per "
                      "farla scorrere", end="", flush=True)
            continue
        elif key in ('1', '2', '3'):
            if (state.focus_type == 'score' and state.focus_param in (0, 2, 3)
                    and scorre(state.focus_param, state.preset['score'][state.focus_idx][state.focus_param])):
                state.port_focus = int(key)
        elif key == '4':
            if state.focus_type == 'score' and state.focus_param in (0, 2, 3):
                param_idx = state.focus_param
                val = state.preset['score'][state.focus_idx][param_idx]
                if scorre(param_idx, val):
                    if param_idx == 0:
                        parts = val.split('.')
                        state.preset['score'][state.focus_idx][0] = f"{parts[1]}.{parts[0]}"
                    elif param_idx == 2:
                        u_parts = pan_to_user(val).split('.')
                        state.preset['score'][state.focus_idx][2] = user_to_pan(f"{u_parts[1]}.{u_parts[0]}")
                    elif param_idx == 3:
                        u_parts = vol_to_user(val).split('.')
                        state.preset['score'][state.focus_idx][3] = user_to_vol(f"{u_parts[1]}.{u_parts[0]}")
                    state.modified = True
        elif key == 'i':
            # Inverte la scivolata: quello che partiva arriva e viceversa.
            # Su una nota fa la stessa cosa del 4, che resta per abitudine.
            if state.focus_type == 'score' and state.focus_param in (0, 2, 3):
                param_idx = state.focus_param
                val = state.preset['score'][state.focus_idx][param_idx]
                if param_idx == 0 and is_rumore(state.preset.get('kind', 1)):
                    b_in, a_in, b_fi, a_fi = banda_pezzi(val)
                    if b_fi:
                        state.preset['score'][state.focus_idx][0] = banda_componi(
                            b_fi, a_fi, b_in, a_in)
                        state.modified = True
                elif scorre(param_idx, val):
                    if param_idx == 0:
                        parti = val.split('.')
                        state.preset['score'][state.focus_idx][0] = f"{parti[1]}.{parti[0]}"
                    elif param_idx == 2:
                        u = pan_to_user(val).split('.')
                        state.preset['score'][state.focus_idx][2] = user_to_pan(f"{u[1]}.{u[0]}")
                    elif param_idx == 3:
                        u = vol_to_user(val).split('.')
                        state.preset['score'][state.focus_idx][3] = user_to_vol(f"{u[1]}.{u[0]}")
                    state.modified = True
        elif key == 'y':
            if state.focus_type == 'score':
                curr_quad = list(state.preset['score'][state.focus_idx])
                state.preset['score'].insert(state.focus_idx + 1, curr_quad)
                state.focus_idx += 1
                state.modified = True
                print(f"\r{' ' * 50}\rDuplicata Sc.{state.focus_idx}", end="", flush=True)
                continue
        elif key in ('c', 'v'):
            avviso = inc_dec_value(state, 1 if key == 'c' else -1)
            if avviso:
                print(f"\r{' ' * 60}\r{avviso}", end="", flush=True)
                continue
        elif key == 'z': state.focus_param = (state.focus_param - 1) % 4
        elif key == 'x': state.focus_param = (state.focus_param + 1) % 4
        elif key == 'b':
            if state.focus_type == 'score':
                rumore = is_rumore(state.preset.get('kind', 1))
                param_key = ['banda' if rumore else 'note',
                             'dur', 'pan', 'vol'][state.focus_param]
                param_name = ["Banda (rapporto)" if rumore else "Nota", "Durata",
                              "Pan (-100..100)", "Volume (0..100)"][state.focus_param]
            else:
                param_key = ['a', 'd', 's', 'r'][state.focus_param]
                param_name = ["Attacco", "Decadimento", "Sustain", "Rilascio"][state.focus_param]
            val = input(f"\nInserisci nuovo step per {param_name} (attuale: {state.steps[param_key]}): ")
            if val.strip():
                try:
                    state.steps[param_key] = float(val)
                except ValueError:
                    print("Valore non valido.")
            handle_print(state, force_newline=True)
        elif key == 'n':
            if state.focus_type == 'score':
                rumore = is_rumore(state.preset.get('kind', 1))
                param_key = ['banda' if rumore else 'note',
                             'dur', 'pan', 'vol'][state.focus_param]
                defaults = [BANDA_DEFAULT if rumore else 'c4', 0.5, 0.0, 0.0]
                default_steps = [PASSO_BANDA if rumore else 10.0, 0.02, 10, 10]
                state.preset['score'][state.focus_idx][state.focus_param] = defaults[state.focus_param]
                state.steps[param_key] = default_steps[state.focus_param]
            else:
                param_key = ['a', 'd', 's', 'r'][state.focus_param]
                defaults = [0.002, 0.0, 100.0, 0.002]
                state.preset['adsr'][state.focus_param] = defaults[state.focus_param]
                state.steps[param_key] = 0.1
            state.modified = True
            
        elif key == 'm':
            ans = input("\nSei sicuro di voler svuotare questo preset (s/n)? ")
            if ans.lower().strip() == 's':
                state.preset['score'] = [['c4', 0.5, 0.0, 0.0]]
                state.preset['adsr'] = [0.002, 0.0, 100.0, 0.002]
                state.preset['kind'] = 1
                state.focus_type = 'score'
                state.focus_idx = 0
                state.focus_param = 0
                state.modified = True
                print("Preset svuotato.")
            handle_print(state, force_newline=True)
            continue
            
        elif key in ('w', 'W'):
            if key == 'w':
                nuova = (state.preset.get('kind', 1) % len(ONDE)) + 1
            else:
                # Dalla 1.11.0 l'onda si sceglie anche diretta, senza fare il
                # giro: per passare dalla triangolare alla sinusoide il giro
                # attraversava due volte il confine fra note e rumori (issue 59).
                print()
                scelta = menu({str(k): v for k, v in ONDE.items()}, p="Onda> ", show=True, ordered=False)
                nuova = int(scelta) if scelta else None
            if nuova is not None and nuova != state.preset.get('kind', 1):
                cambia_onda(state, nuova)
            if key == 'W':
                handle_print(state, force_newline=True)
            continue
        elif key in ('a', 'd', 's', 'r'):
            state.focus_type = 'adsr'
            state.focus_param = {'a':0, 'd':1, 's':2, 'r':3}[key]
        elif key == 'q':
            state.focus_type = 'score'
            state.focus_param = 0 # Torna alla Nota della quartina corrente
        elif key == 'f':
            state.focus_type = 'score'
            primo = BANDA_DEFAULT if is_rumore(state.preset.get('kind', 1)) else 'c4'
            new_quad = [primo, 0.5, 0.0, 0.0]
            state.preset['score'].insert(state.focus_idx, new_quad)
            state.modified = True
            print(f"\r{' ' * 50}\rIns. Sc.{state.focus_idx+1}", end="", flush=True)
            continue
        elif key == 'g':
            state.focus_type = 'score'
            if state.focus_idx > 0: state.focus_idx -= 1
            play_quad(state)
        elif key == 'h':
            state.focus_type = 'score'
            if state.focus_idx < len(state.preset['score']) - 1: state.focus_idx += 1
            play_quad(state)
        elif key == 'j':
            state.focus_type = 'score'
            # Su un rumore la quartina nuova porta una banda, come con f:
            # fino alla 1.10.0 j vi metteva c4, che il rumore non sa leggere.
            primo = BANDA_DEFAULT if is_rumore(state.preset.get('kind', 1)) else 'c4'
            new_quad = [primo, 0.5, 0.0, 0.0]
            state.preset['score'].insert(state.focus_idx + 1, new_quad)
            state.focus_idx += 1
            state.modified = True
            print(f"\r{' ' * 50}\rIns. Sc.{state.focus_idx+1}", end="", flush=True)
            continue
        elif key == 'e':
            if state.focus_type == 'score' and len(state.preset['score']) > 1:
                state.preset['score'].pop(state.focus_idx)
                if state.focus_idx >= len(state.preset['score']):
                    state.focus_idx = len(state.preset['score']) - 1
                state.modified = True
                print(f"\r{' ' * 50}\rEliminato. Ora Sc.{state.focus_idx+1}", end="", flush=True)
                continue
        elif key == 'p':
            print("\nPosizione d'ascolto: sposta tutto il preset fra i due altoparlanti, come farebbe il programma che lo suona.")
            print("Da -100, tutto a sinistra, a 100, tutto a destra. Due valori uniti dal punto, per esempio -100.100, lo fanno")
            print("scorrere da un lato all'altro lungo tutta la durata del preset.")
            print("Il panorama scritto nelle quartine non viene cancellato ma spostato, e si stringe soltanto quanto serve a non")
            print("uscire dai bordi: un suono che vola continua a volare, in uno spazio piu' stretto.")
            print("Il preset non cambia: e' solo il modo in cui lo stai ascoltando. Invio senza scrivere niente la toglie.")
            valore, errore = leggi_posizione(input("\rPosizione\r"))
            if errore:
                print(errore)
            else:
                state.posizione = valore
                if valore is None:
                    print("Posizione tolta: il preset torna a sentirsi dov'e' scritto.")
                else:
                    print(f"Posizione {pan_to_user(valore)}. Il preset non e' cambiato: con u la rendi sua.")
                play_preset(state)
            handle_print(state, force_newline=True)
            continue
        elif key == 'u':
            if state.posizione is None:
                print(f"\r{' ' * 60}\rNessuna posizione da unire", end="", flush=True)
                continue
            # La posizione entra nelle quartine e smette di essere solo un modo
            # di ascoltare: da qui in poi il preset porta con se' quello
            # spostamento, e chi lo suona potra' spostarlo ancora.
            piatto = []
            for q in state.preset['score']:
                piatto.extend(q)
            piatto = panorama_spostato(piatto, state.posizione)
            for i, q in enumerate(state.preset['score']):
                q[2] = pan_in_file(piatto[i * 4 + 2])
            state.posizione = None
            state.modified = True
            print(f"\r{' ' * 60}\rPosizione unita alle quartine", end="", flush=True)
            continue
        elif key == 'l':
            # Dalla 1.11.0 senza righe di trattini e senza la freccia, che NVDA
            # legge segno per segno: le regole di accessibilita' di Gabriele
            # vietano i separatori grafici (issue 59).
            print("\nLe quartine:")
            for i, q in enumerate(state.preset['score']):
                qui = ", qui" if i == state.focus_idx else ""
                print(f"{i+1}{qui}. Nota: {q[0]}, Dur: {q[1]}, Pan: {pan_to_user(q[2])}, Vol: {vol_to_user(q[3])}")
            handle_print(state, force_newline=True)
            continue
        elif key == '?':
            print("\nI tasti dell'editor:")
            print("Spazio: Riproduce l'intero preset, zittendo prima quello che suona")
            print("t: Suona il preset in ciclo, e lo ferma")
            print("k: Zittisce tutto")
            print("o: Volume d'ascolto, la base su cui si sente il preset, da 0 a 100")
            print("Invio: Modifica il valore selezionato. Riconfermare il valore mostrato non cambia niente")
            print(".: Attiva o disattiva il portamento del valore corrente")
            print("1, 2, 3: Fuoco sul portamento (1: part, 2: arr, 3: entrambi)")
            print("i: Inverte il portamento, partenza e arrivo si scambiano")
            print("4: Come i, sulle note, e resta per abitudine")
            print("y: Duplica la quartina corrente")
            print("c / v: Incrementa / Decrementa valore corrente")
            print("z / x: Passa al parametro precedente / successivo")
            print("b: Modifica il passo (step) per il parametro corrente")
            print("n: Ripristina valori di default per il parametro corrente")
            print("m: Svuota l'intero preset (imposta a default)")
            print("w: Cambia forma d'onda, otto in tutto: Seno, Quadra, Triangolare,")
            print("   Dente di Sega e i quattro rumori, bianco, rosa, marrone e azzurro.")
            print("   Con un rumore il primo campo della quartina non e' la nota ma la")
            print("   banda del filtro, per esempio 200-3000, oppure n per nessuna banda.")
            print("   Il trattino separa il taglio basso da quello alto. Il punto sdoppia")
            print("   la banda in partenza e arrivo, per esempio 100-1000.800-1800, che")
            print("   si legge parte come 100-1000 e diventa 800-1800.")
            print("   Sulla banda i numeri scelgono cosa muovono poi c e v:")
            print("   1 il basso di partenza, 2 l'alto di partenza, 3 la banda di")
            print("   partenza, 4 il basso d'arrivo, 5 l'alto d'arrivo, 6 la banda")
            print("   d'arrivo, 7 tutti e quattro i valori insieme.")
            print("   Da 4 in su hanno senso solo se la banda scorre davvero.")
            print("   I tagli si spostano per rapporto, non per Hertz, e restano")
            print("   sempre fra 20 e 20000 Hz. Il taglio basso non scavalca mai")
            print("   quello alto: c e v si fermano prima e lo dicono.")
            print("   Cambiando forma il primo campo si converte da solo: la nota")
            print("   diventa la banda larga un'ottava che le sta intorno e la banda")
            print("   diventa la nota piu' vicina al suo centro. La conversione perde")
            print("   qualcosa, dissolvenze, microtoni, scivolate in Hz, ma l'editor")
            print("   ricorda com'era: tornando indietro senza averla toccata, la")
            print("   quartina torna esattamente com'era.")
            print("W: Sceglie la forma d'onda diretta, senza fare il giro")
            print("a, d, s, r: Passa alla modifica dell'inviluppo ADSR")
            print("q: Passa alla modifica della quartina (Nota)")
            print("f / j: Inserisce nuova quartina prima / dopo quella corrente")
            print("g / h: Sposta il cursore alla quartina precedente / successiva e riproduce")
            print("e: Elimina la quartina corrente")
            print("p: Posizione d'ascolto, cioe' lo spostamento generale del panorama.")
            print("   Da -100 a 100, oppure due valori col punto come -100.100 per farlo")
            print("   scorrere da un lato all'altro lungo tutta la durata del preset.")
            print("   Sposta il panorama delle quartine invece di cancellarlo, e lo stringe")
            print("   solo quanto serve a non uscire dai bordi: un suono che vola continua")
            print("   a volare. Non tocca il preset, e' il modo in cui lo ascolti. Invio a")
            print("   vuoto la toglie. E' lo stesso spostamento che un programma ottiene")
            print("   con il parametro pan di Acusticator.play.")
            print("u: Unisce la posizione d'ascolto alle quartine, e da li' e' del preset")
            print("l: Mostra la lista completa delle quartine")
            print("?: Mostra questa lista di tasti rapidi")
            print("Esc: Esce dall'editor")
            handle_print(state, force_newline=True)
            continue
        elif key == 'esc':
            state.running = False

        if state.running:
            handle_print(state, force_newline=False)


def chiedi_conflitto(conflitti):
	"""Chiede che fare quando un campo e' cambiato anche sul disco: mio,
	disco, oppure None per annullare."""
	if conflitti == ["tolto"]:
		print("Mentre lavoravi, un altro programma ha tolto questo preset dalla collezione.")
		scelta = menu({"m": "Rimettilo con le tue modifiche", "d": "Lascialo tolto", "a": "Annulla"}, p="Tolto> ", show=True)
	else:
		quali = ", ".join(NOMI_CAMPI.get(c, c) for c in conflitti)
		print(f"Mentre lavoravi, un altro programma ha cambiato anche {quali} di questo preset.")
		scelta = menu({"m": "Tieni il tuo", "d": "Tieni quello del disco", "a": "Annulla"}, p="Conflitto> ", show=True)
	return {"m": "mio", "d": "disco"}.get(scelta)


def salva_preset(coll, preset_name, state, nuovo):
	"""Il salvataggio all'uscita dall'editor, scritto subito sul disco.

	Dalla 1.9.0 ogni scelta scrive il disco di adesso attraverso la
	collezione, vedi Collezione: Sovrascrivi fonde le proprie modifiche con
	quelle arrivate nel frattempo, Salva come sceglie il nome libero sul disco,
	e il preset nuovo del tasto piu' arriva sul disco soltanto qui."""
	if not state.modified:
		# Un preset nuovo lasciato com'era non entra nella collezione.
		return
	coll.ricarica()
	# Un suono che c'e' gia' non si salva, nemmeno con un altro nome:
	# la collezione e' condivisa e un doppione la ingrossa e basta.
	gemello = trova_gemello(coll.dati, state.preset, escludi=None if nuovo else preset_name)
	if gemello:
		print(f"Questo suono esiste gia' come '{gemello}'.")
		print("Sarebbe un doppione, quindi non lo salvo.")
		return
	print("\nModifiche rilevate. Scegli un'opzione, Esc torna all'editor:")
	if nuovo:
		scelte = {"1": "Salva il preset nuovo", "3": "Esci senza salvare"}
	else:
		scelte = {"1": "Sovrascrivi preset corrente", "2": "Salva come nuovo preset", "3": "Esci senza salvare"}
	scelta = menu(scelte, p="Salva> ", show=True)
	if scelta is None:
		# Esc, o Invio a vuoto: si torna a lavorare, niente e' perso. Si
		# scarta soltanto scegliendolo.
		return "torna"
	if scelta == "1" and not nuovo:
		if coll.sovrascrivi(preset_name, state.originale, state.preset, chiedi_conflitto):
			print(f"Preset '{preset_name}' aggiornato.")
		else:
			print("Preset non sovrascritto.")
	elif scelta in ("1", "2"):
		# Il nome che il preset ha gia' e' li' pronto: invio lo accetta.
		new_name = dgt(f"Nome breve [{preset_name}]: ", kind="s", smax=50, default=preset_name,
					   avvisi={"troppo_lunga": "Al massimo {massimo} caratteri, ne hai scritti {lunghezza}."})
		new_name = new_name.strip().replace(" ", "")[:50] or preset_name
		desc = state.preset.get('descrizione', '')
		# Con smax alto: dgt taglia a smax il predefinito, e fino alla 1.10.0
		# riconfermare con Invio una descrizione lunga la mozzava a 256
		# caratteri, firme Usato da comprese (issue 59).
		new_desc = dgt(f"Descrizione [{desc}]: ", kind="s", smax=LUNGHEZZA_DESCRIZIONE, default=desc,
					   avvisi={"troppo_lunga": "Al massimo {massimo} caratteri, ne hai scritti {lunghezza}."})
		state.preset['descrizione'] = new_desc
		if not nuovo and new_name == preset_name:
			# Lo stesso nome di un preset che c'e': e' una sovrascrittura.
			if coll.sovrascrivi(preset_name, state.originale, state.preset, chiedi_conflitto):
				print(f"Preset '{preset_name}' aggiornato.")
			else:
				print("Preset non sovrascritto.")
			return
		usato = coll.salva_nuovo(new_name, state.preset)
		if usato:
			print(f"Salvato come preset: '{usato}'.")
		else:
			print("Preset non salvato.")
	else:
		print("Modifiche ignorate.")

def _num(valore, decimali=1):
    """Un numero scritto all'italiana, con la virgola al posto del punto."""
    return f"{valore:.{decimali}f}".replace(".", ",")


def _perc(parte, tutto):
    """Quanto pesa una parte sul totale, in percentuale."""
    if not tutto:
        return "0,0%"
    return _num(parte * 100.0 / tutto) + "%"


def _tempo(secondi):
    """Una durata leggibile: sotto il minuto in secondi, sopra in minuti."""
    if secondi < 60:
        return _num(secondi) + " s"
    minuti = int(secondi // 60)
    return f"{minuti} min e {secondi - minuti * 60:.0f} s"


def _quartine(quante):
    """Il numero con il suo sostantivo, al singolare o al plurale."""
    return f"{quante} quartina" if quante == 1 else f"{quante} quartine"


def _riga(testo):
    """Una riga di statistica, spezzata dove ci sta senza tagliare parole."""
    print(textwrap.fill(testo, 72))


def statistiche(db):
    """Nove righe di numeri sulla collezione, per il gusto di leggerli."""
    if not db:
        print("La collezione e' vuota, niente da contare.")
        return
    quartine = 0
    durata = 0.0
    onde = {}
    scivola_nota = scivola_banda = scivola_pan = 0
    stereo_mobile = stereo_fermo = 0
    piu_lungo = piu_corto = piu_folto = None
    grave = acuto = None
    famiglie = {}
    for nome, dati in db.items():
        score = dati.get("score", [])
        kind = dati.get("kind", 1)
        rumore = is_rumore(kind)
        onde[kind] = onde.get(kind, 0) + 1
        famiglia = nome.split("_")[0].lower()
        famiglie[famiglia] = famiglie.get(famiglia, 0) + 1
        mia_durata = 0.0
        muove = fuori_centro = False
        for quartina in score:
            if not isinstance(quartina, list) or len(quartina) != 4:
                continue
            primo, dur, pan, _ = quartina
            quartine += 1
            try:
                mia_durata += float(dur)
            except (TypeError, ValueError):
                pass
            if scorre(2, pan):
                scivola_pan += 1
                muove = True
            else:
                try:
                    if abs(float(pan)) > 0.01:
                        fuori_centro = True
                except (TypeError, ValueError):
                    pass
            if rumore:
                if banda_pezzi(primo)[2]:
                    scivola_banda += 1
                continue
            momenti = str(primo).strip().lower().split(".")
            if is_portamento(primo) and len(momenti) == 2:
                scivola_nota += 1
            for momento in momenti:
                hz = nota_in_hz(momento)
                if hz is None:
                    continue
                grave = hz if grave is None or hz < grave else grave
                acuto = hz if acuto is None or hz > acuto else acuto
        durata += mia_durata
        stereo_mobile += 1 if muove else 0
        stereo_fermo += 1 if fuori_centro and not muove else 0
        if piu_lungo is None or mia_durata > piu_lungo[1]:
            piu_lungo = (nome, mia_durata)
        if piu_corto is None or mia_durata < piu_corto[1]:
            piu_corto = (nome, mia_durata)
        if piu_folto is None or len(score) > piu_folto[1]:
            piu_folto = (nome, len(score))
    quanti = len(db)
    intonate = sorted([(k, v) for k, v in onde.items() if not is_rumore(k)],
                      key=lambda x: -x[1])
    rumori = sorted([(k, v) for k, v in onde.items() if is_rumore(k)],
                    key=lambda x: -x[1])
    _riga(f"Collezione: {quanti} preset, {_quartine(quartine)}, "
          f"{_tempo(durata)} di suono.")
    _riga(f"In media {_num(quartine / quanti)} quartine e "
          f"{_num(durata / quanti, 2)} s a preset.")
    voci = [f"{ONDE[k]} {_perc(v, quanti)}" for k, v in intonate]
    _riga("Onde: " + (", ".join(voci) if voci else "nessuna") + ".")
    quanti_rumori = sum(v for _, v in rumori)
    voci = [f"{ONDE[k].split()[-1]} {v}" for k, v in rumori]
    _riga(f"Rumori: {quanti_rumori} preset ({_perc(quanti_rumori, quanti)})"
          + (", " + ", ".join(voci) if voci else "") + ".")
    _riga(f"Il piu' lungo e' {piu_lungo[0]}, {_tempo(piu_lungo[1])}.")
    _riga(f"Il piu' corto {piu_corto[0]}, {_tempo(piu_corto[1])}; "
          f"il piu' folto {piu_folto[0]}, {_quartine(piu_folto[1])}.")
    scivolate = scivola_nota + scivola_banda + scivola_pan
    _riga(f"Scivolate: {scivolate} su {quartine} quartine "
          f"({_perc(scivolate, quartine)}), {scivola_nota} note, "
          f"{scivola_banda} bande, {scivola_pan} pan.")
    _riga(f"Stereo in moto in {stereo_mobile} preset "
          f"({_perc(stereo_mobile, quanti)}), fermo fuori centro in "
          f"{stereo_fermo}.")
    regina = max(famiglie.items(), key=lambda x: x[1])
    coda = f"regina {regina[0]} con {regina[1]} ({_perc(regina[1], quanti)})."
    if grave and acuto:
        _riga(f"Note dal {hz_in_nota(grave)} al {hz_in_nota(acuto)}, "
              f"{_num(math.log2(acuto / grave))} ottave; famiglia " + coda)
    else:
        _riga("Nessuna nota da contare; famiglia " + coda)


def main():
    print(f"{APP_NAME} {VERSION}")
    print(f"Autori: {APP_AUTHOR} - {RELEASE_DATE}")

    # Dalla 1.11.0 si puo' aprire la collezione di un progetto, passandone il
    # percorso: Acu_Maker.py ..\Terminal_Beast\sounds.json (issue 59).
    percorso = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else DB_FILE
    coll = Collezione(percorso)
    if percorso != DB_FILE:
        print(f"Collezione {percorso}.")
    if not coll.apri():
        return
    print(f"La libreria contiene {len(coll.dati)} preset.")
    try:
        sessione(coll)
    except KeyboardInterrupt:
        # Dalla 1.9.0 ogni salvataggio e' gia' sul disco: interrompere non
        # perde niente.
        print("\nInterrotto. Cio' che hai salvato e' gia' nella collezione.")
        return
    # Come all'avvio, soltanto i doppioni: la collezione non si riscrive.
    coll.ricarica()
    coll.togli_doppioni()
    statistiche(coll.dati)
    print("Arrivederci!")


def sessione(coll):
    """Il menu dei preset, finche' non se ne esce."""
    while True:
        # Prima di ogni giro si guarda se qualcun altro ha scritto la
        # collezione, e la si rilegge.
        coll.ricarica()
        db = coll.dati
        # Ordiniamo esplicitamente il dizionario alfabeticamente per nome del preset
        menu_dict = {k: v.get("descrizione", "") for k, v in sorted(db.items())}
        menu_dict["+"] = "Nuovo preset vuoto (Default)"
        menu_dict["/"] = "Cerca preset per parola chiave"
        menu_dict["!"] = "Apri un'altra collezione"
        menu_dict["*"] = "Scegli la scheda audio"
        print("\nScegli un preset (digita '?' per la lista, Esc/Invio vuoto per uscire):")
        scelta = menu(d=menu_dict, p="Preset> ", show=False, ordered=True)

        if not scelta:
            break

        if scelta == "!":
            apri_collezione(coll)
            continue

        if scelta == "*":
            scegli_scheda()
            continue

        if scelta == "+":
            # Il preset nuovo resta nell'editor: entra nella collezione
            # soltanto se lo si salva.
            new_name = get_unique_name(db, "nuovo_preset")
            edit_mode(coll, new_name, nuovo={
                "descrizione": "Nuovo preset vuoto",
                "score": [["c4", 0.5, 0.0, 0.0]],
                "kind": 1,
                "adsr": [0.002, 0.0, 100.0, 0.002]
            })
            continue

        if scelta == "/":
            query = input("\nInserisci parole chiave da cercare (spazio per separare): ").strip().lower()
            if not query:
                continue
            words = query.split()

            risultati = {}
            for k, v in sorted(db.items()):
                test_str = (k + " " + v.get("descrizione", "")).lower()
                if all(w in test_str for w in words):
                    risultati[k] = v.get("descrizione", "")
                    
            if not risultati:
                print("Nessun preset trovato corrispondente alla ricerca.")
                continue
            elif len(risultati) == 1:
                scelta = next(iter(risultati))
                print(f"\nTrovato 1 preset: '{scelta}'")
            else:
                print(f"\nTrovati {len(risultati)} preset. Scegli uno (Esc/Invio per annullare):")
                scelta = menu(d=risultati, p="Risultati> ", show=True, ordered=True)
                if not scelta:
                    continue

        print(f"\nHai selezionato: '{scelta}'")
        action_dict = {"c": "Carica (Edit Mode)", "e": "Elimina", "r": "Rinomina", "d": "Cambia la descrizione"}
        azione = menu(d=action_dict, p="Azione> ", show=True)
        # Prima di entrare nel preset, la collezione di adesso.
        coll.ricarica()
        if azione is not None and scelta not in coll.dati:
            print(f"Il preset '{scelta}' non c'e' piu': l'ha tolto un altro programma.")
            continue

        if azione == "e":
            if input(f"Sei sicuro di voler eliminare '{scelta}'? (s/n): ").lower() == 's':
                # Dal disco si toglie soltanto lui.
                if coll.elimina(scelta):
                    print("Preset eliminato.")
                else:
                    print("Preset non eliminato.")
        elif azione == "c":
            edit_mode(coll, scelta)
        elif azione == "r":
            rinomina(coll, scelta)
        elif azione == "d":
            cambia_descrizione(coll, scelta)

if __name__ == "__main__":
    main()
