from datetime import *
import time

#################################################
#	     Datetime manipulation functions		#
#################################################

def getStringDate(input):
	"""
		Accepts a datetime object and returns a string with just the month day and year in MM/DD/YYYY format
	"""
	return input.strftime("%m/%d/%Y")

def getDayOfYear(input):
	"""
		Accepts a datetime object and returns an integer with the day of the year, useful in looping
	"""
	return int(input.strftime("%j"))
def getYear(input):
	"""
		Accepts a datetime object and returns an integer with the year
	"""
	return int(input.strftime("%y"))

def getHour(input):
	"""
		Accepts a datetime object, returns the hours
	"""
	return int(str(input)[11:13])

def getMins(input):
	"""
		Accepts a datetime object, returns the minutes
	"""
	return int(str(input)[14:16])

def getDayOfWeek(input):
	"""
		Accepts a datetime object, returns the day of the week

		For checking purposes, leaving as a string, typecast result
		if an int is needed
	"""
	return input.strftime("%w")

#################################################
#	       String manipulation functions		#
#################################################

def getTime(input):
	"""
		Accepts a full string datetime and returns just the time
	"""
	return input[11:]


def getDate(input):
	"""
		Accepts a full string, returns date
	"""
	return input[0:10]

def convertToDatetime(input):
	"""
		Accepts a formatted string and returns a datetime format
	"""
	return datetime.strptime(input[0:10],"%m/%d/%Y")

def convertToDatetimeFull(input):
	"""
		Accepts a formatted string, returns datetime with hours, mins and secs
	"""
	# corrects an odd case where Google is returning time without seconds. Happens rarely but still was throwing an occasional error
	if len(input) == 16:
		input = input + ":00"
	return datetime.strptime(input, "%Y-%m-%d %H:%M:%S")

def getCorrectedTime(input):
    """
    	Takes a string in the format "04/10/2014 08:00" and sets the year date and mins of current object
    """
    temp = datetime.strptime(input[0:10], '%m/%d/%Y')
    year = int(temp.strftime("%y"))
    date = int(temp.strftime("%j"))
    mins = int(input[11:13]) * 60 + int(input[14:16])
    return year, date, mins

def simpleParse(input):
	"""
		Takes a google date time and parses to the proper format. Previously used dateutil.parser, no longer needed
	"""
	if input[11:] == "":
		ending = "00:00:00"
	else:
		ending = input[11:]
	return input[0:10] + " " + ending

def convertTimeToString(input):
	hours = int(input) / 60
	mins = int(input) % 60
	return str(hours).zfill(2) + ":" + str(mins).zfill(2)

#################################################
#	       Displaying and calculations			#
#################################################

def printTime(input, milTime = False):
	# moved outside of meeting as we need for single user availability
	midDay = ""
	hours = int(input) / 60
	if not milTime:
		midDay = "AM"
		if hours == 00:
			hours = 12
		elif hours >= 12:
			if hours >= 13:
				hours = hours - 12
			midDay = "PM"
	mins = int(input) % 60
	time = "%02d:%02d " % (hours, mins) + midDay
	return time

def getTotalMinutes(hours, mins):
	return int(hours) * 60 + int(mins)

def fixDate(input):
	input = input.split('/')
	month = input[0].zfill(2)
	day = input[1].zfill(2)
	year = str(int(input[2]) + 2000)
	return month + '/' + day + '/' + year

def fixTime(input):
	input = input.zfill(4)
	return input[0:2] + ':' + input[2:4]

def setDateTime(date, hour):
	return date + ' ' + hour

def parseDays(input):
	days = {'S': 0,
			'M': 1,
			'T': 2,
			'W': 3,
			'R': 4,
			'F': 5,
			'A': 6}
	temp = ''
	for day in input:
		temp = temp + str(days[day])

	return temp