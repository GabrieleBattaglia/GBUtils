# menu, con cui lavora questo file di test è stato spostato in gbutils.
def menuOld(d={}, p="> ", ntf="Scelta non valida", show=True, show_only=False, keyslist=True, full_keyslist=False, pager=20, show_on_filter=True, numbered=False):
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

def menuold2(d={}, p="> ", ntf="Scelta non valida", show=True, show_only=False, keyslist=True, pager=20, show_on_filter=True, numbered=False):
    """V4.0 – giovedì 18 settembre 2025 - Gabriele Battaglia & Gemini 2.5 Pro
    
    Questa è l'ultima versione funzionante con anche le righe vuote. Da ripristinare in caso che copilot abbia fatto casini togliendo le righe vuote nella versione che integro in gbutils.
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

    Restituisce:
    La chiave scelta dal dizionario 'd', oppure None se l'utente annulla (ESC o Invio su input vuoto).
    """
    import sys, time, os

    # Funzioni di supporto interne
    def lcp(strings):
        """Calcola il prefisso comune più lungo da una lista di stringhe."""
        if not strings: return ""
        return os.path.commonprefix(strings)

    def key(prompt=""):
        """Legge un singolo carattere dalla console senza bisogno di Invio."""
        print(prompt, end='', flush=True)
        if os.name == 'nt':
            import msvcrt
            ch = msvcrt.getwch()
            if ch in ('\x00', '\xe0'): # Tasti speciali (Frecce, Canc, etc.)
                msvcrt.getwch() # Leggi e ignora il secondo byte
                return '\x00'
            if ch == '\x08': return ch # Backspace
            if ch == '\r': return ch   # Enter
            if ch == '\x1b': return ch # ESC
            if ch == '?': return ch    # Carattere speciale ?
            if ord(ch) == 127: return '\x08' # Gestisce DEL come Backspace
            return ch # Carattere normale
        else: # Unix-like
            import select, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b': # ESC o sequenza speciale
                    r, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if r:
                        sys.stdin.read(2) # Leggi resto sequenza (es. freccia)
                        return '\x00'
                    else:
                        return '\x1b' # Solo ESC
                elif ord(ch) == 127: return '\x08' # Backspace (DEL)
                elif ch in ['\n', '\r']: return '\r' # Normalizza Invio a \r
                else: return ch # Altro carattere
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def Mostra(items_to_show, pager, is_numbered, num_map=None, user_input=""):
        """Visualizza una lista di elementi usando un pager internazionalizzato."""
        count = 0
        total = len(items_to_show)
        if total == 0 and user_input: print(ntf); return True;
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
                # Pager senza testo in lingua
                page_num = int(count / pager)
                prompt_pager = f"--- [{page_num}] ({count-pager+1}-{count}/{total}) ---"
                ch_pager = key(prompt_pager); print();
                if ch_pager == '\x1b': return False;
        # Riga di fine lista senza testo in lingua
        print(f"---------- [{count}/{total}] ----------")
        return True

    def Listaprompt_autocomplete(keys_list, display_input):
        """Genera un prompt che suggerisce i prossimi caratteri validi."""
        if not keys_list or len(keys_list) <= 1: return ">";
        next_chars = set()
        input_len = len(display_input)
        for key in keys_list:
            if len(key) > input_len:
                next_chars.add(key[input_len].upper())
        if not next_chars: return ">";
        return f"({', '.join(sorted(list(next_chars)))})>"

    def valid_match(key_item, sub):
        """Controlla se 'key_item' inizia con 'sub' (case-insensitive)."""
        return key_item.lower().startswith(sub.lower())

    # --- Logica Principale del Menu ---
    orig_keys = list(d.keys())
    user_input = "" # Traccia solo l'input effettivo dell'utente
    last_displayed = None
    num_map = {}

    if numbered:
        num_map = {str(i): k for i, k in enumerate(orig_keys, 1)}
        orig_keys = list(num_map.keys())
    
    if not d: print("No options available."); return None;
    if len(d) == 1 and not show_only: return list(d.keys())[0];
    if show_only: Mostra(orig_keys, pager, numbered, num_map); return None;

    if show:
        if not Mostra(orig_keys, pager, numbered, num_map): return None
        last_displayed = orig_keys[:]

    disable_autocomplete_once = False # NUOVA RIGA
    while True:
        # Il filtro si basa sempre sull'input utente
        filtered = [k for k in orig_keys if valid_match(k, user_input)]

        # 'display_input' è ciò che mostriamo, include l'autocompletamento
        display_input = user_input
        if not numbered and not disable_autocomplete_once and len(filtered) > 1:
            common_prefix = lcp([k.lower() for k in filtered])
            if len(common_prefix) > len(user_input):
                user_input = common_prefix
                display_input = common_prefix        
        disable_autocomplete_once = False # NUOVA RIGA
        # La lista finale si basa sull'input mostrato (con autocompletamento)
        final_filtered = [k for k in orig_keys if valid_match(k, display_input)]

        if len(final_filtered) == 1 and len(display_input) > 0:
            final_choice = final_filtered[0]
            print() # Aggiunge uno spazio per pulizia prima di uscire
            return num_map.get(final_choice, final_choice)
        
        if show_on_filter and final_filtered != last_displayed:
            print("\n-----------------------")
            if not Mostra(final_filtered, pager, numbered, num_map, user_input): return None;
            last_displayed = final_filtered[:]
            
        if numbered:
            prompt_str = p if p != "> " else f"(1-{len(orig_keys)})"
            if not prompt_str.strip().endswith('>'): prompt_str += '> ';
        elif keyslist:
            prompt_str = Listaprompt_autocomplete(final_filtered, display_input)
        else:
            prompt_str = p
        
        full_prompt = prompt_str + display_input
        user_char = key(full_prompt)
        
        if user_char in ['\r', '\n']:
            print()
            if display_input in final_filtered:
                return num_map.get(display_input, display_input)
            elif len(final_filtered) == 1:
                 return num_map.get(final_filtered[0], final_filtered[0])
            elif user_input == "":
                return None
            else:
                 print("--- Scelta ambigua. Premi '?' per la lista. ---")
                 last_displayed = None
                 
        elif user_char == '\x1b': print(); return None;
        elif user_char == '?': last_displayed = None;
        elif user_char == '\x08': # Backspace
            if user_input:
                user_input = user_input[:-1]
                print('\b \b'*len(display_input), end='', flush=True) # Cancella l'intero display_input
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

