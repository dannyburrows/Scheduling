#!
# /*************************************\
# |* Building the UI with Curses       *|
# |* Written by Danny Burrows          *|
# |* burrows.danny@gmail.com           *|
# |* CS419 - Spring 2014               *|
# |* Group Project                     *|
# |* 04/17/2014                        *|
# |*	                               *|
# \*************************************/

from interface import *
from timemanip import *
from curseswrapper import *
import time
import MySQLdb

def _addDateTime(self):
	"""
	Adds the current time to the dates array.
	"""
	start, stop, length = self.gui.getStates()
	temp = {'start': start, 'stop': stop, 'length': length}
	#self.dates.append({'start': start, 'stop': stop, 'length': length})
	year,date,startMins = getCorrectedTime(start)
	year,date,endMins = getCorrectedTime(stop)
	if startMins >= endMins:
		self.gui.addNotification(self.warningY, self.warningX, "Check your start and end times", 5)
		return
	if temp not in self.dates:
		self.dates.append(temp)
		changeWin = self.gui.getWin('timeDates')
		changeWin.changeSelection(0)
	else:
		self.gui.addNotification(self.warningY, self.warningX, "Date and time already added", 5)

def getInput(self):
	"""
	Form control for the user name input. Turns the cursor back on and echos the typed text.
	Pulls the domain and adds the input text, concatenating the two and appending to the selected array.
	"""
	win = self.gui.getWin('inputUser')
	# takes away the highlighted background and refreshes the screen
	win.highlighted = False
	win.modified = True
	self.gui.redrawGUI(self.tab.tab)
	# get the location of the input box, and the length of the box
	y,x,length = win.inputParams()
	# turn on charatcer typing and make the cursor visible
	curses.echo()
	curses.curs_set(2)
	# places the cursor at the beginning of the box, restricting the size to 1 less than the box
	# it is important to ensure we have enough space to type the entire email
	text = self.gui.screen.getstr(y, x, length)
	# turn off character displays and turn the cursor off
	curses.noecho()
	curses.curs_set(0)
	# change the input back to its original state
	win.highlighted = True
	win.modified = True
	# corrects deleting the dates on accepting input
	temp = self.gui.getWin('startDateM')
	temp.modified = True
	temp = self.gui.getWin('startDateD')
	temp.modified = True
	temp = self.gui.getWin('startDateY')
	temp.modified = True
	# warnings
	if not text:
		self.gui.addNotification(self.warningY, self.warningX, 'Please input a valid user name')
		return
	user = text #+ domain
	if user in self.selected: # check to ensure user is not being doubly added
		self.gui.addNotification(self.warningY, self.warningX, 'User already added')
		return
	# updates the selected box and prepares for refresh		
	self.selected.append(user) # return text
	changeWin = self.gui.getWin('selectedUsers')
	changeWin.changeSelection(0)

	return True

def _processUpDown(self, direction):
	"""
	Event handler for when a user press the up or down arrow.

	Modifies the selection variable on the specific window a user is highlighted, if it can be modified.
	"""
	# find which window we're in and modify that value
	# move the index back 1
	activeWin = self.gui.getTab(self.tab.tab)
	if activeWin.scrollable == False:
		self.gui.addNotification(self.warningY, self.warningX, "Cannot modify value",5)
	else:
		try:
			activeWin.changeSelection(direction)
			self.gui.clearWarning(self.warningY, self.warningX)
		except:
			pass

def _jumpToWin(self, index):
	"""
	Jumps to a specific window, based on user input
	"""
	curWin = self.gui.getTab(self.tab.tab)
	self.tab.tab = self.gui.getMap(index)
	newWin = self.gui.getTab(self.tab.tab)
	newWin.modified = True
	curWin.modified = True

def _moveTab(self, direction):
	"""
	Increments or decrements the tabstop. Flags the current and the new window as modifed so they can be refreshed.
	"""
	if direction == +1:
		# move the tabstop and redraw windows, highlighting the next window
		#self.gui.clearWarning(self.warningY, self.warningX)
		curWin = self.gui.getTab(self.tab.tab)
		self.tab.nextTab()
		newWin = self.gui.getTab(self.tab.tab)
		newWin.modified = True
		curWin.modified = True
	elif direction == -1:
		# move the tabstop and redraw windows, highlighting the next window
		#self.gui.clearWarning(self.warningY, self.warningX)
		curWin = self.gui.getTab(self.tab.tab)
		self.tab.prevTab()
		newWin = self.gui.getTab(self.tab.tab)
		curWin.modified = True
		newWin.modified = True

def _removeItem(self, items, window, warningMsg):
	"""
	On enter press, removes item from the window
	"""
	itemWin = self.gui.getWin(window)
	value = itemWin.getSelectedValue()
	try:
		items.remove(value)
	except:
		self.gui.addNotification(self.warningY, self.warningX, warningMsg, 5)
	itemWin.changeSelection(0)

