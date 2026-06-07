import os
import datetime
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def get_outfit_suggestions(temp, gender, description="", city="", month=None):
    if month is None:
        month = datetime.datetime.now().month

    gender_keyword = "女生" if gender == "女" else "男生"

    if month in [6, 7, 8]:
        temp_keyword = "炎熱夏天" if temp >= 28 else "夏天"
    elif month in [3, 4, 5]:
        temp_keyword = "溫暖春天" if temp >= 25 else "涼爽春天"
    elif month in [9, 10, 11]:
        temp_keyword = "初秋" if temp >= 25 else "秋天"
    else:
        temp_keyword = "寒冷冬天" if temp <= 10 else "冬天"

    query = f"{city} {month}月 {temp:.0f}度 {gender_keyword} {temp_keyword} 穿搭建議"

    try:
        search = GoogleSearch({
            "q": query,
            "hl": "zh-tw",
            "gl": "tw",
            "num": 5,
            "api_key": SERPAPI_KEY,
        })
        results = search.get_dict()

        suggestions = []
        for r in results.get("organic_results", []):
            title = r.get("title", "")
            url = r.get("link", "")
            if title and url:
                suggestions.append({
                    "title": title,
                    "url": url,
                })

        return suggestions if suggestions else [{"title": "目前找不到相關穿搭建議", "url": ""}]

    except Exception as e:
        return [{"title": f"搜尋失敗：{e}", "url": ""}]