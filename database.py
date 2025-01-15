import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="user1",
        password="112233",
        database="socialmediadb"
    )
