import requests 

# Your API key (replace with your actual key)
api_key = '99dd44ea364e455a9bafb8ba9f0c83fe'

# Base URL for OpenWeatherMap API
base_url = 'https://api.weatherbit.io/v2.0/current'


# coordinate location for nedlands
latitude = -31.9787
longitude = 115.8058

base_url = f'https://api.weatherbit.io/v2.0/current?lat={latitude}&lon={longitude}&key={api_key}'

# Make the request
response = requests.get(base_url)

# Check if the request was successful
if response.status_code == 200:
    weather_data = response.json()
    print(weather_data)