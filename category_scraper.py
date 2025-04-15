import os
import json
import datetime
import time
import requests
from bs4 import BeautifulSoup

def scrape_category(start_date: str, end_date: str):
    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    valid_books = []
    page = 1
    max_pages = 100  # 最多抓幾頁，可自行調整

    while page <= max_pages:
        url = f"https://www.books.com.tw/web/books_nbtopm_01/?o=1&v=1&page={page}"
        print(f"正在處理第 {page} 頁: {url}")

        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print("請求失敗，結束爬蟲")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        books = soup.select("div.item")
        if not books:
            print("找不到書籍區塊，結束爬蟲")
            break

        stop_crawling = False

        for book in books:
            try:
                a_tag = book.find("a")
                book_url = a_tag["href"].split("?")[0]

                info_span = book.select_one("li.info span")
                if not info_span:
                    continue
                publish_text = info_span.get_text(strip=True)
                if "出版日期：" not in publish_text:
                    continue
                publish_date_str = publish_text.split("出版日期：")[-1].strip()

                try:
                    publish_date_obj = datetime.datetime.strptime(publish_date_str, "%Y-%m-%d")
                except ValueError:
                    print(f"無法解析日期：{publish_date_str}，略過此筆")
                    continue

                if publish_date_obj < start_date_obj:
                    stop_crawling = True
                    break

                if start_date_obj <= publish_date_obj <= end_date_obj:
                    valid_books.append({
                        "url": book_url,
                        "publish_date": publish_date_str
                    })

            except Exception as e:
                print("解析書籍時發生錯誤：", e)
                continue

        if stop_crawling:
            print("遇到過早的出版日期，結束爬蟲")
            break

        page += 1
        time.sleep(1.5)

    os.makedirs("output", exist_ok=True)
    with open(os.path.join("output", "urls.json"), "w", encoding="utf-8") as f:
        json.dump(valid_books, f, ensure_ascii=False, indent=2)

    print(f"共擷取 {len(valid_books)} 筆書籍連結")
    return valid_books

if __name__ == "__main__":
    scrape_category("2025-04-01", "2025-04-09")
