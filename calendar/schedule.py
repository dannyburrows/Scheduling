#!
# /*************************************\
# |* Building the UI with Curses       *|
# |* Written by Danny Burrows          *|
# |* burrows.danny@gmail.com           *|
# |* CS419 - Spring 2014               *|
# |* Group Project                     *|
# |* 04/17/2014                        *|
# |*	                               *|
# |* Implementation of the scheduler   *|
# |* program. Currently handles case   *|
# |* 3 but still missing functionality *|
# |* for database integration.         *|
# |*                                   *|
# \*************************************/

import curses
from interface import *
from timemanip import *

class GUI:
	"""
	The GUI class is the major component of the curses interface. This class sets up the screen that pads are added to.
	Handles the initializaiton and closing of the interface and basic functionality.
	"""
	windows = [] 	# holds a list of all the windows that will be generated
	mapWindows = []	# keeps a mapping of the name of the window and it's tabstop

	def __init__(self):
		self.screen = curses.initscr()	# the main screen that everything will be displayed to
		curses.noecho() # no key presses to the screen
		curses.curs_set(0) # removes cursor from screen
		self.screen.keypad(1) # captures keypresses
		curses.start_color()

		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
		curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
		curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)

	def drawGUI(self):
		"""
		Draws a box around the screen and refreshes the screen.
		"""
		self.screen.box()
		self.screen.refresh()
		return True

	def redrawGUI(self, tab):
		"""
		Redraws pads, based on which pad is currently active

		Parameters
		gui - GUI() object that contains list of windows
		tab - the current tabstop
		"""
		activeWin = self.getWin(tab)
		for x in self.windows:
			if x == activeWin:
				# adds the highlighting
				if x.highlighted:
					x.listItems(True, True)
				else:
					x.listItems(True)
			else:
				x.listItems()

	def cleanGUI(self):
		self.screen.erase()
		self.screen.box()
		self.windows = []
		return True

	def close(self):
		"""
		Closes the GUI window and resets terminal control.
		"""
		curses.nocbreak()
		self.screen.keypad(0)
		curses.echo()
		curses.endwin()
		return True

	def getMap(self, input):
		"""
		Returns the value of the tab index for the specific name of a window.
		Works by taking the string and finding that key, then returns the value at that key.
		"""
		return [x[input] for x in self.mapWindows if input in x][0]

	def getWin(self, tab):
		"""
		Based on the tab location, returns the pad assigned to that tabstop.
		"""
		for x in self.windows:
			if x.tab == tab:
				return x
		return None

	def addLabel(self, y, x, input, justify=None, color=1):
		"""
		Displays a label at specific location.

		Parameters:
		y - row coordinate on larger window object to display
		x - column coordiante
		input - text to display
		justify - if the text needs to right justified
		"""
		# will right justify
		offset = 0
		if justify == "right":
			offset = 12 - len(input) # 12 is ~arbitrary based on the locations currently being used, this can be modified
		self.screen.addstr(y, x + offset, input, curses.color_pair(color))

	def addNotification(self, y, x, input, color):
		self.clearWarning(y,x)
		self.screen.addstr(y,x, input, curses.color_pair(color))
		self.screen.refresh()

	def clearWarning(self, y, x):
		self.screen.move(y,x)
		self.screen.clrtoeol()
		self.screen.box()

	def getStates(self):
		"""
		Grabs the values of every item in the window
		"""
		# get the values for everything on the board
		# compose indices and prep for ouput
		userNames = []							# will hold the list of users that has been selected
		index = self.getMap('selectedUsers')		# the index (tabstop) for the people the user has selected to query
		for x in self.windows[index].items:		
			userNames.append(x)
		startDate = self.getDate("startDate")	# gets the starting date, in a standard format MM/DD/YYYY
		if self.winExists('endDateM'):
			endDate = self.getDate("endDate")	# gets ending date
		else:
			endDate = startDate
		startTime = self._getTime("start")		# gets starting time, in standard format HH:MM
		endTime = self._getTime("end")			# gets ending time
		length = self.windows[self.getMap('length')].getSelectedValue() # gets the length attribute
		start = startDate + " " + startTime		# create the date time string that the interface is expecting
		end = endDate + " " + endTime
		return start, end, int(length), userNames

	def winExists(self,input):
		if input in self.mapWindows[0]:
			return True
		return False

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

