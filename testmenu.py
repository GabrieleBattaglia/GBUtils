def menu(d={}, p="> ", ntf="Scelta non valida", show=True, show_only=False, keyslist=True, pager=20, show_on_filter=True, numbered=False):
    """V4.6 - Ottimizzata per Partner di Programmazione
    Miglioramenti:
    - ESC nel pager interrompe la lista ma NON chiude il menu.
    - Logica di filtraggio ottimizzata (evita doppi calcoli).
    - Gestione input e backspace più pulita.
    """
    import sys, os

    # --- Funzioni Helper ---
    def lcp(strings):
        """Calcola il prefisso comune più lungo."""
        return os.path.commonprefix(strings) if strings else ""

    def key(prompt=""):
        """Legge un singolo carattere (Windows/Unix)."""
        if prompt:
            print(prompt, end='', flush=True)
        
        char = ''
        if os.name == 'nt':
            import msvcrt
            ch = msvcrt.getwch()
            # Gestione tasti speciali (frecce, funzionali) che inviano doppio codice
            if ch in ('\x00', '\xe0'):
                msvcrt.getwch() 
                return '\x00'
            char = ch
        else:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                char = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        # Normalizzazione tasti
        if char == '\x1b': return '\x1b' # ESC
        if char in ('\r', '\n'): return '\r' # INVIO
        if char in ('\x08', '\x7f'): return '\x08' # BACKSPACE
        return char

    def Mostra(items_to_show, pager, is_numbered, num_map=None):
        """
        Mostra la lista. 
        Restituisce: True se completato, False se interrotto da ESC.
        """
        count = 0
        total = len(items_to_show)
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
            # Logica Pager
            if pager > 0 and count % pager == 0 and count < total:
                page_num = int(count / pager)
                prompt_pager = f"--- Pagina {page_num} [{count}/{total}] - Premi un tasto (ESC per stop) ---"
                ch_pager = key(prompt_pager)
                print("\r" + " " * len(prompt_pager) + "\r", end='', flush=True) # Pulisce riga pager
                
                if ch_pager == '\x1b': 
                    print("--- Visualizzazione interrotta ---")
                    return False # Interruzione richiesta
        
        print(f"---------- Fine Lista [{count}/{total}] ----------")
        return True

    def get_autocomplete_prompt(keys_list, current_input):
        """Genera i suggerimenti per il prompt."""
        if not keys_list or len(keys_list) <= 1: return "> "
        
        input_len = len(current_input)
        next_chars = set()
        for k in keys_list:
            if len(k) > input_len:
                next_chars.add(k[input_len].upper()) # Case insensitive display
            
        if not next_chars: return "> "
        return f"({', '.join(sorted(next_chars))})> "

    def valid_match(key_item, sub):
        return key_item.lower().startswith(sub.lower())

    # --- Logica Principale ---
    orig_keys = sorted(d.keys())
    
    # Mappa per menu numerato
    num_map = {}
    if numbered:
        num_map = {str(i): k for i, k in enumerate(orig_keys, 1)}
        orig_keys = list(num_map.keys())

    # Gestione casi limite iniziali
    if not d: 
        print("Nessuna opzione disponibile.")
        return None
    if show_only:
        Mostra(orig_keys, pager, numbered, num_map)
        return None
    if len(d) == 1 and not show: # Se c'è solo una scelta e non mostriamo il menu, la selezioniamo subito?
        # Nota: ho mantenuto la logica originale, ma attenzione se l'utente vuole confermare.
        return list(d.keys())[0]

    # Visualizzazione Iniziale
    if show:
        if not Mostra(orig_keys, pager, numbered, num_map):
            # Se premo ESC durante la PRIMA visualizzazione (senza aver digitato nulla), esco.
            return None

    user_input = ""
    last_displayed_list = orig_keys[:] # Copia della lista
    disable_autocomplete_once = False

    while True:
        # 1. Filtra le chiavi
        filtered = [k for k in orig_keys if valid_match(k, user_input)]
        
        # 2. Gestione Autocompletamento (LCP)
        # Se c'è un solo match esatto o l'utente ha cancellato, non autocompletare
        current_display_input = user_input
        if keyslist and not numbered and not disable_autocomplete_once and len(filtered) > 1:
            common = lcp(filtered)
            if len(common) > len(user_input):
                user_input = common
                current_display_input = common
        
        disable_autocomplete_once = False # Reset flag

        # 3. Aggiornamento lista filtrata finale (dopo eventuale autocompletamento)
        # Ottimizzazione: ricalcoliamo solo se l'input è cambiato
        final_filtered = [k for k in orig_keys if valid_match(k, current_display_input)]

        # 4. Controllo Match Unico
        if len(final_filtered) == 1 and len(current_display_input) > 0:
            # Opzionale: stampa automatica della scelta effettuata
            choice = final_filtered[0]
            print(f"\nSelezionato: {choice}")
            return num_map.get(choice, choice)

        # 5. Visualizzazione Lista Filtrata (Show on Filter)
        if show and show_on_filter and final_filtered != last_displayed_list:
            print("\n-----------------------")
            # Qui la modifica chiave: se Mostra ritorna False (ESC), NON usciamo dal while,
            # ma semplicemente smettiamo di stampare e andiamo al prompt.
            Mostra(final_filtered, pager, numbered, num_map)
            last_displayed_list = final_filtered[:]

        # 6. Costruzione Prompt
        prompt_str = p
        if numbered:
             if p == "> ": prompt_str = f"(1-{len(orig_keys)})> "
        elif keyslist:
            prompt_str = get_autocomplete_prompt(final_filtered, current_display_input)
        
        full_prompt = f"\n{prompt_str}{current_display_input}"
        
        # 7. Input Utente
        char = key(full_prompt)

        # 8. Gestione Tasti
        if char == '\r': # Invio
            print() # A capo estetico
            if current_display_input in final_filtered:
                return num_map.get(current_display_input, current_display_input)
            elif len(final_filtered) == 1:
                 return num_map.get(final_filtered[0], final_filtered[0])
            elif user_input == "":
                return None # Invio a vuoto = Annulla
            else:
                print(f"--- {ntf} ---")
                # Non resettiamo last_displayed_list così non ristampa tutto subito

        elif char == '\x1b': # ESC
            print()
            return None

        elif char == '?': # Richiesta ristampa
            print("\n")
            Mostra(final_filtered, pager, numbered, num_map)
            last_displayed_list = final_filtered[:] # Reset stato visualizzato

        elif char == '\x08': # Backspace
            if user_input:
                user_input = user_input[:-1]
                # Trucco visivo: cancella carattere a schermo
                print('\b \b', end='', flush=True) 
                last_displayed_list = None # Forza refresh lista
                disable_autocomplete_once = True # Evita che LCP riaggiunga subito la lettera cancellata

        elif char == '\x00': 
            pass # Ignora tasti speciali

        else: # Carattere normale
            # Se numerato, accetta solo cifre
            if numbered and not char.isdigit():
                pass
            else:
                user_input += char
                print(char, end='', flush=True) # Echo del carattere
                last_displayed_list = None # Forza refresh

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