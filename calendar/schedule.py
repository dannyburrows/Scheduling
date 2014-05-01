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

from interface import *
from timemanip import *
from curseswrapper import *

class timeFrame:
	def __init__(self):
		self.gui = GUI()
		# deletes gui images already mapped
		self.gui.windows = []
		self.gui.mapWindows = []
		self.tab = tabstop()
		self.selected = []
		#self.users = ['burrows.danny@gmail.com', 'jonesjo@onid.oregonstate.edu', 'clampitl@onid.oregonstate.edu', 'jjames83@gmail.com']
		#self.users = [x for x in range(0, 40)]
		# will hold the dates to check for multiple dates and times
		# array of tuples, taking the type: { 'date': 'MM/DD/YYYY', 'times': ['MM:HH'] }
		self.dates = []
		self.warningY = 28
		self.warningX = 65
		self.buildWindows()
		self.tab.tab = 0
		self.gui.drawGUI(self.tab)
		self.setSelections()
		self.gui.redrawGUI(self.tab.tab)

	def setSelections(self):
		now = datetime.now()
		day = int(now.strftime("%d"))
		month = int(now.strftime("%m"))
		year = int(now.strftime("%Y"))
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
		# quickly allows me to move the entirety of the input UI
		y = 4
		x = 60

		maxY, maxX = self.gui.screen.getmaxyx()
		changeX = maxX / 10
		changeY = maxY / 10

		# add all the windows that will contain lists of information
		 
		# Listing windows
		#self.gui.addLabel(5,6," Select Users ")
		#self.gui.addUIElement('list', 'selectedUsers', self.tab, 16, 40, 7, 4, self.selected, True, True)

		# self.gui.addLabel(6, 6, " Enter a username ")
		self.gui.addLabel(y=5,x=6, input=" Enter a (u)sername ")
		self.gui.addUIElement('input', 'inputUser', self.tab, y=6, x=4, width=50)

		self.gui.addLabel(y=10, x=6, input=" (C)urrently Addded Users ")
		self.gui.addUIElement('list', 'selectedUsers', self.tab, int(changeY * 5), 50, 11, 4, self.selected, True, True)

		# Variables
		# self.gui.addLabel(y, x+14, "MM / DD / YYYY", color=4)
		self.gui.addLabel(y=y+2, x=x-2, input=" Start (d)ate: ")
		self.gui.addUIElement('list', 'startDateM', self.tab, 3, 6, y+1, x+12, months, False, False)
		self.gui.addUIElement('list', 'startDateD', self.tab, 3, 6, y+1, x+17, days, False, False)
		self.gui.addUIElement('list', 'startDateY', self.tab, 3, 6, y+1, x+22, years, False, False)
		self.gui.addLabel(index='startDateM', input='Mon', justify='center', color=4)
		self.gui.addLabel(index='startDateD', input='Day', justify='center', color=4)
		self.gui.addLabel(index='startDateY', input='Year', justify='right', color=4)

		# self.gui.addLabel(y+6,x," Start time: ","right")
		# self.gui.addLabel(y+4,x+14,"HH : MM",color=4)
		self.gui.addLabel(y=y+2, x=x+31, input='(L)ength:')
		self.gui.addUIElement('list', 'length', self.tab, 3, 8, y+1, x+41, lengths, False, False)
		self.gui.addLabel(index='length', input='Min', justify='center', color=4)

		self.gui.addLabel(y=y+5, x=x-1, input='(S)tart Time:')
		self.gui.addUIElement('list', 'startH', self.tab, 3, 6, y+4, x+12, hours, False, False)
		self.gui.addUIElement('list', 'startM', self.tab, 3, 8, y+4, x+17, mins, False, False)
		self.gui.addLabel(index='startH', input='Hr', justify='center', color=4)
		self.gui.addLabel(index='startM', input='Min', justify='center', color=4)
		# self.gui.addLabel(y+6,x+32," End time: ","right")
		# self.gui.addLabel(y+8,x+14,"HH : MM",color=4)

		self.gui.addLabel(y=y+5, x=x+29, input='End (T)ime:')
		self.gui.addUIElement('list', 'endH', self.tab, 3, 6, y+4, x+41, hours, box=False, highlighted=False)
		self.gui.addUIElement('list', 'endM', self.tab, 3, 8, y+4, x+46, mins, False, False)
		self.gui.addLabel(index='endH', input='Hr', justify='center', color=4)
		self.gui.addLabel(index='endM', input='Min', justify='center', color=4)
		#self.gui.addLabel('endH', 'test', 'center')
		# self.gui.addLabel(y+2,x+32," Length: ","right")
		# self.gui.addLabel(y,x+46,"Mins", color=4)
		# Will hold selected dates
		# self.gui.addLabel(10,102," Added Dates and Times ")
		self.gui.addLabel(y=y+9, x=x+2, input='S(e)lected Dates and Times', color=1)
		self.gui.addUIElement('timeWin', 'timeDates', self.tab, int(changeY *3), 50, y+10, x, self.dates, True, True)

		# test input
		# self.gui.windows.append(inputBox(3, 70, 40, self.tab.incTab()))
		# self.gui.mapWindows.append({'input': self.tab.maxTab})

		# Buttons
		self.gui.addUIElement('button', 'addSlot', self.tab, y=1, x=1, text='(A)dd Time Slot')
		self.gui.addUIElement('button', 'submit', self.tab, y=1, x=21, text='(Q)uery')
		self.gui.addUIElement('button', 'back', self.tab, y=1, x=33, text='(B)ack')
		self.gui.addUIElement('button', 'exit', self.tab, y=1, x=44, text='E(x)it')

	def mainLoop(self):
		while True:
			event = self.gui.screen.getch()
			if event == ord("x"):
				self._jumpToWin('exit')
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
			elif event == ord("a"):
				self._jumpToWin('addSlot')
			elif event == ord("q"):
				self._jumpToWin('submit')
			elif event == ord("b"):
				self._jumpToWin('back')
			elif event == ord("u"):
				self._jumpToWin('inputUser')
			elif event == ord("C") or event == ord("c"):
				self._jumpToWin('selectedUsers')
			elif event == ord("d"):
				self._jumpToWin('startDateM')
			elif event == ord("l"):
				self._jumpToWin('length')
			elif event == ord("s"):
				self._jumpToWin('startH')
			elif event == ord("t"):
				self._jumpToWin('endH')
			elif event == ord("e"):
				self._jumpToWin('timeDates')
				#for x in self.dates:
				#	print x
				#print str(len(self.dates))

			self.gui.redrawGUI(self.tab.tab)
	
	def _jumpToWin(self, index):
		curWin = self.gui.getTab(self.tab.tab)
		self.tab.tab = self.gui.getMap(index)
		newWin = self.gui.getTab(self.tab.tab)
		newWin.modified = True
		curWin.modified = True

	def _processUpDown(self, direction):
		# find which window we're in and modify that value
		# move the index back 1
		activeWin = self.gui.getTab(self.tab.tab)
		if activeWin.scrollable == False:
			self.gui.addNotification(self.warningY, self.warningX, "Cannot modify value",5)
		else:
			try:
				activeWin.changeSelection(direction)
			except:
				pass

	def _moveTab(self, direction):
		if direction == +1:
			# move the tabstop and redraw windows, highlighting the next window
			self.gui.clearWarning(self.warningY, self.warningX)
			curWin = self.gui.getTab(self.tab.tab)
			self.tab.nextTab()
			newWin = self.gui.getTab(self.tab.tab)
			newWin.modified = True
			curWin.modified = True
		elif direction == -1:
			# move the tabstop and redraw windows, highlighting the next window
			self.gui.clearWarning(self.warningY, self.warningX)
			curWin = self.gui.getTab(self.tab.tab)
			self.tab.prevTab()
			newWin = self.gui.getTab(self.tab.tab)
			curWin.modified = True
			newWin.modified = True

	def _goBack(self):
		# back to original screen
		self.gui.cleanGUI()
		mainGui().mainLoop()

	def processEnter(self):
		"""
		Caught and Enter key, determine what to do with it
		"""
		#if self.tab.tab == self.gui.getMap('selectUsers'):
		#	self._swapEvent('selectedUsers')
		addWins = [self.gui.getMap('startH'),
			self.gui.getMap('startM'),
			self.gui.getMap('endH'),
			self.gui.getMap('endM'),
			self.gui.getMap('startDateM'),
			self.gui.getMap('startDateD'),
			self.gui.getMap('startDateY'),
			self.gui.getMap('length')
		]
		if self.tab.tab == self.gui.getMap('selectedUsers'):
			self._removeUser()
			#self._swapEvent('selectUsers')
		elif self.tab.tab == self.gui.getMap('submit'):
			self.submitRequest()
		elif self.tab.tab == self.gui.getMap('exit'):
			self.gui.close()
			exit()
		elif self.tab.tab == self.gui.getMap('back'):
			self._goBack()
		elif self.tab.tab == self.gui.getMap('addSlot'):
			self._addDateTime()
		elif self.tab.tab == self.gui.getMap('timeDates'):
			self._removeTime()
		elif self.tab.tab == self.gui.getMap('inputUser'):
			self._getInput()
		elif self.tab.tab in addWins:
			self._addDateTime()

	def _removeUser(self):
		userWin = self.gui.getWin('selectedUsers')
		value = userWin.getSelectedValue()
		try:
			self.selected.remove(value)
		except:
			self.gui.addNotification(self.warningY, self.warningX, "No users to remove", 5)
		userWin.changeSelection(0)

	def _removeTime(self):
		"""
		"""
		#index = self.gui.getMap('timeDates')
		slotWin = self.gui.getWin('timeDates')
		value = slotWin.getSelectedValue()
		try:
			self.dates.remove(value)
		except:
			self.gui.addNotification(self.warningY, self.warningX, "No values to remove", 5)
		slotWin.changeSelection(0)

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
			#datesTab = self.gui.getMap('timeDates')
			changeWin = self.gui.getWin('timeDates')
			changeWin.changeSelection(0)
		else:
			self.gui.addNotification(self.warningY, self.warningX, "Date and time already added", 5)

	def _swapEvent(self, appendWin):
		"""
		On enter inside a field, an event occurs.
		Wrapped in a try..except to prevent values that are no longer in the list from being removed

		Parameters
		removes - the list to remove the value from
		appends - the list to append the value to
		value - the specific value that should be removed and appended
		"""
		removeWin = self.gui.getTab(self.tab.tab)
		addIndex = self.gui.getMap(appendWin)
		addWin = self.gui.getTab(addIndex)
		value = removeWin.getSelectedValue()
		try:
			removeWin.items.remove(value)
			addWin.items.append(value)
		except:
			pass
		removeWin.changeSelection(0)
		addWin.changeSelection(0)

	def _getInput(self):
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
		# updates the selected box and prepares for refresh		
		self.selected.append(text) # return text
		changeWin = self.gui.getWin('selectedUsers')
		changeWin.changeSelection(0)

		return True

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
		#self.gui.addNotification(self.warningY, self.warningX, "Finished!!", 1)

	def calcTimesSlots(self):
		"""
		Makes the call to interface and eventually the calendar API. Creates a window object that lists the times returned
		as available.
		"""
		# process the event
		#service = connection()
		#userNames = []
		finalAvails = []
		#############################################################
		#															#
		# This line will require SIGNIFICANT error checking:		#
		# -ensure the end date and time are after the start 		#
		# -odd days of the month? 30t of feb, 31 of Nov, etc        #
		# -edge cases 												#
		# -years?													#
		#															#
		#############################################################
		
		# this is how i called one, let's make it call all we want
		#start, stop, length, userNames = self.gui.getStates()
		
		finalAvails.append({'date': '04/13/2014', 'times': [x for x in range(0, (24*60), 15)], 'length': 60 })
		# KEEP THIS!!
		finalAvails.append({'date': '04/19/2014', 'times': [x for x in range(180, (20*60), 15)], 'length': 60 })
		# index = self.gui.getMap('selectedUsers')
		# for date in self.dates:
		# 	# erase old people if there
		# 	people = []
		#	users = []
		# 	# create people array
		# 	for user in self.gui.windows[index].items:
		# 		people.append(person(user, int(date['length']), service.service))
		#		users.append(user)
		# 	# meeting object
		# 	newMeeting = meeting(date['start'], date['stop'], date['length'], people)
		# 	# run the algorithms
		# 	if newMeeting.availInTimeSlot():
		# 	#{ 'date': 'MM/DD/YYYY', 'times': ['MM:HH'] }
		# 	# append dates and resulting times
		# 		finalAvails.append({'date': getDate(date['start']), 'times': newMeeting.availableTimes, 'length': date['length'] })
		# 	else:
		# 		self.gui.addNotification(self.warningY, self.warningX, "No users were found")
		# 		return

		# clean the gui, prep to load new window
		self.gui.cleanGUI()
		# make the new window, passing in the results from the query
		resultGui(finalAvails,users).mainLoop()

		#############################################################
		#															#
		# Start the integration with the interface for the calendar #
		# api and other functions.                                  #
		# Need to work on the interface to automatically add events #
		# that are pulled from database, no need to do it here.     #
		#															#
		#############################################################
		# for user in userNames:
		#  	people.append(person(user, length, service.service))

		# # create a meeting object that will hold availability information for the group
		# newMeeting = meeting(start, stop, length, people)
		# # run algorithm to find available time slots
		# newMeeting.availInTimeSlot()
		# times = []
		# # no need to access directly
		# for x in newMeeting.availableTimes:
		# 	# user friendly format
		# 	times.append(printTime(x) + " - "+ printTime(x + length))
		# # check if we have already polled results, if so, then just modify that structure
		# try:
		# 	index = self.gui.getMap('results')
		# except:
		# 	index = 0

		# if index:
		# 	resultsWin = self.gui.getTab(index)
		# 	resultsWin.changeItems(times)
		# else:
		# 	self.gui.addLabel(3,64,"Available Times")
		# 	maxSize = len(times) + 1
		# 	if len(times) > 50:
		# 		maxSize = 50

		# 	self.gui.windows.append(listWindow(maxSize + 2, 23, 6, 60, times, self.tab.incTab(), True, True))
		# 	self.gui.mapWindows.append({'results':self.tab.maxTab})

		# date = self.gui.getDate('startDate')
		# self.gui.addLabel(4,67,date, color=4)				
		return True