class GUIPad:
	"""
	Parent class for a pad.
	"""
	def __init__(self, screen, height, width, y, x, tab=0, highlighted=False):
		self.screen = screen 	# the screen object that is parent to the pad
		self.tab = tab 			# the tabstop for this specific pad
		self.pad = self._newBox(height, width, y, x) # draws the pad
		self.highlighted = highlighted
		self.modified = True

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

class button(GUIPad):
	def __init__(self, screen, y, x, text, tab, box=True, highlighted=True):
		width = len(text) + 4
		height = 3
		GUIPad.__init__(self, screen, height, width, y, x, tab, highlighted)
		self.box = box 	# tracks whether the pad should be boxed or not
		self.text = text
		self.scrollable = False

	def listItems(self, focus=False, highlight=False):
		"""
		Display the tied list of this object. Paginates based on the height of the pad and the length of the list.

		Parameters
		focus - if this object is the location of the current tabstop, provide option to move the values
		"""
		if not self.modified:
			return
		self.pad.clear() # completely wipes this pad
		if highlight:
			self.pad.bkgd(curses.color_pair(3))
		else:
			self.pad.bkgd(curses.color_pair(4))
		self.pad.addstr(1,2,self.text)
		if self.box: # draws box is we are supposed to
			self.pad.box()
		self.pad.refresh() # redraw the pad
		self.modified = False

class listWindow(GUIPad):
	"""
	A child class of the GUIPad. Provides additional functionality, ties a list to the window, handles display and interaction
	"""
	def __init__(self, screen, height, width, y, x, items, tab, box=True, highlighted=False):
		GUIPad.__init__(self, screen, height, width, y, x, tab, highlighted)
		self.selection = 0 		# tracks which item is selected in the list tied to this object
		self.scrollable = True 	# boolean for whether the pad has scrollable values are not
		self.box = box 			# tracks whether the pad should be boxed or not
		self.items = items 		# ties a list to this particular pad object

	def setScrollable(self, input):
		"""
		Modifies the scrollable attribute

		Parameters
		input - boolean which dictates whether this object is scrollable or not
		"""
		self.scrollable = input
		return True

	def listItems(self, focus = False, highlight=False):
		"""
		Display the tied list of this object. Paginates based on the height of the pad and the length of the list.

		Parameters
		focus - if this object is the location of the current tabstop, provide option to move the values
		"""
		if not self.modified:
			return
		self.pad.clear() # completely wipes this pad
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

	def changeItems(self, items):
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

class tabstop:
	def __init__(self):
		self.tab = 0
		self.maxTab = 0

	def nextTab(self):
		self.tab = self.tab + 1
		if self.tab > self.maxTab:
			self.tab = 0

	def prevTab(self):
		self.tab = self.tab - 1
		if self.tab < 0:
			self.tab = self.maxTab

	def incTab(self):
		self.maxTab = self.maxTab + 1
		return self.maxTab

