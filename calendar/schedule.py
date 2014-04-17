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

	def addLabel(self, y, x, input, justify=None):
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
		self.screen.addstr(y, x + offset, input, curses.color_pair(1))

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
		startDate = self._getDate("startDate")	# gets the starting date, in a standard format MM/DD/YYYY
		endDate = self._getDate("endDate")		# gets ending date
		startTime = self._getTime("start")		# gets starting time, in standard format HH:MM
		endTime = self._getTime("end")			# gets ending time
		length = self.windows[self.getMap('length')].getSelectedValue() # gets the length attribute
		start = startDate + " " + startTime		# create the date time string that the interface is expecting
		end = endDate + " " + endTime
		return start, end, int(length), userNames

	def _getDate(self, input):
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
	def __init__(self, screen, height, width, y, x, tab=0):
		self.screen = screen 	# the screen object that is parent to the pad
		self.tab = tab 			# the tabstop for this specific pad
		self.pad = self._newBox(height, width, y, x) # draws the pad

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

class listWindow(GUIPad):
	"""
	A child class of the GUIPad. Provides additional functionality, ties a list to the window, handles display and interaction
	"""
	def __init__(self, screen, height, width, y, x, items, tab=0, box=True):
		GUIPad.__init__(self, screen, height, width, y, x, tab)
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

	def listItems(self, focus = False):
		"""
		Display the tied list of this object. Paginates based on the height of the pad and the length of the list.

		Parameters
		focus - if this object is the location of the current tabstop, provide option to move the values
		"""
		self.pad.clear() # completely wipes this pad
		height, width = self.pad.getmaxyx() # get the size of the pad
		height = height - 2 # remove padding
		page = 0 # for pagination
		if self.selection >= height:
			page = self.selection / height # determines which page the current selection should be on
		for x in range(0,height): # displays as many lines as can be clean fit inside the pad
			index = x + (page * height) # holds the index for items to be displayed, as we are not just listing the first X amount
			if (index) < len(self.items): # prevent out of range error
				if focus and self.scrollable: # the object is focused, so there will be a color change, and it scrollable so we can display the cursor
					if (index) == self.selection: # controls the highlighting of the current selection
						self.pad.addstr(x+1,2, str(self.items[index]), curses.color_pair(2)) # differentiate
					else:
						self.pad.addstr(x+1,2, str(self.items[index]))
				else:
					self.pad.addstr(x+1,2, str(self.items[index]))
		if self.box: # draws box is we are supposed to
			self.pad.box()
		self.pad.refresh() # redraw the pad

	def changeItems(self, items):
		self.items = items
		return True

	def changeSelection(self, direction):
		"""
		Modifies the current selection of the list 

		Parameters
		direction - -1 for up, +1 for down, 0 to reset after an event
		"""
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

def selectedEvent(removes, appends, value):
	"""
	On enter inside a field, an event occurs.
	Wrapped in a try..except to prevent values that are no longer in the list from being removed

	Parameters
	removes - the list to remove the value from
	appends - the list to append the value to
	value - the specific value that should be removed and appended
	"""
	try:
		removes.remove(value)
		appends.append(value)
	except:
		pass

