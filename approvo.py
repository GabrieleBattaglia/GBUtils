"""Ascolto e approvazione delle proposte per Acu_Collection.

Fa sentire una alla volta le creazioni che stanno in nuovi_suoni.json e per
ognuna chiede se approvare, rifiutare o risentire. Finito il giro, aggiunge
alla collezione condivisa solo quelle approvate, scarta le altre e toglie
da nuovi_suoni.json tutto cio' che e' stato deciso.
Niente viene scritto prima della fine del giro: interrompendo con control c
la collezione resta com'era e le proposte restano tutte in attesa.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' Auto)
"""
import json
import os
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Acu_Maker import ONDE

from GBUtils import Acusticator

VERSION = "1.0.0"
RELEASE_DATE = "5 settembre 2026"
CARTELLA = os.path.dirname(os.path.abspath(__file__))
PROPOSTE = os.path.join(CARTELLA, "nuovi_suoni.json")
COLLEZIONE = os.path.join(CARTELLA, "Acu_Collection.json")


def leggi(percorso):
    """Il contenuto di un file json, None se non c'e' o non si legge."""
    if not os.path.isfile(percorso):
        return None
    try:
        with open(percorso, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        print(f"Non riesco a leggere {os.path.basename(percorso)}: {e}")
        return None


def scrivi(percorso, dati):
    """Salva un file json nello stesso stile di Acu_Maker."""
    with open(percorso, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4)


def durata_totale(score):
    """Quanto dura un preset, sommando le durate delle sue quartine."""
    totale = 0.0
    for quartina in score:
        try:
            totale += float(quartina[1])
        except (IndexError, TypeError, ValueError):
            continue
    return totale


def presenta(indice, quante, nome, dati):
    """Le righe di presentazione, corte per il display braille."""
    print(f"{indice} di {quante}: {nome}")
    print(dati.get("descrizione", ""))
    score = dati.get("score", [])
    onda = ONDE.get(dati.get("kind", 1), "sconosciuta")
    quartine = len(score)
    plurale = "quartina" if quartine == 1 else "quartine"
    print(f"Onda {onda}, {quartine} {plurale}, {durata_totale(score):.2f} s")


def chiedi():
    """Aspetta a, r o s. Restituisce la lettera scelta."""
    while True:
        risposta = input("(a)pprovo (r)ifiuto (s)ento di nuovo: ").strip().lower()
        if risposta in ("a", "r", "s"):
            return risposta
        print("Rispondi con a, r oppure s.")


def suona(nome):
    """Fa sentire il preset e aspetta che finisca."""
    if not Acusticator.play(nome, sync=True):
        print("Questo preset non e' partito, lo salto.")
        return False
    return True


def salva_copia():
    """Mette al sicuro la collezione prima di riscriverla."""
    marca = time.strftime("%Y%m%d_%H%M%S")
    copia = os.path.join(tempfile.gettempdir(), f"Acu_Collection_{marca}.json")
    shutil.copy2(COLLEZIONE, copia)
    return copia


def main():
    print(f"Approvo v{VERSION} del {RELEASE_DATE}")
    proposte = leggi(PROPOSTE)
    if not proposte:
        print("Non ci sono proposte da ascoltare.")
        return
    if leggi(COLLEZIONE) is None:
        print("La collezione non si legge, mi fermo.")
        return
    Acusticator.collezione(PROPOSTE)
    quante = len(proposte)
    print(f"{quante} creazioni da ascoltare.")
    print("Rispondi a per tenerla, r per buttarla,")
    print("s per risentirla quante volte vuoi.")
    print("Scrivo tutto solo alla fine del giro.")
    approvate, rifiutate = [], []
    try:
        for indice, (nome, dati) in enumerate(proposte.items(), start=1):
            presenta(indice, quante, nome, dati)
            suona(nome)
            while True:
                scelta = chiedi()
                if scelta == "s":
                    suona(nome)
                    continue
                if scelta == "a":
                    approvate.append(nome)
                    print("Approvata.")
                else:
                    rifiutate.append(nome)
                    print("Rifiutata.")
                break
    except KeyboardInterrupt:
        print("\nInterrotto. Non ho scritto niente,")
        print("le proposte restano tutte in attesa.")
        return
    print(f"Giro finito: {len(approvate)} approvate, {len(rifiutate)} rifiutate.")
    if rifiutate:
        print("Scartate: " + ", ".join(rifiutate))
    if approvate:
        copia = salva_copia()
        print(f"Copia di sicurezza in {copia}")
        collezione = leggi(COLLEZIONE)
        if collezione is None:
            print("La collezione non si rilegge, non scrivo niente.")
            return
        aggiunte, gia_presenti = [], []
        for nome in approvate:
            if nome in collezione:
                gia_presenti.append(nome)
                continue
            collezione[nome] = proposte[nome]
            aggiunte.append(nome)
        scrivi(COLLEZIONE, collezione)
        print(f"Aggiunte alla collezione: {len(aggiunte)}.")
        print(f"La collezione ora ha {len(collezione)} preset.")
        if gia_presenti:
            print("Nomi gia' occupati, non toccati: " + ", ".join(gia_presenti))
    decise = set(approvate) | set(rifiutate)
    restanti = {n: d for n, d in proposte.items() if n not in decise}
    if restanti:
        scrivi(PROPOSTE, restanti)
        print(f"Restano {len(restanti)} proposte in attesa.")
    else:
        os.remove(PROPOSTE)
        print("Nessuna proposta in attesa, ho tolto nuovi_suoni.json.")


if __name__ == "__main__":
    main()
