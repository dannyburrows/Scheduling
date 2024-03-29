#!/usr/bin/env python

import httplib2
import os
import MySQLdb

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache
from datetime import *
import webapp2
import jinja2
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

#################################################
#      Datetime manipulation functions          #
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
#        String manipulation functions          #
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
#        Displaying and calculations            #
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

def addSQLBlocks(user, onid):
  # LIVE DATABASE INFO
  host = "173.194.244.91"
  database = "cs419"
  username = "root"
  passwd = "cs419"

  # # Local testing
  # host = 'localhost'
  # username = 'root'
  # passwd = ''
  # database = 'Scheduling'

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
          # attempt to connect to Calendar API
          events = self.service.events().list(key="AIzaSyBqevPeL6zedWrhNcs-6qRjh55NiWeVt3E" , calendarId=self.userName , pageToken=page_token, timeZone='-5:00').execute()
        except:
          # an error occurred connecting
          return False # TODO
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

MAIN_HEADER = """
<!DOCTYPE HTML>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="http://fonts.googleapis.com/css?family=Gudea" rel="stylesheet" type="text/css">
      <link href="http://oregonstate.edu/css/bootstrap.min.css" rel="stylesheet">
      <link href="http://oregonstate.edu/css/style.css?v=1" rel="stylesheet">
      <script src="js/jquery.js"></script>
    <title>%s</title>
  </head>

  <body>

  <nav id="tophat" class="col-xs-12 hidden-xs">
    <div class="container">
        <a href="http://oregonstate.edu" class="tag" tabindex="1"><img alt="Oregon State University" src="img/osu-tag.png" /></a>
    <ul class="nav navbar-nav">
      <li><a href="http://oregonstate.edu/main/online-services" tabindex="1"><i class="fa fa-cogs"></i>Online Services</a></li>
     <li><a href="http://calendar.oregonstate.edu/" tabindex="1"><i class="fa fa-calendar"></i>Calendar</a></li>
      <li><a href="http://osulibrary.oregonstate.edu/" tabindex="1"><i class="fa fa-book"></i>Library</a></li>
      <li><a href="http://oregonstate.edu/campusmap/" tabindex="1"><i class="fa fa-map-marker"></i>Maps</a></li>
      <li><a href="https://osufoundation.org/giving/online_gift.shtml?first_designation=" tabindex="1"><i class="fa fa-gift"></i>Make a Gift</a></li>
    </ul> 

    <div class="search hidden-xs">
      <form method="get" action="http://search.oregonstate.edu">
       <label class="hidden" for="q">Find People and Pages</label>
      <input class="searchbox" type="text" placeholder="Find People and Pages" name="q" id="q" size="26" maxlength="255" value=""  tabindex="1" autofocus/>
       <input type="hidden" name="client" value="default_frontend" />
       <input class="searchbutton" type="submit" value="SEARCH" tabindex="1"/>
      </form>
    </div>
   </div> 
  </nav>

  <div class="container">
   <nav role="navigation" aria-label="Main menu" class="navbar hidden-xs">
     <ul id="primarynav" class="nav navbar-nav" role="menu">
            <li><a href="/" role="menuitem" aria-haspopup="true">Search by Users</a>
         <li><a href="/time" role="menuitem" aria-haspopup="true">Search by Available Times</a>
<li><a href="/schedule" role="menuitem" aria-haspopup="true">View Schedules</a>
    </nav>

  <br><br>
"""

MAIN_END = """
  </div></div></body>
</html>
"""