def calcTimeSlots():
	"""
	This is the initial work user scenario 3
	Builds GUI and sets up data structures
	Queries the interface to get the calendar information
	"""
	# Instantiate a new GUI module
	timeslots = GUI()

	# Testing purposes
	startY = 5
	startX = 46

	# Add all labels
	timeslots.addLabel(3,6,"Select Users")
	timeslots.addLabel(17,6,"Currently Selected")
	timeslots.addLabel(startY,startX,"Start date:","right")
	timeslots.addLabel(startY+3,startX,"End date:","right")
	timeslots.addLabel(startY+6,startX,"Start time:","right")
	timeslots.addLabel(startY+9,startX,"End time:","right")
	timeslots.addLabel(startY+12,startX,"Length:","right")

	# add all the windows that will contain lists of information
	timeslots.windows.append(listWindow(timeslots.screen, 12, 40, 4, 4, users, 0))
	timeslots.mapWindows.append({'selectUsers':0})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 6, 4, 60, months, 1, False))
	timeslots.mapWindows.append({'startDateM':1})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 6, 4, 64, days, 2, False))
	timeslots.mapWindows.append({'startDateD':2})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 8, 4, 68, years, 3, False))
	timeslots.mapWindows.append({'startDateY':3})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 6, 7, 60, months, 4, False))
	timeslots.mapWindows.append({'endDateM':4})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 6, 7, 64, days, 5, False))
	timeslots.mapWindows.append({'endDateD':5})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 8, 7, 68, years, 6, False))
	timeslots.mapWindows.append({'endDateY':6})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 6, 10, 60, hours, 7, False))
	timeslots.mapWindows.append({'startH':7})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 8, 10, 64, mins, 8, False))
	timeslots.mapWindows.append({'startM':8})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 6, 13, 60, hours, 9, False))
	timeslots.mapWindows.append({'endH':9})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 8, 13, 64, mins, 10, False))
	timeslots.mapWindows.append({'endM':10})

	timeslots.windows.append(listWindow(timeslots.screen, 3, 8, 16, 60, lengths, 11, False))
	timeslots.mapWindows.append({'length':11})

	timeslots.windows.append(listWindow(timeslots.screen, 12, 40, 18, 4, selected, 12))
	timeslots.mapWindows.append({'selectedUsers':12})

	timeslots.drawGUI()
	tab = 0
	timeslots.redrawGUI(tab)

	while True:
		event = timeslots.screen.getch()
		if event == ord("q"):
			timeslots.close()
			break
		elif event == curses.KEY_DOWN:
			# find which window we're in and modify that value
			# move the index forward 1
			activeWin = timeslots.getWin(tab)
			try:
				activeWin.changeSelection(+1)
			except:
				pass
			timeslots.redrawGUI(tab)
		elif event == curses.KEY_UP:
			# find which window we're in and modify that value
			# move the index back 1
			activeWin = timeslots.getWin(tab)
			try:
				activeWin.changeSelection(-1)
			except:
				pass
			timeslots.redrawGUI(tab)
		elif event == curses.KEY_LEFT:
			# move the tabstop and redraw windows, highlighting the next window
			tab = tab - 1
			if tab < 0:
				tab = len(timeslots.windows) - 1
			timeslots.redrawGUI(tab)
		elif event == ord("\t") or event == curses.KEY_RIGHT:
			# move the tabstop and redraw windows, highlighting the next window
			tab = tab + 1
			if tab >= len(timeslots.windows):
				tab = 0
			timeslots.redrawGUI(tab)
		elif event == ord("\n"):
			# on this screen, there are only two boxes that will prompt an event
			if tab == timeslots.getMap('selectUsers'):
				activeWin = timeslots.getWin(tab)
				modifyIndex = timeslots.getMap('selectedUsers')
				changeWin = timeslots.getWin(modifyIndex)
				value = activeWin.getSelectedValue()
				selectedEvent(activeWin.items, changeWin.items, value)
				activeWin.changeSelection(0)
			# in the selected user box, remove selected user
			elif tab == timeslots.getMap('selectedUsers'):
				activeWin = timeslots.getWin(tab)
				modifyIndex = timeslots.getMap('selectUsers')
				changeWin = timeslots.getWin(modifyIndex)
				value = activeWin.getSelectedValue()
				selectedEvent(activeWin.items, changeWin.items, value)
				activeWin.changeSelection(0)

			timeslots.redrawGUI(tab)
		
		elif event == ord("p"):
			# process the event
			service = connection()
			userNames = []
			people = []
			#############################################################
			#															#
			# This line will require SIGNIFICANT error checking:		#
			# -ensure the end date and time are after the start 		#
			# -for this particular case, the dates should be the same 	#
			# -odd days of the month? 30t of feb, 31 of Nov, etc        #
			# -edge cases 												#
			# -years?													#
			#															#
			#############################################################
			start, stop, length, userNames = timeslots.getStates()
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
				times.append(printTime(x))
			# check if we have already polled results, if so, then just modify that structure
			try:
				index = timeslots.getMap('results')
			except:
				index = 0

			if index:
				resultsWin = timeslots.getWin(index)
				resultsWin.changeItems(times)
			else:
				timeslots.addLabel(31,6,"Available Times")
				timeslots.windows.append(listWindow(timeslots.screen, 20, 20, 32, 4, times, 13))
				timeslots.mapWindows.append({'results':13})
			
			# rebuild GUI
			timeslots.redrawGUI(tab)

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

	scenario = 3

	if scenario == 3:
		calcTimeSlots()