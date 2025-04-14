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
  將流程整合，最後輸出一份 `output/books.csv`，內容包含書籍網址、出版日期、書名、作者、出版社、定價與優惠價等資訊。

## 注意事項與除錯提示

### 延遲與重試
在 `book_detail_scraper.py` 中，每次請求書籍詳細資料前會有隨機延遲（2~5 秒），並搭配重試機制處理 ReadTimeout 或連線錯誤，以降低連線異常的風險。

### 手動暫停功能
若需要逐步偵錯，可取消 `book_detail_scraper.py` 中的 `input()` 註解，這樣每次請求前會等待使用者按下 Enter，再繼續執行。

### Chromedriver 路徑
請確認 `category_scraper.py` 中設定的 `chrome_binary` 與 `chromedriver_path` 是否符合你的系統環境，必要時請自行調整。

### 網路環境考量
如果發生連線被重設、ReadTimeout 等問題，建議增加延遲時間或檢查網路狀態，再次嘗試執行。

## 參考程式碼

- [category_scraper.py](./category_scraper.py)
- [book_detail_scraper.py](./book_detail_scraper.py)
- [main.py](./main.py)
```
