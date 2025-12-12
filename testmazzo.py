
# test_mazzo.py
# Script per testare la classe Mazzo (salvata in mazzo_classe.py)

def print_header(title):
	print("\n" + "="*10 + f" {title} " + "="*10)

def print_test_case(description, expected, action_func):
	print(f"\n--- Test: {description} ---")
	print(f"Azione: Eseguo {action_func.__name__ if hasattr(action_func, '__name__') else 'azione specifica'}")
	print(f"Atteso: {expected}")
	result = action_func()
	print(f"Ottenuto: {result}")
	# Spesso utile mostrare lo stato completo dopo l'azione
	if isinstance(result, Mazzo): # Se l'azione ha creato un mazzo
		print(f"Stato mazzo: {result.stato_mazzo()}")
	elif 'mazzo' in locals() or 'mazzo' in globals(): # Se un mazzo è coinvolto nell'azione
					# Cerchiamo l'oggetto mazzo nell'ambiente dell'azione se possibile
					# Questo è un po' un hack, sarebbe meglio passare il mazzo esplicitamente
					# Ma per questo script di test può andare
					mazzo_obj = None
					try:
									# Tentativo di accedere al mazzo nell'ambiente della funzione lambda/azione
									# Questo funzionerà se 'mazzo' è definito nello scope che crea la lambda
									if action_func.__closure__:
													for cell in action_func.__closure__:
																	if isinstance(cell.cell_contents, Mazzo):
																					mazzo_obj = cell.cell_contents
																					break
					except AttributeError:
									pass # Non tutte le funzioni hanno __closure__

					if mazzo_obj:
									print(f"Stato mazzo post-azione: {mazzo_obj.stato_mazzo()}")
									# Mostra le carte nelle pile rilevanti
									print(f"   {mazzo_obj.mostra_carte('mazzo')}")
									print(f"   {mazzo_obj.mostra_carte('pescate')}")
									print(f"   {mazzo_obj.mostra_carte('scarti')}")
									print(f"   {mazzo_obj.mostra_carte('permanenti')}")


# --- Inizio Test ---

print_header("Test Inizializzazione")

# 1. Mazzo Francese Singolo
print("\n--- Test: Creazione Mazzo Francese (1 mazzo) ---")
print("Azione: Creo Mazzo(tipo_francese=True, num_mazzi=1)")
print("Atteso: Oggetto Mazzo con 52 carte in 'carte', 0 nelle altre liste.")
try:
	mazzo_fr = Mazzo(tipo_francese=True, num_mazzi=1)
	print(f"Ottenuto: Oggetto Mazzo creato.")
	print(f"Stato mazzo: {mazzo_fr.stato_mazzo()}")
	print(f"Lunghezza mazzo: {len(mazzo_fr)}")
	assert len(mazzo_fr.carte) == 52 and len(mazzo_fr) == 52
	assert len(mazzo_fr.pescate) == 0
	assert len(mazzo_fr.scarti) == 0
	assert len(mazzo_fr.scarti_permanenti) == 0
	print("Verifica: OK")
except Exception as e:
	print(f"Verifica: FALLITO - {e}")

# 2. Mazzo Italiano Singolo
print("\n--- Test: Creazione Mazzo Italiano (1 mazzo) ---")
print("Azione: Creo Mazzo(tipo_francese=False, num_mazzi=1)")
print("Atteso: Oggetto Mazzo con 40 carte in 'carte', 0 nelle altre liste.")
try:
	mazzo_it = Mazzo(tipo_francese=False, num_mazzi=1)
	print(f"Ottenuto: Oggetto Mazzo creato.")
	print(f"Stato mazzo: {mazzo_it.stato_mazzo()}")
	print(f"Lunghezza mazzo: {len(mazzo_it)}")
	assert len(mazzo_it.carte) == 40 and len(mazzo_it) == 40
	print("Verifica: OK")
except Exception as e:
	print(f"Verifica: FALLITO - {e}")