# run_tests.py
# Script per testare la funzione menu() dal file test.py

import os

# --- 1. DEFINIZIONE DEI DIZIONARI DI TEST ---

dizionario_citta = {
    'Roma': 'Lazio', 'Milano': 'Lombardia', 'Napoli': 'Campania', 'Torino': 'Piemonte',
    'Palermo': 'Sicilia', 'Genova': 'Liguria', 'Bologna': 'Emilia-Romagna', 'Firenze': 'Toscana',
    'Bari': 'Puglia', 'Catania': 'Sicilia', 'Venezia': 'Veneto', 'Verona': 'Veneto',
    'Messina': 'Sicilia', 'Padova': 'Veneto', 'Trieste': 'Friuli-Venezia Giulia',
    'Taranto': 'Puglia', 'Brescia': 'Lombardia', 'Parma': 'Emilia-Romagna', 'Prato': 'Toscana',
    'Modena': 'Emilia-Romagna', 'Reggio Calabria': 'Calabria', 'Reggio Emilia': 'Emilia-Romagna',
    'Perugia': 'Umbria', 'Ravenna': 'Emilia-Romagna', 'Livorno': 'Toscana', 'Cagliari': 'Sardegna',
    'Foggia': 'Puglia', 'Rimini': 'Emilia-Romagna', 'Salerno': 'Campania', 'Ferrara': 'Emilia-Romagna',
    'Latina': 'Lazio', 'Monza': 'Lombardia', 'Siracusa': 'Sicilia', 'Pescara': 'Abruzzo',
    'Trento': 'Trentino-Alto Adige', 'Bergamo': 'Lombardia', 'Forlì': 'Emilia-Romagna'
}

