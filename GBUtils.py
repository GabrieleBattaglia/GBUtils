'''
	GBUtils di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5)
	Data concepimento: lunedì 3 febbraio 2020.
	Raccoglitore di utilità per i miei programmi.
	Spostamento su github in data 27/6/2024. Da usare come submodule per gli altri progetti.
	V161 di lunedì 14 settembre 2026
Indice delle utilità del pacchetto: nome, versione, data, autori. Che cosa fa ognuna, e come si chiama, sta nella sua docstring.
	accorcia V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	Acusticator V8.2.0 di domenica 13 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	cartella_applicazione V1.0.0 di sabato 12 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	contesto_ssl V1.0.0 di martedì 8 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, modalità auto)
	crea_archivio_release V1.1.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	CWzator V11.3.0 di domenica 13 settembre 2026 - Gabriele Battaglia (IZ4APU), Stella/Gemini 3.5 Flash & ClaudIA (Claude Opus 5, UltraCode)
	dgt V2.0.0 di lunedì 7 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	Donazione V2.1.0 di venerdì 11 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode)
	elenco_dispositivi_audio V1.0.0 di domenica 13 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	elenco_interfacce_audio V1.0.0 di domenica 13 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	enter_escape V2.0.0 di venerdì 11 settembre 2026 - Gabriele Battaglia (IZ4APU), Gemini 2.5 Pro & ClaudIA (Claude Fable 5.1, UltraCode)
	formatta_dimensione V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	formatta_durata V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	frequenza_nota V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	gestisci_aggiornamento V1.2.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	key V8.0.2 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU), Stella/Gemini 3.5 Flash & ClaudIA (Claude Opus 5, modalità auto)
	lingua_di_sistema V1.0.0 di sabato 12 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	manuale V2.1.0 di venerdì 11 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode)
	Mazzo V6.1.0 di martedì 8 settembre 2026 - Gabriele Battaglia (IZ4APU), Gemini 2.5 & ClaudIA (Claude Fable 5.1, UltraCode)
	menu V5.1.0 di venerdì 11 settembre 2026 - Gabriele Battaglia (IZ4APU), Stella Gemini 3.5 Flash & ClaudIA (Claude Fable 5.1, UltraCode)
	percorso_risorsa V1.0.0 di sabato 12 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	perform_update V1.6.1 di martedì 8 settembre 2026 - Gabriele Battaglia (IZ4APU) & Stella, poi ClaudIA (Claude Fable 5.1, modalità auto)
	polipo V6.1.0 del 18 luglio 2025 - Gabriele Battaglia (IZ4APU) & Gemini, poi ClaudIA (Claude Opus 5, modalità auto) il 4 settembre 2026
	pulisci_residui V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	scegli_dispositivo_audio V1.0.0 di domenica 6 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	scomponi_nota V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	sonify V8.0.0 di martedì 8 settembre 2026 - Gabriele Battaglia (IZ4APU), Stella, Gemini 3 Pro & ClaudIA (Claude Fable 5.1, modalità auto)
	Tastiera V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	update_checker V1.7.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
'''
VERSION = "161"
# Il contesto SSL condiviso da tutte le connessioni sicure: si costruisce alla
# prima richiesta, perche' caricare gli archivi dei certificati costa.
_CONTESTO_SSL = None
def _parse_version(version_str: str) -> tuple | None:
    """Helper interno per il parsing semantico della versione.
    Restituisce None quando nella stringa non c'e' nessun numero. Prima in quel
    caso rispondeva (0,), che paragonata a qualunque release la faceva sembrare
    piu' recente: una versione scritta male avrebbe fatto proporre
    l'aggiornamento a ogni avvio, senza modo di farlo smettere."""
    import re
    # Estrae solo i numeri separati da punti, ignorando prefissi come 'v'
    match = re.search(r'(\d+(?:\.\d+)*)', version_str or "")
    if not match:
        return None
    return tuple(map(int, match.group(1).split('.')))

def _cartella_chiamante(risalita: int = 1) -> str:
    """Cartella su cui un'utilita' deve risolvere i propri percorsi relativi.
    Se il programma e' congelato con PyInstaller e' quella dell'eseguibile;
    altrimenti e' quella del file che ha chiamato l'utilita', ricavata
    risalendo di risalita livelli nella pila delle chiamate: risalita vale 1
    per chi la invoca direttamente dal corpo di una utilita' pubblica.
    La directory di lavoro corrente resta soltanto come ultima risorsa,
    perche' non ha alcun rapporto con la posizione dell'applicazione."""
    import os
    import sys

    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    try:
        return os.path.dirname(os.path.abspath(sys._getframe(risalita + 1).f_globals["__file__"]))
    except (AttributeError, KeyError, ValueError):
        return os.getcwd()

def cartella_applicazione(risalita: int = 0) -> str:
	"""V1.0.0 di sabato 12 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	La cartella su cui un'applicazione costruisce i propri percorsi: quella
	dell'eseguibile quando e' compilata con PyInstaller, quella del file che
	chiama altrimenti. Mai la directory di lavoro, che dipende da come il
	programma e' stato avviato e non da dove sta: resta soltanto come ultima
	risorsa, quando il file di chi chiama non si riesce a determinare.
	E' il posto dei file che l'applicazione scrive, cioe' salvataggi,
	impostazioni, log e report. Per i file che l'applicazione legge soltanto, e
	che da compilata viaggiano dentro il pacchetto, c'e' percorso_risorsa.
	risalita dice di quanti livelli salire nella pila delle chiamate: zero, il
	predefinito, da' la cartella di chi chiama direttamente; uno da' quella di
	chi ha chiamato lui, e serve a chi avvolge questa funzione in una propria,
	per esempio in un modulo dei percorsi che sta in una sottocartella e deve
	rispondere per il programma intero.
	Nasce con la V138 dalla issue 20: la stessa logica era riscritta in dieci
	progetti del parco software, con nomi diversi e qualita' diverse.
	"""
	return _cartella_chiamante(risalita + 1)

def percorso_risorsa(nome_file: str, risalita: int = 0) -> str:
	"""V1.0.0 di sabato 12 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	Dove sta un file in sola lettura che viaggia con l'applicazione, per
	esempio il manuale o la guida. Un percorso assoluto torna com'e'. Uno
	relativo si cerca prima fra le risorse del pacchetto PyInstaller, in
	sys._MEIPASS, quando il programma e' compilato, perche' i file dichiarati
	nei datas vengono scompattati li' e non accanto all'eseguibile; poi nella
	cartella di chi chiama, secondo cartella_applicazione. Se non esiste in
	nessuno dei due torna quello nella cartella di chi chiama, cosi' che
	l'errore di chi lo apre dica dove lo si aspettava.
	risalita ha lo stesso significato che in cartella_applicazione.
	Nasce con la V134 come funzione privata per manuale, e con la V138 diventa
	pubblica insieme a cartella_applicazione, per la issue 20.
	"""
	return _percorso_risorsa(nome_file, risalita + 1)

def _nome_da_api(api_url: str) -> str:
    """Ricava il nome del repository da un indirizzo dell'API di GitHub.
    Serve solo a firmare le righe del log: se non lo riconosce non insiste."""
    parti = [p for p in str(api_url).split('/') if p]
    if 'repos' in parti:
        i = parti.index('repos')
        if len(parti) > i + 2:
            return parti[i + 2]
    return "applicazione sconosciuta"

def lingua_di_sistema() -> str | None:
    """V1.0.0 di sabato 12 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
    La lingua dell'utente, come codice di due o tre lettere minuscole, per
    esempio it, en o pt; None quando non si riesce a capirla.
    Prova nell'ordine le variabili d'ambiente, che sono una scelta esplicita di
    chi usa il programma, poi l'API di Windows, poi locale.getlocale.
    Non chiama locale.getdefaultlocale, deprecata e in uscita con Python 3.15:
    non serve piu' perche' ripete quello che gia' fanno i due passaggi
    precedenti, cioe' leggere le variabili d'ambiente su Unix e interrogare
    Windows sulle altre macchine. E' questa la ragione per cui la funzione
    esiste ed e' pubblica dalla V139: chi la usa al posto di getdefaultlocale
    non ha nulla da riscrivere quando quella sparira'.
    Il paese non torna mai: da it_IT, it-IT o Italian_Italy si arriva sempre a
    it, e un valore che non sia un codice di lingua viene scartato. Chi ha
    bisogno del paese lo chieda al sistema per conto proprio.
    Restituisce None quando non c'e' niente di leggibile, quindi chi la chiama
    deve avere una lingua di ripiego, di solito quella in cui il programma e'
    scritto. Non solleva e non stampa niente.
    """
    import locale
    import os
    import sys

    def pulisci(valore):
        """Da it_IT.UTF-8, it-IT o it si arriva sempre a it.
        Italian_Italy, che e' cio' che locale.getlocale restituisce su Windows,
        non e' un codice di lingua e viene scartato: chi lo tagliasse al primo
        trattino basso otterrebbe italian, e con quello nessuna traduzione
        verrebbe piu' trovata."""
        if not valore:
            return None
        codice = str(valore).split(':')[0].split('.')[0].split('_')[0].split('-')[0].strip().lower()
        return codice if codice.isalpha() and 2 <= len(codice) <= 3 else None

    for var in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
        codice = pulisci(os.environ.get(var))
        if codice:
            return codice
    if sys.platform == 'win32':
        try:
            import ctypes
            nome = locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage())
            codice = pulisci(nome)
            if codice:
                return codice
        except Exception:  # noqa: BLE001, S110 - se l'API di Windows non risponde si prova il resto
            pass
    try:
        coppia = locale.getlocale()
        codice = pulisci(coppia[0] if coppia else None)
        if codice:
            return codice
    except (TypeError, ValueError):
        pass
    return None

# Il nome storico, con cui la chiamano polipo e Donazione qui dentro: resta
# perche' la funzione era privata fino alla V138, e cambiare i due usi interni
# non aggiungerebbe niente.
_lingua_di_sistema = lingua_di_sistema

def _write_update_log(message: str, cartella: str | None = None, app: str | None = None):
    """Registra un errore dell'aggiornamento accanto all'applicazione.
    La cartella e il nome vengono passati da chi chiama, che li conosce: se
    mancano si ripiega sulla directory di lavoro, che e' il vecchio
    comportamento e non dice a quale programma appartenga il guasto."""
    import os
    import sys
    import traceback
    from datetime import datetime

    LIMITE_LOG = 100_000
    try:
        base_dir = cartella if cartella else _cartella_chiamante(2)
        log_path = os.path.join(base_dir, "auto_updater_error.log")
        # Il file non deve crescere senza fine su un'installazione che
        # incontri spesso l'errore: oltre il limite si riparte da capo.
        modo = "a"
        try:
            if os.path.getsize(log_path) > LIMITE_LOG:
                modo = "w"
        except OSError:
            pass
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ005 - ora locale: il log lo legge chi sta davanti alla macchina
        nome = app if app else "applicazione non dichiarata"
        # Il traceback si scrive solo se c'e' davvero un'eccezione in corso,
        # altrimenti format_exc riempirebbe il log di righe NoneType: None.
        traccia = traceback.format_exc() if sys.exc_info()[0] is not None else ""
        with open(log_path, modo, encoding="utf-8") as f:
            if modo == "w":
                f.write("Log ripartito da capo perche' aveva superato i cento kilobyte.\n")
            f.write(f"Errore del {timestamp}, applicazione {nome}.\n")
            f.write(f"{message}\n")
            if traccia:
                f.write(f"{traccia}\n")
    except Exception as e:  # noqa: BLE001 - un log che non si scrive non deve fermare il programma
        # Nelle applicazioni compilate senza console stdout non esiste e print
        # non scriverebbe da nessuna parte; stderr puo' mancare a sua volta.
        try:
            sys.stderr.write(f"Impossibile scrivere il log dell'aggiornamento: {e}\n")
        except Exception:  # noqa: BLE001, S110 - senza stderr non resta niente da fare
            pass

_NOME_MANIFESTO = "manifesto.txt"

def pulisci_residui(cartella: str | None = None, app: str | None = None) -> int:
    """
    V1.0.0 di lunedì 14 settembre 2026 by Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
    Toglie da _internal quello che la versione precedente si e' lasciata dietro.
    Gli aggiornamenti applicati dalle perform_update fino alla V1.4 copiavano la
    versione nuova sopra la vecchia senza cancellare niente, quindi cio' che
    stava in _internal e nella versione nuova non c'e' piu' resta sul disco.
    Quasi sempre e' innocuo, ma una cartella di pacchetto rimasta con dentro il
    solo binario Python la importa lo stesso, come pacchetto namespace, e fa
    ombra al modulo vero: e' successo con simplejson, e requests ha smesso di
    partire. Per questo la pulizia va fatta prima di qualunque importazione che
    possa toccare i residui, ed e' la prima cosa che fa update_checker.
    Si regola sul manifesto che crea_archivio_release scrive nel pacchetto: cio'
    che sta in _internal e non e' elencato li' viene dalla versione precedente.
    Non tocca mai niente fuori da _internal, dove vivono salvataggi,
    impostazioni e log dell'utente, e non fa niente in tre casi: quando si gira
    da sorgente, quando il pacchetto e' in un pezzo solo e quindi _internal non
    esiste, e quando il manifesto non c'e' perche' il pacchetto e' anteriore.
    Rinuncia anche quando il manifesto non descrive questa installazione, cioe'
    quando un file elencato non e' sul disco: il manifesto viaggia insieme ai
    file, quindi se ne manca uno non sono la stessa cosa, e cancellare sarebbe
    un azzardo. Meglio lasciare i residui che togliere cio' che serve.
    cartella e' l'installazione, quella che contiene _internal; se manca si usa
    quella dell'eseguibile. app da' il nome all'eventuale riga di log.
    Restituisce quanti elementi ha tolto, file e cartelle rimaste vuote. Gli
    errori sui singoli file, per esempio uno in uso, non fermano la pulizia: si
    scrivono nel log dell'aggiornamento e si va avanti con gli altri.
    """
    import os
    import sys

    if cartella is None:
        if not getattr(sys, "frozen", False):
            return 0
        cartella = os.path.dirname(sys.executable)
    interna = os.path.join(cartella, "_internal")
    if not os.path.isdir(interna):
        return 0
    percorso_manifesto = os.path.join(interna, _NOME_MANIFESTO)
    if not os.path.isfile(percorso_manifesto):
        return 0
    nome_app = app or os.path.basename(os.path.abspath(cartella))
    try:
        with open(percorso_manifesto, encoding="utf-8") as f:
            righe = f.read().splitlines()
    except OSError as e:
        _write_update_log(f"Manifesto del pacchetto illeggibile, pulizia dei residui saltata: {e}", cartella, nome_app)
        return 0
    # Le righe di commento servono a chi apre il file per capire che cos'e':
    # senza saltarle verrebbero prese per nomi di file mancanti e basterebbero
    # a far rinunciare la pulizia.
    elencati = {riga.strip().replace("\\", "/").lower() for riga in righe
                if riga.strip() and not riga.lstrip().startswith("#")}
    if not elencati:
        _write_update_log("Manifesto del pacchetto senza nemmeno un file elencato, pulizia dei residui saltata.", cartella, nome_app)
        return 0
    elencati.add(_NOME_MANIFESTO)

    presenti = {}
    for radice, _cartelle, file in os.walk(interna):
        dentro = os.path.relpath(radice, interna)
        for nome in file:
            relativo = nome if dentro == "." else os.path.join(dentro, nome)
            presenti[relativo.replace("\\", "/").lower()] = os.path.join(radice, nome)

    mancanti = elencati - set(presenti)
    if mancanti:
        campione = ", ".join(sorted(mancanti)[:5])
        _write_update_log(
            f"Il manifesto non descrive questa installazione: {len(mancanti)} file elencati non ci sono, "
            f"fra cui {campione}. Pulizia dei residui saltata, non e' stato toccato niente.",
            cartella, nome_app)
        return 0

    tolti = 0
    guai = []
    for chiave in sorted(set(presenti) - elencati):
        try:
            os.remove(presenti[chiave])
            tolti += 1
        except OSError as e:
            guai.append(f"{chiave}: {e}")
    # Dal fondo verso la radice, cosi' una cartella che conteneva solo residui
    # sparisce insieme a loro. _internal non si tocca: e' la casa, non un resto.
    for radice, _cartelle, _file in os.walk(interna, topdown=False):
        if os.path.abspath(radice) == os.path.abspath(interna):
            continue
        try:
            if not os.listdir(radice):
                os.rmdir(radice)
                tolti += 1
        except OSError as e:
            guai.append(f"{os.path.relpath(radice, interna)}: {e}")
    if guai:
        _write_update_log(
            f"Pulizia dei residui: {len(guai)} elementi non rimossi, "
            f"il programma funziona lo stesso. " + "; ".join(guai),
            cartella, nome_app)
    return tolti

def update_checker(current_version: str, api_url: str, timeout: int = 10, cartella_log: str | None = None) -> tuple[bool, str | None, str | None, str | None]:
    """
    V1.7.0 di lunedì 14 settembre 2026 by Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
    Controlla l'ultima release di un repository GitHub e la confronta con la versione corrente.
    Prima di ogni altra cosa chiama pulisci_residui, perche' un pacchetto
    svuotato dalla versione precedente farebbe fallire l'importazione di
    requests, poche righe piu' sotto, e con lei il controllo aggiornamenti.
    Registra gli errori su file, tranne l'assenza di connessione, che e' un evento
    normale e non un guasto del programma.
    La verifica dei certificati non viene mai disattivata: se il certificato non e'
    accettato, il controllo rinuncia e lo scrive nel log.
    Il log nasce accanto all'applicazione che ha chiamato, non nella directory di
    lavoro, ed e' firmato con il nome del repository interrogato.
    timeout e' il tempo massimo di attesa in secondi. Chi fa il controllo in linea
    prima di avviarsi, e non in un thread, puo' abbassarlo: quei secondi sono un
    silenzio in cui l'utente non sa se il programma stia lavorando o sia fermo.
    """
    # Ricavati subito, perche' servono anche se l'import di requests fallisce.
    # cartella_log arriva da chi chiama quando la catena passa per un'altra
    # utilita' di GBUtils: risalire di un livello solo, in quel caso,
    # scriverebbe il log nella cartella della libreria invece che in quella
    # dell'applicazione.
    cartella_log = cartella_log or _cartella_chiamante(1)
    nome_app = _nome_da_api(api_url)
    # Prima di importare qualunque cosa: un aggiornamento fatto dagli script
    # fino alla V1.4 puo' aver lasciato in _internal un pacchetto svuotato che
    # fa ombra a quello vero, e requests e' il primo a inciamparci. La pulizia
    # sta qui e non anche in gestisci_aggiornamento, che passa comunque di qua
    # subito dopo: due volte vorrebbe dire censire _internal due volte a ogni
    # avvio.
    pulisci_residui(app=nome_app)
    try:
        # Fuori da questo try, un import rotto (es. una dipendenza di
        # requests compilata male) farebbe cadere tutto il programma a
        # ogni avvio invece di limitarsi a saltare il controllo aggiornamenti.
        import requests
    except ImportError as e:
        _write_update_log(f"Impossibile importare requests: {e}", cartella_log, nome_app)
        return False, None, None, None
    current_version = current_version.split(' ')[0]
    try:
        try:
            response = requests.get(api_url, timeout=timeout)
        except requests.exceptions.SSLError as e:
            # Nessun ritento senza verifica: questa risposta stabilisce da
            # quale indirizzo perform_update scarichera' l'eseguibile, quindi
            # accettare un certificato qualunque lascerebbe scegliere quel
            # file a chi sappia interporsi sulla connessione. Un errore SSL,
            # oggi, quasi sempre non e' un guasto ma un antivirus o un proxy
            # che ispeziona il traffico: va segnalato, non aggirato.
            _write_update_log(f"Certificato non accettato dal controllo aggiornamenti: {e}", cartella_log, nome_app)
            return False, None, None, None
        response.raise_for_status()
        data = response.json()
        latest_version = data.get("tag_name")
        if not latest_version:
            _write_update_log("Nessun tag_name trovato nella risposta JSON di GitHub.", cartella_log, nome_app)
            return False, None, None, None
        
        changelog = data.get("body")

        current_tuple = _parse_version(current_version)
        latest_tuple = _parse_version(latest_version)
        if current_tuple is None or latest_tuple is None:
            # Senza due numeri da confrontare non si dichiara nessun
            # aggiornamento: dirlo lo stesso significherebbe riproporlo a ogni
            # avvio, e chi lo riceve non avrebbe modo di farlo smettere.
            _write_update_log(
                f"Versione non riconosciuta, confronto saltato. Corrente: {current_version!r}, pubblicata: {latest_version!r}.",
                cartella_log, nome_app)
            return False, latest_version, None, None

        if latest_tuple > current_tuple:
            # L'allegato si sceglie per nome e non per posizione: se un giorno
            # una release avesse due file, prendere il primo caricato
            # significherebbe scaricare a caso.
            assets = data.get("assets") or []
            scelto = next((a for a in assets if str(a.get("name", "")).lower().endswith(".zip")), None)
            if scelto is None and assets:
                scelto = assets[0]
            download_url = scelto.get("browser_download_url") if scelto else None
            return True, latest_version, download_url, changelog
        else:
            return False, latest_version, None, None
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Assenza di rete / DNS fallito: evento di rete fisiologico, non scriviamo il traceback nel file di log.
        return False, None, None, None
    except requests.exceptions.HTTPError as e:
        stato = e.response.status_code if e.response is not None else None
        if stato in (403, 404, 429):
            # 403 e 429 sono il limite di chiamate all'ora di GitHub, che si
            # incontra avviando piu' applicazioni di seguito sulla stessa
            # connessione; 404 e' il repository che non ha ancora nessuna
            # release. Sono eventi normali quanto l'assenza di rete, e come
            # quella non meritano un file di errore dall'aria allarmante.
            return False, None, None, None
        _write_update_log(f"Risposta di errore da GitHub: {e}", cartella_log, nome_app)
        return False, None, None, None
    except Exception as e:  # noqa: BLE001 - qualunque guasto del controllo aggiornamenti deve restare confinato qui
        _write_update_log(f"Errore durante il controllo aggiornamenti: {e}", cartella_log, nome_app)
        return False, None, None, None

def contesto_ssl():
    """
    V1.0.0 di martedì 8 settembre 2026 by Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, modalità auto)
    Contesto SSL con cui il parco software apre le connessioni sicure di urllib.
    Verifica i certificati con l'archivio del sistema e, in aggiunta, con il
    pacchetto certifi che arriva insieme a requests. Le due fonti coprono guai
    diversi: l'archivio di Windows conosce le radici installate da antivirus e
    proxy, ma le altre le scarica soltanto quando un programma Microsoft le
    incontra, e OpenSSL non lo fa mai; certifi le ha tutte dalla nascita, ma
    non sa niente di quello che l'utente ha installato.
    Con il solo archivio di sistema, su un PC dove nessun programma Microsoft
    aveva mai incontrato la radice di GitHub, urllib rifiutava api.github.com
    con "unable to get local issuer certificate" mentre requests, che usa
    certifi, passava: e' la issue 40 di Orologic, e lo stesso sarebbe successo
    a perform_update al momento di scaricare l'aggiornamento.
    La verifica non viene mai disattivata. Se certifi manca resta il solo
    archivio di sistema. Il contesto si costruisce una volta e si riusa.
    Uso: urllib.request.urlopen(url, context=contesto_ssl())
    """
    import ssl
    global _CONTESTO_SSL
    if _CONTESTO_SSL is None:
        contesto = ssl.create_default_context()
        try:
            import certifi
            contesto.load_verify_locations(cafile=certifi.where())
        except (ImportError, OSError):
            pass
        _CONTESTO_SSL = contesto
    return _CONTESTO_SSL

def _scarica(url: str, destinazione: str, avanzamento=None, timeout: int = 30) -> int:
    """Scarica un file e restituisce i byte presi, avvisando man mano.
    Sta fuori da perform_update perche' cosi' si puo' provare senza dover
    aggiornare davvero un programma.
    Legge a blocchi invece di usare urlretrieve, che non accetta un tempo
    massimo: una connessione che si impianta senza chiudersi lasciava il
    programma appeso per sempre. La verifica dei certificati resta attiva, e
    passa da contesto_ssl: questo e' l'unico punto in cui il parco software
    prende dalla rete codice che poi verra' eseguito."""
    import urllib.request

    scaricato = 0
    ultima_percentuale = -1
    with urllib.request.urlopen(url, timeout=timeout, context=contesto_ssl()) as risposta:
        try:
            totale = int(risposta.headers.get("Content-Length") or 0)
        except (TypeError, ValueError):
            totale = 0
        with open(destinazione, "wb") as f:
            while True:
                blocco = risposta.read(65536)
                if not blocco:
                    break
                f.write(blocco)
                scaricato += len(blocco)
                if avanzamento:
                    # Si avvisa al cambio di punto percentuale, non a ogni
                    # blocco: mille annunci al secondo non li ascolta nessuno,
                    # e con lo screen reader sarebbero un muro di parole.
                    percentuale = int(scaricato * 100 / totale) if totale else -1
                    if percentuale != ultima_percentuale:
                        ultima_percentuale = percentuale
                        avanzamento(scaricato, totale)
    if totale and scaricato != totale:
        raise OSError(f"scaricati {scaricato} byte invece di {totale}, download incompleto")
    return scaricato

def _script_aggiornamento(app_name, exe_name, current_exe, current_dir, source_dir,
                          temp_dir, zip_path, log_path, pulisci_internal=False,
                          attesa_massima=30) -> str:
    """Compone lo script batch che sostituisce l'installazione.
    Sta fuori da perform_update perche' cosi' si puo' provare senza dover
    aggiornare davvero un programma.
    Lo script aspetta che l'applicazione si sia chiusa per davvero, invece di
    contare tre secondi e sperare; controlla l'esito della copia; se qualcosa
    va storto non cancella l'archivio scaricato, rimette a posto la cartella
    _internal e lascia scritto nel log perche' l'aggiornamento non e' arrivato.
    In ogni caso riavvia l'applicazione, che dopo un fallimento e' ancora
    quella integra di prima.
    Quando pulisci_internal e' vero la vecchia _internal viene messa da parte
    prima della copia e cancellata solo a copia riuscita: e' l'unica cartella
    prodotta interamente da PyInstaller, quindi l'unica che si possa svuotare
    senza toccare salvataggi, log e impostazioni dell'utente, che vivono
    accanto all'eseguibile.
    tasklist, findstr e ping sono chiamati con il percorso assoluto perche' il
    PATH dell'utente puo' contenere programmi con lo stesso nome: con Git Bash
    installato, per dirne una, find e' quello di Unix e il controllo sulla
    chiusura dell'applicazione fallirebbe in silenzio.
    La pausa fra un controllo e l'altro si fa con ping e non con timeout,
    perche' timeout rinuncia quando lo standard input e' ridiretto e il ciclo
    di attesa girerebbe a vuoto in un lampo."""
    if pulisci_internal:
        metti_da_parte = (
            f'if exist "{current_dir}\\_internal_vecchio" rmdir /S /Q "{current_dir}\\_internal_vecchio"\n'
            f'if exist "{current_dir}\\_internal" ren "{current_dir}\\_internal" "_internal_vecchio"'
        )
        conferma = f'if exist "{current_dir}\\_internal_vecchio" rmdir /S /Q "{current_dir}\\_internal_vecchio"'
        ripristino = (
            f'if not exist "{current_dir}\\_internal_vecchio" goto fallito_log\n'
            f'if exist "{current_dir}\\_internal" rmdir /S /Q "{current_dir}\\_internal"\n'
            f'ren "{current_dir}\\_internal_vecchio" "_internal"'
        )
    else:
        fermo = "rem La nuova versione non porta una cartella _internal: non si tocca niente."
        metti_da_parte = conferma = ripristino = fermo
    return f"""@echo off
chcp 65001 > nul
title Aggiornamento {app_name}
echo Attendo la chiusura di {app_name}. Non chiudere questa finestra.
set /a TENTATIVI=0
:attesa
"%SystemRoot%\\System32\\tasklist.exe" /FI "IMAGENAME eq {exe_name}" /NH 2>nul | "%SystemRoot%\\System32\\findstr.exe" /I /C:"{exe_name}" >nul
if errorlevel 1 goto chiuso
set /a TENTATIVI+=1
if %TENTATIVI% GEQ {attesa_massima} goto scaduto
"%SystemRoot%\\System32\\ping.exe" -n 2 127.0.0.1 >nul
goto attesa
:scaduto
echo Aggiornamento non applicato: {app_name} risulta ancora in esecuzione.
>>"{log_path}" echo Aggiornamento non applicato il %DATE% alle %TIME%, applicazione {app_name}.
>>"{log_path}" echo L'applicazione era ancora in esecuzione dopo {attesa_massima} secondi, quindi non e' stato toccato niente. L'archivio scaricato resta in {zip_path}.
goto fine
:chiuso
echo Applico l'aggiornamento.
{metti_da_parte}
xcopy "{source_dir}\\*" "{current_dir}\\" /S /Y /E /Q
if errorlevel 1 goto fallito
{conferma}
echo Aggiornamento applicato. Riavvio {app_name}.
del /Q "{zip_path}"
rmdir /S /Q "{temp_dir}"
goto riavvio
:fallito
echo Aggiornamento non riuscito. Riavvio la versione precedente.
{ripristino}
:fallito_log
>>"{log_path}" echo Aggiornamento non riuscito il %DATE% alle %TIME%, applicazione {app_name}.
>>"{log_path}" echo La copia dei file non e' andata a buon fine. L'installazione precedente e' rimasta al suo posto e l'archivio scaricato resta in {zip_path}.
goto riavvio
:riavvio
start "" /D "{current_dir}" "{current_exe}"
:fine
(goto) 2>nul & del "%~f0"
"""

def perform_update(download_url: str, app_name: str = "App", avanzamento=None, timeout: int = 30,
                   cartella_log: str | None = None) -> bool:
    """
    V1.6.1 di martedì 8 settembre 2026 by Gabriele Battaglia (IZ4APU) & Stella, poi ClaudIA (Claude Fable 5.1, modalità auto)
    Scarica l'aggiornamento, lo estrae e avvia lo script che sostituisce
    l'installazione, poi restituisce True perche' il chiamante possa chiudersi.
    Il download avviene con la verifica dei certificati attiva, tramite
    contesto_ssl: dalla V1.6.1 vale l'archivio di sistema piu' certifi, cosi'
    una radice che Windows non ha ancora scaricato non blocca l'aggiornamento.
    Gli errori vengono registrati accanto all'applicazione, non nella directory
    di lavoro, e firmati con il nome passato in app_name.
    True significa che lo script e' stato avviato, non che l'aggiornamento sia
    riuscito: quello lo si sapra' solo dopo la chiusura del programma, e in caso
    di fallimento lo script lo scrive nel log e riavvia la versione precedente,
    che resta integra.
    avanzamento, se indicata, viene chiamata durante lo scaricamento con i byte
    presi finora e il totale atteso, che vale zero quando il server non lo
    dichiara. Serve a non lasciare l'utente in silenzio per minuti: chi la passa
    decide come annunciarlo.
    timeout e' il tempo massimo in secondi di attesa di una risposta durante lo
    scaricamento, non la durata complessiva.
    """
    import os
    import shutil
    import subprocess
    import sys
    import tempfile
    import zipfile

    # Serve prima del controllo su frozen, perche' anche la rinuncia va
    # registrata accanto a chi ha chiamato. Vale qui la stessa nota di
    # update_checker sul perche' chi chiama possa indicarla.
    cartella_log = cartella_log or _cartella_chiamante(1)

    if not sys.platform.startswith('win'):
        return False

    try:
        # 1. Determina l'eseguibile corrente
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable
        else:
            _write_update_log("Impossibile aggiornare: in esecuzione da sorgente (sys.frozen=False).", cartella_log, app_name)
            return False
            
        current_dir = os.path.dirname(current_exe)
        exe_name = os.path.basename(current_exe)
        sys_temp = tempfile.gettempdir()
        
        # 2. Cartelle e file temporanei, tutti fuori dall'installazione. Prima
        # la cartella di estrazione stava dentro, nonostante il commento
        # dichiarasse il contrario: restava li' quando l'aggiornamento non
        # arrivava in fondo, e i suoi avanzi finivano poi copiati sopra la
        # versione nuova. Ora si ricomincia sempre da una cartella vuota.
        temp_dir = os.path.join(sys_temp, f"update_{app_name}_estratto")
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)

        zip_path = os.path.join(sys_temp, f"update_{app_name}.zip")
        bat_path = os.path.join(sys_temp, f"updater_{app_name}.bat")
        
        # 3. Download.
        _scarica(download_url, zip_path, avanzamento, timeout)
        
        # 4. Estrazione
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        # 5. Genera lo script che sostituisce l'installazione.
        # Troviamo la cartella che contiene l'eseguibile appena estratto
        source_dir = temp_dir
        exe_name_lower = exe_name.lower()
        for root, dirs, files in os.walk(temp_dir):
            if any(f.lower() == exe_name_lower for f in files):
                source_dir = root
                break

        # La vecchia _internal si svuota solo se anche la nuova versione ne
        # porta una: se il pacchetto e' in un pezzo solo non c'e' niente da
        # ripulire.
        pulisci_internal = (os.path.isdir(os.path.join(source_dir, "_internal"))
                            and os.path.isdir(os.path.join(current_dir, "_internal")))
        # Lo script batch sta in sys_temp, quindi fuori dall'installazione, e
        # si auto-elimina alla fine.
        bat_content = _script_aggiornamento(
            app_name=app_name,
            exe_name=exe_name,
            current_exe=current_exe,
            current_dir=current_dir,
            source_dir=source_dir,
            temp_dir=temp_dir,
            zip_path=zip_path,
            log_path=os.path.join(cartella_log, "auto_updater_error.log"),
            pulisci_internal=pulisci_internal,
        )
        # In UTF-8 con chcp 65001 dichiarato nello script: cmd.exe legge i .bat
        # nella codepage OEM, e senza quella riga i percorsi con lettere
        # accentate arrivavano storpiati e la copia falliva.
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
            
        # 6. Avvia lo script batch
        CREATE_NEW_CONSOLE = 0x00000010
        subprocess.Popen([bat_path], creationflags=CREATE_NEW_CONSOLE)
        
        return True
        
    except Exception as e:  # noqa: BLE001 - un aggiornamento fallito si riferisce, non fa cadere il programma
        _write_update_log(f"Errore durante l'esecuzione dell'aggiornamento: {e}", cartella_log, app_name)
        return False


