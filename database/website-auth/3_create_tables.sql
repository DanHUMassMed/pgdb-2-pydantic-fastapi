-- Users 
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT, -- nullable for magic link users
    is_verified BOOLEAN DEFAULT FALSE, -- email verified
    verification_token TEXT, -- for signup/activation
    magic_link_token TEXT, -- one-time login link
    magic_link_expires_at TIMESTAMP, -- expiry for magic link
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login_at TIMESTAMP,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin'))
);

