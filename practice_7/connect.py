import psycopg2
from config import load_config


def connect(config):
    try:
        with psycopg2.connect(**config) as conn:
            print("Connected to PostgreSQL")

            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                print(cur.fetchone())

    except Exception as e:
        print(e)


if __name__ == "__main__":
    config = load_config()
    connect(config)