# main.py
# 功能：控制整體流程
# - 讀取 list.csv
# - 遍歷每個分類網址
# - 抓取書單與詳細資料
# - 輸出 CSV
# main.py
import os
import csv
import argparse

from category_scraper import scrape_category
from book_detail_scraper import scrape_books_from_urls

def save_books_to_csv(books: list, filepath: str):
    """
    將書籍資料寫入 CSV 檔，欄位：
    書籍網址、出版日期、書名、作者、出版社、定價、優惠價
    """
    fieldnames = ["書籍網址", "出版日期", "書名", "作者", "出版社", "類別", "定價", "優惠價"]
    with open(filepath, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for book in books:
            writer.writerow(book)

def main():
    parser = argparse.ArgumentParser(description="博客來書籍爬蟲")
    parser.add_argument("--start", type=str, default="2025-04-10", help="起始出版日期 (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2025-04-14", help="結束出版日期 (YYYY-MM-DD)")
    args = parser.parse_args()

    # 第一步：抓取分類頁，取得有效書籍網址清單
    urls = scrape_category(args.start, args.end)
    print(f"抓到 {len(urls)} 筆書籍網址。")

    # 第二步：依序進入每本書詳細頁，擷取書籍資訊
    books = scrape_books_from_urls(urls)
    print(f"取得 {len(books)} 筆詳細書籍資訊。")

    # 第三步：輸出到 CSV 檔案
    os.makedirs("output", exist_ok=True)
    csv_filepath = os.path.join("output", "books.csv")
    save_books_to_csv(books, csv_filepath)
    print(f"書籍資訊已儲存到 {csv_filepath}")

if __name__ == "__main__":
    main()