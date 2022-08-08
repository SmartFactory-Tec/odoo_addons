CREATE DATABASE odoo;

REVOKE ALL ON DATABASE odoo FROM public; -- this will revoke default database privileges (CREATE, CONNECT ...) from roles in 'PUBLIC' (all roles). 
REVOKE ALL ON SCHEMA public FROM public;

CREATE ROLE odoo_admin NOINHERIT;
GRANT CONNECT ON DATABASE odoo TO odoo_admin;
GRANT USAGE, CREATE ON SCHEMA public TO odoo_admin;  -- CREATE: allows the creation of schema objects like tables, views, indexes, functions, etc.
ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO odoo_admin;
ALTER DEFAULT PRIVILEGES GRANT ALL ON SEQUENCES TO odoo_admin;

GRANT ALL ON ALL TABLES IN SCHEMA public TO odoo_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO odoo_admin;

CREATE USER odoo INHERIT IN ROLE odoo_admin;

--ALTER ROLE odoo
--WITH PASSWORD '';
