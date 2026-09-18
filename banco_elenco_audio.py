"""Banco di prova degli elenchi audio, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, UltraCode).
Nato con la V152 e la issue 7, il 13 settembre 2026.
Niente di questo fa rumore: le prove di apertura avviano e fermano subito uno
stream senza scrivergli dentro un solo campione.
Le domande sono tre. La prima e' se quello che le due funzioni raccontano
corrisponda a quello che c'e' davvero sulla macchina, perche' un elenco che
mente fa scegliere all'utente una scheda che non voleva. La seconda e' se i
valori che restituiscono si possano davvero passare a CWzator, che e' il
motivo per cui esistono. La terza e' se la prova di apertura costi quello che
la docstring promette.
Attenzione: quello che si misura qui dipende dalla macchina. Il banco non
pretende numeri fissi, controlla che i conti tornino fra loro.
Si lancia con
  python banco_elenco_audio.py
e stampa in fondo quante prove sono passate.
"""
import sys
import time

import sounddevice as sd

import GBUtils
from GBUtils import (
	elenco_dispositivi_audio,
	elenco_interfacce_audio,
	scegli_dispositivo_audio,
)

totale = passate = 0

def prova(titolo, condizione, visto=""):
	global totale, passate
	totale += 1
	if condizione:
		passate += 1
		print(f"{titolo}: ok")
	else:
		print(f"{titolo}: FALLITA {visto}")

def solleva(eccezione, funzione, *argomenti, **chiavi):
	"""Vero se la chiamata solleva proprio quell'eccezione."""
	try:
		funzione(*argomenti, **chiavi)
	except eccezione:
		return True
	except Exception:  # noqa: BLE001
		return False
	return False

CHIAVI_DISPOSITIVO = {"indice", "dispositivo", "interfaccia", "breve", "canali", "frequenza",
					  "latenza", "predefinito", "stessa_scheda", "esclusiva", "apribile", "motivo"}
CHIAVI_INTERFACCIA = {"nome", "breve", "indice", "dispositivo", "nome_dispositivo", "quanti",
					  "latenza", "stessa_scheda", "esclusiva", "preferenza"}

# La prima chiamata sveglia PortAudio: le misure di tempo vengono dopo.
elenco_interfacce_audio()
interfacce = elenco_interfacce_audio()
dispositivi = elenco_dispositivi_audio(prova="nessuno")
print(f"Questa macchina: {len(interfacce)} interfacce, {len(dispositivi)} dispositivi di uscita.\n")

# 1. La forma di quello che tornano.
prova("l'elenco delle interfacce non e' vuoto", bool(interfacce), len(interfacce))
prova("l'elenco dei dispositivi non e' vuoto", bool(dispositivi), len(dispositivi))
prova("ogni interfaccia ha tutte le chiavi promesse",
	  all(set(v) == CHIAVI_INTERFACCIA for v in interfacce),
	  [set(v) ^ CHIAVI_INTERFACCIA for v in interfacce if set(v) != CHIAVI_INTERFACCIA][:1])
prova("ogni dispositivo ha tutte le chiavi promesse",
	  all(set(v) == CHIAVI_DISPOSITIVO for v in dispositivi),
	  [set(v) ^ CHIAVI_DISPOSITIVO for v in dispositivi if set(v) != CHIAVI_DISPOSITIVO][:1])

# 2. Quello che dicono corrisponde a quello che c'e'.
veri = {d["index"]: d for d in sd.query_devices() if d["max_output_channels"] > 0}
api_veri = [h["name"] for h in sd.query_hostapis()]
prova("ci sono tutti i dispositivi di uscita e nessun altro",
	  {v["indice"] for v in dispositivi} == set(veri),
	  {v["indice"] for v in dispositivi} ^ set(veri))
prova("nome, canali e interfaccia di ognuno sono quelli veri",
	  all(v["dispositivo"] == veri[v["indice"]]["name"]
		  and v["canali"] == veri[v["indice"]]["max_output_channels"]
		  and v["interfaccia"] == api_veri[veri[v["indice"]]["hostapi"]] for v in dispositivi))
prova("la latenza e' in millesimi, non in secondi",
	  all(abs(v["latenza"] - veri[v["indice"]]["default_low_output_latency"] * 1000.0) < 1e-6
		  for v in dispositivi))
prova("il nome breve e' quello lungo senza Windows",
	  all(v["breve"] == v["interfaccia"].replace("Windows ", "") for v in dispositivi + interfacce
		  if "interfaccia" in v) and all(v["breve"] == v["nome"].replace("Windows ", "") for v in interfacce))

