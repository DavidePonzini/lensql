FROM postgres:latest


WORKDIR /docker-entrypoint-initdb.d

COPY 00-users.sql .
COPY 01-schema.sql .
COPY 11-analytical_views.sql .