SEARCH_USER = """
  <div data-role="content" class="ui-content" role="main">
  <div class="center-wrapper">
  <br>
    <form action='/queryuser' data-ajax='false'>
    <table cellpadding=10 cellspacing=10 border=0>
    <tr><td valign=top>
    <label for='onid'>ONID username:</label> <br> To enter more than one username, please enter each onid username followed by a semi colon<br><br>
    <textarea name="onid" cols="40" rows="4" placeholder='Type onid usernames here...'></textarea>
    </td><tr>
    <tr>
    <td valign=top>
    <label for='date'>Start Date (YYYY/MM/DD):</label> 
    <input type='date' name='SearchDate' id='SearchDate' placeholder='YYYY/MM/DD'></td></tr>
    <tr>
    <td valign=top>
    <label for='length'>Meeting Length (mins): </label> 
    <select name="length">
    <option value="15" selected>15</option>
    <option value="30">30</option>
    <option value="45">45</option>
    <option value="60">60</option>
    <option value="75">75</option>
    <option value="90">90</option>
    <option value="105">105</option>
    <option value="120">120</option>
    <option value="135">135</option>
    <option value="150">150</option>
    <option value="165">165</option>
    <option value="180">180</option>
    </select>
    </td></tr>
    <tr><td valign=top> 
    <label for='time1'>Start time:</label> Hour 
    <select name="hour1">
    <option value="08" selected>8 AM</option>
    <option value="09">9 AM</option>
    <option value="10">10 AM</option>
    <option value="11">11 AM</option>
    <option value="12">12 PM</option>
    <option value="13">1 PM</option>
    <option value="14">2 PM</option>
    <option value="15">3 PM</option>
    <option value="16">4 PM</option>
    <option value="17">5 PM</option>
    <option value="18">6 PM</option>
    </select>
    Minutes: <select name="min1">
    <option value="00" selected>00</option>
    <option value="15">15</option>
    <option value="30">30</option>
    <option value="45">45</option>
    </select>
    </td></tr>
    <tr>
    <td valign=top> 
    <label for='time2'>End time:</label> Hour 
    <select name="hour2">
    <option value="08">8 AM</option>
    <option value="09">9 AM</option>
    <option value="10">10 AM</option>
    <option value="11">11 AM</option>
    <option value="12">12 PM</option>
    <option value="13">1 PM</option>
    <option value="14">2 PM</option>
    <option value="15">3 PM</option>
    <option value="16">4 PM</option>
    <option value="17">5 PM</option>
    <option value="18" selected>6 PM</option>
    </select>
    Minutes: <select name="min2">
    <option value="00" selected>00</option>
    <option value="15">15</option>
    <option value="30">30</option>
    <option value="45">45</option>
    </select>
    </td></tr>
    
    </table>
    <input type='submit' value='Query'>
    </form> 
  </div>
"""

SEARCH_TIME = """
  <div data-role="content" class="ui-content" role="main">
  <div class="center-wrapper">
  <br>
    <form action='/queryTime' data-ajax='false'>
    <table cellpadding=10 cellspacing=10 border=0>
    <tr><td valign=top colspan=2>
    <label for='onid'>ONID username:</label> <br> To enter more than one username, please enter each onid username followed by a semi colon<br><br>
    <textarea name="onid" cols="40" rows="3" placeholder="Type onid usernames here..."></textarea>
    </td></tr>
    <tr>
    <td valign=top>
    <label for='date'>Date (YYYY/MM/DD):</label> 
    <input type='date' name='SearchDate' id='SearchDate' placeholder='YYYY/MM/DD'></td>
    <td valign=top>
    <label for='time1'>Start time:</label> Hour 
    <select name="hour1">
    <option value="08" selected>8 AM</option>
    <option value="09">9 AM</option>
    <option value="10">10 AM</option>
    <option value="11">11 AM</option>
    <option value="12">12 PM</option>
    <option value="13">1 PM</option>
    <option value="14">2 PM</option>
    <option value="15">3 PM</option>
    <option value="16">4 PM</option>
    <option value="17">5 PM</option>
    <option value="18">6 PM</option>
    </select>
    Minutes: <select name="min1">
    <option value="00" selected>00</option>
    <option value="15">15</option>
    <option value="30">30</option>
    <option value="45">45</option>
    </select>

    </td>
    </tr>
    <tr>
    <td valign=top colspan=2>
    <label for='length'>Meeting Length (mins):</label> 
    <select name="length">
    <option value="15" selected>15</option>
    <option value="30">30</option>
    <option value="45">45</option>
    <option value="60">60</option>
    <option value="75">75</option>
    <option value="90">90</option>
    <option value="105">105</option>
    <option value="120">120</option>
    <option value="135">135</option>
    <option value="150">150</option>
    <option value="165">165</option>
    <option value="180">180</option>
    </select>
    </td></tr>
    </table>
    <input type='submit' value='Query'>
    </form> 
  </div>
"""

