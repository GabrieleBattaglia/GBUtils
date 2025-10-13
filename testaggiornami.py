def update_checker(current_version: str, api_url: str) -> tuple[bool, str | None, str | None, str | None]:
    """
    Controlla l'ultima release di un repository GitHub e la confronta con la versione corrente.
    Args:
        current_version (str): La versione corrente dell'applicazione (es. "v1.0.0").
        api_url (str): L'URL dell'API di GitHub per le releases (es. "https://api.github.com/repos/user/repo/releases/latest").
    Returns:
        tuple[bool, str | None, str | None, str | None]: Una tupla contenente:
        - bool: True se è disponibile un aggiornamento, altrimenti False.
        - str | None: La stringa della versione più recente trovata, o None in caso di errore.
        - str | None: L'URL per il download del primo asset della release, o None se non disponibile.
        - str | None: Il changelog (testo dal campo 'body' della release), o None se non disponibile/aggiornato.
    """
    import requests
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()  # Solleva un'eccezione per codici di stato HTTP 4xx/5xx
        data = response.json()
        latest_version = data.get("tag_name")
        if not latest_version:
            return False, None, None, None
        changelog = data.get("body")
        update_available = latest_version > current_version
        if update_available:
            download_url = None
            assets = data.get("assets")
            if assets:
                download_url = assets[0].get("browser_download_url")
            return True, latest_version, download_url, changelog
        else:
            return False, latest_version, None, None
    except (requests.exceptions.RequestException, ValueError):
        # Errore di rete, URL non valido, o JSON malformato
        return False, None, None, None

# --- Esempio di utilizzo ---
if __name__ == '__main__':
    # Simula una versione corrente obsoleta
    MY_APP_VERSION = "v1.0.0"
    # Sostituisci con il tuo utente e repository
    # Uso un repository pubblico come esempio
    GITHUB_API_URL = "https://api.github.com/repos/git-for-windows/git/releases/latest"
    print(f"Versione corrente: {MY_APP_VERSION}")
    print(f"Controllo aggiornamenti su: {GITHUB_API_URL}")
    is_update_available, new_version, url, log = Aggiornami(MY_APP_VERSION, GITHUB_API_URL)
    if is_update_available:
        print(f"--- AGGIORNAMENTO DISPONIBILE ---")
        print(f"Nuova versione: {new_version}")
        if url:
            print(f"URL per il download: {url}")
        else:
            print("Nessun file per il download trovato.")
        if log:
            print("\n--- CHANGELOG ---")
            print(log)
        else:
            print("\nNessun changelog disponibile.")
    else:
        print("--- NESSUN AGGIORNAMENTO ---")
        print(f"L'applicazione è aggiornata. La versione remota è: {new_version or 'Non trovata'}")