dizionario_programmazione = {
    'Algoritmo': 'Sequenza finita di passaggi per risolvere un problema.',
    'Variabile': 'Un contenitore per memorizzare un valore.',
    'Funzione': 'Un blocco di codice riutilizzabile che esegue un\'attività specifica.',
    'Ciclo For': 'Itera su una sequenza di elementi.',
    'Ciclo While': 'Esegue un blocco di codice finché una condizione è vera.',
    'Condizione If-Else': 'Esegue codice diverso in base a una condizione booleana.',
    'Classe': 'Un modello per creare oggetti.',
    'Oggetto': 'Un\'istanza di una classe.',
    'Metodo': 'Una funzione che appartiene a un oggetto.',
    'Libreria': 'Una collezione di funzioni e metodi pre-scritti.',
    'Framework': 'Una struttura di base su cui costruire un\'applicazione.',
    'API': 'Interfaccia di Programmazione delle Applicazioni, per far comunicare software diversi.',
    'Database': 'Una raccolta organizzata di dati.',
    'SQL': 'Linguaggio per interrogare e manipolare database.',
    'Frontend': 'La parte di un\'applicazione con cui l\'utente interagisce (UI).',
    'Backend': 'La parte di un\'applicazione che gestisce la logica e i dati.',
    'Repository': 'Un archivio per il codice sorgente, spesso gestito con Git.',
    'Commit': 'Un salvataggio delle modifiche in un repository Git.',
    'Merge': 'L\'unione di diverse versioni di codice.',
    'Branch': 'Una linea di sviluppo indipendente nel codice.',
    'Debugging': 'Il processo di trovare e correggere errori nel codice.',
    'Compilatore': 'Traduce il codice sorgente in codice macchina.',
    'Interprete': 'Esegue il codice sorgente riga per riga.',
    'Sintassi': 'Le regole grammaticali di un linguaggio di programmazione.',
    'Parametro': 'Una variabile passata a una funzione.',
    'Argomento': 'Il valore effettivo passato a un parametro di una funzione.',
    'Ricorsione': 'Una funzione che chiama sé stessa.',
    'JSON': 'Formato leggero per lo scambio di dati.',
    'IDE': 'Ambiente di Sviluppo Integrato (es. VS Code).',
    'SDK': 'Kit di Sviluppo Software.'
}

dizionario_libri = {
    'Il Signore degli Anelli': 'J.R.R. Tolkien', '1984': 'George Orwell',
    'Il giovane Holden': 'J.D. Salinger', 'Orgoglio e pregiudizio': 'Jane Austen',
    'Delitto e castigo': 'Fëdor Dostoevskij', 'Guerra e pace': 'Lev Tolstoj',
    'Cent\'anni di solitudine': 'Gabriel García Márquez', 'Moby Dick': 'Herman Melville',
    'Ulisse': 'James Joyce', 'Don Chisciotte della Mancia': 'Miguel de Cervantes',
    'Il processo': 'Franz Kafka', 'Il grande Gatsby': 'F. Scott Fitzgerald',
    'Alla ricerca del tempo perduto': 'Marcel Proust', 'I fratelli Karamazov': 'Fëdor Dostoevskij',
    'Lo straniero': 'Albert Camus', 'Il nome della rosa': 'Umberto Eco',
    'Se questo è un uomo': 'Primo Levi', 'Fahrenheit 451': 'Ray Bradbury',
    'Cronache marziane': 'Ray Bradbury', 'Il buio oltre la siepe': 'Harper Lee',
    'Sulla strada': 'Jack Kerouac', 'Anna Karenina': 'Lev Tolstoj',
    'Il barone rampante': 'Italo Calvino', 'Le città invisibili': 'Italo Calvino',
    'L\'insostenibile leggerezza dell\'essere': 'Milan Kundera', 'Madame Bovary': 'Gustave Flaubert',
    'Il ritratto di Dorian Gray': 'Oscar Wilde', 'Frankenstein': 'Mary Shelley',
    'Dracula': 'Bram Stoker', 'Cime tempestose': 'Emily Brontë'
}

