BEGIN;

SET search_path TO lensql;

INSERT INTO exercises (id, title, request, dataset) VALUES
(1, 'Progetto', 'Esegui qui tutte le query relative al tuo progetto finale', ''),
(2, 'Modalità libera', 'Se hai delle query che non sono state richieste, ma che vuoi comunque eseguire, puoi farlo qui', ''),
(3, 'Lab 1 - Es 1', 'Seleziona ...', '');

INSERT INTO assignments(username, exercise_id) VALUES
('dav', 1),
('dav', 2),
('dav', 3),
('giovanna', 3),
('giovanna', 2),
('barbara', 3);

INSERT INTO teaches (teacher, student) VALUES
('dav', 'giovanna'),
('dav', 'barbara'),
('giovanna', 'barbara');

COMMIT;