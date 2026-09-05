import sys
import json
import math
import os
import re

# Aggiungo la cartella corrente al path per importare GBUtils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from GBUtils import menu, Acusticator, parse_pan_parts

VERSION = "1.5.2" # I tagli della banda non si incrociano piu'
APP_NAME = "Acu_Maker"
APP_AUTHOR = "Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5)"
RELEASE_DATE = "5 settembre 2026"
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Acu_Collection.json")
DEFAULT_VOL = 0.5

# Le forme d'onda, comprese le quattro di rumore introdotte in Acusticator V7.2
ONDE = {1: 'Sinusoide', 2: 'Quadra', 3: 'Triangolare', 4: 'DenteSega',
        5: 'Rumore bianco', 6: 'Rumore rosa', 7: 'Rumore marrone',
        8: 'Rumore azzurro'}
KIND_RUMORE = (5, 6, 7, 8)
BANDA_DEFAULT = "200-3000"
# Un passo di banda e' un rapporto, non una quantita' di Hertz: cosi' vale
# lo stesso in ogni punto dello spettro. 2 elevato a un dodicesimo e' il
# rapporto di un semitono, circa il sei per cento.
PASSO_BANDA = 2 ** (1 / 12)
# I nomi delle dodici note e i loro semitoni, usati sia per trasportare
# sia per tradurre una frequenza nel nome di nota piu' vicino.
NOMI_NOTE = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
SEMITONI_NOTE = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
# Quanto e' larga la banda che nasce da una nota quando si passa a un
# rumore: mezza ottava sotto e mezza ottava sopra, cioe' una banda larga
# un'ottava che si sente intonata su quella nota.
MEZZA_OTTAVA = 2 ** 0.5


def is_portamento(val):
    return isinstance(val, str) and '.' in val


def is_rumore(kind):
    """Vero se questa forma d'onda vuole una banda al posto della nota."""
    return kind in KIND_RUMORE


def banda_pezzi(val):
    """I quattro valori di una banda, come stringhe.

    Restituisce (basso_inizio, alto_inizio, basso_fine, alto_fine). Gli
    ultimi due sono vuoti se la banda e' ferma. Per la pausa e per la banda
    assente il primo contiene il testo e gli altri sono vuoti.
    """
    testo = str(val).strip()
    if testo.lower() in ('p', 'n', ''):
        return testo.lower(), '', '', ''
    momenti = testo.split('.')
    if len(momenti) > 2:
        return testo, '', '', ''
    tagli = []
    for momento in momenti:
        if '-' not in momento:
            return testo, '', '', ''
        basso, _, alto = momento.partition('-')
        tagli.append((basso.strip(), alto.strip()))
    if len(tagli) == 1:
        return tagli[0][0], tagli[0][1], '', ''
    return tagli[0][0], tagli[0][1], tagli[1][0], tagli[1][1]


def banda_componi(basso_in, alto_in, basso_fi='', alto_fi=''):
    """Rimette insieme i quattro valori, o solo i due se la banda e' ferma."""
    if not alto_in:
        return basso_in
    if basso_fi and alto_fi:
        return f"{basso_in}-{alto_in}.{basso_fi}-{alto_fi}"
    return f"{basso_in}-{alto_in}"


# Quale valore muove ciascun selettore. Gli indici sono nell'ordine
# restituito da banda_pezzi: basso all'inizio, alto all'inizio, basso alla
# fine, alto alla fine.
SCELTA_BANDA = {
    1: (0,),           # taglio basso, dove parte
    2: (1,),           # taglio alto, dove parte
    3: (0, 1),         # tutta la banda di partenza
    4: (2,),           # taglio basso, dove arriva
    5: (3,),           # taglio alto, dove arriva
    6: (2, 3),         # tutta la banda d'arrivo
    7: (0, 1, 2, 3),   # tutto insieme, trasla la scivolata intera
}
NOMI_SCELTA = {
    1: "taglio basso alla partenza",
    2: "taglio alto alla partenza",
    3: "banda di partenza",
    4: "taglio basso all'arrivo",
    5: "taglio alto all'arrivo",
    6: "banda d'arrivo",
    7: "tutti e quattro i valori",
}


def banda_ordinata(pezzi):
    """Vero se in ogni momento il taglio basso sta sotto quello alto.

    Una banda rovesciata non e' un effetto ma un incidente: il motore
    spegne tutto sotto il taglio basso e tutto sopra quello alto, e cio'
    che sopravvive e' solo la sfumatura di un bordo, una fettina di
    spettro che non ha piu' niente a che vedere con i due valori scritti.
    Tagli uguali invece vanno bene: danno una campana stretta.
    """
    coppie = [(pezzi[0], pezzi[1])]
    if pezzi[2] or pezzi[3]:
        coppie.append((pezzi[2], pezzi[3]))
    for basso, alto in coppie:
        try:
            if float(basso) > float(alto):
                return False
        except (TypeError, ValueError):
            return False
    return True


def alterna_scivolata(val):
    """Accende o spegne la scivolata di una banda.

    Una banda ferma, per esempio 200-3000, si sdoppia in 200-3000.200-3000 e
    comincia a poter scorrere; una che gia' scorre torna ferma sulla sua
    banda di partenza.
    """
    b_in, a_in, b_fi, _ = banda_pezzi(val)
    if not a_in:
        return str(val).strip()
    if b_fi:
        return banda_componi(b_in, a_in)
    return banda_componi(b_in, a_in, b_in, a_in)


