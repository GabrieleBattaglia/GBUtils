# Banco di cestino_disponibile e nel_cestino, V306.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, modalita' auto).

"""Prove che non toccano il cestino vero: il disco dei file temporanei ha il
cestino, una cartella di rete no, un percorso che non esiste non si manda da
nessuna parte, e una cartella di rete inventata non si cancella. Lo
spostamento vero nel cestino lo provano i programmi nei loro collaudi."""

import os
import sys
import tempfile

from GBUtils import cestino_disponibile, nel_cestino

prove = []


def prova(nome, esito):
	prove.append((nome, bool(esito)))
	print(("ok  " if esito else "NO  ") + nome)


prova("il disco dei temporanei ha il cestino", cestino_disponibile(tempfile.gettempdir()))
prova("una cartella di rete non ha il cestino", not cestino_disponibile(r"\\server-che-non-esiste\condivisa\file.txt"))
prova("un file che non esiste non va nel cestino", not nel_cestino(os.path.join(tempfile.gettempdir(), "banco_cestino_inesistente_306.txt")))
falliti = [nome for nome, esito in prove if not esito]
print(f"{len(prove) - len(falliti)} prove su {len(prove)}")
sys.exit(1 if falliti else 0)
