import sys
import json
import os
import re

# Aggiungo la cartella corrente al path per importare GBUtils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from GBUtils import menu, Acusticator

VERSION = "0.2.0" # Gestione ADSR completa e vincoli
APP_NAME = "Acu_Maker"
APP_AUTHOR = "Gabriele Battaglia & Stella"
RELEASE_DATE = "23 aprile 2026"
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Acu_Collection.json")
DEFAULT_VOL = 0.5

def get_keypress():
    """Legge un singolo tasto, gestendo le frecce direzionali in modo nativo e sicuro."""
    if os.name == 'nt':
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):
            ch2 = msvcrt.getwch()
            if ch2 == 'H': return 'up'
            if ch2 == 'P': return 'down'
            if ch2 == 'K': return 'left'
            if ch2 == 'M': return 'right'
            return ch + ch2
        if ch == '\r': return 'enter'
        if ch == '\x1b': return 'esc'
        if ch == ' ': return 'space'
        return ch
    else:
        import select
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b': # Escape sequence (potrebbe essere una freccia)
                r, _, _ = select.select([sys.stdin], [], [], 0.05)
                if r:
                    sys.stdin.read(1) # scarta '['
                    ch2 = sys.stdin.read(1)
                    if ch2 == 'A': return 'up'
                    if ch2 == 'B': return 'down'
                    if ch2 == 'C': return 'right'
                    if ch2 == 'D': return 'left'
                return 'esc'
            if ch == '\n' or ch == '\r': return 'enter'
            if ch == ' ': return 'space'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {
            "do_re_mi": {
                "descrizione": "Tre note C D E ascendenti",
                "score": [
                    ["c4", 0.5, -1.0, 0.0],
                    ["d4", 0.5, 0.0, 0.0],
                    ["e4", 0.5, 1.0, 0.0]
                ],
                "kind": 1,
                "adsr": [0.002, 0.0, 100.0, 0.002]
            }
        }
        save_db(default_db)
        return default_db
        
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

def get_unique_name(db, base_name):
    if base_name not in db:
        return base_name
    i = 0
    while f"{base_name}{i}" in db:
        i += 1
    return f"{base_name}{i}"

