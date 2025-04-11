BEGIN TRANSACTION;

INSERT INTO lensql.users(username)
VALUES
    ('dav'),
    ('giovanna'),
    ('barbara')

ON CONFLICT (username) DO NOTHING;

COMMIT;
