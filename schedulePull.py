from bs4 import BeautifulSoup
import urllib2
import MySQLdb
import sys
#This is the generic website for searching all the available classes offered by OSU
html = urllib2.urlopen("http://catalog.oregonstate.edu/SOCSearcher.aspx?wks=&chr=abcder").read()

soup = BeautifulSoup(html)

#database information:
host = 'mysql.cs.orst.edu'
dbusername = 'cs419_group2'
passwd = 'bwQR2TY4D4jfAnCZ'
database = 'cs419_group2'

#Start off by clearing out the DB and rebuilding it up from scratch
db = MySQLdb.connect(host=host,user=dbusername,passwd=passwd,db=database)
sql = db.cursor()
query = "DROP TABLE IF EXISTS `usernames`" 
try:
	sql.execute(query)
	db.commit()
	#print "inserted"
	#db.close()
except MySQLdb.Error, e:
	print "Error %d: %s" % (e.args[0], e.args[1])
	db.rollback()
query = "DROP TABLE IF EXISTS `catalog`" 
try:
	sql.execute(query)
	db.commit()
	#print "inserted"
	#db.close()
except MySQLdb.Error, e:
	print "Error %d: %s" % (e.args[0], e.args[1])
	db.rollback()
query = "CREATE TABLE usernames (id INT NOT NULL AUTO_INCREMENT, instructor VARCHAR(255), department VARCHAR(255), username VARCHAR(255), PRIMARY KEY(id))ENGINE=InnoDB" 
try:
	sql.execute(query)
	db.commit()
	#print "inserted"
	#db.close()
except MySQLdb.Error, e:
	print "Error %d: %s" % (e.args[0], e.args[1])
	db.rollback()	
query = "CREATE TABLE catalog (id INT NOT NULL AUTO_INCREMENT, subject_code VARCHAR(255) NOT NULL, course_num VARCHAR(255), term VARCHAR(255), CRN VARCHAR(255), section VARCHAR(255), credits VARCHAR(255), instructor VARCHAR(255), scheduled_days VARCHAR(255),	scheduled_start_time VARCHAR(255), scheduled_end_time VARCHAR(255), scheduled_start_date VARCHAR(255), scheduled_end_date VARCHAR(255), final_scheduled_day VARCHAR(255), final_scheduled_start_time VARCHAR(255), final_scheduled_end_time VARCHAR(255), final_scheduled_date VARCHAR(255), location VARCHAR(255), final_location VARCHAR(255), campus VARCHAR(255), type VARCHAR(255), PRIMARY KEY (id))ENGINE=InnoDB" 
try:
	sql.execute(query)
	db.commit()
	#print "inserted"
	#db.close()
except MySQLdb.Error, e:
	print "Error %d: %s" % (e.args[0], e.args[1])
	db.rollback()		
db.close()

urls = []
website = []
#This filters all the urls from the catalog and stores them in a list called links
for links in soup.find_all('a'):
	link = str(links.get('href'))
	#print(link)
	if link[0] == '/':
		urls.append(link)

#file = open('links.txt', 'w')
for url in urls:
	website.append("http://catalog.oregonstate.edu" + url)


