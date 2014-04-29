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
		self.users = ['burrows.danny@gmail.com', 'jonesjo@onid.oregonstate.edu', 'clampitl@onid.oregonstate.edu', 'jjames83@gmail.com']
		#self.users = [x for x in range(0, 40)]
		# will hold the dates to check for multiple dates and times
		# array of tuples, taking the type: { 'date': 'MM/DD/YYYY', 'times': ['MM:HH'] }
		self.dates = []
		self.warningY = 28
		self.warningX = 50
		self.buildWindows()
		self.tab.tab = 0
		self.gui.drawGUI()
		self.gui.redrawGUI(self.tab.tab)

	def buildWindows(self):
		y = 8
		x = 50
		# add all the windows that will contain lists of information
		 
		# Listing windows
		self.gui.addLabel(5,6," Select Users ")
		self.gui.windows.append(listWindow(self.gui.screen, 16, 40, 7, 4, self.users, self.tab.maxTab, True, True))
		self.gui.mapWindows.append({'selectUsers':self.tab.maxTab})

		self.gui.addLabel(24,6," Currently Selected ")
		self.gui.windows.append(listWindow(self.gui.screen, 16, 40, 26, 4, self.selected, self.tab.incTab(), True, True))
		self.gui.mapWindows.append({'selectedUsers':self.tab.maxTab})

		# Will hold selected dates
		self.gui.addLabel(43,6," Added Dates and Times ")
		self.gui.windows.append(timeWindow(self.gui.screen, 10, 50, 45, 4, self.dates, self.tab.incTab(), True, True))
		self.gui.mapWindows.append({'timeDates':self.tab.maxTab})

		# Variables
		self.gui.addLabel(y, x+14, "MM / DD / YYYY", color=4)
		self.gui.addLabel(y+2, x,"Start date:","right")
		self.gui.windows.append(listWindow(self.gui.screen, 3, 6, y+1, x+12, months, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startDateM':self.tab.maxTab})

		self.gui.windows.append(listWindow(self.gui.screen, 3, 6, y+1, x+17, days, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startDateD':self.tab.maxTab})

		self.gui.windows.append(listWindow(self.gui.screen, 3, 8, y+1, x+22, years, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startDateY':self.tab.maxTab})

		self.gui.addLabel(y+4,x+14,"MM : HH",color=4)
		self.gui.addLabel(y+6,x,"Start time:","right")
		self.gui.windows.append(listWindow(self.gui.screen, 3, 6, y+5, x+12, hours, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startH':self.tab.maxTab})

		self.gui.windows.append(listWindow(self.gui.screen, 3, 8, y+5, x+16, mins, self.tab.incTab(), False))
		self.gui.mapWindows.append({'startM':self.tab.maxTab})

		self.gui.addLabel(y+8,x+14,"MM : HH",color=4)
		self.gui.addLabel(y+10,x,"End time:","right")
		self.gui.windows.append(listWindow(self.gui.screen, 3, 6, y+9, x+12, hours, self.tab.incTab(), False))
		self.gui.mapWindows.append({'endH':self.tab.maxTab})

		self.gui.windows.append(listWindow(self.gui.screen, 3, 8, y+9, x+16, mins,self.tab.incTab(), False))
		self.gui.mapWindows.append({'endM':self.tab.maxTab})

		self.gui.addLabel(y+12,x+14,"Mins", color=4)
		self.gui.addLabel(y+14,x,"Length:","right")
		self.gui.windows.append(listWindow(self.gui.screen, 3, 8, y+13, x+12, lengths, self.tab.incTab(), False))
		self.gui.mapWindows.append({'length':self.tab.maxTab})

		# test input
		# self.gui.windows.append(inputBox(self.gui.screen, 3, 70, 40, self.tab.incTab()))
		# self.gui.mapWindows.append({'input': self.tab.maxTab})

		# Buttons
		self.gui.windows.append(button(self.gui.screen,1,1,"(A)dd Time Slot",self.tab.incTab()))
		self.gui.mapWindows.append({'addSlot':self.tab.maxTab})

		self.gui.windows.append(button(self.gui.screen,1,21,"(Q)uery",self.tab.incTab()))
		self.gui.mapWindows.append({'submit':self.tab.maxTab})

		self.gui.windows.append(button(self.gui.screen,1,33,"(B)ack",self.tab.incTab()))
		self.gui.mapWindows.append({'back':self.tab.maxTab})

		self.gui.windows.append(button(self.gui.screen,1,44,"E(x)it",self.tab.incTab()))
		self.gui.mapWindows.append({'exit':self.tab.maxTab})

	def mainLoop(self):
		while True:
			# if self.tab.tab == self.gui.getMap('input'):			
			# 	index = self.gui.getMap('input')
			# 	win = self.gui.getWin(index)
			# 	#print win
			# 	y,x,length = win.inputParams()
			# 	curses.echo()
			# 	text = self.gui.screen.getstr(y,x, length)
			# 	#print text
			# 	self._moveTab(+1)
			# 	curses.noecho()
			# else:
			event = self.gui.screen.getch()
			if event == ord("x"):
				self.gui.close()
				exit()
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
				self._addDateTime()
			elif event == ord("q"):
				self.submitRequest()
			elif event == ord("b"):
				self._goBack()
				#for x in self.dates:
				#	print x
				#print str(len(self.dates))

			self.gui.redrawGUI(self.tab.tab)

	def _processUpDown(self, direction):
		# find which window we're in and modify that value
		# move the index back 1
		activeWin = self.gui.getWin(self.tab.tab)
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

	def _goBack(self):
		# back to original screen
		self.gui.cleanGUI()
		mainGui().mainLoop()

	def processEnter(self):
		"""
		Caught and Enter key, determine what to do with it
		"""
		if self.tab.tab == self.gui.getMap('selectUsers'):
			self._swapEvent('selectedUsers')
		elif self.tab.tab == self.gui.getMap('selectedUsers'):
			self._swapEvent('selectUsers')
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

	def _removeTime(self):
		"""
		"""
		index = self.gui.getMap('timeDates')
		slotWin = self.gui.getWin(index)
		value = slotWin.getSelectedValue()
		self.dates.remove(value)
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
		if startMins > endMins:
			self.gui.addNotification(self.warningY, self.warningX, "Check your start and end times", 5)
			return
		if temp not in self.dates:
			self.dates.append(temp)
			datesTab = self.gui.getMap('timeDates')
			changeWin = self.gui.getWin(datesTab)
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
		curWin = self.gui.getWin(self.tab.tab)
		curWin.modified = True
		
		if self.calcTimesSlots():
			self.tab.tab = self.tab.maxTab
			pass
		else:
			curWin.modified = False
		self.gui.addNotification(self.warningY, self.warningX, "Finished!!", 1)

	def calcTimesSlots(self):
		"""
		Makes the call to interface and eventually the calendar API. Creates a window object that lists the times returned
		as available.
		"""
		# process the event
		service = connection()
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
		
		index = self.gui.getMap('selectedUsers')
		for date in self.dates:
			# erase old people if there
			people = []
			# create people array
			for user in self.gui.windows[index].items:
				people.append(person(user, int(date['length']), service.service))
			# meeting object
			newMeeting = meeting(date['start'], date['stop'], date['length'], people)
			# run the algorithms
			newMeeting.availInTimeSlot()
			#{ 'date': 'MM/DD/YYYY', 'times': ['MM:HH'] }
			# append dates and resulting times
			finalAvails.append({'date': getDate(date['start']), 'times': newMeeting.availableTimes })

		# clean the gui, prep to load new window
		self.gui.cleanGUI()
		# make the new window, passing in the results from the query
		resultGui(finalAvails).mainLoop()

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
		# 	resultsWin = self.gui.getWin(index)
		# 	resultsWin.changeItems(times)
		# else:
		# 	self.gui.addLabel(3,64,"Available Times")
		# 	maxSize = len(times) + 1
		# 	if len(times) > 50:
		# 		maxSize = 50

		# 	self.gui.windows.append(listWindow(self.gui.screen, maxSize + 2, 23, 6, 60, times, self.tab.incTab(), True, True))
		# 	self.gui.mapWindows.append({'results':self.tab.maxTab})

		# date = self.gui.getDate('startDate')
		# self.gui.addLabel(4,67,date, color=4)				
		return True

class resultGui:
	"""
	Draws the window with the list of results from the queries
	"""
	def __init__(self, dates):
		self.dates = dates
		self.gui = GUI()
		self.tab = tabstop()

		self.warningY = 10
		self.warningX = 10

		self.buildWindows()
		self.tab.tab = 0

		self.gui.drawGUI()
		self.gui.redrawGUI(self.tab.tab)

	def buildWindows(self):
		self.gui.windows.append(dateWindow(self.gui.screen,50,25,2,2,self.dates,0))
		self.gui.mapWindows.append({'results': 0})

	def mainLoop(self):
		while True:
			event = self.gui.screen.getch()
			if event == ord("x"):
				self.gui.close()
				exit()
			elif event == ord("\t") or event == curses.KEY_RIGHT:
				win = self.gui.getMap('results')
				win = self.gui.getWin(win)
				win.changeFocus(+1)

			self.gui.redrawGUI(self.tab.tab)


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

		self.gui.drawGUI()
		self.gui.redrawGUI(self.tab.tab)
	
	def buildWindows(self):
		#(self, screen, y, x, text, tab, box=True, highlighted=True):
		self.gui.addLabel(1, 2, "Scheduling Tool", color=4)
		self.gui.windows.append(button(self.gui.screen, 6, 8,"Schedule a Meeting", self.tab.maxTab))
		self.gui.mapWindows.append({'meeting':self.tab.maxTab})

		self.gui.windows.append(button(self.gui.screen, 11, 8,"Search by Time Frame", self.tab.incTab()))
		self.gui.mapWindows.append({'timeFrame':self.tab.maxTab})

		self.gui.windows.append(button(self.gui.screen, 16, 8,"Search by Users", self.tab.incTab()))
		self.gui.mapWindows.append({'users':self.tab.maxTab})

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
			curWin = self.gui.getWin(self.tab.tab)
			self.tab.nextTab()
			newWin = self.gui.getWin(self.tab.tab)
			newWin.modified = True
			curWin.modified = True
		else:
			curWin = self.gui.getWin(self.tab.tab)
			self.tab.prevTab()
			newWin = self.gui.getWin(self.tab.tab)
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
	mins = [str(x).zfill(2) for x in range(0,75,15)]
	lengths = [str(x) for x in range(15,375,15)]
	selected = []
	users = ['burrows.danny@gmail.com', 'jonesjo@onid.oregonstate.edu', 'clampitl@onid.oregonstate.edu', 'jjames83@gmail.com']
	#users = [ x for x in range(0,50)]

	# testDates = []
	# testDates.append({ 'date': '04/26/2014', 'times':['12:00','12:30','1:00','1:30']})
	# testDates.append({ 'date': '04/27/2014', 'times':['1:00','2:30','4:00','5:30']})

	mainGui().mainLoop()
