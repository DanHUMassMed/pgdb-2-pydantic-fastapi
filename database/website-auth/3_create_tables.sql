-- Users 
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL, -- limit to 50 chars
    last_name VARCHAR(50) NOT NULL, -- limit to 50 chars
    email VARCHAR(255) UNIQUE NOT NULL, -- typical email max length
    password VARCHAR(128), -- hashed passwords are usually <= 128 chars
    organization VARCHAR(128), 
    is_verified BOOLEAN DEFAULT FALSE NOT NULL, -- email verified
    magic_link_token VARCHAR(1024), -- same
    magic_link_expires_at VARCHAR(64), -- expiry for magic link
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login_at VARCHAR(64),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')) NOT NULL
);

-- 1. Create the sequence first
CREATE SEQUENCE sort_pos_seq;

-- 2. Create the table (sequence already exists, so DEFAULT works fine)
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- links event to user
    name VARCHAR(128) NOT NULL,
    event_tz VARCHAR(64) NOT NULL,
    start_date_time TIMESTAMPTZ NOT NULL,
    end_date_time TIMESTAMPTZ NOT NULL,
    location VARCHAR(128),
    affiliation VARCHAR(128),
    sort_pos INT DEFAULT nextval('sort_pos_seq') NOT NULL,
    logo_path VARCHAR(256),
    event_category VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. Attach the sequence ownership to the column
ALTER SEQUENCE sort_pos_seq OWNED BY events.sort_pos;
