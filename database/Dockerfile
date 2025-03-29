FROM postgres:latest

WORKDIR /app

COPY 00-users.sql                   /docker-entrypoint-initdb.d/
COPY 01-schema.sql                  /docker-entrypoint-initdb.d/
COPY 11-analytical_views.sql        /docker-entrypoint-initdb.d/
COPY 20-users.sql                   /docker-entrypoint-initdb.d/

