#!

import MySQLdb
import ConfigParser

config = ConfigParser.RawConfigParser()

config.read('sql_config.ini')
host = config.get('SQL','host')
db = config.get('SQL','db')
user = config.get('SQL','user')
passwd = config.get('SQL','pass')
# host = config.get('host')

# print host

db = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db)

cur = db.cursor()

users=[ 'burrows.danny@gmail.com', 'jonesjo@onid.oregonstate.edu']

for user in users:
	query="SELECT user_name FROM person WHERE user_name=" + user
	cur.execute(query)
	for row in cur.fetchall():
		print row[1] # only the user name is returned