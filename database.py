from pymongo import MongoClient
import os

def database():
    try:
        client = MongoClient(os.environ.get('DB_LINK'), serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        mydb = client['password_manager']
        print("connection succesfull")
        return mydb
    
    except Exception as e:
        print(f"Connection failed: \n{e}")
        return
