from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
mongo_conn = client.get_database("etL_practise")