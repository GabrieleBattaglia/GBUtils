'''
	GBUtils di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5)
	Data concepimento: lunedì 3 febbraio 2020.
	Raccoglitore di utilità per i miei programmi.
	Spostamento su github in data 27/6/2024. Da usare come submodule per gli altri progetti.
	V101 di giovedì 3 settembre 2026
Lista utilità contenute in questo pacchetto
	Acu_Maker V1.4.0 di giovedì 3 settembre 2026. Utilità CLI per preset Acusticator, rumore compreso
	Acusticator V7.2.4 di giovedì 3 settembre 2026. Oggetto chiamabile, collezione dei suoni, mixer a 16 voci e rumore a quattro colori. Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Sonnet 5, modalità auto)
	base62 3.0 di martedì 15 novembre 2022
	CWzator V9.1 di sabato 30 maggio 2026 - Gabriele Battaglia (IZ4APU) e Stella/Gemini 3.5 Flash
	crea_archivio_release V1.0 di mercoledì 2 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5)
	dgt Versione 1.10 di lunedì 24 febbraio 2025
	Donazione V2.0 del 12 luglio 2026
	enter_escape V1.0 del 6 ottobre 2025 by Gabriele Battaglia & Gemini 2.5 Pro
	gridapu 1.2 from IU1FIG
	key V6.1.1 di lunedì 1 giugno 2026 by Gabriele Battaglia and Stella/Gemini 3.5 Flash.
	manuale 1.0.1 di domenica 5 maggio 2024
	mazzo V5.2 - settembre 2025 b Gabriele Battaglia & Gemini 2.5
	menu V4.6.4 - sabato 27 giugno 2026 - Stella Gemini 3.5 Flash & Gabriele Battaglia
	polipo V6.0 by Gabriele Battaglia and Gemini - 18/07/2025
	sonify V7.3 - 11 aprile 2026 - Gabriele Battaglia, Stella & Gemini 3 Pro
	update_checker V1.4.1 di giovedì 3 settembre 2026 by Gabriele Battaglia & ClaudIA (Claude Sonnet 5, modalità auto)
	perform_update V1.4 di giovedì 16 luglio 2026 by Gabriele Battaglia & Stella
'''
VERSION = "101"
def _parse_version(version_str: str) -> tuple:
    """Helper interno per il parsing semantico della versione."""
    import re
    # Estrae solo i numeri separati da punti, ignorando prefissi come 'v'
    match = re.search(r'(\d+(?:\.\d+)*)', version_str)
    if not match:
        return (0,)
    return tuple(map(int, match.group(1).split('.')))

