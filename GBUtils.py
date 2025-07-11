'''
	GBUtils di Gabriele Battaglia (IZ4APU)
	Data concepimento: lunedì 3 febbraio 2020.
	Raccoglitore di utilità per i miei programmi.
	Spostamento su github in data 27/6/2024. Da usare come submodule per gli altri progetti.
	V54 di venerdì 11 luglio 2025
Lista utilità contenute in questo pacchetto
	Acusticator V5.8 di giovedì 27 marzo 2025. Gabriele Battaglia e Gemini 2.5
	base62 3.0 di martedì 15 novembre 2022
	CWzator V8.2 di mercoledì 28 maggio 2025 - Gabriele Battaglia (IZ4APU), Claude 3.5, ChatGPT o3-mini-high, Gemini 2.5 Pro
	dgt Versione 1.10 di lunedì 24 febbraio 2025
	Donazione V1.1 del 18 giugno 2025
	gridapu 1.2 from IU1FIG
	key V5.0 di mercoledì 12/02/2025 by Gabriele Battaglia and ChatGPT o3-mini-high.
	manuale 1.0.1 di domenica 5 maggio 2024
	Mazzo V5.1 - aprile 2025 b Gabriele Battaglia & Gemini 2.5
	menu V3.13 – martedì 8 luglio 2025 - Gabriele Battaglia & Gemini 2.5
	percent V1.0 thu 28, september 2023
	polipo V5.1 by Gabriele Battaglia and Gemini - 28/06/2025
	Scadenza 1.0 del 15/12/2021
	sonify V7.1 - 11 luglio 2025 - Gabriele Battaglia eChatGPT O1, Gemini 2.5 Pro
	Vecchiume 1.0 del 15/12/2018
'''