def gestisci_aggiornamento(app_name: str, current_version: str, api_url: str,
                           timeout: int = 10, chiedi=None, avvisa=None, traduci=None,
                           solo_se_compilato: bool = True, proponi=None,
                           avanzamento=None) -> bool:
    """
    V1.2.0 di lunedì 14 settembre 2026 by Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
    Conduce da sola tutta la conversazione dell'aggiornamento: controlla se ce
    n'e' uno, lo riferisce, mostra le novita', chiede se applicarlo, lo scarica
    annunciando a che punto e' e avvia la sostituzione.
    Restituisce True soltanto quando il programma deve chiudersi perche'
    l'aggiornamento sta per essere applicato; in ogni altro caso False, e il
    programma prosegue.
    Nasce perche' le sette applicazioni che usano l'aggiornamento automatico
    ripetevano ognuna le stesse trenta o cinquanta righe, ed erano gia'
    diventate diverse fra loro: una sola mostrava all'utente le novita' della
    versione nuova, che update_checker restituisce da sempre.
    Le applicazioni con interfaccia grafica passano chiedi e avvisa, cioe' le
    proprie finestre: chiedi riceve un testo e risponde vero o falso, avvisa
    riceve un testo e lo mostra. Chi non le passa ottiene la conversazione da
    console, con enter_escape per la domanda e print per il resto; le novita'
    della release, che possono essere lunghe, passano da manuale e si leggono
    una pagina alla volta, cosi' chi decide se aggiornare le ha davvero lette
    invece di vedersele scorrere via. E' la scelta di Gabriele del 4 settembre
    2026, resa possibile da manuale V2.0.0, che accetta un testo in memoria.
    traduci, se indicata, riceve ogni testo prima che venga mostrato: le
    applicazioni tradotte le passano la propria funzione di gettext. Le frasi
    predefinite sono in italiano, quindi finche' non entrano nei cataloghi
    restano tali, senza che niente si rompa.
    solo_se_compilato lascia perdere quando si gira da sorgente, che e' il caso
    in cui l'aggiornamento non potrebbe comunque essere applicato.
    proponi e' la porta per le interfacce grafiche, dove ogni avvisa e' una
    finestra modale e la conversazione della console diventa tre o quattro
    finestre a ogni avvio, anche quando non c'e' niente da fare. Quando c'e',
    la funzione tace: niente annuncio del controllo, niente hai gia' l'ultima
    versione, niente aggiornamento rimandato. Se un aggiornamento c'e',
    proponi(versione_attuale, versione_nuova, note) riceve i tre dati insieme e
    risponde vero o falso; la finestra la fa il chiamante come vuole, e a
    avvisa restano i soli esiti. Chi la chiama da un thread, che e' la regola
    nelle interfacce grafiche, deve portare la domanda sul thread della
    finestra e aspettare li' la risposta: proponi e' sincrona, e il suo valore
    di ritorno e' la decisione dell'utente.
    avanzamento, se indicata, riceve i byte presi e il totale durante lo
    scaricamento, come vuole perform_update, e prende il posto degli annunci a
    percentuale. Senza di lei e senza proponi restano gli annunci di sempre;
    senza di lei ma con proponi lo scaricamento e' muto, perche' cinque
    finestre modali di fila sarebbero peggio del silenzio.
    """
    import sys

    def tr(testo):
        return traduci(testo) if traduci else testo

    def dillo(testo):
        if avvisa:
            avvisa(testo)
        else:
            print(testo)

    def cortesia(testo):
        # Le frasi che accompagnano il controllo: su console fanno compagnia,
        # in una finestra modale sono un intralcio. Chi passa proponi le
        # ha gia' dichiarate non gradite.
        if proponi is None:
            dillo(testo)

    def domanda(testo):
        if chiedi:
            return bool(chiedi(testo))
        return enter_escape(testo)

    if solo_se_compilato and not getattr(sys, 'frozen', False):
        return False

    # La cartella del log si ricava qui, dove il chiamante e' l'applicazione:
    # lasciandola ricavare alle due funzioni sottostanti, che a quel punto
    # vedrebbero come chiamante questa stessa libreria, il file finirebbe
    # accanto a GBUtils.py invece che accanto al programma.
    cartella_log = _cartella_chiamante(1)
    cortesia(tr("Controllo aggiornamenti."))
    disponibile, versione, indirizzo, changelog = update_checker(
        current_version, api_url, timeout, cartella_log)
    if not disponibile:
        if versione:
            cortesia(tr("Hai gia' l'ultima versione,") + f" {versione}.")
        else:
            cortesia(tr("Controllo non riuscito, si prosegue."))
        return False
    if not indirizzo:
        dillo(tr("Disponibile la versione") + f" {versione}, "
              + tr("ma il pacchetto non e' ancora pronto."))
        return False
    if proponi is not None:
        # Versioni e novita' in un colpo solo: il chiamante ne fa una finestra
        # sola, con le note dove si possono leggere con calma.
        if not proponi(current_version, versione, changelog):
            return False
    else:
        dillo(tr("Disponibile la versione") + f" {versione}.")
        dillo(tr("Tu hai la") + f" {current_version}.")
        if changelog:
            dillo(tr("Novita' di questa versione:"))
            if avvisa:
                dillo(changelog.strip())
            else:
                manuale(testo=changelog.strip(), nome=tr("Novita'"))
        if not domanda(tr("Vuoi aggiornare adesso?")):
            dillo(tr("Aggiornamento rimandato."))
            return False

    # L'avanzamento arriva un punto percentuale alla volta, cioe' centouno
    # volte: annunciarli tutti sarebbe un muro di parole sullo screen reader,
    # quindi se ne dice uno ogni venti, in righe corte da leggere anche sul
    # display braille. Si parte dal venti: annunciare lo zero ripeterebbe
    # soltanto la riga che dice che lo scaricamento e' cominciato. Erano uno
    # ogni dieci fino alla V1.1.0, e Gabriele li ha contati troppi ascoltando
    # un aggiornamento vero.
    PASSO = 20
    ultimo = [0]

    def segnala(preso, totale):
        if not totale:
            return
        percento = int(preso * 100 / totale)
        blocco = percento - percento % PASSO
        if blocco > ultimo[0]:
            ultimo[0] = blocco
            fatti = f"{preso / 1048576:.1f}".replace(".", ",")
            tutti = f"{totale / 1048576:.1f}".replace(".", ",")
            dillo(f"{percento}%, {fatti} MB su {tutti}.")

    cortesia(tr("Scarico l'aggiornamento."))
    if avanzamento is None and proponi is None:
        avanzamento = segnala
    if perform_update(indirizzo, app_name, avanzamento=avanzamento, cartella_log=cartella_log):
        dillo(tr("Aggiornamento pronto, il programma si chiude per applicarlo."))
        return True
    dillo(tr("Aggiornamento non riuscito, si prosegue con questa versione."))
    return False

def crea_archivio_release(nome_app, cartella_dist=None, archivio=None, escludi=None, silenzioso=False,
                          manifesto=True):
    """V1.1.0 di lunedì 14 settembre 2026 by Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
    Comprime in un solo archivio la cartella prodotta da PyInstaller.
    I file finiscono alla radice dell'archivio, senza cartelle intermedie: e' il
    solo formato che perform_update sa gestire, e che gli strumenti di
    compressione di Windows non producono.
    Parametri:
        nome_app: nome dell'applicazione. Se cartella_dist o archivio non sono
            indicati, si assumono dist/<nome_app> e <nome_app>.zip accanto al
            file che chiama la funzione, non alla directory di lavoro.
        cartella_dist: percorso della cartella da comprimere. Se relativo, e'
            risolto rispetto alla cartella del chiamante.
        archivio: percorso dello zip da creare. Stessa regola sui relativi.
        escludi: voci aggiuntive da lasciare fuori, oltre a quelle di serie.
            Una voce che termina con barra o barra rovescia e' un nome di
            cartella e viene saltata a qualunque profondita'. Ogni altra voce e'
            un motivo alla maniera di fnmatch, per esempio partite.json oppure
            *.danneggiato_*, ed e' applicata ai soli file che stanno accanto
            all'eseguibile.
        silenzioso: se vero non stampa nulla e si limita a restituire il conto.
        manifesto: se vero, e se il pacchetto ha una cartella _internal, scrive
            dentro l'archivio _internal/manifesto.txt con l'elenco dei file di
            _internal che contiene, se stesso compreso. Lo legge pulisci_residui
            al primo avvio dopo un aggiornamento, per sapere che cosa e' rimasto
            li' dalla versione precedente. Il file nasce nell'archivio e non
            nella cartella dist, che resta come l'ha lasciata PyInstaller.
    Le cartelle dei dati dell'utente, cioe' log, settings, pgn, txt e images, si
    saltano a qualunque profondita', perche' nascono provando l'eseguibile prima
    di comprimere e conterrebbero i dati di chi ha compilato.
    Niente di tutto questo entra pero' dentro _internal, dove sta quello che ha
    messo PyInstaller: li' una cartella images e' _tk_data/images di tkinter, e
    un base_library.zip o un membrane.dat servono davvero, tanto che senza di
    loro il pacchetto non parte nemmeno. In _internal restano fuori soltanto le
    cartelle di lavoro, cioe' __pycache__ e simili, che non sono mai legittime.
    Il filtro sulle estensioni e i motivi passati in escludi valgono soltanto per
    i file accanto all'eseguibile.
    Restituisce la coppia (quanti, lasciati), cioe' il numero di file scritti
    nell'archivio, manifesto compreso, e l'elenco ordinato di quelli lasciati
    fuori.
    Solleva FileNotFoundError se la cartella da comprimere non esiste.
    """
    import fnmatch
    import os
    import sys
    import zipfile

    cartelle_utente = {"log", "logs", "settings", "pgn", "txt", "images"}
    cartelle_di_lavoro = {"__pycache__", ".git", ".github", ".pytest_cache", ".ruff_cache"}
    estensioni_escluse = (".bak", ".tmp", ".pdb", ".log", ".pyc", ".zip", ".dat")

    try:
        base_dir = os.path.dirname(os.path.abspath(sys._getframe(1).f_globals["__file__"]))
    except (AttributeError, KeyError, ValueError):
        base_dir = os.getcwd()

    def assoluto(percorso):
        return percorso if os.path.isabs(percorso) else os.path.join(base_dir, percorso)

    if cartella_dist is None:
        cartella_dist = os.path.join("dist", nome_app)
    if archivio is None:
        archivio = f"{nome_app}.zip"
    cartella_dist = os.path.normpath(assoluto(cartella_dist))
    archivio = os.path.normpath(assoluto(archivio))

    cartelle_extra = set()
    motivi_extra = []
    for voce in escludi or ():
        voce = str(voce)
        if voce.endswith(("/", "\\")):
            cartelle_extra.add(voce.rstrip("/\\").lower())
        else:
            motivi_extra.append(voce.lower())
    salta_sempre = cartelle_utente | cartelle_di_lavoro | cartelle_extra

    if not silenzioso:
        print(f"Creo {os.path.basename(archivio)}")
        print(f"a partire da {cartella_dist}")
    if not os.path.isdir(cartella_dist):
        raise FileNotFoundError(f"Cartella da comprimere assente: {cartella_dist}")

    quanti = 0
    lasciati = []
    nel_manifesto = []
    radice_assoluta = os.path.abspath(cartella_dist)
    try:
        with zipfile.ZipFile(archivio, "w", zipfile.ZIP_DEFLATED) as zip_out:
            for radice, cartelle, file in os.walk(cartella_dist):
                dentro = os.path.relpath(radice, cartella_dist)
                pezzi = [] if dentro == "." else dentro.replace("\\", "/").split("/")
                # Dentro _internal comanda PyInstaller: li' un nome come images o
                # txt e' una risorsa che serve, non una cartella di dati altrui.
                # Restano fuori solo le cartelle di lavoro, che non sono mai
                # legittime. E' la stessa protezione che ha il filtro sulle
                # estensioni, e senza di lei tkinter perdeva _tk_data/images.
                dentro_internal = bool(pezzi) and pezzi[0].lower() == "_internal"
                salta_qui = cartelle_di_lavoro if dentro_internal else salta_sempre
                for c in cartelle:
                    if c.lower() in salta_qui:
                        ramo = c if dentro == "." else os.path.join(dentro, c)
                        lasciati.append(f"{ramo} e quel che contiene")
                cartelle[:] = [c for c in cartelle if c.lower() not in salta_qui]
                accanto_all_exe = os.path.abspath(radice) == radice_assoluta
                for nome in sorted(file):
                    minuscolo = nome.lower()
                    if accanto_all_exe and (
                        minuscolo.endswith(estensioni_escluse)
                        or any(fnmatch.fnmatch(minuscolo, m) for m in motivi_extra)
                    ):
                        lasciati.append(nome)
                        continue
                    percorso = os.path.join(radice, nome)
                    dentro_archivio = os.path.relpath(percorso, cartella_dist)
                    zip_out.write(percorso, dentro_archivio)
                    quanti += 1
                    if manifesto and dentro_internal:
                        # Il manifesto parla di percorsi relativi a _internal,
                        # perche' e' li' che vive e li' che si applica.
                        nel_manifesto.append(dentro_archivio.replace("\\", "/").split("/", 1)[1])
            if nel_manifesto:
                # Scritto per ultimo, quando si sa tutto quello che e' entrato, e
                # direttamente nell'archivio: la cartella dist resta come l'ha
                # lasciata PyInstaller.
                voci = sorted([*nel_manifesto, _NOME_MANIFESTO], key=str.lower)
                spiegazione = (
                    f"# Elenco dei file di _internal che questo pacchetto contiene, {len(voci)} in tutto.\n"
                    "# Lo legge pulisci_residui di GBUtils al primo avvio dopo un aggiornamento:\n"
                    "# cio' che sta in _internal e non e' elencato qui viene dalla versione\n"
                    "# precedente e si puo' cancellare. Un file per riga, percorso relativo a\n"
                    "# _internal, barra come separatore. Le righe che cominciano con un\n"
                    "# cancelletto sono commenti e non contano.\n")
                zip_out.writestr(f"_internal/{_NOME_MANIFESTO}", spiegazione + "\n".join(voci) + "\n")
                quanti += 1
    except OSError as e:
        if os.path.exists(archivio):
            try:
                os.remove(archivio)
            except OSError:
                pass
        raise OSError(f"Archivio non creato: {e}") from e

    lasciati.sort()
    if not silenzioso:
        print(f"Fatto: {quanti} file archiviati.")
        if nel_manifesto:
            print(f"Manifesto con {len(nel_manifesto) + 1} voci di _internal.")
        if lasciati:
            print(f"Lasciati fuori {len(lasciati)} elementi:")
            for voce in lasciati:
                print(f"  {voce}")
    return quanti, lasciati


def enter_escape(prompt="", guida="", attesa=None):
    """V2.0.0 di venerdì 11 settembre 2026 - Gabriele Battaglia (IZ4APU), Gemini 2.5 Pro & ClaudIA (Claude Fable 5.1, UltraCode)
    Aspetta Invio o Escape e riferisce quale dei due e' arrivato.
    Parametri:
      prompt: testo stampato prima dell'attesa, senza andare a capo, e
        ripetuto dopo ogni tasto che non sia Invio o Escape: chi lavora a
        orecchio risente la domanda e sa che la funzione aspetta ancora.
      guida: frase stampata prima di ripetere il prompt quando arriva un
        tasto diverso da Invio o Escape. Il predefinito e' la stringa vuota,
        cioe' nessuna parola: enter_escape non conosce la lingua di chi la
        chiama, quindi il testo lo passa il chiamante, gia' tradotto, e senza
        testo resta la ripetizione del prompt, che e' gia' nella sua lingua.
      attesa: secondi da aspettare; None, il predefinito, aspetta senza
        limite. Un tasto sbagliato fa ripartire l'attesa.
    Restituisce True se viene premuto Invio, False se viene premuto Escape,
    None se l'attesa scade senza risposta: nei chiamanti scritti come
    "if enter_escape(...)" la scadenza vale come un Escape.
    Solleva KeyboardInterrupt con Ctrl+C, come in qualunque programma da
    console, ed EOFError quando il processo non ha una console o un
    terminale da cui leggere, invece di restare in attesa per sempre.
    Dalla V2.0.0 il tasto lo legge la key di questo pacchetto invece di una
    copia propria: fino alla V1.1 su Windows un tasto speciale, per esempio
    una freccia, arrivava in due pezzi e la guida veniva detta due volte, e
    Ctrl+C veniva preso per un tasto sbagliato. Il predefinito della guida
    era una frase italiana, che i programmi in altre lingue si prendevano
    senza volerlo.
    """
    while True:
        tasto = key(prompt, attesa=attesa, alla_scadenza=None)
        if tasto is None:
            print()
            return None
        if tasto == '\r':
            print()
            return True
        if tasto == '\x1b':
            print()
            return False
        # Qualunque altro tasto: a capo, la guida se c'e', e al giro dopo key
        # ristampa il prompt, cosi' chi ascolta risente la domanda.
        print()
        if guida:
            print(guida, flush=True)
# Ordine di preferenza fra le interfacce audio, dalla piu' pronta alla meno.
# ASIO c'e' ed e' in cima: puo' entrare in gioco soltanto se punta allo stesso
# dispositivo scelto nel sistema, e se un altro programma la tiene in esclusiva
# la prova di apertura fallisce e si passa oltre.
_PREFERENZA_API = ("ASIO", "WASAPI", "WDM-KS", "DirectSound", "MME")
_scelta_audio = {"fatta": False, "device": None, "api": None}
def scegli_dispositivo_audio(api=None, riprova=False):
	"""V1.0.0 di domenica 6 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	Il dispositivo audio su cui suonare, e il nome della sua interfaccia.
	Con api a None sceglie da sola: fra le interfacce che puntano allo stesso
	dispositivo scelto nel sistema prende la piu' pronta che si lascia davvero
	aprire, e poi se lo ricorda. Il vincolo dello stesso dispositivo e' la parte
	che conta: cambiare interfaccia spesso vuol dire cambiare scheda, e su una
	macchina con una interfaccia professionale ASIO punta a quella e DirectSound
	a un driver generico. Scegliere per sola latenza manderebbe il suono dove chi
	ascolta non se lo aspetta.
	Con api indicata il chiamante si prende la responsabilita': puo' passare il
	nome di una interfaccia, per esempio wasapi o asio, oppure direttamente
	l'indice di un dispositivo.
	Con riprova a vero la scelta automatica si rifa' da capo, per esempio dopo
	che l'utente ha cambiato il dispositivo predefinito del sistema.
	Restituisce una coppia: indice del dispositivo e nome dell'interfaccia, o
	(None, None) se non c'e' niente da scegliere e conviene lasciar fare al
	sistema. Solleva ValueError se l'interfaccia chiesta non esiste.
	Costa 0,07 ms per enumerare e da 3 a 16 per una prova di apertura, ma dalla
	seconda chiamata e' in cache e costa nulla."""
	import sounddevice as sd
	if isinstance(api, bool):
		# ValueError e non TypeError: e' il contratto dichiarato nella
		# docstring, ed e' quello che CWzator cattura quando chiama.
		raise ValueError("api non puo' essere un valore logico")  # noqa: TRY004
	if isinstance(api, int):
		return api, None
	if api is not None:
		voluta = str(api).strip().lower()
		for h in sd.query_hostapis():
			if h["name"].lower().replace("windows ", "").startswith(voluta):
				d = h["default_output_device"]
				if d < 0:
					raise ValueError(f"l'interfaccia audio {api} non ha un dispositivo di uscita")
				return d, h["name"]
		raise ValueError(f"interfaccia audio {api} non disponibile")
	if _scelta_audio["fatta"] and not riprova:
		return _scelta_audio["device"], _scelta_audio["api"]
	try:
		predefinito = sd.query_devices(sd.default.device[1])["name"]
	except Exception:  # noqa: BLE001 - il dispositivo audio fallisce in molti modi, e qui si puo' fare senza
		predefinito = None
	candidati = []
	for h in sd.query_hostapis():
		d = h["default_output_device"]
		if d < 0:
			continue
		corto = h["name"].replace("Windows ", "")
		if corto not in _PREFERENZA_API:
			continue
		if predefinito is not None and sd.query_devices(d)["name"] != predefinito:
			continue
		candidati.append((_PREFERENZA_API.index(corto), d, h["name"]))
	scelto, nome = None, None
	for _ordine, d, nome_api in sorted(candidati):
		try:
			extra = sd.WasapiSettings(auto_convert=True) if "WASAPI" in nome_api else None
			prova = sd.OutputStream(device=d, samplerate=44100, channels=2, dtype="int16",
									blocksize=256, latency="low", extra_settings=extra)
			prova.start(); prova.abort(); prova.close()
		except Exception:  # noqa: BLE001, S112 - un'interfaccia che non si apre si scarta e si prova la prossima
			continue
		scelto, nome = d, nome_api
		break
	_scelta_audio.update({"fatta": True, "device": scelto, "api": nome})
	return scelto, nome
# Le interfacce che prendono il dispositivo in esclusiva: finche' uno le usa,
# nessun altro puo' suonare su quella scheda. Non e' una misura ma una
# proprieta' nota dell'interfaccia, e serve a chi presenta la lista: su una
# macchina con una scheda sola, sceglierle vuol dire zittire il lettore di
# schermo.
_API_ESCLUSIVE = ("ASIO", "WDM-KS")

def _prova_apertura(indice, nome_api):
	"""Prova davvero ad aprire un dispositivo, come lo aprirebbe CWzator.

	Restituisce (True, None) se si e' aperto, (False, motivo) altrimenti.
	Costa una cinquantina di millesimi di secondo, e su un'interfaccia
	esclusiva gia' occupata fallisce: e' l'informazione piu' utile da dare a
	chi deve scegliere, perche' e' esattamente quello che succederebbe al
	momento di suonare.
	"""
	import sounddevice as sd
	try:
		extra = sd.WasapiSettings(auto_convert=True) if "WASAPI" in (nome_api or "") else None
		prova = sd.OutputStream(device=indice, samplerate=44100, channels=2, dtype="int16",
								blocksize=256, latency="low", extra_settings=extra)
		prova.start()
		prova.abort()
		prova.close()
	except Exception as e:  # noqa: BLE001 - qui si vuole sapere se si apre, non perche' non si apre
		return False, f"{type(e).__name__}: {e}"
	return True, None

def _ordine_api(nome_api):
	"""Dove sta un'interfaccia nella scala di preferenza, in coda se non c'e'."""
	corto = (nome_api or "").replace("Windows ", "")
	return _PREFERENZA_API.index(corto) if corto in _PREFERENZA_API else len(_PREFERENZA_API)

def elenco_dispositivi_audio(prova="predefinito"):
	"""V1.0.0 di domenica 13 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	I dispositivi di uscita di questa macchina, pronti da presentare a chi sceglie.

	Nasce dalla issue 7: CWzator sapeva scegliere l'uscita e sapeva obbedire a
	chi gliene imponeva una, ma non sapeva elencare le possibilita', e
	un'applicazione che volesse offrirle all'utente doveva importarsi
	sounddevice per conto suo.
	prova dice quanto verificare, perche' quello che il sistema dichiara e
	quello che si riesce davvero ad aprire non sempre coincidono:
	  "predefinito"  il predefinito, e tutti quelli che portano il suo stesso
	                 nome, vengono davvero aperti e chiusi; degli altri si
	                 riporta quello che il sistema dichiara. E' il valore di
	                 partenza: sono pochi e sono quelli che contano.
	  "tutti"        si prova ad aprire ogni dispositivo. Costa una cinquantina
	                 di millesimi ciascuno, quindi oltre un secondo dove i
	                 dispositivi sono venti, e per un istante occupa anche
	                 quelli che nessuno stava usando.
	  "nessuno"      non si apre niente, si riporta solo quello che il sistema
	                 dichiara. Immediato.
	Restituisce una lista di dizionari, ordinata mettendo davanti i dispositivi
	che portano dove si sta gia' ascoltando, cioe' quelli con stessa_scheda, e
	dentro ogni gruppo per preferenza di interfaccia e poi per indice. Cosi' il
	primo della lista e' il modo piu' pronto di raggiungere la scheda che
	l'utente sta gia' usando, che e' quasi sempre la scelta che vuole. Ogni
	voce contiene:
	  indice         il numero da passare al parametro api di CWzator.
	  dispositivo    il nome del dispositivo, come lo scrive il sistema.
	  interfaccia    il nome dell'interfaccia, per esempio "Windows WASAPI".
	  breve          lo stesso senza "Windows", per esempio "WASAPI": e' la
	                 forma che il parametro api accetta come nome.
	  canali         quanti canali di uscita ha.
	  frequenza      la frequenza di campionamento che dichiara di preferire.
	  latenza        la latenza bassa dichiarata, in millesimi di secondo.
	  predefinito    vero per il dispositivo che il sistema riporta come uscita
	                 predefinita, che e' uno solo in tutta la lista. Attenzione
	                 a non fraintenderlo: e' quel dispositivo visto da una
	                 interfaccia sola, di solito MME, e non e' detto che sia la
	                 via migliore per arrivare a quella scheda. Su questa
	                 macchina il predefinito e' l'indice 4, su MME, ma gli
	                 stessi altoparlanti si raggiungono anche con WASAPI, che
	                 ha tre millesimi di latenza invece di novanta. Per quello
	                 c'e' stessa_scheda.
	  stessa_scheda  vero se porta lo stesso nome del predefinito di sistema,
	                 cioe' se con ogni probabilita' e' la stessa scheda vista
	                 da un'altra interfaccia. E' un confronto di nomi e non una
	                 certezza: la stessa scheda puo' avere nomi diversi sotto
	                 interfacce diverse, per esempio "Realtek ASIO" e
	                 "Speakers (Realtek HD Audio output)".
	  esclusiva      vero se l'interfaccia prende il dispositivo in esclusiva.
	  apribile       vero o falso se e' stato provato, None se non lo si e'
	                 provato.
	  motivo         perche' non si e' aperto, quando apribile e' falso.
	Il dato che conta di piu' e' predefinito, insieme a stessa_scheda: chi
	presenta la lista deve poter dire all'utente quale scelta lo porta dove
	sta gia' ascoltando, altrimenti gli fa cambiare scheda senza volerlo.
	Solleva ValueError se prova non e' uno dei tre valori previsti.
	"""
	import sounddevice as sd
	if prova not in ("predefinito", "tutti", "nessuno"):
		raise ValueError(f"prova ({prova}) non valido: predefinito, tutti o nessuno")
	try:
		nome_predefinito = sd.query_devices(sd.default.device[1])["name"]
		indice_predefinito = sd.default.device[1]
	except Exception:  # noqa: BLE001 - senza predefinito si elenca lo stesso, senza poterlo segnalare
		nome_predefinito, indice_predefinito = None, None
	api = [h["name"] for h in sd.query_hostapis()]
	voci = []
	for dispositivo in sd.query_devices():
		if dispositivo["max_output_channels"] <= 0:
			continue
		nome_api = api[dispositivo["hostapi"]] if dispositivo["hostapi"] < len(api) else ""
		corto = nome_api.replace("Windows ", "")
		stessa = nome_predefinito is not None and dispositivo["name"] == nome_predefinito
		voci.append({
			"indice": dispositivo["index"],
			"dispositivo": dispositivo["name"],
			"interfaccia": nome_api,
			"breve": corto,
			"canali": int(dispositivo["max_output_channels"]),
			"frequenza": float(dispositivo["default_samplerate"]),
			"latenza": float(dispositivo["default_low_output_latency"]) * 1000.0,
			"predefinito": dispositivo["index"] == indice_predefinito,
			"stessa_scheda": stessa,
			"esclusiva": corto in _API_ESCLUSIVE,
			"apribile": None,
			"motivo": None,
		})
	for voce in voci:
		if prova == "nessuno" or (prova == "predefinito" and not voce["stessa_scheda"]):
			continue
		voce["apribile"], voce["motivo"] = _prova_apertura(voce["indice"], voce["interfaccia"])
	# Davanti chi porta dove si sta gia' ascoltando: e' la scelta che ha senso
	# nella grande maggioranza dei casi, e chi vuole un altro ordine riordina.
	voci.sort(key=lambda v: (not v["stessa_scheda"], _ordine_api(v["interfaccia"]), v["indice"]))
	return voci

def elenco_interfacce_audio():
	"""V1.0.0 di domenica 13 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)
	Le interfacce audio di questa macchina, con il dispositivo a cui puntano.

	Serve a chi vuole far scegliere il protocollo invece del singolo
	dispositivo: il nome breve di ogni voce e' quello che il parametro api di
	CWzator accetta.
	Restituisce una lista di dizionari, ordinata per preferenza, cioe' dalla
	piu' pronta alla piu' lenta, e poi per nome. Ogni voce contiene:
	  nome           il nome come lo scrive il sistema, per esempio "Windows WASAPI".
	  breve          lo stesso senza "Windows": e' la forma da passare ad api.
	  indice         l'indice dell'interfaccia, che serve di rado.
	  dispositivo    l'indice del suo dispositivo di uscita predefinito, None se
	                 quell'interfaccia non ne ha uno.
	  nome_dispositivo  il nome di quel dispositivo.
	  quanti         quanti dispositivi di uscita offre in tutto.
	  latenza        la latenza bassa dichiarata dal suo predefinito, in
	                 millesimi di secondo, None se non ha dispositivi.
	  stessa_scheda  vero se il suo predefinito porta lo stesso nome del
	                 predefinito di sistema. Vedi elenco_dispositivi_audio per
	                 quanto ci si possa fidare di un confronto di nomi.
	  esclusiva      vero se prende il dispositivo in esclusiva.
	  preferenza     la posizione nella scala con cui CWzator sceglie da sola,
	                 zero per la piu' pronta, None per quelle fuori scala.
	Non prova ad aprire niente: e' immediata. Per sapere se un dispositivo si
	apre davvero c'e' elenco_dispositivi_audio.
	"""
	import sounddevice as sd
	try:
		nome_predefinito = sd.query_devices(sd.default.device[1])["name"]
	except Exception:  # noqa: BLE001 - senza predefinito si elenca lo stesso
		nome_predefinito = None
	dispositivi = list(sd.query_devices())
	voci = []
	for indice, h in enumerate(sd.query_hostapis()):
		corto = h["name"].replace("Windows ", "")
		uscita = h["default_output_device"]
		uscita = uscita if uscita is not None and uscita >= 0 else None
		quanti = sum(1 for d in dispositivi
					 if d["hostapi"] == indice and d["max_output_channels"] > 0)
		nome_uscita = dispositivi[uscita]["name"] if uscita is not None else None
		voci.append({
			"nome": h["name"],
			"breve": corto,
			"indice": indice,
			"dispositivo": uscita,
			"nome_dispositivo": nome_uscita,
			"quanti": quanti,
			"latenza": (float(dispositivi[uscita]["default_low_output_latency"]) * 1000.0
						if uscita is not None else None),
			"stessa_scheda": nome_predefinito is not None and nome_uscita == nome_predefinito,
			"esclusiva": corto in _API_ESCLUSIVE,
			"preferenza": _PREFERENZA_API.index(corto) if corto in _PREFERENZA_API else None,
		})
	voci.sort(key=lambda v: (_ordine_api(v["nome"]), v["nome"]))
	return voci

# Il mixer condiviso, nato con la issue 8 il 12 settembre 2026. Sta qui, fra
# la scelta dell'uscita e CWzator, perche' e' di entrambi: Acusticator e
# CWzator ne avevano uno per ciascuno, e questo prendera' il posto di tutti e
# due. Le classi sono private perche' chi le usa non le vede: vede Acusticator
# e CWzator, che gli passano davanti.

class _Voce:
	"""Un suono in riproduzione: il buffer, dove siamo arrivati, la panoramica
	e l'evento con cui chi l'ha mandato puo' aspettarne la fine."""

	__slots__ = ("a_fine", "buffer", "destra", "fermata", "fine", "nata", "pos", "sinistra")

	def __init__(self, buffer, pan, orologio, a_fine=None):
		import math
		import threading
		self.buffer = buffer
		self.pos = 0
		# Panoramica a potenza costante: al centro i due lati stanno a meno tre
		# decibel ciascuno, cosi' la somma dei due resta la stessa da qualunque
		# parte il suono si trovi. Con il guadagno lineare, al centro il suono
		# sembrerebbe piu' debole che ai lati.
		angolo = (max(-1.0, min(1.0, float(pan))) + 1.0) * math.pi / 4.0
		self.sinistra = math.cos(angolo)
		self.destra = math.sin(angolo)
		self.fine = threading.Event()
		self.nata = orologio()
		self.fermata = False
		# Cosa fare quando questa voce e' finita, oltre a svegliare chi
		# aspetta: serve a chi tiene un oggetto per ogni suono, come CWzator.
		self.a_fine = a_fine


