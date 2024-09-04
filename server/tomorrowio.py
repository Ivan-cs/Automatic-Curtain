import requests 

# Your API key (replace with your actual key)
api_key = 'Du4xFKc0oS0Lv4INY8mnDk033tYVYaQE'

# Base URL for OpenWeatherMap API
base_url = 'https://api.tomorrow.io/v4/weather/forecast'


# coordinate location for nedlands
latitude = -31.9787
longitude = 115.8058

#half an hour interval
base_url = f'https://api.tomorrow.io/v4/timelines?location={latitude},{longitude}&fields=temperature&fields=humidity&fields=weatherCode&fields=windSpeed&fields=windDirection&fields=windGust&timesteps=30m&units=metric&apikey={api_key}'

# Make the request
response = requests.get(base_url)

# Check if the request was successful
if response.status_code == 200:
    weather_data = response.json()
    print(weather_data)