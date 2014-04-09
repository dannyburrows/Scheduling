from calendarAPI import person

users = []

users.append(person("burrows.danny@gmail.com", ""))
users[-1].findAvailbility("04/10/2014 08:30", "04/10/2014 15:00")
users[-1].listAvailabilities()  

users.append(person("jonesjo@onid.oregonstate.edu", ""))
users[-1].findAvailbility("04/10/2014 08:30", "04/10/2014 15:00")
#users[-1].listAvailabilities()  

users.append(person("jjames83@gmail.com", ""))
users[-1].findAvailbility("04/10/2014 08:30", "04/10/2014 15:00")
#users[-1].listAvailabilities()

# find the times everyone on list is available
# start with one user, check their availability
# push into array
# next person, if that person is not available remove time
# repeat

# start with user 1, fill availability based on the first user passed
availableTimes = []
for x in users[0].availabilities['times']:
	#if x == 'All':
	#	for i in range (510,915,15):
	availableTimes.append(x)

print availableTimes

# list comprehension to trim user times
# http://stackoverflow.com/questions/18194968/python-remove-duplicates-from-2-lists
for i in range(1,len(users) - 1):
	availableTimes = [elem for elem in availableTimes if elem in users[i].availabilities['times']]

#for x in availableTimes[:]:
#	for i in removeList:
#		availableTimes.remove(i)

print availableTimes
#print removeList