def _write_update_log(message: str):
    """Scrive un messaggio di errore e il traceback in un file di log locale."""
    import os
    import sys
    import traceback
    from datetime import datetime
    
    try:
        # Determina la cartella dell'eseguibile o dello script
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(locals().get('__sys_module_file__', __file__)))
            # Se siamo in un pacchetto/submodule, meglio usare la cartella di lavoro corrente per i log
            base_dir = os.getcwd()

        log_path = os.path.join(base_dir, "auto_updater_error.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"DATA: {timestamp}\n")
            f.write(f"ERRORE: {message}\n")
            f.write(f"TRACEBACK:\n{traceback.format_exc()}\n")
            f.write(f"{'='*50}\n")
    except Exception as e:
        print(f"Impossibile scrivere il file di log: {e}")

def update_checker(current_version: str, api_url: str) -> tuple[bool, str | None, str | None, str | None]:
    """
    V1.4.1 di giovedì 3 settembre 2026 by Gabriele Battaglia & ClaudIA (Claude Sonnet 5, modalità auto)
    Controlla l'ultima release di un repository GitHub e la confronta con la versione corrente.
    Include logging degli errori su file e retry in caso di errori SSL.
    Gestisce in modo silenzioso la mancanza di connessione internet senza generare file di log allarmanti.
    """
    try:
        # Fuori da questo try, un import rotto (es. una dipendenza di
        # requests compilata male) farebbe cadere tutto il programma a
        # ogni avvio invece di limitarsi a saltare il controllo aggiornamenti.
        import requests
    except ImportError as e:
        _write_update_log(f"Impossibile importare requests: {e}")
        return False, None, None, None
    current_version = current_version.split(' ')[0]
    try:
        try:
            response = requests.get(api_url, timeout=10)
        except requests.exceptions.SSLError:
            _write_update_log("Errore SSL con requests. Ritento disabilitando la verifica SSL (verify=False).")
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(api_url, timeout=10, verify=False)
            
        response.raise_for_status()
        data = response.json()
        latest_version = data.get("tag_name")
        if not latest_version:
            _write_update_log("Nessun tag_name trovato nella risposta JSON di GitHub.")
            return False, None, None, None
        
        changelog = data.get("body")
        
        current_tuple = _parse_version(current_version)
        latest_tuple = _parse_version(latest_version)
        
        update_available = latest_tuple > current_tuple
        if update_available:
            download_url = None
            assets = data.get("assets")
            if assets:
                download_url = assets[0].get("browser_download_url")
            return True, latest_version, download_url, changelog
        else:
            return False, latest_version, None, None
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Assenza di rete / DNS fallito: evento di rete fisiologico, non scriviamo il traceback nel file di log.
        return False, None, None, None
    except Exception as e:
        _write_update_log(f"Errore durante il controllo aggiornamenti: {e}")
        return False, None, None, None

def perform_update(download_url: str, app_name: str = "App") -> bool:
    """
    V1.4 di giovedì 16 luglio 2026 by Gabriele Battaglia & Stella
    Scarica l'aggiornamento, lo estrae ed esegue uno script batch.
    Risolve conflitti cartelle temp e script batch bloccati.
    """
    import os
    import subprocess
    import sys
    import tempfile
    import urllib.request
    import zipfile
    
    if not sys.platform.startswith('win'):
        return False
        
    try:
        # 1. Determina l'eseguibile corrente
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable
        else:
            _write_update_log("Impossibile aggiornare: in esecuzione da sorgente (sys.frozen=False).")
            return False
            
        current_dir = os.path.dirname(current_exe)
        exe_name = os.path.basename(current_exe)
        sys_temp = tempfile.gettempdir()
        
        # 2. Crea cartelle e path temporanei esterni alla dir di destinazione
        temp_dir = os.path.join(current_dir, "_update_temp_dir")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        zip_path = os.path.join(sys_temp, f"update_{app_name}.zip")
        bat_path = os.path.join(sys_temp, f"updater_{app_name}.bat")
        
        # 3. Download
        try:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
            
        urllib.request.urlretrieve(download_url, zip_path)
        
        # 4. Estrazione
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        # 5. Genera script batch
        # Troviamo la cartella che contiene l'eseguibile appena estratto
        source_dir = temp_dir
        exe_name_lower = exe_name.lower()
        for root, dirs, files in os.walk(temp_dir):
            if any(f.lower() == exe_name_lower for f in files):
                source_dir = root
                break
                
        # Lo script batch è fuori dalla current_dir e dalla temp_dir (è in sys_temp)
        # Si auto-eliminerà alla fine
        bat_content = f"""@echo off
title Aggiornamento {app_name}...
echo Attendo la chiusura di {app_name}...
timeout /t 3 /nobreak > nul

echo Applicazione aggiornamento...
xcopy "{source_dir}\\*" "{current_dir}\\" /S /Y /E /Q

echo Riavvio {app_name}...
start "" /D "{current_dir}" "{current_exe}"

echo Pulizia file temporanei...
rmdir /S /Q "{temp_dir}"
del /Q "{zip_path}"
(goto) 2>nul & del "%~f0"
"""
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
            
        # 6. Avvia lo script batch
        CREATE_NEW_CONSOLE = 0x00000010
        subprocess.Popen([bat_path], creationflags=CREATE_NEW_CONSOLE)
        
        return True
        
    except Exception as e:
        _write_update_log(f"Errore durante l'esecuzione dell'aggiornamento: {e}")
        return False


def crea_archivio_release(nome_app, cartella_dist=None, archivio=None, escludi=None, silenzioso=False):
    """V1.0 di mercoledì 2 settembre 2026 by Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5)
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
    Le cartelle dei dati dell'utente, cioe' log, settings, pgn, txt e images, si
    saltano dovunque si trovino, perche' nascono provando l'eseguibile prima di
    comprimere e conterrebbero i dati di chi ha compilato.
    Il filtro sulle estensioni vale invece soltanto per i file accanto
    all'eseguibile, mai dentro _internal, dove sta quello che ha messo
    PyInstaller: li' un base_library.zip o un membrane.dat servono davvero e
    senza di loro il pacchetto non parte nemmeno.
    Restituisce la coppia (quanti, lasciati), cioe' il numero di file scritti
    nell'archivio e l'elenco ordinato di quelli lasciati fuori.
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
    radice_assoluta = os.path.abspath(cartella_dist)
    try:
        with zipfile.ZipFile(archivio, "w", zipfile.ZIP_DEFLATED) as zip_out:
            for radice, cartelle, file in os.walk(cartella_dist):
                dentro = os.path.relpath(radice, cartella_dist)
                for c in cartelle:
                    if c.lower() in salta_sempre:
                        ramo = c if dentro == "." else os.path.join(dentro, c)
                        lasciati.append(f"{ramo} e quel che contiene")
                cartelle[:] = [c for c in cartelle if c.lower() not in salta_sempre]
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
                    zip_out.write(percorso, os.path.relpath(percorso, cartella_dist))
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
        if lasciati:
            print(f"Lasciati fuori {len(lasciati)} elementi:")
            for voce in lasciati:
                print(f"  {voce}")
    return quanti, lasciati


def enter_escape(prompt=""):
    """
				V1.0 del 6 ottobre 2025 by Gabriele Battaglia & Gemini 2.5 Pro
    Funzione cross-platform e auto-contenuta che attende la pressione di Invio o Esc.
    Stampa un prompt opzionale e non richiede ulteriori pressioni di Invio.
    Restituisce:
        - True se viene premuto Invio.
        - False se viene premuto Esc.
    """
    # Le importazioni e le definizioni sono interne per la massima portabilità
    import sys

    try:
        # --- Implementazione per Windows ---
        import msvcrt
        def _get_key_press():
            return msvcrt.getch()

    except ImportError:
        # --- Implementazione per Unix-like (macOS, Linux) ---
        import termios
        import tty
        def _get_key_press():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(sys.stdin.fileno())
                char = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return char.encode('utf-8')

    # Logica principale della funzione
    if prompt:
        print(prompt, end="", flush=True)
    
    while True:
        k = _get_key_press()
        # Invio può essere \r (Windows) o \n (Unix)
        if k in (b'\r', b'\n'):
            print() # Pulisce la riga andando a capo
            return True
        # Esc è sempre \x1b
        elif k == b'\x1b':
            print() # Pulisce la riga andando a capo
            return False
def CWzator(msg, wpm=35, pitch=550, l=30, s=50, p=50, fs=44100, ms=1, vol=0.5, wv=1, sync=False, to_file=False, wave_output_path_file=None, get_map=False):
	"""
	CWzator V9.1 di sabato 30 maggio 2026 - Gabriele Battaglia (IZ4APU) e Stella/Gemini 3.5 Flash
		da un'idea originale di Kevin Schmidt W9CF
	Genera e riproduce l'audio del codice Morse dal messaggio di testo fornito.
	Parameters:
		msg (str|int): Messaggio di testo da convertire in Morse.
			se == -1 restituisce la mappa morse come dizionario (deprecato, usare get_map=True).
		wpm (int): Velocità in parole al minuto (range 5-100).
		pitch (int): Frequenza in Hz per il tono (range 130-2800).
		l (int): Peso per la durata della linea (default 30).
		s (int): Peso per la durata degli spazi tra simboli/lettere (default 50).
		p (int): Peso per la durata del punto (default 50).
		fs (int): Frequenza di campionamento (default 44100 Hz).
		ms (int): Durata in millisecondi per i fade-in/out sui toni (default 1).
		vol (float): Volume (range 0.0 a 1.0, default 0.5).
		wv (int): Tipo d'onda (scipy.signal): 1=Sine(default), 2=Square, 3=Triangle, 4=Sawtooth (dente di sega discendente classica).
		sync (bool): Se True, la funzione aspetta la fine della riproduzione; altrimenti ritorna subito.
		to_file (bool): Se True, salva l'audio in un file WAV.
		wave_output_path_file (str|None): Percorso e/o nome file per il salvataggio WAV.
			Può contenere solo il percorso (directory), solo il nome file, o entrambi.
			Se None (default), salva nella directory corrente con nome autogenerato.
			Dove i dati sono presenti, hanno priorità sul comportamento di default.
		get_map (bool): Se True, restituisce immediatamente il dizionario MORSE_MAP senza generare audio.
	Returns:
		dict: Se get_map=True o msg==-1, restituisce il dizionario della mappa Morse.
		tuple[PlaybackHandle, float]: Un oggetto PlaybackHandle e rwpm (velocità effettiva wpm).
		tuple[None, None]: In caso di errore di validazione parametri.
	"""
	import os
	import sys
	import threading
	import wave
	from datetime import datetime

	import numpy as np
	import sounddevice as sd
	from scipy import signal as scipy_signal
	BLOCK_SIZE = 256
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
	if get_map or msg == -1:
		return MORSE_MAP
	# --- Validazione parametri (DRY) ---
	if not isinstance(msg, str) or msg == "":
		print("CWzator Error: msg deve essere una stringa non vuota.", file=sys.stderr)
		return None, None
	validations = [
		("wpm", wpm, (int,), 5, 100),
		("pitch", pitch, (int,), 130, 2800),
		("l", l, (int,), 1, 100),
		("s", s, (int,), 1, 100),
		("p", p, (int,), 1, 100),
		("fs", fs, (int,), 1, None),
		("ms", ms, (int, float), 0, None),
		("vol", vol, (int, float), 0.0, 1.0),
	]
	for name, val, types, lo, hi in validations:
		if not isinstance(val, types):
			print(f"CWzator Error: {name} ({val}) tipo non valido.", file=sys.stderr)
			return None, None
		if lo is not None and val < lo:
			print(f"CWzator Error: {name} ({val}) sotto il minimo [{lo}].", file=sys.stderr)
			return None, None
		if hi is not None and val > hi:
			print(f"CWzator Error: {name} ({val}) sopra il massimo [{hi}].", file=sys.stderr)
			return None, None
	if not (isinstance(wv, int) and wv in (1, 2, 3, 4)):
		print(f"CWzator Error: wv ({wv}) non valido [1-4].", file=sys.stderr)
		return None, None
	# --- Calcolo Durate ---
	T = 1.2 / float(wpm)
	dot_duration = T * (p / 50.0)
	dash_duration = 3.0 * T * (l / 30.0)
	intra_gap = T * (s / 50.0)
	letter_gap = 3.0 * T * (s / 50.0)
	word_gap = 7.0 * T * (s / 50.0)
	# --- Pre-generazione dei 5 segmenti base ---
	def _generate_tone(duration):
		N = int(round(fs * duration))
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
		fade_samples = int(round(fs * ms / 1000.0))
		if fade_samples > 0 and fade_samples <= N // 2:
			ramp = np.linspace(0, 1, fade_samples, dtype=np.float32)
			signal_float[:fade_samples] *= ramp
			signal_float[-fade_samples:] *= ramp[::-1]
		signal_float = np.clip(signal_float * vol, -1.0, 1.0)
		return (signal_float * 32767.0).astype(np.int16)
	def _generate_silence(duration):
		N = int(round(fs * duration))
		return np.zeros(N, dtype=np.int16) if N > 0 else np.array([], dtype=np.int16)
	seg_dot = _generate_tone(dot_duration)
	seg_dash = _generate_tone(dash_duration)
	seg_intra = _generate_silence(intra_gap)
	seg_letter = _generate_silence(letter_gap)
	seg_word = _generate_silence(word_gap)
	# --- Primo passaggio: pianifica i segmenti e calcola la lunghezza totale ---
	words_list = msg.lower().split()
	plan = []
	total_samples = 0
	valid_char_count = 0
	for w_idx, word in enumerate(words_list):
		valid_letters = "".join(ch for ch in word if ch in MORSE_MAP)
		for l_idx, letter in enumerate(valid_letters):
			code = MORSE_MAP.get(letter)
			if not code:
				continue
			valid_char_count += 1
			for s_idx, symbol in enumerate(code):
				if symbol == '.':
					plan.append(seg_dot)
					total_samples += seg_dot.size
				elif symbol == '-':
					plan.append(seg_dash)
					total_samples += seg_dash.size
				if s_idx < len(code) - 1:
					plan.append(seg_intra)
					total_samples += seg_intra.size
			if l_idx < len(valid_letters) - 1:
				plan.append(seg_letter)
				total_samples += seg_letter.size
		if w_idx < len(words_list) - 1:
			if valid_letters or any(ch in MORSE_MAP for ch in words_list[w_idx + 1]):
				plan.append(seg_word)
				total_samples += seg_word.size
	# --- Silenzio finale (5ms) ---
	silence_samples_end = int(round(fs * 0.005))
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
	# --- Calcolo rwpm (soglia: ≤3 caratteri → wpm nominale) ---
	rwpm = wpm
	if (l, s, p) != (30, 50, 50) and valid_char_count > 3:
		dots = dashes = intra_gaps = letter_gaps_count = word_gaps_count = 0
		for w_idx, w in enumerate(words_list):
			current_word_letters = 0
			for letter in w:
				if letter in MORSE_MAP:
					code = MORSE_MAP[letter]
					if code:
						dots += code.count('.')
						dashes += code.count('-')
						code_len = len(code)
						if code_len > 1:
							intra_gaps += (code_len - 1)
						current_word_letters += 1
			if current_word_letters > 1:
				letter_gaps_count += (current_word_letters - 1)
			if current_word_letters > 0 and w_idx < len(words_list) - 1:
				if any(ch in MORSE_MAP and MORSE_MAP[ch] for ch in words_list[w_idx + 1]):
					word_gaps_count += 1
		standard_total_units = dots + 3 * dashes + intra_gaps + 3 * letter_gaps_count + 7 * word_gaps_count
		actual_dot_units = p / 50.0
		actual_dash_units = 3.0 * (l / 30.0)
		actual_intra_gap_units = s / 50.0
		actual_letter_gap_units = 3.0 * (s / 50.0)
		actual_word_gap_units = 7.0 * (s / 50.0)
		actual_total_units = (dots * actual_dot_units) + \
							 (dashes * actual_dash_units) + \
							 (intra_gaps * actual_intra_gap_units) + \
							 (letter_gaps_count * actual_letter_gap_units) + \
							 (word_gaps_count * actual_word_gap_units)
		if standard_total_units > 0 and actual_total_units > 0:
			ratio = actual_total_units / standard_total_units
			rwpm = wpm / ratio
		elif standard_total_units == 0 and actual_total_units == 0:
			rwpm = wpm
		else:
			rwpm = wpm
			print("CWzator Warning: Calcolo rwpm anomalo, possibile input solo con spazi?", file=sys.stderr)
	# --- Classe PlaybackHandle con caching ---
	if not hasattr(CWzator, '_PlaybackHandle'):
		class _PlaybackHandle:
			def __init__(self, audio_data, sample_rate, block_size):
				self.audio_data = audio_data
				self.sample_rate = sample_rate
				self._block_size = block_size
				self.stream = None
				self.is_playing = threading.Event()
				self._thread = None
				self._lock = threading.Lock()
			def _playback_target(self):
				"""Target function per il thread di riproduzione."""
				self.is_playing.set()
				try:
					with sd.OutputStream(
						samplerate=self.sample_rate, channels=1, dtype=np.int16,
						blocksize=self._block_size, latency='low'
					) as stream:
						with self._lock:
							self.stream = stream
						for i in range(0, len(self.audio_data), self._block_size):
							if not self.is_playing.is_set():
								try:
									stream.stop()
								except Exception:
									pass
								break
							block = self.audio_data[i:min(i + self._block_size, len(self.audio_data))]
							stream.write(block)
						if self.is_playing.is_set():
							pass
				except sd.PortAudioError as pae:
					print(f"CWzator Playback PortAudioError: {pae}", file=sys.stderr)
				except Exception as e:
					print(f"CWzator Playback Error: {e}", file=sys.stderr)
				finally:
					self.is_playing.clear()
					with self._lock:
						self.stream = None
			def play(self):
				"""Avvia la riproduzione in un thread separato."""
				with self._lock:
					if not self.is_playing.is_set() and self.audio_data.size > 0:
						self._thread = threading.Thread(target=self._playback_target)
						self._thread.daemon = True
						self._thread.start()
			def wait_done(self):
				"""Attende la fine della riproduzione corrente."""
				if self._thread is not None and self._thread.is_alive():
					self._thread.join()
			def stop(self):
				"""Richiede l'interruzione della riproduzione."""
				self.is_playing.clear()
			def __del__(self):
				"""Cleanup automatico: ferma la riproduzione se l'oggetto viene distrutto."""
				try:
					self.is_playing.clear()
				except Exception:
					pass
		CWzator._PlaybackHandle = _PlaybackHandle
	# --- Creazione Oggetto e Avvio Playback ---
	PlaybackHandle = CWzator._PlaybackHandle
	play_obj = PlaybackHandle(audio, fs, BLOCK_SIZE)
	CWzator._last_play_obj = play_obj
	play_obj.play()
	# --- Salvataggio File ---
	if to_file:
		default_name = f"cwapu Morse recorded at {datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
		if wave_output_path_file is not None:
			given = wave_output_path_file.strip()
			given_dir = os.path.dirname(given)
			given_file = os.path.basename(given)
			if given_dir and given_file:
				filename = given
			elif given_dir and not given_file:
				filename = os.path.join(given_dir, default_name)
			elif not given_dir and given_file:
				filename = given_file
			else:
				filename = default_name
		else:
			filename = default_name
		try:
			target_dir = os.path.dirname(filename)
			if target_dir and not os.path.exists(target_dir):
				os.makedirs(target_dir, exist_ok=True)
			with wave.open(filename, 'wb') as wf:
				wf.setnchannels(1)
				wf.setsampwidth(2)
				wf.setframerate(fs)
				wf.writeframes(audio.tobytes())
		except Exception as e:
			print(f"CWzator Error durante salvataggio file: {e}", file=sys.stderr)
	# --- Gestione Sync ---
	if sync:
		play_obj.wait_done()
	return play_obj, rwpm

class Mazzo:
	'''
	V5.2 - settembre 2025 b Gabriele Battaglia & Gemini 2.5
	Classe autocontenuta che rappresenta un mazzo di carte italiano o francese,
	con supporto per mazzi multipli, mescolamento, pesca con rimescolamento
	automatico degli scarti, e gestione flessibile delle carte.
	Non produce output diretto (print), ma restituisce valori o stringhe informative.
	'''
	import random
	from collections import namedtuple
	Carta = namedtuple("Carta", ["id", "nome", "valore", "seme_nome", "seme_id", "desc_breve"])
	_SEMI_FRANCESI = ["Cuori", "Quadri", "Fiori", "Picche"]
	_SEMI_ITALIANI = ["Bastoni", "Spade", "Coppe", "Denari"]
	_VALORI_FRANCESI = [("Asso", 1)] + [(str(i), i) for i in range(2, 11)] + [("Jack", 11), ("Regina", 12), ("Re", 13)]
	_VALORI_ITALIANI = [("Asso", 1)] + [(str(i), i) for i in range(2, 8)] + [("Fante", 8), ("Cavallo", 9), ("Re", 10)]
	_VALORI_DESCRIZIONE = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 11: 'J', 12: 'Q', 13: 'K'}
	_SEMI_DESCRIZIONE = {"Cuori": 'C', "Quadri": 'Q', "Fiori": 'F', "Picche": 'P',
																						"Bastoni": 'B', "Spade": 'S', "Coppe": 'O', "Denari": 'D'} # 'O' per Coppe
	def __init__(self, tipo_francese=True, num_mazzi=1):
		'''
		Inizializza uno o più mazzi di carte.
		Parametri:
		- tipo_francese (bool): True per mazzo francese (default), False per mazzo italiano.
		- num_mazzi (int): Numero di mazzi da includere (default 1). Deve essere >= 1.
		'''
		if not isinstance(num_mazzi, int) or num_mazzi < 1:
			raise ValueError("Il numero di mazzi deve essere un intero maggiore o uguale a 1.")
		self.tipo_francese = tipo_francese
		self.num_mazzi = num_mazzi
		# Liste per tracciare lo stato delle carte
		self.carte = [] # Mazzo principale da cui pescare
		self.scarti = [] # Pila degli scarti, possono essere rimescolati
		self.scarti_permanenti = [] # Carte rimosse permanentemente
		self._costruisci_mazzo()
	def _costruisci_mazzo(self):
		'''
		(Metodo privato) Costruisce il mazzo di carte in base al tipo e al numero di mazzi.
		'''
		self.carte = [] # Resetta il mazzo
		semi = self._SEMI_FRANCESI if self.tipo_francese else self._SEMI_ITALIANI
		valori = self._VALORI_FRANCESI if self.tipo_francese else self._VALORI_ITALIANI
		id_carta_counter = 1
		for _ in range(self.num_mazzi):
			for id_seme, nome_seme in enumerate(semi, 1):
				# Correzione: L'ID seme per mazzi italiani dovrebbe partire da 5 per distinguerli?
				# No, l'ID seme è relativo al tipo di mazzo (1-4 per entrambi),
				# il nome_seme è ciò che li distingue. Manteniamo 1-4.
				seme_id_effettivo = id_seme
				if not self.tipo_francese:
					# Se si volesse un ID globale unico (1-4 Francese, 5-8 Italiano)
					# seme_id_effettivo = id_seme + 4 # Questa è un'opzione di design, ma la lasciamo 1-4 per ora
					pass # Manteniamo 1-4 come da codice originale
				for nome_valore, valore_num in valori:
					desc_val = self._VALORI_DESCRIZIONE.get(valore_num, '?')
					desc_seme = self._SEMI_DESCRIZIONE.get(nome_seme, '?')
					desc_breve = f"{desc_val}{desc_seme}"
					nome_completo = f"{nome_valore} di {nome_seme}"
					# Usiamo la definizione di Carta interna alla classe
					carta = self.Carta(id=id_carta_counter,
																								nome=nome_completo,
																								valore=valore_num,
																								seme_nome=nome_seme,
																								seme_id=seme_id_effettivo,
																								desc_breve=desc_breve)
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
		rimescola automaticamente gli scarti prima di pescare.
		Le carte pescate vengono spostate nella lista 'pescate'.
		Parametri:
		- quante (int): Numero di carte da pescare (default 1).
		Ritorna:
		- list[Carta]: Lista delle carte pescate. Può contenere meno carte di 'quante'
									 se il mazzo e gli scarti combinati non sono sufficienti.
		'''
		if quante < 0:
			raise ValueError("Il numero di carte da pescare deve essere non negativo.")
		if quante == 0:
			return []
		# NUOVA LOGICA: Se le carte nel mazzo sono meno di quelle richieste, rimescola gli scarti.
		if len(self.carte) < quante and self.scarti:
			print("\n--- Carte insufficienti nel mazzo. Rimescolo gli scarti... ---") # Feedback utile per il giocatore
			self.carte.extend(self.scarti)
			self.scarti = []
			self.mescola_mazzo()
			print(f"--- Rimescolamento completato. Carte nel mazzo: {len(self.carte)} ---")
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
	def rimescola_scarti(self, include_pescate=False):
		'''
		Rimette le carte dalla pila degli scarti nel mazzo principale e mescola.
		Opzionalmente, può includere anche le carte attualmente pescate.
		Non reintegra le carte scartate permanentemente.
		Parametri:
		- include_pescate (bool): Se True, anche le carte in self.pescate sono rimesse (default False).
		Ritorna:
		- str: Messaggio che riepiloga l'operazione.
		'''
		carte_da_reintegrare = []
		msg_parts = []
		num_scarti = len(self.scarti)
		if num_scarti > 0:
			carte_da_reintegrare.extend(self.scarti)
			self.scarti = []
			msg_parts.append(f"{num_scarti} scarti reintegrati.")
		else:
			msg_parts.append("Nessuno scarto da reintegrare.")
		num_pescate = len(self.pescate)
		if include_pescate:
			if num_pescate > 0:
				carte_da_reintegrare.extend(self.pescate)
				self.pescate = []
				msg_parts.append(f"{num_pescate} carte pescate reintegrate.")
			else:
				msg_parts.append("Nessuna carta pescata da reintegrare.")
		if not carte_da_reintegrare:
			return "Nessuna carta da rimescolare. " + " ".join(msg_parts)
		self.carte.extend(carte_da_reintegrare)
		self.mescola_mazzo()
		msg_parts.append(f"Mazzo ora contiene {len(self.carte)} carte.")
		return " ".join(msg_parts)
	def _rimuovi_carte_da_lista(self, lista_sorgente, condizione, destinazione, nome_destinazione):
		''' Funzione helper per rimuovere carte da una lista in base a una condizione. '''
		carte_da_mantenere = []
		carte_rimosse = []
		for carta in lista_sorgente:
			if condizione(carta):
				carte_rimosse.append(carta)
			else:
				carte_da_mantenere.append(carta)
		if carte_rimosse:
			destinazione.extend(carte_rimosse)
			# Modifica la lista originale inplace
			lista_sorgente[:] = carte_da_mantenere
		return carte_rimosse
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
		nome_dest = "permanenti" if permanente else "temporanei"
		def condizione(carta):
			return carta.seme_id in semi_id_da_rimuovere
		carte_rimosse = self._rimuovi_carte_da_lista(self.carte, condizione, destinazione, nome_dest)
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
		nome_dest = "permanenti" if permanente else "temporanei"
		def condizione(carta):
			return carta.valore in valori_da_rimuovere
		carte_rimosse = self._rimuovi_carte_da_lista(self.carte, condizione, destinazione, nome_dest)
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
		all_cards = self.carte + self.pescate + self.scarti + self.scarti_permanenti
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
		Rimuove tutti i jolly dalle pile modificabili (mazzo, pescate, e scarti se permanente=True)
		e li sposta nella destinazione appropriata (scarti temporanei o permanenti).
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
			carte_rimosse = self._rimuovi_carte_da_lista(lista_sorgente, condizione, destinazione, tipo_destinazione)
			jolly_rimossi_total_obj.extend(carte_rimosse)
		# Rimuove da self.carte
		_processa_lista(self.carte)
		# Rimuove da self.pescate
		_processa_lista(self.pescate)
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
	def _rimuovi_carte_da_lista(self, lista_sorgente, condizione, destinazione, nome_destinazione):
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
		''' Ritorna una stringa che riepiloga lo stato attuale del mazzo. '''
		return (f"Mazzo: {len(self.carte)} carte | "
				f"Scarti: {len(self.scarti)} carte | "
				f"Scarti Permanenti: {len(self.scarti_permanenti)} carte")
	def __len__(self):
		''' Ritorna il numero di carte attualmente nel mazzo principale (self.carte). '''
		return len(self.carte)
	def __str__(self):
		''' Rappresentazione stringa dell'oggetto Mazzo (mostra lo stato). '''
		return self.stato_mazzo()
	def mostra_carte(self, lista='mazzo'):
		'''
		Restituisce una stringa con le descrizioni brevi delle carte
		in una specifica lista (mazzo, pescate, scarti, permanenti).
		Parametri:
		- lista (str): Nome della lista ('mazzo', 'pescate', 'scarti', 'permanenti').
		Ritorna:
		- str: Stringa formattata con le carte o messaggio di lista vuota/non valida.
		'''
		target_lista_ref = None
		nome_lista = ""
		if lista == 'mazzo':
			target_lista_ref = self.carte
			nome_lista = "Mazzo Principale"
		elif lista == 'pescate':
			target_lista_ref = self.pescate
			nome_lista = "Carte Pescate"
		elif lista == 'scarti':
			target_lista_ref = self.scarti
			nome_lista = "Pila Scarti"
		elif lista == 'permanenti':
			target_lista_ref = self.scarti_permanenti
			nome_lista = "Scarti Permanenti"
		else:
			return "Lista non valida. Scegli tra: 'mazzo', 'pescate', 'scarti', 'permanenti'."
		if not target_lista_ref:
			return f"Nessuna carta nella lista '{nome_lista}'."
		# Usa la lista referenziata per ottenere le carte
		return f"{nome_lista} ({len(target_lista_ref)}): " + ", ".join([c.desc_breve for c in target_lista_ref])

