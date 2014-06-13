#####################################################################
# Authors: Group 2 - Danny Burrows, Jonathan Jones, Laura Clampitt  #
# Oregon State University                                           #
# CS419 - Spring 2014                                               #
#                                                                   #
# Integrates the Google Calendar API with python. Takes a username  #
# that has a public calendar and a start and stop time, then        #
# returns a list of availabilities for that user based on their     #
# calendar                                                          #
#####################################################################

import argparse
import httplib2
import os
import ConfigParser
import MySQLdb

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from datetime import *

class unavailTime:
  def __init__(self, start = None, end = None):
    self.start = start  # will be a string representation of start time
    self.end = end      # will be a string representation of end time
    self.length = -1    # length of the time block
    self._updateLength()

  def check(self):
    """
    Ensures everything added properly
    """
    try:
      assert self.start
      assert self.end
      assert self.length
      return True
    except:
      return False

  def getMinuteOfDay(self, flag):
    """
    Converts time to minutes from string.

    flag - determines whether start or end time is requested
    """
    if not flag:
      mins = getMins(self.start)
      hours = getHour(self.start)
    else:
      mins = getMins(self.end)
      hours = getHour(self.end)

    return 60 * hours + mins

  def getNumericalDate(self, flag):
    """
    Gets the day of the year in (based on 365/6 days)

    flag - determines whether start or end time is requested
    """
    if not flag:
      numDate = getDayOfYear(self.start)
      numYear = getYear(self.start)
    else:
      numDate = getDayOfYear(self.end)
      numYear = getYear(self.end)

    return numDate,numYear

  def setEnd(self, end, google = True):
    """
    Sets the end time of the block. There is a bit of brute force here due to the unicode calendar object being returned from Google.

    end - string or unicode datetime structure
    google - if google source, time object is unicode and is handled differently
    """
    if google:
      temp = simpleParse(end) # turn unicode to string
      temp = temp[:19] # trim the time zone out
      self.end = convertToDatetimeFull(temp) # convert to a datetime object for further manipulation later
    else:
      self.end = end
    self._updateLength()
    return True

  def setStart(self, start, google = True):
    """
    Sets the starting time block.

    start - string or unicode datetime structure
    google - if google source, time object is unicode and is handled differently
    """
    if google:
      temp = simpleParse(start)
      temp = temp[:19]
      self.start = convertToDatetimeFull(temp)
    else:
      self.start = start
    self._updateLength()
    return True

  def _updateLength(self):
    """
    Sets the length if there is both a start and end time
    """
    if self.end and self.start:
      # a VERY rough calculated of length
      hourS = getHour(self.start)
      hourE = getHour(self.end)
      minsS = getMins(self.start)
      minsE = getMins(self.end)
      self.length = 60 * (hourE - hourS) + (minsE - minsS)
      return True
    return False

  def printBlock(self):
    """
    Displays both the start and end time blocks.
    Used in debugging.
    """
    print self.start, self.end

