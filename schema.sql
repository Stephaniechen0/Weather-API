DROP TABLE IF EXISTS Weather;
DROP TABLE IF EXISTS County;

CREATE TABLE IF NOT EXISTS County (
    county_id SERIAL PRIMARY KEY,
    county_name VARCHAR(50),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS Weather (
    weather_id SERIAL PRIMARY KEY,
    county_id INTEGER REFERENCES County(county_id),
    weather_time DATE,
    temperature_2m_mean DOUBLE PRECISION,
    et0_fao_evapotranspiration_sum DOUBLE PRECISION,
    soil_moisture_0_to_100cm_mean DOUBLE PRECISION,
    soil_temperature_0_to_100cm_mean DOUBLE PRECISION,
    relative_humidity_2m_mean DOUBLE PRECISION,
    vapour_pressure_deficit_max DOUBLE PRECISION,
    wind_speed_10m_mean DOUBLE PRECISION,
    cloud_cover_mean DOUBLE PRECISION,
    precipitation_sum DOUBLE PRECISION
);