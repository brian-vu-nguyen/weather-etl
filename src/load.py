import os
from pathlib import Path

from dotenv import load_dotenv        # pip install python-dotenv
from pyspark.sql import SparkSession
from transform import build_tidy_df

# 0. Read secrets.env into the process environment
env_path = Path(__file__).with_name("secrets.env")   # adjust if it lives elsewhere
load_dotenv(dotenv_path=env_path)                    # now os.environ has the pairs


# 1. Spark session
spark = (
    SparkSession.builder
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3")
    .appName("weather_load")
    .getOrCreate()
)


# 2. Re-run Transform
coords = [
    (37.3361663, -121.890591),   # San Jose
    (40.7128,    -74.0060),      # New York
    (34.0522,    -118.2437),     # Los Angeles
] 
df = build_tidy_df(spark, coords)
df.show(truncate=False)


# 3. Write to Postgres via JDBC
PG_HOST           = "localhost"          # no fallback → raises if missing
PG_PORT           = 5436
POSTGRES_DB       = os.getenv("POSTGRES_DB")
POSTGRES_USER     = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
WRITE_MODE        = os.getenv("WRITE_MODE", "append")   # optional, keep default
TABLE             = "daily_weather"

jdbc_url = f"jdbc:postgresql://{PG_HOST}:{PG_PORT}/{POSTGRES_DB}"

(df.write
   .mode(WRITE_MODE)
   .jdbc(
       url        = jdbc_url,
       table      = TABLE,
       properties = {
           "user":     POSTGRES_USER,
           "password": POSTGRES_PASSWORD,
           "driver":   "org.postgresql.Driver",
       },
   )
)

print(f"\n✅ Loaded data into {POSTGRES_DB}.{TABLE} ({WRITE_MODE} mode)")
spark.stop()