from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any

from airflow import DAG
from airflow.decorators import task
from airflow.sdk import Variable

from extract import extract_weather_data_bulk
from transform import transform_weather_data
from load import load_weather
from slack_alerts import notify_task_failure

default_args = {
    "owner": "airflow",
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

coords: List[Tuple[float, float]] = [
    (37.3361663, -121.890591),
    (40.7128, -74.0060),
    (34.0522, -118.2437),
]

with DAG(
    dag_id="weather_etl_pipeline",
    start_date=datetime(2025, 6, 11),
    schedule="@hourly",
    catchup=False,
    default_args=default_args,
    tags=["weather"],
) as dag:

    @task(on_failure_callback=[notify_task_failure])
    def extract_task(coord_list: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        # raise RuntimeError("Test Failure")      # ← uncomment to test
        api_key = Variable.get("open_weather_api_key")
        return extract_weather_data_bulk(
            coord_list, api_key=api_key, units="imperial", max_workers=5
        )

    @task(on_failure_callback=[notify_task_failure])
    def transform_task(raw_payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # raise RuntimeError("Test Failure")      # ← uncomment to test
        return transform_weather_data(raw_payloads)

    @task(on_failure_callback=[notify_task_failure])
    def load_task(rows: List[Dict[str, Any]]):
        # raise RuntimeError("Test Failure")      # ← uncomment to test
        load_weather(rows, table="daily_weather", pg_conn_id="weather_pg")

    load_task(transform_task(extract_task(coords)))
