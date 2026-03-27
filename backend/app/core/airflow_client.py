"""Async client for Airflow REST API v2."""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AirflowClient:
    """Async client for Airflow REST API v2."""

    def __init__(self) -> None:
        self.base_url = settings.AIRFLOW_API_URL.rstrip("/")
        self.auth = (settings.AIRFLOW_USERNAME, settings.AIRFLOW_PASSWORD)

    async def trigger_dag_parse(self, dag_py_basename: str) -> None:
        """
        Ask Airflow to parse a DAG file (basename without .py).

        Falls back to no-op on HTTP errors — Airflow will still pick up files
        on the next dag_dir_list_interval.
        """
        name = dag_py_basename.replace(".py", "")
        url = f"{self.base_url}/parseDagFile/{name}"
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url, auth=self.auth, timeout=30.0)
                if r.status_code >= 400:
                    logger.warning(
                        "Airflow parseDagFile returned %s: %s — DAG may still load on refresh",
                        r.status_code,
                        r.text[:200],
                    )
        except Exception as e:
            logger.warning("Airflow parseDagFile request failed: %s", e)
