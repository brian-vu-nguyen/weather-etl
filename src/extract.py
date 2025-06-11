# extract.py
"""
extract.py – Get OpenWeather current-conditions data.

E part of the ETL:
    • extract_weather_data()       → one location
    • extract_weather_data_bulk()  → many locations, optionally in parallel
"""
from __future__ import annotations

import os
from typing import Dict, Any, Iterable, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------#
# Globals
# ---------------------------------------------------------------------------#
load_dotenv()                                 # still allows .env for local runs
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
_ENV_API_KEY = os.getenv("API_KEY")           # fallback only

class WeatherAPIError(RuntimeError):
    """Wrap network / API errors so callers can handle them cleanly."""

# ---------------------------------------------------------------------------#
# Single request
# ---------------------------------------------------------------------------#
def extract_weather_data(
    lat: float,
    lon: float,
    *,
    api_key: str | None = None,               # <─ NEW (override)
    units: str = "imperial",
    timeout: int = 10,
    session: requests.Session | None = None,
) -> Dict[str, Any]:
    """
    Extract current weather for one coordinate pair.
    Returns the raw JSON payload (dict). Raises WeatherAPIError on failure.
    """
    key = api_key or _ENV_API_KEY
    if not key:
        raise WeatherAPIError(
            "API key missing.  "
            "Set the Airflow variable 'open_weather_api_key' or "
            "export API_KEY for local runs."
        )

    params = {
        "lat":   lat,
        "lon":   lon,
        "appid": key,
        "units": units,
        "mode":  "json",
    }

    http = session or requests
    try:
        resp = http.get(BASE_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        raise WeatherAPIError(
            f"Request for lat={lat}, lon={lon} failed: {exc}"
        ) from exc

# ---------------------------------------------------------------------------#
# Bulk requests
# ---------------------------------------------------------------------------#
def extract_weather_data_bulk(
    coords: Iterable[Tuple[float, float]],
    *,
    api_key: str | None = None,               # <─ NEW (propagates to worker)
    units: str = "standard",
    timeout: int = 10,
    max_workers: int = 5,
) -> List[Dict[str, Any]]:
    """
    Extract weather for many locations.  Order of results is preserved.
    """
    coords = list(coords)
    results: List[Dict[str, Any] | None] = [None] * len(coords)

    with requests.Session() as session:

        def _worker(idx: int, lat: float, lon: float):
            results[idx] = extract_weather_data(
                lat,
                lon,
                api_key=api_key,              # <─ pass through
                units=units,
                timeout=timeout,
                session=session,
            )

        if max_workers == 1:
            for i, (lat, lon) in enumerate(coords):
                _worker(i, lat, lon)
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {
                    pool.submit(_worker, i, lat, lon): i
                    for i, (lat, lon) in enumerate(coords)
                }
                for fut in as_completed(futures):
                    fut.result()

    payloads = [p for p in results if p is not None]
    if not payloads:
        raise WeatherAPIError("All weather requests failed.")
    return payloads