class _MixerCondiviso:
	"""Alimenta la scheda audio senza mai interrompersi, sommando le voci.

	Tenere lo stream aperto non basta: se fra un suono e l'altro nessuno
	scrive, il buffer del dispositivo si svuota, la scheda va a secco, e li'
	nasce lo schiocco. Qui si scrive sempre, le voci attive sommate e silenzio
	quando non c'e' niente da suonare, finche' il silenzio non dura abbastanza
	da chiudere e lasciare libera la scheda.
	Alimenta scrivendo, non rispondendo a un callback, ed e' una scelta
	misurata: il callback deve entrare in Python nel momento esatto in cui la
	scheda ha fame, e se un altro filo del programma sta calcolando resta in
	coda per il lucchetto dell'interprete; scrivendo, invece, ci si porta
	avanti e il buffer gia' riempito copre l'attesa. Misurato il 12 settembre
	2026 con quattro fili di calcolo: a callback sette buchi al secondo, a
	scrittura nessuno.
	"""

	# Campioni per blocco. A 44100 hertz, 1024 campioni sono ventitre'
	# millesimi di secondo, ed e' il valore scelto dopo le misure: sotto i 768
	# i buchi tornano anche scrivendo, e 1024 e' il passo successivo, che
	# lascia margine per i carichi non provati.
	BLOCCO = 1024
	# Dopo quanto silenzio si chiude e si lascia libera la scheda.
	SILENZIO_MAX = 120.0
	# Quante voci insieme: oltre questo numero la piu' vecchia lascia il posto,
	# cosi' l'ultimo evento si sente sempre.
	VOCI_MAX = 32
	FS = 44100

	def __init__(self):
		import threading
		self._lock = threading.RLock()
		self._avvio = threading.Lock()
		self._voci = []
		self._stream = None
		self._pompa = None
		self._ferma = threading.Event()
		self._fs = self.FS
		self._device = None
		self._nome_api = None
		self._canali = 2
		self._volume = 1.0
		self._silenzio = self.SILENZIO_MAX
		self._voci_max = self.VOCI_MAX
		self._blocco = self.BLOCCO
		self._uscita_registrata = False
		# Cio' che e' andato storto, per chi vuole saperlo senza che il mixer
		# stampi niente per conto suo.
		self.ultimo_errore = None
		self.buchi = 0

	# --- Cio' che serve a chi manda un suono ---

	def suona(self, buffer, fs=None, pan=0.0, sync=False, a_fine=None):
		"""Manda un buffer al mixer. Restituisce la voce, o None se il
		dispositivo non si apre.

		buffer: array di campioni float32 fra meno uno e piu' uno, mono o
		  stereo. Il mono viene sdoppiato applicando la panoramica.
		fs: la frequenza del buffer, se diversa da quella dello stream: viene
		  riportata a quella giusta.
		pan: da meno uno, tutto a sinistra, a piu' uno, tutto a destra.
		sync: vero aspetta che il suono sia finito; un numero aspetta al
		  massimo quei secondi.
		a_fine: funzione chiamata quando il suono e' finito, anche se e' stato
		  fermato o ha lasciato il posto a un altro. Gira nel filo del mixer,
		  quindi deve essere breve: se ci mette, la scheda resta a secco. Se
		  solleva, il guasto finisce in ultimo_errore e il mixer prosegue.
		"""
		import numpy as np
		if buffer is None or len(buffer) == 0:
			return None
		buffer = np.asarray(buffer, dtype=np.float32)
		if buffer.ndim == 1:
			buffer = buffer.reshape(-1, 1)
		with self._avvio:
			if not self._assicura_stream():
				return None
		if fs is not None and int(fs) != self._fs:
			buffer = self._adatta_frequenza(buffer, int(fs))
		voce = _Voce(buffer, pan, self._orologio, a_fine)
		with self._lock:
			while len(self._voci) >= self._voci_max:
				self._chiudi_voce(self._voci.pop(0))
			self._voci.append(voce)
		if sync:
			attesa = None if sync is True else max(0.0, float(sync))
			if attesa is None:
				# Anche l'attesa senza limite ha un limite, ricavato dalla
				# durata del suono piu' un margine: serve al caso in cui lo
				# stream smetta di rispondere senza passare da chiudi, per
				# esempio se il dispositivo sparisce.
				attesa = len(buffer) / float(self._fs) + 2.0
			voce.fine.wait(timeout=attesa)
		return voce

	def ferma(self, voce=None):
		"""Ferma una voce, o tutte quante se non se ne indica nessuna."""
		with self._lock:
			bersagli = list(self._voci) if voce is None else [v for v in self._voci if v is voce]
			for v in bersagli:
				v.fermata = True
		return len(bersagli)

	def aspetta_uscita(self):
		"""Il tempo che i campioni gia' consegnati impiegano a uscire.

		Quando una voce finisce, i suoi campioni sono usciti dal mixer ma non
		ancora dalle casse: restano nel buffer del dispositivo per un tempo
		pari alla latenza. Chi aspetta la fine di un suono di congedo, prima
		di chiudere il programma, deve aspettare anche questo, altrimenti
		l'ultima nota viene troncata.
		"""
		import time
		ritardo = 0.05
		try:
			if self._stream is not None:
				ritardo = float(self._stream.latency) + 0.02
		except (AttributeError, TypeError, ValueError):
			pass
		time.sleep(min(ritardo, 0.5))

	def stato(self):
		"""Come sta il mixer adesso, per chi vuole guardarlo."""
		with self._lock:
			return {
				"aperto": self._stream is not None,
				"voci": len(self._voci),
				"frequenza": self._fs,
				"blocco": self._blocco,
				"canali": self._canali,
				"buchi": self.buchi,
				"ultimo_errore": self.ultimo_errore,
			}

	def chiudi(self, attesa=2.0):
		"""Ferma tutto e lascia libera la scheda, aspettando che il filo sia
		davvero uscito da PortAudio.

		Serve prima che l'interprete cominci a smontare i moduli: un filo
		daemon sorpreso dentro PortAudio fa morire il processo, e su Windows
		il codice di uscita e' 0xC0000374, corruzione dell'heap. Chiedere
		l'arresto non basta: bisogna anche aspettarlo.
		"""
		with self._lock:
			restate = list(self._voci)
			self._voci = []
			pompa = self._pompa
		for voce in restate:
			self._chiudi_voce(voce)
		self._ferma.set()
		try:
			if pompa is not None and pompa.is_alive():
				pompa.join(attesa)
		finally:
			self._ferma.clear()

	# --- Cio' che sta sotto ---

	def _chiudi_voce(self, voce):
		"""Sveglia chi aspetta la voce e chiama la sua funzione di fine, se
		ce n'e' una. Un guasto li' dentro non deve fermare il mixer."""
		voce.fine.set()
		if voce.a_fine is not None:
			try:
				voce.a_fine()
			except Exception as errore:  # noqa: BLE001 - chi si iscrive alla fine non puo' far cadere il mixer
				self.ultimo_errore = f"la funzione di fine voce ha sollevato: {errore}"

	def _orologio(self):
		import time
		return time.monotonic()

	def _adatta_frequenza(self, buffer, fs):
		"""Riporta un buffer alla frequenza dello stream."""
		from fractions import Fraction

		import numpy as np
		from scipy import signal
		rapporto = Fraction(self._fs, int(fs)).limit_denominator(1000)
		adattato = signal.resample_poly(buffer, rapporto.numerator,
										rapporto.denominator, axis=0)
		return np.clip(adattato, -1.0, 1.0).astype(np.float32)

	def _assicura_stream(self):
		"""Lo stream esiste e la pompa gira, altrimenti li avvia."""
		if self._stream is not None and self._pompa is not None and self._pompa.is_alive():
			return True
		if not self._apri_stream():
			return False
		if not self._uscita_registrata:
			import atexit
			atexit.register(self.chiudi)
			self._uscita_registrata = True
		import threading
		self._ferma.clear()
		self._pompa = threading.Thread(target=self._pompa_audio, daemon=True,
									   name="GBUtils-mixer")
		self._pompa.start()
		return True

	def scegli_uscita(self, api=None, riprova=False):
		"""Sceglie il dispositivo e l'interfaccia audio su cui suonare.

		Senza argomenti prende la piu' pronta fra quelle che puntano al
		dispositivo scelto nel sistema; con api si chiede un'interfaccia per
		nome, per esempio WASAPI, o un dispositivo per numero. La scelta vale
		dalla prossima apertura: se il mixer sta suonando, si chiude prima.
		"""
		device, nome_api = scegli_dispositivo_audio(api, riprova)
		if device != self._device or nome_api != self._nome_api:
			self.chiudi()
			self._device = device
			self._nome_api = nome_api
		return device, nome_api

	def _apri_stream(self):
		"""Apre lo stream, provando il mono se il dispositivo rifiuta lo stereo."""
		import sounddevice as sd
		if self._device is None and self._nome_api is None:
			# Alla prima apertura si chiede al sistema qual e' l'uscita piu'
			# pronta; se la scelta fallisce si lascia decidere a PortAudio.
			try:
				self._device, self._nome_api = scegli_dispositivo_audio()
			except Exception:  # noqa: BLE001 - senza una scelta si va con il predefinito di PortAudio
				self._device, self._nome_api = None, None
		ultimo = None
		for canali in (2, 1):
			try:
				extra = None
				if self._nome_api and "WASAPI" in self._nome_api:
					# Senza questo WASAPI accetta soltanto la frequenza
					# impostata in Windows, e delle dodici che cwapu offre ne
					# passerebbe una sola.
					extra = sd.WasapiSettings(auto_convert=True)
				stream = sd.OutputStream(
					samplerate=self._fs, channels=canali, dtype="float32",
					blocksize=self._blocco, latency="low", device=self._device,
					extra_settings=extra)
				stream.start()
				self._stream = stream
				self._canali = canali
				return True
			except Exception as errore:  # noqa: BLE001 - il dispositivo audio fallisce in molti modi
				ultimo = errore
		self.ultimo_errore = f"apertura del dispositivo audio non riuscita: {ultimo}"
		return False

	def _pompa_audio(self):
		"""Il filo che scrive senza mai interrompersi, finche' c'e' qualcosa da
		suonare o finche' il silenzio non e' durato abbastanza."""
		import numpy as np
		import sounddevice as sd
		stream = self._stream
		silenzio = np.zeros((self._blocco, self._canali), dtype=np.float32)
		ultimo_suono = self._orologio()
		try:
			while not self._ferma.is_set():
				blocco = self._prepara_blocco()
				adesso = self._orologio()
				if blocco is None:
					if adesso - ultimo_suono > self._silenzio > 0:
						break
					blocco = silenzio
				else:
					ultimo_suono = adesso
				# write dice vero quando la scheda e' rimasta a secco: e' il
				# segnale che il codice di prima non guardava mai, ed e' per
				# questo che un difetto del genere si scopriva solo a orecchio.
				if stream.write(blocco):
					self.buchi += 1
		except sd.PortAudioError as errore:
			self.ultimo_errore = f"PortAudioError durante la riproduzione: {errore}"
		except Exception as errore:  # noqa: BLE001 - il filo del mixer non deve morire in silenzio
			self.ultimo_errore = f"errore durante la riproduzione: {errore}"
		finally:
			self._smonta(stream)

	def _prepara_blocco(self):
		"""La somma delle voci attive, o None quando non c'e' niente da suonare."""
		import numpy as np
		with self._lock:
			voci = list(self._voci)
		if not voci:
			return None
		somma = np.zeros((self._blocco, self._canali), dtype=np.float32)
		finite = []
		for voce in voci:
			if voce.fermata:
				finite.append(voce)
				continue
			pezzo = voce.buffer[voce.pos:voce.pos + self._blocco]
			quanti = len(pezzo)
			if quanti:
				if pezzo.shape[1] == 1:
					mono = pezzo[:, 0]
					if self._canali == 2:
						somma[:quanti, 0] += mono * voce.sinistra
						somma[:quanti, 1] += mono * voce.destra
					else:
						somma[:quanti, 0] += mono
				elif self._canali == 2:
					somma[:quanti] += pezzo
				else:
					somma[:quanti, 0] += pezzo.mean(axis=1)
			voce.pos += self._blocco
			if voce.pos >= len(voce.buffer):
				finite.append(voce)
		if finite:
			with self._lock:
				self._voci = [v for v in self._voci if not any(v is f for f in finite)]
			for voce in finite:
				self._chiudi_voce(voce)
		if self._volume != 1.0:
			somma *= self._volume
		np.clip(somma, -1.0, 1.0, out=somma)
		return somma

	def _smonta(self, stream):
		"""Chiude lo stream e sveglia chi stava aspettando una voce."""
		try:
			stream.abort()
			stream.close()
		except Exception:  # noqa: BLE001, S110 - si sta chiudendo: uno stream che non si chiude non ha piu' niente da dire
			pass
		with self._lock:
			restate = list(self._voci)
			self._voci = []
			self._stream = None
			self._pompa = None
		for voce in restate:
			self._chiudi_voce(voce)


# L'istanza sola, quella che tutto il parco software condivide: un mixer, uno
# stream, una scheda audio. Nasce alla prima richiesta, perche' crearla costa
# e chi importa GBUtils per dgt o per menu non deve pagarla.
_MIXER = None

def _mixer_condiviso():
	"""Il mixer di tutti, creato alla prima richiesta."""
	global _MIXER
	if _MIXER is None:
		_MIXER = _MixerCondiviso()
	return _MIXER

def CWzator(msg="", wpm=35, pitch=550, l=30, s=50, p=50, fs=44100, ms=1, vol=0.5, wv=1, sync=False, to_file=False, wave_output_path_file=None, get_map=False, fade_mode="fisso", fade_shape="lineare", play=True, pan=0, verbose=False, api=None, pausa=None, farnsworth=None):
	"""
	CWzator V11.3.0 di domenica 13 settembre 2026 - Gabriele Battaglia (IZ4APU), Stella/Gemini 3.5 Flash e ClaudIA (Claude Opus 5, UltraCode)
		da un'idea originale di Kevin Schmidt W9CF
	Genera e riproduce l'audio del codice Morse dal messaggio di testo fornito.
	Parameters:
		msg (str): Messaggio di testo da convertire in Morse. Non serve passarlo quando si
			chiede soltanto la mappa con get_map.
			I caratteri fuori mappa vengono scartati in silenzio. Lo spazio e il trattino basso
			stanno nella mappa con codice vuoto e servono da segnaposti: non suonano, ma
			separano le parole. Se nessun carattere del messaggio produce suono si riceve un
			PlaybackHandle valido e muto, con rwpm uguale a wpm.
		wpm (int): Velocità in parole al minuto (range 5-120).
			Il tetto era 100 fino alla V9.1. Portarlo a 120 copre chi riceve più veloce senza
			permettere combinazioni senza senso: a 550 Hz un punto contiene 5,5 cicli d'onda a
			120 wpm ma solo 3,3 a 200, e sotto i quattro cicli un tono smette di essere un tono.
		pitch (int): Frequenza in Hz per il tono (range 130-2800).
		l (int): Peso per la durata della linea (default 30).
		s (int): Peso per la durata degli spazi tra simboli, lettere e parole (default 50).
		p (int): Peso per la durata del punto (default 50).
		fs (int): Frequenza di campionamento (default 44100 Hz).
		ms (int|float): Durata in millisecondi della dissolvenza in apertura e in chiusura di ogni tono (default 1).
			Attenzione: la dissolvenza accorcia la durata efficace dell'elemento di ms millesimi,
			sempre, qualunque sia la sua lunghezza. Su un punto a 20 wpm è l'uno e sei per cento,
			a 100 wpm è l'otto e tre. Siccome toglie lo stesso a punto e linea, alle alte velocità
			il loro rapporto si allontana da tre: 3,03 a 20 wpm, 3,19 a 100. Vedi fade_mode.
			Quando ms supera la metà dell'elemento la rampa viene accorciata a metà elemento,
			non scartata: scartarla, come faceva la V9.1, lasciava uno schiocco proprio sugli
			elementi più corti.
		vol (float): Volume (range 0.0 a 1.0, default 0.5).
		wv (int): Tipo d'onda (scipy.signal): 1=Sine(default), 2=Square, 3=Triangle, 4=Sawtooth (dente di sega discendente classica).
		sync (bool): Se True, la funzione aspetta la fine reale del suono; altrimenti ritorna subito.
		to_file (bool): Se True, salva l'audio in un file WAV. La riproduzione avviene comunque,
			salvo che si passi play=False.
		wave_output_path_file (str|os.PathLike|None): Percorso e/o nome file per il salvataggio WAV.
			Può contenere solo il percorso (directory), solo il nome file, o entrambi.
			Se None (default), salva accanto al file che ha chiamato CWzator, o accanto
			all'eseguibile se il programma è compilato, con nome autogenerato. Dove i dati
			sono presenti, hanno priorità sul comportamento di default.
			Il percorso effettivamente usato si legge in file_salvato del PlaybackHandle.
		get_map (bool): Se True, restituisce immediatamente il dizionario MORSE_MAP senza generare audio.
		fade_mode (str): Come la dissolvenza si rapporta alla durata dell'elemento (default "fisso").
			"fisso": ms millesimi tanto sul punto quanto sulla linea. È il comportamento storico e
				quello dei manipolatori veri, dove il tempo di salita non dipende dalla velocità.
				Il rapporto fra linea e punto si allontana da tre man mano che la velocità sale.
			"proporzionale": la rampa è la stessa frazione di ogni elemento, ricavata da ms
				rapportato al punto. Punto e linea perdono la stessa percentuale, quindi il loro
				rapporto resta tre esatto a qualunque velocità, e le durate assolute non cambiano.
			"compensato": la rampa resta di ms millesimi, ma l'elemento si allunga di altrettanto
				e prende in prestito quel tempo dal silenzio che lo segue. La durata efficace torna
				nominale, il rapporto torna tre e la lunghezza totale del messaggio non cambia.
				Il prestito non supera mai metà dello spazio fra simboli.
		fade_shape (str): Forma della rampa (default "lineare").
			"lineare": rampa dritta, come nelle versioni fino alla V9.1.
			"coseno": mezzo coseno rialzato. Toglie all'elemento esattamente la stessa durata
				efficace della lineare, quindi non corregge il rapporto. Con dissolvenze lunghe
				sporca molto meno la banda, da 11 a 15 dB in meno con ms uguale a 5; con ms
				uguale a 1 è invece uguale o un filo peggiore della dritta.
		api (str|int|None): Quale interfaccia audio usare (default None, cioè scegli tu).
			Con None, alla prima riproduzione CWzator sceglie da sola fra le interfacce che
			puntano allo stesso dispositivo scelto in Windows, prendendo la più pronta che si
			lascia davvero aprire, e poi se lo ricorda. Su Windows questo di solito vuol dire
			WASAPI, che porta la latenza da 104 a 22 millesimi.
			Il vincolo dello stesso dispositivo è la parte che conta: cambiare interfaccia
			spesso vuol dire cambiare scheda, quindi scegliere per sola latenza manderebbe il
			suono dove chi ascolta non se lo aspetta.
			ASIO è nella scala di preferenza e può essere scelto, ma soltanto se punta allo
			stesso dispositivo del sistema; e se un altro programma lo tiene in esclusiva la
			prova di apertura fallisce e si passa oltre.
			Si può passare il nome di una interfaccia, per esempio "wasapi", "mme" o "asio",
			oppure direttamente l'indice di un dispositivo di sounddevice.
			scegli_dispositivo_audio(), esportata anche come CWzator.scegli_dispositivo, dice
			quale è stata scelta senza suonare niente, e con riprova=True rifà la scelta da capo,
			per esempio dopo che l'utente ha cambiato il dispositivo predefinito del sistema.
			Per far scegliere all'utente, invece che scegliere da sé, ci sono due elenchi,
			esportati anche come CWzator.elenco_dispositivi e CWzator.elenco_interfacce:
			elenco_interfacce_audio() dà una voce per interfaccia, il cui campo breve è proprio
			la stringa da passare qui; elenco_dispositivi_audio() dà una voce per dispositivo di
			uscita, il cui campo indice è il numero da passare qui. Tutti e due dicono la
			latenza dichiarata e se quella scelta porta alla scheda su cui l'utente sta già
			ascoltando, che è il dato da mostrargli.
			Un avvertimento per chi costruisce un menu: quello che il sistema dichiara e quello
			che si riesce davvero ad aprire non coincidono. Misurato sulla macchina di sviluppo,
			sei dispositivi su ventuno non si aprono, fra cui tutti quelli WDM-KS, che pure la
			scala di preferenza mette al terzo posto. elenco_dispositivi_audio con prova="tutti"
			li prova uno per uno e lo dice nei campi apribile e motivo: costa duecento millesimi
			di secondo una volta sola, e sono ben spesi.
		verbose (bool): Se True stampa gli errori anche su stderr, come le versioni fino
			alla V9.7 (default False, cioè non stampa). Vedi la sezione Errori.
		play (bool): Se False genera l'audio e non lo riproduce (default True, cioè riproduce).
			Serve a chi vuole soltanto il file WAV, a chi vuole l'array dei campioni per
			analizzarlo o rielaborarlo, e alle misure. L'array sta in audio_data del
			PlaybackHandle restituito, e resta riproducibile a mano con il suo metodo play.
		pan (int|float): Posizione fra i due altoparlanti, da -100 tutto a sinistra a +100 tutto
			a destra, 0 al centro (default). Serve soprattutto al pile-up: distribuendo le stazioni
			sul fronte stereo si separano molto meglio che con il solo tono.
			La legge è a potenza costante, quindi una stazione al centro non si sente più debole
			di una tutta da un lato. Riguarda solo la riproduzione: l'array in audio_data e il file
			WAV restano monofonici.
			Nota: Acusticator per la stessa cosa usa la scala da -1 a +1. La differenza è voluta.
		pausa (int|float|None): Quanto dura il silenzio che il trattino basso produce dentro
			il messaggio. Attenzione a cosa fa e cosa non fa: questo parametro decide la
			durata, non la posizione. Dove cade la pausa lo dice il messaggio, mettendoci un
			trattino basso; senza trattini bassi, questo parametro non produce alcun
			silenzio, né all'inizio, né alla fine, né fra le lettere.
			Esempi, a 25 parole al minuto:
				CWzator("ciao", pausa=500) dura quanto CWzator("ciao"): nessuna pausa.
				CWzator("ciao _ mondo", pausa=500) mette mezzo secondo fra le due parole,
					che si somma allo spazio fra parole di 333 millesimi già previsto dal
					morse, per un silenzio complessivo di 833.
				CWzator("ciao mondo _", pausa=500) la mette in coda.
				CWzator("_ ciao mondo", pausa=500) la mette davanti.
				CWzator("ciao _ _ mondo", pausa=300) ne mette due di fila, cioè 600
					millesimi più lo spazio fra parole.
			None (default) vale uno spazio fra parole alla velocità corrente,
			cioè sette unità scalate dal peso s: è ciò che il trattino basso faceva fino alla
			V9.1 e che dalla V10.0 aveva smesso di fare, perché il cambiamento che ha reso
			esatta la velocità effettiva lo aveva reso muto. Un numero vale quei millesimi di
			secondo esatti, indipendenti dalla velocità, per chi vuole una pausa per la testa
			e non per l'orecchio, per esempio fra un esercizio e il successivo.
			Ogni trattino basso è una pausa, dovunque si trovi: "r _ _" ne produce due.
			Il silenzio della pausa resta nell'audio ma non entra nel calcolo della velocità
			effettiva, né fra le unità né nella durata: la velocità annunciata è quella del
			morse che si sente, non quella diluita dalle attese. Se entrasse da una parte
			sola, aggiungere una pausa farebbe scendere la velocità pur restando il suono
			identico.
			Lo spazio semplice non cambia: resta il separatore di parole di sempre.
		farnsworth (int|float|None): Velocità effettiva in parole al minuto, cioè quella
			d'insieme del messaggio (default None, cioè niente Farnsworth e tutto come prima).
			Il metodo di Russell Farnsworth serve a imparare il Morse senza dover reimparare i
			caratteri quando si accelera: i caratteri si trasmettono fin da subito alla velocità
			finale, così l'orecchio impara il loro suono vero, quello compatto, e il tempo per
			riconoscerli si guadagna lasciando molto più silenzio fra una lettera e l'altra.
			Quindi wpm è la velocità dei caratteri e farnsworth quella d'insieme, e la seconda
			è sempre minore o uguale alla prima. È il modo in cui il Farnsworth si esprime
			dappertutto: due numeri, per esempio 18 wpm di carattere e 5 effettivi.
			Cosa non tocca: dentro il carattere non cambia niente. Punto, linea e spazio fra
			simboli restano esattamente quelli che i pesi p, l e s hanno deciso, e la forma
			della singola lettera è la stessa campione per campione, con e senza Farnsworth.
			Ad allungarsi sono soltanto lo spazio fra lettere e quello fra parole.
			Come lo ottiene: le due spaziature si calcolano una volta sola, sulla parola
			campione PARIS con il suo spazio finale, e non dipendono da cosa il messaggio
			contiene. È il punto del metodo, perché chi impara deve sentire sempre la stessa
			distanza fra le lettere, che gli si mandino delle e o degli zeri.
			Delle cinquanta unità di PARIS, trentuno stanno dentro i caratteri, cioè dieci
			punti, quattro linee e nove spazi fra simboli, e diciannove stanno nelle spaziature,
			cioè tre per ognuno dei quattro spazi fra lettere e sette per quello fra parole.
			Il tempo dei caratteri lo decidono i pesi; quanto manca per far durare PARIS 1,2 per
			cinquanta diviso farnsworth si divide in quelle diciannove quote.
			È la formula ARRL, scritta in modo da non presupporre i pesi standard: con l 30,
			s 50 e p 50 dà esattamente i suoi stessi numeri, e con pesi qualsiasi continua a
			valere perché il tempo dei caratteri lo misura invece di darlo per noto.
			Un messaggio di un carattere solo non ha spaziature: lì il Farnsworth non ha dove
			agire e non cambia niente, senza che questo sia un errore.
			Quando pausa è None, la pausa del trattino basso vale uno spazio fra parole, quindi
			segue anche lei l'allargamento; con pausa a un numero resta quei millesimi esatti.
			Errori: farnsworth maggiore di wpm non viene suonato, perché il Farnsworth rallenta
			e non accelera. Non viene suonato nemmeno quando il peso s ha già allargato le
			spaziature oltre quello che la velocità effettiva chiesta consentirebbe, perché per
			accontentarla bisognerebbe stringerle sotto il peso: in quel caso il messaggio
			d'errore dice fin dove si può arrivare con quei pesi.
	Returns:
		dict: Se get_map=True, restituisce una copia del dizionario della mappa Morse.
		tuple[PlaybackHandle, float]: Un oggetto PlaybackHandle e rwpm, la velocità effettiva in wpm.
			rwpm si ricava dalla durata davvero prodotta secondo la definizione PARIS, cioè
			velocità uguale 1,2 per le unità standard del messaggio diviso la durata in secondi.
			Con i pesi standard, cioè l 30, s 50 e p 50, coincide con wpm.
			Con farnsworth è la velocità effettiva, cioè quella d'insieme, e non quella dei
			caratteri. Lì rwpm cambia significato per una ragione precisa: le spaziature
			del Farnsworth non sono proporzionali al testo, quindi la velocità di questo
			testo non è più la velocità, e lo stesso settaggio darebbe 4,60 wpm su un
			messaggio di e e 12,39 su uno di zeri. Si torna allora alla definizione, che
			nel Morse è sempre stata la parola PARIS: rwpm è quanto PARIS durerebbe con i
			segmenti davvero generati, e coincide quindi con farnsworth a meno della
			quantizzazione in campioni.
			Il PlaybackHandle espone tutte e quattro le grandezze: wpm_caratteri, cioè wpm;
			wpm_effettiva, cioè rwpm; farnsworth, cioè il valore chiesto; e
			wpm_del_messaggio, cioè 1,2 per le unità diviso la durata di questo testo, che
			senza Farnsworth coincide con rwpm e con il Farnsworth no.
			Il PlaybackHandle espone play, stop, wait_done(timeout=None) e l'array audio_data.
			Finché suona resta nel registro delle riproduzioni attive, quindi non serve
			conservarne il riferimento per impedire che il garbage collector lo distrugga.
		tuple[None, None]: In caso di errore di validazione parametri.
	Il mixer:
		Le riproduzioni passano da un mixer con un solo stream, sempre alimentato: quando non c'è
		niente da suonare vi si scrive silenzio, perché è il buffer che si svuota a far schioccare
		il dispositivo, non l'apertura dello stream. Dopo CWzator.SILENZIO_MAX secondi di silenzio,
		centoventi di partenza, lo stream si chiude e la scheda torna libera; al messaggio successivo
		riapre da solo, e alla fine del programma si chiude comunque.
		Fino a CWzator.VOCI_MAX messaggi possono suonare insieme, trentadue di partenza.
		VOCI_MAX, SILENZIO_MAX e scegli_dispositivo esistono già prima della prima
		riproduzione, quindi si possono leggere e cambiare all'avvio dell'applicazione, e vengono
		sommati: è così che si simula un pile-up di stazioni che chiamano tutte insieme. Quando le
		voci sono tutte occupate la più vecchia lascia il posto alla nuova. Ogni PlaybackHandle
		controlla soltanto la propria voce, quindi il suo stop non tocca le altre.
		Il mixer è stereo e ogni voce ha la sua posizione, data dal parametro pan. La sintesi resta
		monofonica: il pan si applica soltanto in riproduzione.
		Cambiando frequenza di campionamento il mixer si rifà, perché quella non si può cambiare a
		stream aperto, e le riproduzioni in corso si fermano.
	Errori:
		Non vengono stampati: il punto 3.8 chiede che una utilità li riferisca a chi l'ha
		chiamata, e in un eseguibile senza console stampare vuol dire buttarli via.
		Un errore di validazione fa restituire (None, None) e lascia il messaggio in
		CWzator.ultimo_errore. Un guasto durante la riproduzione o il salvataggio finisce
		in errore del PlaybackHandle, oltre che in CWzator.ultimo_errore.
		Con verbose=True si torna anche a stamparli su stderr, come faceva la V9.7.
	Chiusura ordinata:
		CWzator.chiudi_riproduzioni(attesa=2.0) ferma le riproduzioni ancora in corso e ne attende
		la fine. È registrata con atexit, quindi in un programma che finisce normalmente non c'è
		niente da fare; va chiamata a mano solo da chi esca per vie che saltano atexit, per esempio
		os._exit, oppure da una interfaccia grafica che chiuda la finestra mentre un messaggio suona.
	"""
	import os
	import sys
	import threading
	import wave
	from datetime import datetime

	import numpy as np
	if wv != 1:
		from scipy import signal as scipy_signal
	BLOCK_SIZE = 256
	# Gli errori si riferiscono a chi ha chiamato, non si stampano: il punto 3.8
	# del documento di refactoring lo chiede, e in un eseguibile senza console
	# stampare vuol dire buttare via il messaggio. L'ultimo errore resta qui
	# finche' non ne arriva un altro, e con verbose a vero si stampa anche.
	def _errore(testo):
		CWzator.ultimo_errore = testo
		if verbose:
			print(f"CWzator Error: {testo}", file=sys.stderr)
		return None, None
	CWzator.ultimo_errore = None
	# --- Caching MORSE_MAP sulla funzione stessa ---
	if not hasattr(CWzator, '_morse_map'):
		CWzator._morse_map = {
			"a":".-", "b":"-...", "c":"-.-.", "d":"-..", "e":".", "f":"..-.",
			"g":"--.", "h":"....", "i":"..", "j":".---", "k":"-.-", "l":".-..",
			"m":"--", "n":"-.", "o":"---", "p":".--.", "q":"--.-", "r":".-.",
			"s":"...", "t":"-", "u":"..-", "v":"...-", "w":".--", "x":"-..-",
			"y":"-.--", "z":"--..", "0":"-----", "1":".----", "2":"..---",
			"3":"...--", "4":"....-", "5":".....", "6":"-....", "7":"--...",
			"8":"---..", "9":"----.", ".":".-.-.-", "-":"-....-", ",":"--..--",
			"?":"..--..", "/":"-..-.", ";":"-.-.-.", "(":"-.--.", "[":"-.--.",
			")":"-.--.-", "]":"-.--.-", "@":".--.-.", "*":"...-.-", "+":".-.-.",
			"%":".-...", ":":"---...", "=":"-...-", '"':".-..-.", "'":".----.",
			"!":"-.-.--", "$":"...-..-", " ":"", "_":"",
			"ò":"---.", "à":".--.-", "ù":"..--", "è":"..-..",
			"é":"..-..", "ì":".---."}
	MORSE_MAP = CWzator._morse_map
	# --- Restituzione mappa Morse ---
	if get_map:
		# Una copia, non il dizionario interno: chi lo modificasse cambierebbe
		# il codice Morse per tutto il programma, e sarebbe un difetto di quelli
		# che non si trovano.
		return dict(MORSE_MAP)
	# --- Validazione parametri (DRY) ---
	if not isinstance(msg, str) or msg == "":
		return _errore("msg deve essere una stringa non vuota.")
	validations = [
		("wpm", wpm, (int,), 5, 120),
		("pitch", pitch, (int,), 130, 2800),
		("l", l, (int,), 1, 100),
		("s", s, (int,), 1, 100),
		("p", p, (int,), 1, 100),
		("fs", fs, (int,), 1, None),
		("ms", ms, (int, float), 0, None),
		("vol", vol, (int, float), 0.0, 1.0),
	]
	if pausa is not None:
		if not isinstance(pausa, (int, float)) or isinstance(pausa, bool):
			return _errore(f"pausa ({pausa}) tipo non valido.")
		if pausa < 0:
			return _errore(f"pausa ({pausa}) non puo' essere negativa.")
	for name, val, types, lo, hi in validations:
		if not isinstance(val, types):
			return _errore(f"{name} ({val}) tipo non valido.")
		if lo is not None and val < lo:
			return _errore(f"{name} ({val}) sotto il minimo [{lo}].")
		if hi is not None and val > hi:
			return _errore(f"{name} ({val}) sopra il massimo [{hi}].")
	if farnsworth is not None:
		if not isinstance(farnsworth, (int, float)) or isinstance(farnsworth, bool):
			return _errore(f"farnsworth ({farnsworth}) tipo non valido.")
		if farnsworth < 5 or farnsworth > 120:
			return _errore(f"farnsworth ({farnsworth}) fuori intervallo [5, 120].")
		if farnsworth > wpm:
			return _errore(f"farnsworth ({farnsworth}) non puo' superare wpm ({wpm}): il Farnsworth allarga le spaziature, quindi la velocita' effettiva sta sotto a quella dei caratteri, mai sopra.")
	if not (isinstance(wv, int) and wv in (1, 2, 3, 4)):
		return _errore(f"wv ({wv}) non valido [1-4].")
	if fade_mode not in ("fisso", "proporzionale", "compensato"):
		return _errore(f"fade_mode ({fade_mode}) non valido [fisso, proporzionale, compensato].")
	if fade_shape not in ("lineare", "coseno"):
		return _errore(f"fade_shape ({fade_shape}) non valido [lineare, coseno].")
	if not isinstance(pan, (int, float)) or isinstance(pan, bool):
		return _errore(f"pan ({pan}) tipo non valido.")
	if pan < -100 or pan > 100:
		return _errore(f"pan ({pan}) fuori intervallo [-100, 100].")
	if to_file and wave_output_path_file is not None:
		try:
			wave_output_path_file = os.fspath(wave_output_path_file)
		except TypeError:
			return _errore(f"wave_output_path_file ({wave_output_path_file!r}) non e' un percorso.")
	# --- Calcolo Durate ---
	T = 1.2 / float(wpm)
	dot_duration = T * (p / 50.0)
	dash_duration = 3.0 * T * (l / 30.0)
	intra_gap = T * (s / 50.0)
	letter_gap = 3.0 * T * (s / 50.0)
	word_gap = 7.0 * T * (s / 50.0)
	# --- Farnsworth: caratteri veloci, spaziature larghe ---
	# I caratteri suonano gia' alla velocita' a cui si vuole arrivare, cosi'
	# l'orecchio impara il loro suono vero, e il tempo per riconoscerli si
	# guadagna dilatando soltanto lo spazio fra lettere e fra parole. Dentro il
	# carattere non cambia niente: punto, linea e spazio fra simboli restano
	# quelli che i pesi p, l e s hanno deciso, e la forma della lettera e' la
	# stessa con e senza Farnsworth.
	# Le due spaziature si calcolano una volta sola, sulla parola campione, e
	# non dipendono da cosa il messaggio contiene: e' il punto del metodo.
	# Calcolarle sul messaggio, come si e' provato prima di arrivare qui, le
	# faceva variare da 1163 a 4470 millesimi con le stesse impostazioni, a
	# seconda che si mandassero delle e o degli zeri; chi impara deve invece
	# sentire sempre la stessa distanza fra le lettere.
	# La parola campione e' PARIS con il suo spazio finale, che vale cinquanta
	# unita': trentuno stanno dentro i caratteri, cioe' dieci punti, quattro
	# linee e nove spazi fra simboli, e diciannove stanno nelle spaziature,
	# cioe' tre per ognuno dei quattro spazi fra lettere e sette per quello fra
	# parole. Il tempo dei caratteri lo decidono i pesi; il resto, cioe' quanto
	# manca per far durare la parola campione 1,2 per cinquanta diviso la
	# velocita' effettiva, si divide in diciannove quote. E' la formula ARRL,
	# scritta in modo da non presupporre i pesi standard: con l 30, s 50 e p 50
	# da' esattamente i suoi stessi numeri, e con pesi qualsiasi continua a
	# valere perche' il tempo dei caratteri lo misura invece di darlo per noto.
	if farnsworth is not None:
		caratteri_paris = 10.0 * dot_duration + 4.0 * dash_duration + 9.0 * intra_gap
		quota = (1.2 * 50.0 / float(farnsworth) - caratteri_paris) / 19.0
		# Una quota piu' corta di uno spazio fra simboli vorrebbe dire stringere
		# le spaziature sotto quello che i pesi hanno deciso, cioe' mettere le
		# mani su s. Non si fa: si dice fin dove si puo' arrivare e decide chi
		# ha chiamato.
		if quota < intra_gap * (1.0 - 1e-9):
			massima = 60.0 / (caratteri_paris + 19.0 * intra_gap)
			return _errore(f"farnsworth ({farnsworth}) non raggiungibile: con l {l}, s {s} e p {p} la velocita' effettiva non puo' superare {massima:.2f} wpm, e per arrivarci bisognerebbe stringere le spaziature sotto i pesi.")
		letter_gap = 3.0 * quota
		word_gap = 7.0 * quota
	# --- Dissolvenza: quanto dura e quanto costa ---
	# Una rampa lunga n toglie all'elemento meta' di se' per lato, cioe' in
	# tutto quanto dura la rampa stessa. Vale per la lineare e vale identico
	# per il coseno rialzato, che ha la stessa area: la forma cambia lo
	# spettro, non la durata efficace. Siccome il costo e' in millesimi
	# assoluti, punto e linea perdono la stessa quantita' e il loro rapporto
	# si allontana da tre man mano che la velocita' sale. I due modi non
	# fissi servono a questo, e sono alternativi fra loro.
	fade_seconds = max(0.0, ms / 1000.0)
	fade_frazione = 0.0
	if dot_duration > 0:
		fade_frazione = min(0.5, fade_seconds / dot_duration)
	if fade_mode == "compensato":
		# L'elemento si allunga di quanto la rampa gli toglie, e quel tempo
		# lo prende in prestito dal silenzio che lo segue: cosi' la durata
		# efficace torna nominale senza allungare il messaggio, e il calcolo
		# di rwpm, che lavora sui pesi e non sulle durate, resta valido.
		prestito = min(fade_seconds, intra_gap * 0.5)
		dot_duration += prestito
		dash_duration += prestito
		intra_gap -= prestito
		letter_gap -= prestito
		word_gap -= prestito
	# --- Pre-generazione dei 5 segmenti base ---
	def _rampa(n):
		"""Salita da zero a uno lunga n campioni, nella forma richiesta."""
		x = np.linspace(0.0, 1.0, n, dtype=np.float32)
		if fade_shape == "coseno":
			return (0.5 - 0.5 * np.cos(np.pi * x)).astype(np.float32)
		return x
	def _generate_tone(duration):
		N = round(fs * duration)
		if N <= 0:
			return np.array([], dtype=np.int16)
		t = np.linspace(0, duration, N, endpoint=False, dtype=np.float64)
		if wv == 1:
			signal_float = np.sin(2 * np.pi * pitch * t)
		elif wv == 2:
			signal_float = scipy_signal.square(2 * np.pi * pitch * t)
		elif wv == 3:  # Triangle
			signal_float = scipy_signal.sawtooth(2 * np.pi * pitch * t, width=0.5)
		else:  # Sawtooth classica discendente
			signal_float = scipy_signal.sawtooth(2 * np.pi * pitch * t, width=0)
		signal_float = signal_float.astype(np.float32)
		if fade_mode == "proporzionale":
			fade_samples = round(N * fade_frazione)
		else:
			fade_samples = round(fs * fade_seconds)
		# Quando la rampa e' piu' lunga di meta' elemento si accorcia, non si
		# scarta. Scartarla, come faceva la V9.1, lasciava il tono con due
		# gradini netti proprio sugli elementi piu' corti, cioe' uno schiocco
		# li' dove serve piu' pulizia: sotto i due millesimi di elemento non
		# c'era piu' nessuna dissolvenza.
		fade_samples = min(fade_samples, N // 2)
		if fade_samples > 0:
			ramp = _rampa(fade_samples)
			signal_float[:fade_samples] *= ramp
			signal_float[-fade_samples:] *= ramp[::-1]
		signal_float = np.clip(signal_float * vol, -1.0, 1.0)
		return (signal_float * 32767.0).astype(np.int16)
	def _generate_silence(duration):
		N = round(fs * duration)
		return np.zeros(N, dtype=np.int16) if N > 0 else np.array([], dtype=np.int16)
	seg_dot = _generate_tone(dot_duration)
	seg_dash = _generate_tone(dash_duration)
	seg_intra = _generate_silence(intra_gap)
	seg_letter = _generate_silence(letter_gap)
	seg_word = _generate_silence(word_gap)
	# La pausa che il trattino basso produce. Senza il parametro vale uno
	# spazio fra parole alla velocita' corrente, cioe' quello che faceva fino
	# alla V9.1; con il parametro vale quei millesimi esatti, indipendenti
	# dalla velocita', per chi vuole una pausa per la testa e non per
	# l'orecchio.
	seg_pausa = seg_word if pausa is None else _generate_silence(float(pausa) / 1000.0)
	# --- Primo passaggio: pianifica i segmenti e calcola la lunghezza totale ---
	words_list = msg.lower().split()
	# Le parole che producono suono davvero: quelle che contengono almeno un
	# carattere con un codice non vuoto. Serve una definizione sola, usata sia
	# per decidere dove mettere gli spazi di parola sia per contare le unita',
	# altrimenti i due conti divergono e la velocita' annunciata non e' quella
	# che si sente.
	def _suona(parola):
		return any(MORSE_MAP.get(ch) for ch in parola)
	plan = []
	total_samples = 0
	# Unita' standard occupate dal messaggio: un punto ne vale una, una linea
	# tre, lo spazio fra simboli una, quello fra lettere tre, quello fra parole
	# sette. E' la misura con cui si definisce la velocita': la parola PARIS
	# piu' lo spazio finale ne vale cinquanta.
	standard_units = 0
	# I campioni di silenzio chiesti con il trattino basso. Restano nell'audio
	# ma non entrano nel calcolo della velocita' effettiva, ne' fra le unita'
	# ne' nella durata: se entrassero da una parte sola, la velocita'
	# annunciata scenderebbe pur restando il suono identico.
	campioni_di_pausa = 0
	for w_idx, word in enumerate(words_list):
		# Ogni trattino basso e' una pausa, dovunque si trovi. Lo spazio
		# semplice resta il separatore di parole di sempre: nella mappa hanno
		# tutti e due codice vuoto, ma solo il trattino basso fa pausa.
		for _ in range(word.count("_")):
			if seg_pausa.size:
				plan.append(seg_pausa)
				total_samples += seg_pausa.size
				campioni_di_pausa += seg_pausa.size
		lettere_sonore = [ch for ch in word if MORSE_MAP.get(ch)]
		for l_idx, letter in enumerate(lettere_sonore):
			code = MORSE_MAP[letter]
			for s_idx, symbol in enumerate(code):
				if symbol == '.':
					plan.append(seg_dot)
					total_samples += seg_dot.size
					standard_units += 1
				elif symbol == '-':
					plan.append(seg_dash)
					total_samples += seg_dash.size
					standard_units += 3
				if s_idx < len(code) - 1:
					plan.append(seg_intra)
					total_samples += seg_intra.size
					standard_units += 1
			if l_idx < len(lettere_sonore) - 1:
				plan.append(seg_letter)
				total_samples += seg_letter.size
				standard_units += 3
		if _suona(word) and any(_suona(w) for w in words_list[w_idx + 1:]):
			plan.append(seg_word)
			total_samples += seg_word.size
			standard_units += 7
	# --- Silenzio finale (5ms) ---
	silence_samples_end = round(fs * 0.005)
	if total_samples > 0 and silence_samples_end > 0:
		total_samples += silence_samples_end
	# --- Assemblaggio in array pre-allocato ---
	if total_samples > 0:
		audio = np.empty(total_samples, dtype=np.int16)
		pos = 0
		for seg in plan:
			n = seg.size
			if n > 0:
				audio[pos:pos + n] = seg
				pos += n
		if silence_samples_end > 0:
			audio[pos:pos + silence_samples_end] = 0
	else:
		audio = np.array([], dtype=np.int16)
	# --- Calcolo di rwpm, la velocita' realmente prodotta ---
	# Definizione PARIS: a X wpm si trasmette X volte al minuto la parola PARIS
	# con il suo spazio finale, che vale cinquanta unita'. Un messaggio lungo U
	# unita' dura quindi 1,2 per U diviso X secondi, e rovesciando si ha la
	# velocita' a partire dalla durata: X uguale 1,2 per U diviso la durata.
	# La durata usata qui e' quella dei campioni davvero generati, silenzio di
	# coda escluso, non una durata ricalcolata a parte. Cosi' il numero
	# annunciato non puo' discordare da cio' che si sente, qualunque cosa il
	# messaggio contenga e qualunque sia il modo della dissolvenza.
	# Fino alla V9.3 il conto si rifaceva in un secondo passaggio che percorreva
	# il messaggio con regole leggermente diverse dal primo, e i due divergevano
	# su tre casi: una parola di soli caratteri sconosciuti, un carattere a
	# codice vuoto in coda a una parola, e i messaggi di tre caratteri o meno,
	# per i quali il calcolo veniva saltato del tutto e si restituiva la
	# velocita' nominale anche quando i pesi erano tutt'altro.
	if farnsworth is None and (l, s, p) == (30, 50, 50):
		# Pesi standard e niente Farnsworth: la velocita' e' quella chiesta, e
		# l'unico scarto e' la quantizzazione in campioni, sotto il decimo di
		# per cento.
		rwpm = wpm_del_messaggio = wpm
	else:
		durata = (total_samples - silence_samples_end - campioni_di_pausa) / float(fs) if total_samples > 0 else 0.0
		if standard_units > 0 and durata > 0:
			wpm_del_messaggio = 1.2 * standard_units / durata
		else:
			wpm_del_messaggio = wpm
		rwpm = wpm_del_messaggio
	if farnsworth is not None:
		# Con il Farnsworth le spaziature non sono piu' proporzionali al testo,
		# e allora la velocita' di questo testo non e' piu' la velocita': lo
		# stesso messaggio a venti caratteri e otto effettivi darebbe 4,60 wpm
		# fatto di e e 12,39 fatto di zeri. La velocita' nel Morse e' per
		# definizione quella della parola PARIS, ed e' quella che si misura
		# qui, sui campioni dei segmenti davvero generati: dieci punti, quattro
		# linee, nove spazi fra simboli, quattro spazi fra lettere e uno fra
		# parole. Non e' il parametro ricopiato, e' cio' che la parola campione
		# durerebbe davvero se la si mandasse con questi segmenti.
		# La velocita' di questo singolo testo non si perde: sta in
		# wpm_del_messaggio del PlaybackHandle.
		campioni_paris = (10 * seg_dot.size + 4 * seg_dash.size + 9 * seg_intra.size
			+ 4 * seg_letter.size + seg_word.size)
		if campioni_paris > 0:
			rwpm = 1.2 * 50.0 * float(fs) / campioni_paris
	# --- Riproduzione, costruita una volta sola ---
	# Il mixer non e' piu' suo: dalla tappa 3 della issue 8, il 12 settembre
	# 2026, CWzator usa quello condiviso con Acusticator. Qui resta soltanto
	# l'oggetto che tiene lo stato di ogni messaggio, cioe' se sta suonando,
	# dove e' finito il file e cosa e' andato storto.
	if not hasattr(CWzator, '_PlaybackHandle'):
		CWzator._attivi = set()
		CWzator._attivi_lock = threading.Lock()
		def _chiudi_riproduzioni(attesa=2.0):
			"""Ferma le riproduzioni in corso e chiude il mixer condiviso.

			Resta per chi la chiamava: e' esportata come
			CWzator.chiudi_riproduzioni e serviva a non farsi sorprendere
			dall'interprete che si spegne con un filo dentro PortAudio. Adesso
			quel lavoro lo fa il mixer condiviso, che si registra da solo
			all'uscita; questa chiude anche lui, per chi vuole farlo prima.
			"""
			_mixer_condiviso().chiudi(attesa)
		CWzator.chiudi_riproduzioni = staticmethod(_chiudi_riproduzioni)
		class _PlaybackHandle:
			"""Lo stato di un messaggio: se sta suonando, dove e' finito il
			file, cosa e' andato storto. La riproduzione la fa il mixer
			condiviso, e questo oggetto e' il filo che lo lega a chi chiama."""
			def __init__(self, audio_data, sample_rate, block_size, pan=0, device=None, nome_api=None):
				self.audio_data = audio_data
				self.sample_rate = sample_rate
				self._block_size = block_size
				# La panoramica del mixer condiviso va da meno uno a piu' uno;
				# quella di CWzator da meno cento a piu' cento, ed e' una
				# differenza voluta che resta nella sua firma.
				self.pan = pan
				self._pan_mixer = max(-100.0, min(100.0, float(pan))) / 100.0
				self.device = device
				self.nome_api = nome_api
				self.stream = None
				self._voce = None
				# Cio' che il chiamante deve poter sapere senza leggere stderr:
				# se qualcosa e' andato storto, e dove e' finito il file WAV.
				self.errore = None
				self.file_salvato = None
				# Le velocita' del messaggio. Quella restituita da CWzator e'
				# sempre l'effettiva; qui si rileggono anche quella dei
				# caratteri, che con il Farnsworth e' un'altra cosa, il valore
				# chiesto, e la velocita' di questo singolo testo, che con il
				# Farnsworth non coincide piu' con l'effettiva.
				self.wpm_caratteri = None
				self.wpm_effettiva = None
				self.wpm_del_messaggio = None
				self.farnsworth = None
				self.is_playing = threading.Event()
				# Parte gia' concluso: chi chiede sync senza aver mai avviato
				# la riproduzione, per esempio con play a falso, non deve
				# restare appeso.
				self._finito = threading.Event()
				self._finito.set()
				self._lock = threading.Lock()
			def _segna_fine(self):
				"""Chiamato dal mixer quando l'audio di questa voce e' uscito."""
				self.is_playing.clear()
				self._finito.set()
				with CWzator._attivi_lock:
					CWzator._attivi.discard(self)
			def play(self):
				"""Manda il messaggio al mixer condiviso, che lo somma agli
				altri. Piu' messaggi possono suonare insieme e non si
				interrompono a vicenda: e' cosi' che si simula un pile-up.
				Un messaggio generato a un'altra frequenza di campionamento
				viene riportato a quella dello stream, invece di farlo
				riaprire: cosi' cambiare velocita' non zittisce piu' cio' che
				stava suonando."""
				with self._lock:
					if self.is_playing.is_set():
						return
					if self.audio_data.size == 0:
						self._finito.set()
						return
					self.is_playing.set()
					self._finito.clear()
				with CWzator._attivi_lock:
					CWzator._attivi.add(self)
				mixer = _mixer_condiviso()
				# Le due costanti di CWzator restano il posto dove si
				# impostano, e valgono sul mixer di tutti: chi le cambia
				# all'avvio, come ha sempre fatto, viene ascoltato.
				mixer._voci_max = max(1, int(CWzator.VOCI_MAX))
				mixer._silenzio = max(0.0, float(CWzator.SILENZIO_MAX))
				if self.device is not None and self.device != mixer._device:
					mixer._device = self.device
					mixer._nome_api = self.nome_api
					mixer.chiudi()
				# Il morse nasce in interi a sedici bit, il mixer lavora in
				# decimali fra meno uno e piu' uno: la divisione e' esatta e
				# non cambia un campione.
				dati = self.audio_data.astype(np.float32) / 32768.0
				self._voce = mixer.suona(dati, fs=self.sample_rate,
										 pan=self._pan_mixer, a_fine=self._segna_fine)
				self.stream = mixer._stream
				if self._voce is None:
					self.errore = mixer.ultimo_errore or "il mixer non ha accettato il messaggio"
					CWzator.ultimo_errore = self.errore
					self._segna_fine()
			def wait_done(self, timeout=None):
				"""Attende la fine della riproduzione corrente.
				Con timeout in secondi smette di attendere allo scadere e
				torna comunque: senza, come prima, aspetta quanto serve."""
				self._finito.wait(timeout)
			def stop(self):
				"""Toglie questo messaggio dal mixer. Gli altri proseguono."""
				if self._voce is not None:
					_mixer_condiviso().ferma(self._voce)
				self._segna_fine()
			def __del__(self):
				"""Cleanup automatico: ferma la riproduzione se l'oggetto viene distrutto."""
				try:
					self.is_playing.clear()
				except Exception:  # noqa: BLE001, S110 - __del__ gira anche mentre l'interprete si spegne, e li' non c'e' piu' niente da salvare
					pass
		CWzator._PlaybackHandle = _PlaybackHandle
	# --- Creazione Oggetto e Avvio Playback ---
	PlaybackHandle = CWzator._PlaybackHandle
	try:
		device, nome_api = scegli_dispositivo_audio(api)
	except ValueError as e:
		return _errore(str(e))
	play_obj = PlaybackHandle(audio, fs, BLOCK_SIZE, pan, device, nome_api)
	play_obj.wpm_caratteri = wpm
	play_obj.wpm_effettiva = rwpm
	play_obj.wpm_del_messaggio = wpm_del_messaggio
	play_obj.farnsworth = farnsworth
	# Il registro delle riproduzioni attive, che play riempie e il thread
	# svuota, tiene vivo l'oggetto finche' suona e serve alla chiusura
	# ordinata. Sostituisce _last_play_obj, che teneva in memoria l'ultimo
	# buffer per tutta la vita del processo anche a suono finito da un'ora.
	if play:
		play_obj.play()
	# --- Salvataggio File ---
	if to_file:
		# Nome neutro: portava scritto dentro il nome di una applicazione che non
		# e' questa libreria. E la cartella di chi ha chiamato, non la directory
		# di lavoro: un'utilita' non deve indovinare dove stanno le cose da dove
		# il programma e' stato lanciato. Sono due richieste del punto 3.8.
		default_name = f"Morse {datetime.now().strftime('%Y%m%d%H%M%S')}.wav"  # noqa: DTZ005 - ora locale: il nome lo legge chi sta davanti
		default_dir = _cartella_chiamante(1)
		if wave_output_path_file is not None:
			given = wave_output_path_file.strip()
			given_dir = os.path.dirname(given)
			given_file = os.path.basename(given)
			if given_dir and given_file:
				filename = given
			elif given_dir and not given_file:
				filename = os.path.join(given_dir, default_name)
			elif not given_dir and given_file:
				filename = os.path.join(default_dir, given_file)
			else:
				filename = os.path.join(default_dir, default_name)
		else:
			filename = os.path.join(default_dir, default_name)
		try:
			target_dir = os.path.dirname(filename)
			if target_dir and not os.path.exists(target_dir):
				os.makedirs(target_dir, exist_ok=True)
			with wave.open(filename, 'wb') as wf:
				wf.setnchannels(1)
				wf.setsampwidth(2)
				wf.setframerate(fs)
				wf.writeframes(audio.tobytes())
			play_obj.file_salvato = os.path.abspath(filename)
		except (OSError, ValueError, wave.Error) as e:
			play_obj.errore = f"salvataggio del file non riuscito: {e}"
			CWzator.ultimo_errore = play_obj.errore
			if verbose:
				print(f"CWzator Error: {play_obj.errore}", file=sys.stderr)
	# --- Gestione Sync ---
	if sync:
		play_obj.wait_done()
	return play_obj, rwpm
CWzator.scegli_dispositivo = staticmethod(scegli_dispositivo_audio)
# Gli elenchi stanno anche qui, accanto alla scelta: chi cerca come far
# scegliere l'uscita all'utente guarda dentro CWzator, che e' l'utilita' che
# conosce, non fra le funzioni di modulo che non sa di avere.
CWzator.elenco_dispositivi = staticmethod(elenco_dispositivi_audio)
CWzator.elenco_interfacce = staticmethod(elenco_interfacce_audio)
# Quanti messaggi possono sovrapporsi. Sommarli e' il modo giusto: fino alla
# V9.5 ognuno apriva il proprio stream e la somma la faceva il sistema
# operativo, senza che nessuno la controllasse. Trentadue bastano a simulare
# un pile-up di stazioni che chiamano insieme; quando sono tutte occupate la
# piu' vecchia lascia il posto, cosi' l'ultimo messaggio si sente sempre.
# Sta qui e non dentro la funzione perche' chi la cambia lo fa all'avvio,
# prima di suonare: nascendo alla prima riproduzione si sarebbe vista
# sovrascrivere senza accorgersene. Dal 12 settembre 2026 vale sul mixer
# condiviso, quindi anche su cio' che vi suona Acusticator.
CWzator.VOCI_MAX = 32
# Dopo questo silenzio lo stream si chiude e la scheda torna libera; al
# messaggio successivo riapre da solo. Tenerlo aperto non costa CPU, misurato
# zero per cento, ma impegna il dispositivo e gli impedisce il risparmio
# energetico. E' la stessa soglia che usa Acusticator.
CWzator.SILENZIO_MAX = 120.0

_MAZZO_SEMI_FRANCESI = ("Cuori", "Quadri", "Fiori", "Picche")
_MAZZO_SEMI_ITALIANI = ("Bastoni", "Spade", "Coppe", "Denari")
_MAZZO_VALORI_FRANCESI = (("Asso", 1),) + tuple((str(i), i) for i in range(2, 11)) + (("Jack", 11), ("Regina", 12), ("Re", 13))
_MAZZO_VALORI_ITALIANI = (("Asso", 1),) + tuple((str(i), i) for i in range(2, 8)) + (("Fante", 8), ("Cavallo", 9), ("Re", 10))
_MAZZO_VALORI_DESCRIZIONE = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 11: 'J', 12: 'Q', 13: 'K'}
_MAZZO_SEMI_DESCRIZIONE = {"Cuori": 'C', "Quadri": 'Q', "Fiori": 'F', "Picche": 'P',
	"Bastoni": 'B', "Spade": 'S', "Coppe": 'O', "Denari": 'D'} # 'O' per Coppe
