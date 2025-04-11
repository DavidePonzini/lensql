FROM postgres:latest

COPY 00-users.sql               /docker-entrypoint-initdb.d/
COPY 01-schema.sql              /docker-entrypoint-initdb.d/
COPY 11-analytical_views.sql    /docker-entrypoint-initdb.d/

WORKDIR /app

COPY add_user .
RUN chmod +x add_user

