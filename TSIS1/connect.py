import psycopg2
from config import load_config


def connect():
    """Create and return a PostgreSQL connection."""
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        return conn
    except Exception as error:
        print("Database connection error:", error)
        return None


if __name__ == "__main__":
    connection = connect()
    if connection:
        print("Connected to PostgreSQL")
        connection.close()