def base62(n):
	'''
	Converte un intero in base 10 ad una stringa in base 62.
	Original author: Federico Figus
	Modified by Daniele Zambelli 15/11/2022
	Version 3.0, 15/11/2022
	'''
	symbols='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	if n != int(n):
		return f"{n} is not integer!"
	segno = ''
	if n < 0:
		segno = '-'
		n = -n
	elif n == 0:
		return '0'
	out = []
	while n:
		n, r = divmod(n, len(symbols))
		out.append(r)
	out.reverse()
	return segno + ''.join(symbols[l] for l in out)

def key(prompt="", attesa=99999):
	"""V6.1.1 di lunedì 1 giugno 2026 by Gabriele Battaglia and Stella/Gemini 3.5 Flash.
	Advanced key reader with special keys, numpad (NumLock OFF) and modifiers support.
	Returns logical names for special keys (e.g., 'up', 'ctrl-a', 'pad-up', 'f1').
	Retains original 'key' functionality with timeout and prompt.
	"""
	import os
	import sys
	import time

	if prompt:
		print(prompt, end="", flush=True)

	start_time = time.time()

	if os.name == 'nt':
		import msvcrt
		
		# Mappature per codici speciali su Windows (prefisso \x00 - spesso Tastierino Numerico o F1-F10)
		special_mapping_00 = {
			'H': 'pad-up', 'P': 'pad-down', 'K': 'pad-left', 'M': 'pad-right',
			'G': 'pad-home', 'O': 'pad-end', 'I': 'pad-pageup', 'Q': 'pad-pagedown',
			'R': 'pad-insert', 'S': 'pad-delete', 'L': 'pad-center', # Tasto 5 del numpad
			
			# Tasti funzione standard
			';': 'f1', '<': 'f2', '=': 'f3', '>': 'f4',
			'?': 'f5', '@': 'f6', 'A': 'f7', 'B': 'f8',
			'C': 'f9', 'D': 'f10',
			
			# F-Keys con modificatori (spesso restituiscono \x00)
			# Shift+F1..F10 (84..93)
			'T': 'shift-f1', 'U': 'shift-f2', 'V': 'shift-f3', 'W': 'shift-f4',
			'X': 'shift-f5', 'Y': 'shift-f6', 'Z': 'shift-f7', '[': 'shift-f8',
			'\\': 'shift-f9', ']': 'shift-f10',
			# Ctrl+F1..F10 (94..103)
			'^': 'ctrl-f1', '_': 'ctrl-f2', '`': 'ctrl-f3', 'a': 'ctrl-f4',
			'b': 'ctrl-f5', 'c': 'ctrl-f6', 'd': 'ctrl-f7', 'e': 'ctrl-f8',
			'f': 'ctrl-f9', 'g': 'ctrl-f10',
			# Alt+F1..F10 (104..113)
			'h': 'alt-f1', 'i': 'alt-f2', 'j': 'alt-f3', 'k': 'alt-f4',
			'l': 'alt-f5', 'm': 'alt-f6', 'n': 'alt-f7', 'o': 'alt-f8',
			'p': 'alt-f9', 'q': 'alt-f10',
			
			# Modificatori Numpad (Ctrl)
			'w': 'ctrl-pad-home', 'u': 'ctrl-pad-end', '\x84': 'ctrl-pad-pageup', 'v': 'ctrl-pad-pagedown',
			'\x8d': 'ctrl-pad-up', '\x91': 'ctrl-pad-down', 's': 'ctrl-pad-left', 't': 'ctrl-pad-right',
			
			# Modificatori Numpad (Alt)
			'\x97': 'alt-pad-home', '\x9f': 'alt-pad-end', '\x99': 'alt-pad-pageup', '\xa1': 'alt-pad-pagedown',
			'\x98': 'alt-pad-up', '\xa0': 'alt-pad-down', '\x9b': 'alt-pad-left', '\x9d': 'alt-pad-right',
		}

		# Mappature per codici speciali su Windows (prefisso \xe0 - Tasti Navigazione Dedicati e F11/F12)
		special_mapping_e0 = {
			'H': 'up', 'P': 'down', 'K': 'left', 'M': 'right',
			'G': 'home', 'O': 'end', 'I': 'pageup', 'Q': 'pagedown',
			'R': 'insert', 'S': 'delete',
			
			# F11 e F12 e loro modificatori restituiscono \xe0
			'\x85': 'f11', '\x86': 'f12',
			'\x87': 'shift-f11', '\x88': 'shift-f12',
			'\x89': 'ctrl-f11', '\x8a': 'ctrl-f12',
			'\x8b': 'alt-f11', '\x8c': 'alt-f12',
			
			# Frecce dedicate con modificatori
			'\x8d': 'ctrl-up', '\x91': 'ctrl-down', 's': 'ctrl-left', 't': 'ctrl-right',
			'\x98': 'alt-up', '\xa0': 'alt-down', '\x9b': 'alt-left', '\x9d': 'alt-right',
			
			# PagUp/PagDn/Home/End dedicati con Ctrl e Alt
			'\x84': 'ctrl-pageup', 'v': 'ctrl-pagedown', 'w': 'ctrl-home', 'u': 'ctrl-end',
			'\x99': 'alt-pageup', '\xa1': 'alt-pagedown', '\x97': 'alt-home', '\x9f': 'alt-end',
			
			'\x94': 'ctrl-tab',
			'\x82': 'alt-f11', '\x83': 'alt-f12'
		}

		while time.time() - start_time <= attesa:
			if msvcrt.kbhit():
				ch = msvcrt.getwch()
				
				if ch == '\x00':
					ch2 = msvcrt.getwch()
					return special_mapping_00.get(ch2, f"special-00-{ord(ch2):02x}")
				elif ch == '\xe0':
					ch2 = msvcrt.getwch()
					return special_mapping_e0.get(ch2, f"special-e0-{ord(ch2):02x}")
				elif ch == '\r':
					return '\r'
				elif ch == '\x1b':
					return '\x1b'
				elif ch == '\x08':
					return '\x08'
				elif ch == '\t':
					return '\t'
				elif '\x01' <= ch <= '\x1a':
					# Ctrl + Lettera (Ctrl+A = 1, Ctrl+Z = 26)
					# Escludiamo Invio (\r=13), Tab (\t=9), Esc (\x1b=27) gestiti sopra
					char_letter = chr(ord(ch) + 96).lower()
					if char_letter not in ('m', 'i'): # m=13(enter), i=9(tab)
						return f"ctrl-{char_letter}"
					return ch
				else:
					return ch
			time.sleep(0.01)
		return ''
	else:
		import select
		import termios
		import tty
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		
		# Semplice mappa per alcune sequenze ANSI comuni
		ansi_mapping = {
			'[A': 'up', '[B': 'down', '[C': 'right', '[D': 'left',
			'[H': 'home', '[F': 'end', '[5~': 'pageup', '[6~': 'pagedown',
			'[2~': 'insert', '[3~': 'delete',
			'OP': 'f1', 'OQ': 'f2', 'OR': 'f3', 'OS': 'f4',
			'[15~': 'f5', '[17~': 'f6', '[18~': 'f7', '[19~': 'f8',
			'[20~': 'f9', '[21~': 'f10', '[23~': 'f11', '[24~': 'f12',
		}
		
		# Modificatori ANSI: ...[1;5A = Ctrl+Up
		# 2=Shift, 3=Alt, 4=Shift+Alt, 5=Ctrl, 6=Shift+Ctrl, 7=Alt+Ctrl, 8=Shift+Alt+Ctrl
		mod_map = {'2': 'shift', '3': 'alt', '4': 'shift-alt', '5': 'ctrl', '6': 'shift-ctrl', '7': 'alt-ctrl', '8': 'shift-alt-ctrl'}
		
		try:
			tty.setcbreak(fd)
			while time.time() - start_time <= attesa:
				rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
				if rlist:
					ch = sys.stdin.read(1)
					if ch == '\x1b':
						# Inizio sequenza ANSI
						rlist2, _, _ = select.select([sys.stdin], [], [], 0.05)
						if rlist2:
							seq = ""
							while True:
								# Leggiamo il resto della sequenza non in modo bloccante
								rl, _, _ = select.select([sys.stdin], [], [], 0.01)
								if rl:
									seq += sys.stdin.read(1)
								else:
									break
							
							# Parsa sequenza
							if seq in ansi_mapping:
								return ansi_mapping[seq]
							
							# Controlla per modificatori complessi es. [1;5A
							import re
							match = re.match(r'\[1;(\d)([A-D])', seq)
							if match:
								mod, key_char = match.groups()
								base_key = {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}.get(key_char, key_char)
								mod_str = mod_map.get(mod, f"mod{mod}")
								return f"{mod_str}-{base_key}"
								
							return f"esc-{seq}" # Seq non riconosciuta
						else:
							return 'esc'
					elif ch == '\n' or ch == '\r': return 'enter'
					elif ch == '\x08' or ch == '\x7f': return 'backspace'
					elif ch == '\t': return 'tab'
					elif '\x01' <= ch <= '\x1a':
						char_letter = chr(ord(ch) + 96).lower()
						if char_letter not in ('j', 'm', 'i'): 
							return f"ctrl-{char_letter}"
						return ch
					else:
						return ch
			return ''
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def gridapu(x=0.0, y=0.0, num=10):
	'''GRIDAPU V1.2 - Author unknown, and kindly find on the net by IU1FIG Diego Rispoli.
	Translated from Java by IZ4APU Gabriele Battaglia.
	It Receives long, lat in float and how many digits (num)
	It returns the locator as string.
	'''
	if not isinstance(y, float) or not isinstance(x, float):
		print('Lat or Lon wrong type!')
		return''
	import math
	from string import ascii_lowercase as L
	from string import ascii_uppercase as U
	from string import digits as D
	if x<-180: x+=360
	if x>180: x += -360
	ycalc = [0,0,0]
	ydiv_ar = [10, 1, 1/24, 1/240, 1/240/24]
	ycalc[0] = (x + 180)/2
	ycalc[1] = y + 90
	yn=[0,0,0,0,0,0,0,0,0,0]
	yi,yk=0,0
	while yi < 2:
		while yk < 5:
			ydiv = ydiv_ar[yk]
			yres = ycalc[yi] / ydiv
			ycalc[yi] = yres
			if ycalc[yi] > 0:
				ylp = math.floor(yres)
			else:
				ylp = math.ceil(yres)
			ycalc[yi] = (ycalc[yi] - ylp) * ydiv
			yn[2*yk + yi] = ylp
			yk += 1
		yi += 1
		yk = 0
	qthloc=""
	if num >= 2:
		qthloc += U[yn[0]] + U[yn[1]]
	if num >= 4:
		qthloc += D[yn[2]] + D[yn[3]]
	if num >= 6:
		qthloc += U[yn[4]] + U[yn[5]]
	if num >= 8:
		qthloc += D[yn[6]] + D[yn[7]]
	if num >= 10:
		qthloc += L[yn[8]] + L[yn[9]]
	return qthloc

