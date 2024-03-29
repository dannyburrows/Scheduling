import curses
from timemanip import *

# This is a global to trim the amount of calls to gui.screen
# Sets one screen for the entire GUI
GUIScreen = curses.initscr()

def displayCheckbox(self, focus = False, highlight = False):
	if not self.modified:
		return
	self.pad.clear()
	if highlight:
		self.pad.bkgd(curses.color_pair(3))
	else:
		self.pad.bkgd(curses.color_pair(4))
	try:
		if self.checked:
			self.pad.addstr(1, 2, 'X ' + self.text)
		else:
			self.pad.addstr(1, 4, self.text)
	except:
		pass
	if self.box:
		self.pad.box()
	self.pad.refresh()
	self.modified = False

def displayDateTime(self, focus = False, highlight = False):
	"""
	Specific display function for the date times
	"""
	# stops from updating unnecessarily
	if not self.modified:
		return
	self.pad.clear()
	if highlight:
		self.pad.bkgd(curses.color_pair(3))
	else:
		self.pad.bkgd(curses.color_pair(4))
	height, width = self.pad.getmaxyx() # get the size of the pad
	height = height - 2 # remove padding
	page = 0 # for pagination
	if self.selection >= height:
		page = self.selection / height # determines which page the current selection should be on
	for x in range(0,height): # displays as many lines as can be clean fit inside the pad
		index = x + (page * height) # holds the index for items to be displayed, as we are not just listing the first X amount
		if (index) < len(self.items): # prevent out of range error
			if focus:# and self.scrollable: # the object is focused, so there will be a color change, and it scrollable so we can display the cursor
				if (index) == self.selection: # controls the highlighting of the current selection
					self.pad.addstr(x+1,2, _getStringDateTime(self, index), curses.color_pair(2)) # differentiate
				else:
					self.pad.addstr(x+1,2, _getStringDateTime(self, index))
			else:
				self.pad.addstr(x+1,2, _getStringDateTime(self, index))
	if self.box: # draws box is we are supposed to
		self.pad.box()
	self.pad.refresh() # redraw the pad
	self.modified = False

def displayList(self, focus = False, highlight = False):
	"""
	Displays the contents of the specific array assigned to this wein
	"""
	if not self.modified:
		return
	self.pad.clear() # completely wipes this pad
	if self.label:
		self.addLabel()
	if highlight:
		self.pad.bkgd(curses.color_pair(3))
	else:
		self.pad.bkgd(curses.color_pair(4))
	height, width = self.pad.getmaxyx() # get the size of the pad
	height = height - 2 # remove padding
	page = 0 # for pagination
	if self.selection >= height:
		page = self.selection / height # determines which page the current selection should be on
	for x in range(0,height): # displays as many lines as can be clean fit inside the pad
		index = x + (page * height) # holds the index for items to be displayed, as we are not just listing the first X amount
		if (index) < len(self.items): # prevent out of range error
			if focus:# and self.scrollable: # the object is focused, so there will be a color change, and it scrollable so we can display the cursor
				if (index) == self.selection: # controls the highlighting of the current selection
					self.pad.addstr(x+1,2, str(self.items[index]), curses.color_pair(2)) # differentiate
				else:
					self.pad.addstr(x+1,2, str(self.items[index]))
			else:
				self.pad.addstr(x+1,2, str(self.items[index]))
	if self.box: # draws box is we are supposed to
		self.pad.box()
	self.pad.refresh() # redraw the pad
	self.modified = False	

def displayPagedWindow(self, focus = False, highlight = False):
	"""
	The specific display function for a paged window.

	It's different as it indexes based off both focus and selection
	"""
	# stops from updating unnecessarily
	if not self.modified:
		return
	self.pad.clear()
	if self.label:
		self.pad.addstr(1,2, self.items[self.focus]['date'] + ' ' + str(self.items[self.focus]['length']) + ' mins', curses.color_pair(1))
	if highlight:
		self.pad.bkgd(curses.color_pair(3))
	else:
		self.pad.bkgd(curses.color_pair(4))
	height, width = self.pad.getmaxyx() # get the size of the pad
	height = height - 4 # remove padding
	page = 0 # for pagination
	if self.selection[self.focus] >= height:
		page = self.selection[self.focus] / height # determines which page the current selection should be on
	for x in range(0,height): # displays as many lines as can be clean fit inside the pad
		index = x + (page * height) # holds the index for items to be displayed, as we are not just listing the first X amount
		if (index) < len(self.items[self.focus]['times']): # prevent out of range error
			if focus:# and self.scrollable: # the object is focused, so there will be a color change, and it scrollable so we can display the cursor
				if (index) == self.selection[self.focus]: # controls the highlighting of the current selection
					self.pad.addstr(x+3,2, getPagedTimeString(self, index), curses.color_pair(2)) # differentiate
				else:
					self.pad.addstr(x+3,2, getPagedTimeString(self, index))
			else:
				self.pad.addstr(x+3,2, getPagedTimeString(self, index))
	if self.box: # draws box is we are supposed to
		self.pad.box()
	self.pad.refresh() # redraw the pad
	self.modified = False

