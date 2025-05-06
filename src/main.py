# Install packages
import os 
import requests
from dotenv import load_dotenv

load_dotenv()

# Create variables
api_key = os.getenv("API_KEY")

# Used Postman to retrieve the desired location's latitude and longitude
# https://api.openweathermap.org/geo/1.0/direct?q=San Jose, California&limit=5
# result:
        # "lat": 37.3361663,
        # "lon": -121.890591,
        # "country": "US",
        # "state": "California"

# Base URL
base_url = "http://api.openweathermap.org/data/2.5/weather?"

# # Current Weather Data Endpoint
# curr_weather_data_endpoint = "/data/2.5/weather?"

# Defining params dict for the parameters to be sent to the API
PARAMS = {
    'lat': '37.3361663',
    'lon': '-121.890591',
    'appid': api_key,
    'mode': 'json',
    'units': 'standard'
}

# Sending get request and saving the response as response object
r = requests.get(url = base_url, params = PARAMS)

# Extracting data in json format
data = r.json()

print(data)