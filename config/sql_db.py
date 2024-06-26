import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv('DATABASE_URL')

def create_sql_connection():
    conn = psycopg2.connect(database_url)
    return conn