def displayWindow(self, focus = False, highlight = False):
	"""
	"""
	# stops from updating unnecessarily
	if not self.modified:
		return
	self.pad.clear()
	# self.availabilities = {'date':None,'times':[]}
	if self.label:
		self.pad.addstr(1,2, self.items[self.focus]['date'], curses.color_pair(1))
	if highlight:
		self.pad.bkgd(curses.color_pair(3))
	else:
		self.pad.bkgd(curses.color_pair(4))
	height, width = self.pad.getmaxyx() # get the size of the pad
	height = height - 4 # remove padding
	page = 0 # for pagination
	if self.selection[self.focus] >= height:
		page = self.selection[self.focus] / height # determines which page the current selection should be on
	for x in range(0,height): # displays as many lines as can be clean fit inside the pad
		index = x + (page * height) # holds the index for items to be displayed, as we are not just listing the first X amount
		if (index) < len(self.items[self.focus]['times']): # prevent out of range error
			if focus:# and self.scrollable: # the object is focused, so there will be a color change, and it scrollable so we can display the cursor
				if (index) == self.selection[self.focus]: # controls the highlighting of the current selection
					self.pad.addstr(x+3,2, getPagedString(self, index), curses.color_pair(2)) # differentiate
				else:
					self.pad.addstr(x+3,2, getPagedString(self, index))
			else:
				self.pad.addstr(x+3,2, getPagedString(self, index))
	if self.box: # draws box is we are supposed to
		self.pad.box()
	self.pad.refresh() # redraw the pad
	self.modified = False

def displayStatic(self, focus = False, highlight = False):
	"""
	Basic display for a static object (inputBox and button)
	"""
	if not self.modified:
		return
	self.pad.clear()
	if highlight:
		self.pad.bkgd(curses.color_pair(3))
	else:
		self.pad.bkgd(curses.color_pair(4))
	try:
		self.pad.addstr(1,2,self.text)
	except:
		pass
	if self.box:
		self.pad.box()
	self.pad.refresh()
	self.modified = False

def displayUserString(self, focus = False, highlight = False):
	"""
	The specific display function for a paged window.

	It's different as it indexes based off both focus and selection
	"""
	# stops from updating unnecessarily
	# dates.append({'date': getDate(date['start']), 'users': newMeeting.availUsers, 'length': date['length'] })
	if not self.modified:
		return
	self.pad.clear()
	if self.label:
		self.pad.addstr(1,2, self.items[self.focus]['date'] + ' ' + str(self.items[self.focus]['length']) + ' mins', curses.color_pair(1))
	if highlight:
		self.pad.bkgd(curses.color_pair(3))
	else:
		self.pad.bkgd(curses.color_pair(4))
	height, width = self.pad.getmaxyx() # get the size of the pad
	height = height - 4 # remove padding
	page = 0 # for pagination
	if self.selection[self.focus] >= height:
		page = self.selection[self.focus] / height # determines which page the current selection should be on
	for x in range(0,height): # displays as many lines as can be clean fit inside the pad
		index = x + (page * height) # holds the index for items to be displayed, as we are not just listing the first X amount
		if (index) < len(self.items[self.focus]['users']): # prevent out of range error
			if focus:# and self.scrollable: # the object is focused, so there will be a color change, and it scrollable so we can display the cursor
				if (index) == self.selection[self.focus]: # controls the highlighting of the current selection
					self.pad.addstr(x+3,2, self.items[self.focus]['users'][index], curses.color_pair(2)) # differentiate
				else:
					self.pad.addstr(x+3,2, self.items[self.focus]['users'][index])
			else:
				self.pad.addstr(x+3,2, self.items[self.focus]['users'][index])
	if self.box: # draws box is we are supposed to
		self.pad.box()
	self.pad.refresh() # redraw the pad
	self.modified = False
	#dates.append({'date': getDate(date['start']), 'users': newMeeting.availUsers, 'length': date['length'] })

