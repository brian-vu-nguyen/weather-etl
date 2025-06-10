import os
import json
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
PARAMS = {
    "lat": "37.3361663",
    "lon": "-121.890591",
    "appid": api_key,
    "mode": "json",
    "units": "standard",
}
data = requests.get("http://api.openweathermap.org/data/2.5/weather", params=PARAMS).json()

# --- API call (what you already have) -----------------------------
def fetch_data():
    print("Fetching weather data from API...")
    try:
        response = requests.get(data)
        response.raise_for_status()
        print(response)
        return response.json()
    except requests.exceptions.RequestExceptions as e:
        print(f"An error occurred: {e}")
        raise 

def mock_fetch_data():
    return {"{'coord': {'lon': -121.8906, 'lat': 37.3362}, 'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01n'}], 'base': 'stations', 'main': {'temp': 288.21, 'feels_like': 287.91, 'temp_min': 286.96, 'temp_max': 289.2, 'pressure': 1014, 'humidity': 82, 'sea_level': 1014, 'grnd_level': 985}, 'visibility': 10000, 'wind': {'speed': 4.63, 'deg': 10}, 'clouds': {'all': 0}, 'dt': 1749452410, 'sys': {'type': 2, 'id': 2004102, 'country': 'US', 'sunrise': 1749473204, 'sunset': 1749526038}, 'timezone': -25200, 'id': 5392171, 'name': 'San Jose', 'cod': 200}"}

# --- DB connection ------------------------------------------------
conn = psycopg2.connect(
    host     = 'localhost',   # use IP → TCP only
    port     = 5436,
    dbname   = os.getenv("POSTGRES_DB"),
    user     = os.getenv("POSTGRES_USER"),
    password = os.getenv("POSTGRES_PASSWORD"),
    connect_timeout = 5,            # optional: fail fast if wrong
)

print("Connection details: ", conn)

# --- Inserting row ------------------------------------------------
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