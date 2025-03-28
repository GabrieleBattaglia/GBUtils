'''
	GBUtils di Gabriele Battaglia (IZ4APU)
	Data concepimento: lunedì 3 febbraio 2020.
	Raccoglitore di utilità per i miei programmi.
	Spostamento su github in data 27/6/2024. Da usare come submodule per gli altri progetti.
	V41 di giovedì 27 marzo 2025
Lista utilità contenute in questo pacchetto
	Acusticator V5.8 di giovedì 27 marzo 2025. Gabriele Battaglia e Gemini 2.5
	base62 3.0 di martedì 15 novembre 2022
	CWzator V8.1 di giovedì 27 marzo 2025 - Gabriele Battaglia (IZ4APU), Claude 3.5, ChatGPT o3-mini-high, Gemini 2.5 Pro
	dgt Versione 1.10 di lunedì 24 febbraio 2025
	gridapu 1.2 from IU1FIG
	key V5.0 di mercoledì 12/02/2025 by Gabriele Battaglia and ChatGPT o3-mini-high.
	manuale 1.0.1 di domenica 5 maggio 2024
	Mazzo 4.6 - ottobre 2024 - By ChatGPT-o1 e Gabriele Battaglia
	menu V3.8 – mercoledì 19 marzo 2025 - Gabriele Battaglia e ChatGPT o3-mini-high
	percent V1.0 thu 28, september 2023
	Scadenza 1.0 del 15/12/2021
	sonify V7.0 - 23 marzo 2025 - Gabriele Battaglia eChatGPT O1
	Vecchiume 1.0 del 15/12/2018
'''
def CWzator(msg, wpm=35, pitch=550, l=30, s=50, p=50, fs=44100, ms=1, vol=0.5, wv=1, sync=False, file=False):
	"""
	V8.1 di giovedì 27 marzo 2025 - Gabriele Battaglia (IZ4APU), Claude 3.5, ChatGPT o3-mini-high, Gemini 2.5 Pro
		da un'idea originale di Kevin Schmidt W9CF
	Genera e riproduce l'audio del codice Morse dal messaggio di testo fornito.
	Parameters:
		msg (str): Messaggio di testo da convertire in Morse.
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
	if not isinstance(msg, str) or msg == "": print("CWzator Error: msg deve essere una stringa non vuota.", file=sys.stderr); return None, None
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
	# --- Mappa Morse (invariata) ---
	morse_map = {
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
	# --- Assemblaggio Sequenza (invariato) ---
	segments = []
	words = msg.lower().split()
	for w_idx, word in enumerate(words):
		# Usa una stringa per accumulare le lettere valide invece di una lista
		valid_letters = "".join(ch for ch in word if ch in morse_map)
		for l_idx, letter in enumerate(valid_letters):
			code = morse_map.get(letter) # Usa .get() per sicurezza? No, già filtrato.
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
			if valid_letters or any(ch in morse_map for ch in words[w_idx+1]):
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
				if letter in morse_map:
					code = morse_map[letter]
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
				if any(ch in morse_map and morse_map[ch] for ch in words_list[w_idx+1]):
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
	V4.6 - ottobre 2024 - By ChatGPT-o1 e Gabriele Battaglia
	Classe che rappresenta un mazzo di carte italiano o francese, con funzionalità per mescolare, pescare e manipolare le carte.
	'''
	def __init__(self, tipo=True, num_mazzi=1):
		'''
		Inizializza un mazzo di carte.
		Parametri:
		- tipo (bool): True per mazzo francese, False per mazzo italiano.
		- num_mazzi (int): Numero di mazzi da includere.
		'''
		self.tipo = tipo
		self.num_mazzi = num_mazzi
		self.carte = []
		self.scarti = []
		self.scarti_permanenti = []
		self.pescate = []
		self.CostruisciMazzo()
	def CostruisciMazzo(self):
		'''
		Costruisce il mazzo di carte in base al tipo e al numero di mazzi.
		'''
		semi_francesi = ["Cuori", "Quadri", "Fiori", "Picche"]
		semi_italiani = ["Bastoni", "Spade", "Coppe", "Denari"]
		valori_francesi = [("Asso", 1)] + [(str(i), i) for i in range(2, 11)] + [("Jack", 11), ("Regina", 12), ("Re", 13)]
		valori_italiani = [("Asso", 1)] + [(str(i), i) for i in range(2, 8)] + [("Fante", 8), ("Cavallo", 9), ("Re", 10)]
		valori_descrizione = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 11: 'J', 12: 'Q', 13: 'K'}
		semi_descrizione = {1: 'C', 2: 'Q', 3: 'F', 4: 'P', 5: 'B', 6: 'S', 7: 'C', 8: 'D'}
		num_carte_per_mazzo = 52 if self.tipo else 40
		self.carte = []
		for n in range(self.num_mazzi):
			if self.tipo:
				offset = n * num_carte_per_mazzo
				id_carta = offset + 1
				for seme in semi_francesi:
					for nome_valore, valore in valori_francesi:
						carta_data = [f"{nome_valore} di {seme}", valore, semi_francesi.index(seme) + 1, True, False, False]
						carta_data.append(valori_descrizione[valore] + semi_descrizione[semi_francesi.index(seme) + 1])
						self.carte.append((id_carta, carta_data))
						id_carta += 1
			else:
				offset = n * num_carte_per_mazzo
				id_carta = offset + 1
				for seme in semi_italiani:
					for nome_valore, valore in valori_italiani:
						carta_data = [f"{nome_valore} di {seme}", valore, semi_italiani.index(seme) + 1, True, False, False]
						carta_data.append(valori_descrizione[valore] + semi_descrizione[semi_italiani.index(seme) + 1])
						self.carte.append((id_carta, carta_data))
						id_carta += 1
	def MescolaMazzo(self, millisecondi):
		'''
		Mescola il mazzo per un periodo specificato.
		Parametri:
		- millisecondi (int): Durata del mescolamento in millisecondi.
		'''
		import random
		import time
		start_time = time.time()
		end_time = start_time + (millisecondi / 1000.0)
		while time.time() < end_time:
			random.shuffle(self.carte)
	def Pesca(self, quante=1):
		'''
		Pesca un numero specifico di carte dalla cima del mazzo.
		Parametri:
		- quante (int): Numero di carte da pescare.
		Ritorna:
		- Mazzo: Un nuovo oggetto Mazzo contenente le carte pescate.
		'''
		if quante < 0:
			raise ValueError("Il numero di carte da pescare deve essere non negativo.")
		mazzo_pescato = Mazzo(self.tipo)
		mazzo_pescato.carte = []
		for _ in range(quante):
			if not self.carte:
				break
			carta = self.carte.pop(0)
			carta[1][3] = False  # Non più nel mazzo principale
			carta[1][4] = True   # Pescata
			mazzo_pescato.carte.append(carta)
			self.pescate.append(carta)
		return mazzo_pescato
	def Rimescola(self):
		'''
		Rimette le carte scartate nel mazzo e mescola. Non reintegra le carte eliminate definitivamente.
		'''
		if not self.scarti:
			print("Non ci sono scarti da reintegrare nel mazzo.")
		else:
			print(f"Uniti {len(self.scarti)} scarti nel mazzo.")
			self.carte.extend(self.scarti)
			self.scarti = []
			for _, carta in self.carte:
				carta[3] = True  # Torna nel mazzo principale
				carta[5] = False  # Non più scartata
			self.MescolaMazzo(1000)
			print(f"{len(self.carte)} carte nel mazzo")
	def RimuoviSemi(self, semi_da_rimuovere):
		'''
		Rimuove dal mazzo tutte le carte con i semi specificati e le sposta negli scarti.
		Parametri:
		- semi_da_rimuovere (list): Lista di interi che rappresentano i semi da rimuovere (es. [1, 2]).
		'''
		carte_da_rimuovere = []
		for carta in self.carte:
			if carta[1][2] in semi_da_rimuovere:
				carta[1][3] = False  # Non nel mazzo principale
				carta[1][5] = True   # Scartata
				self.scarti.append(carta)
				carte_da_rimuovere.append(carta)
		for carta in carte_da_rimuovere:
			self.carte.remove(carta)
	def RimuoviValori(self, valori_da_rimuovere):
		'''
		Rimuove dal mazzo tutte le carte con i valori specificati e le sposta negli scarti permanenti.
		Parametri:
		- valori_da_rimuovere (list): Lista di interi che rappresentano i valori da rimuovere (es. [2, 3, 4, 5]).
		'''
		carte_da_rimuovere = []
		for carta in self.carte:
			if carta[1][1] in valori_da_rimuovere:
				carta[1][3] = False  # Non nel mazzo principale
				carta[1][5] = True   # Scartata
				self.scarti_permanenti.append(carta)  # Scarti permanenti
				carte_da_rimuovere.append(carta)
		for carta in carte_da_rimuovere:
			self.carte.remove(carta)
	def JollySi(self):
		'''
		Aggiunge i jolly al mazzo per ogni mazzo presente.
		'''
		if self.tipo:
			num_jolly_aggiunti = 0
			for n in range(self.num_mazzi):
				id_jolly1 = len(self.carte) + 1
				id_jolly2 = len(self.carte) + 2
				carta_jolly1 = ["Jolly", None, 0, True, False, False]
				carta_jolly2 = ["Jolly", None, 0, True, False, False]
				self.carte.append((id_jolly1, carta_jolly1))
				self.carte.append((id_jolly2, carta_jolly2))
				num_jolly_aggiunti += 2
		else:
			print("Questo tipo di mazzo non supporta i jolly.")
	def JollyNo(self):
		'''
		Rimuove tutti i jolly dal mazzo.
		'''
		carte_da_rimuovere = [carta for carta in self.carte if carta[1][0] == "Jolly"]
		for carta in carte_da_rimuovere:
			self.carte.remove(carta)
		print(f"Jolly rimossi dal mazzo. Totale jolly rimossi: {len(carte_da_rimuovere)}")
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
	sonify V7.0 - 23 marzo 2025 - Gabriele Battaglia eChatGPT O1
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
	fade_duration_sec = 0.002
	fade_samples = int(round(fade_duration_sec*sample_rate))
	fade_samples = min(fade_samples, total_samples//2)
	fade_in = np.linspace(0, 1, fade_samples)
	fade_out = np.linspace(1, 0, fade_samples)
	audio_signal[:fade_samples] *= fade_in
	audio_signal[-fade_samples:] *= fade_out
	pan = np.linspace(-1.0, 1.0, total_samples)
	left = audio_signal*((1.0-pan)/2.0)
	right = audio_signal*((1.0+pan)/2.0)
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
def menu(d={}, p="> ", ntf="Scelta non valida", show=False, show_only=False, keyslist=False, full_keyslist=True, pager=20, show_on_filter=True):
	"""V3.8 – mercoledì 19 marzo 2025 - Gabriele Battaglia e ChatGPT o3-mini-high
	Parametri:
		d: dizionario con coppie chiave:descrizione
		p: prompt di default se keyslist è False
		ntf: messaggio in caso di filtro vuoto
		show: se True, mostra il menu iniziale
		show_only: se True, mostra il menu e termina
		keyslist: se True, il prompt è generato dalle chiavi filtrate
		full_keyslist: se True (solo se keyslist True), mostra le chiavi complete (con iniziali maiuscole),
			altrimenti mostra solo l'abbreviazione necessaria (tutto in maiuscolo)
		pager: numero di elementi da mostrare per pagina nel pager
			esc nel pager termina subito la paginazione
		show_on_filter: se True, visualizza la lista delle coppie candidate ad ogni aggiornamento del filtro
		?	nel prompt mostra il pager
	Restituisce:
		la chiave scelta oppure None se annullato
	"""
	import sys, time, os
	if os.name!='nt':
		import select, tty, termios
	def key(prompt=""):
		print(prompt, end='', flush=True)
		if os.name=='nt':
			import msvcrt
			ch=msvcrt.getwch()
			return ch
		else:
			fd=sys.stdin.fileno()
			old_settings=termios.tcgetattr(fd)
			try:
				tty.setcbreak(fd)
				while True:
					r,_,_=select.select([sys.stdin],[],[],0.1)
					if r:
						ch=sys.stdin.read(1)
						return ch
			finally:
				termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	def Mostra(l, pager):
		count=0
		total=len(l)
		print("\n")
		for j in l:
			print(f"- ({j}) -- {d[j]};")
			count+=1
			if count%pager==0 and count<total:
				print(f"--- [PG: {int(count/pager)}] --- ({count-pager+1}/{count})...{total}---",end="")
				ch=key("")
				if ch=='\x1b':
					return False
		print(f"---------- [End]---({count}/{total})----------")
		return True
	def minimal_keys(keys):
		res={}
		keys_lower = {key: key.lower() for key in keys}
		for key_item in keys:
			key_str = key_item.lower()
			n = len(key_str)
			found_abbr = None
			for L in range(1, n+1):
				for i in range(n - L + 1):
					candidate = key_str[i:i+L]
					unique = True
					for other in keys:
						if other==key_item:
							continue
						if candidate in keys_lower[other]:
							unique = False
							break
					if unique:
						found_abbr = candidate.upper()
						break
				if found_abbr is not None:
					break
			if found_abbr is None:
				found_abbr = key_item.upper()
			res[key_item]=found_abbr
		return res
	def Listaprompt(keys_list, full):
		if full:
			formatted=[k.capitalize() for k in keys_list]
		else:
			abbrev=minimal_keys(keys_list)
			formatted=[abbrev[k] for k in keys_list]
		return "\n(" + ", ".join(formatted) + ")>"
	def valid_match(key_item, sub):
		kl=key_item.lower()
		sl=sub.lower()
		if sl=="":
			return True
		if kl==sl:
			return True
		if sl not in kl:
			return False
		if kl.endswith(sl) and kl.find(sl)==(len(kl)-len(sl)) and kl.count(sl)==1:
			return False
		return True
	orig_keys=list(d.keys())
	current_input=""
	last_displayed=None
	if len(d)==0:
		print("Nothing to choose")
		return ""
	elif len(d)==1:
		return orig_keys[0]
	if show_only:
		Mostra(orig_keys, pager)
		return None
	if show:
		Mostra(orig_keys, pager)
		last_displayed = orig_keys[:]
	while True:
		filtered=[k for k in orig_keys if valid_match(k, current_input)]
		if not filtered:
			print("\n"+ntf)
			current_input=""
			filtered=orig_keys[:]
		if len(filtered)==1:
			return filtered[0]
		if show_on_filter and filtered!=last_displayed:
			if not Mostra(filtered, pager):
				last_displayed = filtered[:]
				continue
			last_displayed = filtered[:]
		if keyslist:
			prompt_str=Listaprompt(filtered, full_keyslist)
		else:
			prompt_str=p
		user_char=key(prompt=" "+prompt_str+current_input)
		if user_char in ['\r','\n']:
			if current_input=="":
				return None
			for k in orig_keys:
				if k.lower()==current_input.lower():
					return k
			if len(filtered)==1:
				return filtered[0]
			else:
				print("\nContinua a digitare")
		elif user_char=='\x1b':
			return None
		elif user_char=='?':
			if not Mostra(filtered, pager):
				last_displayed = filtered[:]
				continue
			last_displayed = filtered[:]
		elif user_char=='\x08' or ord(user_char)==127:
			if current_input:
				current_input=current_input[:-1]
		else:
			current_input+=user_char
			filtered=[k for k in orig_keys if valid_match(k, current_input)]
			if len(filtered)==1:
				return filtered[0]
			if len(filtered)==0:
				print("\n"+ntf)
				current_input=""
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