def _getStringDateTime(self, index):
	"""
	Returns a readable string with times that are going to be checked
	"""
	return ((str(self.items[index]['start']) + ' - ' + str(self.items[index]['stop']) + ' : ' + str(self.items[index]['length']) + ' mins'))

def getPagedString(self, index):
	return printTime(self.items[self.focus]['times'][index]) + ' - ' + printTime(self.items[self.focus]['times'][index] + 15)

def getPagedTimeString(self, index):
	"""
	Helper function for the pagedWindow object

	Returns a string with formatted start and stop times
	"""
	return printTime(self.items[self.focus]['times'][index]) + ' - ' + printTime(self.items[self.focus]['times'][index] + self.items[self.focus]['length'])

def getPagedUsersString(self, index):
	"""
	Helper function for the pagedWindow object

	Returns a string with formatted start and stop times
	"""
	return printTime(self.items[self.focus]['users'][index])

class GUI:
	"""
	The GUI class is the major component of the curses interface. This class sets up the screen that pads are added to.
	Handles the initializaiton and closing of the interface and basic functionality.
	"""

	def __init__(self):
		global GUIScreen # removes a lot of calls to self.gui.screen.X
		self.windows = [] 	# holds a list of all the windows that will be generated
		self.mapWindows = []	# keeps a mapping of the name of the window and it's tabstop
		self.screen = GUIScreen#curses.initscr()	# the main screen that everything will be displayed to
		curses.noecho() # no key presses to the screen
		curses.curs_set(0) # removes cursor from screen
		self.screen.keypad(1) # captures keypresses
		curses.start_color()
		
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
		curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
		curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)

		self.screen.bkgd(curses.color_pair(4))

	def addLabel(self, input, y = None, x = None, index = None, justify='left', color=1):
		"""
		Displays a label at specific location.

		Parameters:
		y - row coordinate on larger window object to display
		x - column coordiante
		input - text to display
		justify - if the text needs to right justified
		
		"""
		# lets modify this:
		# take in another parameter: pad
		# find the pad, add the label, centering at y
		# need to get size of pad, find center and length of text
		# if pad is 20 wide, text is 10, 20 - 10 / 2 = 5 ==> startX += 5
		# will right justify
		if index:
			curWin = self.getWin(index)
			maxY, maxX = curWin.getmaxyx()
			# print maxY, maxX
			if (justify == 'center'):
				position = (maxX - len(input)) / 2
			elif justify == 'left':
				position = 0
			elif justify == 'right':
				position = (maxX - len(input))
			#offset = 0
			# if justify == "right":
			# 	offset = 12 - len(input) # 12 is ~arbitrary based on the locations currently being used, this can be modified
			curWin.label.append(0)
			curWin.label.append(position)
			curWin.label.append(input)
			curWin.label.append(color)
		else:
			self.screen.addstr(y, x, input, curses.color_pair(color))

	def addNotification(self, y, x, input, color=5):
		"""
		Adds a notification to the screen to inform the user of a status or event

		Parameters:
		y - row coordinate on larger window object to display
		x - column coordinate
		input - the warning message to display
		color - the color of the warning, defaulted to red
		"""
		self.clearWarning(y,x)
		self.screen.addstr(y,x, input, curses.color_pair(color))
		self.screen.refresh()

	def addUIElement(self, elem, mapping, tab, locations, height=0, width=0, items=None, box=True, highlighted=True, text=None):
		"""
		Adds a specific case of a 'window', with the required parameters

		Parameters:
		elem - the type of window pad to add
		mapping - name of the window to easily control elements
		tab - the tabstop number, used in navigation
		height - number of rows for the pad
		width - number of columns for the pad
		y - the starting row location
		x - the starting colun location
		items - a list of the items that will be displayed in the window; may be a specially formatted dictionary
		box - boolean on whether to draw a box around the window
		highlighted - boolean, determines if the window should be highlighted when focused
		text - the text to display in the window
		"""
		y,x = self.getLocation(locations, mapping)

		if elem == 'list':
			self.windows.append(listWindow(height, width, y, x, items, tab.maxTab, box, highlighted))
			self.mapWindows.append({mapping:tab.maxTab})
		elif elem == 'timeWin':
			newWin = listWindow(height, width, y, x, items, tab.maxTab, box, highlighted)
			newWin.display = displayDateTime
			self.windows.append(newWin)
			self.mapWindows.append({mapping:tab.maxTab})
		elif elem == 'pagedWin':
			self.windows.append(pagedWindow(height, width, y, x, items, tab.maxTab, box, highlighted))
			self.mapWindows.append({mapping:tab.maxTab})
		elif elem == 'pagedWinUsers':
			newWin = pagedWindow(height, width, y, x, items, tab.maxTab, box, highlighted)
			newWin.display = displayUserString
			self.windows.append(newWin)
			self.mapWindows.append({mapping:tab.maxTab})
		elif elem == 'pagedWinTimes':
			newWin = pagedWindow(height, width, y, x, items, tab.maxTab, box, highlighted)
			newWin.display = displayWindow
			self.windows.append(newWin)
			self.mapWindows.append({mapping:tab.maxTab})
		elif elem == 'button':
			self.windows.append(button(y, x, text, tab.maxTab, box, highlighted))
			self.mapWindows.append({mapping:tab.maxTab})
		elif elem == 'input':
			self.windows.append(inputBox(y, x, width, tab.maxTab, box, highlighted))
			self.mapWindows.append({mapping:tab.maxTab})
		elif elem == 'checkbox':
			self.windows.append(checkbox(y, x, text, tab.maxTab, box, highlighted))
			self.mapWindows.append({mapping:tab.maxTab})
		elif elem == 'textLine':
			self.windows.append(textLine(y, x, width, text, tab.maxTab, box, highlighted))
			self.mapWindows.append({mapping:tab.maxTab})
		tab.incTab()

	def drawGUI(self, tab):
		"""
		Draws a box around the screen and refreshes the screen.
		"""
		tab.maxTab = len(self.windows) - 1
		#self.screen.box()
		self.screen.refresh()
		return True

	def cleanGUI(self):
		"""
		Erases the screen and resets the windows and mapWindows arrays.
		"""
		self.screen.erase()
		#self.screen.box()
		self.windows = []
		self.mapWindows = []
		return True

	def clearWarning(self, y, x):
		"""
		Removes the warning message
		"""
		self.screen.move(y,x)
		self.screen.clrtoeol() # clears to the end of the line, this will remove items in between cursor and end of line, be careful
		#self.screen.box()

	def close(self):
		"""
		Closes the GUI window and resets terminal control.
		"""
		self.cleanGUI()
		self.screen.erase()
		curses.nocbreak()
		self.screen.keypad(0)
		curses.echo()
		curses.endwin()
		return True

	def getDate(self, input):
		"""
		Gets the values for the date attributes off the pads

		Parameters
		input - a string that is used in finding the dictionary key, so we can obtain the value
		"""
		monthI = self.getMap(input+'M')	# get the index that holds the month
		dayI = self.getMap(input+'D')	# get the index that holds the day
		yearI = self.getMap(input+'Y')	# get the index that holds the year
		# returns in the expected format
		return (self.windows[monthI].getSelectedValue() + "/" + self.windows[dayI].getSelectedValue() + "/" + self.windows[yearI].getSelectedValue())

	def getLocation(self, locations, window):
		"""
		Returns the x or y coordinate of the window referred to by window
		"""
		for x in locations:
			if x['win'] == window:
				return x['y'], x['x']

	def getMap(self, input):
		"""
		Returns the value of the tab index for the specific name of a window.
		Works by taking the string and finding that key, then returns the value at that key.
		"""
		return [x[input] for x in self.mapWindows if input in x][0]

	def getKey(self, tab):
		return [key for key in self.mapWindows[tab].keys()][0]

	def getStates(self):
		"""
		Grabs the values of dates and time from the window
		Returns the start date and time, and length as a tuple
		"""
		# get the values for everything on the board
		# compose indices and prep for ouput
		#userNames = []							# will hold the list of users that has been selected
		#index = self.getMap('selectedUsers')		# the index (tabstop) for the people the user has selected to query
		#for x in self.windows[index].items:		
		#	userNames.append(x)
		startDate = self.getDate("startDate")	# gets the starting date, in a standard format MM/DD/YYYY
		if self.winExists('endDateM'):
			endDate = self.getDate("endDate")	# gets ending date
		else:
			endDate = startDate
		startTime = self._getTime("start")		# gets starting time, in standard format HH:MM
		try:
			length = self.windows[self.getMap('length')].getSelectedValue() # gets the length attribute
		except:
			length = 15
		# print self.winExists('endH')
		try:
			endTime = self._getTime("end")			# gets ending time\
		except:
			hours = int(startTime[0:2])
			mins = int(startTime[3:5])
			#print hours, mins
			totalMins = getTotalMinutes(hours, mins)
			endTime = totalMins + int(length)
			endTime = printTime(endTime, True)
			# print endTime
		start = startDate + " " + startTime		# create the date time string that the interface is expecting
		end = endDate + " " + endTime
		return start, end, int(length)#, userNames

	def getTab(self, tab):
		"""
		Based on the tab location, returns the pad assigned to that tabstop.
		"""
		for x in self.windows:
			if x.tab == tab:
				return x
		return None

	def _getTime(self, input):
		"""
		Gets the values for the time attributes from the pads

		Parameters
		input - string used in the dictionary key
		"""
		hourI = self.getMap(input+'H')	# get the index that holds the hour
		minI = self.getMap(input+'M')	# get the index that holds the minutes
		# return as a string in the expected format
		return (self.windows[hourI].getSelectedValue() + ":" + self.windows[minI].getSelectedValue())

	def getWin(self, input):
		"""
		Returns the window object for manipulation
		"""
		index = self.getMap(input)
		return self.getTab(index)

	def redrawGUI(self, tab):
		"""
		Redraws pads, based on which pad is currently active

		Parameters
		gui - GUI() object that contains list of windows
		tab - the current tabstop
		"""
		activeWin = self.getTab(tab)
		for x in self.windows:
			if x.modified:
				if x == activeWin:
					# adds the highlighting
					if x.highlighted:
						x.display(x, True, True)
					else:
						x.display(x, True)
				else:
					x.display(x)

	def winExists(self,input):
		"""
		Returns true if the window is in the mapWindows array
		"""
		if input in self.mapWindows[0]:
			return True
		return False