# 3. Il predefinito, che e' il dato che conta.
segnati = [v for v in dispositivi if v["predefinito"]]
prova("il predefinito e' segnato una volta sola, o nessuna",
	  len(segnati) <= 1, [v["indice"] for v in segnati])
if segnati:
	prova("ed e' proprio quello che dice il sistema",
		  segnati[0]["indice"] == sd.default.device[1], segnati[0]["indice"])
	nome_predefinito = veri[sd.default.device[1]]["name"]
	prova("stessa_scheda e' vero esattamente per chi ne porta il nome",
		  all(v["stessa_scheda"] == (v["dispositivo"] == nome_predefinito) for v in dispositivi))
	prova("e il predefinito e' fra quelli con stessa_scheda", segnati[0]["stessa_scheda"])
	print(f"  il predefinito e' l'indice {segnati[0]['indice']} su {segnati[0]['breve']}, "
		  f"e lo stesso nome compare su {sum(1 for v in dispositivi if v['stessa_scheda'])} dispositivi")

# 4. L'ordine: davanti chi porta dove si sta gia' ascoltando.
prima_parte = [v["stessa_scheda"] for v in dispositivi]
prova("i dispositivi della stessa scheda stanno tutti davanti",
	  prima_parte == sorted(prima_parte, reverse=True), prima_parte)
if any(prima_parte):
	prova("e il primo di tutti e' il piu' pronto fra quelli",
		  dispositivi[0]["latenza"] == min(v["latenza"] for v in dispositivi if v["stessa_scheda"]),
		  f"{dispositivi[0]['breve']} a {dispositivi[0]['latenza']:.1f} ms")

# 5. Le prove di apertura, e quanto costano.
t = time.perf_counter()
senza = elenco_dispositivi_audio(prova="nessuno")
t_senza = (time.perf_counter() - t) * 1000
prova("senza prove non si apre niente", all(v["apribile"] is None for v in senza))
prova(f"e costa quasi niente, {t_senza:.2f} ms", t_senza < 20, f"{t_senza:.1f} ms")
t = time.perf_counter()
alcune = elenco_dispositivi_audio(prova="predefinito")
t_alcune = (time.perf_counter() - t) * 1000
provate = [v for v in alcune if v["apribile"] is not None]
prova("con prova predefinito si provano esattamente quelli della stessa scheda",
	  {v["indice"] for v in provate} == {v["indice"] for v in alcune if v["stessa_scheda"]},
	  len(provate))
t = time.perf_counter()
tutte = elenco_dispositivi_audio(prova="tutti")
t_tutte = (time.perf_counter() - t) * 1000
prova("con prova tutti si provano tutti", all(v["apribile"] is not None for v in tutte))
aperti = [v for v in tutte if v["apribile"]]
chiusi = [v for v in tutte if v["apribile"] is False]
prova("chi non si apre dice perche'", all(v["motivo"] for v in chiusi))
prova("chi si apre non ha motivo da dare", all(v["motivo"] is None for v in aperti))
print(f"  costo: senza prove {t_senza:.2f} ms, sul predefinito {t_alcune:.0f} ms, su tutti {t_tutte:.0f} ms")
print(f"  si aprono {len(aperti)} dispositivi su {len(tutte)}; non si aprono {len(chiusi)}")
for v in chiusi[:6]:
	print(f"    {v['indice']:3} {v['breve']:12} {v['dispositivo'][:30]:32} {v['motivo'].split(':')[-1].strip()[:44]}")

# 6. Un valore sbagliato si respinge invece di indovinare.
for sbagliato in ("sempre", "", None, 1, True):
	try:
		elenco_dispositivi_audio(prova=sbagliato)
		prova(f"prova={sbagliato!r} respinto", False, "non ha sollevato")
	except ValueError:
		prova(f"prova={sbagliato!r} respinto con ValueError", True)

# 7. Quello che l'elenco dice si puo' davvero passare a CWzator.
buoni = True
for v in interfacce:
	if v["dispositivo"] is None:
		continue
	try:
		indice, nome = scegli_dispositivo_audio(api=v["breve"])
	except ValueError:
		buoni = False
		continue
	if indice != v["dispositivo"] or nome != v["nome"]:
		buoni = False
prova("il nome breve di ogni interfaccia e' accettato da scegli_dispositivo_audio, e porta dove dice", buoni)
prova("e l'indice di ogni dispositivo e' accettato come tale, e porta con se' il nome della sua interfaccia",
	  all(scegli_dispositivo_audio(api=v["indice"]) == (v["indice"], v["interfaccia"]) for v in dispositivi[:5]))
