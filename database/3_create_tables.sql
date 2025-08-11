-- Conferences
CREATE TABLE conferences (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    start_date DATE,
    end_date DATE
);

-- Attendees 
CREATE TABLE attendees (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    affiliation TEXT,
    position TEXT CHECK (position IN ('Student', 'Post-doc', 'PI', 'Staff_scientist')),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    conference_id INTEGER NOT NULL REFERENCES conferences(id) ON DELETE CASCADE
);

-- Judges (subset of attendees)
CREATE TABLE judges (
    id SERIAL PRIMARY KEY,
    person_id INT UNIQUE NOT NULL REFERENCES attendees(id) ON DELETE CASCADE,
    accepted BOOLEAN DEFAULT FALSE,
    email_response_date DATE,
    email_sent_date DATE
);

-- Posters
CREATE TABLE posters (
    id SERIAL PRIMARY KEY,
    board_location TEXT NOT NULL,
    poster_up_date DATE,
    poster_down_date DATE,
    creator_id INTEGER REFERENCES attendees(id) ON DELETE SET NULL,
    poster_title TEXT NOT NULL,
    poster_abstract TEXT,
    judging_session TEXT
);

-- Judging Assignments
CREATE TABLE judging_assignments (
    id SERIAL PRIMARY KEY,
    judge_id INT NOT NULL REFERENCES judges(id) ON DELETE CASCADE,
    poster_id INT NOT NULL REFERENCES posters(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK (status IN ('Conflict', 'Assigned', 'Completed', 'Skipped')) DEFAULT 'Assigned',
    UNIQUE(judge_id, poster_id)
);

-- Scoring Criteria
CREATE TABLE criteria (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    max_score INT NOT NULL DEFAULT 5
);

-- Scores: Represents a judge scoring a poster (includes comment or optional summary)
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    assignment_id INT NOT NULL REFERENCES judging_assignments(id) ON DELETE CASCADE,
    comment TEXT
);

-- Score Criteria: Individual criterion scores tied to a score "event"
CREATE TABLE score_criteria (
    id SERIAL PRIMARY KEY,
    score_id INT NOT NULL REFERENCES scores(id) ON DELETE CASCADE,
    criterion_id INT NOT NULL REFERENCES criteria(id) ON DELETE CASCADE,
    score_value INT CHECK (score_value >= 0 AND score_value <= 5),
    UNIQUE(score_id, criterion_id)
);