def processEnter(self):
	"""
	Caught Enter key, determine what to do with it
	"""
	event = self.gui.getKey(self.tab.tab)
	if event in self.enterMaps:
		exec(self.enterMaps[event])

def goHome(self):
	"""
	Jump back to original screen
	"""
	self.gui.cleanGUI()
	mainGui().mainLoop()

class whenToMeet:
	def __init__(self):
		self.gui = GUI()
		self.gui.screen.clear()
		# deletes gui images already mapped
		self.gui.windows = []
		self.gui.mapWindows = []
		# lists for items for this particular use case
		self.selected = []
		self.dates = []
		self.locations = [] # x,y coords of pads

		self.tab = tabstop()
		self.warningY = 28
		self.warningX = 62
		self.buildWindows()
		self.tab.tab = 0
		self.gui.drawGUI(self.tab)
		self.setSelections()
		self.gui.redrawGUI(self.tab.tab)
		self.enterMaps = {
			'submit': 'self.submitRequest()',
			'exit': 'self.gui.close()\nexit()',
			'back': 'self._goBack()',
			'addSlot': '_addDateTime(self)',
			'selectedUsers': '_removeItem(self, self.selected, "selectedUsers", "No users to remove")',
			'timeDates': '_removeItem(self, self.dates, "timeDates", "No values to remove")',
			'inputUser': 'getInput(self)',
			'startH': '_addDateTime(self)',
			'startM': '_addDateTime(self)',
			'endH': '_addDateTime(self)',
			'endM': '_addDateTime(self)',
			'startDateM': '_addDateTime(self)',
			'startDateD': '_addDateTime(self)',
			'startDateY': '_addDateTime(self)',
			'length': '_addDateTime(self)',
			'inputUser': 'getInput(self)'
		}

	def _setOrientation(self):
		"""
		Sets up the locations for windows based on sizes of the window.
		"""
		# selected and username:	50 wide	Y height
		# dates/times: 				6 wide	3 height
		# length: 					8 wide	3 height
		# buttons: 					51 wide	3 height
		# y = 36, x = 112
		maxY, maxX = self.gui.screen.getmaxyx()
		interval = maxY / 10
		# case stack all on top of each other
		self.locations.append({'win': 'inputUser', 'x': 1, 'y': 8})
		self.locations.append({'win': 'selectedUsers', 'x': 1, 'y': 13})
		# make the height of selectedUsers only 3 intervals tall
		self.locations.append({'win': 'timeDates', 'x': 1, 'y': ((interval * 3) + 15)})
		self.locations.append({'win': 'startDateM', 'x': 54, 'y': 8})
		self.locations.append({'win': 'startDateD', 'x': 59, 'y': 8})
		self.locations.append({'win': 'startDateY', 'x': 63, 'y': 8})
		self.locations.append({'win': 'length', 'x': 54, 'y': 12})
		self.locations.append({'win': 'startH', 'x': 54, 'y': 16})
		self.locations.append({'win': 'startM', 'x': 58, 'y': 16})
		self.locations.append({'win': 'endH', 'x': 54, 'y': 20})
		self.locations.append({'win': 'endM', 'x': 58, 'y': 20})
		self.locations.append({'win': 'addSlot', 'x': 1, 'y': 3})
		self.locations.append({'win': 'submit', 'x': 21, 'y': 3})
		self.locations.append({'win': 'back', 'x': 33, 'y': 3})
		self.locations.append({'win': 'exit', 'x': 44, 'y': 3})

	def setSelections(self):
		"""
		Sets default selects to values that make sense
		"""
		now = datetime.now()
		day = int(now.strftime("%d"))
		month = int(now.strftime("%m"))
		win = self.gui.getWin('startDateM')
		win.selection = (month - 1)
		win = self.gui.getWin('startDateD')
		win.selection = (day - 1)
		win = self.gui.getWin('startH')
		win.selection = 8
		win = self.gui.getWin('endH')
		win.selection = 18
		win = self.gui.getWin('length')
		win.selection = 3

	def buildWindows(self):
		"""
		Creates the windows to be displayed by the GUI
		"""
		self._setOrientation()

		maxY, maxX = self.gui.screen.getmaxyx()
		interval = maxY / 10
		self.warningY = (interval * 3) + 15
		self.gui.addLabel(y=1,x=1,input="When can I schedule the meeting(s)?")
		# Listing windows
		y,x = self.gui.getLocation(self.locations, 'inputUser')
		self.gui.addLabel(y=y-1,x=x, input=" Enter an ONID (u)sername ")
		self.gui.addUIElement('input', 'inputUser', self.tab, self.locations, width=35)

		y,x = self.gui.getLocation(self.locations, 'selectedUsers')
		self.gui.addLabel(y=y-1, x=x, input=" (C)urrently Addded Users ")
		self.gui.addUIElement('list', 'selectedUsers', self.tab, self.locations, int(interval * 3), 35, self.selected, True, True)

		y,x = self.gui.getLocation(self.locations, 'timeDates')
		self.gui.addLabel(y=y-1, x=x, input=' S(e)lected Dates and Times ', color=1)
		self.gui.addUIElement('timeWin', 'timeDates', self.tab, self.locations, int(interval * 3), 50, self.dates, True, True)


		# Variables
		y,x = self.gui.getLocation(self.locations, 'startDateM')
		self.gui.addLabel(y=y-1, x=x+1, input=" Sta(r)t date: ")
		self.gui.addUIElement('list', 'startDateM', self.tab, self.locations, 3, 6, months, False, False)
		self.gui.addUIElement('list', 'startDateD', self.tab, self.locations, 3, 6, days, False, False)
		self.gui.addUIElement('list', 'startDateY', self.tab, self.locations, 3, 6, years, False, False)
		self.gui.addLabel(index='startDateM', input='Mon', justify='center', color=4)
		self.gui.addLabel(index='startDateD', input='Day', justify='center', color=4)
		self.gui.addLabel(index='startDateY', input='Year', justify='right', color=4)

		y,x = self.gui.getLocation(self.locations, 'length')
		self.gui.addLabel(y=y-1, x=x+1, input='(L)ength:')
		self.gui.addUIElement('list', 'length', self.tab, self.locations, 3, 8, lengths, False, False)
		self.gui.addLabel(index='length', input='Min', justify='center', color=4)

		y,x = self.gui.getLocation(self.locations, 'startH')
		self.gui.addLabel(y=y-1, x=x+1, input='(S)tart Time:')
		self.gui.addUIElement('list', 'startH', self.tab, self.locations, 3, 6, hours, False, False)
		self.gui.addUIElement('list', 'startM', self.tab, self.locations, 3, 8, mins, False, False)
		self.gui.addLabel(index='startH', input='Hr', justify='center', color=4)
		self.gui.addLabel(index='startM', input='Min', justify='center', color=4)

		y,x = self.gui.getLocation(self.locations, 'endH')
		self.gui.addLabel(y=y-1, x=x+1, input='End (T)ime:')
		self.gui.addUIElement('list', 'endH', self.tab, self.locations, 3, 6, hours, box=False, highlighted=False)
		self.gui.addUIElement('list', 'endM', self.tab, self.locations, 3, 8, mins, False, False)
		self.gui.addLabel(index='endH', input='Hr', justify='center', color=4)
		self.gui.addLabel(index='endM', input='Min', justify='center', color=4)

		# Buttons
		self.gui.addUIElement('button', 'addSlot', self.tab, self.locations, text='(A)dd Time Slot')
		self.gui.addUIElement('button', 'submit', self.tab, self.locations, text='(Q)uery')
		self.gui.addUIElement('button', 'back', self.tab, self.locations, text='(B)ack')
		self.gui.addUIElement('button', 'exit', self.tab, self.locations, text='E(x)it')

	def mainLoop(self):
		"""
		The main event handling loop for the UI. Responsible for moving the tabstop, handling list selections and modifying the window upon updates.

		Maps specific keys to respective functions and calls function with required parameters.
		"""
		keyMaps = {ord('x'): '_jumpToWin(self, "exit")',
				ord('\t'): '_moveTab(self, +1)',
				ord('\n'): 'processEnter(self)',
				ord('a'): '_jumpToWin(self, "addSlot")',
				ord('b'): '_jumpToWin(self, "back")',
				ord('c'): '_jumpToWin(self, "selectedUsers")',
				ord('e'): '_jumpToWin(self, "timeDates")',
				ord('l'): '_jumpToWin(self, "length")',
				ord('q'): '_jumpToWin(self, "submit")',
				ord('r'): '_jumpToWin(self, "startDateM")',
				ord('s'): '_jumpToWin(self, "startH")',
				ord('t'): '_jumpToWin(self, "endH")',
				ord('u'): '_jumpToWin(self, "inputUser")',
				curses.KEY_DOWN: '_processUpDown(self, +1)',
				curses.KEY_UP: '_processUpDown(self, -1)',
				curses.KEY_LEFT: '_moveTab(self, -1)',
				curses.KEY_RIGHT: '_moveTab(self, +1)'
				}
		while True:
			event = self.gui.screen.getch()
			if (event in keyMaps):
				exec(keyMaps[event])

			self.gui.redrawGUI(self.tab.tab)

	def _goBack(self):
		"""
		Back to original screen
		"""
		self.gui.cleanGUI()
		mainGui().mainLoop()

	def submitRequest(self):
		"""
		Prepares to query the calendar API and determine the available times.
		"""
		# error catching
		if not self.selected:
			self.gui.addNotification(self.warningY, self.warningX, "No users selected", 5)
			return
		if not self.dates:
			self.gui.addNotification(self.warningY, self.warningX, "No date/times selected", 5)
			return

		self.gui.addNotification(self.warningY, self.warningX, "Processing request...", 5)
		curWin = self.gui.getTab(self.tab.tab)
		curWin.modified = True
		
		if self.calcTimesSlots():
			self.tab.tab = self.tab.maxTab
			pass
		else:
			curWin.modified = False

	def calcTimesSlots(self):
		"""
		Makes the call to interface and eventually the calendar API. Creates a window object that lists the times returned
		as available.
		"""
		# process the event
		service = connection()
		finalAvails = []
	
		index = self.gui.getMap('selectedUsers')
		for date in self.dates:
			# erase old people if there
			people = []
			users = []
			# create people array
			for user in self.gui.windows[index].items:
				temp = person(user + "@onid.oregonstate.edu", int(date['length']), service.service)
				if temp.errorFlag:
					self.gui.addNotification(self.warningY, self.warningX, temp.errorMsg)
					return False
				
				host = 'localhost'
				username = 'root'
				passwd = ''
				database = 'Scheduling'

				try:
					db = MySQLdb.connect(host=host,user=username,passwd=passwd,db=database)
				except:
					self.gui.addNotification(self.warningY, self.warningX, "Issue connecting to the MySQL server. Check the connection.")
					return False
				sql = db.cursor()
				query = 'SELECT scheduled_days, scheduled_start_time, scheduled_end_time, scheduled_start_date, scheduled_end_date FROM class AS cls INNER JOIN instructor AS ins ON ins.id = cls.instructor WHERE ins.username = "' + user + '"'
				sql.execute(query)
				for row in sql.fetchall():
					classDays = parseDays(row[0])
					classStart = fixTime(row[1])
					classEnd = fixTime(row[2])
					start = fixDate(row[3])
					end = fixDate(row[4])
					start = setDateTime(start, classStart)
					end = setDateTime(end, classEnd)
					temp.addClassTimeBlock(classDays, classStart, classEnd, start, end)
				people.append(temp)
				users.append(user)
			# meeting object
			newMeeting = meeting(date['start'], date['stop'], date['length'], people)
			# run the algorithms
			if newMeeting.availInTimeSlot():
			# append dates and resulting times
				finalAvails.append({'date': getDate(date['start']), 'times': newMeeting.availableTimes, 'length': date['length'] })
			else:
				self.gui.addNotification(self.warningY, self.warningX, "No users were found")
				return False

		sql.close()
		# clean the gui, prep to load new window
		self.gui.cleanGUI()
		# make the new window, passing in the results from the query
		whenToMeetResults(finalAvails,users).mainLoop()

