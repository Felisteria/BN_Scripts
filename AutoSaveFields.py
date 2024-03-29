"""Window event handler example

Ask the user for confirmation before closing BioNumerics
"""
#//$AUTORUN;event=CreateMainWin;
import bns

## call the Register class method of a concrete window class in an autostart script

# factory for Window classes
_RegisteredWindowClasses = {}

class Window(object):
	"""Wrapper for Windows to handle events
	Because an eventhandler is set, the instances of the concrete windows are kept alive
	as long as the window exists.
	Arguments:
		- winID: int, the window ID
	"""
	# overwrite the class name in a derived class
	className = None

	@classmethod
	def Register(cls):
		"""Register a concrete Window class.
		Instances of the window class will be automatically generated when a window is opened.
		"""
		# set the event handler for the global 'wincreate' event - only first time!
		if not _RegisteredWindowClasses:
			_SetWinCreatedEvent()
		_RegisteredWindowClasses[cls.className.lower()] = cls
	
	def __init__(self, winid):
		self.__winid = winid
		self.__eventhandlers = {}
		bns.Util.Program.SetFunctorWindowEvent(winid, self.__eventhandler__)
	
	##  - window property
	def __GetWinID(self):
		return self.__winid
	WinID = property(__GetWinID, None, None, "Get the window ID")
	
	##  - event handling - internal functionality
	def __eventhandler__(self, args):
		# Event handling for BN window events
		eventname = args['EventName']

		if eventname == 'closewindow':
			self._HandleCloseWindow(args)
		

	def _HandleCloseWindow(self, args):
		# the window is closing, no way back...
		self.HandleCloseWindow()
	
## Attach the creation of windows to the 'wincreated' event
def _OnWinCreatedEvent(mp):
	"""Event triggered each time a new window is opened.
	If a concrete Window class is registered,
	an instance will be created (persistent while the window is open).
	"""
	winid = int(mp['argument'])
	bnswin = bns.Windows.BnsWindow(winid)
	bnsclass = bnswin.GetClassname().lower()
	if bnsclass in _RegisteredWindowClasses:
		_RegisteredWindowClasses[bnsclass](winid)

def _SetWinCreatedEvent():
	"""Associate the event 'wincreated' with the WinCreatedEvent function
	This function should be executed once in an autostart script
	"""
	bns.Util.Program.SetFunctorEvent(_OnWinCreatedEvent, 'wincreated')

class CompWindow(Window):
	className = 'Comparison'
	
	def HandleCloseWindow(self):
		bns.Util.Program.MessageBox("message","the job overview windows has closed",'information')
		bns.Database.Db.Fields.Save()

CompWindow.Register()