def CWzator(msg, wpm=35, pitch=550, l=30, s=50, p=50, fs=44100, ms=1, vol=0.5, wv=1, sync=False, file=False):
	"""
	V8.2 di mercoledì 28 maggio 2025 - Gabriele Battaglia (IZ4APU), Claude 3.5, ChatGPT o3-mini-high, Gemini 2.5 Pro
		da un'idea originale di Kevin Schmidt W9CF
	Genera e riproduce l'audio del codice Morse dal messaggio di testo fornito.
	Parameters:
		msg (str|int): Messaggio di testo da convertire in Morse.
			se == -1 restituisce la mappa	morse come dizionario.
		wpm (int): Velocità in parole al minuto (range 5-100).
		pitch (int): Frequenza in Hz per il tono (range 130-2000).
		l (int): Peso per la durata della linea (default 30).
		s (int): Peso per la durata degli spazi tra simboli/lettere (default 50).
		p (int): Peso per la durata del punto (default 50).
		fs (int): Frequenza di campionamento (default 44100 Hz).
		ms (int): Durata in millisecondi per i fade-in/out sui toni (default 1).
		vol (float): Volume (range 0.0 a 1.0, default 0.5).
		wv (int): Tipo d’onda (scipy.signal): 1=Sine(default), 2=Square, 3=Triangle, 4=Sawtooth.
		sync (bool): Se True, la funzione aspetta la fine della riproduzione; altrimenti ritorna subito.
		file (bool): Se True, salva l’audio in un file WAV.
	Returns:
		Un oggetto PlaybackHandle e rwpm (velocità effettiva wpm), o (None, None) in caso di errore.
	"""
	import numpy as np
	import sounddevice as sd
	import wave
	from datetime import datetime
	import threading
	import re
	import sys
	from scipy import signal # Importato per le forme d'onda
	BLOCK_SIZE = 256
	# --- Validazione Parametri Migliorata ---
	MORSE_MAP = {
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
	if msg==-1: return MORSE_MAP
	elif not isinstance(msg, str) or msg == "": print("CWzator Error: msg deve essere una stringa non vuota.", file=sys.stderr); return None, None
	if not (isinstance(wpm, int) and 5 <= wpm <= 100): print(f"CWzator Error: wpm ({wpm}) non valido [5-100].", file=sys.stderr); return None, None
	if not (isinstance(pitch, int) and 130 <= pitch <= 2000): print(f"CWzator Error: pitch ({pitch}) non valido [130-2000].", file=sys.stderr); return None, None
	if not (isinstance(l, int) and 1 <= l <= 100): print(f"CWzator Error: l ({l}) non valido [1-100].", file=sys.stderr); return None, None
	if not (isinstance(s, int) and 1 <= s <= 100): print(f"CWzator Error: s ({s}) non valido [1-100].", file=sys.stderr); return None, None
	if not (isinstance(p, int) and 1 <= p <= 100): print(f"CWzator Error: p ({p}) non valido [1-100].", file=sys.stderr); return None, None
	if not (isinstance(fs, int) and fs > 0): print(f"CWzator Error: fs ({fs}) non valido [>0].", file=sys.stderr); return None, None
	if not (isinstance(ms, (int, float)) and ms >= 0): print(f"CWzator Error: ms ({ms}) non valido [>=0].", file=sys.stderr); return None, None
	if not (isinstance(vol, (int, float)) and 0.0 <= vol <= 1.0): print(f"CWzator Error: vol ({vol}) non valido [0.0-1.0].", file=sys.stderr); return None, None
	if not (isinstance(wv, int) and wv in [1, 2, 3, 4]): print(f"CWzator Error: wv ({wv}) non valido [1-4].", file=sys.stderr); return None, None
	# --- Calcolo Durate (con arrotondamento campioni implicito dopo) ---
	T = 1.2 / float(wpm)
	dot_duration = T * (p / 50.0)
	dash_duration = 3.0 * T * (l / 30.0) # Usato 3.0 per float
	intra_gap = T * (s / 50.0)
	letter_gap = 3.0 * T * (s / 50.0)
	word_gap = 7.0 * T * (s / 50.0)
	# --- Funzioni Generazione Segmenti (con forme d'onda scipy e arrotondamento) ---
	def generate_tone(duration):
		# Arrotonda qui per il numero di campioni
		N = int(round(fs * duration))
		if N <= 0: return np.array([], dtype=np.int16) # Ritorna array vuoto se durata troppo breve
		# Usa float64 per tempo e fase per precisione
		t = np.linspace(0, duration, N, endpoint=False, dtype=np.float64)
		# Forme d'onda via scipy.signal (output in [-1, 1])
		if wv == 1:  # Sine
			signal_float = np.sin(2 * np.pi * pitch * t)
		elif wv == 2:  # Square
			signal_float = signal.square(2 * np.pi * pitch * t)
		elif wv == 3:  # Triangle (width=0.5)
			signal_float = signal.sawtooth(2 * np.pi * pitch * t, width=0.5)
		else:  # Sawtooth (width=1)
			signal_float = signal.sawtooth(2 * np.pi * pitch * t, width=1)
		signal_float = signal_float.astype(np.float32) # Converti a float32 per audio
		# Applica Fade In/Out
		fade_samples = int(round(fs * ms / 1000.0)) # Arrotonda campioni fade
		# Condizione robusta per sovrapposizione fade
		if fade_samples > 0 and fade_samples <= N // 2:
			ramp = np.linspace(0, 1, fade_samples, dtype=np.float32)
			signal_float[:fade_samples] *= ramp
			signal_float[-fade_samples:] *= ramp[::-1] # Usa slicing negativo per l'ultimo pezzo
		# Applica volume e converti a int16
		# Clipping prima della conversione int16
		signal_float = np.clip(signal_float * vol, -1.0, 1.0)
		return (signal_float * 32767.0).astype(np.int16)
	def generate_silence(duration):
		# Arrotonda qui per il numero di campioni
		N = int(round(fs * duration))
		return np.zeros(N, dtype=np.int16) if N > 0 else np.array([], dtype=np.int16)
	# --- Assemblaggio Sequenza (invariato) ---
	segments = []
	words = msg.lower().split()
	for w_idx, word in enumerate(words):
		# Usa una stringa per accumulare le lettere valide invece di una lista
		valid_letters = "".join(ch for ch in word if ch in MORSE_MAP)
		for l_idx, letter in enumerate(valid_letters):
			code = MORSE_MAP.get(letter) # Usa .get() per sicurezza? No, già filtrato.
			if not code: continue # Salta se per qualche motivo non c'è codice (non dovrebbe succedere)
			for s_idx, symbol in enumerate(code):
				if symbol == '.':
					segments.append(generate_tone(dot_duration))
				elif symbol == '-':
					segments.append(generate_tone(dash_duration))
				# Aggiungi gap intra-simbolo solo se non è l'ultimo simbolo
				if s_idx < len(code) - 1:
					segments.append(generate_silence(intra_gap))
			# Aggiungi gap tra lettere solo se non è l'ultima lettera
			if l_idx < len(valid_letters) - 1:
				segments.append(generate_silence(letter_gap))
		# Aggiungi gap tra parole solo se non è l'ultima parola
		if w_idx < len(words) - 1:
			# Controlla se la parola precedente non era solo spazi o caratteri ignorati
			if valid_letters or any(ch in MORSE_MAP for ch in words[w_idx+1]):
				segments.append(generate_silence(word_gap))
	# --- Concatenazione e Aggiunta Silenzio Finale ---
	audio = np.concatenate(segments) if segments else np.array([], dtype=np.int16)
	if audio.size > 0: # Aggiungi solo se c'è audio
		silence_samples_end = int(round(fs * 0.005)) # Es. 5ms di silenzio finale
		if silence_samples_end > 0:
			final_silence = np.zeros(silence_samples_end, dtype=np.int16)
			audio = np.concatenate((audio, final_silence))
	# --- Calcolo rwpm (con gestione divisione per zero robusta) ---
	rwpm = wpm # Default se pesi standard o nessun elemento contato
	if (l, s, p) != (30, 50, 50):
		dots = dashes = intra_gaps = letter_gaps = word_gaps = 0
		words_list = msg.lower().split()
		processed_letters_count = 0 # Contatore per gestire gaps
		for w_idx, w in enumerate(words_list):
			current_word_letters = 0
			code_lengths_in_word = []
			for letter in w:
				if letter in MORSE_MAP:
					code = MORSE_MAP[letter]
					if code: # Ignora spazi o caratteri mappati a stringa vuota
						dots += code.count('.')
						dashes += code.count('-')
						code_len = len(code)
						if code_len > 1:
							intra_gaps += (code_len - 1)
						code_lengths_in_word.append(code_len)
						current_word_letters += 1
			if current_word_letters > 1:
				letter_gaps += (current_word_letters - 1)
			processed_letters_count += current_word_letters
			# Aggiungi word gap solo se la parola conteneva elementi e non è l'ultima
			if current_word_letters > 0 and w_idx < len(words_list) - 1:
				# E controlla anche se la parola successiva contiene elementi
				if any(ch in MORSE_MAP and MORSE_MAP[ch] for ch in words_list[w_idx+1]):
					word_gaps += 1
		# Calcola durate totali (in unità di dot)
		# Durata standard: 1 (dot) + 1 (gap) = 2, 3 (dash) + 1 (gap) = 4
		# Gap tra lettere = 3, Gap tra parole = 7
		# L'unità base è la durata del dot standard (T * p/50 dove p=50)
		standard_total_units = dots + 3*dashes + intra_gaps + 3*letter_gaps + 7*word_gaps
		# Durata attuale con pesi
		actual_dot_units = p / 50.0
		actual_dash_units = 3.0 * (l / 30.0)
		actual_intra_gap_units = s / 50.0
		actual_letter_gap_units = 3.0 * (s / 50.0)
		actual_word_gap_units = 7.0 * (s / 50.0)
		actual_total_units = (dots * actual_dot_units) + \
							 (dashes * actual_dash_units) + \
							 (intra_gaps * actual_intra_gap_units) + \
							 (letter_gaps * actual_letter_gap_units) + \
							 (word_gaps * actual_word_gap_units)
		# Calcola rapporto e rwpm solo se ci sono state durate
		if standard_total_units > 0 and actual_total_units > 0:
			ratio = actual_total_units / standard_total_units
			rwpm = wpm / ratio
		elif standard_total_units == 0 and actual_total_units == 0:
			rwpm = wpm # Messaggio vuoto, rwpm è uguale a wpm nominale
		else:
			# Caso anomalo (es. solo spazi?), imposta rwpm a wpm o 0?
			# Manteniamo wpm per ora, ma potrebbe essere indice di errore input.
			rwpm = wpm
			print("CWzator Warning: Calcolo rwpm anomalo, possibile input solo con spazi?", file=sys.stderr)
	# --- Classe PlaybackHandle (invariata ma ora riceve audio con silenzio finale) ---
	class PlaybackHandle:
		def __init__(self, audio_data, sample_rate):
			self.audio_data = audio_data
			self.sample_rate = sample_rate
			self.stream = None
			self.is_playing = threading.Event() # Usa Event per thread-safety
			self._thread = None # Riferimento al thread
		def _playback_target(self):
			"""Target function per il thread di riproduzione."""
			self.is_playing.set() # Segnala inizio riproduzione
			stream = None # Inizializza per blocco finally
			try:
				with sd.OutputStream(
					samplerate=self.sample_rate, channels=1, dtype=np.int16,
					blocksize=BLOCK_SIZE, latency='low'
				) as stream:
					# Salva riferimento allo stream *dopo* che è stato creato con successo
					self.stream = stream
					# Scrittura a blocchi, controllando il flag ad ogni blocco
					for i in range(0, len(self.audio_data), BLOCK_SIZE):
						if not self.is_playing.is_set(): # Controlla l'evento
							# print("Debug: Stop richiesto durante la riproduzione.")
							stream.stop() # Prova a fermare lo stream corrente
							break
						block = self.audio_data[i:min(i + BLOCK_SIZE, len(self.audio_data))]
						stream.write(block)
					# Se il loop finisce normalmente, attendi che lo stream finisca l'output bufferizzato
					if self.is_playing.is_set():
						# print("Debug: Loop terminato, attendo stream.close() implicito.")
						pass # 'with' gestisce la chiusura e l'attesa implicita
			except sd.PortAudioError as pae:
				print(f"CWzator Playback PortAudioError: {pae}", file=sys.stderr)
			except Exception as e:
				print(f"CWzator Playback Error: {e}", file=sys.stderr)
			finally:
				# print("Debug: Uscita blocco try/finally _playback_target.")
				self.is_playing.clear() # Segnala fine riproduzione o errore
				self.stream = None # Rilascia riferimento allo stream
		def play(self):
			"""Avvia la riproduzione in un thread separato."""
			if not self.is_playing.is_set() and self.audio_data.size > 0:
				# Crea e avvia il thread solo se non sta già suonando e c'è audio
				self._thread = threading.Thread(target=self._playback_target)
				self._thread.daemon = False # Assicura non-daemon
				self._thread.start()
			# else: print("Debug: Play chiamato ma già in esecuzione o audio vuoto.")
		def wait_done(self):
			"""Attende la fine della riproduzione corrente."""
			# Attende che l'evento is_playing sia clear O che il thread termini
			if self._thread is not None and self._thread.is_alive():
				# print("Debug: wait_done chiamato, joining thread...")
				self._thread.join()
			# print("Debug: wait_done terminato.")
		def stop(self):
			"""Richiede l'interruzione della riproduzione."""
			# print("Debug: stop richiesto.")
			self.is_playing.clear() # Segnala al loop di playback di fermarsi
			# Nota: l'interruzione effettiva dipende da quanto velocemente il loop
			# controlla l'evento e da quanto tempo impiega stream.stop().
			# Non chiudiamo lo stream qui, il blocco 'with' lo farà.
	# --- Creazione Oggetto e Avvio Playback (Logica Originale) ---
	play_obj = PlaybackHandle(audio, fs)
	# Avvia la riproduzione nel thread interno all'oggetto
	play_obj.play() # Il metodo play ora gestisce l'avvio del thread
	# --- Salvataggio File (invariato) ---
	if file:
		filename = f"cwapu Morse recorded at {datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
		try:
			with wave.open(filename, 'wb') as wf:
				wf.setnchannels(1) # Mono
				wf.setsampwidth(2) # 16-bit
				wf.setframerate(fs)
				wf.writeframes(audio.tobytes())
			# print(f"CWzator: Audio salvato in {filename}")
		except Exception as e:
			print(f"CWzator Error durante salvataggio file: {e}", file=sys.stderr)
	# --- Gestione Sync (usa wait_done dell'oggetto) ---
	if sync:
		play_obj.wait_done() # Usa il metodo dell'oggetto per attendere
	# --- Ritorno Oggetto e rwpm ---
	return play_obj, rwpm

class Mazzo:
	'''
	V5.1 - aprile 2025 b Gabriele Battaglia & Gemini 2.5
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
		self.pescate = [] # Carte attualmente pescate / in gioco
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
		Pesca carte dal mazzo principale. Se il mazzo è vuoto e ci sono scarti,
		li rimescola automaticamente nel mazzo prima di pescare.
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
		# Controlla se il mazzo è vuoto e se ci sono scarti da rimescolare
		if not self.carte and self.scarti:
			# Rimescola gli scarti nel mazzo
			self.carte.extend(self.scarti)
			self.scarti = []
			self.mescola_mazzo() # Mescola il mazzo appena riempito
		num_carte_nel_mazzo = len(self.carte)
		num_da_pescare = min(quante, num_carte_nel_mazzo)
		carte_pescate_ora = []
		if num_da_pescare > 0:
			# Pesca dalla fine per efficienza O(1) con pop()
			# Se si preferisce pescare dall'inizio (pop(0)), cambiare qui.
			# Assumiamo che il mazzo sia già stato mescolato.
			for _ in range(num_da_pescare):
				carte_pescate_ora.append(self.carte.pop()) # Pesca dalla fine
			# Se si pesca dall'inizio:
			# carte_pescate_ora = self.carte[:num_da_pescare]
			# self.carte = self.carte[num_da_pescare:]
		# Aggiunge le carte pescate alla lista self.pescate per tracciamento
		self.pescate.extend(carte_pescate_ora)
		# Non restituisce messaggi di avviso, il chiamante verifica len(risultato)
		return carte_pescate_ora
	def scarta_carte(self, carte_da_scartare):
		'''
		Sposta una lista di carte (presumibilmente dalla mano di un giocatore,
		quindi da self.pescate) nella pila degli scarti (self.scarti).
		Parametri:
		- carte_da_scartare (list[Carta]): Lista di oggetti Carta da spostare negli scarti.
		Ritorna:
		- str: Messaggio che indica quante carte sono state effettivamente trovate e scartate.
		'''
		scartate_count = 0
		non_trovate_count = 0
		carte_da_rimuovere_da_pescate = []
		# Crea un set degli id delle carte da scartare per ricerca efficiente
		ids_da_scartare = {carta.id for carta in carte_da_scartare}
		pescate_dict = {carta.id: carta for carta in self.pescate} # Mappa id->carta per accesso rapido
		carte_effettivamente_scartate = []
		for carta_id in ids_da_scartare:
			if carta_id in pescate_dict:
				carta = pescate_dict[carta_id]
				carte_effettivamente_scartate.append(carta)
				carte_da_rimuovere_da_pescate.append(carta)
				scartate_count += 1
			else:
				# Potrebbe essere utile tracciare quali carte non sono state trovate
				# Ma per ora contiamo solo
				non_trovate_count += 1
		# Aggiorna le liste solo dopo aver iterato
		if carte_da_rimuovere_da_pescate:
			self.pescate = [c for c in self.pescate if c not in carte_da_rimuovere_da_pescate]
			self.scarti.extend(carte_effettivamente_scartate)
		msg = f"Scartate {scartate_count} carte."
		if non_trovate_count > 0:
			msg += f" {non_trovate_count} carte non trovate in 'pescate'."
		return msg
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
		condizione = lambda carta: carta.seme_id in semi_id_da_rimuovere
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
		condizione = lambda carta: carta.valore in valori_da_rimuovere
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
		condizione = lambda carta: carta.nome == "Jolly"
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
										f"Pescate: {len(self.pescate)} carte | "
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

def percent(base=50.0, confronto=100.0, successo=False):
	'''V1.0 thu 28, september 2023
	Rx base e confronto e calcola la percentuale di base rispetto a confronto
	rx anche successo: se vero, estrae un numero casuale fra 0 e 100
	se il numero estratto è uguale o inferiore alla percentuale, restituisce vero, altrimenti falso
	se successo è vero: restituisce la percentuale e una booleana che indica successo o fallimento
	se sucesso è falso: restituisce solo la percentuale
	'''
	from random import uniform
	if not isinstance(base,float): base=float(base)
	if not isinstance(confronto,float): confronto=float(confronto)
	perc=(base/confronto)*100
	if not successo:
		return perc
	else:
		x=uniform(0,100)
		if x<=perc: return perc, True
		else: return perc, False

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
	'''V5.0 12/02/2025 by Gabriele Battaglia and ChatGPT o3-mini-high.
	Attende per il numero di secondi specificati
	se tempo e' scaduto, o si preme un tasto, esce.
	prompt e' il messaggio da mostrare.
	Restituisce il tasto premuto.
	'''
	import sys, time, os
	if prompt:
		print(prompt, end="", flush=True)
	start_time = time.time()
	if os.name == 'nt':
		import msvcrt
		while time.time() - start_time <= attesa:
			if msvcrt.kbhit():
				return msvcrt.getwch()
		return ''
	else:
		import select, tty, termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setcbreak(fd)
			while time.time() - start_time <= attesa:
				rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
				if rlist:
					return sys.stdin.read(1)
			return ''
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def gridapu(x=0.0, y=0.0, num=10):
	'''GRIDAPU V1.2 - Author unknown, and kindly find on the net by IU1FIG Diego Rispoli.
	Translated from Java by IZ4APU Gabriele Battaglia.
	It Receives long, lat in float and how many digits (num)
	It returns the locator as string.
	'''
	if type(y) != float or type(x) != float:
		print('Lat or Lon wrong type!')
		return''
	from string import ascii_lowercase as L
	from string import ascii_uppercase as U
	from string import digits as D
	import math
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
	sonify V7.1 - 11 luglio 2025 - Gabriele Battaglia eChatGPT O1, Gemini 2.5 Pro
	Sonifies a list of float data.
	Parameters:
	  data_list: List of float (5 <= len <= 500000)
	  duration: Total duration in seconds (e.g., 2.58)
	  ptm: If True, applies glissando (continuous portamento)
	  vol: Volume factor (0.1 <= vol <= 1.0)
	  file: If True, saves the audio to sonification[datetime].wav
	Returns immediately (non-blocking playback).
	"""
	import numpy as np
	import sounddevice as sd
	import wave
	n = len(data_list)
	if n < 5 or n > 500000:
		print("sonify: data_list length out of range")
		return
	try:
		data_list = [float(v) for v in data_list]
	except ValueError:
		return
	vol = max(0.1, min(vol, 1.0))
	data_min = min(data_list)
	data_max = max(data_list)
	freq_min = 65.41
	freq_max = 4186.01
	if data_max - data_min == 0:
		frequencies = [(freq_min+freq_max)/2]*n
	else:
		frequencies = [freq_min+(v-data_min)*(freq_max-freq_min)/(data_max-data_min) for v in data_list]
	sample_rate = 44100
	total_samples = int(duration*sample_rate)
	if total_samples <= 0:
		return
	t = np.linspace(0, duration, total_samples, endpoint=False)
	if ptm:
		segment_times = np.linspace(0, duration, n, endpoint=True)
		freq_array = np.interp(t, segment_times, frequencies, left=frequencies[0], right=frequencies[-1])
	else:
		indices = np.floor(np.linspace(0, n, total_samples, endpoint=False)).astype(int)
		freq_array = np.array(frequencies)[indices]
	phase = 2.0*np.pi*np.cumsum(freq_array/sample_rate)
	audio_signal = np.sin(phase)*vol
	fade_duration_sec = 0.01
	fade_samples = int(round(fade_duration_sec * sample_rate))
	fade_samples = min(fade_samples, total_samples // 2)
	fade_in = np.sin(np.linspace(0, np.pi / 2, fade_samples))
	fade_out = np.sin(np.linspace(np.pi / 2, 0, fade_samples)) # o np.cos(np.linspace(0, np.pi/2, fade_samples))
	audio_signal[:fade_samples] *= fade_in
	audio_signal[-fade_samples:] *= fade_out
	pan = np.linspace(-1.0, 1.0, total_samples)
	pan_angle = (pan + 1.0) * np.pi / 4.0
	left_gain = np.cos(pan_angle)
	right_gain = np.sin(pan_angle)
	left = audio_signal * left_gain
	right = audio_signal * right_gain
	audio_stereo = np.column_stack((left, right))
	audio_stereo_int16 = (audio_stereo*32767).astype(np.int16)
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

def Acusticator(score, kind=1, adsr=[.002, 0, 100, .002], fs=22050, sync=False):
	"""
	V5.8 di giovedì 27 marzo 2025. Gabriele Battaglia e Gemini 2.5
	Crea e riproduce (in maniera asincrona) un segnale acustico in base allo score fornito,
	utilizzando sounddevice per la riproduzione e applicando un envelope ADSR definito in termini
	di percentuali della durata della nota.
	Parametri:
	 - score: lista di valori in multipli di 4, in cui ogni gruppo rappresenta:
	     * nota (string|float): una nota musicale (es. "c4", "c#4"), un valore in Hz oppure "p" per pausa.
	     * dur (float): durata in secondi.
	     * pan (float): panning stereo da -1 (sinistra) a 1 (destra).
	     * vol (float): volume da 0 a 1.
	 - kind (int): tipo di onda (1=sinusoide, 2=quadra, 3=triangolare, 4=dente di sega).
	 - adsr: lista di quattro valori [a, d, s, r] in percentuali (0 a 100) dove:
	         • a = percentuale della durata della nota destinata all'attacco (rampa da 0 a 1),
	         • d = percentuale destinata al decadimento (rampa da 1 al livello di sustain),
	         • s = livello di sustain (valore percentuale volume, che verrà scalato in un numero frazionario da 0 a 1),
	         • r = percentuale destinata al rilascio (rampa da sustain a 0).
	         La fase di sustain occupa il tempo rimanente, cioè: 100 - (a + d + r) in percentuale della durata totale.
	         È richiesto che a + d + r ≤ 100.
	         Il valore di default è [.005, 0.0, 100.0, .005].
	 - fs (int): frequenza di campionamento (default 44100 Hz).
	Se sync è False la riproduzione avviene in background, restituendo subito il controllo al chiamante.
	"""
	import numpy as np
	import sounddevice as sd
	import threading
	from scipy import signal
	import re, sys
	def note_to_freq(note):
		if isinstance(note, (int, float)): return float(note)
		if isinstance(note, str):
			note_lower = note.lower()
			if note_lower == 'p': return None
			match = re.match(r"^([a-g])([#b]?)(\d)$", note_lower)
			if not match: raise ValueError(f"Formato nota non valido: '{note}'.")
			note_letter, accidental, octave_str = match.groups()
			try: octave = int(octave_str)
			except ValueError: raise ValueError(f"Numero ottava non valido: '{octave_str}'")
			note_base = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
			semitone = note_base[note_letter]
			if accidental == '#': semitone += 1
			elif accidental == 'b': semitone -= 1
			midi_num = 12 + semitone + 12 * octave
			freq = 440.0 * (2.0 ** ((midi_num - 69) / 12.0))
			return freq
		else: raise TypeError(f"Tipo nota non riconosciuto: {type(note)}.")
	BLOCK_SIZE = 256 # Per il loop di scrittura in play_audio
	SAFETY_BUFFER_SECONDS = 0.001 # Buffer di silenzio alla fine (in play_audio)
	if len(adsr) != 4: raise ValueError("ADSR deve contenere 4 valori")
	a_pct, d_pct, s_level_pct, r_pct = adsr
	if not all(0 <= val <= 100 for val in adsr): raise ValueError("Valori ADSR devono essere tra 0 e 100.")
	if a_pct + d_pct + r_pct > 100.001: raise ValueError(f"Somma A%({a_pct})+D%({d_pct})+R%({r_pct}) > 100 non permessa.")
	attack_frac = a_pct / 100.0
	decay_frac = d_pct / 100.0
	sustain_level = s_level_pct / 100.0
	release_frac = r_pct / 100.0
	segments = []
	for i in range(0, len(score), 4):
		try:
			note_param, dur, pan, vol = score[i:i+4]
			dur, pan, vol = float(dur), float(pan), float(vol)
		except (IndexError, ValueError) as e:
			print(f"Acusticator Warn: Parametri {i} errati. Ignoro. {e}", file=sys.stderr)
			continue
		if dur <= 0: continue # Ignora durata non positiva
		freq = note_to_freq(note_param)
		total_note_samples = int(round(dur * fs))
		if total_note_samples == 0: continue # Ignora durata troppo breve
		if freq is None: # Pausa
			stereo_segment = np.zeros((total_note_samples, 2), dtype=np.float32)
		else: # Nota
			t = np.linspace(0, dur, total_note_samples, endpoint=False)
			if kind == 2: wave = signal.square(2 * np.pi * freq * t)
			elif kind == 3: wave = signal.sawtooth(2 * np.pi * freq * t, 0.5)
			elif kind == 4: wave = signal.sawtooth(2 * np.pi * freq * t)
			else: wave = np.sin(2 * np.pi * freq * t)
			wave = wave.astype(np.float32)
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
			wave *= envelope * vol
			stereo_segment = np.zeros((total_note_samples, 2), dtype=np.float32)
			pan_clipped = np.clip(pan, -1.0, 1.0); pan_angle = pan_clipped * (np.pi / 4.0)
			left_gain = np.cos(pan_angle + np.pi / 4.0); right_gain = np.sin(pan_angle + np.pi / 4.0)
			stereo_segment[:, 0] = wave * left_gain
			stereo_segment[:, 1] = wave * right_gain
		segments.append(stereo_segment)
	if not segments: return
	full_signal_float = np.concatenate(segments, axis=0)
	full_signal_float = np.clip(full_signal_float, -1.0, 1.0)
	audio_data_int16 = (full_signal_float * 32767.0).astype(np.int16)
	def play_audio():
		try:
			with sd.OutputStream(samplerate=fs, channels=2, dtype=np.int16,
								 blocksize=BLOCK_SIZE, latency='low') as stream:
				for i in range(0, len(audio_data_int16), BLOCK_SIZE):
					block = audio_data_int16[i:min(i + BLOCK_SIZE, len(audio_data_int16))]
					stream.write(block)
				silence_samples = int(fs * SAFETY_BUFFER_SECONDS)
				if silence_samples > 0:
					silence = np.zeros((silence_samples, 2), dtype=np.int16)
					stream.write(silence)
				stream.stop()
		except sd.PortAudioError as pae:
			print(f"Acusticator Playback PortAudioError: {pae}", file=sys.stderr)
		except Exception as e:
			print(f"Acusticator Playback Error: {e}", file=sys.stderr)
	thread = threading.Thread(target=play_audio)
	thread.start()
	if sync:
		thread.join()
	return

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
	except IOError:
		print("Attenzione, file della guida mancante.\n\tRichiedere il file all'autore dell'App.")
	return

def menu(d={}, p="> ", ntf="Scelta non valida", show=True, show_only=False, keyslist=True, full_keyslist=False, pager=20, show_on_filter=True, numbered=False):
	"""V3.13 – martedì 8 luglio 2025 - Gabriele Battaglia & Gemini 2.5
	Parametri:
		d: dizionario con coppie chiave:descrizione
		p: prompt di default se keyslist è False
		numbered: mostra numeri al posto delle chiavi
		ntf: messaggio in caso di filtro vuoto o input ambiguo
		show: se True, mostra il menu iniziale completo prima del prompt
		show_only: se True, mostra il menu completo e termina
		keyslist: se True, il prompt è generato dalle chiavi filtrate
		full_keyslist: se True (solo se keyslist True), mostra le chiavi complete (con iniziali maiuscole),
			altrimenti mostra solo l'abbreviazione necessaria (tutto in maiuscolo)
		pager: numero di elementi da mostrare per pagina nel pager
			esc nel pager termina subito la paginazione
		show_on_filter: se True, visualizza la lista delle coppie candidate ad ogni aggiornamento del filtro
						(solo dopo che l'utente ha iniziato a digitare, se show=False)
		?   nel prompt mostra il pager con le opzioni filtrate correnti
	Restituisce:
		la chiave scelta oppure None se annullato (ESC o Invio su input vuoto)
	"""
	import sys, time, os
	def key(prompt=""):
		"""Legge un singolo carattere dalla console senza bisogno di Invio."""
		print(prompt, end='', flush=True)
		if os.name == 'nt':
			import msvcrt # Import specifico per Windows
			ch = msvcrt.getwch()
			# Gestione caratteri speciali Windows (come nel codice precedente)
			if ch == '\x08': return ch # Backspace
			if ch == '\r': return ch   # Enter
			if ch == '\x1b': return ch # ESC
			if ch == '?': return ch    # Carattere speciale ?
			if ord(ch) == 127: return '\x08' # Gestisce DEL come Backspace
			if ch in ('\x00', '\xe0'): # Tasti speciali (Frecce, Canc, etc.)
				msvcrt.getwch() # Leggi e ignora il secondo byte
				return '\x00' # Restituisce un codice nullo per ignorarli
			return ch # Carattere normale
		else:
			# Import specifici per Unix-like
			import select, tty, termios
			fd = sys.stdin.fileno()
			old_settings = termios.tcgetattr(fd)
			try:
				tty.setcbreak(fd) # Imposta la modalità cbreak
				# Gestione caratteri speciali Unix (come nel codice precedente)
				ch = sys.stdin.read(1)
				if ch == '\x1b': # ESC o sequenza speciale
					r, _, _ = select.select([sys.stdin], [], [], 0.05)
					if r:
						extra = sys.stdin.read(2) # Leggi resto sequenza (es. freccia)
						return '\x00' # Ignora sequenze non gestite
					else:
						return '\x1b' # Solo ESC
				elif ord(ch) == 127: # Backspace (DEL)
					return '\x08'
				elif ch in ['\n', '\r']: # Invio
					return '\r' # Normalizza a \r
				else:
					return ch # Altro carattere
			finally:
				termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) # Ripristina
	def Mostra(l, pager):
		"""Visualizza una lista di elementi usando un pager."""
		count = 0
		total = len(l)
		if total == 0:
			print("\n" + ntf)
			return True
		print("\n--- Menu ---")
		for j in l:
			desc = d.get(j, "N/A")
			print(f"- ({j}) -- {desc};")
			count += 1
			if pager > 0 and count % pager == 0 and count < total:
				prompt_pager = f"--- [Pag: {int(count/pager)}] ({count-pager+1}-{count} di {total}) Premi Invio per continuare, ESC per uscire ---"
				ch_pager = key(prompt_pager) # Usa la funzione key interna
				print()
				if ch_pager == '\x1b': # ESC
					print("--- Exit from paging ---")
					return False
		print(f"---------- [End of list] ({count}/{total}) ----------")
		return True
	def minimal_keys(keys):
		"""Calcola le abbreviazioni minime univoche."""
		res = {}
		keys_lower = {key: key.lower() for key in keys}
		for key_item in keys:
			key_str = key_item.lower()
			n = len(key_str)
			found_abbr = None
			for length in range(1, n + 1):
				for i in range(n - length + 1):
					candidate = key_str[i:i + length]
					is_unique = True
					for other_key in keys:
						if other_key == key_item:
							continue
						if candidate in keys_lower[other_key]:
							is_unique = False
							break
					if is_unique:
						found_abbr = candidate.upper()
						break
				if found_abbr is not None:
					break
			if found_abbr is None:
				found_abbr = key_item.upper()
			res[key_item] = found_abbr
		return res
	def Listaprompt(keys_list, full):
		"""Genera la stringa del prompt basata sulle chiavi filtrate."""
		if not keys_list:
			return ">"
		if full:
			formatted = [k.capitalize() for k in keys_list]
		else:
			abbrev = minimal_keys(keys_list) # Usa la funzione minimal_keys interna
			formatted = [abbrev[k] for k in keys_list]
		return "\n(" + ", ".join(formatted) + ")>"
	def valid_match(key_item, sub):
		"""Controlla se 'sub' è una sottostringa valida di 'key_item'."""
		kl = key_item.lower()
		sl = sub.lower()
		if sl == "":
			return True
		return sl in kl
	# --- Logica Principale del Menu ---
	if numbered:
		keys_numerate = list(d.keys())
		if not keys_numerate:
			print("No available options.")
			return None
		while True:
			for i, k in enumerate(keys_numerate, 1):
				print(f"[{i}] -- {d[k]}")
			scelta = input(f"\n{p} (1-{len(keys_numerate)})> ")
			if not scelta:
				return None
			try:
				num_scelta = int(scelta)
				if 1 <= num_scelta <= len(keys_numerate):
					return keys_numerate[num_scelta - 1]
				else:
					print(f"\n{ntf} out of range: 1-{len(keys_numerate)}.")
			except ValueError:
				# Messaggio di errore se l'input non è un numero
				print(f"\n{ntf} not a number.")
			time.sleep(1.5) # Pausa per permettere all'utente di leggere l'errore
	orig_keys = list(d.keys())
	current_input = ""
	last_displayed = None
	# Gestione casi limite iniziali
	if not d:
		print("No options available.")
		return None
	if len(d) == 1 and not show_only:
		return orig_keys[0]
	# Gestione show_only
	if show_only:
		Mostra(orig_keys, pager) # Usa Mostra interna
		return None
	# Gestione show=True iniziale
	if show:
		if not Mostra(orig_keys, pager): # Usa Mostra interna, gestisci ESC nel pager iniziale
			return None # Se l'utente esce subito dal pager iniziale
		last_displayed = orig_keys[:]
	# --- Ciclo Principale di Input/Filtro ---
	while True:
		# 1. Filtra
		filtered = [k for k in orig_keys if valid_match(k, current_input)] # Usa valid_match interna
		# 2. Gestisci filtro vuoto
		if not filtered:
			print("\n" + ntf)
			current_input = ""
			filtered = orig_keys[:]
			# Non mostrare nulla qui, aspetta input o '?'
		# 3. Gestisci risultato unico (solo se si è digitato qualcosa)
		if len(filtered) == 1 and current_input != "":
			print()
			return filtered[0]
		# 4. Mostra su filtro (se richiesto E si è digitato E lista cambiata)
		if show_on_filter and current_input != "" and filtered != last_displayed:
			print("\n-----------------------")
			if not Mostra(filtered, pager): # Usa Mostra interna
				last_displayed = filtered[:]
				continue # ESC nel pager, salta prompt
			last_displayed = filtered[:]
		# 5. Prepara il prompt
		if keyslist:
			prompt_str = Listaprompt(filtered, full_keyslist) # Usa Listaprompt interna
		else:
			prompt_str = p
		full_prompt = " " + prompt_str + current_input
		# 6. Ottieni input
		user_char = key(full_prompt) # Usa key interna
		# 7. Processa input
		if user_char in ['\r', '\n']: # Invio
			print()
			if current_input == "":
				return None # Invio su vuoto = Annulla
			else:
				match_exact = None
				for k in orig_keys:
					if k.lower() == current_input.lower():
						match_exact = k
						break
				if match_exact:
					return match_exact # Match esatto trovato
				if len(filtered) == 1:
					return filtered[0] # Unico elemento filtrato
				elif len(filtered) > 1:
					print("\n--- Press '?' for help. ---")
					if filtered != last_displayed:
						if not Mostra(filtered, pager): # Usa Mostra interna
							last_displayed = filtered[:]
							continue # ESC nel pager
						last_displayed = filtered[:]
				# else: # Caso filtro vuoto già gestito sopra (teoricamente)
				#	 print("\n" + ntf)
				#	 current_input = ""
		elif user_char == '\x1b': # ESC
			print()
			return None
		elif user_char == '?':
			if not Mostra(filtered, pager): # Usa Mostra interna
				last_displayed = filtered[:]
				continue # ESC nel pager
			last_displayed = filtered[:]
		elif user_char == '\x08': # Backspace
			if current_input:
				current_input = current_input[:-1]
				print('\b \b', end='', flush=True) # Feedback visivo backspace
		elif user_char == '\x00': # Tasto speciale ignorato
			pass
		else:
			# Carattere normale
			print(user_char, end='', flush=True) # Feedback visivo carattere
			current_input += user_char
			# Controllo rapido risultato unico/vuoto
			quick_filtered = [k for k in orig_keys if valid_match(k, current_input)]
			if len(quick_filtered) == 1:
				print()
				return quick_filtered[0] # Trovato unico, esci
			elif len(quick_filtered) == 0:
				print("\n" + ntf)
				# Cancella input visivo (tentativo) e logico
				# print(f"\r{' ' * len(full_prompt)}\r", end='')
				print("\r" + " " * len(full_prompt) + "\r", end='') # Sovrascrivi linea con spazi
				current_input = ""
				# Il ciclo ricomincerà e gestirà il reset completo
	# Raggiungibile solo in caso di errore imprevisto
	return None

def Scandenza(y=2100, m=1, g=1, h=0, i=0):
	'''
	V 1.0 del 15/12/2021
	Riceve anno, mese, giorno, ora e minuto e calcola la differenza con l'ADESSO. Quindi la ritorna
	'''
	from datetime import datetime
	from dateutil import relativedelta
	APP=datetime(y,m,g,h,i)
	NOW = datetime.today()
	ETA=relativedelta.relativedelta(APP, NOW)
	if ETA.years > 0:
		if ETA.years == 1: f = str(ETA.years)+" anno, "
		else: f = str(ETA.years)+" anni, "
	else: f = ""
	if ETA.months > 0:
		if ETA.months == 1: f += str(ETA.months)+" mese, "
		else: f += str(ETA.months)+" mesi, "
	if ETA.days > 0:
		if ETA.days == 1: f += str(ETA.days)+" giorno, "
		else: f += str(ETA.days)+" giorni, "
	if ETA.hours > 0:
		if ETA.hours == 1: f += str(ETA.hours)+" ora e "
		else: f += str(ETA.hours)+" ore e "
	if ETA.minutes > 0:
		if ETA.minutes == 1: f += str(ETA.minutes)+" minuto."
		else: f += str(ETA.minutes)+" minuti"
	return(f)

def Vecchiume(y=1974, m=9, g=13, h=22, i=10):
	'''
	Utility che calcola la differenza fra una data e l'ADESSO.
	V1.0 del 15/12 2018 Di Gabriele Battaglia
	Riceve anno, mese, giorno, ora e minuto e calcola la differenza con l'ADESSO. Quindi la ritorna'''
	from datetime import datetime
	from dateutil import relativedelta
	APP=datetime(y,m,g,h,i)
	NOW = datetime.today()
	ETA=relativedelta.relativedelta(NOW,APP)
	if ETA.years > 0:
		if ETA.years == 1: f = str(ETA.years)+" anno, "
		else: f = str(ETA.years)+" anni, "
	else: f = ""
	if ETA.months > 0:
		if ETA.months == 1: f += str(ETA.months)+" mese, "
		else: f += str(ETA.months)+" mesi, "
	if ETA.days > 0:
		if ETA.days == 1: f += str(ETA.days)+" giorno, "
		else: f += str(ETA.days)+" giorni, "
	if ETA.hours > 0:
		if ETA.hours == 1: f += str(ETA.hours)+" ora e "
		else: f += str(ETA.hours)+" ore e "
	if ETA.minutes > 0:
		if ETA.minutes == 1: f += str(ETA.minutes)+" minuto."
		else: f += str(ETA.minutes)+" minuti"
	return(f)

def Donazione():
    """
    V1.1 del 18 giugno 2025
    Mostra un messaggio di donazione con una probabilità del 20%
    nella lingua del sistema operativo (se supportata), altrimenti in inglese.
    Lingue supportate: Italiano, Portoghese, Inglese, Francese, Spagnolo, Tedesco, Russo, Cinese (semplificato), Giapponese, Arabo.
    """
    import random
    import locale
    import platform # Importiamo il modulo platform per un rilevamento più affidabile

    if random.randint(1, 100) <= 20:
        messaggi = {
            'it': "Se questo software ti è piaciuto, ti è stato utile, ti sei divertito ad usarlo, considera l'idea di offrirmi un caffè. Mi trovi su paypal come iz4apu@libero.it Grazie di cuore.",
            'en': "If you enjoyed this software, found it useful, or had fun using it, consider buying me a coffee. You can find me on PayPal at iz4apu@libero.it Thank you.",
            'pt': "Se você gostou deste software, o achou útil ou se divertiu usando-o, considere me pagar um café. Você pode me encontrar no PayPal em iz4apu@libero.it. Muito obrigado.",
            'fr': "Si vous avez aimé ce logiciel, l'avez trouvé utile ou vous êtes amusé en l'utilisant, envisagez de m'offrir un café. Vous pouvez me trouver sur PayPal à l'adresse iz4apu@libero.it Merci beaucoup.",
            'es': "Si te ha gustado este software, te ha resultado útil o te has divertido usándolo, considera la idea de invitarme a un café. Me puedes encontrar en PayPal como iz4apu@limero.it. Muchas gracias.",
            'de': "Wenn Ihnen diese Software gefallen hat, sie nützlich war oder Sie Spaß daran hatten, sie zu nutzen, ziehen Sie in Betracht, mir einen Kaffee auszugeben. Sie finden mich auf PayPal unter iz4apu@libero.it Vielen Dank.",
            'ru': "Если вам понравилась эта программа, она оказалась полезной или вы получили удовольствие от ее использования, рассмотрите возможность угостить меня кофе. Вы можете найти меня на PayPal по адресу iz4apu@libero.it Спасибо.",
            'zh': "如果您喜欢这款软件，觉得它有用，或者在使用过程中获得了乐趣，请考虑请我喝杯咖啡。您可以在PayPal上找到我：iz4apu@libero.it 谢谢。", # Cinese (semplificato)
            'ja': "このソフトウェアを楽しんだり、役立つと感じたり、楽しく使っていただけたなら、私にコーヒーをご馳走することを検討してください。PayPalでiz4apu@libero.itとして見つけることができます。ありがとうございます。",
            'ar': "إذا أعجبك هذا البرنامج، أو وجدته مفيدًا، أو استمتعت باستخدامه، ففكر في شراء قهوة لي. يمكنك العثور عليّ على PayPal على iz4apu@libero.it. شكرًا لك."
        }

        lingua_os = 'en' # Impostiamo l'inglese come predefinito

        try:
            # Tentiamo di ottenere la lingua del sistema operativo
            # `locale.getdefaultlocale()` è spesso più robusto su diversi sistemi operativi
            # rispetto a `locale.setlocale` seguito da `locale.getlocale`.
            lingua_os_completa, encoding = locale.getdefaultlocale()
            if lingua_os_completa:
                lingua_os = lingua_os_completa.split('_')[0].lower() # Prendiamo solo le prime due lettere e convertiamo in minuscolo
        except Exception as e:
            print(f"Errore nel rilevamento della lingua del sistema operativo: {e}")
            # Se c'è un errore, lingua_os rimane 'en'

        messaggio_da_mostrare = messaggi.get(lingua_os, messaggi['en'])
        print(messaggio_da_mostrare)

def polipo(domain='messages', localedir='locales', source_language='en'):
    """
    polipo V5.1 by Gabriele Battaglia and Gemini - 28/06/2025
    Versione autonoma e compatibile con PyInstaller.
    - Trova autonomamente le risorse (es. cartella 'locales').
    - Salva il file di configurazione della lingua accanto all'eseguibile o allo script.
    - Salva l'elenco delle lingue disponibili e mostra il menu se cambiano.
    - Non richiede funzioni esterne di supporto.
    """
    import sys
    import os
    import json
    import gettext
    import locale
    # Rileva se l'app è "congelata" (compilata con PyInstaller)
    is_frozen = getattr(sys, 'frozen', False)
    # LOGICA 1: Trovare il percorso delle RISORSE (dati come la cartella 'locales')
    if is_frozen:
        resources_base_path = sys._MEIPASS
    else:
        resources_base_path = os.getcwd()
    # LOGICA 2: Trovare il percorso di SALVATAGGIO (per il file.json)
    if is_frozen:
        config_save_path = os.path.dirname(sys.executable)
    else:
        config_save_path = os.getcwd()
    # Costruisce i percorsi completi
    localedir_abs = os.path.join(resources_base_path, localedir)
    selected_lang_file = os.path.join(config_save_path, 'selected_language.json')
    # --- Fine Blocco di Autonomia ---
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
            # Mostra il menu se l'elenco delle lingue è cambiato O se la lingua salvata non è più valida
            if set(saved_available_languages) != set(current_available_languages) or language_code not in current_available_languages:
                show_menu = True
                print("Info: List of available languages has changed. Please select again.")
    except (FileNotFoundError, json.JSONDecodeError):
        show_menu = True
    if show_menu:
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
            choice = input(f"Enter selection (1-{len(menu_options)}): ")
            if choice in menu_options:
                language_code = menu_options[choice]
                break
            else:
                print("Invalid choice. Please try again.")
        try:
            with open(selected_lang_file, 'w', encoding='utf-8') as f:
                # Salva sia la lingua scelta sia l'elenco corrente delle lingue
                config_data = {
                    'language_code': language_code,
                    'available_languages': current_available_languages
                }
                json.dump(config_data, f, indent=4)
            print(f"Info: Language '{language_code}' saved to '{selected_lang_file}' for future use.")
        except IOError as e:
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
