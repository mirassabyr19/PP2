import psycopg2
from config import load_config


def connect():
    conn = None
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        print("Connected to PostgreSQL")
        return conn
    except Exception as error:
        print("Error:", error)
        return None