class whenToMeetResults:
	"""
	Draws the window with the list of results from the queries
	"""
	def __init__(self, dates, users):
		self.dates = dates
		self.users = users
		self.gui = GUI()
		self.gui.screen.clear()
		self.tab = tabstop()
		self.locations = []

		self.warningY = 7
		self.warningX = 39

		self.buildWindows()
		self.tab.tab = 0

		self.gui.drawGUI(self.tab)
		self.gui.redrawGUI(self.tab.tab)
		self.enterMaps = {
			'home': 'goHome(self)',
			'exit': 'self.gui.close()\nexit()',
			'back': 'self._goBack()',
			'addSlot': '_addDateTime(self)',
		}

	def _setOrientation(self):
		"""
		Sets up the locations for windows based on sizes of the window.
		"""
		maxY, maxX = self.gui.screen.getmaxyx()
		interval = maxY / 10
		self.locations.append({'win': 'users', 'x': 2, 'y': 8})
		self.locations.append({'win': 'results', 'x': 3, 'y': ((interval * 3) + 12)})
		self.locations.append({'win': 'home', 'x': 2, 'y': 3})
		self.locations.append({'win': 'back', 'x': 13, 'y': 3})
		self.locations.append({'win': 'exit', 'x': 24, 'y': 3})

	def buildWindows(self):
		self._setOrientation()
		maxY, maxX = self.gui.screen.getmaxyx()
		interval = maxY / 10

		self.gui.addLabel(y=1, x=1, input="Multiple Users, Large Time Frame Results")
		y,x = self.gui.getLocation(self.locations, 'users')
		self.gui.addLabel(y=y-1, x=x+1, input='Available (U)sers')
		self.gui.addUIElement('list', 'users', self.tab, self.locations, (interval * 3), 35, self.users, True, True)

		y,x = self.gui.getLocation(self.locations, 'results')
		self.gui.addLabel(y=y-3, x=x+1, input='     Available (T)imes     ')
		self.gui.addLabel(y=y-2, x=x+1, input=' (P)rev page | (N)ext page ')
		self.gui.addUIElement('pagedWin', 'results', self.tab, self.locations, (interval * 3), 24, self.dates, box=True, highlighted=True)
		
		# set window selection for each individual array
		# also, tell the UI to display the label at the top
		tempWin = self.gui.getWin('results')
		tempWin.label = True
		for x in self.dates:
			tempWin.selection.append(0)

		self.gui.addUIElement('button', 'home', self.tab, self.locations, text='(H)ome')
		self.gui.addUIElement('button', 'back', self.tab, self.locations, text='(B)ack')
		self.gui.addUIElement('button', 'exit', self.tab, self.locations, text='E(x)it')

	def mainLoop(self):
		"""
		Catches key presses and determines what to do with them
		"""
		keyMaps = {
			ord('\t'): '_moveTab(self, +1)',
			ord('\n'): 'processEnter(self)',
			ord('b'): '_jumpToWin(self, "back")',
			ord('h'): '_jumpToWin(self, "home")',
			ord('x'): '_jumpToWin(self, "exit")',
			ord('n'): 'win=self.gui.getWin("results")\nwin.changeFocus(+1)',
			ord('p'): 'win=self.gui.getWin("results")\nwin.changeFocus(-1)',
			ord('t'): '_jumpToWin(self, "results")',
			ord('u'): '_jumpToWin(self, "users")',
			curses.KEY_DOWN: '_processUpDown(self, +1)',
			curses.KEY_UP: '_processUpDown(self, -1)',
			curses.KEY_RIGHT: '_moveTab(self, +1)',
			curses.KEY_LEFT: '_moveTab(self, -1)'
		}
		while True:
			event = self.gui.screen.getch()
			if (event in keyMaps):
				exec(keyMaps[event])

			self.gui.redrawGUI(self.tab.tab)
	
	def _goBack(self):
		"""
		Back to previous screen
		"""
		self.gui.cleanGUI()
		whenToMeet().mainLoop()

