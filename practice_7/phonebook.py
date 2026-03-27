import psycopg2
import csv
from config import load_config


def create_table():
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    phone TEXT
                );
            """)


def insert_from_csv(filename):
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    cur.execute(
                        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                        (row[0], row[1])
                    )


def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (name, phone)
            )


def update_contact():
    name = input("Enter name to update: ")
    new_phone = input("Enter new phone: ")

    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE phonebook SET phone=%s WHERE name=%s",
                (new_phone, name)
            )


def query_contacts():
    keyword = input("Enter name or phone prefix: ")

    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM phonebook WHERE name ILIKE %s OR phone LIKE %s",
                (f"%{keyword}%", f"{keyword}%")
            )
            rows = cur.fetchall()

            for row in rows:
                print(row)


def delete_contact():
    name = input("Enter name to delete: ")

    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM phonebook WHERE name=%s",
                (name,)
            )


def menu():
    create_table()

    while True:
        print("\n1.Insert CSV")
        print("2.Insert console")
        print("3.Update")
        print("4.Query")
        print("5.Delete")
        print("6.Exit")

        choice = input("Choose: ")

        if choice == '1':
            insert_from_csv("contacts.csv")
        elif choice == '2':
            insert_from_console()
        elif choice == '3':
            update_contact()
        elif choice == '4':
            query_contacts()
        elif choice == '5':
            delete_contact()
        elif choice == '6':
            break


if __name__ == "__main__":
    menu()