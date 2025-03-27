BEGIN TRANSACTION;

INSERT INTO lensql.users(username)
VALUES
    ('dav'),
    ('dev'),
    ('test')
ON CONFLICT (username) DO NOTHING;

COMMIT;
