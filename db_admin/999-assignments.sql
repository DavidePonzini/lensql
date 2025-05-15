BEGIN;

SET search_path TO lensql;

INSERT INTO teaches (teacher, student) VALUES
('dav', 'dav'),

('giovanna', 'giovanna'),
('giovanna', 'barbara'),
('giovanna', 'dav'),

('barbara', 'barbara'),
('barbara', 'giovanna'),
('barbara', 'dav'),

ON CONFLICT (teacher, student) DO NOTHING;

COMMIT;