# syntax=docker/dockerfile:1
# Extends the official Airflow 3 image.
# https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
#
# The init logic (db migrate, user creation, chown) runs inline in
# docker-compose.airflow.yml via the airflow-init service, exactly as
# the official Apache compose file does it. No external script needed.

FROM apache/airflow:3.1.8

USER root

COPY --chown=airflow:root dags /opt/airflow/dags
COPY --chown=airflow:root plugins /opt/airflow/plugins
COPY --chown=airflow:root config /opt/airflow/config

USER airflow

RUN pip install --no-cache-dir apache-airflow-providers-standard