# I tagli non escono da questi limiti: sotto e sopra non si sente niente e
# non ha senso continuare a spostarli. Il motore poi restringe ancora, fra 40
# Hz e 12 kHz, che e' la fascia in cui l'orecchio e le casse lavorano davvero.
BANDA_MINIMA = 20.0
BANDA_MASSIMA = 20000.0


def normalizza_banda(testo):
    """Controlla e riordina una banda scritta a mano.

    Restituisce la banda ripulita, con i valori riportati dentro i limiti
    udibili, oppure None se non e' leggibile. Serve a non lasciare entrare
    nel preset una banda che poi farebbe cadere l'editor.
    """
    from GBUtils import parse_banda

    grezzo = str(testo).strip().lower()
    if grezzo in ('p', 'n'):
        return grezzo
    try:
        parse_banda(grezzo)
    except (ValueError, TypeError):
        return None

    def limita(pezzo):
        try:
            v = float(pezzo)
        except ValueError:
            return None
        return str(round(max(BANDA_MINIMA, min(BANDA_MASSIMA, v))))

    pezzi = banda_pezzi(grezzo)
    if not pezzi[1]:
        return None
    limitati = [limita(p) if p else '' for p in pezzi]
    if any(x is None for x in limitati):
        return None
    if not banda_ordinata(limitati):
        return None
    return banda_componi(*limitati)


def scala_taglio(taglio, direzione, passo=PASSO_BANDA):
    """Sposta un taglio per rapporto, rispettando il suo portamento.

    Un taglio puo' essere un solo valore, per esempio 200, oppure due uniti
    da un punto, per esempio 200.400, e allora si spostano tutti e due
    insieme cosi' la scivolata resta quella che era.
    """
    def uno(testo):
        try:
            valore = float(testo)
        except ValueError:
            return testo
        nuovo = valore * (passo if direzione > 0 else 1.0 / passo)
        nuovo = max(BANDA_MINIMA, min(BANDA_MASSIMA, nuovo))
        return str(round(nuovo))

    testo = str(taglio).strip()
    if not testo or testo.lower() in ('p', 'n'):
        return testo
    if '.' in testo:
        pezzi = testo.split('.')
        if len(pezzi) == 2:
            return f"{uno(pezzi[0])}.{uno(pezzi[1])}"
    return uno(testo)


def nota_in_hz(val):
    """La frequenza di una nota singola, o None se non e' leggibile.

    Accetta il nome della nota, per esempio c4 o d#4, e anche il numero,
    che nel campo della nota e' gia' una frequenza in Hertz.
    """
    if isinstance(val, (int, float)):
        return float(val) if val > 0 else None
    grezzo = str(val).strip().lower()
    if grezzo.isdigit():
        return float(grezzo) if float(grezzo) > 0 else None
    incontro = re.match(r"^([a-g])([#b]?)(\d)$", grezzo)
    if not incontro:
        return None
    lettera, alterazione, ottava = incontro.groups()
    semitono = SEMITONI_NOTE[lettera]
    if alterazione == '#':
        semitono += 1
    elif alterazione == 'b':
        semitono -= 1
    midi = 12 + semitono + 12 * int(ottava)
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def hz_in_nota(freq):
    """Il nome della nota piu' vicina a una frequenza.

    Resta fra c0 e g9, che sono le note scritte con una cifra sola di
    ottava, le uniche che l'editor e il motore sanno poi rileggere.
    """
    if not freq or freq <= 0:
        return 'c4'
    midi = round(69 + 12 * math.log2(freq / 440.0))
    midi = max(12, min(127, midi))
    return f"{NOMI_NOTE[midi % 12]}{midi // 12 - 1}"


def banda_da_hz(freq):
    """I due tagli della banda larga un'ottava centrata su una frequenza."""
    basso = max(BANDA_MINIMA, min(BANDA_MASSIMA, freq / MEZZA_OTTAVA))
    alto = max(BANDA_MINIMA, min(BANDA_MASSIMA, freq * MEZZA_OTTAVA))
    return str(round(basso)), str(round(alto))


def hz_da_banda(basso, alto):
    """Il centro di una banda, cioe' la frequenza che vi si sente intonata.

    E' la media geometrica dei due tagli e non quella aritmetica: in musica
    conta il rapporto, quindi il centro fra 200 e 3000 sta a meta' strada
    contando le ottave e non gli Hertz.
    """
    try:
        return (float(basso) * float(alto)) ** 0.5
    except (TypeError, ValueError):
        return None


def nota_in_banda(val):
    """Traduce il primo campo dalla nota alla banda, scivolata compresa.

    Una nota diventa la banda larga un'ottava che le sta intorno, e una
    nota che scivola diventa una banda che scorre fra le bande delle due
    note, cosi' passando a un rumore la scivolata resta quella che era.
    """
    if isinstance(val, (int, float)):
        momenti = [val]
    else:
        testo = str(val).strip().lower()
        if testo == 'p':
            return 'p'
        momenti = testo.split('.')
        if len(momenti) != 2:
            momenti = [testo]
    frequenze = [nota_in_hz(m) for m in momenti]
    if frequenze[0] is None:
        return BANDA_DEFAULT
    basso_in, alto_in = banda_da_hz(frequenze[0])
    if len(frequenze) == 1 or frequenze[1] is None:
        return banda_componi(basso_in, alto_in)
    basso_fi, alto_fi = banda_da_hz(frequenze[1])
    return banda_componi(basso_in, alto_in, basso_fi, alto_fi)