class Mazzo:
	'''
	V6.1.0 di martedì 8 settembre 2026 - Gabriele Battaglia (IZ4APU), Gemini 2.5 & ClaudIA (Claude Fable 5.1, UltraCode)
	Dalla V6.1.0 il costruttore accetta lettere_semi, per scegliere le lettere
	dei semi nella descrizione breve dove quelle predefinite non vanno bene:
	la O delle Coppe, scelta per non confonderle con i Cuori, non e' la C che
	portano le carte segnate in braille di Gabriele.
	Rappresenta un mazzo di carte italiano o francese, con supporto per mazzi
	multipli, mescolamento, pesca con rimescolamento automatico degli scarti, e
	gestione flessibile delle carte.
	Non produce output diretto (print), ma restituisce valori o stringhe
	informative. Fino alla V5.2 la promessa era scritta qui e smentita da pesca,
	che stampava due righe: adesso pesca lo dice con l'attributo
	ultimo_rimescolo, che chi vuole legge e chi non vuole ignora.
	Le carte pescate escono dal mazzo e le tiene chi le ha pescate: dalla V6.0.0
	la classe non finge piu' di tenerne l'elenco. Fino alla V5.2 quattro metodi
	su dodici, cioe' rimescola_scarti, aggiungi_jolly, rimuovi_jolly e
	mostra_carte, leggevano una lista pescate che __init__ non ha mai creato, e
	sollevavano AttributeError alla prima chiamata, sempre. Chi vuole rimettere
	nel mazzo le carte che ha in mano le passa a scarta_carte e poi chiama
	rimescola_scarti, che e' la strada che gia' esisteva e che funziona.
	'''
	import random
	from collections import namedtuple
	Carta = namedtuple("Carta", ["id", "nome", "valore", "seme_nome", "seme_id", "desc_breve"])
	def __init__(self, tipo_francese=True, num_mazzi=1, lettere_semi=None):
		'''
		Inizializza uno o più mazzi di carte.
		Parametri:
		- tipo_francese (bool): True per mazzo francese (default), False per mazzo italiano.
		- num_mazzi (int): Numero di mazzi da includere (default 1). Deve essere >= 1.
		- lettere_semi (dict): da nome del seme a lettera per la descrizione
		  breve, sovrapposto alla tabella predefinita, che resta valida per i
		  semi non nominati. Con None, il predefinito, le lettere sono quelle
		  di sempre. Solleva ValueError se non e' un dizionario.
		'''
		if not isinstance(num_mazzi, int) or num_mazzi < 1:
			raise ValueError("Il numero di mazzi deve essere un intero maggiore o uguale a 1.")
		if lettere_semi is not None and not isinstance(lettere_semi, dict):
			raise ValueError("lettere_semi deve essere un dizionario da nome del seme a lettera, oppure None.")
		self.tipo_francese = tipo_francese
		self.num_mazzi = num_mazzi
		self.lettere_semi = dict(_MAZZO_SEMI_DESCRIZIONE)
		if lettere_semi:
			self.lettere_semi.update({str(k): str(v) for k, v in lettere_semi.items()})
		# Liste per tracciare lo stato delle carte
		self.carte = [] # Mazzo principale da cui pescare
		self.scarti = [] # Pila degli scarti, possono essere rimescolati
		self.scarti_permanenti = [] # Carte rimosse permanentemente
		# Vero se l'ultima pesca ha dovuto rimescolare gli scarti. Sostituisce le
		# due righe che pesca stampava per conto suo fino alla V5.2.
		self.ultimo_rimescolo = False
		self._costruisci_mazzo()
	def _costruisci_mazzo(self):
		'''
		(Metodo privato) Costruisce il mazzo di carte in base al tipo e al numero di mazzi.
		L'identificativo del seme va da 1 a 4 per entrambi i tipi di mazzo: a
		distinguere un mazzo italiano da uno francese e' il nome del seme.
		'''
		self.carte = [] # Resetta il mazzo
		semi = _MAZZO_SEMI_FRANCESI if self.tipo_francese else _MAZZO_SEMI_ITALIANI
		valori = _MAZZO_VALORI_FRANCESI if self.tipo_francese else _MAZZO_VALORI_ITALIANI
		id_carta_counter = 1
		for _ in range(self.num_mazzi):
			for id_seme, nome_seme in enumerate(semi, 1):
				for nome_valore, valore_num in valori:
					desc_val = _MAZZO_VALORI_DESCRIZIONE.get(valore_num, '?')
					desc_seme = self.lettere_semi.get(nome_seme, '?')
					carta = self.Carta(id=id_carta_counter,
						nome=f"{nome_valore} di {nome_seme}",
						valore=valore_num,
						seme_nome=nome_seme,
						seme_id=id_seme,
						desc_breve=f"{desc_val}{desc_seme}")
					self.carte.append(carta)
					id_carta_counter += 1
	def mescola_mazzo(self):
		'''
		Mescola le carte nel mazzo principale (self.carte).
		Non restituisce nulla.
		'''
		if not self.carte:
			return # Non fare nulla se il mazzo è vuoto
		self.random.shuffle(self.carte)
	def pesca(self, quante=1):
		'''
		Pesca carte dal mazzo principale. Se le carte nel mazzo non sono sufficienti,
		rimescola automaticamente gli scarti prima di pescare, e in quel caso
		lascia vero l'attributo ultimo_rimescolo, che chi vuole avvisare l'utente
		legge subito dopo la chiamata. Fino alla V5.2 il rimescolamento veniva
		annunciato da due print, che in una applicazione con interfaccia grafica
		nessuno leggeva.
		Le carte pescate escono dal mazzo e le tiene chi le ha pescate: per
		rimetterle in gioco si passano a scarta_carte.
		Parametri:
		- quante (int): Numero di carte da pescare (default 1).
		Ritorna:
		- list[Carta]: Lista delle carte pescate. Può contenere meno carte di 'quante'
									 se il mazzo e gli scarti combinati non sono sufficienti.
		'''
		if quante < 0:
			raise ValueError("Il numero di carte da pescare deve essere non negativo.")
		self.ultimo_rimescolo = False
		if quante == 0:
			return []
		if len(self.carte) < quante and self.scarti:
			self.carte.extend(self.scarti)
			self.scarti = []
			self.mescola_mazzo()
			self.ultimo_rimescolo = True
		# Ora procedi con la pesca
		num_da_pescare = min(quante, len(self.carte))
		carte_pescate_ora = []
		if num_da_pescare > 0:
			for _ in range(num_da_pescare):
				carte_pescate_ora.append(self.carte.pop())
		return carte_pescate_ora
	def scarta_carte(self, carte_da_scartare):
		'''
		Aggiunge una lista di carte alla pila degli scarti.
		Parametri:
		- carte_da_scartare (list[Carta]): Lista di oggetti Carta da spostare negli scarti.
		'''
		if not carte_da_scartare:
			return
		self.scarti.extend(carte_da_scartare)
	def rimescola_scarti(self):
		'''
		Rimette le carte dalla pila degli scarti nel mazzo principale e mescola.
		Non reintegra le carte scartate permanentemente.
		Fino alla V5.2 accettava include_pescate, che leggeva una lista mai
		creata: chiamare questo metodo, in qualunque modo, sollevava sempre
		AttributeError. Il parametro e' stato tolto perche' nessun programma
		poteva usarlo. Chi vuole rimettere in gioco le carte che ha in mano le
		passa prima a scarta_carte.
		Ritorna:
		- str: Messaggio che riepiloga l'operazione.
		'''
		num_scarti = len(self.scarti)
		if num_scarti == 0:
			return "Nessuno scarto da reintegrare."
		self.carte.extend(self.scarti)
		self.scarti = []
		self.mescola_mazzo()
		return f"{num_scarti} scarti reintegrati. Nel mazzo ora {len(self.carte)} carte."
	def rimuovi_semi(self, semi_id_da_rimuovere, permanente=False):
		'''
		Rimuove dal mazzo principale (self.carte) tutte le carte con i semi specificati.
		Le carte rimosse vengono spostate negli scarti temporanei o permanenti.
		Parametri:
		- semi_id_da_rimuovere (list[int]): Lista di ID numerici dei semi da rimuovere.
		- permanente (bool): Se True, sposta in scarti_permanenti, altrimenti in scarti (default False).
		Ritorna:
		- int: Numero di carte rimosse dal mazzo principale.
		'''
		destinazione = self.scarti_permanenti if permanente else self.scarti
		def condizione(carta):
			return carta.seme_id in semi_id_da_rimuovere
		carte_rimosse = self._rimuovi_carte_da_lista(self.carte, condizione, destinazione)
		return len(carte_rimosse)
	def rimuovi_valori(self, valori_da_rimuovere, permanente=True):
		'''
		Rimuove dal mazzo principale (self.carte) tutte le carte con i valori specificati.
		Le carte rimosse vengono spostate negli scarti permanenti o temporanei.
		Parametri:
		- valori_da_rimuovere (list[int]): Lista di valori numerici da rimuovere.
		- permanente (bool): Se True, sposta in scarti_permanenti (default), altrimenti in scarti.
		Ritorna:
		- int: Numero di carte rimosse dal mazzo principale.
		'''
		destinazione = self.scarti_permanenti if permanente else self.scarti
		def condizione(carta):
			return carta.valore in valori_da_rimuovere
		carte_rimosse = self._rimuovi_carte_da_lista(self.carte, condizione, destinazione)
		return len(carte_rimosse)
	def aggiungi_jolly(self, quanti_per_mazzo=2):
		'''
		Aggiunge jolly al mazzo principale fino a raggiungere il numero corretto
		per ogni mazzo originale (quanti_per_mazzo * num_mazzi).
		Funziona solo per mazzi di tipo francese. Jolly esistenti non vengono duplicati.
		Parametri:
		- quanti_per_mazzo (int): Numero di jolly desiderato per ciascun mazzo originale (default 2).
		Ritorna:
		- str: Messaggio che indica quanti jolly sono stati aggiunti o se erano già presenti.
		'''
		if not self.tipo_francese:
			return "I jolly possono essere aggiunti solo ai mazzi di tipo francese."
		if quanti_per_mazzo < 0:
			# Non ha senso avere un numero negativo di jolly per mazzo
			return "Numero di jolly per mazzo non valido (deve essere >= 0)."

		# Calcola il numero totale di jolly che dovrebbero esserci
		jolly_attesi_totali = self.num_mazzi * quanti_per_mazzo
		# Controlla quanti jolly esistono già in *tutte* le liste
		all_cards = self.carte + self.scarti + self.scarti_permanenti
		jolly_esistenti_count = sum(1 for c in all_cards if c.nome == "Jolly")
		# Determina quanti jolly mancano (se ce ne sono)
		jolly_da_aggiungere = jolly_attesi_totali - jolly_esistenti_count
		if jolly_da_aggiungere <= 0:
			# Se non ne mancano o ce ne sono addirittura di più (improbabile ma gestito)
			return f"Nessun nuovo jolly aggiunto (numero richiesto: {jolly_attesi_totali}, già presenti: {jolly_esistenti_count})."
		# Se dobbiamo aggiungere jolly:
		# Trova l'ID massimo attuale per continuare la sequenza
		max_id = 0
		if all_cards:
			ids = [c.id for c in all_cards if c.id is not None]
			if ids:
				max_id = max(ids)
		jolly_aggiunti_count = 0
		for i in range(jolly_da_aggiungere):
			jolly_id = max_id + 1 + i
			# Crea il jolly e aggiungilo al mazzo principale
			jolly = self.Carta(id=jolly_id, nome="Jolly", valore=None, seme_nome="N/A", seme_id=0, desc_breve="XY")
			self.carte.append(jolly)
			jolly_aggiunti_count += 1
			# Aggiorna max_id per il prossimo ciclo (se ce n'è più di uno)
			max_id = jolly_id
		if jolly_aggiunti_count > 0:
			return f"Aggiunti {jolly_aggiunti_count} jolly al mazzo principale."
		else:
			# Questo caso non dovrebbe verificarsi data la logica precedente, ma per sicurezza
			return "Nessun nuovo jolly aggiunto."
	def rimuovi_jolly(self, permanente=False):
		'''
		Rimuove tutti i jolly dal mazzo, e anche dagli scarti se permanente e' vero,
		e li sposta nella destinazione appropriata (scarti temporanei o permanenti).
		I jolly gia' pescati non si toccano, perche' sono usciti dal mazzo e li
		tiene chi li ha pescati.
		Parametri:
		- permanente (bool): Se True, sposta in scarti_permanenti e pulisce anche gli scarti temporanei.
		                     Se False, sposta solo in scarti temporanei.
		Ritorna:
		- str: Messaggio che indica quanti jolly unici sono stati rimossi e dove sono stati spostati.
		'''
		jolly_rimossi_total_obj = [] # Lista per collezionare gli oggetti jolly rimossi
		destinazione = self.scarti_permanenti if permanente else self.scarti
		tipo_destinazione = "permanenti" if permanente else "temporanei"
		def condizione(carta):
			return carta.nome == "Jolly"
		# Helper per evitare codice duplicato e gestire la collezione degli oggetti
		def _processa_lista(lista_sorgente):
			carte_rimosse = self._rimuovi_carte_da_lista(lista_sorgente, condizione, destinazione)
			jolly_rimossi_total_obj.extend(carte_rimosse)
		# Rimuove da self.carte
		_processa_lista(self.carte)
		# Rimuove da self.scarti SOLO SE la destinazione NON è self.scarti
		# Questo previene che gli elementi appena aggiunti a self.scarti vengano rimossi di nuovo.
		if permanente:
			_processa_lista(self.scarti) # Pulisce gli scarti temporanei spostando i jolly in quelli permanenti
		# Calcola quanti jolly unici sono stati effettivamente spostati
		# Utile se per errore un jolly fosse presente in più liste (non dovrebbe accadere)
		num_rimossi_unici = len({j.id for j in jolly_rimossi_total_obj})
		if num_rimossi_unici > 0:
			return f"Rimossi {num_rimossi_unici} jolly unici. Spostati negli scarti {tipo_destinazione}."
		else:
			return "Nessun jolly trovato da rimuovere."
	def _rimuovi_carte_da_lista(self, lista_sorgente, condizione, destinazione):
		''' Funzione helper per rimuovere carte da una lista in base a una condizione. '''
		carte_da_mantenere = []
		carte_rimosse = []
		for carta in lista_sorgente:
			if condizione(carta):
				carte_rimosse.append(carta)
			else:
				carte_da_mantenere.append(carta)
		if carte_rimosse:
			# Aggiunge gli elementi rimossi alla lista di destinazione
			destinazione.extend(carte_rimosse)
			# Modifica la lista originale inplace rimuovendo gli elementi
			lista_sorgente[:] = carte_da_mantenere
			# Ritorna la lista degli elementi rimossi
		return carte_rimosse
	def stato_mazzo(self):
		''' Ritorna una stringa che riepiloga lo stato attuale del mazzo.
		Fino alla V5.2 era lunga sessantuno caratteri e teneva i tre numeri
		divisi da barre verticali, cioe' un allineamento a colonne: adesso e' una
		frase di una trentina di caratteri, che sta in un blocco solo sul display
		braille.
		'''
		return (f"Mazzo {len(self.carte)}, scarti {len(self.scarti)}, "
				f"permanenti {len(self.scarti_permanenti)}.")
	def __len__(self):
		''' Ritorna il numero di carte attualmente nel mazzo principale (self.carte). '''
		return len(self.carte)
	def __str__(self):
		''' Rappresentazione stringa dell'oggetto Mazzo (mostra lo stato). '''
		return self.stato_mazzo()
	def mostra_carte(self, lista='mazzo'):
		'''
		Restituisce una stringa con le descrizioni brevi delle carte
		in una specifica lista (mazzo, scarti, permanenti).
		Fino alla V5.2 accettava anche 'pescate', che leggeva una lista mai
		creata e sollevava sempre AttributeError.
		Parametri:
		- lista (str): Nome della lista ('mazzo', 'scarti', 'permanenti').
		Ritorna:
		- str: Stringa formattata con le carte o messaggio di lista vuota/non valida.
		'''
		target_lista_ref = None
		nome_lista = ""
		if lista == 'mazzo':
			target_lista_ref = self.carte
			nome_lista = "Mazzo Principale"
		elif lista == 'scarti':
			target_lista_ref = self.scarti
			nome_lista = "Pila Scarti"
		elif lista == 'permanenti':
			target_lista_ref = self.scarti_permanenti
			nome_lista = "Scarti Permanenti"
		else:
			return "Lista non valida. Scegli tra: 'mazzo', 'scarti', 'permanenti'."
		if not target_lista_ref:
			return f"Nessuna carta nella lista '{nome_lista}'."
		# Usa la lista referenziata per ottenere le carte
		return f"{nome_lista} ({len(target_lista_ref)}): " + ", ".join([c.desc_breve for c in target_lista_ref])

# Tabelle di key. Sono costanti di modulo perche' key viene chiamata anche
# cento volte al secondo da chi sorveglia la tastiera senza fermarsi, e
# ricostruirle a ogni chiamata era lavoro sprecato. I codici di Windows sono
# stati verificati uno per uno contro la libreria di runtime, iniettando gli
# eventi di tastiera nella console con WriteConsoleInput.
# Windows, prefisso \x00: tastierino a blocco numerico spento, tasti funzione
# con e senza modificatori, Ctrl e Alt con i tasti dedicati di navigazione,
# che la libreria di runtime manda con questo prefisso quando c'e' Alt, e Alt
# con lettere e cifre.
# Windows, codici di tasto virtuale: ogni record della console porta il
# codice del tasto, lo stato dei modificatori e il carattere gia' tradotto,
# quindi non serve piu' la tabella di codici che getwch ereditava dal DOS.
_KEY_VK_BASE = {
	0x26: 'up', 0x28: 'down', 0x25: 'left', 0x27: 'right',
	0x24: 'home', 0x23: 'end', 0x21: 'pageup', 0x22: 'pagedown',
	0x2d: 'insert', 0x2e: 'delete', 0x0c: 'center',
	0x0d: 'enter', 0x1b: 'esc', 0x08: 'backspace', 0x09: 'tab',
}
for _numero in range(1, 25):
	_KEY_VK_BASE[0x6f + _numero] = f"f{_numero}"
del _numero
# I tasti di navigazione esistono in due esemplari: quelli dedicati portano
# il contrassegno di tasto esteso, quelli del tastierino a blocco numerico
# spento no, e sono gli unici che prendono il prefisso pad.
_KEY_VK_TASTIERINO = frozenset(('up', 'down', 'left', 'right', 'home', 'end',
	'pageup', 'pagedown', 'insert', 'delete', 'center'))