# 3. Mazzo Francese Multiplo (3 mazzi)
print("\n--- Test: Creazione Mazzo Francese (3 mazzi) ---")
print("Azione: Creo Mazzo(tipo_francese=True, num_mazzi=3)")
print("Atteso: Oggetto Mazzo con 156 carte (52 * 3) in 'carte'.")
try:
	mazzo_fr_multi = Mazzo(tipo_francese=True, num_mazzi=3)
	print(f"Ottenuto: Oggetto Mazzo creato.")
	print(f"Stato mazzo: {mazzo_fr_multi.stato_mazzo()}")
	print(f"Lunghezza mazzo: {len(mazzo_fr_multi)}")
	assert len(mazzo_fr_multi.carte) == 156 and len(mazzo_fr_multi) == 156
	print("Verifica: OK")
except Exception as e:
	print(f"Verifica: FALLITO - {e}")

# 4. Inizializzazione Errata (num_mazzi < 1)
print("\n--- Test: Creazione Mazzo con num_mazzi non valido ---")
print("Azione: Creo Mazzo(num_mazzi=0)")
print("Atteso: ValueError sollevato.")
try:
	Mazzo(num_mazzi=0)
	print("Ottenuto: Nessun errore sollevato.")
	print("Verifica: FALLITO")
except ValueError as e:
	print(f"Ottenuto: ValueError sollevato correttamente: '{e}'")
	print("Verifica: OK")
except Exception as e:
	print(f"Ottenuto: Errore inatteso: {e}")
	print("Verifica: FALLITO")

# --- Test Mescolamento ---
print_header("Test Mescolamento")
mazzo_test = Mazzo() # Francese, 1 mazzo
print(f"Stato iniziale: {mazzo_test.stato_mazzo()}")
prime_carte_prima = [c.desc_breve for c in mazzo_test.carte[:5]]
print(f"Prime 5 carte prima: {prime_carte_prima}")
print("Azione: mazzo_test.mescola_mazzo()")
print("Atteso: L'ordine delle carte nel mazzo cambia.")
mazzo_test.mescola_mazzo()
print("Ottenuto: Metodo eseguito.")
prime_carte_dopo = [c.desc_breve for c in mazzo_test.carte[:5]]
print(f"Prime 5 carte dopo: {prime_carte_dopo}")
print(f"Stato finale: {mazzo_test.stato_mazzo()}")
# Verifica (probabilistica): è altamente improbabile che rimangano uguali
assert prime_carte_prima != prime_carte_dopo
print("Verifica: OK (ordine cambiato)")

# --- Test Jolly ---
print_header("Test Jolly")
mazzo_fr = Mazzo(tipo_francese=True, num_mazzi=2) # 2 Mazzi Francesi = 104 carte
mazzo_it = Mazzo(tipo_francese=False, num_mazzi=1) # 1 Mazzo Italiano = 40 carte

# 1. Aggiungere Jolly a Mazzo Francese (2 mazzi => 4 jolly)
print("\n--- Test: Aggiungere Jolly a Mazzo Francese (2 mazzi) ---")
print(f"Stato iniziale: {mazzo_fr.stato_mazzo()}")
print("Azione: mazzo_fr.aggiungi_jolly()")
print("Atteso: Messaggio 'Aggiunti 4 jolly...', mazzo principale con 108 carte.")
risultato_add = mazzo_fr.aggiungi_jolly()
print(f"Ottenuto: '{risultato_add}'")
print(f"Stato mazzo: {mazzo_fr.stato_mazzo()}")
print(f"   {mazzo_fr.mostra_carte('mazzo')[-20:]}") # Mostra fine mazzo
assert len(mazzo_fr.carte) == 108 and "Aggiunti 4" in risultato_add
print("Verifica: OK")

# 2. Aggiungere Jolly di nuovo (non dovrebbe aggiungerne altri)
print("\n--- Test: Aggiungere Jolly di nuovo ---")
print("Azione: mazzo_fr.aggiungi_jolly()")
print("Atteso: Messaggio 'Nessun nuovo jolly aggiunto...'")
risultato_add2 = mazzo_fr.aggiungi_jolly()
print(f"Ottenuto: '{risultato_add2}'")
print(f"Stato mazzo: {mazzo_fr.stato_mazzo()}")
assert len(mazzo_fr.carte) == 108 and "Nessun nuovo jolly" in risultato_add2
print("Verifica: OK")

