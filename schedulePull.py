from bs4 import BeautifulSoup
import urllib2
import MySQLdb
import sys
#This is the generic website for searching all the available classes offered by OSU
html = urllib2.urlopen("http://catalog.oregonstate.edu/SOCSearcher.aspx?wks=&chr=abcder").read()

soup = BeautifulSoup(html)

#database information:
host = 'mysql.cs.orst.edu'
username = 'cs419_group2'
passwd = 'bwQR2TY4D4jfAnCZ'
database = 'cs419_group2'



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
	dept = soup.body.a.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.a.get_text()
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
			table.append(str(dept[11:]))
			
			#Now we have all the information, we just need to put in in the table catalog

			db = MySQLdb.connect(host=host,user=username,passwd=passwd,db=database)
			sql = db.cursor()
			query = "INSERT INTO catalog (subject_code, course_num, term, CRN, section, credits, instructor, scheduled_days, scheduled_start_time, scheduled_end_time, scheduled_start_date, scheduled_end_date, final_scheduled_day, final_scheduled_start_time, final_scheduled_end_time, final_scheduled_date, location, final_location, campus, type, department) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" 
			try:
				sql.execute(query, (table[0], table[1], table[2], table[3], table[4], table[5], table[6], table[7], table[8], table[9], table[10], table[11], table[12], table[13], table[14], table[15], table[16], table[17], table[18], table[19], table[20]))
				db.commit()
			except MySQLdb.Error, e:
				print "Error %d: %s" % (e.args[0], e.args[1])
				#from: http://zetcode.com/db/mysqlpython/
				#print "MySQL error"
				db.rollback()
			db.close()
			#file.write("%s\n" % table)
			#INSERT INTO catalog VALUES (0, table[0], table[1], table[2], table[3], table[4], table[5], table[6], table[7], table[8], table[9], table[10], table[11], table[12], table[13], table[14], table[15], table[16], table[17], table[18], table[19], table[20]) 
		except(AttributeError, IndexError):
			break