from flask import Blueprint, request, jsonify
import requests
from config import WEATHER_API_KEY

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/weather")
def get_weather():
    city = request.args.get("city", "Port Louis")
    try:
        res = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        )
        data = res.json()
        forecast = []
        for item in data["list"][:8]:
            forecast.append({
                "time": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "description": item["weather"][0]["description"],
                "wind_speed": item["wind"]["speed"]
            })
        return jsonify({"city": data["city"]["name"], "forecast": forecast})
    except Exception as e:
        return jsonify({"error": str(e)})
