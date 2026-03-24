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



def interpret_fwi(value: float) -> str:
    """
    Convert Fire Weather Index number into explanation.
    """
    if value <= 5.2:
        level = "Very Low"
        explanation = "Fires may start, but are not expected to become intense or difficult to control."
    elif value <= 12.2:
        level = "Low"
        explanation = "Fires are generally easily controlled, but can spread in specific fuels."
    elif value <= 21.3:
        level = "Moderate"
        explanation = "Fires can ignite easily and spread in dry, fine fuel."
    elif value <= 38:
        level = "High"
        explanation = "Fire spreads quickly, and control is difficult; spot fires may occur."
    elif value <= 50:
        level = "Very High"
        explanation = "Fast-spreading, intense fires are expected; suppression is difficult."
    else:
        level = "Extreme"
        explanation = "High-intensity fires with explosive potential; active crown fires are likely."
    
    return f"{level} fire danger — {explanation}"


@tool
def get_fire_weather_forecast(city: str):
    """
    Returns the 5-day Fire Weather Index forecast for a given city,
    translated into human-readable fire danger explanations.
    """

    # 1 Get coordinates using Geocoding API
    lat, lon = get_coordinates(city)

    # 2 Call Fire Weather Index API
    fire_url = "https://api.openweathermap.org/data/2.5/fire-index"
    fire_params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY
    }

    fire_response = requests.get(fire_url, params=fire_params)
    fire_data = fire_response.json()

    if "list" not in fire_data:
        return "Fire index data is currently unavailable."

    # 3 Transform results into readable explanation
    forecast_output = f" Fire Weather Forecast for {city.title()}:\n\n"

    for i, day in enumerate(fire_data["list"][:5]):
        fwi_value = day.get("fwi", 0)
        readable = interpret_fwi(fwi_value)
        forecast_output += f"Day {i+1}: FWI {fwi_value:.1f} → {readable}\n\n"

    return forecast_output



