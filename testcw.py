# --- Incolla qui la definizione completa di CWzator V8.1 ---

# --- Script di Test Timing ---

# Dizionario Morse (necessario per calcolo durata attesa)
morse_map_test = {
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
	"ò":"---.", "à":".--.-", "ù":"..--", "è":"..-..", "é":"..-..", "ì":".---."}

def calculate_expected_duration(msg, wpm, l, s, p):
    """Calcola la durata teorica del messaggio Morse in secondi."""
    if wpm <= 0: return 0
    T = 1.2 / float(wpm)
    dot_duration = T * (p / 50.0)
    dash_duration = 3.0 * T * (l / 30.0)
    intra_gap = T * (s / 50.0) # Gap tra simboli dentro una lettera
    letter_gap = 3.0 * T * (s / 50.0) # Gap tra lettere in una parola
    word_gap = 7.0 * T * (s / 50.0) # Gap tra parole

    total_duration = 0
    words = msg.lower().split()

    for w_idx, word in enumerate(words):
        valid_letters = "".join(ch for ch in word if ch in morse_map_test)
        for l_idx, letter in enumerate(valid_letters):
            code = morse_map_test.get(letter, None)
            if not code: continue

            for s_idx, symbol in enumerate(code):
                if symbol == '.':
                    total_duration += dot_duration
                elif symbol == '-':
                    total_duration += dash_duration

                # Aggiungi gap intra-simbolo se non è l'ultimo simbolo
                if s_idx < len(code) - 1:
                    total_duration += intra_gap

            # Aggiungi gap tra lettere se non è l'ultima lettera della parola
            if l_idx < len(valid_letters) - 1:
                total_duration += letter_gap

        # Aggiungi gap tra parole se non è l'ultima parola E se ci sono lettere valide
        # nella parola attuale O nella successiva (per gestire spazi multipli)
        if w_idx < len(words) - 1:
             if valid_letters or any(c in morse_map_test and morse_map_test.get(c) for c in words[w_idx+1]):
                 total_duration += word_gap

    # Aggiungi il piccolo silenzio finale aggiunto da CWzator
    final_silence_duration = 0.005
    if total_duration > 0: # Aggiungi solo se c'era audio
        total_duration += final_silence_duration

    return total_duration

# --- Parametri del Test ---
import random,	time
test_string = "the quick brown fox jumps over the lazy dog 1234567890 test di velocita"
num_iterations = 10
min_wpm = 10
max_wpm = 80
min_l = 20
max_l = 60
min_s = 15
max_s = 75
min_p = 15
max_p = 55

print("--- Inizio Test Timing CWzator ---")
print(f"Test String: '{test_string}'")
print("-" * 30)

total_diff_perc = 0

for i in range(num_iterations):
    # Genera parametri casuali
    current_wpm = random.randint(min_wpm, max_wpm)
    current_l = random.randint(min_l, max_l)
    current_s = random.randint(min_s, max_s)
    current_p = random.randint(min_p, max_p)

    print(f"Iterazione {i+1}/{num_iterations}: WPM={current_wpm}, L={current_l}, S={current_s}, P={current_p}")

    # Calcola durata attesa
    expected_duration = calculate_expected_duration(test_string, current_wpm, current_l, current_s, current_p)

    # Misura durata effettiva (usando sync=True)
    start_time = time.perf_counter()
    play_handle, actual_rwpm = CWzator(
        msg=test_string,
        wpm=current_wpm,
        l=current_l,
        s=current_s,
        p=current_p,
        sync=True # Fondamentale per misurare il tempo bloccante
    )
    end_time = time.perf_counter()
    actual_duration = end_time - start_time

    # Calcola differenze
    difference = actual_duration - expected_duration
    diff_percentage = (difference / expected_duration * 100.0) if expected_duration > 0 else 0
    total_diff_perc += diff_percentage

    # Stampa risultati iterazione
    print(f"  Durata Attesa  : {expected_duration:.4f} s")
    print(f"  Durata Effettiva: {actual_duration:.4f} s")
    print(f"  Differenza     : {difference:+.4f} s ({diff_percentage:+.2f}%)")
    # print(f"  RWPM Calcolato : {actual_rwpm:.2f}") # Opzionale
    print("-" * 10)

print("-" * 30)
average_diff_perc = total_diff_perc / num_iterations
print(f"Differenza Percentuale Media: {average_diff_perc:.2f}%")
print("--- Fine Test Timing CWzator ---")
