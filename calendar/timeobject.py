from datetime import *
import time

def getCorrectedTime(input):
    """
    	Takes a string in the format "04/10/2014 08:00" and sets the year date and mins of current object
    """
    temp = datetime.strptime(input[0:10], '%m/%d/%Y')
    year = int(temp.strftime("%y"))
    date = int(temp.strftime("%j"))
    mins = int(input[11:13]) * 60 + int(input[14:16])
    return year, date, mins

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

def getTime(input):
	"""
		Accepts a full string datetime and returns just the time
	"""
	return input[11:]

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

def getDate(input):
	"""
		Accepts a full string, returns date
	"""
	return input[0:10]

def convertToDatetime(input):
	"""
		Accepts a formatted datetime string and returns a datetime format
	"""
	return datetime.strptime(input[0:10],"%m/%d/%Y")


def printTime(input, milTime):
	# moved outside of meeting as we need for single user availability
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
	print time