def sonify(data_list, duration, ptm=False, vol=0.5, file=False):
	"""
	sonify V7.3 - 11 aprile 2026 - Gabriele Battaglia, Stella & Gemini 3 Pro
	Sonifies a list of float data. Optimized with NumPy vectorization and float32.
	Parameters:
	  data_list: List of float (5 <= len <= 500000)
	  duration: Total duration in seconds (e.g., 2.58)
	  ptm: If True, applies glissando (continuous portamento)
	  vol: Volume factor (0.1 <= vol <= 1.0)
	  file: If True, saves the audio to sonification[datetime].wav
	Returns immediately (non-blocking playback).
	"""
	import wave

	import numpy as np
	import sounddevice as sd
	
	try:
		data = np.asanyarray(data_list, dtype=np.float32)
	except Exception:
		return

	n = data.size
	if n < 5 or n > 500000:
		print("sonify: data_list length out of range")
		return

	vol = max(0.1, min(vol, 1.0))
	data_min = data.min()
	data_max = data.max()
	
	freq_min = 87.31   # F2
	freq_max = 5587.65 # F8
	
	data_range = data_max - data_min
	if data_range == 0:
		frequencies = np.full(n, (freq_min + freq_max) / 2, dtype=np.float32)
	else:
		frequencies = freq_min + (data - data_min) * ((freq_max - freq_min) / data_range)

	sample_rate = 44100
	total_samples = int(duration * sample_rate)
	if total_samples <= 0:
		return

	t = np.linspace(0, duration, total_samples, endpoint=False, dtype=np.float32)
	
	if ptm:
		segment_times = np.linspace(0, duration, n, endpoint=True, dtype=np.float32)
		freq_array = np.interp(t, segment_times, frequencies)
	else:
		indices = np.floor(np.linspace(0, n, total_samples, endpoint=False)).astype(np.int32)
		freq_array = frequencies[indices]

	# La cumsum in float64 previene la perdita di precisione sulle durate lunghe
	phase = 2.0 * np.pi * np.cumsum(freq_array.astype(np.float64) / sample_rate)
	audio_signal = (np.sin(phase) * vol).astype(np.float32)
	
	fade_duration_sec = 0.01
	fade_samples = int(round(fade_duration_sec * sample_rate))
	fade_samples = min(fade_samples, total_samples // 2)
	
	if fade_samples > 0:
		fade_curve = np.sin(np.linspace(0, np.pi / 2, fade_samples, dtype=np.float32))
		audio_signal[:fade_samples] *= fade_curve
		audio_signal[-fade_samples:] *= fade_curve[::-1]

	pan = np.linspace(-1.0, 1.0, total_samples, dtype=np.float32)
	pan_angle = (pan + 1.0) * (np.pi / 4.0)
	
	left = audio_signal * np.cos(pan_angle)
	right = audio_signal * np.sin(pan_angle)
	
	audio_stereo = np.column_stack((left, right))
	audio_stereo_int16 = (audio_stereo * 32767).astype(np.int16)
	
	sd.play(audio_stereo_int16, sample_rate)
	
	if file:
		from datetime import datetime
		filename = "sonification" + datetime.now().strftime("%Y%m%d%H%M%S") + ".wav"
		with wave.open(filename, 'wb') as wf:
			wf.setnchannels(2)
			wf.setsampwidth(2)
			wf.setframerate(sample_rate)
			wf.writeframes(audio_stereo_int16.tobytes())
	return

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
	  "p"                pausa, non suona niente
	  "n"                nessuna banda, il colore puro senza filtro
	  "200-2000"         passabanda fisso fra 200 e 2000 Hz
	  "200-2000.400"     il taglio alto scende da 2000 a 400 mentre suona
	  "100.400-3000"     si muove solo il taglio basso, da 100 a 400
	  "100.400-3000.900" si muovono tutti e due, ognuno per conto suo
	Il trattino separa i due tagli, il punto indica il portamento di un
	taglio. Nel campo della banda il punto significa sempre portamento e mai
	decimale: su una frequenza di taglio i decimali non servono.
	Si accettano anche le forme a lista, [200, 2000] oppure
	[[100, 400], [3000, 900]], comode da scrivere in un programma.
	Restituisce None per la pausa, altrimenti la quadrupla
	(basso_inizio, basso_fine, alto_inizio, alto_fine), dove None significa
	nessun limite da quel lato.
	Solleva ValueError se la banda e' scritta male.
	"""
	def estremi(pezzo, etichetta):
		"""Un taglio, fisso o in portamento, come coppia di frequenze."""
		if isinstance(pezzo, (list, tuple)):
			if len(pezzo) != 2:
				raise ValueError(f"Taglio {etichetta} non valido: {pezzo!r}")
			return float(pezzo[0]), float(pezzo[1])
		testo = str(pezzo).strip().lower()
		if testo in ("", "n", "none"):
			return None, None
		parti = testo.split('.')
		if len(parti) == 1:
			v = float(parti[0])
			return v, v
		if len(parti) == 2:
			return float(parti[0]), float(parti[1])
		raise ValueError(f"Taglio {etichetta} non valido: '{pezzo}'")

	if isinstance(val, (list, tuple)):
		if len(val) != 2:
			raise ValueError(f"Banda non valida: {val!r}")
		b0, b1 = estremi(val[0], "basso")
		a0, a1 = estremi(val[1], "alto")
	else:
		testo = str(val).strip().lower()
		if testo == 'p':
			return None
		if testo in ("", "n"):
			return _SENZA_BANDA
		if '-' not in testo:
			raise ValueError(
				f"Banda non valida: '{val}'. Serve taglio basso, trattino, taglio alto, "
				"per esempio 200-2000, oppure n per nessuna banda")
		sinistra, _, destra = testo.partition('-')
		b0, b1 = estremi(sinistra, "basso")
		a0, a1 = estremi(destra, "alto")

	for v in (b0, b1, a0, a1):
		if v is not None and v <= 0:
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
	     * nota (string|float): una nota musicale (es. "c4", "c#4"), un portamento separato da punto (es. "c4.e4", "880.920"), un valore in Hz, oppure "p" per pausa. Con i kind di rumore, da 5 a 8, questo campo contiene invece la banda del passabanda, per esempio "200-2000" o "200-2000.400".
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
	import re
	import sys

	import numpy as np
	from scipy import signal
	def note_to_freq(note):
		if isinstance(note, (int, float)): return float(note)
		if isinstance(note, str):
			note_lower = note.lower()
			if note_lower == 'p': return None
			def parse_single(p):
				if p == 'p': return None
				if p.isdigit(): return float(p)
				match = re.match(r"^([a-g])([#b]?)(\d)$", p)
				if not match: raise ValueError(f"Formato nota non valido: '{p}'.")
				note_letter, accidental, octave_str = match.groups()
				try: octave = int(octave_str)
				except ValueError: raise ValueError(f"Numero ottava non valido: '{octave_str}'")
				note_base = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
				semitone = note_base[note_letter]
				if accidental == '#': semitone += 1
				elif accidental == 'b': semitone -= 1
				midi_num = 12 + semitone + 12 * octave
				return 440.0 * (2.0 ** ((midi_num - 69) / 12.0))
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
		total_note_samples = int(round(dur * fs))
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
		else: # Nota, portamento o rumore
			if rumore:
				wave = _genera_rumore(kind, banda, total_note_samples, fs)
			elif kind == 1:
				if isinstance(freq, tuple):
					f_start, f_end = freq
					freq_array = np.linspace(f_start, f_end, total_note_samples, endpoint=False)
					phase = 2.0 * np.pi * np.cumsum(freq_array.astype(np.float64) / fs)
				else:
					t = np.linspace(0, dur, total_note_samples, endpoint=False)
					phase = 2.0 * np.pi * freq * t
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
					phase_ovs = 2.0 * np.pi * np.cumsum(freq_array_ovs.astype(np.float64) / fs_ovs)
				else:
					dt_ovs = np.full(total_ovs_samples, freq / fs_ovs, dtype=np.float64)
					t_ovs = np.linspace(0, dur, total_ovs_samples, endpoint=False)
					phase_ovs = 2.0 * np.pi * freq * t_ovs
				
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
			attack_samples = int(round(attack_frac * total_note_samples))
			decay_samples = int(round(decay_frac * total_note_samples))
			release_samples = int(round(release_frac * total_note_samples))
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
		segments.append(stereo_segment)
	if not segments: return None
	full_signal_float = np.concatenate(segments, axis=0)
	full_signal_float = np.clip(full_signal_float, -1.0, 1.0)
	return full_signal_float

class _Acusticator:
    """V7.2.4 di giovedì 3 settembre 2026 - Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Sonnet 5, modalità auto)

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

        ["200-2000", 2.0, 0, 0.4]       banda ferma fra 200 e 2000 Hz
        ["200-2000.400", 3.0, 0, 0.4]   il taglio alto scende: vento che cala
        ["100.400-3000", 3.0, 0, 0.4]   si muove solo il taglio basso
        ["100.400-3000.900", 3, 0, 0.4] si muovono tutti e due
        ["n", 1.0, 0, 0.4]              nessuna banda, il colore puro
        ["p", 0.5, 0, 0.4]              pausa, come per le note

    I due tagli sono indipendenti: ciascuno ha il suo portamento e non
    sanno l'uno dell'altro. Nel campo della banda il punto significa sempre
    portamento e mai decimale, perche' su una frequenza di taglio i
    decimali non servono. Durata, panning, volume e inviluppo si comportano
    esattamente come per le note.

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
    davvero fra loro, fino a sedici per volta, invece di essere otto
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
    """

    NOME_COLLEZIONE = "Acu_Collection.json"
    BASE_VOL = 0.5
    VOCI_MAX = 16
    SILENZIO_MAX = 120.0
    BLOCCO = 256

    def __init__(self):
        import threading
        self._cache = {}
        self._locali = []
        # Stato del mixer
        self._volume = 1.0
        self._voci_max = self.VOCI_MAX
        self._silenzio = self.SILENZIO_MAX
        self._fs = 44100
        self._device = None
        self._canali = 2
        self._voci = []
        self._stream = None
        self._guardiano = None
        self._silenzio_da = None
        self._uscita_registrata = False
        self._lock = threading.Lock()
        self._avvio = threading.RLock()

    def __call__(self, score, kind=1, adsr=None, fs=44100, sync=False):
        """Sintetizza uno score e lo manda al mixer. Vedi la classe per lo score.

        sync dice quanto aspettare prima di restituire il controllo:
          False   non aspetta, il suono prosegue per conto suo.
          True    aspetta che il suono sia davvero finito nelle casse.
          numero  aspetta al massimo quei secondi, poi torna comunque.
        La scadenza e' una rete di sicurezza: se il dispositivo audio si
        pianta, il chiamante non resta appeso per sempre.
        Restituisce True se il suono e' stato accodato.
        """
        buffer = _sintetizza(score, kind, adsr, fs)
        if buffer is None:
            return False
        return self.riproduci(buffer, fs=fs, sync=sync)

    # --- Il mixer -------------------------------------------------------
    # Un solo stream tenuto aperto, invece di aprirne e chiuderne uno per
    # ogni suono: l'apertura da sola costava 160 ms misurati, pagati da
    # ogni singolo effetto sonoro di ogni applicazione.

    def setup(self, volume=None, voci_max=None, silenzio=None, fs=None, device=None):
        """Imposta il mixer, di solito una volta sola all'avvio dell'applicazione.

        volume    volume generale da 0 a 1, applicato a tutto cio' che suona.
                  Impostandolo qui non serve piu' passarlo a ogni chiamata.
        voci_max  quanti suoni possono sovrapporsi, 16 di partenza. Quando
                  sono tutte occupate, la voce piu' vecchia lascia il posto
                  alla nuova, cosi' l'ultimo evento si sente sempre.
        silenzio  secondi di silenzio dopo i quali lo stream viene chiuso e
                  la scheda audio liberata, 120 di partenza. Si riapre da
                  solo al suono successivo.
        fs        frequenza di campionamento dello stream, 44100 di partenza.
        device    dispositivo di uscita, None per quello di sistema.
        Cambiare fs o device chiude lo stream in corso, che si riaprira'
        con i valori nuovi. Restituisce le impostazioni in vigore.
        """
        if volume is not None:
            self._volume = max(0.0, min(1.0, float(volume)))
        if voci_max is not None:
            self._voci_max = max(1, int(voci_max))
        if silenzio is not None:
            self._silenzio = max(0.0, float(silenzio))
        riapri = False
        if fs is not None and int(fs) != self._fs:
            self._fs = int(fs)
            riapri = True
        if device is not None and device != self._device:
            self._device = device
            riapri = True
        if riapri:
            self.close()
        return {"volume": self._volume, "voci_max": self._voci_max,
                "silenzio": self._silenzio, "fs": self._fs, "device": self._device}

    def _adatta_frequenza(self, buffer, fs):
        """Riporta un buffer alla frequenza dello stream, se serve."""
        if fs == self._fs:
            return buffer
        from fractions import Fraction

        import numpy as np
        from scipy import signal
        rapporto = Fraction(self._fs, int(fs)).limit_denominator(1000)
        adattato = signal.resample_poly(buffer, rapporto.numerator,
                                        rapporto.denominator, axis=0)
        return np.clip(adattato, -1.0, 1.0).astype(np.float32)

    def _callback(self, outdata, frames, tempo, stato):
        """Somma le voci attive. Gira nel thread audio: niente di lento qui."""
        import numpy as np
        outdata.fill(0.0)
        with self._lock:
            # Niente list.remove(voce): confrontare due voci per uguaglianza
            # confronta anche i loro buffer, e numpy solleva ValueError se le
            # forme non combaciano invece di dire semplicemente "diverso".
            attive_voci = []
            for voce in self._voci:
                dati = voce["buffer"]
                da = voce["pos"]
                a = min(da + frames, len(dati))
                quanti = a - da
                if quanti > 0:
                    outdata[:quanti] += dati[da:a]
                voce["pos"] = a
                if a >= len(dati):
                    voce["fine"].set()
                else:
                    attive_voci.append(voce)
            self._voci = attive_voci
            attive = len(self._voci)
        if self._volume != 1.0:
            outdata *= self._volume
        np.clip(outdata, -1.0, 1.0, out=outdata)
        if attive == 0:
            self._silenzio_da = self._silenzio_da or self._orologio()
        else:
            self._silenzio_da = None

    def _orologio(self):
        import time
        return time.monotonic()

    def _apri_stream(self):
        """Apre lo stream, provando il mono se il dispositivo rifiuta lo stereo."""
        import sys

        import sounddevice as sd
        for canali in (2, 1):
            try:
                stream = sd.OutputStream(
                    samplerate=self._fs, channels=canali, dtype="float32",
                    blocksize=self.BLOCCO, latency="low", device=self._device,
                    callback=self._callback)
                stream.start()
                self._canali = canali
                return stream
            except Exception as e:  # noqa: BLE001 - il dispositivo audio fallisce in molti modi
                ultimo = e
        print(f"Acusticator: non riesco ad aprire l'uscita audio: {ultimo}", file=sys.stderr)
        return None

    def _assicura_stream(self):
        """Lo stream esiste ed e' attivo, altrimenti lo apre."""
        if self._stream is not None:
            return True
        self._stream = self._apri_stream()
        if self._stream is None:
            return False
        if not self._uscita_registrata:
            # Alla fine del programma lo stream va chiuso, altrimenti la scheda
            # audio resta impegnata: il guardiano e' un thread daemon e in
            # chiusura non fa in tempo ad accorgersene.
            import atexit
            atexit.register(self.close)
            self._uscita_registrata = True
        self._avvia_guardiano()
        return True

    def _avvia_guardiano(self):
        """Il thread che chiude lo stream dopo abbastanza silenzio."""
        import threading
        if self._guardiano is not None and self._guardiano.is_alive():
            return
        self._guardiano = threading.Thread(target=self._guardia, daemon=True,
                                           name="Acusticator-guardiano")
        self._guardiano.start()

    def _guardia(self):
        import time
        while True:
            time.sleep(1.0)
            if self._stream is None:
                return
            if self._silenzio <= 0:
                continue
            da = self._silenzio_da
            if da is not None and self._orologio() - da >= self._silenzio:
                self.close()
                return

    def riproduci(self, buffer, fs=None, sync=False):
        """Manda al mixer un buffer gia' pronto, stereo float32 fra -1 e 1.

        E' la strada di servizio usata da __call__; torna utile a chi si
        sintetizza l'audio per conto suo e vuole comunque passare dal
        mixer condiviso.
        """
        import threading

        import numpy as np
        if buffer is None or len(buffer) == 0:
            return False
        buffer = np.asarray(buffer, dtype=np.float32)
        if buffer.ndim == 1:
            buffer = np.column_stack((buffer, buffer))
        if fs is not None:
            buffer = self._adatta_frequenza(buffer, fs)
        with self._avvio:
            if not self._assicura_stream():
                return False
            if self._canali == 1:
                buffer = buffer.mean(axis=1, keepdims=True).astype(np.float32)
        fine = threading.Event()
        voce = {"buffer": buffer, "pos": 0, "fine": fine, "nata": self._orologio()}
        with self._lock:
            # Voci esaurite: la piu' vecchia lascia il posto, cosi' l'ultimo
            # evento si sente sempre. Chi la stava aspettando viene svegliato.
            while len(self._voci) >= self._voci_max:
                vecchia = self._voci.pop(0)
                vecchia["fine"].set()
            self._voci.append(voce)
            self._silenzio_da = None
        if sync is not False and sync is not None:
            attesa = None if sync is True else max(0.0, float(sync))
            fine.wait(timeout=attesa)
            if sync is True:
                # I campioni sono usciti dal mixer ma non ancora dalle casse:
                # senza questa attesa un suono di congedo verrebbe troncato.
                self._aspetta_uscita()
        return True

    def _aspetta_uscita(self):
        """Il tempo che i campioni gia' consegnati impiegano a uscire."""
        import time
        ritardo = 0.05
        try:
            if self._stream is not None:
                ritardo = float(self._stream.latency) + 0.02
        except (AttributeError, TypeError, ValueError):
            pass
        time.sleep(min(ritardo, 0.5))

    def stop(self):
        """Zittisce subito tutto quello che sta suonando, senza chiudere nulla.

        Lo stream resta aperto e pronto: e' quello che serve quando l'utente
        preme Esc e vuole silenzio immediato. Restituisce quante voci ha
        interrotto.
        """
        with self._lock:
            quante = len(self._voci)
            for voce in self._voci:
                voce["fine"].set()
            self._voci.clear()
            self._silenzio_da = self._orologio()
        return quante

    def close(self):
        """Zittisce e chiude lo stream, liberando la scheda audio.

        Da chiamare all'uscita dell'applicazione. Non serve farlo per forza:
        dopo il silenzio impostato con setup lo stream si chiude da solo, e
        al suono successivo si riapre. Restituisce True se c'era da chiudere.
        """
        self.stop()
        with self._avvio:
            stream = self._stream
            self._stream = None
            self._guardiano = None
        if stream is None:
            return False
        try:
            stream.stop()
            stream.close()
        except Exception:  # noqa: BLE001, S110 - in chiusura non c'e' piu' niente da salvare
            pass
        return True

    def stato(self):
        """Come sta il mixer adesso, come dizionario. Utile per capire i guai."""
        with self._lock:
            attive = len(self._voci)
        return {"stream_aperto": self._stream is not None, "voci_attive": attive,
                "voci_max": self._voci_max, "volume": self._volume,
                "silenzio": self._silenzio, "fs": self._fs,
                "canali": self._canali, "device": self._device}

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

    def preset(self, nome, volume=None):
        """Restituisce (score, kind, adsr) pronti da passare al motore.

        Lo score torna appiattito e con i volumi assoluti, cioe' gia'
        convertiti dagli scarti scritti nel file. volume, se dato,
        sostituisce la base 0.5 su cui gli scarti si applicano: e' il modo
        di rispettare il volume scelto dall'utente nelle impostazioni.
        Restituisce (None, None, None) se il preset non esiste.
        """
        dati, _ = self._cerca(nome)
        if dati is None:
            self._avvisa(f"preset sconosciuto: {nome}")
            return None, None, None
        base = self.BASE_VOL if volume is None else float(volume)
        piatto = []
        for quartina in dati.get("score", []):
            try:
                nota, dur, pan, scarto = quartina
            except (TypeError, ValueError):
                self._avvisa(f"preset {nome}: quartina malformata, la salto")
                continue
            if isinstance(scarto, str):
                assoluto = scarto
            else:
                assoluto = max(0.0, min(1.0, base + float(scarto)))
            piatto.extend([nota, dur, pan, assoluto])
        return piatto, dati.get("kind", 1), dati.get("adsr")

    def play(self, nome, sync=False, volume=None):
        """Suona un preset della collezione. Vero se e' partito."""
        score, kind, adsr = self.preset(nome, volume=volume)
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

