# Piano di Sviluppo: Ottimizzazione del Rilevamento Lingua in `Donazione()`

Questo documento illustra il piano d'azione per l'adeguamento della funzione `Donazione()` all'interno della libreria `GBUtils` per garantirne la compatibilità futura con Python 3.13+ e migliorarne la precisione nel rilevamento della lingua.

---

## 1. Analisi dello Stato Attuale e Criticità

La versione attuale di `Donazione()` (V1.2) utilizza `locale.getdefaultlocale()` per identificare la lingua del sistema operativo. Questo approccio presenta tre limiti principali:

1. **Deprecazione e Futura Rimozione**: In Python 3.13, `locale.getdefaultlocale()` solleva un `DeprecationWarning` ed è programmata per essere rimossa definitivamente in Python 3.15.
2. **Mancanza di Allineamento con l'App**: La funzione ignora la lingua selezionata dall'utente all'interno dell'applicazione (Tornello), basandosi solo sull'OS.
3. **Imprecisione su Windows**: Rileva le preferenze di formattazione regionali (es. formato valuta o data) anziché la lingua reale dell'interfaccia utente (UI Display Language).

---

## 2. Obiettivi della Riforma

* **Compatibilità futura**: Eliminare qualsiasi warning di deprecazione e garantire il funzionamento in Python 3.15+.
* **Allineamento con l'applicazione**: Permettere a Tornello di passare esplicitamente la lingua attiva impostata dall'utente.
* **Precisione su Windows**: Utilizzare le API native di Windows (`ctypes`) per identificare l'effettiva lingua dell'interfaccia utente quando non viene passata una lingua esplicita.

---

## 3. Specifiche Tecniche delle Modifiche

### Modifica A: Nuova firma della funzione in `GBUtils.py`
La funzione accetterà un parametro opzionale `lang` (codice lingua a due lettere, es. `'it'`, `'en'`, `'es'`).
```python
def Donazione(lang=None):
```

### Modifica B: Algoritmo di Rilevamento della Lingua
La logica interna verrà strutturata in tre livelli di priorità:

1. **Priorità 1 (Parametro esplicito)**: Se `lang` è fornito, viene usato direttamente (convertito in minuscolo e troncato a 2 caratteri).
2. **Priorità 2 (Windows UI Language)**: Se su Windows e senza parametro, viene chiamata la funzione nativa `GetUserDefaultUILanguage` tramite `ctypes` per rilevare la lingua reale dello schermo dell'OS.
3. **Priorità 3 (Unix/Mac fallback)**: Su sistemi non Windows, viene utilizzato `locale.getlocale()`.
4. **Priorità 4 (Fallback finale)**: Se ogni rilevamento fallisce o solleva eccezioni, si imposta la lingua su inglese (`'en'`).

