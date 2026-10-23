"""GBwx, le utilita' per le finestre wxPython, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
V1.1.0 di venerdì 23 ottobre 2026.
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
La 1.1.0, con la V221 di GBUtils e la issue 57, porta finestra_mail, la
finestra delle voci Entra al PUB e Chiedi aiuto al PUB, comune a tutti i
programmi con le finestre.
Non fa parte di GBUtils.py perche' importa wx: PyInstaller lo porterebbe nei
pacchetti di tutti i programmi da console che usano la libreria. Lo importano
solo le applicazioni con le finestre.
Come GBUtils, non scrive frasi sue: misure e posizioni, e le parole della
finestra della posta le passa il chiamante, gia' tradotte.
Cosa c'e' dentro:
  STILE_ADATTABILE     lo stile dei dialoghi che si ridimensionano e si ingrandiscono.
  MISURA_MINIMA        sotto questa misura una finestra non si stringe.
  pannello_scorrevole  il pannello che raccoglie i controlli e scorre se non ci stanno.
  adatta_finestra      la misura dal contenuto, dentro lo schermo.
  dentro_area_utile    una misura data, dentro lo schermo, per chi non scorre.
  area_utile           l'area utile dello schermo su cui sta una finestra.
  finestra_mail        prepara una mail col programma di posta, o passo per
                       passo negli appunti per una webmail.
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


def finestra_mail(genitore, titolo, destinatario, oggetto, corpo, spiegazione, passi, pulsanti, senza_posta="", misura=(560, 420)):
	"""La finestra che prepara una mail, per esempio per le voci Entra al PUB
	e Chiedi aiuto al PUB, con le scelte di Gabriele del 23 ottobre 2026: si
	apre sempre, anche quando il programma di posta c'e', perche' il nuovo
	Outlook di Windows 11 e' spesso associato a mailto anche per chi non lo
	usa, e senza un account la bozza non compare; e quando il programma di
	posta manca accompagna l'utente un passo alla volta, copiando negli
	appunti un campo per volta da incollare nella webmail.
	Il fuoco sta sempre su un'area di testo in sola lettura, che si legge con
	le frecce.
	Con il programma di posta l'area mostra spiegazione, e i pulsanti sono
	apri, il predefinito, passi e chiudi. apri prepara la bozza con apri_mail
	di GBUtils; se Windows la apre, la finestra resta aperta, e Invio la
	chiude: chi non trova la bozza torna qui e sceglie passi. Se non la apre,
	la finestra passa da se' ai passi.
	Senza programma di posta, o con passi, la finestra va un passo alla
	volta, con i pulsanti ok, il predefinito, e annulla. Ogni passo copia il
	suo testo negli appunti, dove resta anche a programma chiuso, e l'area
	mostra l'istruzione seguita dal testo copiato, cosi' l'utente vede che
	cosa incollera'. ok passa al passo dopo, e all'ultimo chiude.
	Parametri, tutte parole del chiamante gia' tradotte:
	  genitore, titolo: della finestra.
	  destinatario, oggetto, corpo: la mail, per apri_mail.
	  spiegazione: il testo con il programma di posta; {programma} diventa il
	    suo nome, per esempio Thunderbird. Dica che verra' preparata una
	    bozza da spedire, e che se non compare si torna qui e si sceglie il
	    pulsante dei passi.
	  passi: la sequenza dei passi, coppie di istruzione e testo da copiare,
	    per esempio l'istruzione di incollare l'indirizzo nel campo A di una
	    mail nuova, poi di tornare e premere OK, con l'indirizzo. Un testo
	    None non copia niente, ed e' l'ultimo passo che dice di spedire. Per
	    l'iscrizione al PUB basta l'indirizzo, perche' Google ignora oggetto
	    e testo.
	  pulsanti: le etichette, in un dizionario con le chiavi apri, passi, ok,
	    chiudi e annulla, con la e commerciale degli acceleratori se si
	    vuole. chiudi e annulla sono lo stesso pulsante, che chiude la
	    finestra anche con Esc e cambia etichetta passando ai passi.
	  senza_posta: la frase che precede il primo passo quando ci si arriva
	    perche' la posta manca o non parte, non quando lo sceglie l'utente.
	  misura: la misura minima, in pixel al 100 per cento.
	Restituisce vero se la bozza si e' aperta o se l'utente ha percorso tutti
	i passi, falso se ha chiuso prima. Solleva ValueError se passi e' vuota.
	"""
	finestra = _FinestraMail(genitore, titolo, (destinatario, oggetto, corpo), spiegazione, passi, pulsanti, senza_posta, misura)
	try:
		finestra.ShowModal()
		return finestra.riuscita
	finally:
		finestra.Destroy()


def _negli_appunti(testo):
	"""Mette il testo negli appunti, dove resta anche dopo la chiusura del
	programma. Vero se ci e' riuscita. Sta in una funzione a se' perche' il
	banco possa sostituirla e lasciare stare gli appunti veri."""
	if not wx.TheClipboard.Open():
		return False
	try:
		riuscita = wx.TheClipboard.SetData(wx.TextDataObject(testo))
	finally:
		wx.TheClipboard.Close()
	if riuscita:
		wx.TheClipboard.Flush()
	return riuscita


class _FinestraMail(wx.Dialog):
	"""Il dialogo di finestra_mail, che ne spiega il comportamento."""

	def __init__(self, genitore, titolo, mail, spiegazione, passi, pulsanti, senza_posta, misura):
		from GBUtils import programma_di_posta
		if not passi:
			raise ValueError("finestra_mail: serve almeno un passo")
		super().__init__(genitore, title=titolo, style=STILE_ADATTABILE)
		self.mail = mail
		self.passi = list(passi)
		self.senza_posta = senza_posta
		self.riuscita = False
		self.passo = None
		self.annulla = pulsanti["annulla"]
		self.pannello = pannello_scorrevole(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.testo = self._area("")
		sizer.Add(self.testo, 1, wx.EXPAND | wx.ALL, 8)
		riga = wx.BoxSizer(wx.HORIZONTAL)
		self.apri = wx.Button(self.pannello, label=pulsanti["apri"])
		self.passo_per_passo = wx.Button(self.pannello, label=pulsanti["passi"])
		self.ok = wx.Button(self.pannello, label=pulsanti["ok"])
		self.chiudi = wx.Button(self.pannello, wx.ID_CANCEL, pulsanti["chiudi"])
		for pulsante in (self.apri, self.passo_per_passo, self.ok, self.chiudi):
			riga.Add(pulsante, 0, wx.ALL, 4)
		sizer.Add(riga, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
		self.pannello.SetSizer(sizer)
		self.apri.Bind(wx.EVT_BUTTON, self._apri)
		self.passo_per_passo.Bind(wx.EVT_BUTTON, lambda evento: self._inizia_passi(""))
		self.ok.Bind(wx.EVT_BUTTON, self._avanti)
		programma = programma_di_posta()
		if programma:
			self.ok.Hide()
			self.apri.SetDefault()
			self.testo.SetValue(spiegazione.replace("{programma}", programma))
		else:
			self._inizia_passi(senza_posta)
		adatta_finestra(self, self.pannello, misura)
		wx.CallAfter(self._al_testo)

	def _area(self, contenuto):
		return wx.TextCtrl(self.pannello, value=contenuto, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)

	def _al_testo(self):
		import contextlib
		with contextlib.suppress(RuntimeError):
			self.testo.SetInsertionPoint(0)
			self.testo.SetFocus()

	def _scrivi(self, contenuto):
		"""Mette il contenuto in un'area nuova, al posto della vecchia, e le da'
		il fuoco. Nuova e non la stessa riscritta: lo screen reader annuncia il
		controllo che riceve il fuoco, e un'area che lo ha gia' cambierebbe
		testo in silenzio, dopo un Invio premuto proprio li'. Il fuoco passa
		prima che la vecchia se ne vada, perche' non resti a nessuno."""
		vecchia = self.testo
		self.testo = self._area(contenuto)
		self.testo.MoveBeforeInTabOrder(vecchia)
		self.pannello.GetSizer().Replace(vecchia, self.testo)
		self.pannello.Layout()
		self._al_testo()
		vecchia.Destroy()

	def _apri(self, evento=None):
		from GBUtils import apri_mail
		if apri_mail(*self.mail):
			# La finestra resta: al ritorno Invio la chiude, e chi la bozza
			# non l'ha trovata sceglie i passi.
			self.riuscita = True
			self.chiudi.SetDefault()
			self._al_testo()
		else:
			self._inizia_passi(self.senza_posta)

	def _inizia_passi(self, premessa):
		self.apri.Hide()
		self.passo_per_passo.Hide()
		self.ok.Show()
		self.ok.SetDefault()
		self.chiudi.SetLabel(self.annulla)
		self.passo = 0
		self._mostra_passo(premessa)

	def _mostra_passo(self, premessa=""):
		istruzione, testo = self.passi[self.passo]
		if testo:
			_negli_appunti(testo)
		self._scrivi("\n".join(parte for parte in (premessa, istruzione, testo) if parte))

	def _avanti(self, evento=None):
		self.passo += 1
		if self.passo < len(self.passi):
			self._mostra_passo()
			return
		self.riuscita = True
		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.SetReturnCode(wx.ID_OK)
