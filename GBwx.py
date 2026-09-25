"""GBwx, le utilita' per le finestre wxPython, di Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
V1.0.0 di venerdì 25 settembre 2026.
Nato con la issue 49 di Tornello: le finestre a misura fissa in pixel, con i
caratteri di Windows al 150 per cento, lasciavano fuori dallo schermo campi e
pulsanti, e lo stesso rimedio serviva a quattro applicazioni, Dadillo,
Tornello, Cartella e Terminal Beast. Le funzioni vengono da ui_utils.py di
Dadillo 2.11.2, dove il rimedio e' nato, e si comportano allo stesso modo.
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
	"""
	return ScrolledPanel(finestra)


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
