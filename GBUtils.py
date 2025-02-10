'''
	GBUtils di Gabriele Battaglia (IZ4APU)
	Data concepimento: lunedì 3 febbraio 2020.
	Raccoglitore di utilità per i miei programmi.
	Spostamento su github in data 27/6/2024. Da usare come submodule per gli altri progetti.
	V27 di lunedì 10 febbraio 2025.
Lista utilità contenute in questo pacchetto
	Acusticator V3.2 di domenica 9 febbraio 2025. Gabriele Battaglia e ChatGPT o3-mini-high
	base62 3.0 di martedì 15 novembre 2022
	CWzator VV6.6.1	di lunedì 10 febbraio 2025 - Kevin Schmidt (W9CF), Gabriele Battaglia (IZ4APU) e	ChatGPT o3-mini-high
	dgt 1.9 di lunedì 17 aprile 2023
	gridapu 1.2 from IU1FIG
	key 4.6
	manuale 1.0.1 di domenica 5 maggio 2024
	Mazzo 4.6 - ottobre 2024 - By ChatGPT-o1 e Gabriele Battaglia
	menu V1.2.1 del 17 luglio 2024
	percent V1.0 thu 28, september 2023
	Scadenza 1.0 del 15/12/2021
	sonify V6.0.1 del 7 febbraio 2025 - Gabriele Battaglia e ChatGPT O1
	Vecchiume 1.0 del 15/12/2018
'''
def CWzator(msg, wpm=35, pitch=550, l=30, s=50, p=50, fs=44100, ms=1, vol=0.5, wv=1, sync=False, file=False):
	"""
	V6.6.1	di lunedì 10 febbraio 2025 - Gabriele Battaglia e	ChatGPT o3-mini-high
		da un'idea originale di Kevin Schmidt W9CF
	Genera e riproduce l'audio del codice Morse dal messaggio di testo fornito.
	Generates and plays Morse code audio from the given text message.
	Parameters:
		msg (str): Text message to convert to Morse code.
		wpm (int): Words per minute rate for Morse timing (valid range: 5 to 100).
		pitch (int): Frequency in Hz for the tone (valid range: 130 to 2000).
		l (int): Weight for dash (line) duration relative to the standard (default 30).
		s (int): Weight for gap (space) duration between symbols relative to the standard (default 50).
		p (int): Weight for dot duration relative to the standard (default 50).
		fs (int): Sampling frequency in Hz (default 44100).
		ms (int): Duration in milliseconds for fade-in and fade-out (anti-click ramps); the tone’s effective duration is reduced by 2*ms (default 1).
		vol (float): Volume multiplier (range 0.0 [silence] to 1.0 [maximum], default 0.5).
		wv (int): Waveform type for the tone:
		          1 = Sine (default),
		          2 = Square,
		          3 = Triangle,
		          4 = Sawtooth.
		sync (bool): If True, the function blocks until audio playback is finished; otherwise, it returns immediately (default False).
		file (bool): If True, saves the audio to a file named "morse[datetime].wav" (default False).
	Returns:
		An object representing the playback (from simpleaudio), or None if parameters are invalid.
		rwpm (float): Effective words per minute rate based on the actual Morse code timing. If the standard timing is used, it equals wpm.
	"""
	import numpy as np
	import simpleaudio as sa
	if not isinstance(msg, str) or msg == "" or pitch < 130 or pitch > 2000 or wpm < 5 or wpm > 100 or \
	   l < 1 or l > 100 or s < 1 or s > 100 or p < 1 or p > 100 or vol < 0 or vol > 1 or wv not in [1,2,3,4]:
		print("Not valid CW parameters")
		return None
	T = 1.2 / float(wpm)
	dot_duration = T * (p/50.0)
	dash_duration = 3 * T * (l/30.0)
	intra_gap = T * (s/50.0)
	letter_gap = 3 * T * (s/50.0)
	word_gap = 7 * T * (s/50.0)
	def generate_tone(duration):
		N = int(fs * duration)
		t = np.linspace(0, duration, N, False)
		if wv == 1:  # Sine wave
			signal = np.sin(2 * np.pi * pitch * t)
		elif wv == 2:  # Square wave
			signal = np.sign(np.sin(2 * np.pi * pitch * t))
		elif wv == 3:  # Triangle wave
			# Triangle wave: 2 * abs(2*(t*freq - floor(t*freq + 0.5))) - 1
			signal = 2 * np.abs(2 * (pitch * t - np.floor(pitch * t + 0.5))) - 1
		elif wv == 4:  # Sawtooth wave
			# Sawtooth wave: 2*(t*freq - floor(0.5 + t*freq))
			signal = 2 * (pitch * t - np.floor(0.5 + pitch * t))
		fade_samples = int(fs * ms / 1000)
		if fade_samples * 2 < N:
			ramp = np.linspace(0, 1, fade_samples)
			signal[:fade_samples] *= ramp
			signal[-fade_samples:] *= ramp[::-1]
		return (signal * (2**15 - 1) * vol).astype(np.int16)
	def generate_silence(duration):
		return np.zeros(int(fs * duration), dtype=np.int16)
	morse_map = { "a":".-", "b":"-...", "c":"-.-.", "d":"-..", "e":".", "f":"..-.",
			"g":"--.", "h":"....", "i":"..", "j":".---", "k":"-.-", "l":".-..",
			"m":"--", "n":"-.", "o":"---", "p":".--.", "q":"--.-", "r":".-.",
			"s":"...", "t":"-", "u":"..-", "v":"...-", "w":".--", "x":"-..-",
			"y":"-.--", "z":"--..", "0":"-----", "1":".----", "2":"..---",
			"3":"...--", "4":"....-", "5":".....", "6":"-....", "7":"--...",
			"8":"---..", "9":"----.", ".":".-.-.-", "-":"-....-", ",":"--..--",
			"?":"..--..", "/":"-..-.", ";":"-.-.-.", "(":"-.--.", "[":"-.--.",
			")":"-.--.-", "]":"-.--.-", "@":".--.-.", "*":"...-.-", "+":".-.-.",
			"%":".-...", ":":"---...", "=":"-...-", '"':".-..-.", "'":".----.",
			"!":"-.-.--", "$":"...-..-"," ":"", "_":"",
			"ò":"---.", "à":".--.-", "ù":"..--", "è":"..-..",
			"é":"..-..", "ì":".---."
	}
	segments = []
	words = msg.lower().split()
	for w_idx, word in enumerate(words):
		letters = [ch for ch in word if ch in morse_map]
		for l_idx, letter in enumerate(letters):
			code = morse_map[letter]
			for s_idx, symbol in enumerate(code):
				if symbol == '.':
					segments.append(generate_tone(dot_duration))
				elif symbol == '-':
					segments.append(generate_tone(dash_duration))
				if s_idx < len(code)-1:
					segments.append(generate_silence(intra_gap))
			if l_idx < len(letters)-1:
				segments.append(generate_silence(letter_gap))
		if w_idx < len(words)-1:
			segments.append(generate_silence(word_gap))
	audio = np.concatenate(segments) if segments else np.array([], dtype=np.int16)
	if (l, s, p) == (30, 50, 50):
		rwpm = wpm
	else:
		dots = 0
		dashes = 0
		intra_gaps = 0
		letter_gaps = 0
		word_gaps = 0
		words_list = msg.lower().split()
		for w in words_list:
			letters = [ch for ch in w if ch in morse_map]
			for letter in letters:
				code = morse_map[letter]
				dots += code.count('.')
				dashes += code.count('-')
				if len(code) > 1:
					intra_gaps += (len(code) - 1)
			if len(letters) > 1:
				letter_gaps += (len(letters) - 1)
		if len(words_list) > 1:
			word_gaps = len(words_list) - 1
		standard_total = dots + 3 * dashes + intra_gaps + 3 * letter_gaps + 7 * word_gaps
		actual_total = (dots * (p / 50.0)) + (3 * dashes * (l / 30.0)) + (intra_gaps * (s / 50.0)) + (3 * letter_gaps * (s / 50.0)) + (7 * word_gaps * (s / 50.0))
		ratio = actual_total / standard_total if standard_total != 0 else 1
		rwpm = wpm / ratio
	play_obj = sa.play_buffer(audio, 1, 2, fs)
	if file:
		from datetime import datetime
		import	wave
		filename = "cwapu Morse recorded at " + datetime.now().strftime("%Y%m%d%H%M%S") + ".wav"
		with wave.open(filename, 'wb') as wf:
			wf.setnchannels(1)
			wf.setsampwidth(2)
			wf.setframerate(44100)
			wf.writeframes(audio.tobytes())
	if sync:
		play_obj.wait_done()
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
	'''V4.6 29/11/2022.
	Attende per il numero di secondi specificati
	se tempo e' scaduto, o si preme un tasto, esce.
	prompt e' il messaggio da mostrare.
	Restituisce il tasto premuto.
	'''
	import msvcrt, time, sys
	if prompt != "":
		print (prompt, end="")
		sys.stdout.flush()
	t = time.time(); a = ""
	while (time.time() - t <= attesa):
		if msvcrt.kbhit():
			a = msvcrt.getwch()
			return a
	return ''
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
	sonify V6.0.1 - 5 febbraio 2025 - Gabriele Battaglia eChatGPT O1
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
	import simpleaudio as sa
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
		freq_array = np.zeros(total_samples, dtype=np.float64)
		segment_duration = duration/n
		for i, freq in enumerate(frequencies):
			start_t = i*segment_duration
			end_t = (i+1)*segment_duration
			start_s = int(round(start_t*sample_rate))
			end_s = int(round(end_t*sample_rate))
			if i == n-1:
				end_s = total_samples
			freq_array[start_s:end_s] = freq
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
	play_obj = sa.play_buffer(audio_stereo_int16, 2, 2, sample_rate)
	if file:
		from	datetime import datetime
		filename = "sonification" + datetime.now().strftime("%Y%m%d%H%M%S") + ".wav"
		with wave.open(filename, 'wb') as wf:
			wf.setnchannels(2)
			wf.setsampwidth(2)
			wf.setframerate(sample_rate)
			wf.writeframes(audio_stereo_int16.tobytes())
	return