class resultGui:
	"""
	Draws the window with the list of results from the queries
	"""
	def __init__(self, dates, users):
		self.dates = dates
		self.users = users
		self.gui = GUI()
		self.tab = tabstop()

		self.warningY = 1
		self.warningX = 70

		self.buildWindows()
		self.tab.tab = 0

		self.gui.drawGUI(self.tab)
		self.gui.redrawGUI(self.tab.tab)

	def buildWindows(self):
		maxY, maxX = self.gui.screen.getmaxyx()
		#self.gui.addUIElement('list', 'startDateY', self.tab, 3, 6, y+1, x+22, years, False, False)
		#self.gui.windows.append(pagedWindow((maxY - 4), 25, 2, 2, self.dates, 0, box=True, highlighted=True))
		#self.gui.mapWindows.append({'results': 0})
		# TODO FIX THIS HIGHLIGHT BULLSHIT
		# This isnt highlighting....
		self.gui.addUIElement('pagedWin', 'results', self.tab, (maxY - 8), 24, 5, 55, self.dates, True, True)
		tempWin = self.gui.getWin('results')
		tempWin.label = True
		for x in self.dates:
			tempWin.selection.append(0)
		self.gui.addUIElement('list', 'users', self.tab, (maxY - 8), 50, 5, 2, self.users, True, True)

		self.gui.addUIElement('button', 'addSlot', self.tab, y=1, x=1, text='(A)dd Time Slot')
		self.gui.addUIElement('button', 'back', self.tab, y=1, x=21, text='(B)ack')
		self.gui.addUIElement('button', 'exit', self.tab, y=1, x=32, text='E(x)it')

	def mainLoop(self):
		while True:
			event = self.gui.screen.getch()
			if event == ord("x"):
				self.gui.close()
				exit()
			elif event == ord("\t"):
				self._moveTab(+1)
			elif event == event == curses.KEY_RIGHT:
				#win = self.gui.getMap('results')
				win = self.gui.getWin('results')
				win.changeFocus(+1)
			elif event == event == curses.KEY_LEFT:
				#win = self.gui.getMap('results')
				win = self.gui.getWin('results')
				win.changeFocus(-1)
			elif event == curses.KEY_DOWN:
				self._processUpDown(+1)
			elif event == curses.KEY_UP:
				self._processUpDown(-1)

			self.gui.redrawGUI(self.tab.tab)

	def _processUpDown(self, direction):
		# find which window we're in and modify that value
		# move the index back 1
		activeWin = self.gui.getTab(self.tab.tab)
		if activeWin.scrollable == False:
			self.gui.addNotification(self.warningY, self.warningX, "Cannot modify value",5)
		else:
			try:
				activeWin.changeSelection(direction)
			except:
				pass

	def _moveTab(self, direction):
		if direction == +1:
			# move the tabstop and redraw windows, highlighting the next window
			self.gui.clearWarning(self.warningY, self.warningX)
			curWin = self.gui.getTab(self.tab.tab)
			self.tab.nextTab()
			newWin = self.gui.getTab(self.tab.tab)
			newWin.modified = True
			curWin.modified = True
		elif direction == -1:
			# move the tabstop and redraw windows, highlighting the next window
			self.gui.clearWarning(self.warningY, self.warningX)
			curWin = self.gui.getTab(self.tab.tab)
			self.tab.prevTab()
			newWin = self.gui.getTab(self.tab.tab)
			curWin.modified = True
			newWin.modified = True


