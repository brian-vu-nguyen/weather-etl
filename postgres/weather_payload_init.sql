-- create the table
CREATE TABLE weather_payload (
    payload_id BIGSERIAL PRIMARY KEY,
    city        TEXT        NOT NULL,
    payload     JSONB       NOT NULL
);

-- helpful indexes
CREATE INDEX weather_payload_city_idx   ON weather_payload (city);
CREATE INDEX weather_payload_payload_gin ON weather_payload USING gin (payload);