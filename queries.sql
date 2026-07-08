-- query 1: Which county has the highest average wind speed in the entire year?
SELECT C.county_name, AVG(W.wind_speed_10m_mean) AS average_wind_speed
FROM County C
LEFT JOIN Weather W ON W.county_id = C.county_id
GROUP BY C.county_name
ORDER BY average_wind_speed DESC
LIMIT 1;

-- query 2: How many counties have moderate cloud cover (30-60%) in the entire year?
SELECT COUNT(*)
FROM (
    SELECT C.county_name, AVG(W.cloud_cover_mean) AS average_cloud
    FROM County C
    LEFT JOIN Weather W ON W.county_id = C.county_id
    GROUP BY C.county_name
    HAVING AVG(W.cloud_cover_mean) BETWEEN 30 AND 60
    ORDER BY average_cloud DESC
);

-- query 3: Which county has the highest total of precipitation in the entire year?
SELECT C.county_name, SUM(W.precipitation_sum) AS total_precipitation
FROM County C
LEFT JOIN Weather W ON W.county_id = C.county_id
GROUP BY C.county_name
ORDER BY total_precipitation DESC
LIMIT 1;

-- query 4: Which month has the lowest average vapour pressure deficit for every county?
SELECT county_name, month, average_vapour
FROM (
    SELECT 
        C.county_name,
        TO_CHAR(W.weather_time, 'Month') AS month,
        W.vapour_pressure_deficit_max AS average_vapour,
        ROW_NUMBER() OVER (
            PARTITION BY C.county_name ORDER BY W.vapour_pressure_deficit_max ASC
        ) as rn
    FROM County C
    LEFT JOIN Weather W ON W.county_id = C.county_id
) AS ranked
WHERE rn = 1
ORDER BY county_name;

-- query 5: Which 5 counties have the lowest total ET0 in the entire year?
SELECT C.county_name, SUM(W.et0_fao_evapotranspiration_sum) as yearly_et0
FROM County C
LEFT JOIN Weather W ON W.county_id = C.county_id
GROUP BY C.county_name
ORDER BY yearly_et0 ASC
LIMIT 5;
    
-- query 6: Which counties have ideal temperatures (18-22 Celcius)?
SELECT C.county_name, AVG(W.temperature_2m_mean) as average_temp
FROM County C
LEFT JOIN Weather W ON W.county_id = C.county_id
GROUP BY C.county_name
HAVING AVG(W.temperature_2m_mean) BETWEEN 18 AND 22
ORDER BY average_temp DESC;

-- query 7: What counties have a moderate average soil moisture, soil temperature, and humidity in the entire year?
WITH Averages AS (
    SELECT
        C.county_name,
        AVG(W.soil_moisture_0_to_100cm_mean) AS average_soil_moisture,
        AVG(W.soil_temperature_0_to_100cm_mean) AS average_soil_temp,
        AVG(W.relative_humidity_2m_mean) AS average_humidity
    FROM County C
    LEFT JOIN Weather W ON W.county_id = C.county_id
    GROUP BY C.county_name
)
SELECT *
FROM Averages
WHERE average_soil_moisture BETWEEN 0.2 AND 0.35
    AND average_soil_temp BETWEEN 15 AND 25
    AND average_humidity BETWEEN 60 AND 70
LIMIT 5;