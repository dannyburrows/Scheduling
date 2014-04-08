#

import MySQLdb

db = MySQLdb.connect(host="oniddb.cws.oregonstate.edu",user="burrowsd-db",passwd="Pv1h12MLwduJsopk",db="burrowsd-db")

#cur = db.cursor()

# cur.execute("SELECT * FROM teams")

# for row in cur.fetchall():
# 	print row

print "End"