# I quattro tasti di servizio, premuti da soli, tornano come caratteri.
_KEY_VK_SERVIZIO = {0x0d: '\r', 0x1b: '\x1b', 0x08: '\x08', 0x09: '\t'}
# Cio' che da solo non e' un tasto: modificatori, blocchi e tasti di sistema.
# Premerli non deve svegliare chi aspetta.
_KEY_VK_SOLO_MODIFICATORE = frozenset((0x00, 0x10, 0x11, 0x12, 0x14, 0x90, 0x91,
	0x5b, 0x5c, 0x5d, 0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5))
# Unix: sequenze che seguono un Escape, nelle forme di xterm, di vt e di rxvt.
_KEY_ANSI = {
	'[A': 'up', '[B': 'down', '[C': 'right', '[D': 'left',
	'[H': 'home', '[F': 'end', 'OH': 'home', 'OF': 'end',
	'[1~': 'home', '[4~': 'end', '[7~': 'home', '[8~': 'end',
	'[5~': 'pageup', '[6~': 'pagedown', '[2~': 'insert', '[3~': 'delete',
	'[E': 'pad-center', '[Z': 'shift-tab',
	'OP': 'f1', 'OQ': 'f2', 'OR': 'f3', 'OS': 'f4',
	'[11~': 'f1', '[12~': 'f2', '[13~': 'f3', '[14~': 'f4',
	'[15~': 'f5', '[17~': 'f6', '[18~': 'f7', '[19~': 'f8',
	'[20~': 'f9', '[21~': 'f10', '[23~': 'f11', '[24~': 'f12',
}
# Unix con modificatori: [1;5A e' Ctrl+Su, [3;3~ e' Alt+Canc, [1;2P e' Shift+F1.
_KEY_ANSI_LETTERE = {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left', 'H': 'home', 'F': 'end', 'P': 'f1', 'Q': 'f2', 'R': 'f3', 'S': 'f4'}
_KEY_ANSI_TILDE = {
	'1': 'home', '2': 'insert', '3': 'delete', '4': 'end', '5': 'pageup', '6': 'pagedown', '7': 'home', '8': 'end',
	'11': 'f1', '12': 'f2', '13': 'f3', '14': 'f4', '15': 'f5', '17': 'f6', '18': 'f7', '19': 'f8',
	'20': 'f9', '21': 'f10', '23': 'f11', '24': 'f12',
}
_KEY_ANSI_MODIFICATORI = {'2': 'shift', '3': 'alt', '4': 'shift-alt', '5': 'ctrl', '6': 'shift-ctrl', '7': 'alt-ctrl', '8': 'shift-alt-ctrl'}

def _key_sequenza_ansi(seq):
	"""Traduce cio' che su Unix segue un Escape in un nome di tasto.
	Restituisce il nome quando lo riconosce, alt- piu' il carattere quando
	l'Escape e' seguito da un solo carattere stampabile, cioe' Alt piu' quel
	tasto, ed esc- piu' la sequenza grezza in tutti gli altri casi, cosi' che
	un tasto nuovo si scopra premendolo."""
	import re
	nome = _KEY_ANSI.get(seq)
	if nome:
		return nome
	trovato = re.fullmatch(r'\[(\d+)(?:;(\d+))?([A-Z~])', seq)
	if trovato:
		numero, modificatore, finale = trovato.groups()
		if finale == '~':
			base = _KEY_ANSI_TILDE.get(numero)
		else:
			base = _KEY_ANSI_LETTERE.get(finale) if numero == '1' else None
		if base:
			if not modificatore or modificatore == '1':
				return base
			return f"{_KEY_ANSI_MODIFICATORI.get(modificatore, 'mod' + modificatore)}-{base}"
	if len(seq) == 1 and seq.isprintable():
		return f"alt-{seq}"
	return f"esc-{seq}"

def _key_carattere(ch):
	"""Nome di un carattere singolo, uguale sui due sistemi: Ctrl piu' lettera
	diventa ctrl-a fino a ctrl-z, Ctrl+C interrompe con KeyboardInterrupt come
	in qualunque programma da console, tutto il resto torna com'e', compresi
	Invio, Escape, Backspace e Tab che restano i loro caratteri."""
	if ch == '\x03':
		raise KeyboardInterrupt
	if '\x01' <= ch <= '\x1a' and ch not in ('\x08', '\t', '\r'):
		return f"ctrl-{chr(ord(ch) + 96)}"
	return ch

def _key_con_modificatori(base, shift, alt, ctrl):
	"""I prefissi nell'ordine shift, alt, ctrl, che e' quello che il ramo Unix
	usa gia' per le sue sequenze, cosi' i due sistemi dicono lo stesso nome."""
	if ctrl:
		base = f"ctrl-{base}"
	if alt:
		base = f"alt-{base}"
	if shift:
		base = f"shift-{base}"
	return base

def _key_nome_windows(vk, stato, carattere):
	"""Il nome di un tasto a partire da cio' che la console riferisce: codice
	del tasto, stato dei modificatori e carattere gia' tradotto.
	Restituisce None per cio' che non va consegnato a chi aspetta, cioe' i
	modificatori premuti da soli e i tasti morti, che danno prima un record
	senza carattere e poi un secondo record con il carattere composto.
	L'ordine delle regole conta: ognuna copre un caso che le successive
	rovinerebbero, ed e' scelto per restituire gli stessi nomi della V7.0.0
	ovunque quella sapesse darne uno."""
	if vk in _KEY_VK_SOLO_MODIFICATORE:
		return None
	shift = bool(stato & 0x0010)
	ctrl = bool(stato & 0x000c)
	alt = bool(stato & 0x0003)
	esteso = bool(stato & 0x0100)
	# AltGr e' Ctrl sinistro piu' Alt destro, e sulle tastiere italiane fa la
	# chiocciola, il cancelletto e le parentesi quadre: e' un simbolo, non una
	# combinazione, e va riconosciuto prima di ogni altra regola.
	if (stato & 0x0001) and (stato & 0x0008) and carattere >= ' ':
		return carattere
	# Ctrl piu' lettera arriva gia' come carattere di controllo, e da li'
	# viene anche ctrl-j di Ctrl+Invio, che la V7.0.0 dava cosi'. Backspace,
	# Tab e Invio sono esclusi perche' hanno un nome proprio, piu' avanti.
	if ctrl and '\x01' <= carattere <= '\x1a' and carattere not in ('\x08', '\t', '\r'):
		return _key_carattere(carattere)
	base = _KEY_VK_BASE.get(vk)
	if base is not None:
		if not (shift or alt or ctrl):
			nudo = _KEY_VK_SERVIZIO.get(vk)
			if nudo is not None:
				return nudo
		if base in _KEY_VK_TASTIERINO and not esteso:
			base = f"pad-{base}" if base != 'center' else "pad-center"
		return _key_con_modificatori(base, shift, alt, ctrl)
	# Alt o Ctrl con una lettera o una cifra non producono carattere, quindi
	# il nome si costruisce dal codice del tasto.
	if (alt or ctrl) and (0x30 <= vk <= 0x39 or 0x41 <= vk <= 0x5a):
		return _key_con_modificatori(chr(vk).lower(), shift, alt, ctrl)
	if carattere and carattere != '\x00':
		return _key_carattere(carattere)
	# Senza carattere e senza modificatori non c'e' niente da consegnare: e'
	# un tasto morto, che sara' seguito dal record con il carattere composto,
	# o un tasto che la console non traduce, come quelli multimediali, che
	# getwch non consegnava affatto. Con un modificatore invece il nome si
	# da' lo stesso, cosi' un tasto nuovo si scopre premendolo.
	if not (shift or alt or ctrl):
		return None
	return _key_con_modificatori(f"special-vk-{vk:02x}", shift, alt, ctrl)

_KEY_CONSOLE = None

def _key_strutture():
	"""Le strutture della console di Windows, costruite una volta sola alla
	prima chiamata: in GBUtils gli import stanno dentro le funzioni, quindi
	ctypes non e' disponibile quando il modulo viene letto.
	Restituisce la libreria di sistema, il manico della console e la classe
	del record. Solleva EOFError se una console non c'e'."""
	global _KEY_CONSOLE
	import ctypes
	import ctypes.wintypes as w
	if _KEY_CONSOLE is None:
		class _KeyUChar(ctypes.Union):
			_fields_ = [("UnicodeChar", w.WCHAR), ("AsciiChar", ctypes.c_char)]
		class _KeyEvent(ctypes.Structure):
			_fields_ = [("bKeyDown", w.BOOL), ("wRepeatCount", w.WORD),
				("wVirtualKeyCode", w.WORD), ("wVirtualScanCode", w.WORD),
				("uChar", _KeyUChar), ("dwControlKeyState", w.DWORD)]
		class _KeyRecordUnione(ctypes.Union):
			_fields_ = [("KeyEvent", _KeyEvent), ("riempimento", ctypes.c_byte * 16)]
		class _KeyRecord(ctypes.Structure):
			_fields_ = [("EventType", w.WORD), ("Event", _KeyRecordUnione)]
		kernel = ctypes.windll.kernel32
		# CONIN$ invece del canale di ingresso standard, che potrebbe essere
		# dirottato altrove: e' la console vera, la stessa che leggeva getwch.
		manico = kernel.CreateFileW("CONIN$", 0x80000000 | 0x40000000, 1 | 2, None, 3, 0, None)
		if manico == w.HANDLE(-1).value:
			raise EOFError("key: nessuna console da cui leggere")
		_KEY_CONSOLE = (kernel, manico, _KeyRecord)
	return _KEY_CONSOLE

_KEY_CRONOMETRI = None

def _key_cronometro(kernel, manico):
	"""Il cronometro della scadenza, uno per thread.

	Aspettare sul solo manico della console arrotonderebbe ai tick del
	sistema, quindici millesimi e mezzo, e chi chiede due millesimi ne
	aspetterebbe sedici; questo invece sveglia al millesimo giusto, e senza
	alzare la frequenza del timer di tutto il sistema come farebbe
	timeBeginPeriod. Dove non c'e', cioe' prima di Windows 10 1803, si ripiega
	su quello comune, preciso quanto l'attesa della V7.0.0.
	Uno per thread e non uno solo, perche' armarlo lo riazzera: due thread che
	chiamassero key insieme si ruberebbero la scadenza a vicenda, e quello con
	l'attesa piu' lunga finirebbe prima senza che niente lo segnali.
	Restituisce il cronometro e l'array dei due oggetti da aspettare, con la
	console per prima: quando tutti e due sono pronti nello stesso istante
	vince quella, e un tasto gia' in coda viene letto anche se la scadenza e'
	scaduta insieme a lui."""
	global _KEY_CRONOMETRI
	import ctypes.wintypes as w
	import threading
	if _KEY_CRONOMETRI is None:
		_KEY_CRONOMETRI = threading.local()
	suo = getattr(_KEY_CRONOMETRI, "coppia", None)
	if suo is None:
		kernel.CreateWaitableTimerExW.restype = w.HANDLE
		cronometro = kernel.CreateWaitableTimerExW(None, None, 0x00000002, 0x1F0003)
		if not cronometro:
			kernel.CreateWaitableTimerW.restype = w.HANDLE
			cronometro = kernel.CreateWaitableTimerW(None, False, None)
		suo = (cronometro, (w.HANDLE * 2)(w.HANDLE(manico), w.HANDLE(cronometro)))
		_KEY_CRONOMETRI.coppia = suo
	return suo

def _key_record_windows(attesa):
	"""I record di tastiera della console, uno alla volta, fino alla scadenza.
	Produce quintuple (giu, codice, scansione, stato, carattere) e finisce
	quando l'attesa scade: il rilascio e i modificatori passano tutti, perche'
	chi legge decide che farsene. Cio' che non e' tastiera, cioe' il mouse, il
	ridimensionamento della finestra e il cambio di fuoco, resta fuori.
	attesa None aspetta senza limite, zero da' un solo sguardo, un numero
	aspetta quei secondi.
	L'attesa avviene dentro il kernel: finche' non succede niente il processo
	non gira affatto, dove la V7.0.0 guardava la tastiera cento volte al
	secondo. E' pero' spezzata in fette da un decimo di secondo, perche' Ctrl+C
	arriva al processo come evento e non come record, e Python lo trasforma in
	eccezione solo quando torna a eseguire il proprio codice: senza le fette un
	Ctrl+C premuto durante l'attesa resterebbe appeso fino al tasto seguente.
	Dieci risvegli al secondo costano un centesimo di quello che costavano i
	cento sguardi, e ne' il tasto ne' la scadenza aspettano la fine della
	fetta: tutti e due svegliano l'attesa da soli.
	Dalla V8.0.2 sta qui, staccata da key, perche' la usa anche Tastiera: sono
	due modi di consegnare gli stessi record, e leggerli e' un mestiere solo."""
	import ctypes
	kernel, manico, _KeyRecord = _key_strutture()
	cronometro, attesi = _key_cronometro(kernel, manico)
	record = _KeyRecord()
	letti = ctypes.c_ulong(0)
	sguardo = attesa is not None and attesa <= 0
	if attesa is None or sguardo:
		quanti = 1
	else:
		quanti = 2
		# Un valore negativo e' un tempo relativo, contato in decimilionesimi
		# di secondo.
		scadenza = ctypes.c_longlong(-int(attesa * 10000000.0))
		if not kernel.SetWaitableTimer(cronometro, ctypes.byref(scadenza), 0, None, None, False):
			raise EOFError("key: non si riesce ad armare la scadenza")
	while True:
		# La fetta da un decimo di secondo non serve alla scadenza, che ha il
		# suo cronometro, ma a lasciare che Python veda i segnali. Quando due
		# oggetti sono pronti insieme vince quello di indice minore, cioe' la
		# console: un tasto gia' in coda viene letto anche se la scadenza e'
		# scaduta nello stesso istante.
		esito = kernel.WaitForMultipleObjects(quanti, attesi, False, 0 if sguardo else 100)
		if esito == 0x102:
			# Con l'attesa a zero lo sguardo e' uno solo: se la console non
			# aveva niente da dare, si torna senza aspettare.
			if sguardo:
				return
			continue
		if esito == 1:
			return
		if esito != 0:
			raise EOFError("key: la console non e' piu' leggibile")
		if not kernel.ReadConsoleInputW(manico, ctypes.byref(record), 1, ctypes.byref(letti)):
			raise EOFError("key: la console non e' piu' leggibile")
		if letti.value == 0:
			continue
		if record.EventType != 1:
			continue
		evento = record.Event.KeyEvent
		# I campi si copiano subito: la struttura e' una sola e viene riscritta
		# al giro dopo, quindi chi tenesse il record si ritroverebbe in mano il
		# tasto seguente.
		yield (bool(evento.bKeyDown), evento.wVirtualKeyCode, evento.wVirtualScanCode,
			evento.dwControlKeyState, evento.uChar.UnicodeChar)

def _key_windows(attesa, alla_scadenza):
	"""Il primo tasto premuto che abbia un nome da consegnare.
	Il rilascio e i modificatori premuti da soli si scartano qui: la V7.0.0 non
	li vedeva affatto, perche' getwch li scartava per conto suo."""
	for giu, vk, _scansione, stato, carattere in _key_record_windows(attesa):
		if not giu:
			continue
		nome = _key_nome_windows(vk, stato, carattere)
		if nome is not None:
			return nome
	return alla_scadenza

def _key_console_windows():
	"""Solleva EOFError se il processo non ha una console: senza, kbhit non
	vede mai niente e key resterebbe in attesa per sempre, per esempio in
	un'applicazione con interfaccia grafica avviata senza terminale."""
	import ctypes
	try:
		senza_console = ctypes.windll.kernel32.GetConsoleCP() == 0
	except (AttributeError, OSError):
		return
	if senza_console:
		raise EOFError("key: nessuna console da cui leggere")

def key(prompt="", attesa=None, alla_scadenza=""):
	"""V8.0.2 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU), Stella/Gemini 3.5 Flash & ClaudIA (Claude Opus 5, modalità auto)
	Legge un tasto singolo senza aspettare Invio, riconosce i tasti speciali,
	il tastierino a blocco numerico spento e i modificatori, e riferisce ogni
	tasto con un nome leggibile, uguale su Windows e su Unix.
	Parametri:
	  prompt: testo stampato prima dell'attesa, senza andare a capo.
	  attesa: secondi da aspettare; None, il predefinito, aspetta senza limite.
	    Zero da' un solo sguardo alla tastiera e torna subito: e' il modo di
	    sorvegliarla senza fermarsi.
	  alla_scadenza: cio' che viene restituito se l'attesa scade senza tasti.
	    Il predefinito e' la stringa vuota. Attenzione: la stringa vuota e'
	    sottostringa di qualunque stringa, quindi un controllo come risposta in
	    "abc" e' vero anche alla scadenza. Chi usa quell'idioma passi None, che
	    non e' sottostringa di niente, e lo confronti per primo.
	Restituisce:
	  i caratteri stampabili come sono, spazio compreso;
	  Invio come \\r, Escape come \\x1b, Backspace come \\x08, Tab come \\t;
	  Ctrl piu' lettera come ctrl-a fino a ctrl-z, tranne le tre combinazioni
	    che sono gia' i tasti sopra;
	  frecce e navigazione dedicate come up, down, left, right, home, end,
	    pageup, pagedown, insert, delete, e con ctrl o alt davanti, per esempio
	    ctrl-left o alt-home;
	  le stesse sul tastierino a blocco numerico spento con pad davanti, per
	    esempio pad-up o ctrl-pad-home, e pad-center per il 5, che pero' con
	    uno screen reader acceso non arrivano: NVDA usa quel tastierino per il
	    suo navigatore a oggetti e se li tiene, quindi un programma pensato
	    per chi legge con lo screen reader non deve dare comandi ai nomi pad-,
	    e nemmeno usarli come scorciatoie alternative, perche' non si
	    premerebbero mai. Con Alt davanti invece passano;
	  i tasti funzione come f1 fino a f12, anche con shift, ctrl e alt davanti;
	  Alt piu' lettera o cifra come alt-a o alt-1, e su Windows anche ctrl-tab
	    e ctrl-backspace;
	  una combinazione con modificatori non riconosciuta come special-vk- piu'
	    il codice del tasto su Windows e come esc- piu' la sequenza su Unix,
	    cosi' che si scopra premendola. Un tasto premuto nudo che la console
	    non sa tradurre in nessun carattere, come quelli multimediali o quelli
	    morti che aspettano la vocale da accentare, non viene invece riferito
	    affatto e l'attesa prosegue, come faceva getwch.
	I modificatori valgono per ogni tasto e si accumulano nel nome nell'ordine
	shift, alt, ctrl: shift-left, shift-ctrl-home, alt-pad-home, shift-tab.
	Con le lettere lo shift non compare, perche' e' gia' nella maiuscola, e
	nemmeno con Ctrl piu' lettera, che resta ctrl-a anche premendo lo shift.
	Un tasto premuto e poi rilasciato da' un tasto solo: il rilascio non viene
	riferito, e nemmeno i modificatori premuti da soli.
	Ctrl+C interrompe il programma con KeyboardInterrupt, come in qualunque
	programma da console, e non viene mai restituito come tasto.
	Solleva EOFError quando il processo non ha una console o un terminale da
	cui leggere, per esempio un'applicazione con interfaccia grafica avviata
	senza terminale, invece di restare in attesa per sempre; solleva TypeError
	se attesa non e' None e non e' un numero.
	Dalla V8.0.0 su Windows i tasti si leggono dai record della console con
	ReadConsoleInputW, invece che da getwch, e l'attesa avviene dentro il
	sistema invece di guardare la tastiera cento volte al secondo: aspettare
	non consuma piu' processore e un tasto arriva in un decimo di millesimo di
	secondo invece di cinque millesimi e mezzo. Ne viene anche che Ctrl+PagSu
	non e' piu' confuso con F12, che Shift con le frecce, Home, Fine, le
	pagine, Ins e Canc si distingue dal tasto nudo, che Alt con il tastierino
	non viene piu' ingoiato, che Shift+Tab torna shift-tab come gia' faceva su
	Unix invece di confondersi con Tab, e che i tasti da F13 a F24 hanno un
	nome. Chi confrontava '\t' per riconoscere Shift+Tab su Windows deve ora
	confrontare anche shift-tab.
	Dalla V8.0.2 solleva RuntimeError se e' aperta una Tastiera, la tastiera a
	eventi che nasce con la V160: il buffer della console e' uno solo e chi
	legge per primo consuma, quindi chiamarle tutte e due vorrebbe dire perdere
	tasti a caso senza capire perche'. Chi ha aperto la Tastiera usa il suo
	metodo tasto(), che fa lo stesso mestiere di key.
	Dalla V7.0.0 i quattro tasti di servizio tornano come caratteri anche su
	Unix, dove prima tornavano come parole; l'attesa predefinita e' senza
	limite, dove prima era di 99999 secondi con una stringa vuota alla
	ventottesima ora; le tabelle dei tasti sono costanti di modulo invece di
	essere ricostruite a ogni chiamata; la tabella di Windows e' stata
	verificata contro la libreria di runtime, correggendo Alt con le frecce
	dedicate, che tornavano con i nomi del tastierino, e aggiungendo Ctrl e Alt
	con Ins e Canc, Ctrl+Tab, Ctrl+Backspace e Alt con lettere e cifre; e su
	Unix i modificatori valgono anche per Home, Fine, le pagine, Ins, Canc e i
	tasti funzione.
	"""
	import os
	import sys
	import time
	if _TASTIERA_APERTA is not None:
		raise RuntimeError("key: c'e' una Tastiera aperta ed e' lei che legge la console; usa il suo metodo tasto()")
	if attesa is not None:
		try:
			attesa = float(attesa)
		except (TypeError, ValueError) as errore:
			raise TypeError("key: attesa deve essere None o un numero di secondi") from errore
	if os.name == 'nt':
		_key_console_windows()
		if prompt:
			print(prompt, end="", flush=True)
		return _key_windows(attesa, alla_scadenza)
	import select
	import termios
	import tty
	try:
		fd = sys.stdin.fileno()
		vecchie_impostazioni = termios.tcgetattr(fd)
	except (AttributeError, ValueError, OSError, termios.error) as errore:
		raise EOFError("key: nessun terminale da cui leggere") from errore
	if prompt:
		print(prompt, end="", flush=True)
	inizio = time.monotonic()
	try:
		tty.setcbreak(fd)
		while True:
			timeout = None
			if attesa is not None:
				timeout = max(0.0, attesa - (time.monotonic() - inizio))
			pronti, _, _ = select.select([sys.stdin], [], [], timeout)
			if not pronti:
				if attesa is not None and time.monotonic() - inizio >= attesa:
					return alla_scadenza
				continue
			ch = sys.stdin.read(1)
			if ch == '\x1b':
				# Un Escape da solo o l'inizio di una sequenza: si aspetta un
				# attimo per vedere se arriva altro, poi si legge il resto.
				seq = ""
				pausa = 0.05
				while True:
					pronti, _, _ = select.select([sys.stdin], [], [], pausa)
					if not pronti:
						break
					seq += sys.stdin.read(1)
					pausa = 0.01
				if not seq:
					return '\x1b'
				return _key_sequenza_ansi(seq)
			if ch in ('\n', '\r'):
				return '\r'
			if ch in ('\x08', '\x7f'):
				return '\x08'
			return _key_carattere(ch)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, vecchie_impostazioni)

_TASTIERA_APERTA = None
# I modificatori premuti da soli. key non li riferisce, perche' una domanda con
# una risposta non saprebbe che farsene; la tastiera a eventi si', perche' li'
# sono tasti come gli altri, che scendono e risalgono. Destro e sinistro danno
# lo stesso nome: finche' uno dei due e' giu', il nome resta fra i premuti.
_TASTIERA_MODIFICATORI = {
	0x10: 'shift', 0xa0: 'shift', 0xa1: 'shift',
	0x11: 'ctrl', 0xa2: 'ctrl', 0xa3: 'ctrl',
	0x12: 'alt', 0xa4: 'alt', 0xa5: 'alt',
	0x5b: 'win', 0x5c: 'win', 0x5d: 'menu',
	0x14: 'capslock', 0x90: 'numlock', 0x91: 'scrolllock',
}

class Tastiera:
	"""V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	La tastiera a eventi: dice quando un tasto scende e quando risale, e quali
	sono giu' in questo momento.
	key e' una domanda con una risposta, "qual e' il prossimo tasto?", e una
	stringa non ha dove dire "e questo e' ancora giu'". Ne viene che con key non
	si possono fare tre cose: una nota che duri finche' il dito resta sul tasto,
	un personaggio che cammini finche' la freccia e' premuta, e un accordo, cioe'
	sapere che due tasti sono premuti insieme. L'informazione pero' c'e': dalla
	V8.0.0 key legge i record della console, che portano anche il rilascio, ed e'
	key che lo butta perche' il suo contratto non saprebbe dove metterlo.
	I nomi dei tasti sono quelli di key, perche' vengono dalla stessa
	traduzione: chi passa dall'una all'altra non deve reimparare niente.
	Uso, per il gioco che vuole lo stato:
	    tastiera = Tastiera()
	    while gioca:
	        tastiera.eventi()                       # svuota la coda, senza fermarsi
	        if "right" in tastiera.premuti: x += passo
	        if "left" in tastiera.premuti: x -= passo
	        disegna()
	Uso, per la musica che vuole il momento:
	    for nome, azione in tastiera.eventi():
	        nota = TASTI.get(nome)
	        if nota is None: continue
	        if azione == "giu": accendi(nota)
	        else: spegni(nota)
	L'auto-ripetizione di Windows, che dopo mezzo secondo di tenuta batte
	trentadue volte al secondo, sparisce da sola: il registro sa gia' che quel
	tasto e' giu', e la seconda pressione non produce niente.
	Tastiera e key non possono leggere insieme: il buffer della console e' uno
	solo e chi legge per primo consuma. Finche' una Tastiera e' aperta, key si
	ferma con un errore invece di rubarle i tasti, ed e' per questo che esiste
	il metodo tasto(), cosi' chi ha aperto la tastiera a eventi non debba
	tornare a key per un menu. Si chiude con chiudi(), o da sola uscendo da un
	blocco with.
	Limiti da sapere prima:
	  il rollover e' della tastiera fisica, non del programma: tre tasti insieme
	    passano, ma le tastiere a membrana di solito si fermano fra i due e i
	    tre, e un accordo di quattro note potrebbe non arrivare tutto;
	  niente dinamica, perche' la tastiera del PC non misura la forza: tutte le
	    note escono uguali, e chi vuole la sfumatura si fa due tasti che alzano
	    e abbassano il volume;
	  il tastierino resta di NVDA, come in key: i nomi pad- non arriveranno mai
	    con uno screen reader acceso;
	  i rilasci avvenuti mentre la finestra non aveva il fuoco non arrivano, e
	    quel tasto resterebbe giu' per sempre: chi perde il fuoco chiama
	    rilascia_tutto(), che restituisce i rilasci mancanti da spegnere.
	Solleva NotImplementedError fuori da Windows, dove un terminale consegna
	caratteri e non eventi e non sa dire quando un tasto viene lasciato;
	EOFError se il processo non ha una console; RuntimeError se una Tastiera e'
	gia' aperta o se si usa dopo averla chiusa.
	Nasce con la issue 37, misurata il 14 settembre 2026 con banco_tenuta.py: il
	rilascio arriva puntuale, tre tasti insieme si distinguono con i loro tre
	rilasci, e suonando veloce non si perde niente, nemmeno le sovrapposizioni.
	"""

	def __init__(self):
		import os
		global _TASTIERA_APERTA
		if os.name != 'nt':
			raise NotImplementedError(
				"Tastiera: i rilasci esistono solo su Windows, perche' un terminale "
				"consegna caratteri e non eventi e non sa dire quando un tasto viene lasciato")
		if _TASTIERA_APERTA is not None:
			raise RuntimeError("Tastiera: ce n'e' gia' una aperta, e il buffer della console e' uno solo")
		try:
			_key_console_windows()
		except EOFError as errore:
			raise EOFError("Tastiera: nessuna console da cui leggere") from errore
		# Il registro sta sul tasto fisico, codice piu' scansione, e non sul
		# nome: premendo z, poi ctrl, e lasciando poi z, il rilascio porta lo
		# stato dei modificatori di quel momento e si chiamerebbe ctrl-z, un
		# nome che nessuno aveva mai acceso. Cosi' invece il rilascio ritrova
		# sempre il nome che era stato dato alla pressione.
		self._fisici = {}
		# Quanti tasti fisici tengono giu' ogni nome: i due shift sono due
		# tasti e un nome solo, e il nome risale quando risale il secondo.
		self._conteggio = {}
		# Cio' che tasto() ha letto e non ha restituito: lo prende la prossima
		# eventi(), invece di perdersi.
		self._coda = []
		self._chiusa = False
		_TASTIERA_APERTA = self

	def __enter__(self):
		return self

	def __exit__(self, *_guai):
		self.chiudi()
		return False

	def chiudi(self):
		"""Restituisce la console a key. Dopo, questa tastiera non si usa piu'."""
		global _TASTIERA_APERTA
		self._chiusa = True
		self._fisici.clear()
		self._conteggio.clear()
		self._coda.clear()
		if _TASTIERA_APERTA is self:
			_TASTIERA_APERTA = None

	def _controlla(self):
		if self._chiusa:
			raise RuntimeError("Tastiera: e' stata chiusa, la console adesso e' di key")

	@property
	def premuti(self):
		"""I nomi dei tasti giu' in questo momento, come insieme immutabile.
		Dice quello che si sapeva all'ultima lettura: si aggiorna chiamando
		eventi(), che e' il momento in cui i record vengono letti davvero."""
		return frozenset(self._conteggio)

	def eventi(self, attesa=0):
		"""Le coppie (nome, 'giu') e (nome, 'su') arrivate, in ordine.
		Con attesa 0, il predefinito, torna subito con cio' che c'e', anche
		niente; con un numero aspetta fino a quel tempo il primo evento e poi
		prende anche tutto quello che gli e' arrivato dietro; con None aspetta
		senza limite. Quando torna, premuti e' aggiornato."""
		import time
		self._controlla()
		if attesa is not None:
			try:
				attesa = float(attesa)
			except (TypeError, ValueError) as errore:
				raise TypeError("Tastiera: attesa deve essere None o un numero di secondi") from errore
		raccolti = self._coda
		self._coda = []
		limite = None if attesa is None else time.monotonic() + max(0.0, attesa)
		while True:
			if raccolti:
				# Il primo evento c'e' gia': quello che resta si raccoglie
				# senza fermarsi, perche' chi aspettava ha gia' la sua risposta.
				resta = 0.0
			elif limite is None:
				resta = None
			else:
				resta = max(0.0, limite - time.monotonic())
			aspettando = resta != 0
			letto = False
			for giu, vk, scansione, stato, carattere in _key_record_windows(resta):
				letto = True
				evento = self._registra(giu, vk, scansione, stato, carattere)
				if evento is None:
					continue
				raccolti.append(evento)
				if aspettando:
					# Questo generatore ha una scadenza addosso: si ricomincia
					# con uno che non aspetta, per svuotare quel che resta.
					break
			if not letto:
				break
		return raccolti

	def tasto(self, prompt="", attesa=None, alla_scadenza=""):
		"""Il primo tasto premuto, come key, per i menu e le domande.
		I rilasci che incontra aspettando li registra, cosi' premuti resta
		vero, ma non li riferisce; gli eventi arrivati dietro al tasto li tiene
		da parte e li da' alla prossima eventi(), invece di perderli."""
		import time
		self._controlla()
		if prompt:
			print(prompt, end="", flush=True)
		limite = None if attesa is None else time.monotonic() + max(0.0, float(attesa))
		while True:
			resta = None if limite is None else max(0.0, limite - time.monotonic())
			arrivati = self.eventi(resta)
			for posto, (nome, azione) in enumerate(arrivati):
				if azione == "giu":
					self._coda = arrivati[posto + 1:] + self._coda
					return nome
			if limite is not None and time.monotonic() >= limite:
				return alla_scadenza

	def rilascia_tutto(self):
		"""Dichiara lasciati tutti i tasti che risultavano giu' e restituisce i
		loro rilasci, da spegnere uno per uno.
		Serve quando la finestra perde il fuoco: quello che succede altrove non
		arriva, e senza questo un tasto resterebbe giu' per sempre, cioe' una
		nota suonerebbe senza fine."""
		self._controlla()
		lasciati = [(nome, "su") for nome in sorted(self._conteggio)]
		self._fisici.clear()
		self._conteggio.clear()
		return lasciati

	def svuota(self):
		"""Butta via i record accumulati e dimentica i tasti premuti, senza
		riferire niente. Si chiama all'inizio, per non trovarsi addosso quello
		che l'utente aveva premuto prima."""
		self._controlla()
		for _record in _key_record_windows(0):
			pass
		self._fisici.clear()
		self._conteggio.clear()
		self._coda.clear()

	def _registra(self, giu, vk, scansione, stato, carattere):
		"""Aggiorna il registro con un record e dice che evento ne esce, se ne
		esce uno."""
		fisico = (vk, scansione)
		if giu:
			if fisico in self._fisici:
				# L'auto-ripetizione di Windows, che sono record separati e non
				# un record con il conteggio alto: il registro sa gia' che quel
				# tasto e' giu' e non se ne fa niente.
				return None
			nome = _TASTIERA_MODIFICATORI.get(vk)
			if nome is None:
				nome = _key_nome_windows(vk, stato, carattere)
			if nome is None:
				return None
			self._fisici[fisico] = nome
			quanti = self._conteggio.get(nome, 0)
			self._conteggio[nome] = quanti + 1
			return (nome, "giu") if quanti == 0 else None
		nome = self._fisici.pop(fisico, None)
		if nome is None:
			# Il rilascio di un tasto che era gia' giu' prima che la tastiera
			# aprisse, o di uno che non aveva un nome da consegnare.
			return None
		quanti = self._conteggio.get(nome, 0) - 1
		if quanti > 0:
			self._conteggio[nome] = quanti
			return None
		self._conteggio.pop(nome, None)
		return (nome, "su")


# Tetto alla durata di sonify: il segnale si costruisce tutto in memoria, e a
# 44100 campioni al secondo cinque minuti sono gia' oltre un centinaio di
# megabyte fra i vettori intermedi. Senza il tetto, una durata sbagliata di
# un ordine di grandezza bloccava la macchina invece di dare un errore.
_SONIFY_DURATA_MASSIMA = 300.0
_SONIFY_DURATA_MINIMA = 0.01
_SONIFY_FREQUENZA_CAMPIONAMENTO = 44100

def _sonify_panoramica(pan):
	"""Traduce il parametro pan di sonify nella coppia di posizioni, iniziale
	e finale, fra -1 a sinistra e 1 a destra. True e' lo scorrimento intero da
	sinistra a destra, False o None il centro fermo, un numero una posizione
	fissa, una coppia di numeri uno scorrimento dal primo al secondo."""
	if pan is True:
		return -1.0, 1.0
	if pan is False or pan is None:
		return 0.0, 0.0
	try:
		if isinstance(pan, (int, float)):
			inizio = fine = float(pan)
		else:
			inizio, fine = (float(v) for v in pan)
	except (TypeError, ValueError) as errore:
		raise ValueError("sonify: pan deve essere True, False, un numero fra -1 e 1 o una coppia di numeri") from errore
	return max(-1.0, min(1.0, inizio)), max(-1.0, min(1.0, fine))

