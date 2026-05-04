import csv
import json
import os
from datetime import date, datetime

from connect import connect


PHONE_TYPES = {"home", "work", "mobile"}
DEFAULT_GROUP = "Other"


# ---------- Helper functions ----------

def run_sql_file(cur, filename):
    """Execute an SQL file such as schema.sql or procedures.sql."""
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "r", encoding="utf-8") as file:
        cur.execute(file.read())


def init_database(conn):
    """Create/update tables, groups, procedures, and functions."""
    with conn.cursor() as cur:
        run_sql_file(cur, "schema.sql")
        run_sql_file(cur, "procedures.sql")
    conn.commit()
    print("Database schema, procedures, and functions are ready.")


def normalize_phone_type(phone_type):
    """Return a valid phone type. Default value is mobile."""
    phone_type = (phone_type or "mobile").strip().lower()
    if phone_type not in PHONE_TYPES:
        raise ValueError("Phone type must be home, work, or mobile")
    return phone_type


def normalize_birthday(value):
    """Convert an empty birthday to None and validate YYYY-MM-DD format."""
    value = (value or "").strip()
    if not value:
        return None

    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise ValueError("Birthday must be in YYYY-MM-DD format")


def value_to_string(value):
    """Convert date/datetime/None values to readable strings."""
    if value is None:
        return "-"
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def get_group_id(cur, group_name):
    """Find a group id. Create the group if it does not exist."""
    group_name = (group_name or DEFAULT_GROUP).strip() or DEFAULT_GROUP
    group_name = group_name.title()

    cur.execute(
        "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )
    cur.execute("SELECT id FROM groups WHERE lower(name) = lower(%s)", (group_name,))
    row = cur.fetchone()
    return row[0]


def find_contact_id(cur, name):
    """Find a contact by name. Name is used for duplicate detection."""
    cur.execute(
        "SELECT id FROM contacts WHERE lower(name) = lower(%s) ORDER BY id LIMIT 1",
        (name.strip(),)
    )
    row = cur.fetchone()
    return row[0] if row else None


def save_contact(cur, name, email=None, birthday=None, group_name=None, phones=None, overwrite=False):
    """Insert a new contact or overwrite an existing contact with the same name."""
    name = (name or "").strip()
    if not name:
        raise ValueError("Contact name cannot be empty")

    email = (email or "").strip() or None
    birthday = normalize_birthday(birthday)
    group_id = get_group_id(cur, group_name)
    phones = phones or []

    existing_id = find_contact_id(cur, name)

    if existing_id and not overwrite:
        return existing_id, False

    if existing_id and overwrite:
        cur.execute(
            """
            UPDATE contacts
            SET email = %s, birthday = %s, group_id = %s
            WHERE id = %s
            """,
            (email, birthday, group_id, existing_id)
        )
        cur.execute("DELETE FROM phones WHERE contact_id = %s", (existing_id,))
        contact_id = existing_id
    else:
        cur.execute(
            """
            INSERT INTO contacts (name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, email, birthday, group_id)
        )
        contact_id = cur.fetchone()[0]

    for item in phones:
        phone = str(item.get("phone", "")).strip()
        phone_type = normalize_phone_type(item.get("type", "mobile"))
        if phone:
            cur.execute(
                """
                INSERT INTO phones (contact_id, phone, type)
                VALUES (%s, %s, %s)
                ON CONFLICT (contact_id, phone)
                DO UPDATE SET type = EXCLUDED.type
                """,
                (contact_id, phone, phone_type)
            )

    return contact_id, True


def display_rows(rows):
    """Print rows returned by search_contacts or get_contacts_paginated."""
    if not rows:
        print("No contacts found.")
        return

    for i, row in enumerate(rows, start=1):
        contact_id, name, email, birthday, group_name, phones, created_at = row
        print(
            f"{i}. ID: {contact_id} | Name: {name} | Email: {value_to_string(email)} | "
            f"Birthday: {value_to_string(birthday)} | Group: {value_to_string(group_name)} | "
            f"Phones: {value_to_string(phones)} | Added: {value_to_string(created_at)}"
        )


# ---------- Console actions ----------

def add_contact_console(conn):
    """Add one contact with email, birthday, group, and first phone number."""
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD or empty): ")
    group_name = input("Group (Family/Work/Friend/Other): ")
    phone = input("Phone number: ")
    phone_type = input("Phone type (home/work/mobile): ") or "mobile"

    with conn.cursor() as cur:
        existing_id = find_contact_id(cur, name)
        overwrite = False
        if existing_id:
            answer = input("Contact with this name exists. Overwrite? [y/n]: ").strip().lower()
            overwrite = answer == "y"
            if not overwrite:
                print("Skipped.")
                return

        save_contact(
            cur,
            name=name,
            email=email,
            birthday=birthday,
            group_name=group_name,
            phones=[{"phone": phone, "type": phone_type}],
            overwrite=overwrite
        )
    conn.commit()
    print("Contact saved.")


def show_all_contacts(conn):
    """Show all contacts by using the extended search function with an empty query."""
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", ("",))
        display_rows(cur.fetchall())


def add_phone_procedure(conn):
    """Use the add_phone stored procedure."""
    name = input("Contact name: ")
    phone = input("New phone number: ")
    phone_type = input("Phone type (home/work/mobile): ") or "mobile"

    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
    conn.commit()
    print("Phone number added.")


def move_to_group_procedure(conn):
    """Use the move_to_group stored procedure."""
    name = input("Contact name: ")
    group_name = input("New group name: ")

    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
    conn.commit()
    print("Contact moved to group.")


def search_all_fields(conn):
    """Search by name, email, birthday, group, phone, or phone type."""
    query = input("Search query: ")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        display_rows(cur.fetchall())


def filter_by_group(conn):
    """Show contacts from one group/category."""
    group_name = input("Group name: ")
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM search_contacts(%s)
            WHERE lower(group_name) = lower(%s)
            """,
            ("", group_name)
        )
        display_rows(cur.fetchall())


def search_by_email(conn):
    """Partial email search, for example gmail returns Gmail contacts."""
    keyword = input("Email keyword: ")
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM search_contacts(%s)
            WHERE email ILIKE %s
            """,
            ("", f"%{keyword}%")
        )
        display_rows(cur.fetchall())


def sort_contacts(conn):
    """Sort output by name, birthday, or date added."""
    print("Sort by: 1) name  2) birthday  3) date added")
    choice = input("Choose: ").strip()

    order_map = {
        "1": "contact_name ASC",
        "2": "birthday ASC NULLS LAST, contact_name ASC",
        "3": "created_at ASC, contact_name ASC"
    }
    order_by = order_map.get(choice)

    if order_by is None:
        print("Invalid sort option.")
        return

    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM search_contacts(%s) ORDER BY {order_by}", ("",))
        display_rows(cur.fetchall())


def paginated_navigation(conn):
    """Navigate pages using the DB function get_contacts_paginated(limit, offset)."""
    try:
        limit = int(input("Page size: "))
    except ValueError:
        print("Page size must be a number.")
        return

    offset = 0

    while True:
        print(f"\n--- Page offset: {offset} ---")
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
            rows = cur.fetchall()
            display_rows(rows)

        command = input("Command [next/prev/quit]: ").strip().lower()
        if command == "next":
            if rows:
                offset += limit
            else:
                print("No next page.")
        elif command == "prev":
            offset = max(0, offset - limit)
        elif command == "quit":
            break
        else:
            print("Unknown command.")


def export_to_json(conn):
    """Export all contacts with groups and multiple phones to a JSON file."""
    filename = input("Output JSON filename [contacts_export.json]: ").strip() or "contacts_export.json"

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday, g.name AS group_name, c.created_at
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY c.name
            """
        )
        contacts = cur.fetchall()

        result = []
        for contact in contacts:
            contact_id, name, email, birthday, group_name, created_at = contact
            cur.execute(
                "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
                (contact_id,)
            )
            phones = [{"phone": row[0], "type": row[1]} for row in cur.fetchall()]

            result.append({
                "name": name,
                "email": email,
                "birthday": birthday.isoformat() if birthday else None,
                "group": group_name,
                "created_at": created_at.isoformat(sep=" ", timespec="seconds") if created_at else None,
                "phones": phones
            })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print(f"Exported {len(result)} contacts to {filename}.")


