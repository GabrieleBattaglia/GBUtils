from pyo import Server, SigTo, Sine, Pan, Pattern
import numpy as np

def Sonify3(data=[], duration=10000, vol=0.35, ptm=False):
    # Controllo della lunghezza dei dati
    if len(data) < 5:
        print("Data serie too short.")
        return

    # Tentativo di conversione dei dati in float
    try:
        data = [float(i) for i in data]
    except ValueError:
        print("Impossibile convertire i dati in float.")
        return

    # Calcolo dei parametri sonori
    soundlowerlimit = 65.41  # Frequenza di Do2
    soundupperlimit = 4186.01  # Frequenza di Do8
    soundrange = soundupperlimit - soundlowerlimit
    datamin = min(data)
    datamax = max(data)
    datarange = datamax - datamin if datamax != datamin else 1  # Evita divisione per zero

    # Calcolo del timing
    total_duration_sec = duration / 1000.0  # Conversione da ms a secondi
    datalength = len(data)
    singlesoundduration = total_duration_sec / datalength

    # Inizializzazione del server
    s = Server().boot()
    s.start()

    # Inizializzazione del segnale di frequenza
    if ptm:
        freq = SigTo(value=0, time=singlesoundduration)
    else:
        freq = SigTo(value=0, time=0)

    # Mappatura dei dati alla frequenza
    def map_data_to_freq(val):
        norm_val = (val - datamin) / datarange
        freq_val = soundlowerlimit + norm_val * soundrange
        return freq_val

    # Oscillatore sinusoidale
    osc = Sine(freq=freq, mul=vol)
    
    # Panning stereo
    pan_pos = SigTo(value=0.0, time=total_duration_sec)
    pan = Pan(osc, pan=pan_pos).out()

    # Funzione per aggiornare la frequenza
    idx = [0]  # Utilizziamo una lista per mantenere lo stato mutable

    def update_freq():
        if idx[0] < datalength:
            next_freq = map_data_to_freq(data[idx[0]])
            freq.value = next_freq
            idx[0] += 1
        else:
            # Fermiamo il server dopo l'ultimo valore
            pat.stop()
            s.stop()
            s.shutdown()

    # Pattern per gestire il timing degli aggiornamenti di frequenza
    pat = Pattern(update_freq, time=singlesoundduration).play()

    # Spostamento del panning da sinistra a destra
    pan_pos.value = 1.0  # Da 0.0 (sinistra) a 1.0 (destra)

    # Manteniamo il programma in esecuzione finché il suono non termina
    try:
        s.gui(locals())
    except (KeyboardInterrupt, SystemExit):
        pat.stop()
        s.stop()
        s.shutdown()

print("Test")
# Esempio di dati
data = [100, 200, 150, 300, 250, 400, 350]

# Chiamata alla funzione
Sonify3(data, duration=12300, vol=0.5, ptm=True)
