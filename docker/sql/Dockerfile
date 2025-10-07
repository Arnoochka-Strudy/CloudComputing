FROM postgres:15

ENV POSTGRES_DB=tgdb
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin

COPY init.sql /docker-entrypoint-initdb.d/