import requests
import pandas as pd

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": 37.77,
    "longitude": -122.42,
    "start_date": "2024-01-01",
    "end_date": "2024-01-01",
    "daily": "apparent_temperature_max,apparent_temperature_min"
}

response = requests.get(url, params=params)
data = response.json()

df = pd.DataFrame(data)

df