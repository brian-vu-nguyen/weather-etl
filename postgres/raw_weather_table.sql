-- Create table to hold raw API responses
CREATE TABLE raw_weather (
    city     TEXT   NOT NULL,  -- e.g. “San Francisco”
    payload  JSONB  NOT NULL   -- full OpenWeatherMap response
);