SEARCH_SCHEDULE = """
  <div data-role="content" class="ui-content" role="main">
  <div class="center-wrapper">
  <br>
    <form action='/querySchedule' data-ajax='false'>
    <table cellpadding=10 cellspacing=10 border=0>
    <tr><td valign=top>
    <label for='onid'>ONID username:</label> 
    <input type="text" name="onid">
    </td><tr>
    <tr>
    <td valign=top>
    <label for='date'>Start Date (YYYY/MM/DD):</label> 
    <input type='date' name='SearchDate' id='SearchDate' placeholder='YYYY/MM/DD'></td></tr>
    <tr><td valign=top> 
    <label for='time1'>Start time:</label> Hour 
    <select name="hour1" id="hour1">
    <option value="08" selected>8 AM</option>
    <option value="09">9 AM</option>
    <option value="10">10 AM</option>
    <option value="11">11 AM</option>
    <option value="12">12 PM</option>
    <option value="13">1 PM</option>
    <option value="14">2 PM</option>
    <option value="15">3 PM</option>
    <option value="16">4 PM</option>
    <option value="17">5 PM</option>
    <option value="18">6 PM</option>
    </select>
    Minutes: <select name="min1" id="min1">
    <option value="00" selected>00</option>
    <option value="15">15</option>
    <option value="30">30</option>
    <option value="45">45</option>
    </select>
    </td></tr>
    <tr>
    <td valign=top> 
    <label for='time2'>End time:</label> Hour 
    <select name="hour2" id="hour2">
    <option value="08">8 AM</option>
    <option value="09">9 AM</option>
    <option value="10">10 AM</option>
    <option value="11">11 AM</option>
    <option value="12">12 PM</option>
    <option value="13">1 PM</option>
    <option value="14">2 PM</option>
    <option value="15">3 PM</option>
    <option value="16">4 PM</option>
    <option value="17">5 PM</option>
    <option value="18" selected>6 PM</option>
    </select>
    Minutes: <select name="min2" id="min2">
    <option value="00" selected>00</option>
    <option value="15">15</option>
    <option value="30">30</option>
    <option value="45">45</option>
    </select>
    </td></tr>
    </table>
    <input type='checkbox' id='saneDefault' name='saneDefault'>Check next 7 days availabilty<br><br>
    <input type='submit' value='Query'>
    </form> 
  <script>
  /* JS for hiding stuff on checkbox check */
  $('#saneDefault').change(function () {
    if ($(this).is(':checked')) {
      $('#SearchDate').prop('disabled', true);
      $('#hour1').prop('disabled', true);
      $('#min1').prop('disabled', true);
      $('#hour2').prop('disabled', true);
      $('#min2').prop('disabled', true);
    } else {
      $('#SearchDate').prop('disabled', false);
      $('#hour1').prop('disabled', false);
      $('#min1').prop('disabled', false);
      $('#hour2').prop('disabled', false);
      $('#min2').prop('disabled', false);
    }
  })
  </script>
  </div>
"""

class searchUsers(webapp2.RequestHandler):
    def get(self):
      self.response.write(MAIN_HEADER % 'OSU Scheduling Tool-search by users')
      self.response.write("<h1>Search by Users</h1>")
      self.response.write(SEARCH_USER)
      self.response.write("<br><br>")
      self.response.write(MAIN_END)

class searchTime(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_HEADER % 'OSU Scheduling Tool-search by available times')
    self.response.write("""
      <h1>Search by Available Times</h1>
    <div data-role="content" class="ui-content" role="main">
    <div class="center-wrapper">""")
    self.response.write(SEARCH_TIME)
    self.response.write("<br><br>")
    self.response.write(MAIN_END)

class searchSchedule(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_HEADER % 'OSU Scheduling Tool-view schedules')
    self.response.write("""
      <h1>View Schedules</h1>
    <div data-role="content" class="ui-content" role="main">
    <div class="center-wrapper">""")
    self.response.write(SEARCH_SCHEDULE)
    self.response.write("<br><br>")
    self.response.write(MAIN_END)

class queryUser(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_HEADER % "Results")
    users = self.request.get('onid').split(';')
    length = int(self.request.get('length'))
    startTime = self.request.get('hour1') + ":" + self.request.get('min1')
    endTime = self.request.get('hour2') + ":" + self.request.get('min2')
    rawDate = self.request.get('SearchDate').replace('-', '/')
    startDate = rawDate[5:] + '/' + rawDate[:4]
    start = startDate + " " + startTime
    end = startDate + " " + endTime
    onidusers = [] # array for person objects
    # add google calendar blocks and SQL blocks
    for user in users:
      temp = person(user+'@onid.oregonstate.edu', length, service)
      addSQLBlocks(temp, user) # temp is the person object, user is the onid name
      onidusers.append(temp)
    # all data structures prepped, query for meeting
    newMeeting = meeting(start, end, length, onidusers) # available times will be held in newMeeting.
    # times were successfully found
    self.response.write("<div class='row'><div class='col-md-8' style='text-align:center'><h3><strong>Meeting Info</strong></h3></div></div>")
    self.response.write("<br><div class='row'><div class='col-md-2'><strong>Date: </strong>%s</div>" % rawDate)
    self.response.write("<div class='col-md-2'><strong>Start Time: </strong>%s</div>" % startTime)
    self.response.write("<div class='col-md-2'><strong>End Time: </strong>%s</div>" % endTime)
    self.response.write("<div class='col-md-2'><strong>Length: </strong>%s</div></div>" % str(length))
    self.response.write("<br><div class='row'><div class='col-md-3'><strong>Users</strong></div>")
    self.response.write("<div class='col-md-3'><strong>Available Times</strong></div></div>")
    if newMeeting.availInTimeSlot():
      # output the data
      self.response.write("<div class='row'><div class='col-md-3'>")
      for user in onidusers:
        self.response.write(user.userName + "<br>")
      self.response.write("</div><div class='col-md-3'>")
      for timeslot in newMeeting.availableTimes:
        self.response.write(printTime(timeslot) + " - " + printTime(timeslot+length) + "<br>")
      self.response.write("</div></div>")
    self.response.write(MAIN_END)