file = open('tables.txt', 'w')
for site in website:
	html2 = urllib2.urlopen(site).read()
	
	#this gathers all the '=' and '&' in the url to pull the subject code and course number easily
	equals = []
	ampersand = []
	i = 0
	for chars in site:
		if chars == '=':
			#print(i+1)
			equals.append(i+1)
		if chars == '&':
			#print(i)
			ampersand.append(i)
		i += 1

	soup = BeautifulSoup(html2)
	#This line pulls the text right after the College of _____ text.
	#dept = soup.body.a.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.a.get_text()
	tr = soup.fieldset.div.next_sibling.next_sibling.next_sibling.next_sibling.div.table.tr
	
	while True:
		try:
			tr = tr.next_sibling
			td = tr.stripped_strings
			table = [site[equals[0]:ampersand[0]], site[equals[1]:ampersand[1]]]
			count = 2
			start = 0
			final_present = False
			for string in td:
				if count == 7:
					i = 0
					while string[i] != ' ':
						i += 1
					table.append(str(string[:i]))
					count += 1
					start = i + 1
					table.append(str(string[start:start+4]))
					count += 1
					table.append(str(string[start+5:start+9]))
					count += 1
				elif count == 10:
					i = 0
					while string[i] != '-':
						i += 1
					table.append(str(string[:i]))
					count += 1
					table.append(str(string[i+1:]))
					count += 1
				elif count == 12:
					#This is a check to see if the first character is alone in this line. If it is alone, then we have a case of the final exam being listed.  We need to parse that out if it exists or skip it all together if it does not.  We can hard code it due to the way the final exam is listed.
					if string[1] == ' ':
						final_present = True
						table.append(str(string[0]))
						count += 1
						table.append(str(string[2:6]))
						count += 1
						table.append(str(string[7:]))
						count += 1
					else:
					#If the next string is not a final schedule day, then we need to insert skips for the finals date, and record the location.
						table.append("__NOT-PRESENT__")
						table.append("__NOT-PRESENT__")
						table.append("__NOT-PRESENT__")
						table.append("__NOT-PRESENT__")
						table.append(str(string))
						table.append("__NOT-PRESENT__")
						count += 6
				elif count == 16:
					#if the final present tag is set and the count is 16 then the final is present and we need to record the room for the final, otherwise we need to skip it.
					if final_present == True:
						table.append(str(string))
						count += 1
				elif count > 19:
					break
				else:
					#Need to skip the "P/N" string if it occurs.
					if string == "P/N":
						pass
					else:
						table.append(str(string))
						count += 1
			#table.append(str(dept))
			
			#Now we have all the information, we just need to put in in the table catalog

			db = MySQLdb.connect(host=host,user=dbusername,passwd=passwd,db=database)
			sql = db.cursor()
			query = "INSERT INTO catalog (subject_code, course_num, term, CRN, section, credits, instructor, scheduled_days, scheduled_start_time, scheduled_end_time, scheduled_start_date, scheduled_end_date, final_scheduled_day, final_scheduled_start_time, final_scheduled_end_time, final_scheduled_date, location, final_location, campus, type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 
			try:
				sql.execute(query, (table[0], table[1], table[2], table[3], table[4], table[5], table[6], table[7], table[8], table[9], table[10], table[11], table[12], table[13], table[14], table[15], table[16], table[17], table[18], table[19]))
				db.commit()
				#print "inserted"
				#db.close()
			except MySQLdb.Error, e:
				print "Error %d: %s" % (e.args[0], e.args[1])
				db.rollback()
			db.close()
			#file.write("%s\n" % table)
			#INSERT INTO catalog VALUES (0, table[0], table[1], table[2], table[3], table[4], table[5], table[6], table[7], table[8], table[9], table[10], table[11], table[12], table[13], table[14], table[15], table[16], table[17], table[18], table[19], table[20]) 
		except(AttributeError, IndexError):
			break

print "Catalog scrape and insertion complete, moving to finding onid usernames."
#Now begin the updating of the onid username table.  Start by pulling distinct instructor, department combinations from catalog and put those in a list.  Then take the pairs from that list and use them to find the onid username on the search page.  Finally take all three items and use them to build the onid useranme table.

instructor = []
subject = []
usernames = []
#Connect to the database and pull the unique instructor, department tuples.  Following the model set forth in schedule.py
try:
	db = MySQLdb.connect(host=host,user=dbusername,passwd=passwd,db=database)
except MySQLdb.Error, e:
	print "Error %d: %s" % (e.args[0], e.args[1])
	
sql = db.cursor()
#I really don't care what the order is, it just needs to be distinct.  
#query = "SELECT DISTINCT instructor, department, subject_code FROM catalog"
query = "SELECT DISTINCT instructor, subject_code FROM catalog"
sql.execute(query)
#row[0] should be the instructor and row[1] should be the department
for row in sql.fetchall():
	instructor.append(row[0])
	#subject.append(row[2])
	subject.append(row[1])
	
