FROM python:3.7
RUN pip install kopf psycopg2-binary
ADD . /src
CMD kopf run --liveness=http://0.0.0.0:8080/healthz --verbose /src/handlers.py
