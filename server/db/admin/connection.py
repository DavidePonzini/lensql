from dav_tools import database
import os

SCHEMA = 'lensql'

db = database.PostgreSQL(
    host        =       os.getenv('DB_HOST', 'localhost'),
    port        =   int(os.getenv('DB_PORT', '5432')),
    database    =       os.getenv('DB_DATABASE', 'postgres'),
    user        =       os.getenv('DB_USERNAME', 'postgres'),
    password    =       os.getenv('DB_PASSWORD', ''),
)