# 3. Rimuovere Jolly (temporaneamente)
print("\n--- Test: Rimuovere Jolly (temporaneamente) ---")
print("Azione: mazzo_fr.rimuovi_jolly(permanente=False)")
print("Atteso: Messaggio 'Rimossi 4 jolly...', mazzo con 104 carte, scarti con 4 jolly.")
risultato_rem_temp = mazzo_fr.rimuovi_jolly(permanente=False)
print(f"Ottenuto: '{risultato_rem_temp}'")
print(f"Stato mazzo: {mazzo_fr.stato_mazzo()}")
print(f"   {mazzo_fr.mostra_carte('scarti')}")
assert len(mazzo_fr.carte) == 104 and len(mazzo_fr.scarti) == 4 and "Rimossi 4" in risultato_rem_temp
assert all(c.nome == "Jolly" for c in mazzo_fr.scarti)
print("Verifica: OK")

# 4. Rimuovere Jolly (quando non ci sono nel mazzo/pescate/scarti)
print("\n--- Test: Rimuovere Jolly (quando non ci sono più) ---")
print("Azione: mazzo_fr.rimuovi_jolly(permanente=False)")
print("Atteso: Messaggio 'Nessun jolly trovato...'")
risultato_rem_none = mazzo_fr.rimuovi_jolly(permanente=False)
print(f"Ottenuto: '{risultato_rem_none}'")
print(f"Stato mazzo: {mazzo_fr.stato_mazzo()}")
assert "Nessun jolly trovato" in risultato_rem_none
print("Verifica: OK")

# 5. Aggiungere di nuovo e Rimuovere Jolly (permanentemente)
print("\n--- Test: Aggiungere e Rimuovere Jolly (permanentemente) ---")
mazzo_fr.aggiungi_jolly() # Riaggiunge i 4 jolly al mazzo (ora 108 carte)
print(f"Stato pre-rimozione: {mazzo_fr.stato_mazzo()}")
print("Azione: mazzo_fr.rimuovi_jolly(permanente=True)")
print("Atteso: Messaggio 'Rimossi 4 jolly...', mazzo con 104 carte, scarti_permanenti con 4 jolly.")
risultato_rem_perm = mazzo_fr.rimuovi_jolly(permanente=True)
print(f"Ottenuto: '{risultato_rem_perm}'")
print(f"Stato mazzo: {mazzo_fr.stato_mazzo()}")
print(f"   {mazzo_fr.mostra_carte('scarti_permanenti')}")
assert len(mazzo_fr.carte) == 104 and len(mazzo_fr.scarti_permanenti) == 4 and "Rimossi 4" in risultato_rem_perm
assert all(c.nome == "Jolly" for c in mazzo_fr.scarti_permanenti)
print("Verifica: OK")

# 6. Provare ad aggiungere Jolly a Mazzo Italiano
print("\n--- Test: Aggiungere Jolly a Mazzo Italiano ---")
print(f"Stato iniziale: {mazzo_it.stato_mazzo()}")
print("Azione: mazzo_it.aggiungi_jolly()")
print("Atteso: Messaggio che indica non supportato, stato invariato.")
risultato_it_add = mazzo_it.aggiungi_jolly()
print(f"Ottenuto: '{risultato_it_add}'")
print(f"Stato mazzo: {mazzo_it.stato_mazzo()}")
assert len(mazzo_it.carte) == 40 and "possono essere aggiunti solo ai mazzi di tipo francese" in risultato_it_add
print("Verifica: OK")

# --- Test Pesca, Scarto e Rimescolamento Automatico ---
print_header("Test Pesca, Scarto e Rimescolamento")
mazzo = Mazzo() # Mazzo francese singolo
mazzo.mescola_mazzo()
print(f"Stato iniziale: {mazzo.stato_mazzo()}")