class whoToExpect:
	def __init__(self):
		self.gui = GUI()
		self.gui.screen.clear()
		self.tab = tabstop()
		self.selected = []
		self.locations = []
		# array of tuples, taking the type: { 'date': 'MM/DD/YYYY', 'times': ['MM:HH'] }
		self.dates = []
		# will hold the dates to check for multiple dates and times
		self.warningY = 28
		self.warningX = 62
		self.buildWindows()
		self.tab.tab = 0
		self.gui.drawGUI(self.tab)
		self.gui.redrawGUI(self.tab.tab)
		self.enterMaps = {'submit': 'self.submitRequest()',
			'exit': 'self.gui.close()\nexit()',
			'back': 'self._goBack()',
			'addSlot': '_addDateTime(self)',
			'selectedUsers': '_removeItem(self, self.selected, "selectedUsers", "No users to remove")',
			'timeDates': '_removeItem(self, self.dates, "timeDates", "No values to remove")',
			'inputUser': 'getInput(self)',
			'startH': '_addDateTime(self)',
			'startM': '_addDateTime(self)',
			'startDateM': '_addDateTime(self)',
			'startDateD': '_addDateTime(self)',
			'startDateY': '_addDateTime(self)',
			'length': '_addDateTime(self)',
			'inputUser': 'getInput(self)'
		}

	def _setOrientation(self):
		"""
		Sets up the locations for windows based on sizes of the window.
		"""
		# selected and username:	50 wide	Y height
		# dates/times: 				6 wide	3 height
		# length: 					8 wide	3 height
		# buttons: 					51 wide	3 height
		# y = 36, x = 112
		maxY, maxX = self.gui.screen.getmaxyx()
		interval = maxY / 10
		# case stack all on top of each other
		self.locations.append({'win': 'inputUser', 'x': 1, 'y': 8})
		self.locations.append({'win': 'selectedUsers', 'x': 1, 'y': 13})
		# make the height of selectedUsers only 3 intervals tall
		self.locations.append({'win': 'timeDates', 'x': 1, 'y': ((interval * 3) + 15)})
		self.locations.append({'win': 'startDateM', 'x': 54, 'y': 8})
		self.locations.append({'win': 'startDateD', 'x': 59, 'y': 8})
		self.locations.append({'win': 'startDateY', 'x': 63, 'y': 8})
		self.locations.append({'win': 'length', 'x': 54, 'y': 12})
		self.locations.append({'win': 'startH', 'x': 54, 'y': 16})
		self.locations.append({'win': 'startM', 'x': 58, 'y': 16})
		self.locations.append({'win': 'addSlot', 'x': 1, 'y': 3})
		self.locations.append({'win': 'submit', 'x': 21, 'y': 3})
		self.locations.append({'win': 'back', 'x': 33, 'y': 3})
		self.locations.append({'win': 'exit', 'x': 44, 'y': 3})

	def buildWindows(self):
		"""
		Build the UI and prepare for display
		"""
		self._setOrientation()
		maxY, maxX = self.gui.screen.getmaxyx()
 		#changeX = maxX / 10
		interval = maxY / 10

		# User input and remove data
		y,x = self.gui.getLocation(self.locations, 'inputUser')
		self.gui.addLabel(y=y-1, x=x+1, input=" Enter a (u)sername ")
		self.gui.addUIElement('input', 'inputUser', self.tab, self.locations, width=35)

		y,x = self.gui.getLocation(self.locations, 'selectedUsers')
		self.gui.addLabel(y=y-1, x=x+1, input=" (C)urrently Addded Users ")
		self.gui.addUIElement('list', 'selectedUsers', self.tab, self.locations, (interval * 3), 35, self.selected, True, True)

		# Meeting parameters input
		y,x = self.gui.getLocation(self.locations, 'startDateM')
		self.gui.addLabel(y=y-1, x=x+1, input=" Da(t)e: ")
		self.gui.addUIElement('list', 'startDateM', self.tab, self.locations, 3, 6, months, False, False)
		self.gui.addUIElement('list', 'startDateD', self.tab, self.locations, 3, 6, days, False, False)
		self.gui.addUIElement('list', 'startDateY', self.tab, self.locations, 3, 6, years, False, False)
		self.gui.addLabel(index='startDateM', input='Mon', justify='center', color=4)
		self.gui.addLabel(index='startDateD', input='Day', justify='center', color=4)
		self.gui.addLabel(index='startDateY', input='Year', justify='right', color=4)

		y,x = self.gui.getLocation(self.locations, 'length')
		self.gui.addLabel(y=y-1, x=x+1, input='(L)ength:')
		self.gui.addUIElement('list', 'length', self.tab, self.locations, 3, 8, lengths, False, False)
		self.gui.addLabel(index='length', input='Min', justify='center', color=4)

		y,x = self.gui.getLocation(self.locations, 'startH')
		self.gui.addLabel(y=y-1, x=x+1, input='(S)tart Time:')
		self.gui.addUIElement('list', 'startH', self.tab, self.locations, 3, 6, hours, False, False)
		self.gui.addUIElement('list', 'startM', self.tab, self.locations, 3, 8, mins, False, False)
		self.gui.addLabel(index='startH', input='Hr', justify='center', color=4)
		self.gui.addLabel(index='startM', input='Min', justify='center', color=4)

		y,x = self.gui.getLocation(self.locations, 'timeDates')
		self.gui.addLabel(y=y-1, x=x+1, input='S(e)lected Dates and Times', color=1)
		self.gui.addUIElement('timeWin', 'timeDates', self.tab, self.locations, (interval * 3), 50, self.dates, True, True)

		# Buttons
		self.gui.addUIElement('button', 'addSlot', self.tab, self.locations, text='(A)dd Time Slot')
		self.gui.addUIElement('button', 'submit', self.tab, self.locations, text='(Q)uery')
		self.gui.addUIElement('button', 'back', self.tab, self.locations, text='(B)ack')
		self.gui.addUIElement('button', 'exit', self.tab, self.locations, text='E(x)it')		

	def mainLoop(self):
		"""
		Catches key presses and determines what to do with them
		"""
		# determines action of each key listed
		keyMaps = {ord('x'): '_jumpToWin(self, "exit")',
				ord('\t'): '_moveTab(self, +1)',
				ord('\n'): 'processEnter(self)',
				ord('a'): '_jumpToWin(self, "addSlot")',
				ord('b'): '_jumpToWin(self, "back")',
				ord('c'): '_jumpToWin(self, "selectedUsers")',
				ord('d'): '_jumpToWin(self, "domain")',
				ord('e'): '_jumpToWin(self, "timeDates")',
				ord('l'): '_jumpToWin(self, "length")',
				ord('q'): '_jumpToWin(self, "submit")',
				ord('t'): '_jumpToWin(self, "startDateM")',
				ord('s'): '_jumpToWin(self, "startH")',
				ord('u'): '_jumpToWin(self, "inputUser")',
				curses.KEY_DOWN: '_processUpDown(self, +1)',
				curses.KEY_UP: '_processUpDown(self, -1)',
				curses.KEY_LEFT: '_moveTab(self, -1)',
				curses.KEY_RIGHT: '_moveTab(self, +1)'
				}
		while True:
			event = self.gui.screen.getch()
			if (event in keyMaps):
				exec(keyMaps[event])

			self.gui.redrawGUI(self.tab.tab)

	def submitRequest(self):
		"""
		Makes request to both Google Calendar and MySQL database to build the availability structures
		"""
		service = connection()
		dates = []
		index = self.gui.getMap('selectedUsers')
		for date in self.dates:
			# erase old people if there
			people = []
			# create people array
			for user in self.gui.windows[index].items:
				temp = person(user + "@onid.oregonstate.edu", int(date['length']), service.service)

				host = 'localhost'
				username = 'root'
				passwd = ''
				database = 'Scheduling'

				try:
					db = MySQLdb.connect(host=host,user=username,passwd=passwd,db=database)
				except:
					self.gui.addNotification(self.warningY, self.warningX, "Issue connecting to the MySQL server. Check the connection.")
					return False
				sql = db.cursor()
				query = 'SELECT scheduled_days, scheduled_start_time, scheduled_end_time, scheduled_start_date, scheduled_end_date FROM class AS cls INNER JOIN instructor AS ins ON ins.id = cls.instructor WHERE ins.username = "' + user + '"'
				sql.execute(query)
				for row in sql.fetchall():
					classDays = parseDays(row[0])
					classStart = fixTime(row[1])
					classEnd = fixTime(row[2])
					start = fixDate(row[3])
					end = fixDate(row[4])
					start = setDateTime(start, classStart)
					end = setDateTime(end, classEnd)
					temp.addClassTimeBlock(classDays, classStart, classEnd, start, end)

				if temp.errorFlag:
					self.gui.addNotification(self.warningY, self.warningX, temp.errorMsg)
					return False
				else:
					people.append(temp)
			# meeting object
			newMeeting = meeting(date['start'], date['stop'], date['length'], people)
			# run the algorithms
			if newMeeting.availInTimeSlot():
			#
			# users are held in newMeeting.availUsers
			# 
				dates.append({'date': date['start'], 'users': newMeeting.availUsers, 'length': date['length'] })
			else:
				self.gui.addNotification(self.warningY, self.warningX, "No users were found")
				return False
		#self.gui.cleanGUI()
		#  call new results gui
		whoToExpectResults(dates)
		return True
	
	def _goBack(self):
		"""
		Back to original screen
		"""
		self.gui.cleanGUI()
		mainGui().mainLoop()

