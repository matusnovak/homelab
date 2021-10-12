FROM python:3.7
RUN apt-get update && apt-get install -y build-essential python3-dev libldap2-dev libsasl2-dev
RUN pip install kopf python-ldap
ADD . /src
CMD kopf run --liveness=http://0.0.0.0:8080/healthz --verbose /src/handlers.py
