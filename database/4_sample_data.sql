-- Insert one conference
INSERT INTO conferences (id, name, location, start_date, end_date)
VALUES 
(1,'2025 Scientific Poster Conference', 'Boston, MA', '2025-11-01', '2025-11-03'),
(2,'2024 Scientific Conference', 'Worcester, MA', '2024-11-01', '2024-11-03');

SELECT setval('conferences_id_seq', (SELECT MAX(id) FROM conferences));
-- Insert attendees
INSERT INTO attendees (id, first_name, last_name, email, affiliation, position, conference_id)
VALUES 
(1, 'Alice', 'Nguyen', 'alice.nguyen@example.com', 'Harvard University', 'Student', 1),
(2, 'Bob', 'Smith', 'bob.smith@example.com', 'MIT', 'Post-doc', 1),
(3, 'Amy', 'Smith', 'amy.smith@example.com', 'MIT', 'PI', 1),
(4, 'Carla', 'Rodriguez', 'carla.rodriguez@example.com', 'UCLA', 'PI', 1),
(5, 'David', 'Lee', 'david.lee@example.com', 'Stanford University', 'Post-doc', 1),
(6, 'Elena', 'Garcia', 'elena.garcia@example.com', 'Yale University', 'Student', 1),
(7, 'Frank', 'Wright', 'frank.wright@example.com', 'Columbia University', 'Staff_scientist', 1),
(8, 'Grace', 'Kim', 'grace.kim@example.com', 'University of Chicago', 'Student', 1),
(9, 'Hassan', 'Ali', 'hassan.ali@example.com', 'Princeton University', 'Post-doc', 1),
(10, 'Isabel', 'Martinez', 'isabel.martinez@example.com', 'University of Michigan', 'Staff_scientist', 1),
(11, 'Hassan', 'Ali', 'hassan.ali1@example.com', 'Princeton University', 'Post-doc', 2),
(12, 'Isabel', 'Martinez', 'isabel.martinez1@example.com', 'University of Michigan', 'Staff_scientist', 2);
SELECT setval('attendees_id_seq', (SELECT MAX(id) FROM attendees));

-- Insert 10 posters, one for each attendee
INSERT INTO posters (id, board_location, poster_up_date, poster_down_date, creator_id, poster_title, poster_abstract, judging_session)
VALUES
(1, 'A1', '2025-11-01', '2025-11-02', 1, 'Role of RNA-binding Proteins in Neurogenesis', 'Explores key regulatory proteins in neural development.', 'Session 1'),
(2, 'B2', '2025-11-01', '2025-11-02', 2, 'Machine Learning for Microscopy Image Segmentation', 'Using CNNs for high-throughput image analysis.', 'Session 1'),
(3, 'C3', '2025-11-03', '2025-11-04', 3, 'CRISPR Screens in C. elegans', 'Uncovering essential genes using genome editing.', 'Session 2'),
(4, 'D4', '2025-11-03', '2025-11-04', 4, 'Glial Cell Metabolism in Brain Aging', 'Investigates glial metabolic changes during aging.', 'Session 2'),
(5, 'E5', '2025-11-03', '2025-11-04', 5, 'Single-cell Transcriptomics of Brain Organoids', 'Analyzing developmental dynamics in vitro.', 'Session 2'),
(6, 'F6', '2025-11-05', '2025-11-06', 6, 'Stress Granules and RNA Decay', 'A closer look at mRNA regulation under stress.', 'Session 3'),
(7, 'G7', '2025-11-05', '2025-11-06', 7, 'Automated Detection of Mitochondrial Morphology', 'AI-based tools for cell imaging analysis.', 'Session 3'),
(8, 'H8', '2025-11-05', '2025-11-06', 8, 'Circadian Regulation of Immune Function', 'Chronobiology meets immunology.', 'Session 3'),
(9, 'I9', '2025-11-05', '2025-11-06', 9, 'Optogenetic Tools for Synapse Mapping', 'New approaches to map brain connectivity.', 'Session 3'),
(10, 'J10', '2025-11-05', '2025-11-06', 10, 'Comparative Genomics of Aging Pathways', 'Insights from long-lived species.', 'Session 3');
SELECT setval('posters_id_seq', (SELECT MAX(id) FROM posters));

-- Insert posters (Alice and Bob are authors)
INSERT INTO judges (id, person_id, accepted, email_response_date, email_sent_date)
VALUES 
(1, 3, TRUE, '2025-08-01', '2025-07-25'),
(2, 4, TRUE, '2025-08-01', '2025-07-25');
SELECT setval('judges_id_seq', (SELECT MAX(id) FROM judges));

-- Insert judging assignments with overlapping posters
INSERT INTO judging_assignments (id, judge_id, poster_id, status)
VALUES 
(1, 1, 1, 'Assigned'),
(2, 1, 5, 'Assigned'),
(3, 1, 7, 'Assigned'),
(4, 2, 1, 'Assigned'),  -- Same poster as judge 1
(5, 2, 6, 'Assigned'),
(6, 2, 7, 'Assigned');  -- Same poster as judge 1
SELECT setval('judging_assignments_id_seq', (SELECT MAX(id) FROM judging_assignments));

-- Insert scoring criteria
INSERT INTO criteria (name, description, max_score)
VALUES
('Scientific Clarity and Rigor', 'Was the scientific question clear and was the methodology appropriate and rigorous?', 5),
('Data Presentation and Interpretation', 'Were the results clearly presented and convincingly interpreted?', 5),
('Visual Design and Organization', 'Was the poster visually clear, well-organized, and easy to follow?', 5),
('Impact and Innovation', 'Did the poster present novel insights or potential impact for the field?', 5),
('Tiebreaker', 'Was there something special about the poster/presenter we could consider in case of a tie?', 5);

-- Insert scores and score_criteria for Poster 1
INSERT INTO scores (assignment_id, comment)
VALUES (1, 'Strong work and great clarity throughout');
VALUES (3, 'Good presentation, but some methods were unclear');

-- Insert scores and score_criteria for judges 1 on Poster 1
INSERT INTO score_criteria (score_id, criterion_id, score_value)
VALUES 
(1, 1, 5),
(1, 2, 4),
(1, 3, 4),
(1, 4, 5),
(1, 5, 3);

-- Insert scores and score_criteria for judges 2 on Poster 1
INSERT INTO scores (assignment_id, comment)
VALUES (3, 'Innovative approach, but data section was hard to follow');

INSERT INTO score_criteria (score_id, criterion_id, score_value)
VALUES 
(2, 1, 4),
(2, 2, 3),
(2, 3, 5),
(2, 4, 5),
(2, 5, 4);