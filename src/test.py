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

# --- API call ---
def fetch_data():
    print("Fetching weather data from API...")
    try:
        response = requests.get(data)
        response.raise_for_status()
        print(response)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise 

fetch_data()

# # --- DB connection ------------------------------------------------
# conn = psycopg2.connect(
#     host     = 'localhost',   # use IP → TCP only
#     port     = 5436,
#     dbname   = os.getenv("POSTGRES_DB"),
#     user     = os.getenv("POSTGRES_USER"),
#     password = os.getenv("POSTGRES_PASSWORD"),
#     connect_timeout = 5,            # optional: fail fast if wrong
# )

# print("Connection details: ", conn)

# # --- Inserting row ------------------------------------------------
# def insert_payload(conn, city: str, payload: dict) -> int:
#     """
#     Inserts a weather payload row and returns the generated payload_id.

#     Parameters
#     ----------
#     conn    : psycopg2 connection (already open)
#     city    : str  – e.g. "San Jose, CA"
#     payload : dict – raw Python dict with the API response

#     Returns
#     -------
#     int – the new payload_id
#     """
#     try:
#         with conn.cursor() as cur:
#             cur.execute(
#                 """
#                 INSERT INTO weather_payload (city, payload)
#                 VALUES (%s, %s)
#                 RETURNING payload_id;
#                 """,
#                 (city, Json(payload)),   # Json adapter writes correct JSONB
#             )
#             new_id = cur.fetchone()[0]

#         conn.commit()
#         print(f"✅ Row inserted (payload_id = {new_id})")
#         return new_id

#     except Exception as e:
#         conn.rollback()           # leave the connection usable
#         print("❌ Insert failed:", e)
#         raise                    # re-raise so caller can decide what to do