from pymongo import MongoClient

def database():
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        mydb = client['password_manager']
        print("connection succesfull")
        return mydb
    
    except Exception as e:
        print(f"Connection failed: {e}")
        return
