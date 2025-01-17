'''
	GBUtils di Gabriele Battaglia (IZ4APU)
	Data concepimento: lunedì 3 febbraio 2020.
	Raccoglitore di utilità per i miei programmi.
	Spostamento su github in data 27/6/2024. Da usare come submodule per gli altri progetti.
	V15 di martedì 29 ottobre 2024

Lista utilità contenute in questo pacchetto
	base62 3.0 di martedì 15 novembre 2022
	dgt 1.9 di lunedì 17 aprile 2023
	gridapu 1.2 from IU1FIG
	key 4.6
	manuale 1.0.1 di domenica 5 maggio 2024
	Mazzo 4.6 - ottobre 2024 - By ChatGPT-o1 e Gabriele Battaglia
	menu V1.2.1 del 17 luglio 2024
	percent V1.0 thu 28, september 2023
	Scadenza 1.0 del 15/12/2021
	sonify V5.0, october 29th, 2024
	Vecchiume 1.0 del 15/12/2018
'''

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

def sonify(data_list, duration, ptm=False, vol=0.5):
	'''
	sonify V5.0, oct 29th, 2024
	It sonify a serie of data float
	RX a float list in between 5 and 500k values
	   duration in ms
				bool portamento, if it's true a glissando will be applied in between value transition
	It returns nothing but audio
	'''
	import random
	import numpy as np
	import sounddevice as sd
	if len(data_list) < 5 or len(data_list) > 500000:
		print("Sonify4: data serie length out of range")
		return
	try:
		data_list = [float(value) for value in data_list]
	except ValueError:
		return  # Non produce alcun output se la conversione fallisce
	if not (0.1 <= vol <= 1.0):
		vol = max(0.1, min(vol, 1.0))
	data_min = min(data_list)
	data_max = max(data_list)
	data_mean = sum(data_list) / len(data_list)
	freq_min = 65.41   # C2
	freq_max = 4186.01 # C8
	if data_max - data_min == 0:
		frequencies = [(freq_min + freq_max) / 2] * len(data_list)
	else:
		frequencies = [freq_min + (value - data_min) * (freq_max - freq_min) / (data_max - data_min) for value in data_list]
	total_duration_sec = duration / 1000.0
	sample_rate = 44100
	total_samples = int(total_duration_sec * sample_rate)
	t = np.arange(total_samples) / sample_rate
	if ptm:
		segment_times = np.linspace(0, total_duration_sec, len(frequencies), endpoint=False)
		freq_array = np.interp(t, segment_times, frequencies, left=frequencies[0], right=frequencies[-1])
	else:
		segment_samples = total_samples // len(frequencies)
		freq_array = np.zeros(total_samples)
		for i, freq in enumerate(frequencies):
			start = i * segment_samples
			end = start + segment_samples
			if i == len(frequencies) - 1:
				end = total_samples
			freq_array[start:end] = freq
	phase = 2 * np.pi * np.cumsum(freq_array / sample_rate)
	audio_signal = np.sin(phase)
	audio_signal *= vol
	fade_samples = int(0.7 * sample_rate)  # 150 ms in numero di campioni
	if fade_samples * 2 > total_samples:
		fade_samples = total_samples // 2  # Assicura che il fade non sia più lungo del segnale
	fade_in = np.linspace(0, 1, fade_samples)
	fade_out = np.linspace(1, 0, fade_samples)
	audio_signal[:fade_samples] *= fade_in
	audio_signal[-fade_samples:] *= fade_out
	pan = np.linspace(-1.0, 1.0, total_samples)
	left = audio_signal * ((1 - pan) / 2)
	right = audio_signal * ((1 + pan) / 2)
	audio = np.column_stack((left, right))
	sd.play(audio, samplerate=sample_rate)
	sd.wait()
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