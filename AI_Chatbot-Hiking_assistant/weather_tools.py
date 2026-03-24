from langchain.tools import tool
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".secrets")


OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_coordinates(city: str):
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY
    }

    response = requests.get(geo_url, params=params)
    data = response.json()

    if not data:
        return None, None

    return data[0]["lat"], data[0]["lon"] 



@tool
def get_current_temperature(city: str) -> str:
    """
    Returns the current temperature and basic weather conditions for a city.
    """

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"  # Celsius
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"Weather data unavailable: {response.text}"

    data = response.json()

    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    description = data["weather"][0]["description"]

    return (
        f"Current weather in {city.title()}:\n"
        f"Temperature: {temp}°C\n"
        f"Feels like: {feels_like}°C\n"
        f"Conditions: {description}"
    )

@tool
def get_weather_alerts(city: str) -> str:
    """
    Returns active weather alerts for a given city.
    """

    # Step 1: Geocode
    lat, lon = get_coordinates(city)

    # Step 2: One Call API
    alert_url = "https://api.openweathermap.org/data/3.0/onecall"
    alert_params = {
        "lat": lat,
        "lon": lon,
        "exclude": "current,minutely,hourly,daily",
        "appid": OPENWEATHER_API_KEY
    }

    alert_response = requests.get(alert_url, params=alert_params)

    if alert_response.status_code != 200:
        return f"Alert data unavailable: {alert_response.text}"

    alert_data = alert_response.json()

    if "alerts" not in alert_data:
        return f"No active weather alerts for {city.title()}."

    output = f"Active Weather Alerts for {city.title()}:\n\n"

    for alert in alert_data["alerts"]:
        output += (
            f"Event: {alert['event']}\n"
            f"From: {alert['start']}\n"
            f"To: {alert['end']}\n"
            f"Description: {alert['description']}\n\n"
        )

    return output

@tool
def get_next_rain(city: str) -> str:
    """
    Returns rain volume for the next available forecast time.
    """

    lat, lon = get_coordinates(city)
    if lat is None:
        return f"Could not find location data for {city}."

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"Rain data unavailable: {response.text}"

    data = response.json()

    next_entry = data["list"][0]
    timestamp = next_entry["dt_txt"]
    rain_volume = next_entry.get("rain", {}).get("3h", 0)

    return (
        f"Next Rain Forecast for {city.title()}:\n"
        f"Time: {timestamp}\n"
        f"Rain (next 3h): {rain_volume} mm"
    )

@tool
def get_next_wind(city: str) -> str:
    """
    Returns wind speed and direction for the next available forecast time.
    """

    lat, lon = get_coordinates(city)
    if lat is None:
        return f"Could not find location data for {city}."

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"Wind data unavailable: {response.text}"

    data = response.json()

    next_entry = data["list"][0]
    timestamp = next_entry["dt_txt"]
    wind_speed = next_entry["wind"]["speed"]
    wind_deg = next_entry["wind"]["deg"]

    return (
        f"Next Wind Forecast for {city.title()}:\n"
        f"Time: {timestamp}\n"
        f"Wind Speed: {wind_speed} m/s\n"
        f"Direction: {wind_deg}°"
    )

