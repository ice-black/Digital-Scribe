host_name = "localhost"
user_name = "root"
password_key = "12hezron12"
database_name = "hostel"
import mysql.connector

mydb = mysql.connector.connect(
host=host_name,
user=user_name,
password=password_key,
database=database_name
)
mycursor = mydb.cursor()

mycursor.execute(
f"""
                            
                            
""")
mydb.commit()

