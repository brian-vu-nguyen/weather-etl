# transform.py  (example)
from extract import fetch_weather_bulk

import json
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import round

coords = [
    (37.3361663, -121.890591),   # San Jose
    (40.7128,    -74.0060),      # New York
    (34.0522,    -118.2437),     # Los Angeles
]

# 1. Extract
raw_payloads = fetch_weather_bulk(coords)   # list of dicts
# …proceed with your transform logic…

# 2. Start Spark
spark = (
    SparkSession.builder
    .appName("weather_transform")
    .getOrCreate()
)

# 3. Feed JSON into Spark
# • Spark’s JSON reader expects an RDD/DataFrame of JSON *strings*.
# • Turn each dict → json.dumps(...) → parallelize → read.
rdd_json = spark.sparkContext.parallelize([json.dumps(p) for p in raw_payloads])
weather_df = spark.read.json(rdd_json)

# 4. Explore
weather_df.printSchema()
weather_df.select(
    "name",                    # city name
    "main.temp",               # nested access
    "main.humidity",
    "coord.lat",
    "coord.lon"
).show(truncate=False)

# 5. Transform
tidy_df = (
    weather_df.select(
        F.col("name").alias("city"),
        F.round(((F.col("main.temp") - 273.15) * (9/5) + 32), 2).alias("temp_f"),
        (F.col("main.humidity")).alias("humidity_pct"),
        F.col("coord.lat").alias("lat"),
        F.col("coord.lon").alias("lon"),
        (F.col("dt").cast("timestamp")).alias("obs_time_utc")
    )
    .withColumn("ingested_at", F.current_timestamp())
).show(truncate=False)

# 6. Stop Spark
spark.stop()