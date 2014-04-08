# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

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

    _cleanTime(inputTime)
    --returns a time string formatted "mm/dd/yyyy hh:mm"
    --strips timezone information, unsure of full result of this as of current
    
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
    self.length = None
    self._updateLength()

  def getStart(self):
    return self.start

  def getEnd(self):
    return self.end

  def setStart(self, start):
    self.start = dateutil.parser.parse(start)#self._cleanTime(start)
    self._updateLength()
    return True

  def setEnd(self, end):
    self.end = dateutil.parser.parse(end)#self._cleanTime(end)
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
      hour1 = str(self.start)[11:13]
      hour2 = str(self.end)[11:13]
      mins1 = str(self.start)[14:16]
      mins2 = str(self.end)[14:16]
      hours = int(hour2) - int(hour1)
      mins = int(mins2) - int(mins1)
      self.length = 60 * hours + mins 

      #self.length = 1#int(self.end) - int(self.start) # TEST THIS!!!
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

    #print "Start - " + str(self.start) + " End - " + str(self.end) + " Length - " + str(self.length)

class person:
  """
    person

    A class instance that tracks the username of a person as well as a list of times that they are not available

    addBlockedTime(start, end)
    -takes in start and end as unicoded time objects, creates a new unavailTime object and appends to internal array that tracks all unavailable time slots
    -performs a self check to ensure that start, end and length are all properly set before appending

    getUserNam()
    -returns user name for the current person

    listAvailbility(startTime, endTime)
    -CURRENT NOT IMPLEMENTED
    -will display a formatted list of times current available between the start and end time parameters

    _generateBlocks(service)
    -creates an array of blocked times by looping through the calendar object
  """
  def __init__(self, userName, service):
    assert userName
    assert service
    self.blockedTimes = []
    self.userName = userName
    self._generateBlocks(service)

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

  # Format date time as a string
  def _formatDateTime(self, inputDateTime):
     return dateutil.parser.parse(inputDateTime).strftime("%m/%d/%y %I:%M")

  # Display a list of availabilities
  def listAvailbility(self, startTime, endTime):
    # loop through blockedTimes
    # if time frame is not in blocked times, prints
    # else skip

    # loop from 8am to 6pm in 15 minute increments (while loop, checkTime.init=8am)
    # -loop through each self.blockedTime
    # --if self.blockedTime[x] = checkTime
    # ---checkTime=checkTime + length of block out
    # --else
    # ---add checkTime to available time
    pass

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

          self.addBlockedTime(eventStart, eventEnd)
          #if not self.addBlockedTime(eventStart, eventEnd):
          #  print "An error occured adding the time block"
          #  exit()

          # the parsing function in the class should be taking care of this
          #currentDateTime = time.strftime("%m/%d/%y")
          #eventStart = dateutil.parser.parse(eventStart)
          #eventEnd = dateutil.parser.parse(eventEnd)

          # [-1] for the last added time block
          curTime = datetime.now()
          startTime = self.blockedTimes[-1].getStart()
          if curTime < startTime.replace(tzinfo=None):
            print self.blockedTimes[-1].getStart(),
            print " - ",
            print self.blockedTimes[-1].getEnd(),
            print " - length:",
            print self.blockedTimes[-1].length
            print "\t" + self.getUserName()
            #print totalTime
          
       
        page_token = events.get('nextPageToken')
        if not page_token:
          break
    except client.AccessTokenRefreshError:
      print ("The credentials have been revoked or expired, please re-run"
        "the application to re-authorize")
      return False
    return True

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/724364097552/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv):
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Calendar API.
  service = discovery.build('calendar', 'v3', http=http)
  user = person("burrows.danny@gmail.com", service)
  # try:
  #   #print "Success! Now add code here."
  #   page_token = None
    
  #   while True:
  #     events = service.events().list(calendarId=user.getUserName() , pageToken=page_token).execute()
  #     userName = events['summary']
  #     for event in events['items']:

  #       try: # there is a switch from an older calendar type using dateTime in the JSON to date in the JSON, a meek attempt at correcting
  #         eventStart = event['start']['dateTime']
  #         eventEnd = event['end']['dateTime']
  #       except:
  #         eventStart = event['start']['date']
  #         eventEnd = event['end']['date']

  #       if not user.addBlockedTime(eventStart, eventEnd):
  #         print "An error occured adding the time block"
  #         exit()

  #       # the parsing function in the class should be taking care of this
  #       #currentDateTime = time.strftime("%m/%d/%y")
  #       #eventStart = dateutil.parser.parse(eventStart)
  #       #eventEnd = dateutil.parser.parse(eventEnd)

  #       # [-1] for the last added time block
  #       if datetime.now() < user.blockedTime[-1].getStart():
  #         print user.blockedTime[-1].getStart(),
  #         print " - ",
  #         print user.blockedTime[-1].getEnd(),
  #         print "\t" + user.getUserName()
        
     
  #     page_token = events.get('nextPageToken')
  #     if not page_token:
  #       break
  # except client.AccessTokenRefreshError:
  #   print ("The credentials have been revoked or expired, please re-run"
  #     "the application to re-authorize")


# For more information on the Calendar API you can visit:
#
#   https://developers.google.com/google-apps/calendar/firstapp
#
# For more information on the Calendar API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
  main(sys.argv)