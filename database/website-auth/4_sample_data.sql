-- Insert users
-- Insert two users with explicit IDs
INSERT INTO users (id, first_name, last_name, email, password, organization, is_verified, role)
VALUES
    (1, 'Dan', 'Johnson', 'dan2@example.com', 'hashed_password_1', 'Tech Corp', TRUE, 'user'),
    (2, 'Bob', 'Smith', 'bob.smith@example.com', 'hashed_password_2', 'Innovate Inc', FALSE, 'admin');

-- Reset the sequence so the next SERIAL value continues correctly
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- Insert events with explicit IDs
INSERT INTO events (id, user_id, name, event_tz, start_date_time, end_date_time, location, affiliation, event_category)
VALUES
    (1, 1, 'Annual Conference', 'America/New_York','2025-09-15 09:00:00+00', '2025-09-15 17:00:00+00', 'Conference Center', 'Tech Corp','New Events/AnnConf'),
    (2, 1, 'Team Building Retreat', 'America/New_York','2025-10-05 08:00:00+00', '2025-10-07 18:00:00+00', 'Lakeside Resort', 'Tech Corp','New Events/TeamRet'),
    (3, 1, 'Webinar on AI', 'America/New_York','2025-11-12 14:00:00+00', '2025-11-12 16:00:00+00', 'Online', 'Tech Corp','New Events/WebAI');

-- Reset the sequence so the next SERIAL value continues correctly
SELECT setval('events_id_seq', (SELECT MAX(id) FROM events));