class person:
  """
    person

    The heart of the scheduling program. Contains information on blocked times, available times, the users name and the meeting length.
    On instantiation, checks whether the blocked source is from the google calendar or from the database. If it's the database, a separate
    function must be called. If there is a google source, a service object is required for connection to the api.
  """
  def __init__(self, userName, length, service = None, google = True):
    assert userName
    self.service = service        # google flow service object 
    self.meetingLength = length   # length of the meeting
    self.userName = userName      # users specific ONID, used for Google Calendar and MySQL database
    self.errorFlag = False        # tells interface built on top of this that an error occured
    self.errorMsg = ""            # used to communicated what the error was
    self.blockedTimes = []        # list of blockted times, these will be unavailTime objects
    self.availabilities = {'date':None,'times':[]} # dictionary of dates and available times
    self._process(google)
  
  def _process(self, google):
    """
    Runs algorithms and connections to get the times the user is not available
    """
    if google:
      assert self.service != None
      if not self._generateBlocks(self.service):
        self.errorFlag = True
        self.errorMsg = self.userName + ' calendar unavailable'

  # Add new blocked out time
  def _addBlockedTime(self, start, end, google = True):
    """
      Adds a blocked time to the users blocked time
      -helper function for addClassTimeBlock and _generateBlocks

      start - takes a properly formatted string and sets unavailTime.start
      end - takes a properly formatted string and sets unavailTime.end
    """
    newBlock = unavailTime()
    newBlock.setStart(start, google)
    newBlock.setEnd(end, google)
    if newBlock.check():
      self.blockedTimes.append(newBlock)
      return True
    return False

  def addClassTimeBlock(self, classDays, classStart, classEnd, startDay, endDay):
    """
    Adds a blocked time for a class depending on the time frame being tested
    and the days the class is in session.

    classDays - a compressed string (eg "135") of the numerical days of the week
    -this is expected from the database
    classStart - time of day that the class starts; format HH:MM:SS
    classEnd - time of day that the class ends; format HH:MM:SS
    startDay - beginning date to look; format MM/DD/YYYY
    endDay - ending date to check; format MM/DD/YYYY
    """
    # convert to datetime and pull day of year back out for the starting day
    sDay = convertToDatetime(startDay)
    sDayOfYear = getDayOfYear(sDay)
    # find the day of the year for the ending day to check
    eDay = convertToDatetime(endDay)
    eDayOfYear = getDayOfYear(eDay)
    # there exists a fringe case where the end time is not divisible by 15 evenly that was causing an issue, this corrects that

    tempEnd = getTotalMinutes(classEnd[:2], classEnd[3:])
    while tempEnd % 15 != 0:
      tempEnd = tempEnd + 5
    
    classEnd = convertTimeToString(tempEnd)
    # loopDay is the modified day of the year that is used to check against the days of the week
    loopDay = sDay
    for x in range(sDayOfYear, eDayOfYear + 1):
      # check to see if the loopDay's day of the week is one of the class days
      checkDay = getDayOfWeek(loopDay)
      if checkDay in classDays: 
        # create formatted start day
        addStart = loopDay.strftime("%Y-%m-%d") + " " + classStart
        addStart = convertToDatetimeFull(addStart)
        # create formatted end day
        addEnd = loopDay.strftime("%Y-%m-%d") + " " + classEnd
        addEnd = convertToDatetimeFull(addEnd)
        # add the block to the blocked times, specify that this is not a google source
        self._addBlockedTime(addStart,addEnd, False)
      # increment the day of the year by 1
      loopDay = loopDay + timedelta(days=1)

  def clearAvail(self):
    """
      Clear all availabilities for this specific user

      Used during the find window option
    """
    self.availabilities = {'date':None,'times':[]}
    return True

  # Display a list of availabilities
  def findAvailability(self, startTime, endTime, timeFrame = 15):
    """
      Iterate through the blocked times and make a list of available times in between startTime and endTime

      startTime - the beginning time that the user is checking ;a date and time STRING, format 'MM/DD/YYYY HH:MM'
      endTime - the ending time that the user is checking ;a date and time STRING, format 'MM/DD/YYYY HH:MM'
      timeFrame - changes the time frames to check (probably not going to be used much, if at all)
    """
    try:
      # restriction of the time frame for checking to 15 minute increments
      assert self.meetingLength >= 15
      assert timeFrame >= 15
    except:
      return False

    startYear, startDate, start = getCorrectedTime(startTime)
    endYear, endDate, end = getCorrectedTime(endTime)
    self.availabilities['date'] = getDate(startTime)
    for i in range(start, end - self.meetingLength + timeFrame, timeFrame):
      # start with full availabilitiy
      self.availabilities['times'].append(i)

    # loop through blocked times, times that user has an event scheduled
    # and remove times that are unavailble
    for cur in self.blockedTimes:
      eventDay,eventYear = cur.getNumericalDate(0)
      # the calendar days match up, now find what times are available
      if startYear == eventYear and startDate == eventDay:
        # collision between checking day and event already scheduled
        # need to pull start and stop times of event, and remove all times between start and stop
        eventStart = cur.getMinuteOfDay(0)
        eventEnd = cur.getMinuteOfDay(1)

        # removes times before an event, based on length of the event
        j = eventEnd - timeFrame # ensures we include the time at the end of the event
        while j > (eventStart - self.meetingLength):
          try:#if j in self.availabilities['times']:
            self.availabilities['times'].remove(j)
          except:
            pass
          j = j - 15
    return True

  def listAvailabilities(self, milTime):
    """
      Prints the availabilities in a simple list

      milTime - boolean dictating whether to display in military time
    """
    try:
      assert (self.availabilities['date'] != None)
      print self.availabilities['date'], self.userName
      for i in self.availabilities['times']:
        print printTime(i, milTime)
    except:
      print "Error in printing availabilities"

  def _generateBlocks(self, service):
    """
      Creates an array of blocked times by looping through the calendar object
    """
    # loop through calendar for this specific user and add blocked times as they are pulled from api
    try:
      page_token = None
      
      while True:
        # pull the object, correcting timezone to central
        try:
          events = service.events().list(calendarId=self.userName , pageToken=page_token, timeZone='-5:00').execute()
        except:
          # cannot find the user for whatever reason
          return False
        for event in events['items']:

          try: # there is a switch from an older calendar type using dateTime in the JSON to date in the JSON, a meek attempt at correcting
            eventStart = event['start']['dateTime']
            eventEnd = event['end']['dateTime']
          except:
            eventStart = event['start']['date']
            eventEnd = event['end']['date']

          if not self._addBlockedTime(eventStart, eventEnd):
            # if for some reason adding a blocked time failed
            # we can catch it and process it here
            pass
            #print "An error occured"

        page_token = events.get('nextPageToken')
        if not page_token:
          break

    except client.AccessTokenRefreshError:
      print ("The credentials have been revoked or expired, please re-run"
        "the application to re-authorize")
      return False
    return True

