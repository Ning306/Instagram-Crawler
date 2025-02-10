import json
import re
import os
import requests
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

# WebDriver 設定
options = webdriver.ChromeOptions()
# 設置 User-Agent 模擬真實的瀏覽器行為
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")  
options.add_argument("--start-maximized")  # 視窗最大化
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 資料儲存
listLink = []
listData = []
if not os.path.exists('images'):
    os.makedirs('images')

def random_sleep(min_time=2, max_time=5):
    """隨機睡眠時間，避免頻繁操作"""
    sleep(randint(min_time, max_time))


def login():
    try:
        driver.get(IG_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
        driver.find_element(By.NAME, 'username').send_keys(USERNAME)
        driver.find_element(By.NAME, 'password').send_keys(PASSWORD)
        random_sleep(5, 10)  # 隨機等待時間，模擬真實操作
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 等待導航列出現，確保登入成功
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'nav')))
        print("✅ 登入成功")
    except TimeoutException:
        print("❌ 登入失敗，請檢查帳號或密碼")
        driver.quit()

def visit():
    driver.get(IG_URL + IG_ACCOUNT)
    random_sleep(5, 10)  # 隨機等待時間，模擬真實操作

def get_post_links():
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/p/']")
        for index, element in enumerate(elements):
            if index >= 10:
                break
            listLink.append(element.get_attribute('href'))
        pprint(listLink)
    except Exception as e:
        print(f"❌ 抓取貼文連結失敗: {e}")

def parse():
    for link in listLink:
        image_set = set()
        driver.get(link)
        page_id = re.search(r'/p/([a-zA-Z0-9-_]+)/', link)[1]
        print(f"📌 貼文 ID: {page_id}")
        random_sleep(2, 5)  # 隨機等待時間，模擬真實操作
        
        while True:
            images = driver.find_elements(By.CSS_SELECTOR, 'img')
            for img in images:
                image_set.add(img.get_attribute("src"))
            
            next_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Next"]')
            if next_buttons:
                next_buttons[0].click()
                random_sleep(2, 5)  # 隨機等待時間，模擬真實操作
            else:
                break
        
        listData.append({
            "id": page_id,
            "url": link,
            "images": list(image_set)
        })

def save_json():
    with open("./ig_data.json", "w", encoding='utf-8') as fp:
        json.dump(listData, fp, ensure_ascii=False, indent=4)

def download_images():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://www.instagram.com/"
    }
    for post in listData:
        for idx, img_url in enumerate(post['images']):
            try:
                img_data = requests.get(img_url, headers=headers).content
                with open(f"images/{post['id']}_{idx}.jpg", 'wb') as f:
                    f.write(img_data)
                print(f"✅ 下載成功: {post['id']}_{idx}.jpg")
            except Exception as e:
                print(f"❌ 下載錯誤: {e}")

def close():
    driver.quit()

if __name__ == "__main__":
    login()
    visit()
    get_post_links()
    parse()
    save_json()
    download_images()
    close()