import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather(
    city: str
):

    print("Weather tool invoked!")
    url = f"http://api.weatherapi.com/v1/current.json?q={city}&key={os.environ["WEATHER_API_KEY"]}"
    response = requests.get(url).json()
    
    temp_c = response["current"]["temp_c"]
    return temp_c