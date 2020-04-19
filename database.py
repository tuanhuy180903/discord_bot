import sqlite3
import time

#Create data
def createdb(name, tbname):
    """Create a new database named <name>"""
    connection = sqlite3.connect(name) 
    crsr = connection.cursor()
    if tbname == 'student':
        crsr.execute(f"""CREATE TABLE IF NOT EXISTS student (  
        name TEXT NOT NULL,
        class TEXT NOT NULL);""")
    elif tbname == 'teacher':
        crsr.execute(f"""CREATE TABLE IF NOT EXISTS teacher (  
        name TEXT NOT NULL PRIMARY KEY);""")
    connection.commit()
    connection.close()

#Insert data
def writedb(db_name, name, class_name, tbname):
    """Write data to db"""
    connection = sqlite3.connect(db_name) 
    crsr = connection.cursor() 
    #current_time = int(time.time()) 
    crsr.execute(f"INSERT INTO {tbname} VALUES (?, ?)",
        (name, class_name) )
        # time         sensor name  temp  humid
    connection.commit()
    connection.close()

#Fetching data
def fetch(paraname, dbname):
    """fetching colums data from database
    connect with the myTable database """
    connection = sqlite3.connect(dbname) 
# cursor object 
    crsr = connection.cursor() 
# execute the command to fetch all the data from the table emp 
    crsr.execute(f"SELECT {paraname} FROM student") 
# store all the fetched data in the ans variable 
    ans= crsr.fetchall() 
# loop to print all the data
    x=[]
    for i in ans: 
	    x.append(i)
    return x 

'''createdb('bot.db','student')
writedb('bot.db','asd','eeit2017','student')
writedb('bot.db','fef','eeit2017','student')
print(fetch('name','bot.db'))'''