def banda_in_nota(val):
    """Traduce il primo campo dalla banda alla nota, scivolata compresa.

    La nota e' quella piu' vicina al centro della banda, e una banda che
    scorre diventa una nota che scivola fra i centri delle due bande, cosi'
    passando a un'onda intonata la scivolata resta quella che era.
    """
    b_in, a_in, b_fi, a_fi = banda_pezzi(val)
    if not a_in:
        return 'p' if str(b_in).strip().lower() == 'p' else 'c4'
    centro_in = hz_da_banda(b_in, a_in)
    if centro_in is None:
        return 'c4'
    nota_in = hz_in_nota(centro_in)
    if not b_fi:
        return nota_in
    centro_fi = hz_da_banda(b_fi, a_fi)
    if centro_fi is None:
        return nota_in
    return f"{nota_in}.{hz_in_nota(centro_fi)}"


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
    semitone = SEMITONI_NOTE[note_letter]
    if accidental == '#': semitone += 1
    elif accidental == 'b': semitone -= 1
    
    midi_num = 12 + semitone + 12 * octave
    new_midi = midi_num + semitones
    
    if new_midi < 0: new_midi = 0
    if new_midi > 127: new_midi = 127
    
    new_octave = (new_midi // 12) - 1
    new_note = NOMI_NOTE[new_midi % 12]
    return f"{new_note}{new_octave}"

class EditorState:
    def __init__(self, preset_data):
        self.preset = json.loads(json.dumps(preset_data))
        self.focus_type = 'score'
        self.focus_idx = 0
        self.focus_param = 0
        self.port_focus = 3
        
        self.steps = {
            'banda': PASSO_BANDA,
            'note': 10.0,
            'dur': 0.02,
            'pan': 10,
            'vol': 10,
            'a': 0.001,
            'd': 0.001,
            's': 1.0,
            'r': 0.001
        }
        self.modified = False
        self.running = True

def pan_to_user(val):
    if is_portamento(val):
        parts = parse_pan_parts(val)
        p1 = int(round(float(parts[0]) * 100))
        p2 = int(round(float(parts[1]) * 100))
        return f"{p1}.{p2}"
    else:
        return str(int(round(float(val) * 100)))

def user_to_pan(val_str):
    val_str = str(val_str).strip()
    if is_portamento(val_str):
        parts = parse_pan_parts(val_str)
        p1 = max(-1.0, min(1.0, float(parts[0]) / 100.0))
        p2 = max(-1.0, min(1.0, float(parts[1]) / 100.0))
        s1 = str(int(p1)) if p1.is_integer() else str(round(p1, 2))
        s2 = str(int(p2)) if p2.is_integer() else str(round(p2, 2))
        return f"{s1}.{s2}"
    else:
        fval = float(val_str) / 100.0
        return max(-1.0, min(1.0, round(fval, 2)))

def vol_to_user(val):
    if is_portamento(val):
        parts = parse_pan_parts(val)
        v1 = int(round((DEFAULT_VOL + float(parts[0])) * 100))
        v2 = int(round((DEFAULT_VOL + float(parts[1])) * 100))
        return f"{v1}.{v2}"
    else:
        v = int(round((DEFAULT_VOL + float(val)) * 100))
        return str(max(0, min(100, v)))

def user_to_vol(val_str):
    val_str = str(val_str).strip()
    if is_portamento(val_str):
        parts = parse_pan_parts(val_str)
        d1 = (float(parts[0]) / 100.0) - DEFAULT_VOL
        d2 = (float(parts[1]) / 100.0) - DEFAULT_VOL
        d1 = max(-0.5, min(0.5, d1))
        d2 = max(-0.5, min(0.5, d2))
        s1 = str(int(d1)) if d1.is_integer() else str(round(d1, 2))
        s2 = str(int(d2)) if d2.is_integer() else str(round(d2, 2))
        return f"{s1}.{s2}"
    else:
        v = float(val_str) / 100.0
        d = v - DEFAULT_VOL
        return max(-0.5, min(0.5, round(d, 2)))

def get_status_string(state):
    if state.focus_type == 'score':
        quad = state.preset['score'][state.focus_idx]
        param_names = ["Nota", "Durata", "Pan", "Volume"]
        if state.focus_param == 0 and is_rumore(state.preset.get('kind', 1)):
            pezzi = list(banda_pezzi(quad[0]))
            scelti = SCELTA_BANDA.get(state.port_focus, ())
            if pezzi[1]:
                mostrati = [f"<{p}>" if i in scelti else p
                            for i, p in enumerate(pezzi) if p]
                if len(mostrati) == 4:
                    val_str = f"{mostrati[0]}-{mostrati[1]}.{mostrati[2]}-{mostrati[3]}"
                else:
                    val_str = f"{mostrati[0]}-{mostrati[1]}"
            else:
                val_str = pezzi[0]
            s = f"Sc.{state.focus_idx+1} Banda: {val_str}"
        elif state.focus_param == 0:
            val = quad[0]
            if is_portamento(val):
                parts = val.split('.')
                p1 = f"<{parts[0]}>" if state.port_focus in (1, 3) else parts[0]
                p2 = f"<{parts[1]}>" if state.port_focus in (2, 3) else parts[1]
                val_str = f"{p1}.{p2}"
            else:
                val_str = str(val)
            s = f"Sc.{state.focus_idx+1} {param_names[0]}: {val_str}"
        elif state.focus_param == 2:
            val_user = pan_to_user(quad[2])
            if is_portamento(val_user):
                parts = val_user.split('.')
                p1 = f"<{parts[0]}>" if state.port_focus in (1, 3) else parts[0]
                p2 = f"<{parts[1]}>" if state.port_focus in (2, 3) else parts[1]
                val_str = f"{p1}.{p2}"
            else:
                val_str = str(val_user)
            s = f"Sc.{state.focus_idx+1} {param_names[2]}: {val_str}"
        elif state.focus_param == 3:
            val_user = vol_to_user(quad[3])
            if is_portamento(val_user):
                parts = val_user.split('.')
                p1 = f"<{parts[0]}>" if state.port_focus in (1, 3) else parts[0]
                p2 = f"<{parts[1]}>" if state.port_focus in (2, 3) else parts[1]
                val_str = f"{p1}.{p2}"
            else:
                val_str = str(val_user)
            s = f"Sc.{state.focus_idx+1} {param_names[3]}: {val_str}"
        else:
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
        if is_portamento(vol_delta):
            parts = parse_pan_parts(vol_delta)
            v1 = max(0.0, min(1.0, DEFAULT_VOL + float(parts[0])))
            v2 = max(0.0, min(1.0, DEFAULT_VOL + float(parts[1])))
            vol_param = (v1, v2)
        else:
            vol_param = max(0.0, min(1.0, DEFAULT_VOL + float(vol_delta)))
        score_flat.extend([note, dur, pan, vol_param])
    Acusticator(score_flat, kind=state.preset['kind'], adsr=state.preset['adsr'], sync=False)

def play_quad(state):
    q = state.preset['score'][state.focus_idx]
    note, dur, pan, vol_delta = q
    if is_portamento(vol_delta):
        parts = parse_pan_parts(vol_delta)
        v1 = max(0.0, min(1.0, DEFAULT_VOL + float(parts[0])))
        v2 = max(0.0, min(1.0, DEFAULT_VOL + float(parts[1])))
        vol_param = (v1, v2)
    else:
        vol_param = max(0.0, min(1.0, DEFAULT_VOL + float(vol_delta)))
    Acusticator([note, dur, pan, vol_param], kind=state.preset['kind'], adsr=state.preset['adsr'], sync=False)

def transpose_single(val_str, direction, step):
    if val_str.lower() == 'p': return 'p'
    try:
        fval = float(val_str)
        if fval.is_integer():
            return str(int(fval + direction * step))
        return str(round(fval + direction * step, 2))
    except ValueError:
        return transpose_note(val_str, direction)

def inc_dec_value(state, direction):
    """Muove il valore corrente di un passo.

    Restituisce None se si e' mosso, altrimenti la ragione per cui e'
    rimasto fermo, che il chiamante mostra al posto della riga di stato.
    """
    era_modificato = state.modified
    state.modified = True
    if state.focus_type == 'score':
        quad = state.preset['score'][state.focus_idx]
        param = state.focus_param
        if param == 0 and is_rumore(state.preset.get('kind', 1)):
            pezzi = list(banda_pezzi(quad[0]))
            if not pezzi[1]:
                # pausa oppure nessuna banda: non c'e' niente da spostare
                state.modified = era_modificato
                return "Qui non c'e' una banda da spostare"
            passo = state.steps.get('banda', PASSO_BANDA)
            nuovi = list(pezzi)
            for i in SCELTA_BANDA.get(state.port_focus, (0, 1)):
                if nuovi[i]:
                    nuovi[i] = scala_taglio(nuovi[i], direction, passo)
            if not banda_ordinata(nuovi):
                # Il taglio basso finirebbe sopra quello alto: la banda
                # non lascerebbe passare piu' niente di sensato.
                state.modified = era_modificato
                return 'I tagli si incrocerebbero, fermo qui'
            quad[0] = banda_componi(*nuovi)
        elif param == 0:
            val = quad[0]
            if is_portamento(val):
                parts = val.split('.')
                if state.port_focus in (1, 3):
                    parts[0] = transpose_single(parts[0], direction, state.steps['note'])
                if state.port_focus in (2, 3):
                    parts[1] = transpose_single(parts[1], direction, state.steps['note'])
                quad[0] = f"{parts[0]}.{parts[1]}"
            else:
                if isinstance(val, str) and val.lower() != 'p':
                    quad[0] = transpose_note(val, direction)
                elif isinstance(val, (int, float)):
                    quad[0] = round(val + direction * state.steps['note'], 2)
        elif param == 1:
            quad[1] = max(0.0, round(quad[1] + direction * state.steps['dur'], 3))
        elif param == 2:
            val_user = pan_to_user(quad[2])
            step_val = int(state.steps['pan'])
            if is_portamento(val_user):
                parts = val_user.split('.')
                p1, p2 = int(parts[0]), int(parts[1])
                if state.port_focus in (1, 3):
                    p1 = max(-100, min(100, p1 + direction * step_val))
                if state.port_focus in (2, 3):
                    p2 = max(-100, min(100, p2 + direction * step_val))
                quad[2] = user_to_pan(f"{p1}.{p2}")
            else:
                p = int(val_user)
                p = max(-100, min(100, p + direction * step_val))
                quad[2] = user_to_pan(str(p))
        elif param == 3:
            val_user = vol_to_user(quad[3])
            step_val = int(state.steps['vol'])
            if is_portamento(val_user):
                parts = val_user.split('.')
                v1, v2 = int(parts[0]), int(parts[1])
                if state.port_focus in (1, 3):
                    v1 = max(0, min(100, v1 + direction * step_val))
                if state.port_focus in (2, 3):
                    v2 = max(0, min(100, v2 + direction * step_val))
                quad[3] = user_to_vol(f"{v1}.{v2}")
            else:
                v = int(val_user)
                v = max(0, min(100, v + direction * step_val))
                quad[3] = user_to_vol(str(v))
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
            param_name = ["Nota", "Durata", "Pan (-100..100)", "Volume (0..100)"][state.focus_param] if state.focus_type == 'score' else ["A", "D", "S", "R"][state.focus_param]
            if state.focus_type == 'score':
                if state.focus_param == 0 and is_rumore(state.preset.get('kind', 1)):
                    scelti = SCELTA_BANDA.get(state.port_focus, ())
                    if len(scelti) == 1:
                        param_name = f"{NOMI_SCELTA[state.port_focus]}, in Hz"
                    else:
                        param_name = ("Banda intera, per esempio 200-3000 oppure "
                                      "100-1000.800-1800, n, p")
                elif state.focus_param == 0:
                    current_val = state.preset['score'][state.focus_idx][0]
                    if is_portamento(current_val):
                        if state.port_focus == 1: param_name = "Nota (partenza)"
                        elif state.port_focus == 2: param_name = "Nota (arrivo)"
                        else: param_name = "Nota (entrambe)"
                elif state.focus_param == 2:
                    current_val = state.preset['score'][state.focus_idx][2]
                    if is_portamento(current_val):
                        if state.port_focus == 1: param_name = "Pan partenza (-100..100)"
                        elif state.port_focus == 2: param_name = "Pan arrivo (-100..100)"
                        else: param_name = "Pan entrambi (-100..100)"
                elif state.focus_param == 3:
                    current_val = state.preset['score'][state.focus_idx][3]
                    if is_portamento(current_val):
                        if state.port_focus == 1: param_name = "Volume partenza (0..100)"
                        elif state.port_focus == 2: param_name = "Volume arrivo (0..100)"
                        else: param_name = "Volume entrambi (0..100)"
                    
            val = input(f"\nInserisci nuovo valore per {param_name}: ")
            if val.strip():
                try:
                    if state.focus_type == 'score':
                        if state.focus_param == 0 and is_rumore(state.preset.get('kind', 1)):
                            pezzi = list(banda_pezzi(state.preset['score'][state.focus_idx][0]))
                            scritto = val.strip()
                            scelti = SCELTA_BANDA.get(state.port_focus, ())
                            if not pezzi[1] or len(scelti) > 1 or '-' in scritto:
                                # Si sta scrivendo la banda intera
                                candidata = scritto
                            else:
                                pezzi[scelti[0]] = scritto
                                candidata = banda_componi(*pezzi)
                            # Si controlla prima di scrivere: una banda illeggibile
                            # resterebbe nel preset e farebbe cadere l'editor dopo.
                            pulita = normalizza_banda(candidata)
                            if pulita is None:
                                print("\nBanda non valida. Il trattino separa il "
                                      "taglio basso da quello alto, per esempio "
                                      "200-3000. Il punto separa la banda di "
                                      "partenza da quella d'arrivo, per esempio "
                                      "100-1000.800-1800. Vale anche n per nessuna "
                                      "banda e p per pausa. Il taglio basso deve "
                                      "restare sotto quello alto.")
                            else:
                                state.preset['score'][state.focus_idx][0] = pulita
                                state.modified = True
                        elif state.focus_param == 0:
                            current_val = state.preset['score'][state.focus_idx][0]
                            if is_portamento(current_val):
                                val_to_insert = val
                                if val.lower() == 'p':
                                    val_to_insert = 'p'
                                elif val.replace('-', '').replace('.', '', 1).isdigit():
                                    fval = float(val)
                                    val_to_insert = str(int(fval)) if fval.is_integer() else str(fval)
                                parts = current_val.split('.')
                                if state.port_focus in (1, 3): parts[0] = val_to_insert
                                if state.port_focus in (2, 3): parts[1] = val_to_insert
                                state.preset['score'][state.focus_idx][0] = f"{parts[0]}.{parts[1]}"
                                state.modified = True
                            else:
                                if val.lower() == 'p': state.preset['score'][state.focus_idx][0] = 'p'
                                else:
                                    try: state.preset['score'][state.focus_idx][0] = float(val)
                                    except ValueError: state.preset['score'][state.focus_idx][0] = val
                                state.modified = True
                        elif state.focus_param == 2:
                            current_val = state.preset['score'][state.focus_idx][2]
                            if is_portamento(current_val):
                                parts_user = pan_to_user(current_val).split('.')
                                if state.port_focus in (1, 3): parts_user[0] = val
                                if state.port_focus in (2, 3): parts_user[1] = val
                                state.preset['score'][state.focus_idx][2] = user_to_pan(f"{parts_user[0]}.{parts_user[1]}")
                            else:
                                state.preset['score'][state.focus_idx][2] = user_to_pan(val)
                            state.modified = True
                        elif state.focus_param == 3:
                            current_val = state.preset['score'][state.focus_idx][3]
                            if is_portamento(current_val):
                                parts_user = vol_to_user(current_val).split('.')
                                if state.port_focus in (1, 3): parts_user[0] = val
                                if state.port_focus in (2, 3): parts_user[1] = val
                                state.preset['score'][state.focus_idx][3] = user_to_vol(f"{parts_user[0]}.{parts_user[1]}")
                            else:
                                state.preset['score'][state.focus_idx][3] = user_to_vol(val)
                            state.modified = True
                        else:
                            state.preset['score'][state.focus_idx][state.focus_param] = float(val)
                            state.modified = True
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
            
        elif key == '.':
            if state.focus_type == 'score' and state.focus_param in (0, 2, 3):
                param_idx = state.focus_param
                val = state.preset['score'][state.focus_idx][param_idx]
                if param_idx == 0 and is_rumore(state.preset.get('kind', 1)):
                    # Su una banda il punto sdoppia la banda in partenza e
                    # arrivo, o la richiude. Senza questo ramo la banda
                    # verrebbe presa per un valore singolo e duplicata.
                    nuova = alterna_scivolata(val)
                    if nuova != str(val).strip():
                        state.preset['score'][state.focus_idx][0] = nuova
                        state.port_focus = 3
                        state.modified = True
                elif is_portamento(val):
                    if param_idx == 0:
                        parts = val.split('.')
                        new_val = parts[0] if state.port_focus in (1, 3) else parts[1]
                        if new_val.replace('-', '').replace('.', '', 1).isdigit():
                            fval = float(new_val)
                            new_val = int(fval) if fval.is_integer() else fval
                        state.preset['score'][state.focus_idx][0] = new_val
                    elif param_idx == 2:
                        user_parts = pan_to_user(val).split('.')
                        new_val_str = user_parts[0] if state.port_focus in (1, 3) else user_parts[1]
                        state.preset['score'][state.focus_idx][2] = user_to_pan(new_val_str)
                    elif param_idx == 3:
                        user_parts = vol_to_user(val).split('.')
                        new_val_str = user_parts[0] if state.port_focus in (1, 3) else user_parts[1]
                        state.preset['score'][state.focus_idx][3] = user_to_vol(new_val_str)
                else:
                    if param_idx == 0:
                        if isinstance(val, float) and val.is_integer(): val = int(val)
                        state.preset['score'][state.focus_idx][0] = f"{val}.{val}"
                    elif param_idx == 2:
                        u_val = pan_to_user(val)
                        state.preset['score'][state.focus_idx][2] = user_to_pan(f"{u_val}.{u_val}")
                    elif param_idx == 3:
                        u_val = vol_to_user(val)
                        state.preset['score'][state.focus_idx][3] = user_to_vol(f"{u_val}.{u_val}")
                    state.port_focus = 3
                state.modified = True
        elif key in ('1', '2', '3', '4', '5', '6', '7') and \
                state.focus_type == 'score' and state.focus_param == 0 and \
                is_rumore(state.preset.get('kind', 1)):
            # Sulla banda i numeri scelgono quale dei quattro valori muovere.
            # Da 4 in su hanno senso solo se la banda scorre davvero.
            scelta = int(key)
            pezzi = banda_pezzi(state.preset['score'][state.focus_idx][0])
            if scelta <= 3 or pezzi[2]:
                state.port_focus = scelta
                print(f"\r{' ' * 60}\r{NOMI_SCELTA[scelta]}", end="", flush=True)
            else:
                print(f"\r{' ' * 60}\rLa banda e' ferma: premi il punto per "
                      "farla scorrere", end="", flush=True)
            continue
        elif key in ('1', '2', '3'):
            if state.focus_type == 'score' and state.focus_param in (0, 2, 3):
                if is_portamento(
                        state.preset['score'][state.focus_idx][state.focus_param]):
                    state.port_focus = int(key)
        elif key == '4':
            if state.focus_type == 'score' and state.focus_param in (0, 2, 3):
                param_idx = state.focus_param
                val = state.preset['score'][state.focus_idx][param_idx]
                if is_portamento(val):
                    if param_idx == 0:
                        parts = val.split('.')
                        state.preset['score'][state.focus_idx][0] = f"{parts[1]}.{parts[0]}"
                    elif param_idx == 2:
                        u_parts = pan_to_user(val).split('.')
                        state.preset['score'][state.focus_idx][2] = user_to_pan(f"{u_parts[1]}.{u_parts[0]}")
                    elif param_idx == 3:
                        u_parts = vol_to_user(val).split('.')
                        state.preset['score'][state.focus_idx][3] = user_to_vol(f"{u_parts[1]}.{u_parts[0]}")
                    state.modified = True
        elif key == 'i':
            # Inverte la scivolata: quello che partiva arriva e viceversa.
            # Su una nota fa la stessa cosa del 4, che resta per abitudine.
            if state.focus_type == 'score' and state.focus_param in (0, 2, 3):
                param_idx = state.focus_param
                val = state.preset['score'][state.focus_idx][param_idx]
                if param_idx == 0 and is_rumore(state.preset.get('kind', 1)):
                    b_in, a_in, b_fi, a_fi = banda_pezzi(val)
                    if b_fi:
                        state.preset['score'][state.focus_idx][0] = banda_componi(
                            b_fi, a_fi, b_in, a_in)
                        state.modified = True
                elif is_portamento(val):
                    if param_idx == 0:
                        parti = val.split('.')
                        state.preset['score'][state.focus_idx][0] = f"{parti[1]}.{parti[0]}"
                    elif param_idx == 2:
                        u = pan_to_user(val).split('.')
                        state.preset['score'][state.focus_idx][2] = user_to_pan(f"{u[1]}.{u[0]}")
                    elif param_idx == 3:
                        u = vol_to_user(val).split('.')
                        state.preset['score'][state.focus_idx][3] = user_to_vol(f"{u[1]}.{u[0]}")
                    state.modified = True
        elif key == 'y':
            if state.focus_type == 'score':
                curr_quad = list(state.preset['score'][state.focus_idx])
                state.preset['score'].insert(state.focus_idx + 1, curr_quad)
                state.focus_idx += 1
                state.modified = True
                print(f"\r{' ' * 50}\rDuplicata Sc.{state.focus_idx}", end="", flush=True)
                continue
        elif key in ('c', 'v'):
            avviso = inc_dec_value(state, 1 if key == 'c' else -1)
            if avviso:
                print(f"\r{' ' * 60}\r{avviso}", end="", flush=True)
                continue
        elif key == 'z': state.focus_param = (state.focus_param - 1) % 4
        elif key == 'x': state.focus_param = (state.focus_param + 1) % 4
        elif key == 'b':
            if state.focus_type == 'score':
                rumore = is_rumore(state.preset.get('kind', 1))
                param_key = ['banda' if rumore else 'note',
                             'dur', 'pan', 'vol'][state.focus_param]
                param_name = ["Banda (rapporto)" if rumore else "Nota", "Durata",
                              "Pan (-100..100)", "Volume (0..100)"][state.focus_param]
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
                rumore = is_rumore(state.preset.get('kind', 1))
                param_key = ['banda' if rumore else 'note',
                             'dur', 'pan', 'vol'][state.focus_param]
                defaults = [BANDA_DEFAULT if rumore else 'c4', 0.5, 0.0, 0.0]
                default_steps = [PASSO_BANDA if rumore else 10.0, 0.02, 10, 10]
                state.preset['score'][state.focus_idx][state.focus_param] = defaults[state.focus_param]
                state.steps[param_key] = default_steps[state.focus_param]
            else:
                param_key = ['a', 'd', 's', 'r'][state.focus_param]
                defaults = [0.002, 0.0, 100.0, 0.002]
                state.preset['adsr'][state.focus_param] = defaults[state.focus_param]
                state.steps[param_key] = 0.1
            state.modified = True
            
        elif key == 'm':
            ans = input("\nSei sicuro di voler svuotare questo preset (s/n)? ")
            if ans.lower().strip() == 's':
                state.preset['score'] = [['c4', 0.5, 0.0, 0.0]]
                state.preset['adsr'] = [0.002, 0.0, 100.0, 0.002]
                state.preset['kind'] = 1
                state.focus_type = 'score'
                state.focus_idx = 0
                state.focus_param = 0
                state.modified = True
                print("Preset svuotato.")
            handle_print(state, force_newline=True)
            continue
            
        elif key == 'w':
            prima_rumore = is_rumore(state.preset['kind'])
            state.preset['kind'] = (state.preset['kind'] % len(ONDE)) + 1
            state.modified = True
            # Passando fra note e rumore il primo campo cambia significato:
            # si converte quello che c'e', scivolata compresa, altrimenti
            # resterebbe illeggibile e il portamento andrebbe perso.
            adesso_rumore = is_rumore(state.preset['kind'])
            if prima_rumore != adesso_rumore:
                for quartina in state.preset['score']:
                    if str(quartina[0]).strip().lower() == 'p':
                        continue
                    quartina[0] = (nota_in_banda(quartina[0]) if adesso_rumore
                                   else banda_in_nota(quartina[0]))
                state.port_focus = 3
                print(f"\r{' ' * 60}\rOnda: {ONDE[state.preset['kind']]}, "
                      f"il primo campo ora e' "
                      f"{'la banda' if adesso_rumore else 'la nota'}",
                      end="", flush=True)
            else:
                print(f"\r{' ' * 60}\rOnda: {ONDE[state.preset['kind']]}",
                      end="", flush=True)
            continue
        elif key in ('a', 'd', 's', 'r'):
            state.focus_type = 'adsr'
            state.focus_param = {'a':0, 'd':1, 's':2, 'r':3}[key]
        elif key == 'q':
            state.focus_type = 'score'
            state.focus_param = 0 # Torna alla Nota della quartina corrente
        elif key == 'f':
            state.focus_type = 'score'
            primo = BANDA_DEFAULT if is_rumore(state.preset.get('kind', 1)) else 'c4'
            new_quad = [primo, 0.5, 0.0, 0.0]
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
                print(f"{indicator} [{i+1}] Nota: {q[0]}, Dur: {q[1]}, Pan: {pan_to_user(q[2])}, Vol: {vol_to_user(q[3])}")
            print("-------------------")
            handle_print(state, force_newline=True)
            continue
        elif key == '?':
            print("\n--- Lista Tasti Rapidi ---")
            print("Spazio: Riproduce l'intero preset")
            print("Invio: Modifica il valore selezionato")
            print(".: Attiva o disattiva il portamento del valore corrente")
            print("1, 2, 3: Fuoco sul portamento (1: part, 2: arr, 3: entrambi)")
            print("i: Inverte il portamento, partenza e arrivo si scambiano")
            print("4: Come i, sulle note, e resta per abitudine")
            print("y: Duplica la quartina corrente")
            print("c / v: Incrementa / Decrementa valore corrente")
            print("z / x: Passa al parametro precedente / successivo")
            print("b: Modifica il passo (step) per il parametro corrente")
            print("n: Ripristina valori di default per il parametro corrente")
            print("m: Svuota l'intero preset (imposta a default)")
            print("w: Cambia forma d'onda, otto in tutto: Seno, Quadra, Triangolare,")
            print("   Dente di Sega e i quattro rumori, bianco, rosa, marrone e azzurro.")
            print("   Con un rumore il primo campo della quartina non e' la nota ma la")
            print("   banda del filtro, per esempio 200-3000, oppure n per nessuna banda.")
            print("   Il trattino separa il taglio basso da quello alto. Il punto sdoppia")
            print("   la banda in partenza e arrivo, per esempio 100-1000.800-1800, che")
            print("   si legge parte come 100-1000 e diventa 800-1800.")
            print("   Sulla banda i numeri scelgono cosa muovono poi c e v:")
            print("   1 il basso di partenza, 2 l'alto di partenza, 3 la banda di")
            print("   partenza, 4 il basso d'arrivo, 5 l'alto d'arrivo, 6 la banda")
            print("   d'arrivo, 7 tutti e quattro i valori insieme.")
            print("   Da 4 in su hanno senso solo se la banda scorre davvero.")
            print("   I tagli si spostano per rapporto, non per Hertz, e restano")
            print("   sempre fra 20 e 20000 Hz. Il taglio basso non scavalca mai")
            print("   quello alto: c e v si fermano prima e lo dicono.")
            print("   Cambiando forma il primo campo si converte da solo: la nota")
            print("   diventa la banda larga un'ottava che le sta intorno e la banda")
            print("   diventa la nota piu' vicina al suo centro. La scivolata non si")
            print("   perde, resta scivolata su tutte e otto le forme d'onda.")
            print("a, d, s, r: Passa alla modifica dell'inviluppo ADSR")
            print("q: Passa alla modifica della quartina (Nota)")
            print("f / j: Inserisce nuova quartina prima / dopo quella corrente")
            print("g / h: Sposta il cursore alla quartina precedente / successiva e riproduce")
            print("e: Elimina la quartina corrente")
            print("l: Mostra la lista completa delle quartine")
            print("?: Mostra questa lista di tasti rapidi")
            print("Esc: Esce dall'editor")
            print("--------------------------")
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
        menu_dict["+"] = "Nuovo preset vuoto (Default)"
        menu_dict["/"] = "Cerca preset per parola chiave"
        print("\nScegli un preset (digita '?' per la lista, Esc/Invio vuoto per uscire):")
        scelta = menu(d=menu_dict, p="Preset> ", show=False, ordered=True)
        
        if not scelta:
            break
            
        if scelta == "+":
            new_name = get_unique_name(db, "nuovo_preset")
            db[new_name] = {
                "descrizione": "Nuovo preset vuoto",
                "score": [["c4", 0.5, 0.0, 0.0]],
                "kind": 1,
                "adsr": [0.002, 0.0, 100.0, 0.002]
            }
            edit_mode(db, new_name)
            continue
            
        if scelta == "/":
            query = input("\nInserisci parole chiave da cercare (spazio per separare): ").strip().lower()
            if not query:
                continue
            words = query.split()
            
            risultati = {}
            for k, v in sorted(db.items()):
                test_str = (k + " " + v.get("descrizione", "")).lower()
                if all(w in test_str for w in words):
                    risultati[k] = v.get("descrizione", "")
                    
            if not risultati:
                print("Nessun preset trovato corrispondente alla ricerca.")
                continue
            elif len(risultati) == 1:
                scelta = list(risultati.keys())[0]
                print(f"\nTrovato 1 preset: '{scelta}'")
            else:
                print(f"\nTrovati {len(risultati)} preset. Scegli uno (Esc/Invio per annullare):")
                scelta = menu(d=risultati, p="Risultati> ", show=True, ordered=True)
                if not scelta:
                    continue

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
