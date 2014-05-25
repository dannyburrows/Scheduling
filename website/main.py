#!/usr/bin/env python

import httplib2
import os

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache
from datetime import *

import webapp2
import jinja2

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
  return hours * 60 + mins


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

class unavailTime:
  """
    unavailTime

    This class is designed as a data structure for a time frame. A break down of functionalities follow:

    getStart(), getEnd(), setStart(), setEnd()
    --standard getter and setters
    --sets expect a unicoded format of time

    getMinuteOfDay(flag)
    --returns an integer that is the minute of the day, based on the equation hour*60 + minutes
    --flag is a boolean, 0 for the start, 1 for end

    getNumericalDate(flag)
    --returns a numerical representation of the date for comparison purposes
    --flag is a boolean, 0 for the start, 1 for the end

    _updateLength()
    --checks if both end and start have been set, if so calculates and sets the length

    check()
    --a few small checks for the class instance
    --if an assert fails, catches and returns false, allowing program to continue
    --should be used every time a new unavailTime is created
  """
  def __init__(self, start = None, end = None):
    self.start = start
    self.end = end
    self.length = -1
    self._updateLength()

  def getStart(self):
    return self.start

  def getEnd(self):
    return self.end

  def getLength(self):
    return self.length

  # flag determines whether start or end is returned
  def getMinuteOfDay(self, flag):
    if not flag:
      mins = getMins(self.start)
      hours = getHour(self.start)
    else:
      mins = getMins(self.end)
      hours = getHour(self.end)

    return 60 * hours + mins

  def getNumericalDate(self, flag):
    if not flag:
      numDate = getDayOfYear(self.start)#int(self.start.strftime("%j"))
      numYear = getYear(self.start)#int(self.start.strftime("%y"))
    else:
      numDate = getDayOfYear(self.end)#int(self.end.strftime("%j"))
      numYear = getYear(self.end)#int(self.end.strftime("%y"))

    return numDate,numYear

  def setStart(self, start, google = True):
    """
      Sets the start time of the block. There is a bit of brute force here due to the unicode calendar object being returned from Google.
    """
    if google:
      temp = simpleParse(start)
      temp = temp[:19]
      self.start = convertToDatetimeFull(temp)
    else:
      self.start = start
    self._updateLength()
    return True

  def setEnd(self, end, google = True):
    """
      Sets the end time of the block. There is a bit of brute force here due to the unicode calendar object being returned from Google.
    """
    if google:
      temp = simpleParse(end) # turn unicode to string
      temp = temp[:19] # trim the time zone out
      self.end = convertToDatetimeFull(temp) # convert to a datetime object for further manipulation later
    else:
      self.end = end
    self._updateLength()
    return True

  # sets the length if there is both a start and end time
  def _updateLength(self):
    if self.end and self.start:
      # a VERY rough calculated of length
      hourS = getHour(self.start)
      hourE = getHour(self.end)
      minsS = getMins(self.start)
      minsE = getMins(self.end)
      self.length = 60 * (hourE - hourS) + (minsE - minsS)
      return True
    return False

  def check(self):
    try:
      assert self.start
      assert self.end
      assert self.length
      return True
    except:
      return False

class person:
  """
    person

    The heart of the scheduling program. Contains information on blocked times, available times, the users name and the meeting length.
    On instantiation, checks whether the blocked source is from the google calendar or from the database. If it's the database, a separate
    function must be called. If there is a google source, a service object is required for connection to the api.
  """
  def __init__(self, userName, length, service = None, google = True):
    assert userName
    self.service = service
    self.meetingLength = length
    self.blockedTimes = []
    self.availabilities = {'date':None,'times':[]}
    self.userName = userName
    self.errorFlag = False
    self.errorMsg = ""
    self._process(google)
    # if the source is the google calendar
  
  def _process(self, google):
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


  def getUserName(self):
    """
      Simply provides an abstracted method to obtain user name
    """
    return self.userName

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


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<p>
<code>%s</code>.
</p>
<p>with information found on the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>
""" % CLIENT_SECRETS

http = httplib2.Http(memcache)
service = discovery.build('calendar', 'v3', http=http)
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=MISSING_CLIENT_SECRETS_MESSAGE)

class MainHandler(webapp2.RequestHandler):

  @decorator.oauth_aware
  def get(self):
    test = person('burrows.danny@gmail.com', 60, service)
    test.findAvailability("04/15/2014 07:00", "04/15/2014 21:00")
    for x in test.availabilities['times']:
      self.response.write("%s<br>" % x)

app = webapp2.WSGIApplication(
    [
     ('/', MainHandler),
     (decorator.callback_path, decorator.callback_handler()),
    ],
    debug=True)