# 1. Pesca normale
print("\n--- Test: Pesca 5 carte ---")
print("Azione: mazzo.pesca(5)")
print("Atteso: Lista con 5 carte, mazzo con 47 carte, pescate con 5 carte.")
carte_p1 = mazzo.pesca(5)
print(f"Ottenuto: Pescate {len(carte_p1)} carte: {[c.desc_breve for c in carte_p1]}")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
assert len(carte_p1) == 5 and len(mazzo.carte) == 47 and len(mazzo.pescate) == 5
print("Verifica: OK")

# 2. Scarta carte pescate
print("\n--- Test: Scarta 2 delle carte pescate ---")
carte_da_scartare = carte_p1[:2] # Scarta le prime 2 pescate
print(f"Azione: mazzo.scarta_carte([{', '.join(c.desc_breve for c in carte_da_scartare)}])")
print("Atteso: Messaggio 'Scartate 2 carte', pescate con 3 carte, scarti con 2 carte.")
risultato_scarto = mazzo.scarta_carte(carte_da_scartare)
print(f"Ottenuto: '{risultato_scarto}'")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
print(f"   {mazzo.mostra_carte('pescate')}")
print(f"   {mazzo.mostra_carte('scarti')}")
assert "Scartate 2" in risultato_scarto and len(mazzo.pescate) == 3 and len(mazzo.scarti) == 2
print("Verifica: OK")

# 3. Scarta carte non in 'pescate'
print("\n--- Test: Scarta carte non valide ---")
carta_non_pescata = mazzo.carte[0] # Prende una carta ancora nel mazzo
print(f"Azione: mazzo.scarta_carte([{carta_non_pescata.desc_breve}])")
print("Atteso: Messaggio 'Scartate 0 carte. 1 carte non trovate...', stato invariato.")
risultato_scarto_inv = mazzo.scarta_carte([carta_non_pescata])
print(f"Ottenuto: '{risultato_scarto_inv}'")
print(f"Stato mazzo: {mazzo.stato_mazzo()}") # Stato dovrebbe essere lo stesso di prima
assert "Scartate 0" in risultato_scarto_inv and "1 carte non trovate" in risultato_scarto_inv
assert len(mazzo.pescate) == 3 and len(mazzo.scarti) == 2
print("Verifica: OK")

# 4. Pesca fino a svuotare il mazzo principale
print("\n--- Test: Pesca le rimanenti 47 carte ---")
print("Azione: mazzo.pesca(47)")
print("Atteso: Lista con 47 carte, mazzo con 0 carte, pescate con 50 carte (3+47).")
carte_p2 = mazzo.pesca(47)
print(f"Ottenuto: Pescate {len(carte_p2)} carte.")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
assert len(carte_p2) == 47 and len(mazzo.carte) == 0 and len(mazzo.pescate) == 50
print("Verifica: OK")

# 5. Pesca con mazzo vuoto ma scarti presenti (trigger rimescolamento)
print("\n--- Test: Pesca con mazzo vuoto (trigger rimescolamento scarti) ---")
print(f"Stato prima: {mazzo.stato_mazzo()}") # Mazzo: 0, Pescate: 50, Scarti: 2
print("Azione: mazzo.pesca(1)")
print("Atteso: Rimescolamento automatico degli scarti (2 carte). Lista con 1 carta pescata. Mazzo con 1 carta, Pescate con 51, Scarti con 0.")
carte_p3 = mazzo.pesca(1)
print(f"Ottenuto: Pescate {len(carte_p3)} carte: {[c.desc_breve for c in carte_p3]}")
print(f"Stato mazzo post-pesca: {mazzo.stato_mazzo()}")
assert len(carte_p3) == 1 and len(mazzo.carte) == 1 and len(mazzo.pescate) == 51 and len(mazzo.scarti) == 0
print("Verifica: OK")

# 6. Pesca ulteriore dopo rimescolamento
print("\n--- Test: Pesca l'ultima carta ---")
print("Azione: mazzo.pesca(1)")
print("Atteso: Lista con 1 carta. Mazzo con 0 carte, Pescate con 52, Scarti con 0.")
carte_p4 = mazzo.pesca(1)
print(f"Ottenuto: Pescate {len(carte_p4)} carte: {[c.desc_breve for c in carte_p4]}")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
assert len(carte_p4) == 1 and len(mazzo.carte) == 0 and len(mazzo.pescate) == 52 and len(mazzo.scarti) == 0
print("Verifica: OK")

