"""GBsintesi, la voce degli screen reader e il display braille, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
V1.0.0 di mercoledì 21 ottobre 2026.
Nato da sintesi.py e braille.py di MeTeOra 1.113.5, dove leggevano i
sottotitoli, perche' anche MESS 1.79.0 vuole la cronaca della partita dal vivo
letta in automatico: due programmi, quindi una famiglia di GBUtils, decisione
di Gabriele. Si comporta come i due moduli di MeTeOra, lezioni comprese.
Non fa parte di GBUtils.py perche' porta accessible_output2 e pywin32, che
PyInstaller metterebbe nei pacchetti di tutti i programmi: lo importano solo
quelli che parlano attraverso lo screen reader. accessible_output2 e la voce
di Windows si aprono soltanto quando servono, quindi importare questo modulo
non costa niente, e senza la libreria le uscite semplicemente non rispondono.
Come GBUtils, non scrive frasi: le chiavi sono identificativi da salvare
nelle impostazioni, e i nomi da leggere all'utente li da' chi chiama.
Cosa c'e' dentro:
  AUTOMATICA        la scelta dell'uscita automatica: il primo screen reader attivo, poi la voce di Windows.
  USCITE            le uscite, nell'ordine della scelta automatica: nvda, jaws, sapi5.
  DESTINAZIONI      dove vanno i testi: entrambi, sintesi, braille.
  CON_IL_BRAILLE    le uscite che hanno il braille: nvda e jaws.
  disponibili       le uscite che si possono usare adesso.
  Sintesi           manda i testi all'uscita scelta, alla voce, al braille o a tutti e due.
  blocchi           un testo diviso in blocchi lunghi al piu' quante celle ha il display.
  Coda              i blocchi in fila per il display, ognuno col suo tempo minimo di lettura.
Lo schema d'uso, in un programma wx:
  voce = Sintesi()
  coda = Coda(lambda blocco: voce.dici(blocco, scelta, "braille"), lambda secondi, funzione: wx.CallLater(max(1, round(secondi * 1000)), funzione))
  voce.dici(testo, scelta, "sintesi")
  coda.aggiungi(testo, celle, minimo)
Si importa cosi', dalla cartella di GBUtils che sta nel percorso:
  from GBsintesi import AUTOMATICA, Coda, Sintesi
"""

import collections
import contextlib
import importlib
import time

AUTOMATICA = "automatica"
# Le uscite, nell'ordine della scelta automatica: chiave salvata nelle
# impostazioni, (modulo di accessible_output2, classe). ZDSR, Dolphin, System
# Access e PC-Talker non ci sono: le loro DLL sono proprietarie, senza un
# permesso di ridistribuirle, e Dolphin e System Access hanno solo DLL a 32
# bit, che un programma a 64 bit non puo' caricare (MeTeOra 1.85.0, decisione
# di Gabriele).
USCITE = {
    "nvda": ("nvda", "NVDA"),
    "jaws": ("jaws", "Jaws"),
    "sapi5": ("sapi5", "SAPI5"),
}
VOCE_DI_SISTEMA = "sapi5"
# Dove vanno i testi: alla voce e al braille, solo alla voce, solo al braille.
DESTINAZIONI = ("entrambi", "sintesi", "braille")
# Le uscite che hanno il braille, in accessible_output2: con le altre il
# braille non arriva.
CON_IL_BRAILLE = frozenset({"nvda", "jaws"})
# Il tempo di un testo, per dividerlo fra i blocchi del display, al piu' tanti
# secondi: un testo che dura molto non deve fermare il display (MeTeOra 1.83.0).
DURATA_MASSIMA = 15.0


class _VoceDiWindows:
    """La voce di Windows, SAPI5, aperta qui senza leggere l'elenco delle voci
    installate: accessible_output2 lo legge all'apertura, e su certi Windows,
    con una voce registrata male, l'elenco fallisce e l'uscita non si apriva,
    lasciando chi non ha uno screen reader senza la voce di ripiego (MeTeOra
    1.83.3, sul PC di Gabriele)."""

    def __init__(self):
        import win32com.client

        self._voce = win32com.client.Dispatch("SAPI.SpVoice")

    def speak(self, testo, interrupt=False):
        # SVSFlagsAsync, e con interrupt SVSFPurgeBeforeSpeak.
        self._voce.Speak(testo, 1 | (2 if interrupt else 0))

    def braille(self, _testo):
        return False

    def is_active(self):
        return True


