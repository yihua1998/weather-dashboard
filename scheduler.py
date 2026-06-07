import os
import time
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from weather import get_7day_forecast
from database import save_daily_weather

load_dotenv()

POPULAR_CITIES = [
    "Tokyo", "Seoul", "Paris", "London", "Bangkok",
    "Singapore", "New York", "Sydney", "Osaka", "Rome",
    "Taipei", "Kaohsiung"
]

def daily_update():
    print(f"\n[{datetime.now()}] 開始自動更新天氣資料...")
    for city in POPULAR_CITIES:
        try:
            forecast = get_7day_forecast(city)
            save_daily_weather(city, forecast)
            print(f"✅ {city} 更新成功")
            time.sleep(1)
        except Exception as e:
            print(f"❌ {city} 更新失敗：{e}")
    print(f"[{datetime.now()}] 更新完成！")

if __name__ == "__main__":
    # 先立刻跑一次
    daily_update()

    # 每天凌晨 2 點自動跑
    scheduler = BlockingScheduler()
    scheduler.add_job(daily_update, "cron", hour=2, minute=0)
    print("\n排程已啟動，每天凌晨 2 點自動更新...")
    scheduler.start()