def Acusticator(score, kind=1, adsr=[0.2, 0.0, 100.0, 0.2], fs=44100, sync=False):
	"""
	V3.2 di domenica 9 febbraio 2025. Gabriele Battaglia e ChatGPT o3-mini-high
	Crea e riproduce (in maniera asincrona) un segnale acustico in base allo score fornito,
	utilizzando simpleaudio per la riproduzione e applicando un envelope ADSR definito in termini
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
	         Il valore di default è [.2, 0.0, 100.0, .2].
	 - fs (int): frequenza di campionamento (default 44100 Hz).
	Se la lunghezza di score non è un multiplo di 4 viene sollevato un errore.
	La riproduzione avviene in background, restituendo subito il controllo al chiamante.
	"""
	import numpy as np
	import simpleaudio as sa
	from scipy import signal
	import threading
	import re
	# Converte i valori ADSR da percentuali (0-100) a frazioni
	a_pct, d_pct, s_pct, r_pct = adsr
	a_frac = a_pct / 100.0
	d_frac = d_pct / 100.0
	s_level = s_pct / 100.0
	r_frac = r_pct / 100.0
	if a_pct + d_pct + r_pct > 100:
		raise ValueError("La somma delle percentuali per attacco, decadimento e rilascio deve essere <= 100")
	def note_to_freq(note):
		if isinstance(note, (int, float)):
			return float(note)
		if isinstance(note, str):
			if note.lower() == 'p':
				return None
			match = re.match(r"^([a-g])([#b]?)(\d)$", note.lower())
			if not match:
				raise ValueError("Formato nota non valido: " + note)
			note_letter, accidental, octave = match.groups()
			octave = int(octave)
			note_base = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
			semitone = note_base[note_letter]
			if accidental == '#':
				semitone += 1
			elif accidental == 'b':
				semitone -= 1
			midi_num = 12 + semitone + 12 * octave
			freq = 440 * 2 ** ((midi_num - 69) / 12)
			return freq
		else:
			raise TypeError("Tipo nota non riconosciuto")
	if len(score) % 4 != 0:
		raise ValueError("La lista score non è un multiplo di 4")
	segments = []
	for i in range(0, len(score), 4):
		note_param = score[i]
		dur = float(score[i+1])
		pan = float(score[i+2])
		vol = float(score[i+3])
		n_samples = int(fs * dur)
		t = np.linspace(0, dur, n_samples, endpoint=False)
		# Calcola i campioni per ciascuna fase in base alle frazioni
		attack_samples = int(n_samples * a_frac)
		decay_samples = int(n_samples * d_frac)
		release_samples = int(n_samples * r_frac)
		sustain_samples = n_samples - (attack_samples + decay_samples + release_samples)
		if sustain_samples < 0:
			sustain_samples = 0
		# Costruisce l'envelope ADSR:
		# Attack: ramp da 0 a 1
		attack_env = np.linspace(0, 1, attack_samples, endpoint=False) if attack_samples > 0 else np.array([])
		# Decay: ramp da 1 al livello di sustain (s_level)
		decay_env = np.linspace(1, s_level, decay_samples, endpoint=False) if decay_samples > 0 else np.array([])
		# Sustain: livello costante pari a s_level
		sustain_env = np.full(sustain_samples, s_level) if sustain_samples > 0 else np.array([])
		# Release: ramp da s_level a 0
		release_env = np.linspace(s_level, 0, release_samples, endpoint=True) if release_samples > 0 else np.array([])
		envelope = np.concatenate([attack_env, decay_env, sustain_env, release_env])
		if envelope.shape[0] < n_samples:
			envelope = np.pad(envelope, (0, n_samples - envelope.shape[0]), mode='edge')
		elif envelope.shape[0] > n_samples:
			envelope = envelope[:n_samples]
		left_gain = np.sqrt((1 - pan) / 2)
		right_gain = np.sqrt((1 + pan) / 2)
		freq = note_to_freq(note_param)
		if freq is None:
			wave = np.zeros(n_samples)
		else:
			if kind == 1:
				wave = np.sin(2 * np.pi * freq * t)
			elif kind == 2:
				wave = signal.square(2 * np.pi * freq * t)
			elif kind == 3:
				wave = signal.sawtooth(2 * np.pi * freq * t, width=0.5)
			elif kind == 4:
				wave = signal.sawtooth(2 * np.pi * freq * t, width=1.0)
			else:
				raise ValueError("Tipo di onda non riconosciuto")
			# Applica l'envelope ADSR
			wave *= envelope
		stereo = np.zeros((n_samples, 2))
		stereo[:, 0] = wave * vol * left_gain
		stereo[:, 1] = wave * vol * right_gain
		segments.append(stereo)
	full_signal = np.concatenate(segments, axis=0)
	audio_data = np.int16(full_signal * 32767)
	def play_audio():
		play_obj = sa.play_buffer(audio_data.tobytes(), num_channels=2, bytes_per_sample=2, sample_rate=fs)
		play_obj.wait_done()
	import threading
	thread = threading.Thread(target=play_audio)
	thread.start()
	if sync: thread.join()
	return
