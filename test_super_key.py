import sys
import os

# Assicuriamoci che GBUtils sia importabile dalla cartella locale
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from GBUtils import key

def main():
    print("--- Test Minimale key() V6.0 ---")
    print("Premi i tasti per vedere il valore restituito e il codice ASCII.")
    print("Premi 'ctrl-q' per uscire.\n")

    while True:
        # Usiamo un prompt vuoto per il massimo controllo sulla riga
        tasto = key(attesa=60)
        
        if tasto == '':
            print("\rTimeout 60s scaduto.                       ", end="")
            continue
            
        # Calcoliamo il codice ASCII se è un carattere singolo
        if len(tasto) == 1:
            codice = ord(tasto)
            info = f"Valore: '{tasto}' | ASCII: {codice}"
        else:
            info = f"Valore: '{tasto}' | (Tasto Speciale)"
            
        # Stampiamo sovrascrivendo la riga e mantenendo il focus
        # Usiamo spazi alla fine per pulire eventuali residui di stringhe lunghe precedenti
        print(f"\r{info}{' ' * 20}", end="", flush=True)
        
        # Uscita con ctrl-q (o q se non mappato diversamente)
        if tasto == 'ctrl-q' or tasto == 'q':
            print("\n\nTest concluso.")
            break

if __name__ == "__main__":
    main()
