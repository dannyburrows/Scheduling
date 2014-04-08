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
import sys

import dateutil.parser
import time

from datetime import *
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Person class
# Will track availability information for each person
# Will contain an array that has a start and stop time where the person is not available

# Class to hold a time slot that is completely blocked out
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

    _cleanTime(inputTime)
    --returns a time string formatted "mm/dd/yyyy hh:mm"
    --strips timezone information, unsure of full result of this as of current
    
    _updateLength()
    --checks if both end and start have been set, if so calculates and sets the length

    _getHours()
    --helper function for _updateLength
    --takes the input (either start or end time) and returns an int representation of the hours

    _getMins()
    --helper funciton for _updateLength
    --takes the input (either start or end time) and returns an int representation of the mins

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
      mins = self._getMins(self.start)
      hours = self._getHour(self.start)
    else:
      mins = self._getMins(self.end)
      hours = self._getHour(self.end)

    return 60 * hours + mins

  def getNumericalDate(self, flag):
    if not flag:
      numDate = int(self.start.strftime("%j"))
      numYear = int(self.start.strftime("%y"))
    else:
      numDate = int(self.end.strftime("%j"))
      numYear = int(self.end.strftime("%y"))

    return numDate,numYear

  def setStart(self, start):
    self.start = dateutil.parser.parse(start)
    self._updateLength()
    return True

  def setEnd(self, end):
    self.end = dateutil.parser.parse(end)
    self._updateLength()
    return True

  # properly formats date and time
  def _cleanTime(self, inputTime):
    temp = dateutil.parser.parse(inputTime)
    temp.replace(tzinfo=None)
    return temp.strftime("%m/%d/%y %I:%M")

  # sets the length if there is both a start and end time
  def _updateLength(self):
    if self.end and self.start:
      # a VERY rough calculated of length
      hourS = self._getHour(self.start)
      hourE = self._getHour(self.end)
      minsS = self._getMins(self.start)
      minsE = self._getMins(self.end)
      self.length = 60 * (hourE - hourS) + (minsE - minsS)
      return True
    return False

  # returns an integer for hour based by parsing the datetime as a string
  # there is an easier way to do this...
  def _getHour(self, input):
    return int(str(input)[11:13])

  # returns an integer for minutes based by parsing the datetime as a string
  # there is an easier way to do this...
  def _getMins(self, input):
    return int(str(input)[14:16])

  def check(self):
    try:
      assert self.start
      assert self.end
      assert self.length
      return True
    except:
      return False

    #print "Start - " + str(self.start) + " End - " + str(self.end) + " Length - " + str(self.length)

class person:
  """
    person

    A class instance that tracks the username of a person as well as a list of times that they are not available

    addBlockedTime(start, end)
    --takes in start and end as unicoded time objects, creates a new unavailTime object and appends to internal array that tracks all unavailable time slots
    --performs a self check to ensure that start, end and length are all properly set before appending

    getUserName()
    --returns user name for the current person

    findAvailbility(startTime, endTime)
    --creates a list of available times based on string passed into function
    
    listAvailabilities()
    --displays a list of availabilities for this specific user, on the date that passed into the findAvailbility() function

    _displayTime(input)
    --helper function for listAvailabilities
    --returns a string with a prettily formatted time

    _getCorrectedTime(input)
    --helper function for findAvailbility
    --returns year, date, mins of a passed in string

    
    _generateBlocks(service)
    --creates an array of blocked times by looping through the calendar object

    connect()
    --connects to the google calendar api
  """
  def __init__(self, userName):
    assert userName
    self.service = None
    self.connect()
    self.blockedTimes = []
    self.availabilities = {'date':None,'times':[]}
    self.userName = userName
    self._generateBlocks(self.service)

  # Add new blocked out time
  def addBlockedTime(self, start, end):
    newBlock = unavailTime()
    newBlock.setStart(start)
    newBlock.setEnd(end)
    if newBlock.check():
      self.blockedTimes.append(newBlock)
      return True
    return False

  def getUserName(self):
    return self.userName

  # Display a list of availabilities
  def findAvailbility(self, startTime, endTime):
    startYear, startDate, start = self._getCorrectedTime(startTime)
    endYear, endDate, end = self._getCorrectedTime(endTime)
    self.availabilities['date'] = startTime[0:10]
    for cur in self.blockedTimes:
      i = start
      eventDay,eventYear = cur.getNumericalDate(0)
      # the calendar days match up, now find what times are available
      if startYear == eventYear and startDate == eventDay:
        while (i <= end):
          # there is a collision between a scheduled event for this user and the time entered
          if cur.getMinuteOfDay(0) == i:
            i = i + cur.getLength()
          self.availabilities['times'].append(i)
          i = i + 15
    if not self.availabilities['times']:
      self.availabilities['times'].append("All")

  def listAvailabilities(self):
    try:
      assert (self.availabilities['date'] != None)
      print self.availabilities['date'], self.userName
      if self.availabilities['times'][0] == 'All':
        print "All"
      else:
        for i in self.availabilities['times']:
          print self._displayTime(i)
    except:
      print "Error in printing availabilities"

  def _displayTime(self, input):
    hours = input / 60
    mins = input % 60
    time = "%02d:%02d" % (hours, mins)
    return time

  def _getCorrectedTime(self, input):
    # "04/10/2014 08:00"
    temp = datetime.strptime(input[0:10], '%m/%d/%Y')
    year = int(temp.strftime("%y"))
    date = int(temp.strftime("%j"))
    mins = int(input[11:13]) * 60 + int(input[14:16])
    #print date,mins
    return year,date,mins

  def _generateBlocks(self, service):
    # loop through calendar for this specific user and add blocked times as they are pulled from api
    try:
      #print "Success! Now add code here."
      page_token = None
      
      while True:
        events = service.events().list(calendarId=self.userName , pageToken=page_token).execute()
        userName = events['summary']
        for event in events['items']:

          try: # there is a switch from an older calendar type using dateTime in the JSON to date in the JSON, a meek attempt at correcting
            eventStart = event['start']['dateTime']
            eventEnd = event['end']['dateTime']
          except:
            eventStart = event['start']['date']
            eventEnd = event['end']['date']

          if not self.addBlockedTime(eventStart, eventEnd):
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

  def connect(self):
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
      credentials = tools.run_flow(FLOW, storage, None)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    self.service = discovery.build('calendar', 'v3', http=http)

def main(argv):
  user = person("burrows.danny@gmail.com")
  user.findAvailbility("04/10/2014 08:30", "04/10/2014 15:00")
  user.listAvailabilities()  
 
if __name__ == '__main__':
  main(sys.argv)