def dgt(prompt="", kind="s", imin=-999999999, imax=999999999, fmin=-999999999.9, fmax=999999999.9, smin=0, smax=256, pwd=False, default=None):
	'''Versione 1.9 di lunedì 17 aprile 2023
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
					return imin
				elif p > imax:
					print(f"Corretto con {imax-p}, accettato: {imax}")
					return imax
				else: return p
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
					return fmin
				elif p > fmax:
					print(f"Corretto con {fmax-p:10.3}, accettato: {fmax}")
					return fmax
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
def menu(d={}, p="> ", ntf="Scelta non valida", show=False, show_only=False, keyslist=False):
	'''
	V1.2.1 del 17 luglio 2024
	riceve
		dict d: il menù da mostrare d{'chiave':'spiegazione'}
		str p: prompt per richiesta comandi
		str ntf: da mostrare in caso di comando non presente in d
		bool show: se vero, mostra menù alla chiamata
		bool show_only: se vero mostra menù e ritorna None
		bool keyslist: se vero genera prompt con sequenza di chiavi e ignora p
	ritorna
		str stringa: scelta effettuata
	'''
	import msvcrt
	def key(prompt):
		print(prompt, end='', flush=True)
		ch = msvcrt.getch().decode('utf-8')
		return ch
	def Mostra(l):
		count = 0
		item = len(l)
		print("\n")
		for j in l:
			print(f"- '{j}' -- {d[j]};")
			count += 1
			if count % 20 == 0:
				print(f"---------- [{int(count/20)}]---({count-19}/{count})...{item}--------AnyKey-or-ESC--")
				ch = msvcrt.getch()
				if ch == b'\x1b':  return False
		return True
	def Listaprompt(l):
		p = '\n['
		for k in l:
			p += k + "."
		p += "]>"
		return p
	if show_only:
		Mostra(d)
		return None
	if show:
		Mostra(d)
	ksd = list(map(str, d.keys()))
	stringa = ''
	if len(d) < 2:
		print('Not enough voices in menu')
		return ''
	if keyslist:
		p = Listaprompt(ksd)
	while True:
		s = key(prompt=f"{p} {stringa}")
		if s == '\r':
			if stringa == '':
				return None
			elif stringa in ksd:
				return stringa
			elif len([k for k in ksd if k.startswith(stringa)]) == 1:
				return [k for k in ksd if k.startswith(stringa)][0]
			else:
				print("\nContinua a digitare")
		elif s == '\x08':  # backspace
			stringa = stringa[:-1]
			if stringa == '':
				return None
			ksl = [j for j in ksd if j.startswith(stringa)]
			Mostra(ksl)
		else:
			stringa += s
			ksl = [j for j in ksd if j.startswith(stringa)]
			if len(ksl) == 1:
				return ksl[0]
			elif len(ksl) == 0:
				print("\n" + ntf)
				stringa = stringa[:-1]
				ksl = [j for j in ksd if j.startswith(stringa)]
				if not Mostra(ksl):
					return None
			else:
				Mostra(ksl)
			if keyslist:
				p = Listaprompt(ksl)
	return
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