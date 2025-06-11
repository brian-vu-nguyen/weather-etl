from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any

from airflow import DAG
from airflow.decorators import task
from airflow.sdk import Variable                    

from extract import extract_weather_data_bulk
from transform import transform_weather_data
from load import load_weather                             

# ---------------------------------------------------------------------------#
# DAG-level settings
# ---------------------------------------------------------------------------#
default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

coords: List[Tuple[float, float]] = [
    (37.3361663, -121.890591),  # San Jose
    (40.7128,    -74.0060),     # New York
    (34.0522,    -118.2437),    # Los Angeles
]

with DAG(
    dag_id="weather_etl_pipeline",
    start_date=datetime(2025, 6, 11),
    schedule="@hourly",
    catchup=False,
    default_args=default_args,
    tags=["weather"],
) as dag:

    # ------------------------------------------------------------------#
    # EXTRACT
    # ------------------------------------------------------------------#
    @task()
    def extract_task(coord_list: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        api_key = Variable.get("open_weather_api_key")     # pulled at runtime
        return extract_weather_data_bulk(
            coord_list,
            api_key=api_key,
            units="imperial",
            max_workers=5,
        )

    # ------------------------------------------------------------------#
    # TRANSFORM
    # ------------------------------------------------------------------#
    @task()
    def transform_task(raw_payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return transform_weather_data(raw_payloads)

    # ------------------------------------------------------------------#
    # LOAD
    # ------------------------------------------------------------------#
    @task()
    def load_task(rows: List[Dict[str, Any]]):
        """
        Persist rows into Postgres.  Adjust `table` or `pg_conn_id`
        to match your connection.
        """
        load_weather(rows, table="daily_weather", pg_conn_id="weather_pg")

    load_task(transform_task(extract_task(coords)))