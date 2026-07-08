import requests
import pandas as pd
import json
import psycopg
import os

from dotenv import load_dotenv

load_dotenv()
print(os.getenv("DB_NAME"))

url = "https://archive-api.open-meteo.com/v1/archive"

locs = [
    ("Fresno County", 36.7378, -119.7871),
    ("Kern County", 35.3733, -119.0187),
    ("Tulare County", 36.3302, -119.2921),
    ("Monterey County", 36.6777, -121.6555),
    ("Merced County", 37.3022, -120.4829),
    ("Stanislaus County", 37.6391, -120.9969),
    ("San Joaquin County", 37.9577, -121.2908),
    ("Ventura County", 34.2746, -119.2290),
    ("Kings County", 36.3275, -119.6457),
    ("Imperial County", 32.7920, -115.5631),
    ("San Diego County", 32.7157, -117.1611),
    ("Madera County", 36.9613, -120.0607),
    ("San Luis Obispo County", 35.2828, -120.6596),
    ("Santa Barbara County", 34.9530, -120.4357),
    ("Yolo County", 38.6785, -121.7733),
    ("Colusa County", 39.2143, -122.0094),
    ("Butte County", 39.5138, -121.5564),
    ("Glenn County", 39.5243, -122.1936),
    ("Sutter County", 39.1404, -121.6169),
    ("Tehama County", 40.1785, -122.2358)
]

weather_df = pd.DataFrame()
all_counties = []

for county, lat, long in locs:
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "daily": 
            "temperature_2m_mean,"
            "et0_fao_evapotranspiration_sum,"
            "soil_moisture_0_to_100cm_mean,"
            "soil_temperature_0_to_100cm_mean,"
            "relative_humidity_2m_mean,"
            "vapour_pressure_deficit_max,"
            "wind_speed_10m_mean,"
            "cloud_cover_mean,"
            "precipitation_sum"
    }
    response = requests.get(url, params=params)
    data = response.json()
    data["county"] = county
    data["latitude"] = lat
    data["longitude"] = long
    all_counties.append(data)

    df = pd.DataFrame(data["daily"])
    df["time"] = pd.to_datetime(df["time"])
    df["county"] = county
    df["latitude"] = lat
    df["longitude"] = long

    weather_df = pd.concat([weather_df, df], ignore_index=True)

with open("all_counties_weather_data.json", "w") as file:
    json.dump(all_counties, file, indent=4)

weather_columns = [
    "temperature_2m_mean",
    "et0_fao_evapotranspiration_sum",
    "soil_moisture_0_to_100cm_mean",
    "soil_temperature_0_to_100cm_mean",
    "relative_humidity_2m_mean",
    "vapour_pressure_deficit_max",
    "wind_speed_10m_mean",
    "cloud_cover_mean",
    "precipitation_sum"
]

weather_df = weather_df[["county", "time", "latitude", "longitude"] + weather_columns]

print(weather_df)
print(weather_df.isnull().sum())
print(weather_df.dtypes)

print(weather_df.describe())
print("-----------------------------")
for col in weather_columns:
    print(f"\n{col}")
    print(f"Min: {weather_df[col].min()}")
    print(f"Max: {weather_df[col].max()}")
print("-----------------------------")

print(weather_df.duplicated().sum())

# query 1: Which county has the highest average wind speed in the entire year?
def query_one(cur):
    cur.execute("""
    SELECT C.county_name, AVG(W.wind_speed_10m_mean) AS average_wind_speed
    FROM County C
    LEFT JOIN Weather W ON W.county_id = C.county_id
    GROUP BY C.county_name
    ORDER BY average_wind_speed DESC
    LIMIT 1;
    """)
    return cur.fetchone()

