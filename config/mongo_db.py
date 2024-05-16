from pymongo import MongoClient, ssl_support
import os
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=True)

try:
    mongo_conn = client.get_database("etL_practise")
    print("Connection successful")
    print(mongo_conn.list_collection_names())
except Exception as e:
    print(f"Connection failed: {e}")