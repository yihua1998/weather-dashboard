import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["weather_dashboard"]
weather_collection = db["daily_weather"]

def save_daily_weather(city: str, forecast: list):
    """儲存當天天氣快照"""
    today = forecast[0]
    doc = {
        "city": city,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "temp_max": today["temp_max"],
        "temp_min": today["temp_min"],
        "temp_avg": today["temp_avg"],
        "description": today["description"],
        "humidity": today["humidity"],
        "rain": today["rain"],
        "saved_at": datetime.now(),
    }
    # 同一城市同一天只存一筆
    weather_collection.update_one(
        {"city": city, "date": doc["date"]},
        {"$set": doc},
        upsert=True
    )
    print(f"已儲存 {city} {doc['date']} 天氣資料")

def get_history(city: str, days: int = 30):
    """取得某城市過去N天的歷史資料"""
    results = list(
        weather_collection.find(
            {"city": city},
            {"_id": 0}
        ).sort("date", -1).limit(days)
    )
    return list(reversed(results))