class queryTime(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_HEADER % "Results")
    users = self.request.get('onid').split(';')
    length = int(self.request.get('length'))
    rawTime = self.request.get('hour1') + ":" + self.request.get('min1')
    startTime = rawTime
    endTime = convertTimeToString(getTotalMinutes(rawTime[0:2], rawTime[3:5]) + length)
    rawDate = self.request.get('SearchDate').replace('-', '/')
    startDate = rawDate[5:] + '/' + rawDate[:4]
    start = startDate + " " + startTime
    end = startDate + " " + endTime
    onidusers = [] # array for person objects
    # add google calendar blocks and SQL blocks
    for user in users:
      temp = person(user+'@onid.oregonstate.edu', length, service)
      addSQLBlocks(temp, user) # temp is the person object, user is the onid name
      onidusers.append(temp)
    # all data structures prepped, query for meeting
    newMeeting = meeting(start, end, length, onidusers) # available times will be held in newMeeting.
    # times were successfully found
    self.response.write("<div class='row'><div class='col-md-6' style='text-align:center'><h3><strong>Meeting Info</strong></h3></div></div>")
    self.response.write("<br><div class='row'><div class='col-md-2'><strong>Date: </strong>%s</div>" % rawDate)
    self.response.write("<div class='col-md-2'><strong>Start Time: </strong>%s</div>" % startTime)
    self.response.write("<div class='col-md-2'><strong>Length: </strong>%s</div></div>" % str(length))
    self.response.write("<br><div class='row'><div class='col-md-6'><strong>Available Users</strong></div></div>")
    if newMeeting.availInTimeSlot():
      # output the data
      self.response.write("<div class='row'><div class='col-md-6'>")
      # self.response.write("</div><div class='col-md-2'> </div><div class='col-md-2'>")
      for user in newMeeting.availUsers:
        self.response.write(user + "<br>")
      self.response.write("</div></div>")
    self.response.write(MAIN_END)

class querySchedule(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_HEADER % "Results")
    getUser = self.request.get('onid')
    user = person(getUser  + "@onid.oregonstate.edu", 15, service)
    addSQLBlocks(user, getUser)
    saneDefault = self.request.get('saneDefault')
    if saneDefault:
      # handle the checked box
      newWindow = window(user)
      self.response.write("<div class='row'><div class='col-md-6' style='text-align:center'><h3><strong>%s's Schedule</strong></h3></div></div>" % getUser)
      self.response.write("<br><div class='row'><div class='col-md-2'><strong>Next 7 days</strong></div>")
      self.response.write("<div class='col-md-2'><strong>Start Time: </strong>08:00</div>")
      self.response.write("<div class='col-md-2'><strong>End Time: </strong>16:00</div></div>")
    else:
      startTime = self.request.get('hour1') + ":" + self.request.get('min1')
      endTime = self.request.get('hour2') + ":" + self.request.get('min2')
      rawDate = self.request.get('SearchDate').replace('-', '/')
      startDate = rawDate[5:] + '/' + rawDate[:4]
      start = startDate + " " + startTime
      end = startDate + " " + endTime
      newWindow = window(user, start, end)
      self.response.write("<div class='row'><div class='col-md-6' style='text-align:center'><h3><strong>%s's Available Times</strong></h3></div></div>" % getUser)
      self.response.write("<br><div class='row'><div class='col-md-2'><strong>Date: </strong>%s</div>" % rawDate)
      self.response.write("<div class='col-md-2'><strong>Start Time: </strong>%s</div>" % startTime)
      self.response.write("<div class='col-md-2'><strong>End Time: </strong>%s</div></div>" % endTime)

    self.response.write("<br><br><div class='row'>")
    for slots in newWindow.availableDates:
      self.response.write("<div class='col-md-1'><strong>%s</strong><br>" % slots['date'])
      for times in slots['times']:
        self.response.write(printTime(times) + "<br>")
      self.response.write("</div>")
    self.response.write("</div>")
    self.response.write(MAIN_END)

app = webapp2.WSGIApplication([
    ('/', searchUsers),
    ('/time', searchTime),
    ('/schedule', searchSchedule),
    ('/queryuser', queryUser),
    ('/queryTime', queryTime),
    ('/querySchedule', querySchedule),
    (decorator.callback_path, decorator.callback_handler()),
    ], debug=True)