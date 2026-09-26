"""GBwx, le utilita' per le finestre wxPython, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
V1.0.1 di sabato 26 settembre 2026.
Nato con la issue 49 di Tornello: le finestre a misura fissa in pixel, con i
caratteri di Windows al 150 per cento, lasciavano fuori dallo schermo campi e
pulsanti, e lo stesso rimedio serviva a quattro applicazioni, Dadillo,
Tornello, Cartella e Terminal Beast. Le funzioni vengono da ui_utils.py di
Dadillo 2.11.2, dove il rimedio e' nato, e si comportano allo stesso modo.
Dalla 1.0.1 una finestra costruita con pannello_scorrevole, quando si chiude,
restituisce il fuoco al controllo che lo aveva prima di lei, come un dialogo
senza pannello: fino alla 1.0.0 il fuoco restava sulla cornice della finestra
principale, dove NVDA legge soltanto il titolo. Come con un dialogo senza
pannello, il controllo che aveva il fuoco alla chiusura non riceve
EVT_KILL_FOCUS; se quello di prima non puo' riprenderlo, per esempio perche'
e' spento, il fuoco va al primo controllo della finestra che si riattiva.
Chi chiama non deve fare niente di nuovo.
Non fa parte di GBUtils.py perche' importa wx: PyInstaller lo porterebbe nei
pacchetti di tutti i programmi da console che usano la libreria. Lo importano
solo le applicazioni con le finestre.
Come GBUtils, non scrive frasi: misure e posizioni soltanto.
Cosa c'e' dentro:
  STILE_ADATTABILE     lo stile dei dialoghi che si ridimensionano e si ingrandiscono.
  MISURA_MINIMA        sotto questa misura una finestra non si stringe.
  pannello_scorrevole  il pannello che raccoglie i controlli e scorre se non ci stanno.
  adatta_finestra      la misura dal contenuto, dentro lo schermo.
  dentro_area_utile    una misura data, dentro lo schermo, per chi non scorre.
  area_utile           l'area utile dello schermo su cui sta una finestra.
Lo schema di un dialogo:
  super().__init__(genitore, title=titolo, style=STILE_ADATTABILE)
  pannello = pannello_scorrevole(self)
  ... i controlli, figli del pannello, e pannello.SetSizer(sizer) ...
  adatta_finestra(self, pannello, (larghezza, altezza))
adatta_finestra va chiamata dopo aver dato ai controlli i loro caratteri:
misurare prima vorrebbe dire misurare testi piu' piccoli di quelli veri.
Si importa cosi', dalla cartella di GBUtils che sta nel percorso:
  from GBwx import STILE_ADATTABILE, adatta_finestra, pannello_scorrevole
"""
import wx
from wx.lib.scrolledpanel import ScrolledPanel

# Lo stile dei dialoghi: si ridimensionano e si ingrandiscono a tutto
# schermo, come chiede chi usa i caratteri grandi.
STILE_ADATTABILE = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX

# Sotto questa misura la finestra non si stringe: oltre, ci pensano le barre.
MISURA_MINIMA = (240, 160)


def area_utile(finestra):
	"""L'area utile dello schermo su cui sta il genitore della finestra, o la
	finestra stessa se non ha genitore: lo schermo meno la barra delle
	applicazioni. Sta in una funzione a se' perche' banchi e prove possano
	sostituirla con un'area simulata, per esempio quella di uno schermo con la
	scala al 150 per cento, che su un programma non consapevole dei DPI da
	1920 per 1032 pixel diventa 1280 per 688.
	"""
	schermo = wx.Display.GetFromWindow(finestra.GetParent() or finestra)
	return wx.Display(max(schermo, 0)).GetClientArea()


def pannello_scorrevole(finestra):
	"""Il pannello che raccoglie i controlli di una finestra e che scorre
	quando il contenuto non ci sta. Quando un controllo riceve il focus, il
	pannello scorre da se' fino a mostrarlo, quindi chi si muove col tab lo
	vede sempre, anche dentro un riquadro o una pagina di un Notebook. Per lo
	screen reader non cambia niente: e' un pannello come quello di prima.
	Dalla 1.0.1, quando la finestra si chiude, il fuoco torna al controllo
	che lo aveva prima che si aprisse, come con un dialogo senza pannello,
	senza che i controlli della finestra ricevano EVT_KILL_FOCUS a finestra
	chiusa: il perche' e i casi limite li spiega
	_fuoco_restituito_alla_chiusura.
	"""
	_fuoco_restituito_alla_chiusura(finestra)
	return ScrolledPanel(finestra)


