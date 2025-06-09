import os
import json
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# --- API call (what you already have) -----------------------------
api_key = os.getenv("API_KEY")
PARAMS = {
    "lat": "37.3361663",
    "lon": "-121.890591",
    "appid": api_key,
    "mode": "json",
    "units": "standard",
}
data = requests.get("http://api.openweathermap.org/data/2.5/weather", params=PARAMS).json()

# --- DB connection ------------------------------------------------
conn = psycopg2.connect(
    host     = os.getenv("DB_HOST", "127.0.0.1"),   # use IP → TCP only
    port     = os.getenv("DB_PORT", "5433"),
    dbname   = os.getenv("POSTGRES_DB", "postgres"),
    user     = os.getenv("POSTGRES_USER"),
    password = os.getenv("POSTGRES_PASSWORD"),
    connect_timeout = 5,            # optional: fail fast if wrong
)
cur = conn.cursor()

cur.execute(
    """
    INSERT INTO raw_weather (city, payload)
    VALUES (%s, %s::jsonb)
    """,
    ("San Jose, CA", json.dumps(data)),
)

conn.commit()
cur.close()
conn.close()
print("✅ Row inserted")