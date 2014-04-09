#README

Scheduler

##A break down of the project
####Scrape OSU Catalog
####Scrape web catalog and post to database

-Scrape page (I've looked into beautifulsoup for scraping)

-Iterate through each set of links

-Pull relevant data

-Post relevant data to database (MySQLdb seems to be a functional library)
####Pull Google Calendar
####Query database
Make sure queries are parsable
####Availability
List times

-In: User name, time frame

-Out: Open times within the time frame

Specific time frame, multiple people

-In: Specific time frame, list of user names

-Out: List all users available in time frame

Broad time frame

-In: Broad time frame, list of user names

-Out: All time periods where ALL are available

##Web interface and curses implementation are needed