# 7. Pesca con mazzo e scarti vuoti
print("\n--- Test: Pesca con mazzo e scarti vuoti ---")
print("Azione: mazzo.pesca(1)")
print("Atteso: Lista vuota. Stato invariato.")
carte_p5 = mazzo.pesca(1)
print(f"Ottenuto: Pescate {len(carte_p5)} carte: {carte_p5}")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
assert len(carte_p5) == 0 and len(mazzo.carte) == 0 and len(mazzo.pescate) == 52 and len(mazzo.scarti) == 0
print("Verifica: OK")

# --- Test Rimescola Scarti Manuale ---
print_header("Test Rimescola Scarti Manuale")
mazzo = Mazzo()
mazzo.mescola_mazzo()
carte_p = mazzo.pesca(10)
mazzo.scarta_carte(carte_p[:5]) # Scarta 5 delle 10 pescate
print(f"Stato iniziale: {mazzo.stato_mazzo()}") # Mazzo: 42, Pescate: 5, Scarti: 5

# 1. Rimescola solo scarti
print("\n--- Test: Rimescola solo scarti ---")
print("Azione: mazzo.rimescola_scarti(include_pescate=False)")
print("Atteso: Messaggio '5 scarti reintegrati...', Mazzo con 47 carte, Pescate con 5, Scarti con 0.")
risultato_r1 = mazzo.rimescola_scarti(include_pescate=False)
print(f"Ottenuto: '{risultato_r1}'")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
assert "5 scarti reintegrati" in risultato_r1 and len(mazzo.carte) == 47 and len(mazzo.pescate) == 5 and len(mazzo.scarti) == 0
print("Verifica: OK")

# 2. Rimescola includendo pescate
# Prima mettiamo qualcosa negli scarti di nuovo
mazzo.scarta_carte(mazzo.pescate[:2]) # Scarta 2 carte -> Scarti: 2, Pescate: 3, Mazzo: 47
print(f"\nStato pre-rimescolamento (include pescate): {mazzo.stato_mazzo()}")
print("\n--- Test: Rimescola scarti includendo pescate ---")
print("Azione: mazzo.rimescola_scarti(include_pescate=True)")
print("Atteso: Messaggio '2 scarti reintegrati. 3 carte pescate reintegrate...', Mazzo con 52 carte (47+2+3), Pescate con 0, Scarti con 0.")
risultato_r2 = mazzo.rimescola_scarti(include_pescate=True)
print(f"Ottenuto: '{risultato_r2}'")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
assert "2 scarti reintegrati" in risultato_r2 and "3 carte pescate reintegrate" in risultato_r2
assert len(mazzo.carte) == 52 and len(mazzo.pescate) == 0 and len(mazzo.scarti) == 0
print("Verifica: OK")

# 3. Rimescola quando non c'è nulla da rimescolare
print("\n--- Test: Rimescola con scarti e pescate vuoti ---")
print("Azione: mazzo.rimescola_scarti(include_pescate=True)")
print("Atteso: Messaggio 'Nessuna carta da rimescolare...', stato invariato.")
risultato_r3 = mazzo.rimescola_scarti(include_pescate=True)
print(f"Ottenuto: '{risultato_r3}'")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
assert "Nessuna carta da rimescolare" in risultato_r3 and len(mazzo.carte) == 52
print("Verifica: OK")


# --- Test Rimozione Semi e Valori ---
print_header("Test Rimozione Semi e Valori")
mazzo = Mazzo(num_mazzi=1) # Mazzo francese standard, non mescolato per prevedibilità
# Semi ID: Cuori=1, Quadri=2, Fiori=3, Picche=4
# Valori: Asso=1, ..., 10=10, J=11, Q=12, K=13
print(f"Stato iniziale: {mazzo.stato_mazzo()}")

