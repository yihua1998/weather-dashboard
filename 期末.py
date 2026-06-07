import requests
import time
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.104.com.tw/jobs/search/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def parse_salary(salary_str):
    import re
    nums = re.findall(r"\d+", salary_str.replace(",", ""))
    nums = [int(n) for n in nums]
    if len(nums) >= 2:
        return nums[0], nums[1]
    elif len(nums) == 1:
        return nums[0], nums[0]
    return None, None

def scrape_104(keyword="Python", pages=3):
    jobs = []
    # 先訪問首頁，拿到 cookie
    session = requests.Session()
    session.get("https://www.104.com.tw/jobs/search/?keyword=Python", headers=HEADERS, timeout=10)
    time.sleep(2)

    for page in range(1, pages + 1):
        url = "https://www.104.com.tw/jobs/search/list"
        params = {
            "ro": 0,
            "kwop": 7,
            "keyword": keyword,
            "order": 14,
            "asc": 0,
            "s9": 1,
            "page": page,
        }
        try:
            res = session.get(url, headers=HEADERS, params=params, timeout=10)
            print(f"Page {page} status: {res.status_code}")
            print(f"回應內容: {res.text[:300]}")  # 加這行
            data = res.json()
            for item in data.get("data", {}).get("list", []):
                salary_min, salary_max = parse_salary(item.get("salaryDesc", ""))
                jobs.append({
                    "title": item.get("jobName", ""),
                    "company": item.get("custName", ""),
                    "location": item.get("jobAddrNoDesc", ""),
                    "salary_desc": item.get("salaryDesc", ""),
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "skills": item.get("tags", []),
                    "source": "104",
                    "keyword": keyword,
                    "scraped_at": datetime.utcnow(),
                })
        except Exception as e:
            print(f"Error on page {page}: {e}")
        time.sleep(2)
    return jobs

if __name__ == "__main__":
    results = scrape_104(keyword="Python", pages=2)
    print(f"抓到 {len(results)} 筆職缺")
    for job in results[:3]:
        print(job)