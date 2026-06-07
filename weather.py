import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("OWM_API_KEY")

WEATHER_ICONS = {
    "晴天": "☀️", "晴": "☀️", "多雲": "⛅", "陰": "🌥️",
    "小雨": "🌦️", "雨": "🌧️", "大雨": "🌧️", "雷雨": "⛈️",
    "雪": "❄️", "霧": "🌫️",
}

def get_weather_icon(description):
    for key, icon in WEATHER_ICONS.items():
        if key in description:
            return icon
    return "🌤️"

def get_7day_forecast(city):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "zh_tw", "cnt": 40}
    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    data = res.json()
    days = {}
    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        date_str = dt.strftime("%m/%d")
        weekday = ["一","二","三","四","五","六","日"][dt.weekday()]
        if date_str not in days:
            days[date_str] = {"date": date_str, "weekday": f"週{weekday}", "temps": [], "descriptions": [], "humidity": [], "rain": 0}
        days[date_str]["temps"].append(item["main"]["temp"])
        days[date_str]["descriptions"].append(item["weather"][0]["description"])
        days[date_str]["humidity"].append(item["main"]["humidity"])
        if "rain" in item:
            days[date_str]["rain"] += item["rain"].get("3h", 0)
    result = []
    for date_str, day in days.items():
        desc = max(set(day["descriptions"]), key=day["descriptions"].count)
        result.append({
            "date": day["date"], "weekday": day["weekday"],
            "temp_max": round(max(day["temps"]), 1),
            "temp_min": round(min(day["temps"]), 1),
            "temp_avg": round(sum(day["temps"]) / len(day["temps"]), 1),
            "description": desc, "icon": get_weather_icon(desc),
            "humidity": round(sum(day["humidity"]) / len(day["humidity"])),
            "rain": round(day["rain"], 1),
        })
    return result

def get_air_quality(city):
    geo_res = requests.get("http://api.openweathermap.org/geo/1.0/direct", params={"q": city, "limit": 1, "appid": API_KEY}, timeout=10).json()
    if not geo_res:
        return []
    lat, lon = geo_res[0]["lat"], geo_res[0]["lon"]
    aqi_data = requests.get("http://api.openweathermap.org/data/2.5/air_pollution/forecast", params={"lat": lat, "lon": lon, "appid": API_KEY}, timeout=10).json()
    aqi_labels = {1: "良好 😊", 2: "普通 🙂", 3: "敏感族群注意 😷", 4: "不健康 😨", 5: "非常不健康 🚫"}
    results = []
    for item in aqi_data["list"]:
        aqi = item["main"]["aqi"]
        results.append({
            "datetime": datetime.fromtimestamp(item["dt"]),
            "aqi": aqi, "aqi_label": aqi_labels.get(aqi, "未知"),
            "pm2_5": item["components"]["pm2_5"],
            "pm10": item["components"]["pm10"],
            "no2": item["components"]["no2"],
        })
    return results

def get_current_weather(city: str):
    """拿當下即時天氣"""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "zh_tw",
    }
    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    data = res.json()
    return {
        "temp": round(data["main"]["temp"], 1),
        "feels_like": round(data["main"]["feels_like"], 1),
        "temp_max": round(data["main"]["temp_max"], 1),
        "temp_min": round(data["main"]["temp_min"], 1),
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "icon": get_weather_icon(data["weather"][0]["description"]),
    }