def sonify(data_list, duration, ptm=False, vol=0.5, file=False, pan=True, freq_min=87.31, freq_max=5587.65):
	"""V8.0.0 di martedi' 8 settembre 2026 - Gabriele Battaglia (IZ4APU), Stella, Gemini 3 Pro & ClaudIA (Claude Fable 5.1, modalita' auto)
	Sonifica una serie di numeri: ogni valore diventa una frequenza, dal piu'
	basso al piu' alto, e la serie viene suonata in stereo per la durata
	chiesta, con un suono che scorre da sinistra a destra per far
	corrispondere il tempo allo spazio. La riproduzione parte e la funzione
	torna subito, senza aspettare la fine; una chiamata nuova interrompe la
	precedente.
	Parametri:
	  data_list: sequenza semplice di numeri, da 5 a 500000 valori, tutti
	    finiti.
	  duration: durata totale in secondi, da 0.01 a 300.
	  ptm: con True le frequenze scivolano l'una nell'altra, come un
	    portamento; con False ogni valore tiene la propria nota.
	  vol: volume da 0.1 a 1.0; i valori fuori vengono riportati al limite.
	  file: False non scrive niente; True scrive sonification seguito da data
	    e ora, con estensione wav, nella cartella del programma che chiama; un
	    percorso scrive li', e se e' relativo lo risolve sulla stessa cartella.
	  pan: True, il predefinito, fa scorrere il suono da sinistra a destra;
	    False lo tiene al centro; un numero fra -1 e 1 lo tiene fermo li'; una
	    coppia di numeri lo fa scorrere dal primo al secondo.
	  freq_min e freq_max: estremi in hertz della scala su cui si
	    distribuiscono i valori; i predefiniti sono il fa della seconda ottava
	    e quello dell'ottava.
	Una serie di valori tutti uguali produce una nota sola, a meta' della
	scala.
	Restituisce il percorso completo del file scritto, o None se non ne ha
	scritto nessuno.
	Solleva TypeError se i dati, la durata, il volume o le frequenze non sono
	numeri o se file non e' un percorso; ValueError se i dati sono troppi,
	troppo pochi, non finiti, None compreso, o non in una sola dimensione, se
	la durata o le frequenze sono fuori dai limiti o se pan non ha una delle
	forme ammesse; OSError se il file non si puo'
	scrivere; e gli errori di sounddevice se la scheda audio non si apre. Fino
	alla 7.3 i dati sbagliati facevano uscire in silenzio, la lunghezza
	sbagliata veniva stampata in inglese e il file nasceva nella directory di
	lavoro: dalla V8.0.0 ogni errore torna a chi chiama, e il file nasce
	accanto a chi l'ha chiesto. Il tetto alla durata prima non c'era.
	"""
	import os
	import time
	import wave

	import numpy as np
	import sounddevice as sd
	try:
		data = np.asarray(data_list, dtype=np.float32)
	except (TypeError, ValueError) as errore:
		raise TypeError("sonify: data_list deve contenere soltanto numeri") from errore
	if data.ndim != 1:
		raise ValueError("sonify: data_list deve essere una sequenza semplice di numeri, non annidata")
	n = data.size
	if n < 5 or n > 500000:
		raise ValueError(f"sonify: servono da 5 a 500000 valori, ricevuti {n}")
	if not np.isfinite(data).all():
		raise ValueError("sonify: data_list contiene valori non finiti")
	try:
		durata = float(duration)
		vol = float(vol)
		freq_min = float(freq_min)
		freq_max = float(freq_max)
	except (TypeError, ValueError) as errore:
		raise TypeError("sonify: duration, vol, freq_min e freq_max devono essere numeri") from errore
	if not _SONIFY_DURATA_MINIMA <= durata <= _SONIFY_DURATA_MASSIMA:
		raise ValueError(f"sonify: la durata deve stare fra {_SONIFY_DURATA_MINIMA} e {_SONIFY_DURATA_MASSIMA:.0f} secondi, ricevuta {durata}")
	fs = _SONIFY_FREQUENZA_CAMPIONAMENTO
	if not 0 < freq_min < freq_max <= fs / 2:
		raise ValueError(f"sonify: serve 0 < freq_min < freq_max <= {fs // 2}, ricevute {freq_min} e {freq_max}")
	vol = max(0.1, min(vol, 1.0))
	pan_inizio, pan_fine = _sonify_panoramica(pan)
	campioni = int(durata * fs)
	data_min = data.min()
	data_max = data.max()
	if data_max == data_min:
		frequenze = np.full(n, (freq_min + freq_max) / 2, dtype=np.float32)
	else:
		frequenze = (freq_min + (data - data_min) * ((freq_max - freq_min) / (data_max - data_min))).astype(np.float32)
	if ptm:
		t = np.linspace(0, durata, campioni, endpoint=False, dtype=np.float32)
		tempi = np.linspace(0, durata, n, endpoint=True, dtype=np.float32)
		freq_array = np.interp(t, tempi, frequenze).astype(np.float32)
		del t, tempi
	else:
		indici = np.floor(np.linspace(0, n, campioni, endpoint=False)).astype(np.int32)
		freq_array = frequenze[indici]
		del indici
	# La fase si accumula in float64: in float32, su una sonificazione lunga,
	# perderebbe il conto e la frequenza scivolerebbe.
	fase = 2.0 * np.pi * np.cumsum(freq_array.astype(np.float64) / fs)
	del freq_array
	segnale = (np.sin(fase) * vol).astype(np.float32)
	del fase
	# Dissolvenza di un centesimo di secondo ai due estremi, contro lo
	# schiocco, e non oltre meta' del segnale quando questo e' cortissimo.
	dissolvenza = min(round(0.01 * fs), campioni // 2)
	if dissolvenza > 0:
		curva = np.sin(np.linspace(0, np.pi / 2, dissolvenza, dtype=np.float32))
		segnale[:dissolvenza] *= curva
		segnale[-dissolvenza:] *= curva[::-1]
	# Panoramica a potenza costante, con coseno e seno: il volume percepito
	# non cala mentre il suono attraversa il centro.
	angolo = (np.linspace(pan_inizio, pan_fine, campioni, dtype=np.float32) + 1.0) * (np.pi / 4.0)
	stereo = np.column_stack((segnale * np.cos(angolo), segnale * np.sin(angolo)))
	del segnale, angolo
	stereo_int16 = (stereo * 32767).astype(np.int16)
	del stereo
	percorso = None
	if file is not False and file is not None:
		if file is True:
			percorso = os.path.join(_cartella_chiamante(), "sonification" + time.strftime("%Y%m%d%H%M%S") + ".wav")
		else:
			try:
				percorso = os.fspath(file)
			except TypeError as errore:
				raise TypeError("sonify: file deve essere True, False o un percorso") from errore
			if not os.path.isabs(percorso):
				percorso = os.path.join(_cartella_chiamante(), percorso)
		with wave.open(percorso, 'wb') as wf:
			wf.setnchannels(2)
			wf.setsampwidth(2)
			wf.setframerate(fs)
			wf.writeframes(stereo_int16.tobytes())
	sd.play(stereo_int16, fs)
	return percorso

def parse_pan_parts(val):
	"""
	Parsa una stringa, tupla, lista o numero che rappresenta uno o due valori di panning.
	Restituisce una lista di 2 stringhe [p1_str, p2_str].
	"""
	if isinstance(val, (tuple, list)) and len(val) == 2:
		def fmt(x):
			fx = float(x)
			return str(int(fx)) if fx.is_integer() else str(round(fx, 2))
		return [fmt(val[0]), fmt(val[1])]
	
	val_str = str(val).strip()
	dot_indices = [i for i, ch in enumerate(val_str) if ch == '.']
	
	for idx in dot_indices:
		left = val_str[:idx]
		right = val_str[idx+1:]
		try:
			f_left = float(left)
			f_right = float(right)
			if -1.0 <= f_left <= 1.0 and -1.0 <= f_right <= 1.0:
				def fmt(fval, orig_str):
					return orig_str if orig_str in (str(int(fval)), str(round(fval, 2))) else (str(int(fval)) if fval.is_integer() else str(round(fval, 2)))
				return [fmt(f_left, left), fmt(f_right, right)]
		except ValueError:
			continue
			
	parts = val_str.split('.')
	if len(parts) >= 2:
		return [parts[0], parts[1]]
	return [val_str, val_str]

def parse_pan_values(pan_param):
	"""
	Parsa il parametro pan (float, int, str, tuple, list).
	Restituisce un float (se panning fisso) oppure una tupla (p_start, p_end) se portamento panning.
	Tutti i valori sono limitati nell'intervallo [-1.0, 1.0].
	"""
	if isinstance(pan_param, (int, float)):
		return max(-1.0, min(1.0, float(pan_param)))
	if isinstance(pan_param, (tuple, list)) and len(pan_param) == 2:
		p1 = max(-1.0, min(1.0, float(pan_param[0])))
		p2 = max(-1.0, min(1.0, float(pan_param[1])))
		return (p1, p2)
	if isinstance(pan_param, str):
		pan_str = pan_param.strip()
		is_single_float = False
		try:
			fval = float(pan_str)
			if -1.0 <= fval <= 1.0 and pan_str.count('.') <= 1:
				is_single_float = True
		except ValueError:
			pass
			
		if is_single_float:
			return float(pan_str)
			
		parts = parse_pan_parts(pan_str)
		try:
			p1 = max(-1.0, min(1.0, float(parts[0])))
			p2 = max(-1.0, min(1.0, float(parts[1])))
			return (p1, p2)
		except ValueError:
			pass
	return 0.0

def panorama_spostato(score, pan):
	"""Sposta il panorama di uno score piatto senza sostituirlo.

	pan e' uno spostamento, con la stessa grammatica del panorama delle
	quartine: un numero, cioe' fermo per tutto il suono, oppure una coppia,
	cioe' che scorre da un valore all'altro lungo l'intero suono, non dentro
	ogni nota.
	Il panorama che lo score ha di suo non viene cancellato ma spostato, e si
	stringe soltanto quel tanto che serve a non uscire dai bordi. E' la
	differenza che conta: sommare e tagliare, come si era proposto nella issue
	18, appiattirebbe contro il bordo cinquantuno preset su centocinque con
	uno spostamento di 0,6, e fra questi volo_radente, passaggio_veloce e le
	spazzate aliene, cioe' proprio quelli la cui identita' e' il movimento.
	Con pan a zero non cambia un campione, e non e' un caso trattato a parte:
	viene dalla formula, perche' il fattore di restringimento vale uno quando
	non c'e' niente da restringere.
	Restituisce uno score nuovo, senza toccare quello ricevuto.
	"""
	spostamento = parse_pan_values(pan)
	c1, c2 = (spostamento, spostamento) if isinstance(spostamento, float) else spostamento
	interni, durate = [], []
	for i in range(0, len(score) - 3, 4):
		valore = parse_pan_values(score[i + 2])
		interni.append((valore, valore) if isinstance(valore, float) else valore)
		try:
			durate.append(max(0.0, float(score[i + 1])))
		except (TypeError, ValueError):
			durate.append(0.0)
	if not interni:
		return list(score)
	# Quanto si puo' spostare senza sbattere: il fattore e' il piu' stretto
	# fra quello che tiene dentro il bordo destro e quello del sinistro, e
	# non supera mai uno, perche' il movimento si stringe, non si allarga.
	estremi = [x for coppia in interni for x in coppia]
	minimo, massimo = min(estremi), max(estremi)
	centro_min, centro_max = min(c1, c2), max(c1, c2)
	fattore = 1.0
	if massimo > 0:
		fattore = min(fattore, (1.0 - centro_max) / massimo)
	if minimo < 0:
		fattore = min(fattore, (-1.0 - centro_min) / minimo)
	fattore = max(0.0, fattore)
	totale = sum(durate)
	nuovo = list(score)
	trascorso = 0.0
	for indice, (v1, v2) in enumerate(interni):
		if totale > 0:
			centro1 = c1 + (c2 - c1) * (trascorso / totale)
			centro2 = c1 + (c2 - c1) * ((trascorso + durate[indice]) / totale)
		else:
			centro1 = centro2 = c1
		trascorso += durate[indice]
		p1 = centro1 + v1 * fattore
		p2 = centro2 + v2 * fattore
		# Un numero quando il panorama sta fermo, una coppia quando scorre:
		# e' la stessa forma che il motore si aspetta dalle quartine.
		nuovo[indice * 4 + 2] = p1 if abs(p1 - p2) < 1e-12 else (p1, p2)
	return nuovo

def parse_vol_values(vol_param):
	"""
	Parsa il parametro vol (float, int, str, tuple, list).
	Restituisce un float (se volume fisso) oppure una tupla (v_start, v_end) se portamento volume.
	Tutti i valori sono limitati nell'intervallo [0.0, 1.0].
	"""
	if isinstance(vol_param, (int, float)):
		return max(0.0, min(1.0, float(vol_param)))
	if isinstance(vol_param, (tuple, list)) and len(vol_param) == 2:
		v1 = max(0.0, min(1.0, float(vol_param[0])))
		v2 = max(0.0, min(1.0, float(vol_param[1])))
		return (v1, v2)
	if isinstance(vol_param, str):
		vol_str = vol_param.strip()
		is_single_float = False
		try:
			fval = float(vol_str)
			if 0.0 <= fval <= 1.0 and vol_str.count('.') <= 1:
				is_single_float = True
		except ValueError:
			pass
			
		if is_single_float:
			return float(vol_str)
			
		parts = parse_pan_parts(vol_str)
		try:
			v1 = max(0.0, min(1.0, float(parts[0])))
			v2 = max(0.0, min(1.0, float(parts[1])))
			return (v1, v2)
		except ValueError:
			pass
	return 0.5


# Il rumore come forma d'onda: il colore e' la pendenza dello spettro.
# L'esponente si applica allo spettro di ampiezza, cioe' meta' di quello
# della densita' di potenza: bianco piatto, rosa meno 3 dB per ottava,
# marrone meno 6, azzurro piu' 3.
_RUMORE_ESPONENTE = {5: 0.0, 6: -0.5, 7: -1.0, 8: 0.5}
_RUMORE_NOMI = {5: "bianco", 6: "rosa", 7: "marrone", 8: "azzurro"}
_SENZA_BANDA = (None, None, None, None)
# Sotto questa frequenza non si scende mai. Il rumore marrone teneva il 98,8
# per cento della sua energia sotto i 40 Hz, dove un altoparlante normale non
# riproduce nulla: quell'energia non si sentiva ma pesava sulla
# normalizzazione, e la sua componente quasi continua faceva partire il
# segnale da un valore alto, cioe' uno schiocco all'attacco.
# Portato da 30 a 50 e poi a 40 Hz negli ascolti del 2026-09-03: sotto,
# il marrone spendeva meta' della sua energia dove gli altoparlanti comuni
# non arrivano, ma a 40 Hz Gabriele lo preferisce, un filo piu' cupo.
_MINIMO_UDIBILE = 40.0
# Il tetto e' il difetto speculare della soglia. L'azzurro teneva il 59,9 per
# cento della sua energia sopra i 14 kHz, dove l'orecchio adulto sente poco e
# molti altoparlanti niente: la ponderazione A lassu' attenua appena 7 dB e
# quindi lo dichiarava pari agli altri, mentre all'ascolto arrivava piu' piano.
_MASSIMO_UDIBILE = 12000.0
# Il livello ponderato A a cui si porta ogni rumore. Si pareggia questo e non
# il valore efficace, perche' l'orecchio pesa le frequenze: a parita' di
# energia il marrone si sentiva 8,9 dB piu' piano del bianco e l'azzurro 2.
_LIVELLO_RUMORE = 0.15
# Il limitatore morbido comincia ad agire qui e non lascia passare oltre il
# tetto. Serve perche' pareggiare il livello percepito chiede di alzare il
# marrone di quasi 9 dB, che tagliarebbe di netto.
_LIMITE_GINOCCHIO = 0.6
_LIMITE_TETTO = 0.95
# Segnaposto al posto della frequenza quando la quartina e' di rumore: basta
# che non sia None, che vuol dire pausa, e che non sia una coppia, che vuol
# dire portamento.
_E_RUMORE = "rumore"


def parse_banda(val):
	"""Legge la banda del rumore dal campo che per le note contiene la nota.

	Forme accettate:
	  "p"                  pausa, non suona niente
	  "n"                  nessuna banda, il colore puro senza filtro
	  "200-3000"           banda ferma fra 200 e 3000 Hz
	  "100-1000.800-1800"  parte come banda 100-1000 e diventa 800-1800
	Il trattino separa il taglio basso da quello alto; il punto separa la
	banda di partenza da quella d'arrivo. I quattro valori si muovono
	ciascuno per conto suo, quindi la banda puo' allargarsi, stringersi,
	salire o scendere come si vuole.
	Nel campo della banda il punto significa sempre scivolata e mai
	decimale: su una frequenza di taglio i decimali non servono.
	Si accettano anche le forme a lista, comode da scrivere in un
	programma: [200, 3000] per una banda ferma, [[100, 1000], [800, 1800]]
	per una che scorre.
	Restituisce None per la pausa, altrimenti la quadrupla
	(basso_inizio, basso_fine, alto_inizio, alto_fine), dove None significa
	nessun limite da quel lato.
	Solleva ValueError se la banda e' scritta male.
	"""
	def coppia(pezzo, quando):
		"""I due tagli di una banda, cioe' quello basso e quello alto."""
		if isinstance(pezzo, (list, tuple)):
			if len(pezzo) != 2:
				raise ValueError(f"Banda {quando} non valida: {pezzo!r}")
			return float(pezzo[0]), float(pezzo[1])
		testo = str(pezzo).strip().lower()
		if '-' not in testo:
			raise ValueError(
				f"Banda {quando} non valida: '{pezzo}'. Serve taglio basso, "
				"trattino, taglio alto, per esempio 200-3000")
		sinistra, _, destra = testo.partition('-')
		return float(sinistra), float(destra)

	if isinstance(val, (list, tuple)):
		if len(val) != 2:
			raise ValueError(f"Banda non valida: {val!r}")
		if all(isinstance(x, (list, tuple)) for x in val):
			b0, a0 = coppia(val[0], "di partenza")
			b1, a1 = coppia(val[1], "d'arrivo")
		else:
			b0, a0 = coppia(val, "ferma")
			b1, a1 = b0, a0
	else:
		testo = str(val).strip().lower()
		if testo == 'p':
			return None
		if testo in ("", "n"):
			return _SENZA_BANDA
		pezzi = testo.split('.')
		if len(pezzi) == 1:
			b0, a0 = coppia(pezzi[0], "ferma")
			b1, a1 = b0, a0
		elif len(pezzi) == 2:
			b0, a0 = coppia(pezzi[0], "di partenza")
			b1, a1 = coppia(pezzi[1], "d'arrivo")
		else:
			raise ValueError(
				f"Banda non valida: '{val}'. Il punto separa la banda di "
				"partenza da quella d'arrivo e puo' comparire una volta sola")

	for v in (b0, b1, a0, a1):
		if v <= 0:
			raise ValueError(f"Frequenza di taglio non positiva in '{val}'")
	return (b0, b1, a0, a1)


def _maschera_banda(frequenze, basso, alto, morbidezza=1.35):
	"""Il guadagno da applicare a ogni frequenza, con i bordi sfumati.

	Un taglio netto suonerebbe di campana, quindi i bordi sfumano con un
	coseno rialzato che copre poco piu' di un terzo di ottava attorno a
	ciascun taglio. Su una banda stretta, pero', due sfumature cosi' larghe
	sarebbero piu' larghe della banda e il filtro non chiuderebbe: quando i
	due tagli sono vicini la sfumatura si stringe insieme a loro.
	"""
	import numpy as np
	maschera = np.ones_like(frequenze)
	if basso is not None and alto is not None and alto > basso:
		morbidezza = max(1.02, min(morbidezza, (alto / basso) ** 0.25))
	if basso is not None:
		piede = basso / morbidezza
		maschera[frequenze < piede] = 0.0
		rampa = (frequenze >= piede) & (frequenze < basso)
		if rampa.any():
			x = (frequenze[rampa] - piede) / (basso - piede)
			maschera[rampa] = 0.5 - 0.5 * np.cos(np.pi * x)
	if alto is not None:
		tetto = alto * morbidezza
		maschera[frequenze > tetto] = 0.0
		rampa = (frequenze > alto) & (frequenze <= tetto)
		if rampa.any():
			x = (frequenze[rampa] - alto) / (tetto - alto)
			maschera[rampa] = 0.5 + 0.5 * np.cos(np.pi * x)
	return maschera


def _filtra_banda_fissa(onda, basso, alto, fs):
	"""Passabanda con i tagli fermi: una sola trasformata su tutto il segmento."""
	import numpy as np
	frequenze = np.fft.rfftfreq(len(onda), 1.0 / fs)
	return np.fft.irfft(np.fft.rfft(onda) * _maschera_banda(frequenze, basso, alto), len(onda))


def _filtra_banda_mobile(onda, b0, b1, a0, a1, fs):
	"""Passabanda con i tagli che scorrono, ciascuno per conto suo.

	Il segnale viene lavorato a blocchi che si sovrappongono a meta', ognuno
	con la banda che compete al suo istante, e poi ricucito. Le finestre di
	Hann sommate a passo dimezzato danno uno, quindi ricucire non altera il
	livello.
	Il segnale viene imbottito di silenzio davanti e dietro, e l'imbottitura
	poi si butta: senza, i campioni ai due capi sarebbero coperti da una sola
	finestra, il cui peso agli estremi tende a zero, e dividere per quel peso
	faceva uscire un campione enorme, cioe' uno schiocco.
	"""
	import numpy as np
	n = len(onda)
	blocco = 1024
	while blocco > 64 and blocco > n:
		blocco //= 2
	passo = max(1, blocco // 2)
	finestra = np.hanning(blocco)
	frequenze = np.fft.rfftfreq(blocco, 1.0 / fs)
	imbottita = np.concatenate([np.zeros(passo), onda, np.zeros(blocco + passo)])
	uscita = np.zeros(len(imbottita))
	pesi = np.zeros(len(imbottita))
	for inizio in range(0, n + passo, passo):
		# Il blocco che parte qui e' centrato sul campione utile di indice
		# inizio, perche' il passo e' meta' blocco quanto l'imbottitura.
		quando = min(1.0, inizio / max(n - 1, 1))
		basso = None if b0 is None else b0 + (b1 - b0) * quando
		alto = None if a0 is None else a0 + (a1 - a0) * quando
		pezzo = imbottita[inizio:inizio + blocco] * finestra
		maschera = _maschera_banda(frequenze, basso, alto)
		uscita[inizio:inizio + blocco] += np.fft.irfft(np.fft.rfft(pezzo) * maschera, blocco)
		pesi[inizio:inizio + blocco] += finestra
	utile = slice(passo, passo + n)
	peso = pesi[utile].copy()
	peso[peso < 1e-3] = 1.0
	return uscita[utile] / peso


def _ponderazione_a(frequenze):
	"""Il guadagno della curva A, che approssima la sensibilita' dell'orecchio.

	E' la ponderazione della norma IEC 61672: attenua fortemente i bassi,
	dove sentiamo poco, e leggermente gli acuti estremi.
	"""
	import numpy as np
	f2 = np.asarray(frequenze, dtype=np.float64) ** 2
	numeratore = (12194.0 ** 2) * (f2 ** 2)
	denominatore = ((f2 + 20.6 ** 2)
					* np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2))
					* (f2 + 12194.0 ** 2))
	with np.errstate(divide='ignore', invalid='ignore'):
		guadagno = np.where(denominatore > 0, numeratore / denominatore, 0.0)
	return guadagno * (10 ** 0.1)


def _livello_ponderato(onda, fs):
	"""Quanto forte si sente un suono, pesando le frequenze come l'orecchio."""
	import numpy as np
	spettro = np.fft.rfft(onda)
	frequenze = np.fft.rfftfreq(len(onda), 1.0 / fs)
	pesato = spettro * _ponderazione_a(frequenze)
	return float(np.sqrt(np.sum(np.abs(pesato) ** 2)) / len(onda) * np.sqrt(2))


def _limita_morbido(onda):
	"""Arrotonda i picchi invece di tagliarli di netto.

	Sotto il ginocchio non tocca niente; sopra comprime con una tangente
	iperbolica, che non introduce lo spigolo del taglio netto. Sul rumore e'
	inudibile: misurato, la pendenza dello spettro resta quella di prima
	anche quando il limitatore lavora su un quinto dei campioni.
	"""
	import numpy as np
	fuori = np.abs(onda) > _LIMITE_GINOCCHIO
	if not fuori.any():
		return onda
	larghezza = _LIMITE_TETTO - _LIMITE_GINOCCHIO
	eccesso = (np.abs(onda[fuori]) - _LIMITE_GINOCCHIO) / larghezza
	onda = onda.copy()
	onda[fuori] = np.sign(onda[fuori]) * (_LIMITE_GINOCCHIO + larghezza * np.tanh(eccesso))
	return onda