class timeSlots():
	def __init__(self):
		self.gui = GUI()
		self.tab = tabstop()
		self.selected = []
		self.users = ['burrows.danny@gmail.com', 'jonesjo@onid.oregonstate.edu', 'clampitl@onid.oregonstate.edu', 'jjames83@gmail.com']
		self.warningY = 54
		self.warningX = 6
		self.buildWindows()
		self.tab.tab = 0
		self.gui.drawGUI()
		self.gui.redrawGUI(self.tab.tab)

	def buildWindows(self):
		# add all the windows that will contain lists of information
		self.gui.addLabel(2,6," Select Users ")
		self.gui.windows.append(listWindow(self.gui.screen, 16, 40, 3, 4, users, self.tab.maxTab, True, True))
		self.gui.mapWindows.append({'selectUsers':self.tab.maxTab})

		self.gui.addLabel(20,6," Currently Selected ")
		self.gui.windows.append(listWindow(self.gui.screen, 16, 40, 21, 4, selected, self.tab.incTab(), True, True))
		self.gui.mapWindows.append({'selectedUsers':self.tab.maxTab})

		self.gui.addLabel(38, 20, "MM / DD / YYYY", color=4)
		self.gui.addLabel(40, 6,"Start date:","right")
		self.gui.windows.append(listWindow(self.gui.screen, 3, 6, 39, 18, months, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startDateM':self.tab.maxTab})

		self.gui.windows.append(listWindow(self.gui.screen, 3, 6, 39, 23, days, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startDateD':self.tab.maxTab})

		self.gui.windows.append(listWindow(self.gui.screen, 3, 8, 39, 28, years, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startDateY':self.tab.maxTab})

		self.gui.addLabel(42,20,"MM : HH",color=4)
		self.gui.addLabel(44,6,"Start time:","right")
		self.gui.windows.append(listWindow(self.gui.screen, 3, 6, 43, 18, hours, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startH':self.tab.maxTab})
		self.gui.windows.append(listWindow(self.gui.screen, 3, 8, 43, 22, mins, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startM':self.tab.maxTab})

		self.gui.addLabel(46,20,"MM : HH",color=4)
		self.gui.addLabel(48,6,"End time:","right")
		self.gui.windows.append(listWindow(self.gui.screen, 3, 6, 47, 18, hours, self.tab.incTab(), False))
		self.gui.mapWindows.append({'endH':self.tab.maxTab})

		self.gui.windows.append(listWindow(self.gui.screen, 3, 8, 47, 22, mins,self.tab.incTab(), False))
		self.gui.mapWindows.append({'endM':self.tab.maxTab})

		self.gui.addLabel(50,20,"Mins", color=4)
		self.gui.addLabel(52,6,"Length:","right")
		self.gui.windows.append(listWindow(self.gui.screen, 3, 8, 51, 18, lengths, self.tab.incTab(), False))
		self.gui.mapWindows.append({'length':self.tab.maxTab})

		self.gui.windows.append(button(self.gui.screen,56,6,"Submit",self.tab.incTab()))
		self.gui.mapWindows.append({'submit':self.tab.maxTab})

		self.gui.windows.append(button(self.gui.screen,56,18:00,"Exit",self.tab.incTab()))
		self.gui.mapWindows.append({'exit':self.tab.maxTab})

	def mainLoop(self):
		while True:
			event = self.gui.screen.getch()
			if event == ord("q"):
				self.gui.close()
				break
			elif event == curses.KEY_DOWN:
				self._processUpDown(+1)
			elif event == curses.KEY_UP:
				self._processUpDown(-1)
			elif event == curses.KEY_LEFT:
				self._moveTab(-1)
			elif event == ord("\t") or event == curses.KEY_RIGHT:
				self._moveTab(+1)
			elif event == ord("\n"):
				self.processEnter()

			self.gui.redrawGUI(self.tab.tab)

	def _processUpDown(self, direction):
		# find which window we're in and modify that value
		# move the index back 1
		activeWin = self.gui.getWin(self.tab.tab)
		if activeWin.scrollable == False:
			self.gui.addNotification(self.warningY, self.warningX, "Cannot modify value",5)
		elif self.tab.tab == self.gui.getMap('startDateM') or self.tab.tab == self.gui.getMap('startDateD') or self.tab.tab == self.gui.getMap('startDateY'):
			try:
				activeWin.changeSelection(direction)	
			except:
				pass
		else:
			try:
				activeWin.changeSelection(direction)
			except:
				pass

	def _moveTab(self, direction):
		if direction == +1:
			# move the tabstop and redraw windows, highlighting the next window
			self.gui.clearWarning(self.warningY, self.warningX)
			curWin = self.gui.getWin(self.tab.tab)
			self.tab.nextTab()
			newWin = self.gui.getWin(self.tab.tab)
			newWin.modified = True
			curWin.modified = True
		elif direction == -1:
			# move the tabstop and redraw windows, highlighting the next window
			self.gui.clearWarning(self.warningY, self.warningX)
			curWin = self.gui.getWin(self.tab.tab)
			self.tab.prevTab()
			newWin = self.gui.getWin(self.tab.tab)
			curWin.modified = True
			newWin.modified = True

	def processEnter(self):
		if self.tab.tab == self.gui.getMap('selectUsers'):
			self._swapEvent('selectedUsers')
		elif self.tab.tab == self.gui.getMap('selectedUsers'):
			self._swapEvent('selectUsers')
		elif self.tab.tab == self.gui.getMap('submit'):
			self.submitRequest()
		elif self.tab.tab == self.gui.getMap('exit'):
			self.gui.close()
			exit()

	def _swapEvent(self, appendWin):
		"""
		On enter inside a field, an event occurs.
		Wrapped in a try..except to prevent values that are no longer in the list from being removed

		Parameters
		removes - the list to remove the value from
		appends - the list to append the value to
		value - the specific value that should be removed and appended
		"""
		removeWin = self.gui.getWin(self.tab.tab)
		addIndex = self.gui.getMap(appendWin)
		addWin = self.gui.getWin(addIndex)
		value = removeWin.getSelectedValue()
		try:
			removeWin.items.remove(value)
			addWin.items.append(value)
		except:
			pass
		removeWin.changeSelection(0)
		addWin.changeSelection(0)

	def submitRequest(self):
		self.gui.addNotification(self.warningY, self.warningX, "Processing request...", 5)
		curWin = self.gui.getWin(self.tab.tab)
		curWin.modified = True
		
		if self.calcTimesSlots():
			self.tab.tab = self.tab.maxTab
			pass
		else:
			curWin.modified = False
		self.gui.addNotification(self.warningY, self.warningX, "Finished!!", 1)

	def calcTimesSlots(self):
				# process the event
				service = connection()
				userNames = []
				people = []
				#############################################################
				#															#
				# This line will require SIGNIFICANT error checking:		#
				# -ensure the end date and time are after the start 		#
				# -odd days of the month? 30t of feb, 31 of Nov, etc        #
				# -edge cases 												#
				# -years?													#
				#															#
				#############################################################
				start, stop, length, userNames = self.gui.getStates()
				#############################################################
				#															#
				# Start the integration with the interface for the calendar #
				# api and other functions.                                  #
				# Need to work on the interface to automatically add events #
				# that are pulled from database, no need to do it here.     #
				#															#
				#############################################################
				for user in userNames:
				 	people.append(person(user, length, service.service))

				# create a meeting object that will hold availability information for the group
				newMeeting = meeting(start, stop, length, people)
				# run algorithm to find available time slots
				newMeeting.availInTimeSlot()
				times = []
				# no need to access directly
				for x in newMeeting.availableTimes:
					# user friendly format
					times.append(printTime(x) + " - "+ printTime(x + length))
				# check if we have already polled results, if so, then just modify that structure
				try:
					index = self.gui.getMap('results')
				except:
					index = 0

				if index:
					resultsWin = self.gui.getWin(index)
					resultsWin.changeItems(times)
				else:
					self.gui.addLabel(3,64,"Available Times")
					maxSize = len(times) + 1
					if len(times) > 50:
						maxSize = 50

					self.gui.windows.append(listWindow(self.gui.screen, maxSize + 2, 23, 6, 60, times, self.tab.incTab(), True, True))
					self.gui.mapWindows.append({'results':self.tab.maxTab})

				date = self.gui.getDate('startDate')
				self.gui.addLabel(4,67,date, color=4)				
				return True

if __name__ == "__main__":
	# Test structures
	months = [str(x).zfill(2) for x in range(1, 13)]
	days = [str(x).zfill(2) for x in range(1, 32)]
	years = [str(x) for x in range(2014,2021)]
	hours = [str(x).zfill(2) for x in range(0,24)]
	mins = [str(x).zfill(2) for x in range(0,75,15)]
	lengths = [str(x) for x in range(15,375,15)]
	selected = []
	users = ['burrows.danny@gmail.com', 'jonesjo@onid.oregonstate.edu', 'clampitl@onid.oregonstate.edu', 'jjames83@gmail.com']

	scenario = timeSlots()
	scenario.mainLoop()

	# scenario = 3

	# if scenario == 3:
	# 	displayTimeSlots()
		#calcTimeSlots()