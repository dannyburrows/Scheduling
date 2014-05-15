from calendarAPI import person
from calendarAPI import connection
from datetime import *
from timemanip import *

#import time

class meeting:
	"""
		meeting

		A class that will find a common available time between users

		_findAllAvailabilities()
		--iterates through users list and sets their availabilities in their own class
		--then iterates through each user's availabilities and creates a list of open times

		listAvailTime()
		--run after _findAllAvailabilities()
		--prints to the screen a list of available times, based on every users availability
	"""
	def __init__(self, start, stop, length, users):
		self.start = start
		self.stop = stop
		self.length = length
		self.users = users
		self.availableTimes = []
		self.availUsers = []
		self._findAllAvailabilities()

	def _findAllAvailabilities(self):
		# find availabilities for each user
		for x in self.users:
			if not x.findAvailability(self.start, self.stop):
				print "Error occurred in finding availability. Ensure meeting length >= 15."

		# add the availability for first user
		for i in self.users[0].availabilities['times']:
			self.availableTimes.append(i)

		# trim times that are not listed in each individual persons availability
		# list comprehension
		for i in range(1, len(self.users)):
			self.availableTimes = [elem for elem in self.availableTimes if elem in self.users[i].availabilities['times']]
	
	def listAvailTimes(self, milTime):
		# this can be modified to something different, for whatever interface we end up using
		for x in self.availableTimes:
			print printTime(x, milTime)

	def availInTimeSlot(self):
		"""
			Takes a start and stop time and returns an array of user names that are available during the time frame
		"""
		possTimes = []
		availableUsers = []
		timeFrame = 15
		startYear, startDate, start = getCorrectedTime(self.start)
		endYear, endDate, end = getCorrectedTime(self.stop)

		for i in range(start, end, timeFrame):
			possTimes.append(i)

		# loop through all possible times in slot, if user is available entire time, add to available users
		# else exclude from available users
		for i in possTimes:
			for j in self.users:
				addUser = True
				if i not in j.availabilities['times']:
					addUser = False
				if addUser:
					availableUsers.append(j.getUserName())
		# set removes duplicates, easy way to remove duplicates
		if availableUsers:
			self.availUsers = set(availableUsers)
			return True
		return False

	def printAvailUsers(self):
		"""
			Lists the users that are in availUsers.

			availUsers is appeneded in availInTimeSlot, which returns a list of people that are available
			for the full time slot passed to the function
		"""
		for user in self.availUsers:
			print user

class window:
	def __init__(self, user, startTime = None, endTime = None):
		self.user = user
		self.startTime = startTime
		self.endTime = endTime
		self.beginTime = None
		self.stopTime = None
		self.startDate = None
		self.endDate = None
		self.availableDates = []

		# ensure that is startTime or endTime is set, other is set as well
		if startTime:
			assert endTime
		elif endTime:
			assert startTime
		self._constructTimes()


	def printWindow(self, milTime):
		for i in self.availableDates:
			print "------" + i['date'] + "------"
			for availTime in i['times']:
				print "      ",
				print printTime(availTime, milTime)

	def _constructTimes(self):
		# startTime/endTime are parameters coming in
		#
		# start/end are formatted from startTime/endTime or from todays date
		# -returns the current day of the year in integer format
		#
		# beginTime/stopTime are appended to start/end to make the expected datetime format for the calendarapi
		# -creates 'MM/DD/YY HH:MM' format

		today = datetime.now() 	# get today's date
		loopDay = today # used in the while loop
		
		# if a window is selected, parse time and set time
		##### THIS ONE WORKS CORRECTLY #####
		if self.startTime and self.endTime:
			startYear, self.startDate, start = getCorrectedTime(self.startTime) # ints for loops and manipulation
			endYear, self.endDate, end = getCorrectedTime(self.endTime) # ints for loops and manipulation
			loopDay = convertToDatetime(self.startTime) #datetime.strptime(self.startTime[0:10], '%m/%d/%Y') # gets the initial day of the year to start our loop
			self.beginTime = getTime(self.startTime) # beginning time
			self.stopTime = getTime(self.endTime) # ending time
		else: ##### TODO FIX THIS #####
			endDay = today + timedelta(days=7) # sets ending loop day, where start is today's date
			# start = getStringDate(today) # date conversion for start date
			# end = getStringDate(endDay) # date conversion for end date
			self.startDate = getDayOfYear(today) # day of the year
			self.endDate = getDayOfYear(endDay) # day of the year
			self.beginTime = "08:00" # school hours
			self.stopTime = "18:00"	# school hours
			start = 480
			end = 1080

		assert self.startDate <= self.endDate

		self._findAvail(start, end, loopDay)
		return True
	
	def _findAvail(self, start, end, loopDay):
		i = self.startDate
		while i <= self.endDate:
			stringDay = getStringDate(loopDay) # convert the looped day to day and year
			start = stringDay + " " + str(self.beginTime) # get ready for findavailability call
			end = stringDay + " " + str(self.stopTime)	 # get ready for findavailability call

			self.user.findAvailability(start,end) # list of availabilities
			availTimes = self.user.availabilities # copy of availabilities
			self.user.clearAvail()				 # clear availabilities for next day

			self.availableDates.append(availTimes) # add current availabilities to array
			loopDay = loopDay + timedelta(days=1) # increment 1 day
			i = i + 1
		return True

