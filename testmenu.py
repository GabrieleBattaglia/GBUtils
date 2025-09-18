def menu(d={}, p="> ", ntf="Scelta non valida", show=True, show_only=False, keyslist=True, pager=20, show_on_filter=True, numbered=False):
    """V4.1 – mercoledì 18 settembre 2025 - Gabriele Battaglia & Partner di programmazione
    Integrata la modalità 'numbered' nel ciclo principale.
    Ora supporta il pager e il filtraggio interattivo multi-cifra.
    """
    import sys, time, os

    # La funzione key() rimane invariata.
    def key(prompt=""):
        print(prompt, end='', flush=True)
        if os.name == 'nt':
            import msvcrt
            ch = msvcrt.getwch()
            if ch == '\x08': return ch;
            if ch == '\r': return ch;
            if ch == '\x1b': return ch;
            if ch == '?': return ch;
            if ord(ch) == 127: return '\x08';
            if ch in ('\x00', '\xe0'): msvcrt.getwch(); return '\x00';
            return ch
        else:
            import select, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    r, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if r: sys.stdin.read(2); return '\x00';
                    else: return '\x1b';
                elif ord(ch) == 127: return '\x08';
                elif ch in ['\n', '\r']: return '\r';
                else: return ch;
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # *** MODIFICA 1: La funzione Mostra ora gestisce anche la modalità numerata ***
    def Mostra(items_to_show, pager, is_numbered, num_map=None):
        """Visualizza una lista di elementi, gestendo il pager e la modalità numerata."""
        count = 0
        total = len(items_to_show)
        if total == 0:
            print("\n" + ntf)
            return True
        print("\n--- Menu ---")
        for item in items_to_show:
            if is_numbered:
                # 'item' è una stringa numerica (es. "12")
                original_key = num_map[item]
                desc = d[original_key]
                print(f"[{item}] -- {desc}")
            else:
                # 'item' è la chiave originale (es. "Torino")
                desc = d.get(item, "N/A")
                print(f"- ({item}) -- {desc};")

            count += 1
            if pager > 0 and count % pager == 0 and count < total:
                prompt_pager = f"--- [Pag: {int(count/pager)}] ({count-pager+1}-{count} di {total}) Premi Invio per continuare, ESC per uscire ---"
                ch_pager = key(prompt_pager)
                print()
                if ch_pager == '\x1b':
                    print("--- Exit from paging ---")
                    return False
        print(f"---------- [End of list] ({count}/{total}) ----------")
        return True

    def Listaprompt_autocomplete(keys_list, current_input):
        """Genera un prompt che suggerisce i prossimi caratteri validi."""
        if not keys_list or len(keys_list) <= 1: return ">";
        next_chars = set()
        input_len = len(current_input)
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
    current_input = ""
    last_displayed = None
    num_map = {} # Dizionario per mappare il numero (stringa) alla chiave originale

    # *** MODIFICA 2: La logica di 'numbered' viene preparata qui all'inizio ***
    if numbered:
        num_map = {str(i): k for i, k in enumerate(orig_keys, 1)}
        # Le "chiavi" su cui opereremo saranno i numeri stessi, come stringhe
        orig_keys = list(num_map.keys())
    
    if not d: print("No options available."); return None;
    if len(d) == 1 and not show_only: return list(d.keys())[0];
    if show_only: Mostra(orig_keys, pager, numbered, num_map); return None;

    if show:
        if not Mostra(orig_keys, pager, numbered, num_map):
            return None
        last_displayed = orig_keys

    # --- Ciclo Principale di Input/Filtro (ora unico per entrambe le modalità) ---
    while True:
        # Il filtro funziona sia per le chiavi testuali che per i numeri (come stringhe)
        filtered = [k for k in orig_keys if valid_match(k, current_input)]
        
        # Gestione del filtro vuoto
        if not filtered and current_input != "":
            print("\n" + ntf)
            current_input = ""
            continue

        # Selezione automatica se la scelta è univoca
        if len(filtered) == 1 and current_input != "":
            final_choice = filtered[0]
            print()
            # Se numerato, restituisce la chiave originale, non il numero
            return num_map[final_choice] if numbered else final_choice
        
        # Mostra la lista filtrata se richiesto
        if show_on_filter and current_input != "" and filtered != last_displayed:
            print("\n-----------------------")
            if not Mostra(filtered, pager, numbered, num_map):
                last_displayed = filtered[:]; continue;
            last_displayed = filtered[:]
        
        # Preparazione del prompt
        if numbered:
            prompt_str = p if p != "> " else f"(1-{len(orig_keys)})>"
        elif keyslist:
            prompt_str = Listaprompt_autocomplete(filtered, current_input)
        else:
            prompt_str = p
        full_prompt = " " + prompt_str + current_input
        
        # Ottieni input
        user_char = key(full_prompt)
        
        # Processa input
        if user_char in ['\r', '\n']:
            print()
            if current_input == "": return None;
            if len(filtered) == 1:
                final_choice = filtered[0]
                return num_map[final_choice] if numbered else final_choice
            else:
                 print("\n--- Scelta ambigua. Premi '?' per la lista. ---")
        elif user_char == '\x1b': print(); return None;
        elif user_char == '?':
            if not Mostra(filtered, pager, numbered, num_map): last_displayed = filtered[:]; continue;
            last_displayed = filtered[:]
        elif user_char == '\x08':
            if current_input:
                current_input = current_input[:-1]
                print('\b \b', end='', flush=True)
        elif user_char == '\x00': pass
        else:
            # *** MODIFICA 3: Accetta solo cifre in modalità numerata ***
            if numbered and not user_char.isdigit():
                continue # Ignora input non numerico
            
            print(user_char, end='', flush=True)
            current_input += user_char
            
            # Controllo rapido dopo l'aggiunta del carattere
            quick_filtered = [k for k in orig_keys if valid_match(k, current_input)]
            if len(quick_filtered) == 1:
                final_choice = quick_filtered[0]
                print()
                return num_map[final_choice] if numbered else final_choice

    return None
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