def _genera_rumore(kind, banda, campioni, fs):
	"""Il rumore del colore chiesto, filtrato dalla banda, normalizzato a uno.

	La normalizzazione finale serve perche' colori e bande hanno ampiezze
	molto diverse fra loro: senza, lo stesso volume darebbe suoni di forza
	molto diversa a seconda del filtro.
	"""
	import numpy as np
	generatore = np.random.default_rng()
	bianco = generatore.standard_normal(campioni)
	esponente = _RUMORE_ESPONENTE[kind]
	if esponente == 0.0:
		onda = bianco
	else:
		spettro = np.fft.rfft(bianco)
		f = np.fft.rfftfreq(campioni)
		scala = np.zeros_like(f)
		scala[1:] = f[1:] ** esponente
		onda = np.fft.irfft(spettro * scala, campioni)
	b0, b1, a0, a1 = banda
	nyquist = fs / 2.0
	# Il taglio basso non scende mai sotto la soglia dell'udibile, anche
	# quando nessuna banda e' stata chiesta: sotto di essa c'e' solo energia
	# che non si sente ma che falserebbe la normalizzazione e farebbe partire
	# il segnale da un valore alto, con uno schiocco.
	b0 = _MINIMO_UDIBILE if b0 is None else max(b0, _MINIMO_UDIBILE)
	b1 = _MINIMO_UDIBILE if b1 is None else max(b1, _MINIMO_UDIBILE)
	b0, b1 = min(b0, nyquist), min(b1, nyquist)
	tetto = min(_MASSIMO_UDIBILE, nyquist)
	a0 = tetto if a0 is None else min(a0, tetto)
	a1 = tetto if a1 is None else min(a1, tetto)
	if b0 == b1 and a0 == a1:
		onda = _filtra_banda_fissa(onda, b0, a0, fs)
	else:
		onda = _filtra_banda_mobile(onda, b0, b1, a0, a1, fs)
	# Si pareggia il livello ponderato, cioe' quanto forte si sente, e non il
	# valore efficace, che pesa allo stesso modo frequenze che l'orecchio
	# sente in modo molto diverso. Poi il limitatore morbido tiene i picchi
	# senza tagliarli di netto: al marrone serve quasi il doppio e mezzo, che
	# altrimenti sfonderebbe.
	livello = _livello_ponderato(onda, fs)
	if livello > 0:
		onda = onda * (_LIVELLO_RUMORE / livello)
	onda = _limita_morbido(onda)
	# Un breve smorzamento ai due capi. Il rumore comincia e finisce su un
	# valore casuale qualsiasi: senza, sarebbe uno scalino dal silenzio, cioe'
	# un clic. Non basta l'inviluppo ADSR, perche' il suo attacco predefinito
	# vale lo 0,002 per cento della durata, che su un suono di un secondo e
	# mezzo fa un solo campione.
	sfumatura = min(int(fs * 0.004), campioni // 4)
	if sfumatura > 1:
		rampa = np.linspace(0.0, 1.0, sfumatura)
		onda[:sfumatura] = onda[:sfumatura] * rampa
		onda[-sfumatura:] = onda[-sfumatura:] * rampa[::-1]
	return onda.astype(np.float32)


# Le tabelle per leggere il nome di una nota. Stanno qui e non dentro la
# funzione perche' scomponi_nota viene chiamata una volta per ogni nota di uno
# score, e ricostruirle ogni volta sarebbe lavoro sprecato.
_NOTA_SEMITONI = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
# Simboli microtonali in coda al nome, dal piu' lungo al piu' corto per non
# confondere la doppia tilde con quella singola. Valgono in semitoni.
_NOTA_MICROTONI = (("~~", 1.5), ("``", -1.5), ("~", 0.5), ("`", -0.5))

def scomponi_nota(nome):
	"""V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	Legge il nome di una nota e lo riduce a un numero.
	Restituisce la coppia (numero MIDI intero, scostamento in semitoni), oppure
	None quando il testo non e' una nota, compresa la pausa scritta p.
	Il nome si scrive con la lettera inglese, da a a g, l'alterazione e il
	numero di ottava: c4, f#3, eb2. Maiuscole e minuscole sono la stessa cosa,
	e il trattino vale come la b del bemolle, perche' music21 scrive cosi'.
	In coda alla lettera possono esserci i simboli microtonali: la tilde alza
	di un quarto di tono e l'accento grave lo abbassa, doppi per tre quarti.
	Sono loro la ragione per cui la risposta e' una coppia invece di un numero
	solo: un quarto di tono non e' un numero MIDI intero, e chi deve mandare la
	nota a un sintetizzatore MIDI usa la parte intera e ignora il resto, mentre
	chi la sintetizza da se' li somma e ne ricava la frequenza esatta.
	E' l'unico punto del parco software in cui si interpreta il nome di una
	nota. Fino alla V160 stava in Chitabry, e Acusticator ne aveva una seconda
	copia, piu' povera, che di microtoni non sapeva niente.
	"""
	import re
	if not isinstance(nome, str):
		return None
	testo = nome.strip().lower().replace('-', 'b')
	if testo == 'p':
		return None
	ottava = re.search(r"\d+$", testo)
	if not ottava:
		return None
	base = testo[:ottava.start()]
	micro = 0.0
	for simbolo, scostamento in _NOTA_MICROTONI:
		if base.endswith(simbolo):
			micro = scostamento
			base = base[:-len(simbolo)]
			break
	lettera = re.match(r"^([a-g])([#b]?)$", base)
	if not lettera:
		return None
	nota, alterazione = lettera.groups()
	semitono = _NOTA_SEMITONI[nota] + {'#': 1, 'b': -1}.get(alterazione, 0)
	return 12 + semitono + 12 * int(ottava.group()), micro

def frequenza_nota(nota):
	"""V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	La frequenza in hertz di una nota scritta per nome, con il la a 440.
	Accetta i nomi che legge scomponi_nota, microtoni compresi; un numero lo
	prende per una frequenza gia' pronta e lo restituisce com'e'.
	Risponde 0.0 quando non c'e' niente da suonare, cioe' per la pausa e per un
	nome che non si riesce a leggere: chi vuole distinguere i due casi, o
	rifiutare il nome sbagliato invece di tacere, chiami prima scomponi_nota.
	Un valore logico non e' una frequenza e vale 0.0, perche' in Python True
	sarebbe un hertz.
	"""
	if isinstance(nota, bool):
		return 0.0
	if isinstance(nota, (int, float)):
		return float(nota)
	scomposta = scomponi_nota(nota)
	if scomposta is None:
		return 0.0
	midi, micro = scomposta
	return 440.0 * (2.0 ** ((midi + micro - 69) / 12.0))

def _sintetizza(score, kind=1, adsr=None, fs=44100):
	"""
	Motore di sintesi di Acusticator, gia' V6.5, ora interno.
	Produce il buffer stereo float32 e non lo riproduce: della riproduzione si
	occupa il mixer della classe _Acusticator. Non va chiamato direttamente:
	si usa l'oggetto Acusticator, vedi la sua docstring.
	Restituisce un array (campioni, 2) float32, oppure None se lo score e' vuoto.
	Crea e riproduce (in maniera asincrona) un segnale acustico in base allo score fornito,
	utilizzando sounddevice per la riproduzione e applicando un envelope ADSR definito in termini
	di percentuali della durata della nota.
	Parametri:
	 - score: lista di valori in multipli di 4, in cui ogni gruppo rappresenta:
	     * nota (string|float): una nota musicale (es. "c4", "c#4"), un portamento separato da punto (es. "c4.e4", "880.920"), un valore in Hz, oppure "p" per pausa. Con i kind di rumore, da 5 a 8, questo campo contiene invece la banda del passabanda, per esempio "200-2000" oppure "100-1000.800-1800" per una banda che scorre.
	     * dur (float): durata in secondi.
	     * pan (float|str|tuple): panning stereo da -1 (sinistra) a 1 (destra), oppure portamento panning con due valori (es. "-1.1", "-0.5.0.5").
	     * vol (float|str|tuple): volume da 0 a 1, oppure portamento volume con due valori.
	 - kind (int): tipo di onda (1=sinusoide, 2=quadra, 3=triangolare, 4=dente di sega,
	     5=rumore bianco, 6=rosa, 7=marrone, 8=azzurro). Con i kind di rumore il primo
	     campo della quartina non e' una nota ma la banda, vedi parse_banda.
	 - adsr: lista di quattro valori [a, d, s, r] in percentuali (0 a 100).
	 - fs (int): frequenza di campionamento (default 44100 Hz).
	Se sync è False la riproduzione avviene in background, restituendo subito il controllo al chiamante.
	"""
	import sys

	import numpy as np
	from scipy import signal
	def note_to_freq(note):
		"""La frequenza di una nota della quartina. Un numero e' gia' una
		frequenza; una stringa di sole cifre pure, ed e' come si scrivono gli
		hertz in uno score; il punto separa le due note di un portamento; p e'
		la pausa e vale None.
		Il nome vero e proprio lo legge frequenza_nota, che dalla V161 sta in
		GBUtils per tutti: qui c'era una seconda copia del parsing, che non
		sapeva niente di microtoni e si fermava all'ottava di una cifra sola.
		Un nome illeggibile continua a far saltare la quartina con ValueError,
		dove frequenza_nota da sola risponderebbe zero."""
		if isinstance(note, (int, float)): return float(note)
		if isinstance(note, str):
			note_lower = note.lower()
			if note_lower == 'p': return None
			def parse_single(p):
				if p == 'p': return None
				if p.isdigit(): return float(p)
				freq = frequenza_nota(p)
				if not freq:
					raise ValueError(f"Formato nota non valido: '{p}'.")
				return freq
			if '.' in note_lower:
				parts = note_lower.split('.')
				if len(parts) == 2:
					return (parse_single(parts[0]), parse_single(parts[1]))
				else:
					raise ValueError(f"Formato portamento non valido: '{note}'")
			return parse_single(note_lower)
		else: raise TypeError(f"Tipo nota non riconosciuto: {type(note)}.")
	# adsr predefinito costruito a ogni chiamata: una lista come valore di
	# default sarebbe creata una volta sola e condivisa da tutti i chiamanti.
	if adsr is None: adsr = [.002, 0, 100, .002]
	if len(adsr) != 4: raise ValueError("ADSR deve contenere 4 valori")
	a_pct, d_pct, s_level_pct, r_pct = adsr
	if not all(0 <= val <= 100 for val in adsr): raise ValueError("Valori ADSR devono essere tra 0 e 100.")
	if a_pct + d_pct + r_pct > 100.001: raise ValueError(f"Somma A%({a_pct})+D%({d_pct})+R%({r_pct}) > 100 non permessa.")
	attack_frac = a_pct / 100.0
	decay_frac = d_pct / 100.0
	sustain_level = s_level_pct / 100.0
	release_frac = r_pct / 100.0
	segments = []
	rumore = kind in _RUMORE_ESPONENTE
	# La fase con cui comincia la nota seguente. Fino alla V8.1.0 ogni nota
	# ripartiva da zero, e fra due note contigue il segnale saltava dal valore
	# a cui la prima era arrivata allo zero da cui la seconda cominciava: e'
	# il gradino che si sentiva come uno schiocco, presente in cinquantuno
	# preset della collezione. Adesso l'onda prosegue da dove era arrivata, e
	# la saldatura non si sente perche' non c'e' niente da sentire.
	# Non e' una rampa nascosta e non tocca l'inviluppo: quello resta quello
	# che l'autore del preset ha scritto, e un attacco a zero continua a fare
	# lo schiocco che chi lo sceglie si aspetta. Qui si cura soltanto il
	# gradino che il motore stesso creava dove nessuno lo aveva chiesto.
	# La fase si porta avanti a una condizione sola: che la nota finisca con
	# il suono ancora acceso. Se l'inviluppo l'ha gia' spenta, o se prima c'e'
	# una pausa o un rumore, la nota seguente riparte da zero, altrimenti
	# comincerebbe a meta' onda dopo il silenzio e il gradino lo creeremmo
	# noi dove non c'era.
	fase_portata = 0.0
	for i in range(0, len(score), 4):
		# La conversione della nota sta dentro il try insieme al resto della
		# quartina: un nome di nota sbagliato deve far saltare quella quartina
		# come ogni altro errore, non abbattere l'applicazione che chiama.
		try:
			note_param, dur, pan_param, vol_param = score[i:i+4]
			dur = float(dur)
			pan = parse_pan_values(pan_param)
			vol = parse_vol_values(vol_param)
			if rumore:
				# Per il rumore il primo campo non e' una nota ma la banda.
				banda = parse_banda(note_param)
				freq = None if banda is None else _E_RUMORE
			else:
				banda = None
				freq = note_to_freq(note_param)
		except (IndexError, ValueError, TypeError) as e:
			print(f"Acusticator Warn: Parametri {i} errati. Ignoro. {e}", file=sys.stderr)
			continue
		if dur <= 0: continue # Ignora durata non positiva
		total_note_samples = round(dur * fs)
		if total_note_samples == 0: continue # Ignora durata troppo breve
		
		vol_portamento = None
		if isinstance(freq, tuple):
			f1, f2 = freq
			if f1 is None and f2 is None:
				freq = None
			elif f1 is None:
				freq = f2
				vol_portamento = 'fade_in'
			elif f2 is None:
				freq = f1
				vol_portamento = 'fade_out'
		
		if freq is None: # Pausa
			stereo_segment = np.zeros((total_note_samples, 2), dtype=np.float32)
			fase_portata = 0.0
		else: # Nota, portamento o rumore
			fase_dopo = 0.0
			if rumore:
				wave = _genera_rumore(kind, banda, total_note_samples, fs)
			elif kind == 1:
				if isinstance(freq, tuple):
					f_start, f_end = freq
					freq_array = np.linspace(f_start, f_end, total_note_samples, endpoint=False)
					passi = 2.0 * np.pi * freq_array.astype(np.float64) / fs
					phase = fase_portata + np.cumsum(passi)
					fase_dopo = phase[-1] + passi[-1]
				else:
					t = np.linspace(0, dur, total_note_samples, endpoint=False)
					phase = fase_portata + 2.0 * np.pi * freq * t
					fase_dopo = fase_portata + 2.0 * np.pi * freq * total_note_samples / fs
				wave = np.sin(phase).astype(np.float32)
			else:
				# PolyBLEP + Oversampling 8x con filtro Kaiser stretto per Synth-Grade Anti-Aliasing
				OVS = 8
				fs_ovs = fs * OVS
				total_ovs_samples = total_note_samples * OVS
				
				if isinstance(freq, tuple):
					f_start, f_end = freq
					freq_array_ovs = np.linspace(f_start, f_end, total_ovs_samples, endpoint=False)
					dt_ovs = freq_array_ovs / fs_ovs
					passi_ovs = 2.0 * np.pi * freq_array_ovs.astype(np.float64) / fs_ovs
					phase_ovs = fase_portata + np.cumsum(passi_ovs)
					fase_dopo = phase_ovs[-1] + passi_ovs[-1]
				else:
					dt_ovs = np.full(total_ovs_samples, freq / fs_ovs, dtype=np.float64)
					t_ovs = np.linspace(0, dur, total_ovs_samples, endpoint=False)
					phase_ovs = fase_portata + 2.0 * np.pi * freq * t_ovs
					fase_dopo = fase_portata + 2.0 * np.pi * freq * total_ovs_samples / fs_ovs
				
				t_phase = (phase_ovs / (2.0 * np.pi)) % 1.0
				dt_ovs = np.clip(dt_ovs, 1e-8, 0.5)
				
				def poly_blep(t_val, dt_val):
					res = np.zeros_like(t_val)
					m1 = t_val < dt_val
					tt1 = t_val[m1] / dt_val[m1]
					res[m1] = tt1 * (2.0 - tt1) - 1.0
					m2 = t_val > 1.0 - dt_val
					tt2 = (t_val[m2] - 1.0) / dt_val[m2]
					res[m2] = tt2 * (tt2 + 2.0) + 1.0
					return res
				
				if kind == 2: # Square
					wave_ovs = np.where(t_phase < 0.5, 1.0, -1.0)
					wave_ovs += poly_blep(t_phase, dt_ovs)
					wave_ovs -= poly_blep((t_phase + 0.5) % 1.0, dt_ovs)
				elif kind == 3: # Triangle
					# OVS 8x + Kaiser 14 è sufficiente a pulire la triangolare
					wave_ovs = 2.0 * np.abs(2.0 * t_phase - 1.0) - 1.0
				elif kind == 4: # Sawtooth
					wave_ovs = 2.0 * t_phase - 1.0
					wave_ovs -= poly_blep(t_phase, dt_ovs)
				
				# Decimazione con filtro anti-aliasing molto più aggressivo
				wave = signal.resample_poly(wave_ovs, up=1, down=OVS, window=('kaiser', 14.0)).astype(np.float32)
				
				# Compensazione per eventuali arrotondamenti di lunghezza
				if len(wave) > total_note_samples:
					wave = wave[:total_note_samples]
				elif len(wave) < total_note_samples:
					wave = np.pad(wave, (0, total_note_samples - len(wave)))
			attack_samples = round(attack_frac * total_note_samples)
			decay_samples = round(decay_frac * total_note_samples)
			release_samples = round(release_frac * total_note_samples)
			sustain_samples = total_note_samples - attack_samples - decay_samples - release_samples
			delta_samples = total_note_samples - (attack_samples + decay_samples + sustain_samples + release_samples)
			sustain_samples = max(0, sustain_samples + delta_samples)
			envelope = np.zeros(total_note_samples, dtype=np.float32); current_pos = 0
			if attack_samples > 0: envelope[current_pos : current_pos + attack_samples] = np.linspace(0., 1., attack_samples, dtype=np.float32); current_pos += attack_samples
			if decay_samples > 0: envelope[current_pos : current_pos + decay_samples] = np.linspace(1., sustain_level, decay_samples, dtype=np.float32); current_pos += decay_samples
			if sustain_samples > 0: envelope[current_pos : current_pos + sustain_samples] = sustain_level; current_pos += sustain_samples
			# --- Blocco Release Corretto ---
			if release_samples > 0:
				end_pos = min(current_pos + release_samples, total_note_samples)
				samples_in_this_segment = max(0, end_pos - current_pos)
				# Applica linspace solo se samples_in_this_segment è effettivamente > 0
				if samples_in_this_segment > 0:
					envelope[current_pos : end_pos] = np.linspace(sustain_level, 0., samples_in_this_segment, dtype=np.float32)
					current_pos = end_pos
			# --- Fine Blocco Release Corretto ---
			if current_pos < total_note_samples: envelope[current_pos:] = 0.0
			
			if vol_portamento == 'fade_out':
				envelope *= np.linspace(1.0, 0.0, total_note_samples, dtype=np.float32)
			elif vol_portamento == 'fade_in':
				envelope *= np.linspace(0.0, 1.0, total_note_samples, dtype=np.float32)
				
			if isinstance(vol, tuple):
				v_start, v_end = vol
				vol_array = np.linspace(v_start, v_end, total_note_samples, endpoint=False, dtype=np.float32)
				wave *= envelope * vol_array
			else:
				wave *= envelope * vol

			stereo_segment = np.zeros((total_note_samples, 2), dtype=np.float32)
			if isinstance(pan, tuple):
				p_start, p_end = pan
				pan_array = np.linspace(p_start, p_end, total_note_samples, endpoint=False, dtype=np.float32)
				pan_clipped = np.clip(pan_array, -1.0, 1.0)
				pan_angle = pan_clipped * (np.pi / 4.0)
				left_gain = np.cos(pan_angle + np.pi / 4.0)
				right_gain = np.sin(pan_angle + np.pi / 4.0)
			else:
				pan_clipped = np.clip(pan, -1.0, 1.0)
				pan_angle = pan_clipped * (np.pi / 4.0)
				left_gain = np.cos(pan_angle + np.pi / 4.0)
				right_gain = np.sin(pan_angle + np.pi / 4.0)
			stereo_segment[:, 0] = wave * left_gain
			stereo_segment[:, 1] = wave * right_gain
			# Si porta avanti solo se qui il suono e' ancora acceso: se
			# l'inviluppo l'ha spento, la nota seguente deve ripartire da zero
			# come ha sempre fatto.
			fase_portata = float(fase_dopo % (2.0 * np.pi)) if not rumore and float(envelope[-1]) > 1e-4 else 0.0
		segments.append(stereo_segment)
	if not segments: return None
	full_signal_float = np.concatenate(segments, axis=0)
	full_signal_float = np.clip(full_signal_float, -1.0, 1.0)
	return full_signal_float

class _Acusticator:
    """V8.2.0 di domenica 13 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode)

    Motore audio e libreria dei suoni del parco software.

    L'oggetto si usa in due modi, e sono indipendenti fra loro.

    Primo modo, chiamarlo come una funzione, che e' come ha sempre
    funzionato Acusticator e come lo usano tutte le chiamate esistenti:

        Acusticator(["c5", 0.2, 0, 0.5])
        Acusticator(["c4", 0.1, -1, 0.4, "g4", 0.1, 1, 0.4], kind=2, sync=True)

    Lo score e' una lista piatta di quartine [nota, durata, pan, volume]:
      nota    nome della nota come "c4" o "c#4", oppure un valore in Hz,
              oppure due valori uniti da un punto per il portamento come
              "c4.e4" o "880.920", oppure "p" per una pausa.
      durata  secondi.
      pan     da -1 tutto a sinistra a 1 tutto a destra; anche in
              portamento, come "-1.1".
      volume  da 0 a 1; anche in portamento.
    kind sceglie l'onda: 1 sinusoide, 2 quadra, 3 triangolare, 4 dente di
    sega, e da 5 a 8 il rumore, vedi piu' sotto. adsr sono quattro
    percentuali [attacco, decadimento, sostegno, rilascio]. Con sync a False
    il suono parte e il controllo torna subito.

    Con i kind da 5 a 8 si sintetizza rumore, e il colore e' la forma
    d'onda: 5 bianco, 6 rosa, 7 marrone, 8 azzurro. Il colore e' la
    pendenza dello spettro, rispettivamente piatta, meno 3, meno 6 e piu' 3
    dB per ottava. In quel caso il primo campo della quartina non contiene
    una nota ma la banda del filtro passabanda, con il trattino fra i due
    tagli e il punto per il portamento di ciascuno:

        ["200-2000", 2.0, 0, 0.4]        banda ferma fra 200 e 2000 Hz
        ["200-2000.200-400", 3, 0, 0.4]  il taglio alto scende: vento che cala
        ["100-3000.400-3000", 3, 0, 0.4] si muove solo il taglio basso
        ["100-1000.800-1800", 3, 0, 0.4] la banda intera sale
        ["100-3000.900-1100", 3, 0, 0.4] la banda si stringe attorno al mille
        ["n", 1.0, 0, 0.4]               nessuna banda, il colore puro
        ["p", 0.5, 0, 0.4]               pausa, come per le note

    Il trattino separa il taglio basso da quello alto, il punto separa la
    banda di partenza da quella d'arrivo: si legge "parte come questa banda
    e diventa quest'altra". I quattro valori si muovono ciascuno per conto
    suo, quindi la banda puo' allargarsi, stringersi, salire o scendere.
    Nel campo della banda il punto significa sempre scivolata e mai
    decimale, perche' su una frequenza di taglio i decimali non servono.
    Durata, panning, volume e inviluppo si comportano come per le note.

    Tre cose accadono al rumore senza che si debba chiederle. La banda non
    esce mai dai 40 Hz e dai 12 kHz, nemmeno chiedendola piu' larga: fuori
    di li' c'e' solo energia che l'orecchio non sente e gli altoparlanti non
    riproducono, e non e' poca. Il marrone ne spendeva il 97 per cento sotto
    i 20 Hz, tanto da sentirsi debolissimo pur essendo il piu' forte, e da
    schioccare all'attacco; l'azzurro il 59,9 per cento sopra i 14 kHz, che
    lo faceva arrivare piu' piano degli altri. Le due soglie sono state
    scelte da Gabriele all'ascolto, confrontando piu' valori.
    E ai due capi di ogni suono c'e' un breve smorzamento di quattro
    millisecondi: il rumore comincia e finisce su un valore casuale
    qualsiasi, che senza sarebbe uno scalino dal silenzio, cioe' un clic.
    Non basterebbe l'inviluppo ADSR, il cui attacco predefinito vale lo
    0,002 per cento della durata, un campione solo su un suono lungo.
    E il livello viene pareggiato su quanto un suono si sente, non su quanta
    energia ha: l'orecchio e' molto meno sensibile ai bassi, e a parita' di
    energia il marrone arrivava 8,9 dB piu' piano del bianco. Il pareggio usa
    la ponderazione A e un limitatore morbido, cosi' i quattro colori, a
    parita' di volume chiesto, arrivano all'orecchio ugualmente forti.

    Secondo modo, attingere alla collezione condivisa Acu_Collection.json,
    che e' la libreria dei suoni gia' pronti, curata con Acu_Maker:

        Acusticator.play("conferma")            suona un preset
        Acusticator.play("conferma", volume=.8) lo stesso, piu' forte
        Acusticator.play("conferma", pan=-0.6)  lo stesso, da sinistra
        Acusticator.play("conferma", pan=(-1,1)) lo stesso, che passa davanti
        Acusticator.list("vittoria")            cerca fra nomi e descrizioni
        Acusticator.preset("conferma")          restituisce (score, kind, adsr)
        Acusticator.info()                      due conti sulla collezione
        Acusticator.save(...)                   aggiunge un preset nuovo

    Nella collezione il volume di ogni quartina e' scritto come scarto
    rispetto a una base di 0.5, mentre il motore vuole il valore assoluto:
    la conversione, insieme all'appiattimento delle quartine, la fanno
    play e preset, ed e' il motivo per cui non va mai passato ad
    Acusticator uno score preso pari pari dal file.

    Un progetto puo' avere una collezione propria, che viene cercata prima
    di quella condivisa, cosi' i suoi suoni non devono per forza entrare
    nell'archivio comune:

        Acusticator.collezione("suoni_del_progetto.json")

    Un preset che non esiste non fa cadere niente: viene segnalato su
    stderr e il suono semplicemente non parte.

    Sotto entrambi i modi c'e' un mixer con un solo stream tenuto aperto.
    Prima ogni chiamata apriva uno stream suo dentro un thread suo, e lo
    chiudeva alla fine del suono: una raffica di otto notifiche apriva e
    chiudeva otto stream e otto thread. Sul ritardo il guadagno e'
    modesto, perche' il grosso e' il buffering della scheda e non dipende
    da noi: misurato su Realtek in MME, l'attesa prima di sentire scende
    da 4,1 a 0,2 ms, e una chiamata con sync=True su un suono da 100 ms
    da 253 a 227 ms. Il guadagno vero e' altrove: niente piu' apertura e
    chiusura continua del dispositivo, e i suoni che ora si sommano
    davvero fra loro, fino a trentadue per volta, invece di essere otto
    stream distinti che il sistema operativo mescola per conto suo.
    Quando le voci sono tutte occupate la piu' vecchia lascia il posto
    alla nuova, cosi' l'ultimo evento si sente sempre.

        Acusticator.setup(volume=0.6)   il volume generale, una volta sola
        Acusticator.stop()              silenzio immediato, stream aperto
        Acusticator.close()             chiude e libera la scheda audio
        Acusticator.stato()             come sta il mixer in questo momento

    Il volume generale impostato con setup si applica a tutto, quindi non
    serve piu' passarlo a ogni chiamata. Dopo il silenzio impostato, due
    minuti di partenza, lo stream si chiude da solo e la scheda torna
    libera; al suono successivo si riapre senza che nessuno debba fare
    niente, e alla fine del programma si chiude comunque.

    Il parametro sync dice quanto aspettare: False non aspetta, True
    aspetta la fine reale del suono, un numero aspetta al massimo quei
    secondi. La scadenza serve da rete di sicurezza, perche' se il
    dispositivo audio si pianta il chiamante non resti appeso.

    Con Acusticator vengono cinque funzioni che parlano soltanto la sua
    lingua, cioe' la grammatica delle quartine, e che per questo non sono
    nell'indice del pacchetto: da sole non vorrebbero dire niente.
      parse_pan_parts    legge uno o due valori di panorama da una stringa
      parse_pan_values   li riduce a un numero o a una coppia
      parse_vol_values   fa lo stesso per il volume
      parse_banda        legge la banda del rumore dal campo della nota
      panorama_spostato  sposta il panorama di uno score senza sostituirlo
    Le usa Acu_Maker, per controllare quello che l'utente scrive prima di
    scriverlo nella collezione.
    """

    NOME_COLLEZIONE = "Acu_Collection.json"
    BASE_VOL = 0.5
    # Quante voci insieme: erano 16 finche' il mixer era solo di Acusticator,
    # e dal mixer condiviso sono quelle che bastano anche a CWzator.
    VOCI_MAX = 32
    # Quanto si concede a un suono oltre la sua durata, prima di considerare
    # che il mixer si sia fermato. Comprende la latenza del dispositivo, che
    # sulle schede lente arriva a un decimo di secondo, e un po' di respiro.
    MARGINE_ATTESA = 2.0
    SILENZIO_MAX = 120.0
    BLOCCO = 256

    def __init__(self):
        # Lo stato del mixer non sta piu' qui: sta nel mixer condiviso, che
        # Acusticator usa senza possederlo. Qui resta cio' che e' suo, cioe'
        # la collezione dei preset.
        self._cache = {}
        self._locali = []

    def __call__(self, score, kind=1, adsr=None, fs=44100, sync=False, pan=None):
        """Sintetizza uno score e lo manda al mixer. Vedi la classe per lo score.

        sync dice quanto aspettare prima di restituire il controllo:
          False   non aspetta, il suono prosegue per conto suo.
          True    aspetta che il suono sia davvero finito nelle casse.
          numero  aspetta al massimo quei secondi, poi torna comunque.
        La scadenza e' una rete di sicurezza: se il dispositivo audio si
        pianta, il chiamante non resta appeso per sempre.
        pan sposta il panorama di tutto lo score, vedi play per come si
        comporta; None, il predefinito, lo lascia com'e'.
        Restituisce True se il suono e' stato accodato.
        """
        if pan is not None:
            score = self._sposta(score, pan)
        buffer = _sintetizza(score, kind, adsr, fs)
        if buffer is None:
            return False
        return self.riproduci(buffer, fs=fs, sync=sync)

    # --- Il mixer -------------------------------------------------------
    # Il mixer e' quello condiviso, uno solo per tutto il parco software:
    # Acusticator ne aveva uno a callback e CWzator uno a scrittura, e dal
    # 12 settembre 2026 ne esiste uno solo, a scrittura, per la issue 8.
    # Il callback perdeva campioni quando il programma calcolava mentre il
    # suono suonava, perche' doveva entrare in Python nel momento esatto in
    # cui la scheda aveva fame e restava in coda per il lucchetto
    # dell'interprete: sette buchi al secondo, misurati, contro nessuno.

    def setup(self, volume=None, voci_max=None, silenzio=None, fs=None, device=None):
        """Imposta il mixer, di solito una volta sola all'avvio dell'applicazione.

        volume    volume generale da 0 a 1, applicato a tutto cio' che suona.
                  Impostandolo qui non serve piu' passarlo a ogni chiamata.
        voci_max  quanti suoni possono sovrapporsi, 32 di partenza. Quando
                  sono tutte occupate, la voce piu' vecchia lascia il posto
                  alla nuova, cosi' l'ultimo evento si sente sempre. Erano 16
                  finche' il mixer era solo di Acusticator; adesso e'
                  condiviso e il numero e' quello che serviva al piu' esigente
                  dei due.
        silenzio  secondi di silenzio dopo i quali lo stream viene chiuso e
                  la scheda audio liberata, 120 di partenza. Si riapre da
                  solo al suono successivo.
        fs        frequenza di campionamento dello stream, 44100 di partenza.
        device    dispositivo di uscita, None per quello di sistema.
        Cambiare fs o device chiude lo stream in corso, che si riaprira'
        con i valori nuovi. Restituisce le impostazioni in vigore.
        Le impostazioni valgono per il mixer condiviso, quindi anche per chi
        altro lo stia usando.
        """
        mixer = _mixer_condiviso()
        if volume is not None:
            mixer._volume = max(0.0, min(1.0, float(volume)))
        if voci_max is not None:
            mixer._voci_max = max(1, int(voci_max))
        if silenzio is not None:
            mixer._silenzio = max(0.0, float(silenzio))
        riapri = False
        if fs is not None and int(fs) != mixer._fs:
            mixer._fs = int(fs)
            riapri = True
        if device is not None and device != mixer._device:
            mixer._device = device
            riapri = True
        if riapri:
            mixer.chiudi()
        return {"volume": mixer._volume, "voci_max": mixer._voci_max,
                "silenzio": mixer._silenzio, "fs": mixer._fs, "device": mixer._device}

    def riproduci(self, buffer, fs=None, sync=False):
        """Manda al mixer un buffer gia' pronto, stereo float32 fra -1 e 1.

        E' la strada di servizio usata da __call__; torna utile a chi si
        sintetizza l'audio per conto suo e vuole comunque passare dal
        mixer condiviso.
        """
        mixer = _mixer_condiviso()
        voce = mixer.suona(buffer, fs=fs, sync=sync)
        if voce is None:
            return False
        if sync is True:
            # I campioni sono usciti dal mixer ma non ancora dalle casse:
            # senza questa attesa un suono di congedo verrebbe troncato.
            mixer.aspetta_uscita()
        return True

    def stop(self):
        """Zittisce subito tutto quello che sta suonando, senza chiudere nulla.

        Lo stream resta aperto e pronto: e' quello che serve quando l'utente
        preme Esc e vuole silenzio immediato. Restituisce quante voci ha
        interrotto. Zittisce il mixer condiviso, quindi anche cio' che vi
        stesse suonando qualcun altro.
        """
        return _mixer_condiviso().ferma()

    def close(self):
        """Zittisce e chiude lo stream, liberando la scheda audio.

        Da chiamare all'uscita dell'applicazione. Non serve farlo per forza:
        dopo il silenzio impostato con setup lo stream si chiude da solo, e
        al suono successivo si riapre. Restituisce True se c'era da chiudere.
        """
        mixer = _mixer_condiviso()
        c_era = mixer.stato()["aperto"]
        mixer.chiudi()
        return c_era

    def stato(self):
        """Come sta il mixer adesso, come dizionario. Utile per capire i guai."""
        mixer = _mixer_condiviso()
        dentro = mixer.stato()
        return {"stream_aperto": dentro["aperto"], "voci_attive": dentro["voci"],
                "voci_max": mixer._voci_max, "volume": mixer._volume,
                "silenzio": mixer._silenzio, "fs": dentro["frequenza"],
                "canali": dentro["canali"], "device": mixer._device,
                "buchi": dentro["buchi"]}

    def _sposta(self, score, pan):
        """Applica lo spostamento di panorama, dopo aver controllato che sia
        chiedibile. Un pan senza senso non zittisce il suono: lo si segnala e
        si suona il preset dov'era, perche' un avviso di posizione non vale
        la perdita del suono."""
        va_bene = isinstance(pan, (int, float)) and not isinstance(pan, bool)
        if not va_bene and isinstance(pan, (tuple, list)) and len(pan) == 2:
            va_bene = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in pan)
        if not va_bene and isinstance(pan, str):
            va_bene = pan.strip() != ""
        if not va_bene:
            self._avvisa(f"pan ({pan!r}) non valido: un numero fra -1 e 1, una coppia, o la forma con il punto come '-1.1'. Lo ignoro.")
            return score
        return panorama_spostato(score, pan)

    def _avvisa(self, messaggio):
        import sys
        print(f"Acusticator: {messaggio}", file=sys.stderr)

    def _percorso_hub(self):
        """Dove sta la collezione condivisa, da sorgente e da eseguibile."""
        import os
        import sys
        if getattr(sys, "frozen", False):
            for base in (getattr(sys, "_MEIPASS", None), os.path.dirname(sys.executable)):
                if base:
                    p = os.path.join(base, self.NOME_COLLEZIONE)
                    if os.path.isfile(p):
                        return p
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), self.NOME_COLLEZIONE)

    def _percorsi(self):
        """Le collezioni da consultare, quelle del progetto prima dell'hub."""
        return list(self._locali) + [self._percorso_hub()]

    def collezione(self, percorso):
        """Aggiunge una collezione del progetto, cercata prima di quella condivisa.

        Il percorso relativo si intende rispetto al file che chiama.
        Restituisce il numero di preset letti, oppure 0 se il file manca.
        """
        import os
        import sys
        if not os.path.isabs(percorso):
            try:
                chiamante = sys._getframe(1).f_globals["__file__"]
                percorso = os.path.join(os.path.dirname(os.path.abspath(chiamante)), percorso)
            except (AttributeError, KeyError, ValueError):
                percorso = os.path.abspath(percorso)
        percorso = os.path.normpath(percorso)
        dati = self._carica(percorso)
        if dati is None:
            self._avvisa(f"collezione non trovata: {percorso}")
            return 0
        if percorso not in self._locali:
            self._locali.insert(0, percorso)
        return len(dati)

    def _carica(self, percorso):
        """Legge una collezione, tenendola in memoria. None se non c'e'."""
        import json
        import os
        if percorso in self._cache:
            return self._cache[percorso]
        if not os.path.isfile(percorso):
            return None
        try:
            with open(percorso, encoding="utf-8") as f:
                dati = json.load(f)
        except (OSError, ValueError) as e:
            self._avvisa(f"collezione illeggibile, {percorso}: {e}")
            return None
        if not isinstance(dati, dict):
            self._avvisa(f"collezione malformata, {percorso}: la radice non e' un dizionario")
            return None
        self._cache[percorso] = dati
        return dati

    def reload(self):
        """Dimentica quello che ha in memoria: da rilanciare dopo Acu_Maker."""
        self._cache.clear()

    def _cerca(self, nome):
        """Il primo preset con quel nome, e da quale collezione viene."""
        for percorso in self._percorsi():
            dati = self._carica(percorso)
            if dati and nome in dati:
                return dati[nome], percorso
        return None, None

    def preset(self, nome, volume=None, pan=None):
        """Restituisce (score, kind, adsr) pronti da passare al motore.

        Lo score torna appiattito e con i volumi assoluti, cioe' gia'
        convertiti dagli scarti scritti nel file. volume, se dato,
        sostituisce la base 0.5 su cui gli scarti si applicano: e' il modo
        di rispettare il volume scelto dall'utente nelle impostazioni.
        pan sposta il panorama dello score che esce, vedi play.
        Restituisce (None, None, None) se il preset non esiste.
        Attenzione a non chiederlo due volte: uno score gia' spostato qui e
        poi passato all'oggetto chiamabile con un altro pan si sposta ancora.
        """
        dati, _ = self._cerca(nome)
        if dati is None:
            self._avvisa(f"preset sconosciuto: {nome}")
            return None, None, None
        base = self.BASE_VOL if volume is None else float(volume)
        piatto = []
        for quartina in dati.get("score", []):
            try:
                # Il panorama della quartina si chiama panorama e non pan:
                # il parametro pan e' un'altra cosa, e chiamarli uguale lo
                # copriva, cosi' che lo spostamento chiesto veniva ignorato e
                # al suo posto si usava il panorama dell'ultima quartina.
                nota, dur, panorama, scarto = quartina
            except (TypeError, ValueError):
                self._avvisa(f"preset {nome}: quartina malformata, la salto")
                continue
            if isinstance(scarto, str):
                assoluto = scarto
            else:
                assoluto = max(0.0, min(1.0, base + float(scarto)))
            piatto.extend([nota, dur, panorama, assoluto])
        if pan is not None:
            piatto = self._sposta(piatto, pan)
        return piatto, dati.get("kind", 1), dati.get("adsr")

    def play(self, nome, sync=False, volume=None, pan=None):
        """Suona un preset della collezione. Vero se e' partito.

        pan sposta il preset fra i due altoparlanti, e ha la stessa
        grammatica del panorama delle quartine: un numero fra -1, tutto a
        sinistra, e 1, tutto a destra, oppure una coppia come (-1, 1), che
        fa scorrere il suono da un lato all'altro lungo tutta la sua durata.
        None, il predefinito, lascia il preset dov'e'.
          play("conferma", pan=-0.6)     la conferma arriva da sinistra
          play("conferma", pan=(-1, 1))  la conferma passa davanti
        E' uno spostamento, non una sostituzione: il panorama che il preset
        ha di suo resta, e si stringe soltanto quel tanto che serve a non
        uscire dai bordi. volo_radente spostato a 0,6 vola da 0,2 a 1
        invece di appiattirsi contro il bordo destro a meta' volo, che e'
        cio' che sarebbe successo sommando e tagliando: dei centocinque
        preset che si muovono, cinquantuno ci sbattevano.
        Con pan a zero non cambia un campione rispetto a chiamarlo senza.
        """
        score, kind, adsr = self.preset(nome, volume=volume, pan=pan)
        if not score:
            return False
        self(score, kind=kind, adsr=adsr, sync=sync)
        return True

    def list(self, filtro=None):
        """I nomi dei preset, in ordine.

        Con un filtro restituisce solo quelli il cui nome o la cui
        descrizione contengono quel testo, senza badare alle maiuscole.
        """
        nomi = {}
        for percorso in self._percorsi():
            dati = self._carica(percorso)
            if not dati:
                continue
            for nome, v in dati.items():
                nomi.setdefault(nome, v)
        if not filtro:
            return sorted(nomi)
        cercato = str(filtro).lower()
        return sorted(
            n for n, v in nomi.items()
            if cercato in n.lower() or cercato in str(v.get("descrizione", "")).lower()
        )

    def descrizione(self, nome):
        """La descrizione di un preset, stringa vuota se non ce l'ha."""
        dati, _ = self._cerca(nome)
        return "" if dati is None else str(dati.get("descrizione", ""))

    def info(self):
        """Due conti sulle collezioni consultabili, come dizionario."""
        conti = {"collezioni": [], "preset": 0, "senza_descrizione": 0, "durata_media": 0.0}
        durate = []
        visti = set()
        for percorso in self._percorsi():
            dati = self._carica(percorso)
            if not dati:
                continue
            conti["collezioni"].append((percorso, len(dati)))
            for nome, v in dati.items():
                if nome in visti:
                    continue
                visti.add(nome)
                conti["preset"] += 1
                if not str(v.get("descrizione", "")).strip():
                    conti["senza_descrizione"] += 1
                try:
                    durate.append(sum(float(q[1]) for q in v.get("score", [])))
                except (TypeError, ValueError, IndexError):
                    pass
        if durate:
            conti["durata_media"] = round(sum(durate) / len(durate), 3)
        return conti

    def save(self, nome, score, kind=1, adsr=None, descrizione="", percorso=None):
        """Aggiunge o sostituisce un preset in una collezione.

        score si passa nella stessa forma che vuole il motore, cioe' la
        lista piatta con i volumi assoluti: qui viene ripiegato in
        quartine e i volumi tornano scarti dalla base 0.5, che e' il
        formato del file.
        Da eseguibile congelato non si salva: la collezione sta dentro la
        cartella del pacchetto, che ogni aggiornamento sostituisce, quindi
        il preset andrebbe perso. Aggiungere suoni e' un lavoro da
        sorgente, con Acu_Maker o con questo metodo.
        Restituisce True se ha scritto.
        """
        import json
        import os
        import sys
        if getattr(sys, "frozen", False):
            self._avvisa("da eseguibile la collezione non si scrive, usa Acu_Maker da sorgente")
            return False
        if not str(descrizione).strip():
            self._avvisa(f"preset {nome} senza descrizione: non lo salvo")
            return False
        if percorso is None:
            percorso = self._locali[0] if self._locali else self._percorso_hub()
        dati = self._carica(percorso)
        if dati is None:
            dati = {}
        quartine = []
        for i in range(0, len(score), 4):
            try:
                nota, dur, pan, vol = score[i:i + 4]
            except ValueError:
                self._avvisa(f"preset {nome}: lo score non e' fatto di quartine")
                return False
            if isinstance(vol, str):
                scarto = vol
            else:
                scarto = round(float(vol) - self.BASE_VOL, 4)
            quartine.append([nota, dur, pan, scarto])
        if not quartine:
            self._avvisa(f"preset {nome}: score vuoto, non lo salvo")
            return False
        dati[nome] = {
            "descrizione": str(descrizione),
            "score": quartine,
            "kind": kind,
            "adsr": adsr if adsr is not None else [0.002, 0.0, 100.0, 0.002],
        }
        try:
            with open(percorso, "w", encoding="utf-8") as f:
                json.dump(dati, f, indent=4)
        except OSError as e:
            self._avvisa(f"non riesco a scrivere {os.path.basename(percorso)}: {e}")
            return False
        self._cache[percorso] = dati
        return True


Acusticator = _Acusticator()

def _dgt_limita_default(default, kind, minimo, massimo):
	'''Riporta il predefinito di dgt dentro i limiti dichiarati nella stessa
	chiamata e lo converte al tipo chiesto con kind, cioe' gli applica le
	stesse regole che dgt applica a cio' che l'utente digita.
	Riceve i limiti gia' risolti da dgt: per gli interi e i decimali sono il
	minimo e il massimo del valore, per le stringhe sono smin e smax, cioe' la
	lunghezza. Restituisce il valore da consegnare a chi ha chiamato dgt.
	Un predefinito piu' corto di smin fa eccezione e viene restituito com'e':
	allungarlo non si puo', e rifiutarlo toglierebbe a chi chiama il modo di
	offrire una risposta vuota che significhi nessuna scelta.
	Solleva ValueError se il predefinito non e' convertibile al tipo chiesto,
	perche' quello e' un errore di chi programma e non di chi digita.
	'''
	if kind == "i":
		try: valore = int(default)
		except (TypeError, ValueError):
			raise ValueError(f"dgt: il default {default!r} non e' convertibile in intero.") from None
		return min(max(valore, minimo), massimo)
	if kind == "f":
		try: valore = float(default)
		except (TypeError, ValueError):
			raise ValueError(f"dgt: il default {default!r} non e' convertibile in decimale.") from None
		return min(max(valore, minimo), massimo)
	return str(default)[:massimo]
def dgt(prompt="", kind="s", imin=-999999999, imax=999999999, fmin=-999999999.9, fmax=999999999.9, smin=0, smax=256, pwd=False, default=None):
	'''V2.0.0 di lunedi' 7 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' auto)
	Potenzia input con i controlli che input non ha, e ripete la domanda
	finche' non riceve un valore accettabile.
	Riceve il prompt, il tipo e i limiti:
	  imin e imax, minimo e massimo per gli interi;
	  fmin e fmax, minimo e massimo per i decimali;
	  smin e smax, lunghezza minima e massima per le stringhe.
	kind vale s per stringa, i per intero, f per decimale.
	Un valore digitato fuori dai limiti viene riportato al limite piu' vicino,
	e la funzione lo dice; con pwd vero viene invece rifiutato e la domanda si
	ripete, perche' cio' che si digita mascherato non si puo' rileggere.
	default viene restituito quando si preme invio senza aver digitato niente.
	Dalla V2.0.0, prima di essere restituito, viene convertito al tipo chiesto
	e riportato dentro i limiti: fino alla 1.10 li scavalcava, quindi una
	chiamata che dichiarava dei limiti poteva restituire un valore che li
	violava, e perfino di un tipo diverso da quello chiesto. Fa eccezione il
	predefinito piu' corto di smin, che viene restituito com'e'.
	Cio' che l'utente digita viene restituito fedelmente, spazi ai bordi
	compresi: e' chi chiama a decidere se toglierli.
	Solleva ValueError quando kind non e' valido, quando i limiti sono
	incoerenti fra loro e quando il predefinito non e' convertibile al tipo
	chiesto; solleva EOFError quando non c'e' un terminale da cui leggere.
	Sono errori di chi programma, e dalla V2.0.0 la funzione li riferisce a
	chi l'ha chiamata invece di stamparli su una console che, in una
	applicazione con interfaccia grafica, potrebbe non esistere. Restano
	stampati soltanto i messaggi rivolti a chi sta digitando, che sono il
	dialogo di cui la funzione vive.
	'''
	import getpass
	import math
	if not isinstance(kind, str) or not kind:
		raise ValueError(f"dgt: kind deve essere una stringa non vuota, ricevuto {kind!r}.")
	kind = kind[0].lower()
	if kind not in "sif":
		raise ValueError(f"dgt: kind deve valere s, i oppure f, ricevuto {kind!r}.")
	if kind == "i":
		if imin > imax:
			raise ValueError(f"dgt: imin {imin} e' maggiore di imax {imax}.")
		minimo, massimo = math.ceil(imin), math.floor(imax)
		if minimo > massimo:
			raise ValueError(f"dgt: fra imin {imin} e imax {imax} non c'e' nessun intero.")
	elif kind == "f":
		if fmin > fmax:
			raise ValueError(f"dgt: fmin {fmin} e' maggiore di fmax {fmax}.")
		minimo, massimo = float(fmin), float(fmax)
	else:
		if smin < 0:
			raise ValueError(f"dgt: smin non puo' essere negativo, ricevuto {smin}.")
		if smin > smax:
			raise ValueError(f"dgt: smin {smin} e' maggiore di smax {smax}.")
		minimo, massimo = smin, smax
	while True:
		try:
			p = getpass.getpass(prompt) if pwd else input(prompt)
		except EOFError:
			raise EOFError("dgt: non c'e' un terminale da cui leggere, lo standard input e' chiuso.") from None
		if p == "" and default is not None:
			return _dgt_limita_default(default, kind, minimo, massimo)
		if kind == "i":
			try: valore = int(p)
			except ValueError:
				print("Serve un numero intero.")
				continue
		elif kind == "f":
			try: valore = float(p)
			except ValueError:
				print("Serve un numero decimale.")
				continue
		else:
			valore = p
		misura = len(valore) if kind == "s" else valore
		if pwd:
			if misura < minimo or misura > massimo:
				if kind == "s": print(f"Lunghezza fuori da {smin} a {smax}.")
				else: print(f"Fuori dai limiti {minimo} - {massimo}.")
				continue
			return valore
		if misura < minimo:
			if kind == "s":
				print(f"Troppo corta, servono {smin} caratteri.")
				continue
			print(f"Troppo basso, accettato {minimo}.")
			return minimo
		if misura > massimo:
			if kind == "s":
				print(f"Troppo lunga, accettati {smax} caratteri.")
				return valore[:smax]
			print(f"Troppo alto, accettato {massimo}.")
			return massimo
		return valore
