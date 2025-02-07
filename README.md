# Instagram Crawler

這是一個用於爬取 Instagram 帳號貼文資料的爬蟲程式，能夠自動登入、抓取指定帳號的貼文，並下載相關的圖片。

## 功能

- **登入 Instagram 帳號**：使用提供的帳號密碼進行登入。
- **爬取指定 Instagram 帳號的貼文連結**：取得最多 10 筆貼文的 URL。
- **解析貼文中的圖片 URL**：抓取每個貼文中的圖片 URL。
- **下載圖片**：將抓取到的圖片下載到本地儲存。
- **儲存資料**：將所有抓取的貼文資料存成 JSON 檔案。

## 安裝與使用

### 1. 克隆專案

```bash
git clone https://github.com/yourusername/InstaScraper.git
cd InstaScraper
```
### 2. 創建虛擬環境並安裝依賴
```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```
### 3.	配置環境變數
創建 .env 檔案，並在其中加入你的 Instagram 帳號和密碼：
```bash
IG_USERNAME=你的Instagram帳號
IG_PASSWORD=你的Instagram密碼
```
### 4.	執行
```bash
python Instagram-Crawler.py
```