def import_from_json(conn):
    """Import contacts from JSON and handle duplicate names."""
    filename = input("Input JSON filename: ").strip()
    if not filename:
        print("Filename is required.")
        return

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    inserted = 0
    skipped = 0

    with conn.cursor() as cur:
        for item in data:
            name = item.get("name", "").strip()
            if not name:
                skipped += 1
                continue

            existing_id = find_contact_id(cur, name)
            overwrite = False
            if existing_id:
                answer = input(f"Duplicate contact '{name}'. [s]kip or [o]verwrite? ").strip().lower()
                if answer == "o":
                    overwrite = True
                else:
                    skipped += 1
                    continue

            save_contact(
                cur,
                name=name,
                email=item.get("email"),
                birthday=item.get("birthday"),
                group_name=item.get("group"),
                phones=item.get("phones", []),
                overwrite=overwrite
            )
            inserted += 1

    conn.commit()
    print(f"JSON import finished. Inserted/updated: {inserted}. Skipped: {skipped}.")


def parse_csv_row(row, header=None):
    """Parse both old and extended CSV formats."""
    if header:
        lower_header = [h.strip().lower() for h in header]
        data = dict(zip(lower_header, row))
        return {
            "name": data.get("name", ""),
            "email": data.get("email", ""),
            "birthday": data.get("birthday", ""),
            "group": data.get("group", DEFAULT_GROUP),
            "phones": [{
                "phone": data.get("phone", ""),
                "type": data.get("type", "mobile")
            }]
        }

    # Old Practice 7 format: name, phone
    if len(row) == 2:
        return {
            "name": row[0],
            "email": "",
            "birthday": "",
            "group": DEFAULT_GROUP,
            "phones": [{"phone": row[1], "type": "mobile"}]
        }

    # Extended format without header: name,email,birthday,group,phone,type
    if len(row) >= 6:
        return {
            "name": row[0],
            "email": row[1],
            "birthday": row[2],
            "group": row[3],
            "phones": [{"phone": row[4], "type": row[5]}]
        }

    raise ValueError("CSV row must have either 2 columns or 6 columns")