class connection:
  """
  Connection class

  Creates the FLOW object and sevice object required for interacting with the calendar's api
  """
  def __init__(self, argv = ""):
    self.service = None # will contain the google flow service object that interacts with google
    self.connect(argv)  # connects to the google flow service

  def connect(self,argv):
    parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])

    flags = parser.parse_args(argv[1:])

    CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
    FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
      scope=[
          'https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/calendar.readonly',
        ],
        message=tools.message_if_missing(CLIENT_SECRETS))
    storage = file.Storage('credentials.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
      credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    self.service = discovery.build('calendar', 'v3', http=http)

class meeting:
  """
  A class that will find available users and available times for a list of users
  """
  def __init__(self, start, stop, length, users):
    self.start = start            # beginning time of the meeting
    self.stop = stop              # ending time of the meeting
    self.length = length          # length of the meeting
    self.users = users            # list of people user is checking
    self.availableTimes = []      # will hold times all users are available
    self.availUsers = []          # will hold names of all users that are available
    self._findAllAvailabilities()

  def _findAllAvailabilities(self):
    """
    Iterates availabilities for each user, trims times as necessary.
    """
    # find availabilities for each user
    for x in self.users:
      if not x.findAvailability(self.start, self.stop):
        print "Error occurred in finding availability."

    # add the availability for first user
    for i in self.users[0].availabilities['times']:
      self.availableTimes.append(i)

    # trim times that are not listed in each individual persons availability
    # list comprehension
    for i in range(1, len(self.users)):
      self.availableTimes = [elem for elem in self.availableTimes if elem in self.users[i].availabilities['times']]
  
  def listAvailTimes(self, milTime):
    """
    Used in debugging, prints a list of available times after the algorithms have run
    """
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
          availableUsers.append(j.userName)
    # set removes duplicates, easy way to remove duplicates
    if availableUsers:
      self.availUsers = list(set(availableUsers))
      return True
    return False

  def printAvailUsers(self):
    """
    Lists the users that are in availUsers, used in debugging

    availUsers is appeneded in availInTimeSlot, which returns a list of people that are available
    for the full time slot passed to the function
    """
    for user in self.availUsers:
      print user

class window:
  """
  Class that determines when an individual user is available
  """
  def __init__(self, user, startTime = None, endTime = None):
    self.user = user            # user is a person() object
    self.startTime = startTime  # string with start date and time
    self.endTime = endTime      # string with end date and time
    self.beginTime = None       # start of time window (HH:MM) to check
    self.stopTime = None        # end of time window (HH:MM) to check
    self.startDate = None       # start date to check (MM/DD/YYYY)
    self.endDate = None         # end date to check (MM/DD/YYYY)
    self.availableDates = []    # list of dictionaries that hold dates and times available

    # ensure that is startTime or endTime is set, other is set as well
    if startTime:
      assert endTime
    elif endTime:
      assert startTime
    self._constructTimes()


  def printWindow(self, milTime):
    """
    Used in debugging, lists available dates and times for user
    """
    for i in self.availableDates:
      print "------" + i['date'] + "------"
      for availTime in i['times']:
        print "      ",
        print printTime(availTime, milTime)

  def _constructTimes(self):
    """
    Helper function for _findAvail()
    """
    today = datetime.now()  # get today's date
    loopDay = today # used in the while loop
    
    # if a window is selected, parse time and set time
    if self.startTime and self.endTime:
      startYear, self.startDate, start = getCorrectedTime(self.startTime) # ints for loops and manipulation
      endYear, self.endDate, end = getCorrectedTime(self.endTime) # ints for loops and manipulation
      loopDay = convertToDatetime(self.startTime) # gets the initial day of the year to start our loop
      self.beginTime = getTime(self.startTime) # beginning time
      self.stopTime = getTime(self.endTime) # ending time
    else:
      endDay = today + timedelta(days=7) # sets ending loop day, where start is today's date
      self.startDate = getDayOfYear(today) # day of the year
      self.endDate = getDayOfYear(endDay) # day of the year
      self.beginTime = "08:00" # school hours
      self.stopTime = "18:00" # school hours
      start = 480
      end = 1080

    assert self.startDate <= self.endDate

    self._findAvail(start, end, loopDay)
    return True
  
  def _findAvail(self, start, end, loopDay):
    """
    Creates the list of dates and times that the user is available

    start - integer day of the year to begin
    end - integer day of the year to end
    loopDay - initial day to start loop on
    """
    i = self.startDate
    while i <= self.endDate:
      stringDay = getStringDate(loopDay) # convert the looped day to day and year
      start = stringDay + " " + str(self.beginTime) # get ready for findavailability call
      end = stringDay + " " + str(self.stopTime)   # get ready for findavailability call

      self.user.findAvailability(start,end) # list of availabilities
      availTimes = self.user.availabilities # copy of availabilities
      self.user.clearAvail()         # clear availabilities for next day

      self.availableDates.append(availTimes) # add current availabilities to array
      loopDay = loopDay + timedelta(days=1) # increment 1 day
      i = i + 1
    return True

def addSQLBlocks(user, onid):
  config = ConfigParser.RawConfigParser()
  config.read('sql_config_live.ini')
  host = config.get('SQL', 'host')
  username = config.get('SQL', 'user')
  passwd = config.get('SQL', 'pass')
  database = config.get('SQL', 'db')

  try:
    db = MySQLdb.connect(host=host,user=username,passwd=passwd,db=database)
    sql = db.cursor()
    query = 'SELECT scheduled_days, scheduled_start_time, scheduled_end_time, scheduled_start_date, scheduled_end_date FROM class AS cls INNER JOIN instructor AS ins ON ins.id = cls.instructor WHERE ins.username = "' + onid + '"'
    sql.execute(query)
    for row in sql.fetchall():
      classDays = parseDays(row[0])
      classStart = fixTime(row[1])
      classEnd = fixTime(row[2])
      start = fixDate(row[3])
      end = fixDate(row[4])
      start = setDateTime(start, classStart)
      end = setDateTime(end, classEnd)
      user.addClassTimeBlock(classDays, classStart, classEnd, start, end)
  except:
    return False
  sql.close()
  return True

#################################################
#      Datetime manipulation functions    #
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
#        String manipulation functions    #
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
#        Displaying and calculations      #
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