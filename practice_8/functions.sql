CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(name TEXT, surname TEXT, phone TEXT) AS
$$
BEGIN
    RETURN QUERY
    SELECT c.name, c.surname, c.phone
    FROM contacts c
    WHERE c.name ILIKE '%' || pattern || '%'
       OR c.surname ILIKE '%' || pattern || '%'
       OR c.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paginated(lim INT, off INT)
RETURNS TABLE(name TEXT, surname TEXT, phone TEXT) AS
$$
BEGIN
    RETURN QUERY
    SELECT c.name, c.surname, c.phone
    FROM contacts c
    LIMIT lim OFFSET off;
END;
$$ LANGUAGE plpgsql;