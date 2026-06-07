import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from pymongo import MongoClient
    client = MongoClient(
        os.getenv("MONGO_URI"),
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
    )
    client.admin.command('ping')
    db = client["weather_dashboard"]
    weather_collection = db["daily_weather"]
    DB_CONNECTED = True
except Exception as e:
    print(f"MongoDB 連線失敗：{e}")
    DB_CONNECTED = False
    weather_collection = None

def save_daily_weather(city: str, forecast: list):
    if not DB_CONNECTED or weather_collection is None:
        return
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
    try:
        weather_collection.update_one(
            {"city": city, "date": doc["date"]},
            {"$set": doc},
            upsert=True
        )
    except:
        pass

def get_history(city: str, days: int = 30):
    if not DB_CONNECTED or weather_collection is None:
        return []
    try:
        results = list(
            weather_collection.find(
                {"city": city},
                {"_id": 0}
            ).sort("date", -1).limit(days)
        )
        return list(reversed(results))
    except:
        return []