class whoToExpectResults:
	"""
	Will display results for 2nd use case
	"""
	def __init__(self, dates):
		self.dates = dates
		self.gui = GUI()
		self.gui.screen.clear()
		self.tab = tabstop()
		self.warningY = 1
		self.warningX = 70
		self.locations = []
		self.buildWindows()
		self.tab.tab = 0

		self.gui.drawGUI(self.tab)
		self.gui.redrawGUI(self.tab.tab)
		self.enterMaps = {
			'exit': 'self.gui.close()\nexit()',
			'back': 'self._goBack()',
			'home': 'goHome(self)'
		}
		self.mainLoop()

	def _setOrientation(self):
		"""
		Sets up the locations for windows based on sizes of the window.
		"""
		maxY, maxX = self.gui.screen.getmaxyx()
		interval = maxY / 10
		self.locations.append({'win': 'results', 'x': 3, 'y': 10})
		self.locations.append({'win': 'home', 'x': 2, 'y': 3})
		self.locations.append({'win': 'back', 'x': 13, 'y': 3})
		self.locations.append({'win': 'exit', 'x': 24, 'y': 3})

	def buildWindows(self):
		self._setOrientation()
		maxY, maxX = self.gui.screen.getmaxyx()
		interval = maxY / 10
		# the results are going to formulated a bit differently
		# we need a list of users for each date and time
		# display the start time of the meeting, the date, the length of the meeting and a list of users that are going to attend

		# MM/DD/YYYY - 120 Mins 	
		# user1
		# user2
		# user3
		#
		# Left/right arrows to nav
		self.gui.addLabel(y=1, x=1, input="Who can I expect at the meeting(s)?")
		
		y,x = self.gui.getLocation(self.locations, 'results')
		self.gui.addLabel(y=y-3, x=x+10, input='    Available (U)sers    ')
		self.gui.addLabel(y=y-2, x=x+10, input='(P)rev page | (N)ext Page')
		self.gui.addUIElement('pagedWinUsers', 'results', self.tab, self.locations, (interval * 8), 50, self.dates, True, True)
		tempWin = self.gui.getWin('results')
		tempWin.label = True
		for x in self.dates:
			tempWin.selection.append(0)

		self.gui.addUIElement('button', 'home', self.tab, self.locations, text='(H)ome')
		self.gui.addUIElement('button', 'back', self.tab, self.locations, text='(B)ack')
		self.gui.addUIElement('button', 'exit', self.tab, self.locations, text='E(x)it')

	def mainLoop(self):
		keyMaps = {
			ord('\t'): '_moveTab(self, +1)',
			ord('\n'): 'processEnter(self)',
			ord('b'): '_jumpToWin(self, "back")',
			ord('h'): '_jumpToWin(self, "home")',
			ord('x'): '_jumpToWin(self, "exit")',
			ord('n'): 'win=self.gui.getWin("results")\nwin.changeFocus(+1)',
			ord('p'): 'win=self.gui.getWin("results")\nwin.changeFocus(-1)',
			ord('u'): '_jumpToWin(self, "results")',
			curses.KEY_DOWN: '_processUpDown(self, +1)',
			curses.KEY_UP: '_processUpDown(self, -1)',
			curses.KEY_RIGHT: '_moveTab(self, +1)',
			curses.KEY_LEFT: '_moveTab(self, -1)'
		}
		while True:
			event = self.gui.screen.getch()
			if (event in keyMaps):
				exec(keyMaps[event])

			self.gui.redrawGUI(self.tab.tab)

	def _goBack(self):
		"""
		Back to original screen
		"""
		self.gui.cleanGUI()
		whoToExpect().mainLoop()		