#now that we have all the pairs, we need to rifle through them and use them to create search urls
i = 0
name = ""
surname = ""
department = ""
affiliation = "employee"
#file = open('usernames.txt', 'w')
success = 0
while i < len(subject):
	count = 0
	for chars in instructor[i]:
		if chars == ',':	#%2C for the delimiter
			surname = str(instructor[i][:count])
			name = str(instructor[i][:count]) + "%2C+" + str(instructor[i][count+2:])	
			break
		count += 1
		if count > len(instructor[i]):
			name = str(instructor[i])	#There is no comma for whatever reason.
			break
	#This inserts the comma delimiter
	#If there is no comma, then the surname is not set as the program cannot determine the last name and the last name is not set.
	
	#Next we switch through the subject code to determine what prompt will be used in the department search criteria
	if (subject[i] == "ACTG"):
		department = "business"
	elif (subject[i] == "AEC"):
		department = "economics"
	elif (subject[i] == "AED"):
		department = "agriculture"
	elif (subject[i] == "AG"):
		department = "agriculture"
	elif (subject[i] == "AGRI"):
		department = "agriculture"
	elif (subject[i] == "AHE"):
		department = "education"
	elif (subject[i] == "ALS"):
		department = ""		#Wide variety, from INTO OSU to Public Health.  Just have to do 'best effort matching' using name alone.
	elif (subject[i] == "ANS"):
		department = "animal"
	elif (subject[i] == "ANTH"):
		department = "anthropology"
	elif (subject[i] == "AREC"):
		department = "economics"
	elif (subject[i] == "ART"):
		department = "art"
	elif (subject[i] == "AS"):
		department = "aerospace"
	elif (subject[i] == "ASL"):
		department = "foreign"
	elif (subject[i] == "ATS"):
		department = "earth" #another hard one, the actual department name does not show results, but using a part the with the name works so far.
	elif (subject[i] == "BA"):
		department = "business"
	elif (subject[i] == "BB"):
		department = "Biochem+%2F+Biophysics"
	elif (subject[i] == "BEE"):
		department = "Engineering"
	elif (subject[i] == "BI"):
		department = "biology"
	elif (subject[i] == "BIOE"):
		department = "Chem%2FBio%2FEnvr+Eng"	
	elif (subject[i] == "BOT"):
		department = "botany"
	elif (subject[i] == "BRR"):
		department = "ag"
	elif (subject[i] == "CBEE"):
		department = "Chem%2FBio%2FEnvr+Eng"
	elif (subject[i] == "CCE"):
		department = "civil"
	elif (subject[i] == "CE"):
		department = "civil"
	elif (subject[i] == "CEM"):
		department = "civil"
	elif (subject[i] == "CH"):
		department = "chemistry"
	elif (subject[i] == "CHE"):
		department = "chem"
	elif (subject[i] == "CHN"):
		department = "foreign"
	elif (subject[i] == "COMM"):
		department = "comm"
	elif (subject[i] == "CROP"):
		department = "crop"
	elif (subject[i] == "CS"):
		department = "comp"
	elif (subject[i] == "CSS"):
		department = "ag"
	elif (subject[i] == "DHE"):
		department = "business"
	elif (subject[i] == "ECE"):
		department = "comp"
	elif (subject[i] == "ECON"):
		department = "economics"
	elif (subject[i] == "EECS"):
		department = "comp"
	elif (subject[i] == "ENG"):
		department = "lit"
	elif (subject[i] == "ENGR"):
		department = "engr"
	elif (subject[i] == "ENSC"):
		department = "earth"
	elif (subject[i] == "ENT"):
		department = "crop"
	elif (subject[i] == "ENVE"):
		department = "env"
	elif (subject[i] == "ES"):
		department = "ethnic"
	elif (subject[i] == "EXSS"):
		department = "sport"
	elif (subject[i] == "FE"):	
		department = "forest"
	elif (subject[i] == "FES"):
		department = "forest"
	elif (subject[i] == "FILM"):
		department = "film"
	elif (subject[i] == "FIN"):
		department = "business"
	elif (subject[i] == "FOR"):
		department = "forest"
	elif (subject[i] == "FR"):
		department = "foreign"
	elif (subject[i] == "FS"):
		department = "forest"
	elif (subject[i] == "FST"):
		department = "food"
	elif (subject[i] == "FW"):
		department = "fish"
	elif (subject[i] == "GD"):
		department = "business"
	elif (subject[i] == "GEO"):
		department = "sci"
	elif (subject[i] == "GER"):
		department = "foreign"
	elif (subject[i] == "GPH"):
		department = "sci"
	elif (subject[i] == "GRAD"):
		department = "grad"
	elif (subject[i] == "GS"):
		department = "sci"
	elif (subject[i] == "H"):
		department = "health"
	elif (subject[i] == "HC"):
		department = "honor"
	elif (subject[i] == "HDFS"):
		department = "sci"
	elif (subject[i] == "HHS"):
		department = "sci"
	elif (subject[i] == "HORT"):
		department = "hort"
	elif (subject[i] == "HST"):
		department = "hist"
	elif (subject[i] == "HSTS"):
		department = "hist"
	elif (subject[i] == "IE"):
		department = "engr"
	elif (subject[i] == "IEPA"):
		department = "INTO+OSU"
	elif (subject[i] == "IEPG"):
		department = "INO+OSU"
	elif (subject[i] == "IEPH"):
		department = "INTO+OSU"
	elif (subject[i] == "INTL"):
		department = "int"
	elif (subject[i] == "IST"):	
		department = "pol"
	elif (subject[i] == "IT"):
		department = "foreign"
	elif (subject[i] == "JPN"):
		department = "foreign"
	elif (subject[i] == "LA"):
		department = "lit"
	elif (subject[i] == "LING"):
		department = "foreign"
	elif (subject[i] == "MATS"):
		department = "engr"
	elif (subject[i] == "MB"):
		department = "bio"
	elif (subject[i] == "MCB"):
		department = "bio"
	elif (subject[i] == "ME"):
		department = "engr"
	elif (subject[i] == "MFGE"):
		department = "engr"
	elif (subject[i] == "MGMT"):
		department = "business"
	elif (subject[i] == "MIME"):
		department = "engr"
	elif (subject[i] == "MP"):
		department = "nuc"
	elif (subject[i] == "MPP"):
		department = "pol"
	elif (subject[i] == "MRKT"):
		department = "business"
	elif (subject[i] == "MRM"):
		department = "sea"
	elif (subject[i] == "MS"):
		department = "ROTC"
	elif (subject[i] == "MTH"):
		department = "math"
	elif (subject[i] == "MUED"):
		department = "mus"
	elif (subject[i] == "MUP"):
		department = "mus"
	elif (subject[i] == "MUS"):
		department = "mus"
	elif (subject[i] == "NE"):
		department = "nuc"
	elif (subject[i] == "NMC"):
		department = "comm"
	elif (subject[i] == "NR"):
		department = "forest"
	elif (subject[i] == "NS"):
		department = "ROTC"
	elif (subject[i] == "NUTR"):
		department = "sci"
	elif (subject[i] == "OC"):
		department = "sci"
	elif (subject[i] == "OEAS"):
		department = "sci"
	elif (subject[i] == "PAC"):
		department = "sport"
	elif (subject[i] == "PAX"):
		department = "phil"
	elif (subject[i] == "PBG"):
		department = "hort"
	elif (subject[i] == "PH"):
		department = "physics"
	elif (subject[i] == "PHAR"):
		department = "pharm"
	elif (subject[i] == "PHL"):
		department = "phil"
	elif (subject[i] == "PPOL"):
		department = "pol"
	elif (subject[i] == "PS"):
		department = "pol"
	elif (subject[i] == "PSY"):
		department = "psych"
	elif (subject[i] == "QS"):
		department = "" #hard to classify, art to women's studies should just leave blank.
	elif (subject[i] == "RHP"):
		department = "rad"
	elif (subject[i] == "RNG"):
		department = "animal"
	elif (subject[i] == "RS"):
		department = "econ"
	elif (subject[i] == "RUS"):
		department = "foreign"
	elif (subject[i] == "SED"):
		department = "edu"
	elif (subject[i] == "SNR"):
		department = "forest"
	elif (subject[i] == "SOC"):
		department = "soc"
	elif (subject[i] == "SOIL"):
		department = "sci"
	elif (subject[i] == "SPAN"):
		department = "foreign"
	elif (subject[i] == "ST"):
		department = "stat"
	elif (subject[i] == "SUS"):
		department = "crop"
	elif (subject[i] == "TA"):
		department = "comm"
	elif (subject[i] == "TCE"):
		department = "edu"
	elif (subject[i] == "TOX"):
		department = "toxic"
	elif (subject[i] == "VMB"):
		department = "vet"
	elif (subject[i] == "VMC"):
		department = "vet"
	elif (subject[i] == "WGSS"):
		department = "women"
	elif (subject[i] == "WLC"):
		department = "foreign"
	elif (subject[i] == "WR"):
		department = "lit"
	elif (subject[i] == "WRE"):
		department = ""
	elif (subject[i] == "WRP"):
		department = ""
	elif (subject[i] == "WRS"):
		department = "sci"
	elif (subject[i] == "WSE"):
		department = "sci"
	elif (subject[i] == "Z"):
		department = "zoo"
	else:
		department = ""

	#now we build the url with the following parts, name, surname, department, and affiliation
	url = "http://directory.oregonstate.edu/?type=search&cn="+name+"&surname="+surname+"&mail=&telephonenumber=&osualtphonenumber=&homephone=&facsimiletelephonenumber=&osuofficeaddress=&osudepartment="+department+"&affiliation="+affiliation+"&anyphone=&join=and"
	#print url
	username = "NOT FOUND"
	Valid = False
	try:	
		html = urllib2.urlopen(url).read()
		soup = BeautifulSoup(html)
		soup2 = soup.body.div.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.div.dl.find_all()
		
		if (str(soup2[len(soup2)-2])[3:len(str(soup2[len(soup2)-2]))-4] == "ONID Username"):
			Valid = True
			success += 1
		#print "%s" % Valid
		#print(str(soup2[len(soup2)-2])[3:len(str(soup2[len(soup2)-2]))-4])
		username = str(soup2[len(soup2)-1])[4:len(str(soup2[len(soup2)-1]))-5]
		
		#Second check, this time without the department
		if Valid == False:
			url = "http://directory.oregonstate.edu/?type=search&cn="+name+"&surname="+surname+"&mail=&telephonenumber=&osualtphonenumber=&homephone=&facsimiletelephonenumber=&osuofficeaddress=&osudepartment=&affiliation="+affiliation+"&anyphone=&join=and"
			html = urllib2.urlopen(url).read()
			soup = BeautifulSoup(html)
			soup2 = soup.body.div.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.div.dl.find_all()
			
			if (str(soup2[len(soup2)-2])[3:len(str(soup2[len(soup2)-2]))-4] == "ONID Username"):
				Valid = True
				success += 1
			#print "%s" % Valid
			#print(str(soup2[len(soup2)-2])[3:len(str(soup2[len(soup2)-2]))-4])
			username = str(soup2[len(soup2)-1])[4:len(str(soup2[len(soup2)-1]))-5]
		#Third check, this time with department and without the employee affiliation
		if Valid == False:
			url = "http://directory.oregonstate.edu/?type=search&cn="+name+"&surname="+surname+"&mail=&telephonenumber=&osualtphonenumber=&homephone=&facsimiletelephonenumber=&osuofficeaddress=&osudepartment="+department+"&affiliation=&anyphone=&join=and"
			html = urllib2.urlopen(url).read()
			soup = BeautifulSoup(html)
			soup2 = soup.body.div.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.div.dl.find_all()
			
			if (str(soup2[len(soup2)-2])[3:len(str(soup2[len(soup2)-2]))-4] == "ONID Username"):
				Valid = True
				success += 1
			#print "%s" % Valid
			#print(str(soup2[len(soup2)-2])[3:len(str(soup2[len(soup2)-2]))-4])
			username = str(soup2[len(soup2)-1])[4:len(str(soup2[len(soup2)-1]))-5]
			
		#Fourth check, this time without department and without the employee affiliation
		if Valid == False:
			url = "http://directory.oregonstate.edu/?type=search&cn="+name+"&surname="+surname+"&mail=&telephonenumber=&osualtphonenumber=&homephone=&facsimiletelephonenumber=&osuofficeaddress=&osudepartment=&affiliation=&anyphone=&join=and"
			html = urllib2.urlopen(url).read()
			soup = BeautifulSoup(html)
			soup2 = soup.body.div.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.div.dl.find_all()
			
			if (str(soup2[len(soup2)-2])[3:len(str(soup2[len(soup2)-2]))-4] == "ONID Username"):
				Valid = True
				success += 1
			#print "%s" % Valid
			#print(str(soup2[len(soup2)-2])[3:len(str(soup2[len(soup2)-2]))-4])
			username = str(soup2[len(soup2)-1])[4:len(str(soup2[len(soup2)-1]))-5]
		
	except AttributeError:
		pass
		#print "Not a valid search"
		
	db = MySQLdb.connect(host=host,user=dbusername,passwd=passwd,db=database)
	sql = db.cursor()
	query = "INSERT INTO usernames (instructor, department, username) VALUES (%s, %s, %s)" 
	try:
		sql.execute(query, (instructor[i], subject[i], username))
		db.commit()
		#print "inserted"
		#db.close()
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		db.rollback()
	db.close()
	
	#file.write("name:%s, surname:%s, department:%s, affiliation:%s, valid:%s, username:%s\n" % (name, surname, department, affiliation, Valid, username))
	#if i%100 == 0:
		#print str(i)+" of "+str(len(subject))
	i += 1
	
#print "Name and simple department returns %d of %d records" % (success, len(subject))   1475 out of 2341, well that's a lot worse than I found through random checking.  Going to insert the values into a database and check how many unique instructors are without ONID IDs.