def _crea(chiave):
    """L'uscita, o None se non si apre: accessible_output2 solleva errori suoi
    e di COM, e una libreria che manca non deve fermare il programma. La voce
    di Windows che accessible_output2 non apre la apre _VoceDiWindows."""
    modulo, classe = USCITE[chiave]
    try:
        return getattr(importlib.import_module(f"accessible_output2.outputs.{modulo}"), classe)()
    except Exception:  # noqa: BLE001 - qualunque errore vuol dire che quell'uscita non c'e'
        if chiave != VOCE_DI_SISTEMA:
            return None
    try:
        return _VoceDiWindows()
    except Exception:  # noqa: BLE001 - nemmeno SAPI risponde
        return None


def _attiva(chiave, uscita):
    """Vero se l'uscita si puo' usare adesso: uno screen reader in funzione, o
    la voce di Windows che si e' aperta."""
    if uscita is None:
        return False
    if chiave == VOCE_DI_SISTEMA:
        return True
    with contextlib.suppress(Exception):
        return bool(uscita.is_active())
    return False


def disponibili():
    """Le chiavi delle uscite che si possono usare adesso, nell'ordine di USCITE."""
    return [chiave for chiave in USCITE if _attiva(chiave, _crea(chiave))]


class Sintesi:
    """Manda i testi all'uscita scelta, aprendola alla prima richiesta e
    tenendola aperta. Da usare sempre dallo stesso filo: la voce di Windows
    passa da COM."""

    def __init__(self):
        self._aperte = {}

    def _uscita(self, chiave):
        if chiave not in self._aperte:
            self._aperte[chiave] = _crea(chiave)
        return self._aperte[chiave]

    def scelta(self, chiave):
        """La chiave dell'uscita che si userebbe adesso per la scelta data, o
        None se non ce n'e': per l'automatica, il primo screen reader attivo e
        poi la voce di Windows."""
        if chiave != AUTOMATICA:
            return chiave if chiave in USCITE and _attiva(chiave, self._uscita(chiave)) else None
        return next((c for c in USCITE if _attiva(c, self._uscita(c))), None)

    def dici(self, testo, chiave=AUTOMATICA, dove="entrambi", interrompi=False):
        """Dice il testo con l'uscita scelta, senza interrompere quello che sta
        dicendo, o con interrompi lasciandolo a meta': alla voce, al braille o
        a tutti e due, come dice dove, una delle DESTINAZIONI. La voce di
        Windows da sola non interrompe e accoda: interrompi la fa tacere prima
        (MeTeOra 1.105.0). Il braille ce l'hanno solo le uscite di
        CON_IL_BRAILLE. Falso se nessuna uscita risponde. Voce e braille si
        chiamano uno per uno: output di accessible_output2, con NVDA, dopo
        averli fatti tutti e due solleva un errore, perche' le funzioni di NVDA
        non restituiscono niente, e l'uscita si buttava e si riapriva a ogni
        testo (MeTeOra 1.82.0)."""
        effettiva = self.scelta(chiave)
        if effettiva is None:
            return False
        uscita = self._uscita(effettiva)
        try:
            if dove in ("entrambi", "sintesi"):
                uscita.speak(testo, interrupt=interrompi)
            if dove in ("entrambi", "braille"):
                uscita.braille(testo)
        except Exception:  # noqa: BLE001 - uno screen reader chiuso nel frattempo
            self._aperte.pop(effettiva, None)
            return False
        return True


def blocchi(testo, celle):
    """Il testo in blocchi lunghi al piu' celle caratteri, spezzati fra le
    parole; una parola piu' lunga del display si spezza dove finisce il
    display. Con celle 0 il testo resta intero. Ogni carattere occupa una
    cella: il braille informatico a otto punti."""
    testo = " ".join(testo.split())
    if not testo:
        return []
    if not celle or len(testo) <= celle:
        return [testo]
    risultato, corrente = [], ""
    for parola in testo.split(" "):
        while len(parola) > celle:
            if corrente:
                risultato.append(corrente)
                corrente = ""
            risultato.append(parola[:celle])
            parola = parola[celle:]
        if not parola:
            continue
        if not corrente:
            corrente = parola
        elif len(corrente) + 1 + len(parola) <= celle:
            corrente += " " + parola
        else:
            risultato.append(corrente)
            corrente = parola
    if corrente:
        risultato.append(corrente)
    return risultato


