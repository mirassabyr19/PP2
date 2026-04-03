from connect import connect


def add_contact(cur):
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    cur.execute("CALL insert_or_update_user(%s, %s)", (name, phone))


def show_contacts(cur):
    cur.execute("SELECT name, surname, phone FROM contacts")
    rows = cur.fetchall()
    print_rows(rows)


def update_phone(cur):
    name = input("Enter name: ")
    phone = input("Enter new phone: ")
    cur.execute("CALL insert_or_update_user(%s, %s)", (name, phone))


def update_name(cur):
    old_name = input("Enter old name: ")
    new_name = input("Enter new name: ")
    cur.execute("UPDATE contacts SET name=%s WHERE name=%s", (new_name, old_name))


def delete_contact(cur):
    value = input("Enter name or phone: ")
    cur.execute("CALL delete_contact(%s)", (value,))


def search_by_name(cur):
    name = input("Enter name: ")
    cur.execute("SELECT * FROM search_contacts(%s)", (name,))
    rows = cur.fetchall()
    print_rows(rows)


def search_by_phone(cur):
    phone = input("Enter phone: ")
    cur.execute("SELECT * FROM search_contacts(%s)", (phone,))
    rows = cur.fetchall()
    print_rows(rows)


def search_by_prefix(cur):
    prefix = input("Enter phone prefix: ")
    cur.execute(
        "SELECT name, surname, phone FROM contacts WHERE phone LIKE %s",
        (prefix + "%",)
    )
    rows = cur.fetchall()
    print_rows(rows)


def show_paginated(cur):
    limit = int(input("Enter limit: "))
    offset = int(input("Enter offset: "))
    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    rows = cur.fetchall()
    print_rows(rows)


def print_rows(rows):
    if not rows:
        print("No data found")
        return

    for i, row in enumerate(rows, start=1):
        # row = (name, surname, phone)
        if len(row) == 3:
            name, surname, phone = row
        else:
            name, phone = row
            surname = ""

        print(f"{i}. Name: {name} | Surname: {surname} | Phone: {phone}")


def main():
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()

    while True:
        print("\n1) Add")
        print("2) Show")
        print("3) Update phone number")
        print("4) Update name")
        print("5) Delete")
        print("6) Search by name")
        print("7) Search by phone")
        print("8) Search by phone prefix")
        print("9) Pagination")
        print("10) Exit")

        choice = input("Choose: ")

        try:
            if choice == "1":
                add_contact(cur)
            elif choice == "2":
                show_contacts(cur)
            elif choice == "3":
                update_phone(cur)
            elif choice == "4":
                update_name(cur)
            elif choice == "5":
                delete_contact(cur)
            elif choice == "6":
                search_by_name(cur)
            elif choice == "7":
                search_by_phone(cur)
            elif choice == "8":
                search_by_prefix(cur)
            elif choice == "9":
                show_paginated(cur)
            elif choice == "10":
                break
            else:
                print("Invalid choice")

            conn.commit()

        except Exception as e:
            print("Error:", e)
            conn.rollback()

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()