class mainGui:
	"""
	Main landing page for user to choose what to do
	"""
	def __init__(self):
		self.gui = GUI()
		self.tab = tabstop()

		self.warningY = 54
		self.warningX = 6

		self.buildWindows()
		self.tab.tab = 0

		self.gui.drawGUI(self.tab)
		self.gui.redrawGUI(self.tab.tab)
	
	def buildWindows(self):
		#(self, screen, y, x, text, tab, box=True, highlighted=True):
		# self.gui.addLabel(1, 2, "Scheduling Tool", color=4)

		self.gui.addUIElement('button', 'meeting', self.tab, y=6, x=8, text='Schedule a Meeting')
		self.gui.addUIElement('button', 'timeFrame', self.tab, y=11, x=8, text='Search by Time Frame')
		self.gui.addUIElement('button', 'users', self.tab, y=16, x=8, text='Search by Users')

	def mainLoop(self):
		while True:
			event = self.gui.screen.getch()
			if event == ord('x'):
				self.gui.close()
				exit()
			elif event == curses.KEY_DOWN or event == ord('\t'):
				self._processUpDown(+1)
			elif event == curses.KEY_UP:
				self._processUpDown(-1)
			elif event == ord('\n'):
				if self.processEnter() == 2:
					timeFrame().mainLoop()

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
		if self.tab.tab == self.gui.getMap('timeFrame'):
			self.gui.cleanGUI()
			return 2
		# elif self.tab.tab == self.gui.getMap('users'):
		# 	self.gui.cleanGUI()
		# 	return 3

	def __del__(self):
		pass

if __name__ == "__main__":
	# Test structures
	months = [str(x).zfill(2) for x in range(1, 13)]
	days = [str(x).zfill(2) for x in range(1, 32)]
	years = [str(x) for x in range(2014,2021)]
	hours = [str(x).zfill(2) for x in range(0,24)]
	mins = [str(x).zfill(2) for x in range(0,45,15)]
	lengths = [str(x) for x in range(15,375,15)]
	selected = []
	users = ['burrows.danny@gmail.com', 'jonesjo@onid.oregonstate.edu', 'clampitl@onid.oregonstate.edu', 'jjames83@gmail.com']
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
