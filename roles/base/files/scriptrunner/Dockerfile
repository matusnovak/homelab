FROM ubuntu:latest

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-pip \
    python3-dev \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    slapd \
    ldap-utils \
    tox

RUN python3 -m pip install \
    requests \
    docker \
    psycopg2 \
    python-ldap
