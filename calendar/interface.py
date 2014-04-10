from calendarAPI import person
from calendarAPI import connection

class meeting:
	"""
		meeting

		A class that will find a common available time between users

		_findAllAvailabilities()
		--iterates through users list and sets their availabilities in their own class
		--then iterates through each user's availabilities and creates a list of open times

		_printTime(milTime)
		--helper function for listAvailabilities
		--prints the time in either military time or not

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
		for i in range(1, len(self.users)):
			self.availableTimes = [elem for elem in self.availableTimes if elem in self.users[i].availabilities['times']]
	
	def _printTime(self, input, milTime):
		midDay = ""
		hours = input / 60
		if not milTime:
			midDay = "AM"
			if hours >= 12:
				if hours >= 13:
					hours = hours - 12
				midDay = "PM"
		mins = input % 60
		time = "%02d:%02d " % (hours, mins) + midDay
		return time

	def listAvailTimes(self, milTime):
		# this can be modified to something different, for whatever interface we end up using
		for x in self.availableTimes:
			print self._printTime(x, milTime)

def main(argv = ""):
	# the connection class is the class that actually connects to the api
	# if the user has not given this application the permissions, a browser
	# will open and ask for the permissions
	# Always get a connection object and ensure to pass that to each instance
	# of a user to ensure connections
	service = connection()
	# this is the expected format of the testing times, for this particular implementation
	start = "04/15/2014 08:00"
	stop = "04/15/2014 20:00"
	# length will be 15 or greater
	length = 60

	# the meeting class will expect a list of users.
	# the user names are the name of the calendar owner, found in calendar settings on calendar.google.com
	# each user can have his/her individual time frames printed via <user>.listAvailabilities(<militaryTime>)
	users = []
	users.append(person("jonesjo@onid.oregonstate.edu", length, service.service))
	users.append(person("burrows.danny@gmail.com", length, service.service))
	users.append(person("clampitl@onid.oregonstate.edu", length, service.service))

	# meeting class expects a start and stop time, a length of the meeting and a list of users
	testMeeting = meeting(start, stop, length, users)
	testMeeting.listAvailTimes(False)

if __name__ == "__main__":
	main()