def dgt(prompt="", kind="s", imin=-999999999, imax=999999999, fmin=-999999999.9, fmax=999999999.9, smin=0, smax=256, pwd=False, default=None):
	'''Versione 1.10 di lunedì 24 febbraio 2025
	Potenzia la funzione input implementando controlli di sicurezza.
	Riceve il prompt, il tipo e
	  imin e imax minimo e massimo per i valori interi;
	  fmin e fmax minimo e massimo per i valori float;
	  smin e smax minimo e massimo per la quantità di caratteri nella stringa.
	se il valore e più piccolo di minimo, quest'ultimo viene ritornato, idem per il valore massimo;
	il kind può essere s stringa, i intero e f float;
	se pwd è vera, si chiama getpass per l'inserimento mascherato e non vengono accettati valori fuori dai limiti
	default viene ritornato solo se si preme invio prima di aver fornito un input e se dgt ha ricevuto un valore diverso da None
	'''
	kind = kind[0].lower()
	if kind not in 'sif':
		print("Chiamata non corretta a DGT, verificare parametro kind.")
		kind="s"
	if pwd: import getpass
	while True:
		if pwd: p = getpass.getpass(prompt)
		else: p = input(prompt)
		if p == "" and default is not None: return default
		if kind == "i":
			try:
				p = int(p)
				if pwd:
					if p < imin or p > imax: print(f"Valore {p} non consentito.")
					else: return p
				elif p < imin:
					print(f"Corretto con {imin-p}, accettato: {imin}")
					return int(imin)
				elif p > imax:
					print(f"Corretto con {imax-p}, accettato: {imax}")
					return int(imax)
				else: return int(p)
			except ValueError:
				print("Si prega di inserire un valore numerico intero.")
		if kind == "f":
			try:
				p = float(p)
				if pwd:
					if p < fmin or p > fmax: print(f"Valore {p} non consentito.")
					else: return p
				elif p < fmin:
					print(f"Corretto con {fmin-p:10.3}, accettato: {fmin}")
					return float(fmin)
				elif p > fmax:
					print(f"Corretto con {fmax-p:10.3}, accettato: {fmax}")
					return float(fmax)
				else: return p
			except ValueError:
				print("Si prega di inserire un valore numerico decimale.")
		elif kind == "s":
			if pwd:
				if len(p) < smin or len(p) > smax:
					print("Lunghezza stringa non consentita.")
				else: return p
			elif len(p) < smin:
				print(f"Stringa troppo corta: {len(p)}, richiesta: {smin}")
			elif len(p) > smax:
				print(f"Lunghezza stringa eccessiva: {len(p)}, richiesti: {smax} caratteri.")
				p = p[:smax]
				print(f"Accettato {p}")
				return p
			else: return p

