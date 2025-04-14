# book_detail_scraper.py
import time
import random
import requests
from bs4 import BeautifulSoup

# 設定 headers 以模擬一般瀏覽器
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.77 Safari/537.36"
    )
}

def parse_meta_description(meta_text: str) -> dict:
    """
    解析 meta 的 description，抽出書名、作者、出版社等資訊。
    """
    data = {}
    try:
        parts = meta_text.split("，")
        for part in parts:
            if "書名：" in part:
                data["書名"] = part.split("書名：")[-1].strip()
            elif "作者：" in part:
                data["作者"] = part.split("作者：")[-1].strip()
            elif "出版社：" in part:
                data["出版社"] = part.split("出版社：")[-1].strip()
    except Exception as e:
        print("解析 meta description 時出錯:", e)
    return data

def fetch_url_with_retry(url: str, max_retries: int = 3, delay: int = 10, timeout: int = 30):
    """
    帶有重試機制的請求，預設最多重試 3 次，每次失敗後等待 10 秒，並設定 timeout 時間。
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.encoding = "utf-8"
            return response
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            print(f"第 {attempt} 次連線失敗: {e}. 等待 {delay} 秒後重試...")
            time.sleep(delay)
    print(f"無法抓取 {url}，超過重試次數。")
    return None

def scrape_books_from_urls(urls: list) -> list:
    """
    讀取來自分類頁傳入的書籍網址清單，每筆資料格式包含：
      - 書籍網址、出版日期（分類頁資訊）
      - 書名、作者、出版社（來自 meta description）
      - 定價（ul.price > li em）
      - 優惠價（ul.price > li strong.price01 > b）
      
    使用延遲與重試機制來降低連線問題，並提供手動暫停選項供偵錯時使用。
    """
    books = []
    for idx, entry in enumerate(urls):
        url = entry.get("url")
        publish_date = entry.get("publish_date")
        
        # 可在每次請求前加上隨機延遲，避免過快請求導致被封鎖
        sleep_time = random.uniform(2, 60)
        print(f"【{idx+1}/{len(urls)}】等待 {sleep_time:.2f} 秒後開始處理 {url}")
        time.sleep(sleep_time)

        # 若需要手動暫停檢查，可取消下面的註解
        # input("按 Enter 繼續處理下一本書...")

        response = fetch_url_with_retry(url)
        if not response:
            # 若連線失敗則略過此筆，或可記錄錯誤
            continue

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 解析 meta description
            meta = soup.select_one('meta[name="description"]')
            meta_data = {}
            if meta and meta.get("content"):
                meta_data = parse_meta_description(meta["content"])

            # 解析價格區塊：定價與優惠價
            price_elem = soup.select_one("ul.price li em")
            price = price_elem.text.strip() if price_elem else ""
            discount_elem = soup.select_one("ul.price li strong.price01 b")
            discount_price = discount_elem.text.strip() if discount_elem else ""
            
            book_data = {
                "書籍網址": url,
                "出版日期": publish_date,
                "書名": meta_data.get("書名", ""),
                "作者": meta_data.get("作者", ""),
                "出版社": meta_data.get("出版社", ""),
                "定價": price,
                "優惠價": discount_price
            }
            books.append(book_data)
            print(f"成功解析：{book_data['書名']}")
        except Exception as e:
            print(f"處理 {url} 時解析失敗: {e}")
            continue

    return books

if __name__ == "__main__":
    # 測試用：假設 output/urls.json 已有分類頁抓下來的資料
    import json
    try:
        with open("output/urls.json", "r", encoding="utf-8") as f:
            urls = json.load(f)
    except Exception as e:
        print("讀取 urls.json 發生錯誤:", e)
        urls = []
    
    books = scrape_books_from_urls(urls)
    print(f"共取得 {len(books)} 筆書籍資訊。")
    # 你可以將 books 資料傳回或交由主控程式做 CSV 輸出