# query 2: How many counties have moderate cloud cover (30-60%) in the entire year?
def query_two(cur):
    cur.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT C.county_name, AVG(W.cloud_cover_mean) AS average_cloud
        FROM County C
        LEFT JOIN Weather W ON W.county_id = C.county_id
        GROUP BY C.county_name
        HAVING AVG(W.cloud_cover_mean) BETWEEN 30 AND 60
        ORDER BY average_cloud DESC
    );
    """)
    return cur.fetchall()

# query 3: Which county has the highest total of precipitation in the entire year?
def query_three(cur):
    cur.execute("""
    SELECT C.county_name, SUM(W.precipitation_sum) AS total_precipitation
    FROM County C
    LEFT JOIN Weather W ON W.county_id = C.county_id
    GROUP BY C.county_name
    ORDER BY total_precipitation DESC
    LIMIT 1;
    """)
    return cur.fetchone()

# query 4: Which month has the lowest average vapour pressure deficit for every county?
def query_four(cur):
    cur.execute("""
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
    """)
    return cur.fetchall()

# query 5: Which 5 counties have the lowest total ET0 in the entire year?
def query_five(cur):
    cur.execute("""
    SELECT C.county_name, SUM(W.et0_fao_evapotranspiration_sum) as yearly_et0
    FROM County C
    LEFT JOIN Weather W ON W.county_id = C.county_id
    GROUP BY C.county_name
    ORDER BY yearly_et0 ASC
    LIMIT 5;
    """)
    return cur.fetchall()
    
# query 6: Which counties have ideal temperatures (18-22 Celcius)?
def query_six(cur):
    cur.execute("""
    SELECT C.county_name, AVG(W.temperature_2m_mean) as average_temp
    FROM County C
    LEFT JOIN Weather W ON W.county_id = C.county_id
    GROUP BY C.county_name
    HAVING AVG(W.temperature_2m_mean) BETWEEN 18 AND 22
    ORDER BY average_temp DESC;
    """)
    return cur.fetchall()

# query 7: What counties have a moderate average soil moisture, soil temperature, and humidity in the entire year?
def query_seven(cur):
    cur.execute("""
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
    """)
    return cur.fetchall()

with psycopg.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
) as conn:
    with conn.cursor() as cur:
        # create table
        cur.execute("""
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
        """)

        # add every dataframe row into table
        county_df = weather_df[["county", "latitude", "longitude"]].drop_duplicates()
        county_rows = list(county_df.itertuples(index=False, name=None))
        cur.executemany("""
        INSERT INTO County (
            county_name,
            latitude,
            longitude
        )
        VALUES (%s,%s,%s);
        """, county_rows)

        cur.execute("SELECT COUNT(*) FROM County;")
        count = cur.fetchone()[0]
        print(f"Rows inserted: {count}")

        weather_rows = []
        for row in weather_df.itertuples(index=False):
            weather_rows.append((
                row.time,
                row.temperature_2m_mean,
                row.et0_fao_evapotranspiration_sum,
                row.soil_moisture_0_to_100cm_mean,
                row.soil_temperature_0_to_100cm_mean,
                row.relative_humidity_2m_mean,
                row.vapour_pressure_deficit_max,
                row.wind_speed_10m_mean,
                row.cloud_cover_mean,
                row.precipitation_sum,
                row.county
            ))

        cur.executemany("""
        INSERT INTO Weather (
            county_id,
            weather_time,
            temperature_2m_mean,
            et0_fao_evapotranspiration_sum,
            soil_moisture_0_to_100cm_mean,
            soil_temperature_0_to_100cm_mean,
            relative_humidity_2m_mean,
            vapour_pressure_deficit_max,
            wind_speed_10m_mean,
            cloud_cover_mean,
            precipitation_sum
        )
        SELECT
            c.county_id,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        FROM County c
        WHERE c.county_name = %s;
        """, weather_rows)
        cur.execute("SELECT COUNT(*) FROM Weather;")
        count = cur.fetchone()[0]
        print(f"Rows inserted: {count}")

        # SQL queries
        print(query_one(cur))
        print(query_two(cur))
        print(query_three(cur))     
        print(query_four(cur))
        print(query_five(cur))
        print(query_six(cur))
        print(query_seven(cur))
