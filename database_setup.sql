-- PostgreSQL Database Setup Commands

-- 1. Create a new database user
CREATE USER castlang WITH PASSWORD 'W6VH8WyGKZrDvjQKNx9YA33ZCxY8sobkEw2Co';

-- 2. Create the database
CREATE DATABASE castlang OWNER castlang;

-- 3. Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE castlang TO castlang;

-- 4. Connect to the new database (run this command separately)
-- \c castlang

-- 5. Grant schema privileges (run after connecting to the database)
GRANT ALL ON SCHEMA public TO castlang; 