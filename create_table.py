import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    db="insideOut")

my_cursor = mydb.cursor() 
my_cursor.execute("CREATE TABLE USERS (uid INT PRIMARY KEY, name varchar(100), phone INT, DOB date, email varchar(100), password varchar(100), userType varchar(100)")

my_cursor.execute("SELECT * FROM TAB")
for tables in my_cursor:
    print(tables)