dizionario_elementi = {
    'Idrogeno': 'H', 'Elio': 'He', 'Litio': 'Li', 'Berillio': 'Be', 'Boro': 'B', 'Carbonio': 'C',
    'Azoto': 'N', 'Ossigeno': 'O', 'Fluoro': 'F', 'Neon': 'Ne', 'Sodio': 'Na', 'Magnesio': 'Mg',
    'Alluminio': 'Al', 'Silicio': 'Si', 'Fosforo': 'P', 'Zolfo': 'S', 'Cloro': 'Cl', 'Argon': 'Ar',
    'Potassio': 'K', 'Calcio': 'Ca', 'Scandio': 'Sc', 'Titanio': 'Ti', 'Vanadio': 'V', 'Cromo': 'Cr',
    'Manganese': 'Mn', 'Ferro': 'Fe', 'Cobalto': 'Co', 'Nichel': 'Ni', 'Rame': 'Cu', 'Zinco': 'Zn',
    'Gallio': 'Ga', 'Germanio': 'Ge', 'Arsenico': 'As', 'Selenio': 'Se', 'Bromo': 'Br', 'Kripton': 'Kr'
}


# --- 2. FUNZIONE PER ESEGUIRE I TEST ---

def run_tests():
    """Esegue una serie di test sulla funzione menu."""
    
    # Test 1: Lista di città, comportamento standard
    print("--- TEST 1: Scegli una città italiana (comportamento standard) ---")
    scelta_citta = menu(dizionario_citta)
    if scelta_citta:
        print(f"\n✅ Città scelta: {scelta_citta} (Regione: {dizionario_citta[scelta_citta]})")
    else:
        print("\n❌ Selezione annullata.")
    input("\nPremi Invio per continuare con il prossimo test...")
    os.system('cls' if os.name == 'nt' else 'clear')

    # Test 2: Termini di programmazione, senza mostrare il menù all'inizio (show=False)
    print("--- TEST 2: Scegli un termine di programmazione (menù nascosto all'inizio) ---")
    print("Inizia a digitare per filtrare la lista...")
    scelta_prog = menu(dizionario_programmazione, show=False)
    if scelta_prog:
        print(f"\n✅ Termine scelto: {scelta_prog} -> {dizionario_programmazione[scelta_prog]}")
    else:
        print("\n❌ Selezione annullata.")
    input("\nPremi Invio per continuare con il prossimo test...")
    os.system('cls' if os.name == 'nt' else 'clear')

    # Test 3: Lista di libri, con menù numerato (numbered=True)
    print("--- TEST 3: Scegli un libro famoso (menù numerato) ---")
    scelta_libro = menu(dizionario_libri, numbered=True, p="Scegli il numero del libro")
    if scelta_libro:
        print(f"\n✅ Libro scelto: '{scelta_libro}' di {dizionario_libri[scelta_libro]}")
    else:
        print("\n❌ Selezione annullata.")
    input("\nPremi Invio per continuare con il prossimo test...")
    os.system('cls' if os.name == 'nt' else 'clear')

    # Test 4: Elementi chimici, con prompt personalizzato e senza lista di chiavi
    print("--- TEST 4: Scegli un elemento chimico (prompt personalizzato) ---")
    scelta_elemento = menu(dizionario_elementi, p="Elemento? > ", keyslist=False)
    if scelta_elemento:
        print(f"\n✅ Elemento scelto: {scelta_elemento} (Simbolo: {dizionario_elementi[scelta_elemento]})")
    else:
        print("\n❌ Selezione annullata.")

    print("\n\n--- Test completati! ---")

# --- 3. ESECUZIONE DELLO SCRIPT ---
if __name__ == "__main__":
    run_tests()