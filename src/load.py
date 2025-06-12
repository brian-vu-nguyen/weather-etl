# load.py
"""
Load step – write the transformed weather rows into Postgres using
Airflow's PostgresHook (psycopg2 under the hood).

Requirements
------------
* Airflow's 'postgres' provider   (already present in the standard image)
* A Postgres connection in Admin → Connections. Example:
      Conn Id:   weather_pg        (use the same id in `load_weather`)
      Conn Type: Postgres
      Host:      host.docker.internal   # or your container name / RDS endpoint
      Schema:    weather
      Login:     airflow
      Password:  ****
      Port:      5432

The function is **idempotent**: it will auto-create the table if missing.
"""

from __future__ import annotations
from typing import List, Dict, Any
import logging

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values


def _ensure_table_exists(pg_hook: PostgresHook, table: str) -> None:
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table} (
        city            TEXT,
        temp_f          NUMERIC,
        humidity_pct    NUMERIC,
        lat             NUMERIC,
        lon             NUMERIC,
        obs_time_utc    TIMESTAMP WITH TIME ZONE,
        ingested_at     TIMESTAMP WITH TIME ZONE
    );
    """
    with pg_hook.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(create_sql)
        conn.commit()


def load_weather(
    rows: List[Dict[str, Any]],
    *,
    table: str = "daily_weather",
    pg_conn_id: str = "weather_pg",
    batch_size: int = 500,
) -> None:
    """
    Insert each dict in *rows* into *table*.

    Parameters
    ----------
    rows        – list of dicts from transform_weather_data().
    table       – Postgres table name (created if absent).
    pg_conn_id  – Airflow Postgres connection id.
    batch_size  – how many rows per execute_values() call.
    """
    if not rows:
        logging.warning("load_weather: received 0 rows – nothing to write.")
        return

    pg_hook = PostgresHook(postgres_conn_id=pg_conn_id)
    _ensure_table_exists(pg_hook, table)

    fields = [
        "city",
        "temp_f",
        "humidity_pct",
        "lat",
        "lon",
        "obs_time_utc",
        "ingested_at",
    ]

    values = [[r.get(f) for f in fields] for r in rows]

    insert_sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES %s"

    with pg_hook.get_conn() as conn:
        with conn.cursor() as cur:
            for i in range(0, len(values), batch_size):
                execute_values(cur, insert_sql, values[i : i + batch_size])
        conn.commit()

    logging.info("%s rows written to %s via %s", len(rows), table, pg_conn_id)