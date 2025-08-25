-- Users 
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL, -- limit to 50 chars
    last_name VARCHAR(50) NOT NULL, -- limit to 50 chars
    email VARCHAR(255) UNIQUE NOT NULL, -- typical email max length
    password VARCHAR(128), -- hashed passwords are usually <= 128 chars
    organization VARCHAR(128), 
    is_verified BOOLEAN DEFAULT FALSE NOT NULL, -- email verified
    magic_link_token VARCHAR(128), -- same
    magic_link_expires_at VARCHAR(64), -- expiry for magic link
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login_at VARCHAR(64),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')) NOT NULL
);