class mainGui:
	"""
	Main landing page for user to choose what to do
	"""
	def __init__(self):
		self.gui = GUI()
		self.tab = tabstop()
		self.locations = []
		self.gui.screen.clear()

		self.warningY = 54
		self.warningX = 6

		self.buildWindows()
		self.tab.tab = 0

		self.gui.drawGUI(self.tab)
		self.gui.redrawGUI(self.tab.tab)

	def _setLocations(self):
		self.locations.append({'win': 'spec', 'x': 8, 'y': 6})
		self.locations.append({'win': 'users', 'x': 8, 'y': 11})
		self.locations.append({'win': 'meeting', 'x': 8, 'y': 16})

	def buildWindows(self):
		# maxY, maxX = self.gui.screen.getmaxyx()
		# self.gui.close()
		# print maxY, maxX
		# exit()
		self._setLocations()
		self.gui.addUIElement('button', 'spec', self.tab, self.locations, text='Search Time Frame')
		self.gui.addUIElement('button', 'users', self.tab, self.locations, text='Search by Users')
		self.gui.addUIElement('button', 'meeting', self.tab, self.locations, text='Schedule Meeting')

	def mainLoop(self):	
		keyMaps = {ord('x'): 'self.gui.close()\nexit()',
				curses.KEY_DOWN: '_moveTab(self, +1)',
				curses.KEY_UP: '_moveTab(self, -1)',
				curses.KEY_LEFT: '_moveTab(self, -1)',
				curses.KEY_RIGHT: '_moveTab(self, +1)'
				}

		while True:
			event = self.gui.screen.getch()
			if event == ord('\n'):
				newWin = self.processEnter()
				if newWin == 2:
					whenToMeet().mainLoop()
				elif newWin == 3:
					prog = whoToExpect()
					prog.mainLoop()
			elif (event in keyMaps):
				exec(keyMaps[event])

			self.gui.redrawGUI(self.tab.tab)

	def _processUpDown(self, direction):
		# find which window we're in and modify that value
		# move the index back 1
		if direction == +1:
			curWin = self.gui.getTab(self.tab.tab)
			self.tab.nextTab()
			newWin = self.gui.getTab(self.tab.tab)
			newWin.modified = True
			curWin.modified = True
		else:
			curWin = self.gui.getTab(self.tab.tab)
			self.tab.prevTab()
			newWin = self.gui.getTab(self.tab.tab)
			newWin.modified = True
			curWin.modified = True

	def processEnter(self):
		# if self.tab.tab == self.gui.getMap('meeting'):
		# 	self.gui.cleanGUI()
		# 	return 1
		if self.tab.tab == self.gui.getMap('spec'):
			self.gui.cleanGUI()
			return 2
		elif self.tab.tab == self.gui.getMap('users'):
			self.gui.cleanGUI()
			return 3

	def __del__(self):
		pass

