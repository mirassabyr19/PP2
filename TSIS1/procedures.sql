-- TSIS 1: New server-side objects for the extended phonebook.

CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_type VARCHAR(10);
BEGIN
    v_type := lower(trim(p_type));

    IF v_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Phone type must be home, work, or mobile';
    END IF;

    IF p_phone IS NULL OR trim(p_phone) = '' THEN
        RAISE EXCEPTION 'Phone number cannot be empty';
    END IF;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE lower(name) = lower(trim(p_contact_name))
    ORDER BY id
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, trim(p_phone), v_type)
    ON CONFLICT (contact_id, phone)
    DO UPDATE SET type = EXCLUDED.type;
END;
$$;


CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
    v_group_name VARCHAR(50);
BEGIN
    v_group_name := initcap(trim(p_group_name));

    IF v_group_name IS NULL OR v_group_name = '' THEN
        RAISE EXCEPTION 'Group name cannot be empty';
    END IF;

    INSERT INTO groups (name)
    VALUES (v_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE lower(name) = lower(v_group_name)
    LIMIT 1;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE lower(name) = lower(trim(p_contact_name))
    ORDER BY id
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;
END;
$$;


CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    contact_id INTEGER,
    contact_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id AS contact_id,
        c.name AS contact_name,
        c.email,
        c.birthday,
        COALESCE(g.name, 'No group')::VARCHAR AS group_name,
        COALESCE(
            string_agg(DISTINCT p.phone || ' (' || p.type || ')', ', '),
            'No phones'
        ) AS phones,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        p_query IS NULL
        OR trim(p_query) = ''
        OR c.name ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR CAST(c.birthday AS TEXT) ILIKE '%' || p_query || '%'
        OR CAST(c.created_at AS TEXT) ILIKE '%' || p_query || '%'
        OR g.name ILIKE '%' || p_query || '%'
        OR p.phone ILIKE '%' || p_query || '%'
        OR p.type ILIKE '%' || p_query || '%'
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.name;
END;
$$;


-- Practice 8-style pagination function. It is included so the project works
-- from a clean database, and the Python console uses it with next/prev/quit.
CREATE OR REPLACE FUNCTION get_contacts_paginated(lim INT, off INT)
RETURNS TABLE(
    contact_id INTEGER,
    contact_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id AS contact_id,
        c.name AS contact_name,
        c.email,
        c.birthday,
        COALESCE(g.name, 'No group')::VARCHAR AS group_name,
        COALESCE(
            string_agg(DISTINCT p.phone || ' (' || p.type || ')', ', '),
            'No phones'
        ) AS phones,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.name
    LIMIT lim OFFSET off;
END;
$$;
