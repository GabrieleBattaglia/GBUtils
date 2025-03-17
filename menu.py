def menu(d={}, p="> ", ntf="Scelta non valida", show=False, show_only=False, keyslist=False, full_keyslist=True, pager=20, show_on_filter=True):
	"""V3.7 – lunedì 17 marzo 2025 - Gabriele Battaglia e ChatGPT o3-mini-high
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
			print(f"- '{j}' -- {d[j]};")
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

t = {
	"A": "La vita è un'avventura inaspettata.",
	"B": "Il silenzio parla più forte delle parole.",
	"C": "L'arte di vivere consiste nell'imparare a lasciare andare.",
	"Tempo": "Il tempo è un'illusione che sfida la logica.",
	"Spirito": "Lo spirito umano è un universo di possibilità.",
	"Onda": "Come un'onda, le emozioni vanno e vengono.",
	"Arcobaleno": "L'arcobaleno è la promessa di speranza dopo la tempesta.",
	"Viaggio": "Ogni viaggio inizia con un passo incerto.",
	"Sogno": "I sogni sono le chiavi che aprono le porte dell'immaginazione.",
	"Stella": "Una stella brilla nell'oscurità per guidare chi cerca.",
	"Desiderio": "Il desiderio è il motore che accende il cuore.",
	"Silenzio": "Nel silenzio, le verità più profonde si svelano.",
	"Melodia": "La melodia della vita risuona in ogni angolo dell'anima.",
	"Vento": "Il vento porta con sé storie dimenticate.",
	"Speranza": "La speranza illumina anche i giorni più bui.",
	"Fiamma": "Una fiamma ardente sfida la notte più fredda.",
	"Riflesso": "Il riflesso dell'acqua racconta storie antiche.",
	"Nebbia": "Tra la nebbia, il mistero si nasconde.",
	"Eco": "L'eco delle parole non dette risuona lontano.",
	"Orologio": "L'orologio segna il ritmo inarrestabile del destino.",
	"Sguardo": "Un solo sguardo può cambiare il corso di una vita.",
	"Parola": "La parola ha il potere di guarire o ferire.",
	"Pensiero": "Il pensiero libero è la scintilla della creatività.",
	"Risata": "Una risata sincera è una medicina per l'anima.",
	"Deserto": "Il deserto custodisce segreti di mondi antichi.",
	"Foresta": "Nella foresta, ogni albero racconta una storia.",
	"Mare": "Il mare è un abisso di emozioni senza confini.",
	"Fiume": "Il fiume scorre, portando via ricordi e speranze.",
	"Montagna": "La montagna sfida chi osa guardarla con stupore.",
	"Luna": "La luna illumina la via dei viaggiatori notturni.",
	"Sole": "Il sole riscalda il cuore in ogni alba.",
	"Pioggia": "La pioggia rinfresca la terra assetata.",
	"Tempesta": "La tempesta purifica l'anima con la sua forza.",
	"Arcano": "Il mistero arcano invita a scoprire l'ignoto.",
	"Vita": "La vita è un mosaico di momenti preziosi.",
	"Infinito": "L'infinito si svela nelle piccole cose quotidiane.",
	"Origine": "L'origine di ogni sogno è un seme di speranza.",
	"Destino": "Il destino intreccia le storie degli esseri viventi.",
	"EcoInfinito": "L'eco infinito del passato risuona nel presente.",
	"Ricordo": "Ogni ricordo è una pagina scritta nel libro della vita."
}
s = menu(t, show=True, keyslist=True, full_keyslist=False, pager=5, show_on_filter=True)
print(f"\nScelta: {s}")