def _fuoco_restituito_alla_chiusura(finestra):
	"""Quando la finestra di primo livello che contiene il pannello viene
	distrutta con il fuoco dentro, toglie il fuoco prima che se ne vadano i
	controlli: cosi' la finestra che si riattiva, per esempio la principale,
	lo rimette sul controllo che lo aveva prima, come fa wx da se' con un
	dialogo senza pannello.
	Il difetto, misurato con wxPython 4.3.1 e wxWidgets 3.3.3: wx distrugge
	prima il controllo col fuoco, che passa al suo pannello, poi il pannello,
	che lo passa al dialogo. Quando Windows riattiva la finestra principale,
	il fuoco sta ancora sul dialogo a meta' distruzione, che wx a quel punto
	non conta piu' come finestra di primo livello e prende per un figlio
	della principale: la principale crede di avere gia' il fuoco, non rimette
	quello che aveva, e il fuoco resta sulla sua cornice, dove NVDA legge
	soltanto il titolo. Con i controlli figli diretti del dialogo il fuoco
	sparisce con l'ultimo di loro, e la principale lo rimette. Succede con
	qualunque pannello dentro un dialogo, non solo con quello scorrevole, e
	in qualunque modo il dialogo si chiuda: ESC, Annulla, OK, EndModal, e
	anche la distruzione di un dialogo non modale.
	Il controllo che perde cosi' il fuoco non riceve EVT_KILL_FOCUS, come
	con un dialogo senza pannello, dove wx non lo manda a un controllo gia'
	in distruzione: mandato qui, a finestra chiusa, farebbe lavorare i suoi
	gestori dopo Annulla, per esempio uno SpinCtrl che conferma il numero
	scritto e non ancora confermato, o un gestore che tocca il dialogo, gia'
	cancellato per Python, e solleva RuntimeError. Per questo, mentre il
	fuoco si toglie, un gestore messo in cima a quelli del controllo
	trattiene l'evento.
	Se il controllo che aveva il fuoco prima non lo puo' riprendere, per
	esempio perche' e' stato spento mentre la finestra era aperta, Windows
	rifiuta il fuoco che wx gli rimette, e la finestra che si riattiva
	resterebbe senza fuoco, con i tasti che non arrivano a nessun controllo:
	allora, finiti gli eventi della chiusura, il fuoco va al primo controllo
	di quella finestra che lo accetta, e in mancanza alla finestra stessa.
	Qui GBwx non fa come un dialogo senza pannello, che in questo caso lo
	lascia sulla cornice della finestra, dove NVDA legge soltanto il titolo.
	Se prima della distruzione il programma ha gia' spostato il fuoco fuori
	dalla finestra, qui non si tocca niente. Solo in Windows: il difetto e'
	di wxMSW, e il fuoco si toglie con SetFocus di user32, perche' wx non ha
	un modo per lasciarlo a nessuno.
	"""
	if wx.Platform != "__WXMSW__":
		return
	finestra = finestra.GetTopLevelParent() or finestra
	if getattr(finestra, "_gbwx_fuoco_alla_chiusura", False):
		return
	finestra._gbwx_fuoco_alla_chiusura = True
	maniglia = finestra.GetHandle()

	def alla_distruzione(evento):
		# L'evento sale anche dai controlli che se ne vanno dopo: conta solo
		# quello della finestra, che arriva prima di loro.
		evento.Skip()
		if evento.GetWindow().GetHandle() != maniglia:
			return
		user32 = _user32_del_fuoco()
		fuoco = user32.GetFocus()
		if not fuoco or not (fuoco == maniglia or user32.IsChild(maniglia, fuoco)):
			return
		# Il filtro trattiene l'EVT_KILL_FOCUS che wx manderebbe al
		# controllo, ancora vivo: wx guarda soltanto se e' in distruzione il
		# controllo stesso, non la sua finestra, e IsBeingDeleted, che guarda
		# anche la finestra, qui direbbe di si'. Alla finestra, gia' in
		# distruzione, wx non manda niente, e il filtro non serve.
		controllo = wx.Window.FindFocus()
		if controllo is not None and controllo.GetHandle() == maniglia:
			controllo = None
		filtro = wx.EvtHandler()
		filtro.Bind(wx.EVT_KILL_FOCUS, lambda _evento: None)
		if controllo is not None:
			controllo.PushEventHandler(filtro)
		try:
			user32.SetFocus(None)
		finally:
			if controllo is not None:
				controllo.RemoveEventHandler(filtro)
		# Una finestra distrutta quando il programma si chiude puo' arrivare
		# qui dopo che wx.App se n'e' andata: allora non c'e' niente da rimettere.
		if wx.GetApp() is not None:
			wx.CallAfter(_fuoco_a_chi_ne_e_rimasto_senza)

	finestra.Bind(wx.EVT_WINDOW_DESTROY, alla_distruzione)


def _user32_del_fuoco():
	"""user32 con le firme delle funzioni del fuoco. Una copia tutta sua,
	cosi' le firme non cambiano quelle che usa il resto del programma."""
	import ctypes
	from ctypes import wintypes

	user32 = ctypes.WinDLL("user32")
	user32.GetFocus.restype = wintypes.HWND
	user32.IsChild.argtypes = [wintypes.HWND, wintypes.HWND]
	user32.SetFocus.argtypes = [wintypes.HWND]
	return user32


