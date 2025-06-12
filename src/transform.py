# transform.py
"""
Transform raw weather payloads into a tidy tabular structure — pandas version
(no Java / Spark required).

The function returns a list[dict] so it is JSON-serialisable for Airflow XCom.
"""

from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime, timezone

import pandas as pd


def transform_weather_data(
    raw_payloads: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Convert a list of OpenWeather JSON payloads into a list of row-dicts.

    Parameters
    ----------
    raw_payloads  – List of dicts from extract_weather_data_bulk().

    Returns
    -------
    list[dict] — one cleaned row per city.
    """
    rows = []
    now_utc = datetime.now(tz=timezone.utc)

    for p in raw_payloads:
        rows.append(
            {
                "city":          p.get("name"),
                "temp_f":        p.get("main", {}).get("temp"),
                "humidity_pct":  p.get("main", {}).get("humidity"),
                "lat":           p.get("coord", {}).get("lat"),
                "lon":           p.get("coord", {}).get("lon"),
                "obs_time_utc":  datetime.fromtimestamp(p.get("dt"), tz=timezone.utc)
                                 if p.get("dt") else None,
                "ingested_at":   now_utc,
            }
        )

    # Optional sanity-check while local-testing
    # df = pd.DataFrame(rows); print(df.head())

    return rows