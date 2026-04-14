import sys
from GBUtils import menu

print("=== Test 1: Chiavi in minuscolo ===")
d1 = {"sport": "Sport", "meditazione": "Meditazione", "memoria": "Memoria"}
print("Premi 'm', dovresti vedere (D, M)>me")
menu(d1)

print("\n=== Test 2: Chiavi con case misto (IL BUG) ===")
d2 = {"Sport": "Sport", "meditazione": "Meditazione", "Memoria": "Memoria"}
print("Premi 'm'. Senza il fix vedrai (E)>m. Con il fix dovresti vedere (D, M)>me")
menu(d2)

print("\n=== Test 3: Match esatto (BUG 2) ===")
d3 = {"Sport": "Solo Sport", "Sportivo": "Persona sportiva"}
print("Scrivi 'sport' e premi Invio. Senza il fix dà 'Scelta non valida'. Con il fix lo accetta.")
menu(d3)

print("\nTest completati.")
