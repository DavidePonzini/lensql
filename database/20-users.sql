BEGIN TRANSACTION;

INSERT INTO lensql.users(username)
VALUES
    ('dav'),
    ('dev'),
    ('test'),
    ('barbara'),
    ('giovanna')

ON CONFLICT (username) DO NOTHING;

COMMIT;
