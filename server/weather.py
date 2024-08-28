import requests

# Your API key (replace with your actual key)
api_key = ''

# Base URL for OpenWeatherMap API
base_url = 'http://api.openweathermap.org/data/2.5/weather'

cityname = "Nedlands,WA,Australia"

base_url = f'https://api.weatherapi.com/v1/current.json?key=a49b400c13f6452eae5152413242808&q={cityname}&aqi=no'

# Make the request
response = requests.get(base_url)

# Check if the request was successful
if response.status_code == 200:
    weather_data = response.json()
    print(weather_data)
