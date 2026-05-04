# TSIS 1: PhoneBook — Extended Contact Management

## Objective
This project extends the Practice 7 and Practice 8 PhoneBook application with:

- an extended relational database model;
- multiple phone numbers per contact;
- contact email and birthday;
- contact groups/categories;
- advanced console search and filtering;
- JSON import/export;
- extended CSV import;
- new PostgreSQL stored procedures and functions.

## Project structure

```text
TSIS1/
├── phonebook.py
├── config.py
├── connect.py
├── schema.sql
├── procedures.sql
├── contacts.csv
├── sample_import.json
├── database.ini
└── database.example.ini
```

## Database model

### groups
Stores contact categories:

- Family
- Work
- Friend
- Other

### contacts
Stores main contact information:

- id
- name
- email
- birthday
- group_id
- created_at

### phones
Stores multiple phone numbers for each contact:

- id
- contact_id
- phone
- type: home, work, or mobile

The relation between `contacts` and `phones` is one-to-many: one contact can have many phone numbers.

## How to run

1. Install dependency:

```bash
pip install psycopg2-binary
```

2. Edit `database.ini` and write your PostgreSQL password/database name.

3. Run the program:

```bash
python phonebook.py
```

4. In the menu, choose:

```text
0) Initialize database schema/procedures
```

This creates/updates the schema and creates the stored procedures/functions.

## Main features

### Updated schema
The project creates:

- `groups` table;
- `phones` table;
- `email` field in `contacts`;
- `birthday` field in `contacts`;
- `group_id` foreign key in `contacts`.

### Console search and filter
The console supports:

- filter by group;
- search by email using partial match;
- sort by name, birthday, or date added;
- paginated navigation with `next`, `prev`, and `quit`.

### Import / export
The project supports:

- export contacts to JSON;
- import contacts from JSON;
- duplicate handling during JSON import: skip or overwrite;
- extended CSV import with `email`, `birthday`, `group`, `phone`, and `type`.

### New server-side objects
`procedures.sql` contains:

- `add_phone(p_contact_name, p_phone, p_type)`;
- `move_to_group(p_contact_name, p_group_name)`;
- `search_contacts(p_query)`;
- `get_contacts_paginated(lim, off)` for console pagination.

## Defense explanation

### Why separate `phones` table?
A contact can have more than one phone number. If phone numbers are stored directly in the `contacts` table, the structure becomes limited. A separate `phones` table creates a one-to-many relation: one contact can have many phones.

### Why use foreign keys?
Foreign keys connect tables and keep data consistent. For example, `phones.contact_id` references `contacts.id`, so every phone number belongs to a real contact.

### Why `ON DELETE CASCADE`?
If a contact is deleted, all phone numbers of this contact are also deleted automatically. This prevents orphan phone records.

### Why use stored procedures?
Stored procedures move important database logic to PostgreSQL. For example, `add_phone` validates phone type and adds the number directly on the database side.

### Why use `%s` placeholders?
`%s` placeholders safely pass values to SQL queries. This is safer than string formatting because it helps prevent SQL injection.
