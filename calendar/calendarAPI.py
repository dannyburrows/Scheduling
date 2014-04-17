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

from timemanip import *
from dateutil.tz import *
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
    if google:
      self.start = dateutil.parser.parse(start)
    else:
      self.start = start
    self._updateLength()
    return True

  def setEnd(self, end, google = True):
    if google:
      self.end = dateutil.parser.parse(end)
      self._updateLength()
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
    # if the source is the google calendar
    if google:
      assert service != None
      self._generateBlocks(self.service)

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
        events = service.events().list(calendarId=self.userName , pageToken=page_token, timeZone='-5:00').execute()
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

"""
  Connection class

  Creates the FLOW object and sevice object required for interacting with the calendar's api
"""
class connection:
  def __init__(self, argv = ""):
    self.service = None
    self.connect(argv)

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

# Uncomment for local testing within the api
# def main(argv):
#   service = connection(argv)
#   user = person("clampitl@onid.oregonstate.edu",30,service.service)
#   user.findAvailability("04/15/2014 07:00", "04/15/2014 21:00")
#   user.listAvailabilities(False)  
  
#   user = person("burrows.danny@gmail.com",30,service.service)
#   user.findAvailability("04/15/2014 07:00", "04/15/2014 21:00")
#   user.listAvailabilities(False)  
 
# if __name__ == '__main__':
#   main(sys.argv)