def manuale(nf):
	'''
	Versione 1.0.1 di domenica 5 maggio 2024
	pager che carica e mostra un file di testo.
	riceve il nomefile e non restituisce nulla
	'''
	try:
		man = open(nf, "rt")
		rig = man.readlines()
		man.close()
		cr = 0; tasto = "."
		for l in rig:
			print(l,end="")
			cr += 1
			if cr % 15 == 0:
				tasto = dgt("\nPremi invio per proseguire o 'e' per uscire dalla guida. Pagina "+str(int(cr/15)))
				if tasto.lower() == "e": break
	except OSError:
		print("Attenzione, file della guida mancante.\n\tRichiedere il file all'autore dell'App.")

def menu(d={}, p="> ", ntf="Scelta non valida", show=True, show_only=False, keyslist=True, pager=20, show_on_filter=True, numbered=False, ordered=True, empty_enter=None):
    """V4.6.4 - sabato 27 giugno 2026 - Stella Gemini 3.5 Flash & Gabriele Battaglia
    Crea un menu interattivo da un dizionario, con filtraggio e autocompletamento robusto.
    Parametri:
    d: dizionario con coppie chiave:descrizione.
    p: prompt personalizzato; usato in modalità non-keyslist o in modalità numerata.
    ntf: messaggio in caso di filtro vuoto o input ambiguo.
    show: se True, mostra il menu iniziale completo prima del prompt.
    show_only: se True, mostra il menu completo e termina (non interattivo).
    keyslist: se True (default), il prompt suggerisce i caratteri per l'autocompletamento.
    pager: numero di elementi da mostrare per pagina. Impostare a 0 per disabilitare.
    show_on_filter: se True, la lista delle opzioni si aggiorna visivamente a ogni tasto.
    numbered: se True, il menu diventa numerato, con selezione interattiva dei numeri.
    ordered: se True (default), le voci del menu vengono ordinate alfabeticamente per chiave.
    Restituisce:
    La chiave scelta dal dizionario 'd', oppure None se l'utente annulla (ESC o Invio su input vuoto).
    """
    import os
    import sys
    def lcp(strings):
        """Calcola il prefisso comune più lungo da una lista di stringhe ignorando il case."""
        if not strings: return ""
        lower_strings = [s.lower() for s in strings]
        prefix_len = len(os.path.commonprefix(lower_strings))
        return strings[0][:prefix_len]
    def key(prompt=""):
        """Legge un singolo carattere dalla console senza bisogno di Invio."""
        print(prompt, end='', flush=True)
        if os.name == 'nt':
            import msvcrt
            ch = msvcrt.getwch()
            if ch in ('\x00', '\xe0'):
                msvcrt.getwch()
                return '\x00'
            if ch == '\x08': return ch
            if ch == '\r': return ch
            if ch == '\x1b': return ch
            if ch == '?': return ch
            if ord(ch) == 127: return '\x08'
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
                if ch == '\x1b':
                    r, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if r:
                        sys.stdin.read(2)
                        return '\x00'
                    else:
                        return '\x1b'
                elif ord(ch) == 127: return '\x08'
                elif ch in ['\n', '\r']: return '\r'
                else: return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    def Mostra(items_to_show, pager, is_numbered, num_map=None, user_input=""):
        """Visualizza una lista di elementi usando un pager internazionalizzato."""
        count = 0
        total = len(items_to_show)
        if total == 0 and user_input: print(ntf); return True
        if total == 0: return True
        print("--- Menu ---")
        for item in items_to_show:
            if is_numbered:
                original_key = num_map[item]
                desc = d[original_key]
                print(f"[{item}] -- {desc}")
            else:
                desc = d.get(item, "N/A")
                print(f"- ({item}) -- {desc};")
            count += 1
            if pager > 0 and count % pager == 0 and count < total:
                page_num = int(count / pager)
                prompt_pager = f"--- [{page_num}] ({count-pager+1}-{count}/{total}) ---"
                ch_pager = key(prompt_pager); print()
                if ch_pager == '\x1b': return False
        print(f"---------- [{count}/{total}] ----------")
        return True
    def Listaprompt_autocomplete(keys_list, display_input):
        """Genera un prompt che suggerisce i prossimi caratteri validi."""
        if not keys_list or len(keys_list) <= 1: return ">"
        next_chars = []
        seen = set()
        input_len = len(display_input)
        for key in keys_list:
            if len(key) > input_len:
                char = key[input_len].upper()
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
    if not d: print("No options available."); return None
    if len(d) == 1 and not show_only: return list(d.keys())[0]
    if show_only: Mostra(orig_keys, pager, numbered, num_map); return None
    if show:
        Mostra(orig_keys, pager, numbered, num_map)
        last_displayed = orig_keys[:]
    disable_autocomplete_once = False
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
            print("\n-----------------------")
            Mostra(final_filtered, pager, numbered, num_map, user_input)
            last_displayed = final_filtered[:]
        if numbered:
            prompt_str = p if p != "> " else f"(1-{len(orig_keys)})"
            if not prompt_str.strip().endswith('>'): prompt_str += '> '
        elif keyslist:
            prompt_str = Listaprompt_autocomplete(final_filtered, display_input)
        else:
            prompt_str = p
        full_prompt = "\n"+prompt_str + display_input
        user_char = key(full_prompt)
        if user_char in ['\r', '\n']:
            print()
            exact_matches = [k for k in final_filtered if k.lower() == display_input.lower()]
            if exact_matches:
                return num_map.get(exact_matches[0], exact_matches[0])
            elif len(final_filtered) == 1:
                 return num_map.get(final_filtered[0], final_filtered[0])
            elif user_input == "":
                return empty_enter
            else:
                 print("--- '?' . ---")
                 last_displayed = None
        elif user_char in ['\x1b', '\x03']: print(); return None
        elif user_char == '?':
            print("\n")
            Mostra(final_filtered, pager, numbered, num_map, user_input)
            last_displayed = final_filtered[:]
        elif user_char == '\x08':
            if user_input:
                user_input = user_input[:-1]
                print('\b \b'*len(display_input), end='', flush=True)
                last_displayed = None
                disable_autocomplete_once = True
        elif user_char == '\x00': pass
        else:
            if (numbered and not user_char.isdigit()): pass
            else:
                print(user_char, end='', flush=True)
                user_input += user_char
                last_displayed = None
                disable_autocomplete_once = False