def import_from_csv(conn):
    """Import contacts from CSV with new fields: email, birthday, group, phone type."""
    filename = input("CSV filename [contacts.csv]: ").strip() or "contacts.csv"

    with open(filename, "r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file))

    if not rows:
        print("CSV file is empty.")
        return

    first_row = [cell.strip().lower() for cell in rows[0]]
    has_header = "name" in first_row and "phone" in first_row
    header = rows[0] if has_header else None
    data_rows = rows[1:] if has_header else rows

    inserted = 0
    skipped = 0

    with conn.cursor() as cur:
        for row in data_rows:
            if not row or all(not cell.strip() for cell in row):
                continue

            item = parse_csv_row(row, header)
            name = item["name"].strip()
            if not name:
                skipped += 1
                continue

            existing_id = find_contact_id(cur, name)
            overwrite = False
            if existing_id:
                answer = input(f"Duplicate contact '{name}'. [s]kip or [o]verwrite? ").strip().lower()
                if answer == "o":
                    overwrite = True
                else:
                    skipped += 1
                    continue

            save_contact(
                cur,
                name=name,
                email=item["email"],
                birthday=item["birthday"],
                group_name=item["group"],
                phones=item["phones"],
                overwrite=overwrite
            )
            inserted += 1

    conn.commit()
    print(f"CSV import finished. Inserted/updated: {inserted}. Skipped: {skipped}.")


def delete_contact(conn):
    """Delete a contact by name. Phones are deleted automatically by ON DELETE CASCADE."""
    name = input("Contact name to delete: ")
    with conn.cursor() as cur:
        cur.execute("DELETE FROM contacts WHERE lower(name) = lower(%s)", (name,))
        deleted = cur.rowcount
    conn.commit()
    print(f"Deleted contacts: {deleted}")


# ---------- Main menu ----------

def menu():
    conn = connect()
    if conn is None:
        return

    while True:
        print("\n========== TSIS 1 PhoneBook ==========")
        print("0) Initialize database schema/procedures")
        print("1) Add contact")
        print("2) Show all contacts")
        print("3) Add phone to existing contact (procedure add_phone)")
        print("4) Move contact to group (procedure move_to_group)")
        print("5) Search all fields (function search_contacts)")
        print("6) Filter by group")
        print("7) Search by email")
        print("8) Sort by name / birthday / date added")
        print("9) Paginated navigation next / prev / quit")
        print("10) Export contacts to JSON")
        print("11) Import contacts from JSON")
        print("12) Import contacts from CSV")
        print("13) Delete contact")
        print("14) Exit")

        choice = input("Choose: ").strip()

        try:
            if choice == "0":
                init_database(conn)
            elif choice == "1":
                add_contact_console(conn)
            elif choice == "2":
                show_all_contacts(conn)
            elif choice == "3":
                add_phone_procedure(conn)
            elif choice == "4":
                move_to_group_procedure(conn)
            elif choice == "5":
                search_all_fields(conn)
            elif choice == "6":
                filter_by_group(conn)
            elif choice == "7":
                search_by_email(conn)
            elif choice == "8":
                sort_contacts(conn)
            elif choice == "9":
                paginated_navigation(conn)
            elif choice == "10":
                export_to_json(conn)
            elif choice == "11":
                import_from_json(conn)
            elif choice == "12":
                import_from_csv(conn)
            elif choice == "13":
                delete_contact(conn)
            elif choice == "14":
                break
            else:
                print("Invalid choice.")
        except Exception as error:
            print("Error:", error)
            conn.rollback()

    conn.close()


if __name__ == "__main__":
    menu()