class GUIPad:
	"""
	Parent class for a pad.
	"""
	def __init__(self, height, width, y, x, tab=0, highlighted=False):
		global GUIScreen
		self.screen = GUIScreen 	# the screen object that is parent to the pad
		self.tab = tab 			# the tabstop for this specific pad
		self.pad = self._newBox(height, width, y, x) # draws the pad
		self.highlighted = highlighted
		self.modified = True
		self.label = []

	def _newBox(self,height,width,y,x):
		"""
		Returns a subpad object

		Parameters:
		height - height of pad in text columns
		width - width of pad in text columns
		y - start location of rows the larger screen
		x - start location of columns in the larger screen
		"""
		window = self.screen.subpad(height, width, y, x)
		return window

	def getmaxyx(self):
		"""
		A specially wrapped method of getting the size of the pad.
		Returns Y,X tuple
		"""
		return self.pad.getmaxyx()

	def addLabel(self):
		self.pad.addstr(self.label[0], self.label[1], self.label[2], curses.color_pair(self.label[3]))

class inputBox(GUIPad):
	def __init__(self, y, x, width, tab, box=True, highlighted=True):
		height = 3
		GUIPad.__init__(self, height, width, y, x, tab, highlighted)
		self.box = box
		self.scrollable = False
		self.length = width - 2
		self.display = displayStatic
		self.x = x
		self.y = y

	def inputParams(self):
		return (self.y + 1, self.x + 1, self.length)

	def clean(self):
		self.modified = True

