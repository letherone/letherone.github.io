# category_scraper.py
import os
import json
import time
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_binary = r"C:\Users\kim.lin\Documents\book-crawler\chrome-win64\chrome.exe"
chromedriver_path = r"C:\Users\kim.lin\Documents\book-crawler\chromedriver-win64\chromedriver.exe"


def scrape_category(start_date: str, end_date: str):
    """
    進入博客來分類頁面，模擬翻頁並擷取每本書的詳細頁網址與出版日期，
    當遇到出版日期早於 start_date 時，停止翻頁。
    有效書籍（出版日期介於 start_date 與 end_date 之間）將存入 output/urls.json。
    
    輸出格式：
    [
      {
        "url": "https://www.books.com.tw/products/0011018046",
        "publish_date": "2025-04-09"
      },
      ...
    ]
    """
    # 轉換日期字串為 datetime 物件
    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    # 設定 Selenium Chrome driver（無頭模式）
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    base_url = "https://www.books.com.tw/web/books_nbtopm_01/?loc=P_0003_001"
    driver.get(base_url)
    time.sleep(2)  # 可依網速調整等待時間

    valid_books = []

    while True:
        # 根據實際網頁 DOM 結構選取每本書的區塊，這裡假設用 "div.item" 當容器
        # 如需調整請依據目標網頁重新指定 CSS Selector
        books = driver.find_elements(By.CSS_SELECTOR, "div.item")
        if not books:
            break

        stop_crawling = False
        for book in books:
            try:
                # 擷取詳細頁連結
                url_element = book.find_element(By.CSS_SELECTOR, "a")
                raw_url = url_element.get_attribute("href")
                book_url = raw_url.split("?")[0]  # 只取 ? 前面的內容
                # 擷取出版日期，假設位於 <li class="info"><span>出版日期：2025-04-09</span></li>
                info_element = book.find_element(By.CSS_SELECTOR, "li.info span")
                publish_text = info_element.text.strip()  # e.g. "出版日期：2025-04-09"
                # 分割字串取得日期部分
                parts = publish_text.split("：")
                publish_date_str = parts[1].strip() if len(parts) > 1 else ""
                # 轉成 datetime 物件
                try:
                    publish_date_obj = datetime.datetime.strptime(publish_date_str, "%Y-%m-%d")
                except Exception as e:
                    print(f"轉換出版日期格式失敗: {publish_date_str}，錯誤：{e}")
                    continue

                # 若遇到出版日期早於 start_date，假設後續頁面皆不符合則停止翻頁
                if publish_date_obj < start_date_obj:
                    stop_crawling = True
                    break

                # 若出版日期在指定範圍內則加入清單
                if start_date_obj <= publish_date_obj <= end_date_obj:
                    valid_books.append({
                        "url": book_url,
                        "publish_date": publish_date_str
                    })

            except Exception as e:
                print("處理某本書資料時發生錯誤:", e)
                continue

        if stop_crawling:
            print("遇到出版日期早於目標區間，停止翻頁。")
            break

        # 嘗試找到下一頁按鈕，並模擬點擊
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.swright"))
            )
            next_button.click()
            print("已點擊下一頁，繼續爬取...")
            time.sleep(2)  # 等待頁面切換
        except Exception as e:
            print("找不到下一頁按鈕或無法點擊，結束爬取", e)
            break

    driver.quit()

    # 存檔至 output/urls.json
    os.makedirs("output", exist_ok=True)
    with open(os.path.join("output", "urls.json"), "w", encoding="utf-8") as f:
        json.dump(valid_books, f, ensure_ascii=False, indent=2)
    
    return valid_books

if __name__ == "__main__":
    # 測試用，可根據需求調整日期區間
    urls = scrape_category(start_date="2025-04-10", end_date="2025-04-14")
    print(f"抓取到 {len(urls)} 筆有效書籍網址。")