prova("un indice che non esiste non solleva qui: lo dira' l'apertura",
	  scegli_dispositivo_audio(api=9999) == (9999, None))

# 8. Le due liste raccontano la stessa macchina.
da_dispositivi = {v["interfaccia"] for v in dispositivi}
da_interfacce = {v["nome"] for v in interfacce if v["quanti"] > 0}
prova("ogni interfaccia con dispositivi compare anche nella lista dei dispositivi",
	  da_interfacce <= da_dispositivi, da_interfacce - da_dispositivi)
prova("e i conteggi coincidono",
	  all(v["quanti"] == sum(1 for d in dispositivi if d["interfaccia"] == v["nome"]) for v in interfacce),
	  [(v["nome"], v["quanti"]) for v in interfacce])
prova("i nomi brevi delle interfacce non si ripetono",
	  len({v["breve"] for v in interfacce}) == len(interfacce))
prova("le esclusive sono ASIO e WDM-KS e nessun'altra",
	  {v["breve"] for v in interfacce if v["esclusiva"]} <= {"ASIO", "WDM-KS"},
	  {v["breve"] for v in interfacce if v["esclusiva"]})
in_scala = [v for v in interfacce if v["preferenza"] is not None]
prova("le interfacce in scala sono ordinate per preferenza crescente",
	  [v["preferenza"] for v in in_scala] == sorted(v["preferenza"] for v in in_scala),
	  [(v["breve"], v["preferenza"]) for v in in_scala])
print()
for v in interfacce:
	print(f"  {v['breve']:12} {str(v['nome_dispositivo'])[:32]:34} {v['quanti']:2} uscite  "
		  f"lat {v['latenza'] if v['latenza'] is None else round(v['latenza'], 1)}  "
		  f"stessa scheda {v['stessa_scheda']}, esclusiva {v['esclusiva']}")


# Il modo di apertura, che nasce con la issue 36. Il mixer di questo pacchetto
# alimenta la scheda scrivendo, quello di Chitabry lascia che sia il
# dispositivo a chiedere i campioni, e non tutte le interfacce reggono tutti e
# due i modi: la prova va fatta nello stesso modo in cui si suonera'.
prova("un modo di apertura inventato viene rifiutato",
	  solleva(ValueError, scegli_dispositivo_audio, modo="fantasia"))
prova("il modo predefinito e' la scrittura",
	  scegli_dispositivo_audio(riprova=True) == scegli_dispositivo_audio(modo="scrittura", riprova=True))

a_scrittura = scegli_dispositivo_audio(modo="scrittura", riprova=True)
a_callback = scegli_dispositivo_audio(modo="callback", riprova=True)
prova("le due scelte sono tutte e due utilizzabili",
	  all(scelta[0] is None or isinstance(scelta[0], int) for scelta in (a_scrittura, a_callback)),
	  (a_scrittura, a_callback))
prova("la cache tiene le due risposte separate",
	  set(GBUtils._scelta_audio) == {"scrittura", "callback"}, GBUtils._scelta_audio)
inizio = time.perf_counter()
scegli_dispositivo_audio(modo="callback")
prova("dalla cache la risposta costa meno di un millesimo",
	  (time.perf_counter() - inizio) * 1000 < 1.0)

tutti_scrittura = elenco_dispositivi_audio(prova="tutti", modo="scrittura")
tutti_callback = elenco_dispositivi_audio(prova="tutti", modo="callback")
prova("l'elenco prova ogni dispositivo in tutti e due i modi",
	  all(v["apribile"] is not None for v in tutti_scrittura + tutti_callback))
prova("i due elenchi parlano degli stessi dispositivi",
	  [v["indice"] for v in tutti_scrittura] == [v["indice"] for v in tutti_callback])

# Questa non dipende dalla macchina: PortAudio non ha ancora l'API bloccante
# per WDM-KS, quindi a scrittura non se ne apre nessuno, dovunque.
wdm_scrittura = [v for v in tutti_scrittura if v["breve"] == "WDM-KS"]
wdm_callback = [v for v in tutti_callback if v["breve"] == "WDM-KS"]
if wdm_scrittura:
	prova(f"nessuno dei {len(wdm_scrittura)} WDM-KS si apre a scrittura",
		  not [v for v in wdm_scrittura if v["apribile"]],
		  [v["dispositivo"] for v in wdm_scrittura if v["apribile"]])
	print(f"  WDM-KS: {sum(1 for v in wdm_callback if v['apribile'])} su {len(wdm_callback)} si aprono a callback")

print(f"\nProve {totale}, passate {passate}.")
sys.exit(0 if passate == totale else 1)