class button(GUIPad):
	def __init__(self, y, x, text, tab, box=True, highlighted=True):
		width = len(text) + 4 # dynamic size of button
		height = 3 # basic height of button
		GUIPad.__init__(self, height, width, y, x, tab, highlighted)
		self.box = box 	# tracks whether the pad should be boxed or not
		self.text = text
		self.scrollable = False
		self.display = displayStatic

class textLine(GUIPad):
	def __init__(self, y, x, width, text, tab, box=True, highlighted=True):
		height = 3 # basic height of button
		GUIPad.__init__(self, height, width, y, x, tab, highlighted)
		self.box = box 	# tracks whether the pad should be boxed or not
		self.text = text
		self.scrollable = False
		self.display = displayStatic

class listWindow(GUIPad):
	"""
	A child class of the GUIPad. Provides additional functionality, ties a list to the window, handles display and interaction

	A parent class of timeWindow and dateWindow.
	"""
	def __init__(self, height, width, y, x, items, tab, box=True, highlighted=False):
		GUIPad.__init__(self, height, width, y, x, tab, highlighted)
		self.selection = 0 		# tracks which item is selected in the list tied to this object
		self.scrollable = True 	# boolean for whether the pad has scrollable values are not
		self.box = box 			# tracks whether the pad should be boxed or not
		self.items = items 		# ties a list to this particular pad object
		self.display = displayList

	def setScrollable(self, input):
		"""
		Modifies the scrollable attribute

		Parameters
		input - boolean which dictates whether this object is scrollable or not
		"""
		self.scrollable = input
		return True

	def changeItems(self, items):
		"""
		Changes the items array of the current window to a different array.
		"""
		self.selection = 0
		self.modified = True
		self.items = items
		return True

	def changeSelection(self, direction):
		"""
		Modifies the current selection of the list 

		Parameters
		direction - -1 for up, +1 for down, 0 to reset after an event
		"""
		self.modified = True
		self.selection = self.selection + direction
		# correct for going out of bounds
		if self.selection == len(self.items):
			self.selection = 0
		if self.selection == -1:
			self.selection = len(self.items) - 1
		return True

	def getSelectedValue(self):
		"""
		Returns the currently selected value of the list
		Wrapped in a try to prevent an out of range error when the list is empty
		"""
		try:
			return self.items[self.selection]
		except:
			return None