class Coda:
    """I blocchi in fila per il display: chi ha un display di poche celle legge
    male un testo lungo, e un messaggio braille sostituisce quello di prima,
    quindi i blocchi si mostrano uno dopo l'altro (MeTeOra 1.83.0, Gabriele, 4
    ottobre 2026). Ogni blocco resta per la sua parte del tempo che rimane al
    testo, in proporzione alla lunghezza, e mai meno del tempo minimo di
    lettura; un testo nuovo aspetta solo il tempo minimo del blocco mostrato,
    non la sua parte, e se il tempo minimo crea una coda i testi aspettano il
    loro turno. mostra(blocco) manda il blocco al braille; pianifica(secondi,
    funzione) chiama funzione piu' tardi, nello stesso filo, e restituisce un
    oggetto con Stop(), come wx.CallLater; orologio da' i secondi, come
    time.monotonic."""

    def __init__(self, mostra, pianifica, orologio=time.monotonic):
        self._mostra = mostra
        self._pianifica = pianifica
        self._orologio = orologio
        # (blocco, fine del testo o None, caratteri dal blocco alla fine del
        # testo, minimo in secondi, numero del testo)
        self._fila = collections.deque()
        self._testi = 0
        # Il numero del testo del blocco mostrato, per togli.
        self._mostrato = None
        # Fin quando il blocco mostrato deve restare: con la sua parte del
        # tempo del testo, e con il solo minimo; e l'attesa pianificata.
        self._libera = float("-inf")
        self._minimo_fino = float("-inf")
        self._attesa = None

    def aggiungi(self, testo, celle=0, minimo=2.0, durata=None):
        """Un testo nuovo, in coda: celle quante ne ha il display, 0 per il
        testo intero; minimo il tempo minimo di lettura di ogni blocco, in
        secondi; durata quanti secondi d'orologio resta il testo, se si sa,
        per dividerla fra i blocchi. Torna il numero del testo, per togli, o
        None se il testo e' vuoto."""
        pezzi = blocchi(testo, celle)
        if not pezzi:
            return None
        self._testi += 1
        fine = self._orologio() + min(durata, DURATA_MASSIMA) if durata else None
        for numero, pezzo in enumerate(pezzi):
            self._fila.append((pezzo, fine, sum(len(p) for p in pezzi[numero:]), minimo, self._testi))
        # Il blocco mostrato trattiene il testo nuovo solo per il suo minimo.
        if self._libera > self._minimo_fino:
            self._libera = self._minimo_fino
            if self._attesa is not None:
                self._attesa.Stop()
                self._attesa = None
        if self._attesa is None:
            self._prossimo()
        return self._testi

    def togli(self, numero):
        """Toglie il testo numero, quello che aggiungi ha restituito, perche' uno
        nuovo ne prende il posto: i suoi blocchi ancora in fila e, se il blocco
        mostrato e' suo, il tempo che deve restare, cosi' il testo dopo si
        mostra subito. Gli altri testi in fila restano. None non toglie niente."""
        if numero is None:
            return
        self._fila = collections.deque(voce for voce in self._fila if voce[4] != numero)
        if self._mostrato != numero:
            return
        self._libera = self._minimo_fino = float("-inf")
        if self._attesa is not None:
            self._attesa.Stop()
            self._attesa = None
        self._prossimo()

    def svuota(self):
        """Toglie dalla fila i testi non ancora mostrati, e il tempo minimo del
        blocco mostrato: il testo che arriva dopo si mostra subito."""
        self._fila.clear()
        self._libera = self._minimo_fino = float("-inf")
        if self._attesa is not None:
            self._attesa.Stop()
            self._attesa = None

    @property
    def in_fila(self):
        return len(self._fila)

    def _prossimo(self):
        self._attesa = None
        if not self._fila:
            return
        ora = self._orologio()
        if ora < self._libera:
            self._attesa = self._pianifica(self._libera - ora, self._prossimo)
            return
        pezzo, fine, rimasti, minimo, numero = self._fila.popleft()
        self._mostrato = numero
        self._mostra(pezzo)
        # La parte del tempo del testo vale finche' non aspetta un altro testo.
        altro = any(voce[4] != numero for voce in self._fila)
        quota = (fine - ora) * len(pezzo) / rimasti if fine is not None and fine > ora and not altro else 0.0
        self._minimo_fino = ora + minimo
        self._libera = ora + max(minimo, quota)
        if self._fila:
            self._attesa = self._pianifica(self._libera - ora, self._prossimo)
