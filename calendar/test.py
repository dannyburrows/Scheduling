from calendarAPI import person

user = person("burrows.danny@gmail.com")
user.findAvailbility("04/10/2014 08:30", "04/10/2014 15:00")
user.listAvailabilities()  

newUser = person("jjames83@gmail.com")
newUser.findAvailbility("04/10/2014 08:30", "04/10/2014 15:00")
newUser.listAvailabilities()  