def main():
	# the connection class is the class that actually connects to the api
	# if the user has not given this application the permissions, a browser
	# will open and ask for the permissions
	# Always get a connection object and ensure to pass that to each instance
	# of a user to ensure connections
	service = connection()
	# this is the expected format of the testing times, for this particular implementation
	start = "04/15/2014 10:00"
	stop = "04/20/2014 18:00"
	# length will be 15 or greater
	length = 60
	userWindow = False
	shortWindow = False
	broadWindow = False

	# the meeting class will expect a list of users.
	# the user names are the name of the calendar owner, found in calendar settings on calendar.google.com
	# each user can have his/her individual time frames printed via <user>.listAvailabilities(<militaryTime>)
	users = []
	users.append(person("jonesjo@onid.oregonstate.edu", length, service.service))
	users.append(person("burrows.danny@gmail.com", length, service.service))

	classDays = "135" # M W F
	classStart = "10:00:00" # 10 AM
	classEnd = "11:30:00" # 1130 AM
	# addClassTimeBlock(self, classDays, classStart, classEnd, startDay, endDay)
	# start = datetime.now()
	# end = start + timedelta(days=7)
	# start = getStringDate(start), end = getStringDate(end)
	users[0].addClassTimeBlock(classDays, classStart, classEnd, start, stop)

	users.append(person("clampitl@onid.oregonstate.edu", length, service.service))
	users.append(person("jjames83@gmail.com", length, service.service))
	
	if userWindow:
		#1 	Given a single username in the local domain, provide a list of open times within the window specified
		#	If no window is specified, use a sane default (7 days, 8AM-6PM)
		#
		# Note that the start takes in both the start date and start time
		# Stop takes in both the stop date and stop time
		userWindow = window(users[0])#,start,stop) # INDIVIDUAL USER
		userWindow.printWindow(False)
	elif shortWindow:
		#2 	Given a specific time window and a list of usernames, list all users available for the entire duration.
		#	This is more in the nature of "who can i expect at the meeting"
		#
		# Takes in a list of users, the start and stop time of the potential meeting and the expected length of the meeting
		# The object sets internal variables and calls functions to process and display
		# The length of the meeting here is ONLY the difference between the start and stop time
		newMeeting = meeting(start, stop, length, users)
		newMeeting.availInTimeSlot()
		newMeeting.printAvailUsers()
	elif broadWindow:
		#3 	Given a more broad window and a list of usernames, provide all time periods where all are available.
		#	This is more in the nature of "when can I schedule the meeting?"
		#
		# This meeting object is the same structure as #2 but calls a different process to create the list
		newMeeting = meeting(start, stop, length, users)
		newMeeting.listAvailTimes(False)
	else:
		# this is test the database implementation when it is up
		# manual checking for now
		classDays = "135" # M W F
		classStart = "10:00:00" # 10 AM
		classEnd = "11:30:00" # 1130 AM
		# addClassTimeBlock(self, classDays, classStart, classEnd, startDay, endDay)
		
		# start and stop here are specified before determining whether we want a sane default or just a restricted time
		users[1].addClassTimeBlock(classDays, classStart, classEnd, start, stop)

		newWindow = window(users[1])#,start,stop)
		newWindow.printWindow(False)

if __name__ == "__main__":
	main()