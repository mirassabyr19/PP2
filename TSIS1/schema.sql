-- TSIS 1: PhoneBook — Extended Contact Management
-- This schema extends the previous contacts table with groups, email, birthday,
-- multiple phone numbers, and date-added information.

CREATE TABLE IF NOT EXISTS groups (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO groups (name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS contacts (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100),
    birthday    DATE,
    group_id    INTEGER REFERENCES groups(id),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migration support for older Practice 7/8 contacts tables.
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS email VARCHAR(100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS birthday DATE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES groups(id);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS phones (
    id          SERIAL PRIMARY KEY,
    contact_id  INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone       VARCHAR(20) NOT NULL,
    type        VARCHAR(10) NOT NULL CHECK (type IN ('home', 'work', 'mobile')),
    UNIQUE (contact_id, phone)
);

-- If the old contacts table still has a single phone column, copy those old
-- phone numbers into the new phones table once.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'contacts'
          AND column_name = 'phone'
    ) THEN
        INSERT INTO phones (contact_id, phone, type)
        SELECT c.id, c.phone::VARCHAR(20), 'mobile'
        FROM contacts c
        WHERE c.phone IS NOT NULL
          AND c.phone::TEXT <> ''
          AND NOT EXISTS (
              SELECT 1
              FROM phones p
              WHERE p.contact_id = c.id
                AND p.phone = c.phone::VARCHAR(20)
          );
    END IF;
END $$;