# 1. Rimuovi Semi (Cuori, ID=1) temporaneamente
print("\n--- Test: Rimuovi Seme Cuori (ID=1) temporaneamente ---")
print("Azione: mazzo.rimuovi_semi([1], permanente=False)")
print("Atteso: Ritorna 13. Mazzo con 39 carte, Scarti con 13 carte (tutte Cuori).")
num_rimossi_s1 = mazzo.rimuovi_semi([1], permanente=False)
print(f"Ottenuto: Rimosse {num_rimossi_s1} carte.")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
print(f"   {mazzo.mostra_carte('scarti')}")
assert num_rimossi_s1 == 13 and len(mazzo.carte) == 39 and len(mazzo.scarti) == 13
assert all(c.seme_id == 1 for c in mazzo.scarti)
print("Verifica: OK")

# 2. Rimuovi Valori (Assi=1, Re=13) permanentemente
print("\n--- Test: Rimuovi Valori Asso(1) e Re(13) permanentemente ---")
# Ci aspettiamo 3 Assi e 3 Re rimanenti (non Cuori)
print("Azione: mazzo.rimuovi_valori([1, 13], permanente=True)")
print("Atteso: Ritorna 6. Mazzo con 33 carte, Scarti Permanenti con 6 carte (Assi/Re non Cuori).")
num_rimossi_v1 = mazzo.rimuovi_valori([1, 13], permanente=True)
print(f"Ottenuto: Rimosse {num_rimossi_v1} carte.")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
print(f"   {mazzo.mostra_carte('permanenti')}")
assert num_rimossi_v1 == 6 and len(mazzo.carte) == 33 and len(mazzo.scarti_permanenti) == 6
assert all(c.valore in [1, 13] for c in mazzo.scarti_permanenti)
assert all(c.seme_id != 1 for c in mazzo.scarti_permanenti) # Verifica che non siano Cuori
print("Verifica: OK")

# 3. Rimuovi un valore non presente nel mazzo
print("\n--- Test: Rimuovi Valore non presente (es. Asso=1) ---")
print("Azione: mazzo.rimuovi_valori([1], permanente=True)") # Assi già rimossi
print("Atteso: Ritorna 0. Stato invariato rispetto a prima.")
num_rimossi_v2 = mazzo.rimuovi_valori([1], permanente=True)
print(f"Ottenuto: Rimosse {num_rimossi_v2} carte.")
print(f"Stato mazzo: {mazzo.stato_mazzo()}")
assert num_rimossi_v2 == 0 and len(mazzo.carte) == 33 and len(mazzo.scarti_permanenti) == 6
print("Verifica: OK")

# --- Test Metodi Ausiliari ---
print_header("Test Metodi Ausiliari")
mazzo = Mazzo()
print(f"Stato: {mazzo.stato_mazzo()}")
print(f"len(mazzo): {len(mazzo)}")
print(f"str(mazzo): {str(mazzo)}")

print("\n--- Test: mostra_carte (mazzo) ---")
print(f"Atteso: Stringa con le 52 carte del mazzo.")
mostra_m = mazzo.mostra_carte('mazzo')
print(f"Ottenuto: {mostra_m[:100]}...") # Mostra solo inizio per brevità
assert "Mazzo Principale (52):" in mostra_m and len(mostra_m.split(',')) == 52
print("Verifica: OK")

print("\n--- Test: mostra_carte (pescate - vuoto) ---")
print(f"Atteso: Messaggio 'Nessuna carta nella lista...'")
mostra_p = mazzo.mostra_carte('pescate')
print(f"Ottenuto: {mostra_p}")
assert "Nessuna carta nella lista 'Carte Pescate'" in mostra_p
print("Verifica: OK")

print("\n--- Test: mostra_carte (lista non valida) ---")
print(f"Atteso: Messaggio 'Lista non valida...'")
mostra_inv = mazzo.mostra_carte('invalid_list')
print(f"Ottenuto: {mostra_inv}")
assert "Lista non valida" in mostra_inv
print("Verifica: OK")

print("\n" + "="*30)
print("===== FINE TEST =====")
print("="*30)