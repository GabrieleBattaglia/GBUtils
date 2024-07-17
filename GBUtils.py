'''
	GB UTILS di Gabriele Battaglia (IZ4APU)
	Data concepimento: lunedì 3 febbraio 2020.
	Raccoglitore di utilità per i miei programmi.
	Spostamento su github in data 27/6/2024. Da usare come submodule per gli altri progetti.
	V13 di mercoledì 17 luglio 2024

Lista utilità contenute in questo pacchetto
	percent V1.0 thu 28, september 2023
	base62 3.0 di martedì 15 novembre 2022
	dgt 1.9 di lunedì 17 aprile 2023
	key 4.6
	gridapu 1.2 from IU1FIG
	sonify2 a serie of data, V4.0, march 19th, 2024
	sonify V2.5, april 27th, 2023
	manuale 1.0.1 di domenica 5 maggio 2024
	menu V1.2.1 del 17 luglio 2024
	Scadenza 1.0 del 15/12/2021
	Vecchiume 1.0 del 15/12/2018
'''

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

def sonify(data=[], totalduration=10):
	# Sonify a serie of data, V2.5, april 27th, 2023
	# data= serie of value to sonify
	# totalduration= duration of whole sonification in seconds
	# it plays sound and returns nothing
	datalength = len(data)
	if datalength < 2:
		print("Data serie too short.")
		return
	from time import sleep as S
	from pyo import Server, SigTo, Sine, Pan
	s=Server(verbosity=1).boot()
	s.start()
	singlesoundduration=totalduration/datalength
	if singlesoundduration < 0.08:
		totalduration = 0.08*datalength
		singlesoundduration=totalduration/datalength
		print(f"Duration too short, it has been set to {totalduration:.3f}.")
	ramp=singlesoundduration/100*50
	soundlowerlimit = 130 # about C3
	soundupperlimit = 4186 # about C8
	soundrange=soundupperlimit-soundlowerlimit
	dataloweredge = 99999999999999
	dataupperedge = -99999999999999
	for j in data:
		if j < dataloweredge: dataloweredge = j
		if j > dataupperedge: dataupperedge = j
	if dataloweredge>dataupperedge or dataupperedge<dataloweredge:
		print("Wrong data serie.")
		return
	datarange = dataupperedge-dataloweredge
	g=SigTo(dataloweredge+datarange/2, time=ramp)
	a=Sine(freq=g, mul=.2)
	p=Pan(a, pan=0).out()
	salto=1/datalength
	cnt=1
	for j in data:
		x = (j-dataloweredge) * 100/datarange
		y = x/100*soundrange
		p.pan=salto*cnt-salto/2
		g.value=soundlowerlimit+y
		S(singlesoundduration)
		cnt+=1
	s.stop()
	s.shutdown()
	return

def sonify2(data=[], totalduration=10.0, soundlowerlimit=130.0, soundupperlimit=4186.0, vol=.35, ptm=True):
	# Sonify2 a serie of data, V4.0, march 19th, 2024
	# list data= values to sonify
	# float totalduration= duration of whole sonification in seconds
	# it plays sound and returns nothing
	# default lower and upper sound limit are C3 and C8 notes
	# float vol is amplitude
	# bool ptm = True determines if portamento
	totalduration=float(totalduration)
	datalength = len(data)
	if datalength < 2:
		print("Data serie too short.")
		return
	from pyo import Server, SigTo, Sine, Pan
	from threading import Thread
	from time import sleep
	s=Server(verbosity=1).boot()
	s.start()
	def Sonip():
		# It creates sound with portamento
		singlesoundduration=totalduration/datalength
		soundrange=soundupperlimit - soundlowerlimit
		datarange = max(data) - min(data)
		startsound=soundlowerlimit + soundrange/2
		slide=SigTo(init=data[0], value=data[0], time=singlesoundduration)
		sound=Sine(freq=slide, mul=vol)
		stereo=SigTo(init=0.0, value=1.0, time=totalduration)
		p=Pan(sound, pan=stereo).out()
		for j in data:
			x = (j-min(data)) * 100/datarange
			y = x/100*soundrange
			slide.value=soundlowerlimit + y
			sleep(singlesoundduration)
		sleep(singlesoundduration)
		s.stop()
		s.shutdown()
		return
	def Sonis():
		# It creates sound sliced, no portamento
		singlesoundduration=totalduration/datalength
		soundrange=soundupperlimit - soundlowerlimit
		datarange = max(data) - min(data)
		startsound=soundlowerlimit + soundrange/2
		slide=data[0]
		sound=Sine(freq=slide, mul=vol)
		stereo=SigTo(init=0.0, value=1.0, time=totalduration)
		p=Pan(sound, pan=stereo).out()
		for j in data:
			x = (j-min(data)) * 100/datarange
			y = x/100*soundrange
			sound.freq=soundlowerlimit + y
			sleep(singlesoundduration)
		sleep(singlesoundduration)
		s.stop()
		s.shutdown()
		return
	if ptm: t1=Thread(target=Sonip)
	else: t1=Thread(target=Sonis)
	t1.start()
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
		print("Attenzione, file della guida, mancante.\n\tRichiedere il file all'autore dell'App.")
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