class timeWindow(listWindow):
	"""
	A child class of the GUIPad. Provides additional functionality, ties a list to the window, handles display and interaction

	A parent class of timeWindow and dateWindow.
	"""
	def __init__(self, height, width, y, x, items, tab, box=True, highlighted=False):
		listWindow.__init__(self, height, width, y, x, items, tab, box, highlighted)
		self.display = displayDateTime

class pagedWindow(listWindow):
	"""
	A child of the listWindow class. Allows indexing of multiple windows to one tab, displaying only the currently highlighted window.
	"""
	def __init__(self, height, width, y, x, items, tab, box=True, highlighted=True):
		listWindow.__init__(self, height, width, y, x, items, tab, box, highlighted)
		self.focus = 0
		self.selection = []
		self.display = displayPagedWindow

	def changeSelection(self, direction):
		self.modified = True
		self.selection[self.focus] = self.selection[self.focus] + direction
		# correct for going out of bounds
		try:
			if self.selection[self.focus] == len(self.items[self.focus]['times']):
				self.selection[self.focus] = 0
			if self.selection[self.focus] == -1:
				self.selection[self.focus] = len(self.items[self.focus]['times']) - 1
		except:
			if self.selection[self.focus] == len(self.items[self.focus]['users']):
				self.selection[self.focus] = 0
			if self.selection[self.focus] == -1:
				self.selection[self.focus] = len(self.items[self.focus]['users']) - 1

		return True

	def changeFocus(self, direction):
		"""
		Changes which array index is being viewed. Allows multiple windows to be indexed to one tabstop.
		"""
		self.modified = True
		self.focus = self.focus + direction
		if self.focus == len(self.items):
			self.focus = 0
		if self.focus == - 1:
			self.focus = len(self.items) - 1
		return True

class checkbox(GUIPad):
	def __init__(self, y, x, text, tab, box=True, highlighted=True):
		width = len(text) + 5
		height = 3
		GUIPad.__init__(self, height, width, y, x, tab, highlighted)
		self.box = box
		self.text = text
		self.scrollable = False
		self.display = displayCheckbox
		self.checked = False

class tabstop:
	"""
	The tab class. Used to help manuevering through the windows on the curses pad.
	"""
	def __init__(self):
		self.tab = 0
		self.maxTab = 0

	def nextTab(self):
		"""
		Move the tab stop up one
		"""
		self.tab = self.tab + 1
		if self.tab > self.maxTab:
			self.tab = 0

	def prevTab(self):
		"""
		Move the tab stop down one
		"""
		self.tab = self.tab - 1
		if self.tab < 0:
			self.tab = self.maxTab

	def incTab(self):
		"""
		Used to increase the maximum amount of tabs
		"""
		self.maxTab = self.maxTab + 1
		return self.maxTab