if __name__ == "__main__":
	# Global variables for selections in each window
	months = [str(x).zfill(2) for x in range(1, 13)]
	days = [str(x).zfill(2) for x in range(1, 32)]
	years = [str(x) for x in range(2014,2021)]
	hours = [str(x).zfill(2) for x in range(0,24)]
	mins = [str(x).zfill(2) for x in range(0,60,15)]
	lengths = [str(x) for x in range(15,375,15)]
	
	# selected = []
	# domains =['@gmail.com', '@onid.oregonstate.edu', '@eecs.oregonstate.edu']
	# users = ['burrows.danny@gmail.com', 'jonesjo@onid.oregonstate.edu', 'clampitl@onid.oregonstate.edu', 'jjames83@gmail.com']
	#users = [ x for x in range(0,50)]
	# test = GUI()
	# x = button(test.screen, 3, 3, "TESTING",0)
	# x.display(x, True, True)
	# y = listWindow(test.screen, 20, 20, 8, 3, days, 1)
	# y.display(y)
	# #test.windows.append(button(test.screen, 3, 3, "TESTING",0))
	# testDates = []
	# # testDates.append({'start': 1, 'stop': 2, 'length': 3})
	# # testDates.append({'start': 1, 'stop': 2, 'length': 3})
	# # testDates.append({'start': 1, 'stop': 2, 'length': 3})
	# testDates.append({ 'date': '04/26/2014', 'times':['12:00','12:30','1:00','1:30']})
	# testDates.append({ 'date': '04/27/2014', 'times':['1:00','2:30','4:00','5:30']})
	# z = pagedWindow(test.screen, 20, 20, 8, 40, testDates, 2)
	# z.display = displayPagedWindow
	# z.display(z)
	# #button(screen)

	# test.redrawGUI(0)
	# test.close()
	# exit()
	#GUIscreen = curses.initscr()
	
	mainGui().mainLoop()