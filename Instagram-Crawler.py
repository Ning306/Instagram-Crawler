import json
import re
from time import sleep
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import requests

# Instagram 目標帳號
url = "https://www.instagram.com/"
ig_account = "dlwlrma"

# 加載 .env 文件中的變數（需創建 .env）
load_dotenv()

username = os.getenv('IG_USERNAME')
password = os.getenv('IG_PASSWORD')

dictJson = {
    "username": username,
    "password": password
}

# 初始化 WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # 視窗最大化
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 存放貼文連結 & 解析資料
listLink = []
listData = []

# 創建資料夾來存放圖片
if not os.path.exists('images'):
    os.makedirs('images')

def login():
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
        )

        # 輸入帳號 & 密碼
        driver.find_element(By.CSS_SELECTOR, 'input[name="username"]').send_keys(dictJson['username'])
        driver.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(dictJson['password'])

        sleep(2)  # 等待 2 秒

        # 點擊登入按鈕
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # 等待登入後頁面加載完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Feed"]'))
        )
        print("登入成功")

    except TimeoutException:
        print("等待逾時")
        driver.quit()

def visit():
    driver.get(url + ig_account)

def getUrl():
    try:
        for index, a in enumerate(driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")):
            if index == 10:  # 只抓 10 個貼文
                break
            listLink.append(a.get_attribute('href'))
        pprint(listLink)
    except Exception as e:
        print(f"抓取貼文連結時出錯: {e}")

def parse():
    for aLink in listLink:
        setTmp = set()
        driver.get(aLink)
        pageId = re.search(r'\/p\/([a-zA-Z0-9-_]+)\/', aLink)[1]
        print(f"網頁 id: {pageId}")

        sleep(2)
        while len(driver.find_elements(By.CSS_SELECTOR, "div._ab8w div._aao_ button._afxw")) > 0:
            driver.find_element(By.CSS_SELECTOR, "div._ab8w div._aao_ button._afxw").click()
            if len(driver.find_elements(By.CSS_SELECTOR, 'div._aa06[role="button"]')) > 0:
                for li in driver.find_elements(By.CSS_SELECTOR, 'div._aa06[role="button"]'):
                    img_url = li.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    setTmp.add(img_url)  # 儲存圖片 URL
        
        listData.append({
            "id": pageId,
            "url": aLink,
            "listDL": list(setTmp)
        })

# 保存爬取到的資料到 JSON
def saveJson():
    with open("./ig.json", "w", encoding='utf-8') as fp:
        json.dump(listData, fp, ensure_ascii=False, indent=4)

# 下載圖片
def download_images():
    for post in listData:
        for idx, img_url in enumerate(post['listDL']):
            try:
                # 使用 requests 下載圖片
                img_data = requests.get(img_url).content
                # 儲存圖片
                with open(f"images/{post['id']}_{idx}.jpg", 'wb') as f:
                    f.write(img_data)
                print(f"下載成功: {post['id']}_{idx}.jpg")
            except Exception as e:
                print(f"下載錯誤: {e}")

def close():
    driver.quit()

# 🚀 啟動流程
if __name__ == "__main__":
    login()       # 登入
    sleep(5)      # 等待登入完成
    visit()       # 瀏覽 IG 帳號
    sleep(5)      # 等待頁面加載
    getUrl()      # 取得貼文連結
    parse()       # 解析圖片 & 影片連結
    saveJson()    # 存成 JSON
    download_images()  # 下載圖片
    close()       # 關閉瀏覽器