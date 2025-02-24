import json
import re
import os
import requests
import mysql.connector
from time import sleep
from random import randint
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Instagram 目標帳號
IG_URL = "https://www.instagram.com/"
IG_ACCOUNT = "dlwlrma"

# 加載 .env 文件中的變數（需創建 .env）
load_dotenv()
USERNAME = os.getenv('IG_USERNAME')
PASSWORD = os.getenv('IG_PASSWORD')

# MySQL 連線設定
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "ig_scraper")

# WebDriver 設定
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
options.add_argument("--start-maximized")  
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 資料儲存
listLink = []
listData = []

if not os.path.exists('images'):
    os.makedirs('images')

# 連接 MySQL
def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def save_to_db(post_id, post_url, image_url):
    """儲存數據到 MySQL"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        sql = """
        INSERT INTO ig_posts (post_id, post_url, image_url) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE image_url = VALUES(image_url);
        """
        cursor.execute(sql, (post_id, post_url, image_url))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ 存入資料庫成功: {post_id}")
    except Exception as e:
        print(f"❌ 存入 MySQL 失敗: {e}")

def random_sleep(min_time=10, max_time=20):
    """隨機睡眠時間，避免頻繁操作"""
    sleep(randint(min_time, max_time))

def login():
    try:
        driver.get(IG_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
        driver.find_element(By.NAME, 'username').send_keys(USERNAME)
        driver.find_element(By.NAME, 'password').send_keys(PASSWORD)
        random_sleep(10, 30)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'nav')))
        print("✅ 登入成功")
    except TimeoutException:
        print("❌ 登入失敗，請檢查帳號或密碼")
        driver.quit()

def visit():
    driver.get(IG_URL + IG_ACCOUNT)
    random_sleep(10, 30)  

    # 滾動多次確保載入足夠的貼文
    for _ in range(5):  # 滾動 5 次
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_sleep(10, 30)  # 增加隨機等待時間，避免被封鎖)  # 等待 IG 加載更多內容



def get_post_links():
    try:
        # 滾動頁面確保載入更多貼文
        for _ in range(5):  # 滾動 5 次
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_sleep(10, 30)

        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        for index, element in enumerate(elements):
            if index >= 10:  # 限制最多抓取 10 個貼文
                break
            listLink.append("https://www.instagram.com" + element.get_attribute('href'))
        pprint(listLink)
    except Exception as e:
        print(f"❌ 抓取貼文連結失敗: {e}")

        

def parse():
    for link in listLink:
        image_set = set()
        driver.get(link)
        page_id = re.search(r'/p/([a-zA-Z0-9-_]+)/', link)[1]
        print(f"📌 貼文 ID: {page_id}")
        random_sleep(10, 30) # 隨機等待時間

        # 解析圖片
        images = driver.find_elements(By.CSS_SELECTOR, 'div._aagu img')
        for img in images:
            image_set.add(img.get_attribute("src"))

        listData.append({
            "id": page_id,
            "url": link,
            "images": list(image_set)
        })

def close():
    driver.quit()

if __name__ == "__main__":
    login()
    visit()
    get_post_links()
    parse()
    close()