def transpose_note(note_str, semitones):
    if note_str.lower() == 'p': return note_str
    match = re.match(r"^([a-g])([#b]?)(\d)$", note_str.lower())
    if not match: return note_str
    note_letter, accidental, octave_str = match.groups()
    octave = int(octave_str)
    note_base = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
    semitone = note_base[note_letter]
    if accidental == '#': semitone += 1
    elif accidental == 'b': semitone -= 1
    
    midi_num = 12 + semitone + 12 * octave
    new_midi = midi_num + semitones
    
    if new_midi < 0: new_midi = 0
    if new_midi > 127: new_midi = 127
    
    notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
    new_octave = (new_midi // 12) - 1
    new_note = notes[new_midi % 12]
    return f"{new_note}{new_octave}"

class EditorState:
    def __init__(self, preset_data):
        self.preset = json.loads(json.dumps(preset_data))
        self.focus_type = 'score'
        self.focus_idx = 0
        self.focus_param = 0
        
        self.steps = {
            'note': 10.0,
            'dur': 0.1,
            'pan': 0.1,
            'vol': 0.1,
            'a': 0.001,
            'd': 0.001,
            's': 1.0,
            'r': 0.001
        }
        self.modified = False
        self.running = True

def get_status_string(state):
    if state.focus_type == 'score':
        quad = state.preset['score'][state.focus_idx]
        param_names = ["Nota", "Durata", "Pan", "VolD"]
        s = f"Sc.{state.focus_idx+1} {param_names[state.focus_param]}: {quad[state.focus_param]}"
    else:
        adsr = list(state.preset['adsr'])
        adsr[state.focus_param] = f"<{adsr[state.focus_param]}>"
        s = f"ADSR: {adsr[0]} {adsr[1]} {adsr[2]} {adsr[3]}"
    return s

def handle_print(state, force_newline=False):
    s = get_status_string(state)
    if force_newline:
        print()
    clear_line = " " * 50
    print(f"\r{clear_line}\r{s}", end="", flush=True)

def play_preset(state):
    score_flat = []
    for q in state.preset['score']:
        note, dur, pan, vol_delta = q
        vol = max(0.0, min(1.0, DEFAULT_VOL + vol_delta))
        score_flat.extend([note, dur, pan, vol])
    Acusticator(score_flat, kind=state.preset['kind'], adsr=state.preset['adsr'], sync=False)

def play_quad(state):
    q = state.preset['score'][state.focus_idx]
    note, dur, pan, vol_delta = q
    vol = max(0.0, min(1.0, DEFAULT_VOL + vol_delta))
    Acusticator([note, dur, pan, vol], kind=state.preset['kind'], adsr=state.preset['adsr'], sync=False)

def inc_dec_value(state, direction):
    state.modified = True
    if state.focus_type == 'score':
        quad = state.preset['score'][state.focus_idx]
        param = state.focus_param
        if param == 0:
            val = quad[0]
            if isinstance(val, str) and val.lower() != 'p':
                quad[0] = transpose_note(val, direction)
            elif isinstance(val, (int, float)):
                quad[0] = round(val + direction * state.steps['note'], 2)
        elif param == 1:
            quad[1] = max(0.0, round(quad[1] + direction * state.steps['dur'], 3))
        elif param == 2:
            quad[2] = max(-1.0, min(1.0, round(quad[2] + direction * state.steps['pan'], 2)))
        elif param == 3:
            quad[3] = round(quad[3] + direction * state.steps['vol'], 2)
    elif state.focus_type == 'adsr':
        param = state.focus_param
        val = state.preset['adsr'][param]
        step_key = ['a', 'd', 's', 'r'][param]
        step = state.steps[step_key]
        new_val = round(val + direction * step, 3)
        
        if param in (0, 1, 3):
            new_val = max(0.0, new_val)
            others = sum([state.preset['adsr'][i] for i in (0,1,3) if i != param])
            if new_val + others > 100.0:
                new_val = round(100.0 - others, 3)
        elif param == 2:
            new_val = max(0.0, min(100.0, new_val))
            
        state.preset['adsr'][param] = new_val

def edit_mode(db, preset_name):
    state = EditorState(db[preset_name])
    print(f"\n--- Edit Preset: {preset_name} ---")
    handle_print(state, force_newline=True)
    
    while state.running:
        key = get_keypress()

        if key == 'space':
            play_preset(state)
        elif key == 'enter':
            param_name = ["Nota", "Durata", "Pan", "Delta Volume"][state.focus_param] if state.focus_type == 'score' else ["A", "D", "S", "R"][state.focus_param]
            val = input(f"\nInserisci nuovo valore per {param_name}: ")
            if val.strip():
                try:
                    if state.focus_type == 'score':
                        if state.focus_param == 0:
                            if val.lower() == 'p': state.preset['score'][state.focus_idx][0] = 'p'
                            else:
                                try: state.preset['score'][state.focus_idx][0] = float(val)
                                except ValueError: state.preset['score'][state.focus_idx][0] = val
                        else:
                            state.preset['score'][state.focus_idx][state.focus_param] = float(val)
                    elif state.focus_type == 'adsr':
                        param = state.focus_param
                        new_val = float(val)
                        if param in (0, 1, 3):
                            new_val = max(0.0, new_val)
                            others = sum([state.preset['adsr'][i] for i in (0,1,3) if i != param])
                            if new_val + others > 100.0:
                                new_val = round(100.0 - others, 3)
                        elif param == 2:
                            new_val = max(0.0, min(100.0, new_val))
                        state.preset['adsr'][param] = new_val
                    state.modified = True
                except ValueError:
                    print("Valore non valido.")
            handle_print(state, force_newline=True)
            
        elif key == 'c': inc_dec_value(state, 1)
        elif key == 'v': inc_dec_value(state, -1)
        elif key == 'z': state.focus_param = (state.focus_param - 1) % 4
        elif key == 'x': state.focus_param = (state.focus_param + 1) % 4
        elif key == 'b':
            if state.focus_type == 'score':
                param_key = ['note', 'dur', 'pan', 'vol'][state.focus_param]
                param_name = ["Nota", "Durata", "Pan", "Delta Volume"][state.focus_param]
            else:
                param_key = ['a', 'd', 's', 'r'][state.focus_param]
                param_name = ["Attacco", "Decadimento", "Sustain", "Rilascio"][state.focus_param]
            val = input(f"\nInserisci nuovo step per {param_name} (attuale: {state.steps[param_key]}): ")
            if val.strip():
                try:
                    state.steps[param_key] = float(val)
                except ValueError:
                    print("Valore non valido.")
            handle_print(state, force_newline=True)
        elif key == 'n':
            if state.focus_type == 'score':
                param_key = ['note', 'dur', 'pan', 'vol'][state.focus_param]
                defaults = ['c4', 0.5, 0.0, 0.0]
                state.preset['score'][state.focus_idx][state.focus_param] = defaults[state.focus_param]
                state.steps[param_key] = 0.1
            else:
                param_key = ['a', 'd', 's', 'r'][state.focus_param]
                defaults = [0.002, 0.0, 100.0, 0.002]
                state.preset['adsr'][state.focus_param] = defaults[state.focus_param]
                state.steps[param_key] = 0.1
            state.modified = True
            
        elif key == 'w':
            state.preset['kind'] = (state.preset['kind'] % 4) + 1
            state.modified = True
            waves = {1: 'Sinusoide', 2: 'Quadra', 3: 'Triangolare', 4: 'DenteSeg'}
            print(f"\r{' ' * 50}\rOnda: {waves[state.preset['kind']]}", end="", flush=True)
            continue
        elif key in ('a', 'd', 's', 'r'):
            state.focus_type = 'adsr'
            state.focus_param = {'a':0, 'd':1, 's':2, 'r':3}[key]
        elif key == 'q':
            state.focus_type = 'score'
            state.focus_param = 0 # Torna alla Nota della quartina corrente
        elif key == 'f':
            state.focus_type = 'score'
            new_quad = ['c4', 0.5, 0.0, 0.0]
            state.preset['score'].insert(state.focus_idx, new_quad)
            state.modified = True
            print(f"\r{' ' * 50}\rIns. Sc.{state.focus_idx+1}", end="", flush=True)
            continue
        elif key == 'g':
            state.focus_type = 'score'
            if state.focus_idx > 0: state.focus_idx -= 1
            play_quad(state)
        elif key == 'h':
            state.focus_type = 'score'
            if state.focus_idx < len(state.preset['score']) - 1: state.focus_idx += 1
            play_quad(state)
        elif key == 'j':
            state.focus_type = 'score'
            new_quad = ['c4', 0.5, 0.0, 0.0]
            state.preset['score'].insert(state.focus_idx + 1, new_quad)
            state.focus_idx += 1
            state.modified = True
            print(f"\r{' ' * 50}\rIns. Sc.{state.focus_idx+1}", end="", flush=True)
            continue
        elif key == 'e':
            if state.focus_type == 'score' and len(state.preset['score']) > 1:
                state.preset['score'].pop(state.focus_idx)
                if state.focus_idx >= len(state.preset['score']):
                    state.focus_idx = len(state.preset['score']) - 1
                state.modified = True
                print(f"\r{' ' * 50}\rEliminato. Ora Sc.{state.focus_idx+1}", end="", flush=True)
                continue
        elif key == 'l':
            print("\n--- Lista Score ---")
            for i, q in enumerate(state.preset['score']):
                indicator = "->" if i == state.focus_idx else "  "
                print(f"{indicator} [{i+1}] Nota: {q[0]}, Dur: {q[1]}, Pan: {q[2]}, VolD: {q[3]}")
            print("-------------------")
            handle_print(state, force_newline=True)
            continue
        elif key == 'esc':
            state.running = False

        if state.running:
            handle_print(state, force_newline=False)

    print()
    if state.modified:
        print("\nModifiche rilevate. Scegli un'opzione:")
        scelta = menu({"1": "Sovrascrivi preset corrente", "2": "Salva come nuovo preset", "3": "Esci senza salvare"}, p="Salva> ", show=True)
        if scelta == "1":
            db[preset_name] = state.preset
            print(f"Preset '{preset_name}' aggiornato.")
        elif scelta == "2":
            new_name = input("Inserisci il nome breve del nuovo preset (max 50 car., no spazi): ").strip()
            new_name = new_name.replace(" ", "")[:50]
            if not new_name:
                new_name = "nuovo_preset"
            
            new_name = get_unique_name(db, new_name)
            new_desc = input("Inserisci una descrizione: ")
            
            state.preset['descrizione'] = new_desc
            db[new_name] = state.preset
            print(f"Salvato come nuovo preset: '{new_name}'.")
        else:
            print("Modifiche ignorate.")

def main():
    print(f"--- {APP_NAME} v{VERSION} ---")
    print(f"Autori: {APP_AUTHOR} - {RELEASE_DATE}\n")

    db = load_db()
    print(f"La libreria contiene {len(db)} preset.")

    while True:
        # Ordiniamo esplicitamente il dizionario alfabeticamente per nome del preset
        menu_dict = {k: v.get("descrizione", "") for k, v in sorted(db.items())}
        print("\nScegli un preset (digita '?' per la lista, Esc/Invio vuoto per uscire):")
        scelta = menu(d=menu_dict, p="Preset> ", show=False, ordered=True)
        
        if not scelta:
            break
            
        print(f"\nHai selezionato: '{scelta}'")
        action_dict = {"c": "Carica (Edit Mode)", "e": "Elimina"}
        azione = menu(d=action_dict, p="Azione> ", show=True)
        
        if azione == "e":
            if input(f"Sei sicuro di voler eliminare '{scelta}'? (s/n): ").lower() == 's':
                del db[scelta]
                save_db(db)
                print("Preset eliminato.")
        elif azione == "c":
            edit_mode(db, scelta)
            
    print("\nSalvataggio libreria in corso...")
    save_db(db)
    print("Arrivederci!")

if __name__ == "__main__":
    main()
