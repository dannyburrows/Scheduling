from calendarAPI import person
from calendarAPI import connection

def printTime(input, militaryTime):
	midDay = ""
	hours = input / 60
	if not militaryTime:
		midDay = "AM"
		if hours >= 12:
			if hours >= 13:
				hours = hours - 12
			midDay = "PM"
	mins = input % 60
	time = "%02d:%02d " % (hours, mins) + midDay
	print time

# the connection class is the class that actually connects to the api
# if the user has not given this application the permissions, a browser
# will open and ask for the permissions
# Always get a connection object and ensure to pass that to each instance
# of a user to ensure connections
service = connection()
start = "04/17/2014 08:00"
stop = "04/17/2014 18:00"
length = 30

users = []

users.append(person("jonesjo@onid.oregonstate.edu", length, service.service))
users[-1].findAvailbility(start, stop)

users.append(person("burrows.danny@gmail.com", length, service.service))
users[-1].findAvailbility(start, stop) 

users.append(person("clampitl@onid.oregonstate.edu", length, service.service))
users[-1].findAvailbility(start, stop)

# find the times everyone on list is available
# start with one user, check their availability
# push into array
# next person, if that person is not available remove time
# repeat

# start with user 1, fill availability based on the first user passed
availableTimes = []
for x in users[0].availabilities['times']:
	availableTimes.append(x)

# list comprehension to trim user times
# http://stackoverflow.com/questions/18194968/python-remove-duplicates-from-2-lists
for i in range(1,len(users)):
	availableTimes = [elem for elem in availableTimes if elem in users[i].availabilities['times']]
	#availableTimes = sorted(list(set(availableTimes)), key=int)

#print availableTimes

for x in availableTimes:
	printTime(x, False)