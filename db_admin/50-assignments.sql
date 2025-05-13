BEGIN;

SET search_path TO lensql;

INSERT INTO exercises (id, request, dataset, expected_answer) VALUES
(1, 'Select this and that from the table t','', ''),
(2, 'Select something from this other','', ''),
(3, 'Select something else','', '');

INSERT INTO assignments(username, exercise_id) VALUES
('dav', 1),
('dav', 2),
('dav', 3),
('giovanna', 3),
('giovanna', 2),
('barbara', 3);

COMMIT;