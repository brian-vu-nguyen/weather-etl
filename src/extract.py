"""
extract.py – Fetch OpenWeather current-conditions data.

E part of the ETL:
    • fetch_weather()       → one location
    • fetch_weather_bulk()  → many locations, optionally in parallel
"""

# Import packages and save global variables
from __future__ import annotations

import os
from typing import Dict, Any, Iterable, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY  = os.getenv("API_KEY")


# Reusable Weather API runtime error
class WeatherAPIError(RuntimeError):
    """Wrap network / API errors so callers can handle them cleanly."""


# Single request
def fetch_weather(
    lat: float,
    lon: float,
    *,
    units: str = "standard",
    timeout: int = 10,
    session: requests.Session | None = None,
) -> Dict[str, Any]:
    """
    Fetch current weather for one coordinate pair.

    Returns the raw JSON payload (dict). Raises WeatherAPIError on failure.
    """
    if not API_KEY:
        raise WeatherAPIError("API_KEY not found in environment variables")

    params = {
        "lat":   lat,
        "lon":   lon,
        "appid": API_KEY,
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


# Multiple requests
def fetch_weather_bulk(
    coords: Iterable[Tuple[float, float]],
    *,
    units: str = "standard",
    timeout: int = 10,
    max_workers: int = 5,
) -> List[Dict[str, Any]]:
    """
    Fetch weather for many locations.

    Parameters
    ----------
    coords      : iterable of (lat, lon) tuples.
    units       : pass-through to fetch_weather().
    timeout     : per-request timeout.
    max_workers : thread pool size; set to 1 for sequential.

    Returns
    -------
    List[dict] – one payload per successful location, **order preserved**.

    Raises
    ------
    WeatherAPIError if *all* requests fail.
    """
    coords = list(coords)  # so we can map results back in order
    results: List[Dict[str, Any] | None] = [None] * len(coords)

    # Re-use a Session for connection pooling
    with requests.Session() as session:
        def _worker(idx: int, lat: float, lon: float):
            results[idx] = fetch_weather(
                lat, lon, units=units, timeout=timeout, session=session
            )

        # Either sequential or threaded
        if max_workers == 1:
            for i, (lat, lon) in enumerate(coords):
                _worker(i, lat, lon)
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {
                    pool.submit(_worker, i, lat, lon): i
                    for i, (lat, lon) in enumerate(coords)
                }
                # propagate exceptions immediately
                for fut in as_completed(futures):
                    fut.result()

    payloads = [p for p in results if p is not None]
    if not payloads:
        raise WeatherAPIError("All weather requests failed.")
    return payloads


# Manual test: `python extract.py`
# If extraction works, we should print the single and multiple requests
if __name__ == "__main__":
    san_jose = (37.3361663, -121.890591)
    nyc      = (40.7128,    -74.0060)
    la       = (34.0522,    -118.2437)

    # single
    print(fetch_weather(*san_jose)["name"])

    # bulk (threaded)
    bulk = fetch_weather_bulk([san_jose, nyc, la], max_workers=3)
    print([p["name"] for p in bulk])
