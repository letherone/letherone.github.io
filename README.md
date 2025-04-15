# 使用說明

## 設定日期區間
透過命令列參數指定出版日期範圍（格式： YYYY-MM-DD），例如：

```bash
python main.py --start 2025-04-10 --end 2025-04-14
```

## 流程說明

- **Step 1:** `category_scraper.py`  
  載入博客來分類頁，模擬翻頁並擷取在指定日期區間內的書籍網址與出版日期，結果會存入 `output/urls.json`。

- **Step 2:** `book_detail_scraper.py`  
  讀取上述網址清單，逐一解析每本書的 meta description 與價格資訊，同時內建延遲、重試機制以及 (選用) 手動暫停機制來降低連線問題。

- **Step 3:** `main.py`  
  將流程整合，最後輸出一份 `output/books.csv`，內容包含書籍網址、出版日期、ISBN、書籍類別、書名、作者、出版社、定價與優惠價等資訊。

## 參考程式碼

- [category_scraper.py](./category_scraper.py)
- [book_detail_scraper.py](./book_detail_scraper.py)
- [main.py](./main.py)
```
