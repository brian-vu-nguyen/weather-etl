from extract import fetch_weather_bulk
import json
from pyspark.sql import functions as F

def build_tidy_df(spark, coords):
    """
    Run Extract + Transform inside an existing Spark session.

    Parameters
    ----------
    spark   : pyspark.sql.SparkSession
    coords  : iterable[(lat, lon)]

    Returns
    -------
    pyspark.sql.DataFrame – one row per location, ready to load.
    """
    raw_payloads = fetch_weather_bulk(coords)          # E
    rdd_json = spark.sparkContext.parallelize(
        [json.dumps(p) for p in raw_payloads]
    )
    weather_df = spark.read.json(rdd_json)

    tidy_df = (
        weather_df.select(
            F.col("name").alias("city"),
            F.round(((F.col("main.temp") - 273.15) * 9/5 + 32), 2).alias("temp_f"),
            F.col("main.humidity").alias("humidity_pct"),
            F.col("coord.lat").alias("lat"),
            F.col("coord.lon").alias("lon"),
            F.col("dt").cast("timestamp").alias("obs_time_utc")
        )
        .withColumn("ingested_at", F.current_timestamp())
    )
    return tidy_df