def _fuoco_a_chi_ne_e_rimasto_senza():
	"""Finiti gli eventi della chiusura: se nessuna finestra ha il fuoco ma
	una finestra del programma e' attiva, lo da' al primo controllo di
	quella che lo prende davvero, o in mancanza alla finestra stessa. Ogni
	tentativo si verifica con GetFocus: un pannello, per esempio, gira il
	fuoco all'ultimo controllo che lo ha avuto, anche se e' spento, e
	Windows lo rifiuta. Se il programma non e' in primo piano, o la
	finestra attiva e' ridotta a icona, non tocca niente: al ritorno ci
	pensano Windows e wx."""
	user32 = _user32_del_fuoco()
	if user32.GetFocus():
		return
	attiva = wx.GetActiveWindow()
	if attiva is None or not attiva.IsShown():
		return
	if isinstance(attiva, wx.TopLevelWindow) and attiva.IsIconized():
		return
	for controllo in _controlli_per_il_fuoco(attiva):
		controllo.SetFocus()
		if user32.GetFocus():
			return
	user32.SetFocus(attiva.GetHandle())


def _controlli_per_il_fuoco(finestra):
	"""I discendenti della finestra che possono ricevere adesso il fuoco
	dalla tastiera, nell'ordine dei figli: accesi, visibili, e non finestre
	di primo livello a se', come un dialogo che ha la finestra per
	genitore. Di ogni figlio vengono prima i controlli che ha dentro, e poi
	lui, cosi' un pannello arriva solo dopo i suoi controlli."""
	for figlio in finestra.GetChildren():
		if figlio.IsTopLevel() or not figlio.IsShown() or not figlio.IsEnabled():
			continue
		yield from _controlli_per_il_fuoco(figlio)
		if figlio.CanAcceptFocusFromKeyboard():
			yield figlio


def adatta_finestra(finestra, pannello, misura=None):
	"""Da' alla finestra la misura del suo contenuto, dentro lo schermo.
	Con una misura fissa in pixel, scelta con i caratteri al 100 per cento,
	i controlli crescono con i caratteri di Windows al 150 e gli ultimi,
	spesso proprio il campo da compilare o i pulsanti, finiscono fuori, in
	una finestra che non si puo' ne' allargare ne' scorrere. Qui la misura la
	decide il contenuto; misura, espressa in pixel al 100 per cento, resta
	come minimo, cosi' con i caratteri normali la finestra ha l'aspetto di
	sempre. Se il contenuto supera lo schermo, la finestra si ferma al bordo
	e il pannello scorre.
	pannello e' quello di pannello_scorrevole, con il suo sizer gia' dato.
	Va chiamata di nuovo quando il contenuto cambia misura; se cambia solo un
	po', per esempio il testo di un'etichetta, basta pannello.FitInside().
	"""
	pannello.SetupScrolling(scrollToTop=False)
	larghezza, altezza = finestra.ClientToWindowSize(pannello.GetSizer().GetMinSize())
	if misura:
		voluta = finestra.FromDIP(wx.Size(misura))
		larghezza = max(larghezza, voluta.width)
		altezza = max(altezza, voluta.height)
	area = area_utile(finestra)
	if altezza > area.height:
		# La barra verticale ruba spazio in larghezza: se non glielo si
		# restituisce, compare anche quella orizzontale.
		larghezza += wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X, finestra)
	finestra.SetMinSize(finestra.FromDIP(wx.Size(MISURA_MINIMA)))
	_colloca(finestra, larghezza, altezza, area)


def dentro_area_utile(finestra, misura):
	"""Da' alla finestra la misura voluta, in pixel al 100 per cento, ma mai
	piu' grande dell'area utile dello schermo, e ve la centra dentro.
	E' per le finestre senza pannello scorrevole, i cui controlli scorrono
	gia' da se', come una finestra principale fatta di un'area di testo e di
	un albero: una misura fissa, per esempio 1024 per 768, con la scala dello
	schermo al 150 per cento e' piu' alta dello schermo, e il bordo in basso
	con i controlli che ci stanno finisce fuori. Il minimo lo decide chi
	chiama, perche' dipende da che cosa la finestra contiene.
	Su una finestra principale va chiamata prima di Maximize: la misura data
	qui e' quella che torna ripristinando la finestra.
	"""
	voluta = finestra.FromDIP(wx.Size(misura))
	_colloca(finestra, voluta.width, voluta.height, area_utile(finestra))


def _colloca(finestra, larghezza, altezza, area):
	"""Ferma la misura all'area utile, la da' alla finestra e la centra sul
	genitore; se cosi' una parte uscisse dall'area, la sposta dentro."""
	larghezza = min(larghezza, area.width)
	altezza = min(altezza, area.height)
	finestra.SetSize(larghezza, altezza)
	finestra.CentreOnParent()
	x, y = finestra.GetPosition()
	x = min(max(x, area.x), area.x + area.width - larghezza)
	y = min(max(y, area.y), area.y + area.height - altezza)
	finestra.Move(x, y)