def Donazione(lang=None):
    """
    V2.0 del 12 luglio 2026
    Mostra un messaggio di donazione con una probabilità del 20%
    nella lingua specificata o rilevata dal sistema/configurazione.
    Lingue supportate: Italiano, Portoghese, Inglese, Francese, Spagnolo, Tedesco, Russo, Cinese (semplificato), Giapponese, Arabo.
    """
    import builtins
    import json
    import locale
    import os
    import random
    import sys

    if random.randint(1, 100) <= 20:
        messaggi = {
            'it': "Se questo software ti è piaciuto, ti è stato utile, ti sei divertito ad usarlo, considera l'idea di offrirmi un caffè. Mi trovi su paypal come gabriele.battaglia@gmail.com Grazie di cuore.",
            'en': "If you enjoyed this software, found it useful, or had fun using it, consider buying me a coffee. You can find me on PayPal at gabriele.battaglia@gmail.com Thank you.",
            'pt': "Se você gostou deste software, o achou útil ou se divertiu usando-o, considere me pagar um café. Você pode me encontrar no PayPal em gabriele.battaglia@gmail.com. Muito obrigado.",
            'fr': "Si vous avez aimé ce logiciel, l'avez trouvé utile ou vous êtes amusé en l'utilisant, envisagez de m'offrir un café. Vous pouvez me trouver sur PayPal à l'adresse gabriele.battaglia@gmail.com Merci beaucoup.",
            'es': "Si te ha gustado este software, te ha resultado útil o te has divertido usándolo, considera la idea de invitarme a un café. Me puedes encontrar en PayPal como gabriele.battaglia@gmail.com. Muchas gracias.",
            'de': "Wenn Ihnen diese Software gefallen hat, sie nützlich war oder Sie Spaß daran hatten, sie zu nutzen, ziehen Sie in Betracht, mir einen Kaffee auszugeben. Sie finden mich auf PayPal unter gabriele.battaglia@gmail.com Vielen Dank.",
            'ru': "Если вам понравилась эта программа, она оказалась полезной или вы получили удовольствие от ее использования, рассмотрите возможность угостить меня кофе. Вы можете найти меня на PayPal по адресу gabriele.battaglia@gmail.com Спасибо.",
            'zh': "如果您喜欢这款软件，觉得它有用，或者在使用过程中获得了乐趣，请考虑请我喝杯咖啡。您可以在PayPal上找到我：gabriele.battaglia@gmail.com 谢谢。",
            'ja': "このソフトウェアを楽しんだり、役立つと感じたり、楽しく使っていただけたなら、私にコーヒーをご馳走することを検討してください。PayPalでgabriele.battaglia@gmail.comとして見つけることができます。ありがとうございます。",
            'ar': "إذا أعجبك هذا البرنامج، أو وجدته مفيدًا، أو استمتعت باستخدامه، ففكر في شراء قهوة لي. يمكنك العثور عليّ على PayPal على gabriele.battaglia@gmail.com. شكرًا لك."
        }
        lingua_rilevata = None

        # 1. Priorità: Parametro esplicito 'lang'
        if lang:
            try:
                lingua_rilevata = str(lang).strip().lower().split('_')[0].split('-')[0]
            except Exception:
                pass

        # 2. Priorità: Leggere la lingua selezionata da selected_language.json (usato da polipo)
        if not lingua_rilevata:
            percorsi_ricerca = []
            try:
                if hasattr(sys, 'frozen') and sys.frozen:
                    percorsi_ricerca.append(os.path.dirname(sys.executable))
                if sys.argv and sys.argv[0]:
                    percorsi_ricerca.append(os.path.dirname(os.path.abspath(sys.argv[0])))
            except Exception:
                pass
            percorsi_ricerca.append(os.getcwd())

            for percorso in percorsi_ricerca:
                if not percorso:
                    continue
                file_settings = os.path.join(percorso, 'selected_language.json')
                if os.path.exists(file_settings):
                    try:
                        with open(file_settings, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            codice = data.get('language_code')
                            if codice:
                                lingua_rilevata = str(codice).strip().lower().split('_')[0].split('-')[0]
                                break
                    except Exception:
                        pass

        # 3. Priorità: Ispezionare la funzione di traduzione builtins._
        if not lingua_rilevata:
            try:
                if hasattr(builtins, '_'):
                    _ = builtins._
                    if hasattr(_, '__self__'):
                        trans = _.__self__
                        if hasattr(trans, 'info'):
                            info = trans.info()
                            if 'language' in info:
                                lingua_rilevata = info['language'].strip().lower().split('_')[0].split('-')[0]
            except Exception:
                pass

        # 4. Priorità: Variabili d'ambiente standard
        if not lingua_rilevata:
            for var in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
                valore = os.environ.get(var)
                if valore:
                    valore_pulito = valore.split(':')[0].split('_')[0].split('-')[0].strip().lower()
                    if valore_pulito:
                        lingua_rilevata = valore_pulito
                        break

        # 5. Priorità: Windows UI Language via ctypes
        if not lingua_rilevata and sys.platform == 'win32':
            try:
                import ctypes
                lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
                locale_name = locale.windows_locale.get(lang_id)
                if locale_name:
                    lingua_rilevata = locale_name.split('_')[0].lower()
            except Exception:
                pass

        # 6. Priorità: Unix/Mac fallback locale.getlocale()
        if not lingua_rilevata:
            try:
                locale_tuple = locale.getlocale()
                if locale_tuple and locale_tuple[0]:
                    lingua_rilevata = locale_tuple[0].split('_')[0].lower()
            except Exception:
                pass

        # 7. Priorità: locale.getdefaultlocale() (ultimo fallback deprecato prima della rimozione)
        if not lingua_rilevata:
            try:
                if hasattr(locale, 'getdefaultlocale'):
                    lingua_os_completa, _ = locale.getdefaultlocale()
                    if lingua_os_completa:
                        lingua_rilevata = lingua_os_completa.split('_')[0].lower()
            except Exception:
                pass

        # Fallback finale: inglese
        if not lingua_rilevata:
            lingua_rilevata = 'en'

        messaggio_da_mostrare = messaggi.get(lingua_rilevata, messaggi['en'])
        print(messaggio_da_mostrare)

def polipo(domain='messages', localedir='locales', source_language='en', config_path=None):
    """
    polipo V6.0 by Gabriele Battaglia and Gemini - 18/07/2025
    Versione autonoma e compatibile con PyInstaller.
    - Trova autonomamente le risorse (es. cartella 'locales').
    - Salva il file di configurazione della lingua accanto all'eseguibile o allo script.
    - Salva l'elenco delle lingue disponibili e mostra il menu se cambiano.
    - Non richiede funzioni esterne di supporto.
    """
    import gettext
    import json
    import locale
    import os
    import sys
    # Rileva se l'app è "congelata" (compilata con PyInstaller)
    is_frozen = getattr(sys, 'frozen', False)
    # LOGICA 1: Trovare il percorso delle RISORSE (dati come la cartella 'locales')
    if is_frozen:
        resources_base_path = sys._MEIPASS
    else:
        resources_base_path = os.getcwd()
    # LOGICA 2: Trovare il percorso di SALVATAGGIO (per il file.json)
    # 1. Determina il percorso di base di default
    if is_frozen:
        base_save_path = os.path.dirname(sys.executable) # Cartella dell'eseguibile
    else:
        base_save_path = os.getcwd() # Cartella dello script
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
    # Assicuriamoci che la cartella di configurazione esista, altrimenti la creiamo
    if not os.path.exists(config_save_path):
        try:
            os.makedirs(config_save_path)
            print(f"Info: Created configuration directory at '{config_save_path}'")
        except OSError as e:
            print(f"ERROR: Could not create configuration directory: {e}")
            # Se non possiamo creare la cartella, non possiamo procedere con il salvataggio
            # Potremmo voler gestire questo errore in modo più robusto
            # Per ora, terminiamo la parte di configurazione e usiamo la lingua di default
            return source_language, lambda text: text
    # Costruisce i percorsi completi
    localedir_abs = os.path.join(resources_base_path, localedir)
    selected_lang_file = os.path.join(config_save_path, 'selected_language.json')
    system_lang, _ = locale.getdefaultlocale()
    system_lang_code = system_lang.split('_')[0] if system_lang else source_language
    try:
        available_translations = [d for d in os.listdir(localedir_abs) if os.path.isdir(os.path.join(localedir_abs, d))]
    except FileNotFoundError:
        print(f"WARNING: Translations folder '{localedir_abs}' not found.")
        print(f"The application will use the source language ('{source_language}').")
        return source_language, lambda text: text
    current_choices_set = {source_language}
    if system_lang_code:
        current_choices_set.add(system_lang_code)
    current_choices_set.update(available_translations)
    current_available_languages = sorted(list(current_choices_set))
    language_code = None
    show_menu = False
    try:
        with open(selected_lang_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            language_code = data.get('language_code')
            saved_available_languages = data.get('available_languages', [])
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
    except (FileNotFoundError, json.JSONDecodeError):
        show_menu = True

    if show_menu:
        if system_lang_code in current_available_languages:
            default_fallback = system_lang_code
        else:
            default_fallback = source_language

        print("\nSelect your language:")
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
            except (EOFError, KeyboardInterrupt):
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
            print(f"Info: Language '{language_code}' saved to '{selected_lang_file}' for future use.")
        except OSError as e:
            print(f"WARNING: Could not save the selected language. Error: {e}")
    if language_code == source_language:
        return source_language, lambda text: text
    else:
        try:
            translation = gettext.translation(
                domain,
                localedir=localedir_abs,
                languages=[language_code],
                fallback=True
            )
            return language_code, translation.gettext
        except FileNotFoundError:
            print(f"ERROR: Translation file for '{language_code}' not found in '{localedir_abs}'.")
            return source_language, lambda text: text