# Le tre formattazioni della issue 9: una dimensione, una durata e un testo
# troppo lungo, scritti allo stesso modo da tutto il parco software invece che
# riscritti in ogni programma. Non stampano niente e non sanno dove finira'
# cio' che restituiscono: la stringa torna a chi ha chiamato, che decide se
# metterla in una riga di avanzamento, in un report o in una finestra.
def formatta_dimensione(byte, decimali=2, separatore=".", unita=("B", "KB", "MB", "GB", "TB", "PB"), byte_interi=False):
	"""V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	Una quantita' di byte con l'unita' adatta alla sua grandezza: 1.40 GB.
	Sale di unita' ogni 1024, si ferma sull'ultima che ha a disposizione e
	mette il segno meno davanti ai valori negativi, che servono a chi mostra
	di quanto una misura e' cambiata rispetto a prima. Il piu' davanti ai
	positivi non c'e', e lo aggiunge chi chiama se gli serve: una dimensione,
	di solito, e' soltanto una dimensione.
	  byte: la quantita' da scrivere, anche negativa e anche con la virgola.
	  decimali: quante cifre dopo il separatore. Due come nasce, che e' la
	    forma con cui scriba la scriveva; su un display braille sono spesso
	    rumore e uno basta.
	  separatore: il punto decimale, predefinito il punto. Chi scrive in
	    italiano passa la virgola.
	  unita: i nomi delle unita', dalla piu' piccola alla piu' grande. Quelli
	    predefiniti sono le sigle internazionali, che non parlano nessuna
	    lingua; chi vuole byte per esteso, o i nomi di un'altra lingua, passa
	    la propria sequenza. Oltre l'ultima non si sale: con le predefinite,
	    una quantita' enorme resta in PB.
	  byte_interi: sotto il chilo niente decimali, 980 byte invece di
	    980.00 byte, perche' mezzo byte non esiste. Sopra il chilo non cambia
	    niente.
	Restituisce la stringa, con l'unita' staccata dal numero da uno spazio.
	Solleva ValueError se le unita' sono una sequenza vuota o se i decimali
	sono negativi.
	Nasce dalla issue 9, dove la stessa formula era riscritta in scriba, in
	Cartella e a mano in Tornello e in orologic."""
	if not unita:
		raise ValueError("formatta_dimensione: serve almeno un nome di unita'")
	if decimali < 0:
		raise ValueError(f"formatta_dimensione: decimali negativi: {decimali}")
	valore = float(byte)
	segno = "-" if valore < 0 else ""
	valore = abs(valore)
	ultima = len(unita) - 1
	posto = 0
	while valore >= 1024.0 and posto < ultima:
		valore /= 1024.0
		posto += 1
	if posto == 0 and byte_interi:
		return f"{segno}{int(valore)} {unita[0]}"
	numero = f"{valore:.{decimali}f}"
	if separatore != ".":
		numero = numero.replace(".", separatore)
	return f"{segno}{numero} {unita[posto]}"
def formatta_durata(secondi, compatta=True, vuoto="--:--"):
	"""V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	Una durata in cifre, come la mostra un cronometro: un'ora, due minuti e tre
	secondi diventano 01:02:03, e tre minuti e mezzo diventano 03:30.
	  secondi: quanti ne sono passati, o quanti ne mancano. I decimi si
	    scartano invece di arrotondare, cosi' una durata non viene mai
	    annunciata piu' lunga di quello che e'.
	  compatta: le ore compaiono soltanto quando ci sono. Falso le scrive
	    sempre, anche a zero, e serve a chi incolonna piu' durate una sotto
	    l'altra, dove una riga piu' corta delle altre si legge male.
	  vuoto: cosa rispondere quando la durata non c'e', cioe' quando secondi e'
	    None o non e' positivo. Una durata che non si conosce non e' una durata
	    di zero, e chi la mostra deve poterle dare l'aspetto che preferisce.
	Le ore non si fermano a ventiquattro: due giorni fanno 48:00:00, perche'
	questa e' una durata e non un orario.
	Restituisce la stringa. Le durate dette a parole, con le unita' scritte per
	esteso, restano a chi chiama: i nomi delle unita', i plurali e la
	congiunzione che unisce l'ultimo pezzo sono lingua, e questo pacchetto,
	chiamato da tutto il parco software, non sa in che lingua parlare.
	Nasce dalla issue 9, dove la stessa formula era scritta due volte dentro
	scriba."""
	if secondi is None or secondi <= 0:
		return vuoto
	minuti, avanzo = divmod(int(secondi), 60)
	ore, minuti = divmod(minuti, 60)
	if ore or not compatta:
		return f"{ore:02d}:{minuti:02d}:{avanzo:02d}"
	return f"{minuti:02d}:{avanzo:02d}"
def accorcia(testo, lunghezza, posizione="centro"):
	"""V1.0.0 di lunedì 14 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalità auto)
	Un testo ridotto alla larghezza voluta, con tre puntini al posto di cio'
	che e' stato tolto. Un testo che ci sta gia' torna intatto.
	  testo: quello da accorciare.
	  lunghezza: quanti caratteri puo' occupare. Il risultato non li supera
	    mai, e puo' venire piu' corto di uno quando lo spazio da dividere fra
	    testa e coda e' dispari.
	  posizione: da dove togliere. "centro", il predefinito, tiene la testa e
	    la coda e leva la pancia, ed e' la forma giusta per un percorso, dove
	    il nome del file sta in fondo ed e' quello che interessa; "fine" tiene
	    la testa, "inizio" tiene la coda.
	Sotto i quattro caratteri i puntini non starebbero insieme a nient'altro, e
	il testo viene tagliato e basta; con lunghezza zero o negativa torna la
	stringa vuota.
	Solleva ValueError se la posizione non e' una delle tre.
	Nasce dalla issue 9, per le righe di avanzamento che devono stare nei
	quaranta caratteri di un display braille."""
	if posizione not in ("centro", "inizio", "fine"):
		raise ValueError(f"accorcia: posizione sconosciuta: {posizione!r}")
	if lunghezza <= 0:
		return ""
	if len(testo) <= lunghezza:
		return testo
	if lunghezza <= 3:
		return testo[:lunghezza]
	if posizione == "inizio":
		return "..." + testo[-(lunghezza - 3):]
	meta = (lunghezza - 3) // 2
	if posizione == "fine" or meta < 1:
		return testo[:lunghezza - 3] + "..."
	return f"{testo[:meta]}...{testo[-meta:]}"
def _percorso_risorsa(nome_file, risalita=1):
	"""Dove sta un file in sola lettura che viaggia con l'applicazione, per
	esempio la guida. Un percorso assoluto torna com'e'. Uno relativo si cerca
	prima fra le risorse del pacchetto PyInstaller, in sys._MEIPASS, quando il
	programma e' congelato, perche' i file dichiarati nei datas vengono
	scompattati li' e non accanto all'eseguibile; poi nella cartella di chi
	chiama secondo _cartella_chiamante, mai nella directory di lavoro. Se non
	esiste in nessuno dei due torna quello nella cartella di chi chiama, cosi'
	che l'errore di chi lo apre dica dove lo si aspettava. risalita vale 1 per
	chi la invoca dal corpo di una utilita' pubblica. Nasce con la issue 26
	per manuale; la issue 20 potra' renderla pubblica per tutti i progetti."""
	import os
	import sys
	if os.path.isabs(nome_file):
		return nome_file
	candidati = []
	if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
		candidati.append(os.path.join(sys._MEIPASS, nome_file))
	candidati.append(os.path.join(_cartella_chiamante(risalita + 1), nome_file))
	for percorso in candidati:
		if os.path.exists(percorso):
			return percorso
	return candidati[-1]

def manuale(nf=None, testo=None, nome="", codifica=None, righe_pagina=None):
	'''V2.1.0 di venerdì 11 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode)
	Impagina un testo lungo e lo mostra a pezzi, fermandosi a ogni pagina.
	Riceve, in alternativa fra loro:
	  nf, il nome del file da mostrare, assoluto oppure relativo: quello
	    relativo si cerca prima fra le risorse del pacchetto PyInstaller, in
	    sys._MEIPASS, quando il programma e' congelato, e poi nella cartella
	    di chi chiama, mai nella directory di lavoro;
	  testo, una stringa gia' in memoria, per impaginare cio' che non e' un
	    file, per esempio le note di una release arrivate dalla rete.
	nome e' cio' che si sta mostrando e apre il prompt di fine pagina. Il
	  predefinito e' la stringa vuota: manuale non conosce la lingua di chi la
	  chiama, quindi la parola la passa il chiamante, gia' tradotta.
	codifica None significa prova utf-8 e, se non si decodifica, ripiega sulla
	  codifica preferita dal sistema; un valore esplicito impone quello e basta.
	righe_pagina None significa quante righe entrano nella console, misurate a
	  ogni chiamata, con quindici come ripiego se non c'e' un terminale da
	  misurare; un numero impone quello.
	A fine pagina il prompt e' nome seguito da (pagina / pagine), fra due
	ritorni carrello perche' il display braille vi resti sopra, e aspetta un
	tasto: Esc interrompe la lettura, ogni altro tasto continua. Fino alla
	V2.0.0 la domanda era una frase italiana e si usciva con la lettera e.
	Restituisce True se il testo e' stato mostrato fino in fondo, False se
	l'utente ha interrotto la lettura: fino alla 1.0.1 chi chiamava non aveva
	modo di saperlo.
	Solleva ValueError se non riceve ne' nf ne' testo, oppure se li riceve
	entrambi, e OSError se il file non si apre o non si decodifica con nessuna
	codifica. Sono notizie per chi chiama, e dalla V2.0.0 la funzione non le
	stampa piu' per conto proprio: in una applicazione con interfaccia grafica
	nessuno le leggerebbe. Dal tasto, letto con key, arrivano KeyboardInterrupt
	con Ctrl+C ed EOFError quando non c'e' una console da cui leggere.
	'''
	import os
	if (nf is None) == (testo is None):
		raise ValueError("manuale: serve o un nome di file o un testo gia' pronto, non nessuno dei due e non tutti e due.")
	if testo is None:
		percorso = _percorso_risorsa(nf, 1)
		errore = None
		for prova in ([codifica] if codifica else ["utf-8", None]):
			try:
				with open(percorso, "rt", encoding=prova) as f:
					testo = f.read()
				break
			except UnicodeDecodeError as e:
				errore = e
		if testo is None:
			raise OSError(f"manuale: {nome or nf} in {percorso} non si decodifica.") from errore
	righe = testo.splitlines()
	if not righe: return True
	if righe_pagina is None:
		try: righe_pagina = max(5, os.get_terminal_size().lines - 2)
		except OSError: righe_pagina = 15
	pagine = (len(righe) + righe_pagina - 1) // righe_pagina
	etichetta = f"{nome} " if nome else ""
	for numero, riga in enumerate(righe, 1):
		print(riga)
		if numero % righe_pagina == 0 and numero < len(righe):
			tasto = key(f"\r{etichetta}({numero // righe_pagina} / {pagine})\r"); print()
			if tasto == '\x1b': return False
	return True

def menu(d=None, p="> ", ntf="", show=True, show_only=False, keyslist=True, pager=20, show_on_filter=True, numbered=False, ordered=True, empty_enter=None):
    """V5.1.0 - venerdì 11 settembre 2026 - Gabriele Battaglia (IZ4APU), Stella Gemini 3.5 Flash & ClaudIA (Claude Fable 5.1, UltraCode)
    Crea un menu interattivo da un dizionario, con filtraggio e autocompletamento robusto.
    Parametri:
    d: dizionario con coppie chiave:descrizione.
    p: prompt personalizzato; usato in modalità non-keyslist o in modalità numerata.
    ntf: messaggio stampato quando cio' che si e' digitato non corrisponde a
      nessuna voce. Il predefinito e' la stringa vuota, cioe' nessuna parola:
      menu non conosce la lingua del programma che la chiama, quindi il testo
      lo passa il chiamante, gia' tradotto, e senza testo resta il conteggio
      (0 / 0), che e' uguale in ogni lingua.
    show: se True, mostra il menu iniziale completo prima del prompt.
    show_only: se True, mostra il menu completo e termina (non interattivo).
    keyslist: se True (default), il prompt suggerisce i caratteri per l'autocompletamento.
    pager: numero di elementi da mostrare per pagina. Impostare a 0 per disabilitare.
    show_on_filter: se True, la lista delle opzioni si aggiorna visivamente a ogni tasto.
    numbered: se True, il menu diventa numerato, con selezione interattiva dei numeri.
    ordered: se True (default), le voci del menu vengono ordinate alfabeticamente per chiave.
    empty_enter: cio' che viene restituito quando si preme Invio senza aver digitato niente.
    Restituisce:
    La chiave scelta dal dizionario 'd', oppure None se l'utente annulla con Esc;
    Invio senza aver digitato niente restituisce empty_enter, che per predefinito e' None.
    None e' anche cio' che si riceve quando 'd' e' vuoto: dalla V5.0.0 il caso
    non viene piu' annunciato con una stampa, perche' chi ha passato il
    dizionario sa gia' che era vuoto e in una interfaccia grafica quella frase
    non la leggerebbe nessuno.
    Dalla V5.1.0 menu non dice piu' una parola di suo: chiamata da tutto il
    parco software, non sa in che lingua parlare. Dopo ogni elenco stampa un
    conteggio che ha la stessa forma in ogni lingua, (viste / totale), seguito
    da - (pagina / pagine) quando le pagine sono almeno due; a fine pagina lo
    stesso conteggio e' il prompt che aspetta un tasto, fra due ritorni
    carrello perche' il display braille vi resti sopra: Esc interrompe
    l'elenco, ogni altro tasto continua. Quando il filtro non trova niente
    stampa ntf, o (0 / 0) se ntf e' vuoto; Invio su un prefisso ambiguo non
    dice piu' niente, e l'elenco dei candidati si ripresenta da solo quando
    show_on_filter e' vero, altrimenti lo si chiede con il punto
    interrogativo. I tasti li legge la key di questo pacchetto invece di una
    copia propria: frecce, tasti funzione, Tab e le combinazioni con Ctrl e
    Alt vengono ignorati invece di finire nel filtro, Ctrl+C interrompe il
    programma con KeyboardInterrupt come in qualunque programma da console,
    e senza una console da cui leggere si riceve EOFError invece di
    un'attesa senza fine.
    Dalla V5.0.0 l'elenco non ha piu' righe di trattini attorno alle voci ne'
    fra la chiave e la descrizione: le regole di accessibilita' vietano i
    separatori grafici, e menu, essendo chiamata da tutto il parco software,
    era il posto in cui se ne stampavano di piu'.
    """
    import os
    if d is None: d = {}
    def lcp(strings):
        """Calcola il prefisso comune più lungo da una lista di stringhe ignorando il case."""
        if not strings: return ""
        lower_strings = [s.lower() for s in strings]
        prefix_len = len(os.path.commonprefix(lower_strings))
        return strings[0][:prefix_len]
    def Mostra(items_to_show, pager, is_numbered, num_map=None):
        """Elenca le voci, fermandosi ogni pager righe, e chiude con il
        conteggio (viste / totale) - (pagina / pagine), che a fine pagina e'
        anche il prompt fra due ritorni carrello. Restituisce False se
        l'elenco e' stato interrotto con Esc, True altrimenti."""
        total = len(items_to_show)
        pagine = (total + pager - 1) // pager if pager > 0 else 1
        def conteggio(viste):
            testo = f"({viste} / {total})"
            if pagine > 1:
                testo += f" - ({(viste + pager - 1) // pager} / {pagine})"
            return testo
        if total == 0:
            print(ntf if ntf else conteggio(0))
            return True
        for count, item in enumerate(items_to_show, 1):
            if is_numbered:
                print(f"{item}. {d[num_map[item]]}")
            else:
                desc = d.get(item, "")
                print(f"{item}: {desc}" if desc else f"{item}")
            if pager > 0 and count % pager == 0 and count < total:
                ch_pager = key(f"\r{conteggio(count)}\r"); print()
                if ch_pager == '\x1b': return False
        print(conteggio(total))
        return True
    def Listaprompt_autocomplete(keys_list, display_input):
        """Genera un prompt che suggerisce i prossimi caratteri validi."""
        if not keys_list or len(keys_list) <= 1: return ">"
        next_chars = []
        seen = set()
        input_len = len(display_input)
        for voce in keys_list:
            if len(voce) > input_len:
                char = voce[input_len].upper()
                if char not in seen:
                    seen.add(char)
                    next_chars.append(char)
        if not next_chars: return ">"
        return f"({', '.join(next_chars)})>"
    def valid_match(key_item, sub):
        """Controlla se 'key_item' inizia con 'sub' (case-insensitive)."""
        return key_item.lower().startswith(sub.lower())
    orig_keys = list(d.keys())
    if ordered:
        orig_keys.sort()
    user_input = ""
    last_displayed = None
    num_map = {}
    if numbered:
        num_map = {str(i): k for i, k in enumerate(orig_keys, 1)}
        orig_keys = list(num_map.keys())
    if not d: return None
    if len(d) == 1 and not show_only: return next(iter(d))
    if show_only: Mostra(orig_keys, pager, numbered, num_map); return None
    if show:
        Mostra(orig_keys, pager, numbered, num_map)
        last_displayed = orig_keys[:]
    disable_autocomplete_once = False
    # Vero quando l'ultima cosa stampata e' rimasta a meta' riga, cioe' il
    # prompt o il carattere appena digitato. Serve per andare a capo solo
    # quando c'e' davvero una riga da chiudere: prima si andava a capo sempre,
    # e dopo un elenco ne nasceva una riga vuota che NVDA legge per intero.
    a_capo_pendente = False
    while True:
        filtered = [k for k in orig_keys if valid_match(k, user_input)]
        display_input = user_input
        if keyslist and not numbered and not disable_autocomplete_once and len(filtered) > 1:
            common_prefix = lcp(filtered)
            if len(common_prefix) > len(user_input):
                user_input = common_prefix
                display_input = common_prefix
        disable_autocomplete_once = False
        final_filtered = [k for k in orig_keys if valid_match(k, display_input)]
        if len(final_filtered) == 1 and len(display_input) > 0:
            final_choice = final_filtered[0]
            print()
            return num_map.get(final_choice, final_choice)
        if show and show_on_filter and final_filtered != last_displayed:
            if a_capo_pendente: print()
            Mostra(final_filtered, pager, numbered, num_map)
            last_displayed = final_filtered[:]
            a_capo_pendente = False
        if numbered:
            prompt_str = p if p != "> " else f"(1-{len(orig_keys)})"
            if not prompt_str.strip().endswith('>'): prompt_str += '> '
        elif keyslist:
            prompt_str = Listaprompt_autocomplete(final_filtered, display_input)
        else:
            prompt_str = p
        full_prompt = ("\n" if a_capo_pendente else "") + prompt_str + display_input
        user_char = key(full_prompt)
        a_capo_pendente = True
        if user_char == '\r':
            print()
            a_capo_pendente = False
            exact_matches = [k for k in final_filtered if k.lower() == display_input.lower()]
            if exact_matches:
                return num_map.get(exact_matches[0], exact_matches[0])
            elif len(final_filtered) == 1:
                return num_map.get(final_filtered[0], final_filtered[0])
            elif user_input == "":
                return empty_enter
            else:
                # Prefisso ambiguo: nessuna parola, perche' menu non sa in che
                # lingua dirla. Azzerare l'ultimo elenco fa ripresentare i
                # candidati al giro dopo, quando show_on_filter e' vero.
                last_displayed = None
        elif user_char == '\x1b': print(); return None
        elif user_char == '?':
            print()
            Mostra(final_filtered, pager, numbered, num_map)
            last_displayed = final_filtered[:]
            a_capo_pendente = False
        elif user_char in ('\x08', 'ctrl-backspace'):
            if user_input:
                user_input = user_input[:-1]
                print('\b \b'*len(display_input), end='', flush=True)
                last_displayed = None
                disable_autocomplete_once = True
        elif len(user_char) != 1 or not user_char.isprintable():
            # Frecce, tasti funzione, combinazioni con Ctrl e Alt, Tab e la
            # stringa vuota: non sono caratteri da filtro e si lasciano cadere.
            pass
        elif numbered and not user_char.isdigit():
            pass
        else:
            print(user_char, end='', flush=True)
            user_input += user_char
            last_displayed = None
            disable_autocomplete_once = False

# L'indirizzo a cui arrivano i caffe': sta qui una volta sola, e le dieci
# traduzioni lo compongono nel messaggio.
_EMAIL_DONAZIONI = "gabriele.battaglia@gmail.com"

def Donazione(lang=None, probabilita=20, stampa=True):
    """V2.1.0 di venerdì 11 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode)
    L'invito a offrire un caffe' all'autore, nella lingua giusta fra dieci:
    italiano, inglese, portoghese, francese, spagnolo, tedesco, russo, cinese
    semplificato, giapponese e arabo.
    Parametri:
      lang: codice della lingua, per esempio it, en o it_IT. Se manca, la
        lingua si ricava nell'ordine dal file selected_language.json che
        polipo salva nella cartella di chi chiama, dalla funzione di
        traduzione installata in builtins, e dalla lingua di sistema, con
        l'inglese come ultima rete.
      probabilita: percentuale di volte in cui l'invito compare. Venti per
        predefinito, cento per farlo comparire sempre, per esempio da una voce
        di menu che lo mostra a richiesta, zero per non farlo comparire mai.
      stampa: se vero, il predefinito, il messaggio viene anche stampato, come
        faceva la funzione fino alla V2.0.1. Chi ha una finestra passa falso e
        lo mostra come vuole.
    Restituisce il messaggio quando il sorteggio passa, None altrimenti.
    Il sorteggio usa un generatore casuale privato: chiamarla non sposta il
    generatore globale del programma, e una partita riproducibile resta tale.
    Dalla V2.1.0 il messaggio torna a chi chiama invece di essere soltanto
    stampato: nella finestra di Tornello, compilata senza console, la stampa
    finiva nel nulla e l'invito non compariva mai. La lingua salvata da polipo
    si cerca nella cartella di chi chiama, non piu' in argv zero o nella
    directory di lavoro, e le eccezioni intercettate hanno un nome: un file
    che manca e' il caso normale, uno che non si legge viene saltato, tutto il
    resto risale.
    """
    import builtins
    import json
    import os
    import random
    if random.Random().randint(1, 100) > probabilita:
        return None
    email = _EMAIL_DONAZIONI
    messaggi = {
        'it': f"Se questo software ti è piaciuto, ti è stato utile, ti sei divertito ad usarlo, considera l'idea di offrirmi un caffè. Mi trovi su paypal come {email} Grazie di cuore.",
        'en': f"If you enjoyed this software, found it useful, or had fun using it, consider buying me a coffee. You can find me on PayPal at {email} Thank you.",
        'pt': f"Se você gostou deste software, o achou útil ou se divertiu usando-o, considere me pagar um café. Você pode me encontrar no PayPal em {email}. Muito obrigado.",
        'fr': f"Si vous avez aimé ce logiciel, l'avez trouvé utile ou vous êtes amusé en l'utilisant, envisagez de m'offrir un café. Vous pouvez me trouver sur PayPal à l'adresse {email} Merci beaucoup.",
        'es': f"Si te ha gustado este software, te ha resultado útil o te has divertido usándolo, considera la idea de invitarme a un café. Me puedes encontrar en PayPal como {email}. Muchas gracias.",
        'de': f"Wenn Ihnen diese Software gefallen hat, sie nützlich war oder Sie Spaß daran hatten, sie zu nutzen, ziehen Sie in Betracht, mir einen Kaffee auszugeben. Sie finden mich auf PayPal unter {email} Vielen Dank.",
        'ru': f"Если вам понравилась эта программа, она оказалась полезной или вы получили удовольствие от ее использования, рассмотрите возможность угостить меня кофе. Вы можете найти меня на PayPal по адресу {email} Спасибо.",
        'zh': f"如果您喜欢这款软件，觉得它有用，或者在使用过程中获得了乐趣，请考虑请我喝杯咖啡。您可以在PayPal上找到我：{email} 谢谢。",
        'ja': f"このソフトウェアを楽しんだり、役立つと感じたり、楽しく使っていただけたなら、私にコーヒーをご馳走することを検討してください。PayPalで{email}として見つけることができます。ありがとうございます。",
        'ar': f"إذا أعجبك هذا البرنامج، أو وجدته مفيدًا، أو استمتعت باستخدامه، ففكر في شراء قهوة لي. يمكنك العثور عليّ على PayPal على {email}. شكرًا لك.",
    }
    def codice(valore):
        """Da it_IT, it-IT o IT si arriva a it; None se non c'e' niente."""
        valore = str(valore or "").strip().lower().split('_')[0].split('-')[0]
        return valore or None
    lingua = codice(lang)
    if not lingua:
        # La scelta che l'utente ha gia' fatto con polipo, salvata accanto a
        # chi chiama. Un file che manca e' il caso normale; uno che non si
        # legge, non e' JSON o non ha la forma attesa viene saltato.
        percorso = os.path.join(_cartella_chiamante(1), 'selected_language.json')
        if os.path.exists(percorso):
            try:
                with open(percorso, 'r', encoding='utf-8') as f:
                    dati = json.load(f)
                lingua = codice(dati.get('language_code')) if isinstance(dati, dict) else None
            except (OSError, ValueError):
                lingua = None
    if not lingua:
        # La funzione di traduzione installata da gettext, se c'e': il suo
        # oggetto sa in che lingua sta traducendo.
        traduzione = getattr(getattr(builtins, '_', None), '__self__', None)
        info = getattr(traduzione, 'info', None)
        if callable(info):
            try:
                lingua = codice(info().get('language'))
            except (AttributeError, TypeError):
                lingua = None
    if not lingua:
        lingua = _lingua_di_sistema()
    messaggio = messaggi.get(lingua or 'en', messaggi['en'])
    if stampa:
        print(messaggio)
    return messaggio

def polipo(domain='messages', localedir='locales', source_language='en', config_path=None,
           interattivo=True, lingua_predefinita=None):
    """
    polipo V6.1.0 by Gabriele Battaglia and Gemini - 18/07/2025, poi ClaudIA (Claude Opus 5, modalità auto) - 4/9/2026
    Restituisce la coppia (codice della lingua, funzione di traduzione).
    Versione autonoma e compatibile con PyInstaller.
    - Trova autonomamente le risorse (es. cartella 'locales').
    - Salva il file di configurazione della lingua accanto all'eseguibile o al
      file che ha chiamato polipo, mai nella directory di lavoro corrente.
    - I percorsi relativi passati in localedir e config_path si intendono
      relativi a quella stessa cartella; i percorsi assoluti vengono usati
      cosi' come sono.
    - Propone soltanto le lingue che hanno davvero il catalogo tradotto, cioe'
      LC_MESSAGES con dentro il file del dominio richiesto: prima bastava una
      sottocartella qualsiasi, e si poteva scegliere una lingua che poi non
      traduceva niente.
    - Salva l'elenco delle lingue disponibili e mostra il menu se cambiano.
    - interattivo=False non mostra mai il menu e sceglie da solo: serve alle
      applicazioni con interfaccia grafica, che non hanno un terminale su cui
      chiedere. Anche in modalita' interattiva, se il terminale manca del
      tutto, polipo sceglie da solo invece di fallire.
    - lingua_predefinita e' la lingua da usare quando la scelta non viene
      chiesta o viene annullata; se non e' indicata o non e' disponibile, si
      usa quella di sistema, e in mancanza di quella la lingua sorgente.
    - Non richiede funzioni esterne di supporto.
    """
    import gettext
    import json
    import os
    import struct
    import sys
    # Rileva se l'app è "congelata" (compilata con PyInstaller)
    is_frozen = getattr(sys, 'frozen', False)
    # Cartella dell'eseguibile se congelato, altrimenti quella del file che ha
    # chiamato polipo. Prima si usava os.getcwd, che cambia a seconda di dove
    # il programma viene lanciato: chi passava percorsi relativi non ritrovava
    # ne' le traduzioni ne' la lingua gia' scelta.
    cartella_chiamante = _cartella_chiamante(1)
    # LOGICA 1: Trovare il percorso delle RISORSE (dati come la cartella 'locales')
    if is_frozen:
        resources_base_path = sys._MEIPASS
    else:
        resources_base_path = cartella_chiamante
    # LOGICA 2: Trovare il percorso di SALVATAGGIO (per il file.json)
    # 1. Determina il percorso di base di default: cartella dell'eseguibile se
    # congelato, altrimenti quella del file che ha chiamato polipo.
    base_save_path = cartella_chiamante
    # 2. Decide il percorso finale in base a config_path
    if config_path:
        # Controlla se il percorso fornito è assoluto
        if os.path.isabs(config_path):
            # Se è assoluto (es. "E:\git\orologic\settings"), usalo direttamente
            config_save_path = config_path
        else:
            # Se è relativo (es. "settings"), uniscilo al percorso di base
            config_save_path = os.path.join(base_save_path, config_path)
    else:
        # Se non è stato fornito nessun config_path, usa semplicemente il percorso di base
        config_save_path = base_save_path
    # Assicuriamoci che la cartella di configurazione esista, altrimenti la
    # creiamo. exist_ok evita che due istanze avviate insieme si tolgano la
    # lingua a vicenda: prima, chi arrivava secondo trovava la cartella appena
    # creata dall'altro e ripiegava sulla lingua sorgente.
    try:
        os.makedirs(config_save_path, exist_ok=True)
    except OSError as e:
        print(f"Warning: could not create the configuration directory: {e}")
        # Senza quella cartella la scelta non si puo' salvare: si prosegue
        # nella lingua sorgente invece di fermare il programma.
        return source_language, lambda text: text
    # Costruisce i percorsi completi
    localedir_abs = os.path.join(resources_base_path, localedir)
    selected_lang_file = os.path.join(config_save_path, 'selected_language.json')
    system_lang_code = _lingua_di_sistema()

    def ha_catalogo(lingua):
        """Vera solo se quella lingua ha davvero il file tradotto del dominio."""
        return os.path.isfile(os.path.join(localedir_abs, lingua, 'LC_MESSAGES', f'{domain}.mo'))

    try:
        available_translations = [d for d in os.listdir(localedir_abs)
                                  if os.path.isdir(os.path.join(localedir_abs, d)) and ha_catalogo(d)]
    except OSError:
        print(f"Warning: translations folder '{localedir_abs}' not found.")
        print(f"The application will use the source language ('{source_language}').")
        return source_language, lambda text: text
    current_choices_set = {source_language}
    # La lingua di sistema si propone solo se qualcuno l'ha davvero tradotta,
    # altrimenti si offriva una scelta che lasciava i testi come prima.
    if system_lang_code and (system_lang_code == source_language or ha_catalogo(system_lang_code)):
        current_choices_set.add(system_lang_code)
    current_choices_set.update(available_translations)
    current_available_languages = sorted(current_choices_set)
    if len(current_available_languages) < 2:
        # C'e' solo la lingua sorgente: non ha senso chiedere niente.
        return source_language, lambda text: text
    language_code = None
    show_menu = False
    # La rilettura non si fida di cio' che trova: un file troncato da un
    # arresto improvviso, o che contenga JSON valido ma non un oggetto,
    # faceva morire il programma all'avvio invece di far ricomparire il menu.
    try:
        with open(selected_lang_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, ValueError):
        # OSError copre il file che manca e quello che non si puo' leggere,
        # ValueError il JSON malformato: in tutti i casi si richiede la scelta.
        data = None
    if not isinstance(data, dict):
        show_menu = True
    else:
        language_code = data.get('language_code')
        saved_available_languages = data.get('available_languages', [])
        if not isinstance(saved_available_languages, list):
            saved_available_languages = []
        if language_code not in current_available_languages:
            show_menu = True
        elif set(saved_available_languages) != set(current_available_languages):
            # Se la lingua salvata è già valida ma la lista di lingue disponibili è cambiata,
            # aggiorna il file in modo silente senza interrompere l'utente con il menu.
            try:
                with open(selected_lang_file, 'w', encoding='utf-8') as sf:
                    config_data = {
                        'language_code': language_code,
                        'available_languages': current_available_languages
                    }
                    json.dump(config_data, sf, indent=4)
            except OSError:
                pass

    if show_menu:
        if lingua_predefinita in current_available_languages:
            default_fallback = lingua_predefinita
        elif system_lang_code in current_available_languages:
            default_fallback = system_lang_code
        else:
            default_fallback = source_language
        if not interattivo:
            # Nessun terminale su cui chiedere: si sceglie e si tira dritto.
            language_code = default_fallback
        else:
            print("Select your language:")
            menu_options = {}
            for i, lang in enumerate(current_available_languages, 1):
                label = lang
                details = []
                if lang == source_language: details.append("Source")
                if lang == system_lang_code: details.append("System")
                if details: label += f" ({', '.join(details)})"
                print(f"{i}. {label}")
                menu_options[str(i)] = lang
            while True:
                try:
                    choice = input(f"Enter selection (1-{len(menu_options)}): ")
                    if choice in menu_options:
                        language_code = menu_options[choice]
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except (EOFError, KeyboardInterrupt, RuntimeError):
                    # RuntimeError e' quello che Python solleva quando lo
                    # standard input non esiste, cioe' in un eseguibile
                    # compilato senza console: prima non era intercettato e il
                    # programma moriva li', senza finestra e senza messaggio.
                    language_code = default_fallback
                    break

        try:
            with open(selected_lang_file, 'w', encoding='utf-8') as f:
                # Salva sia la lingua scelta sia l'elenco corrente delle lingue
                config_data = {
                    'language_code': language_code,
                    'available_languages': current_available_languages
                }
                json.dump(config_data, f, indent=4)
            if interattivo:
                print(f"Language set to '{language_code}'.")
        except OSError as e:
            print(f"Warning: could not save the selected language: {e}")
    if language_code == source_language:
        return source_language, lambda text: text
    else:
        # fallback=True copre il catalogo mancante, che qui non puo' comunque
        # accadere perche' si propongono solo le lingue che il catalogo ce
        # l'hanno. Non copre pero' il catalogo illeggibile o troncato, per
        # esempio da un aggiornamento interrotto: gettext solleva OSError se
        # il file non ha il numero magico giusto e struct.error se e' troppo
        # corto perche' lo si possa leggere. Senza questa rete il programma
        # non partirebbe affatto.
        try:
            translation = gettext.translation(
                domain,
                localedir=localedir_abs,
                languages=[language_code],
                fallback=True
            )
        except (OSError, struct.error) as e:
            print(f"Warning: the '{language_code}' catalogue could not be read: {e}")
            return source_language, lambda text: text
        return language_code, translation.gettext