```python
# Anteprima del codice da implementare in GBUtils.py:
def Donazione(lang=None):
    import random
    import locale
    import sys

    if random.randint(1, 100) <= 20:
        messaggi = {
            'it': "Se questo software ti è piaciuto, ti è stato utile, ti sei divertito ad usarlo, considera l'idea di offrirmi un caffè. Mi trovi su paypal come gabriele.battaglia@gmail.com Grazie di cuore.",
            'en': "If you enjoyed this software, found it useful, or had fun using it, consider buying me a coffee. You can find me on PayPal at gabriele.battaglia@gmail.com Thank you.",
            'pt': "Se você gostou deste software, o achou útil ou se divertiu usando-o, considere me pagar um café. Você pode me encontrar no PayPal em gabriele.battaglia@gmail.com. Muito obrigado.",
            'fr': "Si vous avez aimé ce logiciel, l'avez trouvé utile ou vous êtes amusé en l'utilisant, envisagez de m'offrir un café. Vous pouvez me trouver sur PayPal à l'adresse gabriele.battaglia@gmail.com Merci beaucoup.",
            'es': "Si te ha gustado este software, te ha resultado útil o te has divertido usándolo, considera la idea de invitarme a un café. Me puedes encontrar en PayPal como gabriele.battaglia@gmail.com. Muchas gracias.",
            'de': "Wenn Ihnen diese Software gefallen hat, sie nützlich war oder Sie Spaß daran hatten, sie zu nutzen, ziehen Sie in Betracht, mir einen Kaffee auszugeben. Sie finden mich auf PayPal unter gabriele.battaglia@gmail.com Vielen Dank.",
            'ru': "Если вам понравилась эта программа, она оказалась полезной или вы получили удовольствие от ее использования, рассмотрите возможность угостить меня кофе. Вы можете найти меня на PayPal по адресу gabriele.battaglia@gmail.com Спасибо.",
            'zh': "如果您喜欢这款软件，觉得它有用，或者在使用过程中获得了乐趣，请考虑请我喝杯咖啡。您可以在PayPal上找到我：gabriele.battaglia@gmail.com 谢谢。",
            'ja': "このソフトウェアを楽しんだり、役立つと感じたり、楽しく使っていただけたなら、私にコーヒーをご馳走することを検討してください。PayPalでgabriele.battaglia@gmail.comとして見つけることができます。ありがとうございます。",
            'ar': "إذا أعجبك هذا البرنامج، أو وجدته مفيدًا، أو استمتعت باستycتخدامه، ففكر في شراء قهوة لي. يمكنك العثور عليّ على PayPal على gabriele.battaglia@gmail.com. شكرًا لك."
        }

        if lang:
            lingua_os = str(lang).lower().split('_')[0]
        else:
            lingua_os = 'en'
            try:
                if sys.platform == 'win32':
                    import ctypes
                    windll = ctypes.windll.kernel32
                    lang_id = windll.GetUserDefaultUILanguage()
                    locale_name = locale.windows_locale.get(lang_id, 'en')
                    lingua_os = locale_name.split('_')[0].lower()
                else:
                    locale_tuple = locale.getlocale()
                    if locale_tuple and locale_tuple[0]:
                        lingua_os = locale_tuple[0].split('_')[0].lower()
            except Exception:
                try:
                    # Fallback deprecato ma sicuro per vecchie versioni Python su altri OS
                    lingua_os_completa, _ = locale.getdefaultlocale()
                    if lingua_os_completa:
                        lingua_os = lingua_os_completa.split('_')[0].lower()
                except Exception:
                    lingua_os = 'en'

        messaggio_da_mostrare = messaggi.get(lingua_os, messaggi['en'])
        print(messaggio_da_mostrare)
```

---

## 4. Modifiche in Tornello per l'Integrazione

Per allineare Tornello al nuovo comportamento:

### In `src/gui/main_frame.py` (Metodo di visualizzazione donazione):
Passare la lingua attiva di Tornello alla chiamata:
```diff
-            Donazione()
+            current_lang = self.settings.get("language", "it")
+            Donazione(lang=current_lang)
```

### In `tornello.py` (Chiamata atexit per chiusura):
Adattare la registrazione all'uscita per passare la lingua se il modulo settings è caricato, oppure lasciare che utilizzi l'auto-rilevamento dell'OS corretto.
```python
def mostra_donazione_finale():
    from GBUtils import Donazione
    try:
        from gui.settings import load_settings
        settings = load_settings()
        lang = settings.get("language", "it")
    except Exception:
        lang = None
    Donazione(lang=lang)

# Registrazione atexit:
atexit.register(mostra_donazione_finale)
```

---

## 5. Fasi di Test Raccomandate

1. **Unit Test di Fallback**: Verificare che con `lang=None` la funzione continui a stampare un messaggio coerente con l'OS senza sollevare eccezioni.
2. **Test di Forza Lingua**: Verificare che chiamando `Donazione(lang='es')` venga stampato il messaggio in spagnolo, indipendentemente dalla lingua dell'OS.
3. **Verifica dei Log**: Assicurarsi che nel terminale non vengano più stampati `DeprecationWarning` all'avvio o alla chiusura del programma.
