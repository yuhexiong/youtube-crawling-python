from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
import os
import subprocess
import wget

my_options = webdriver.ChromeOptions()
my_options.add_argument("--start-maximized")         #最大化視窗
my_options.add_argument("--incognito")               #開啟無痕模式
my_options.add_argument("--disable-popup-blocking") #禁用彈出攔截
my_options.add_argument("--disable-notifications")  #取消 chrome 推播通知
my_options.add_argument("--lang=zh-TW")  #設定為正體中文

driver = webdriver.Chrome(
    options = my_options,
    service = Service(ChromeDriverManager().install())
)

if __name__ == '__main__':
    driver.get('https://www.youtube.com/')

    txtInput = driver.find_element(By.CSS_SELECTOR, "input#search")
    txtInput.send_keys("あいみょん")

    sleep(1)
    txtInput.submit()
    
    sleep(5)

    innerHeight = 0
    offset = 0 # 也可修改每次滑的距離
    
    while True:
        # 每次移動高度設定成網頁高度
        offset = driver.execute_script('return window.document.documentElement.scrollHeight;')

        driver.execute_script(f"window.scrollTo({{top: {offset}, behavior: 'smooth'}});")
        sleep(3)
        
        # 取得目前高度
        innerHeight = driver.execute_script('return window.document.documentElement.scrollHeight;')
        
        # 設置希望停止的高度 或 已經滑到底
        if offset >= 3000 or offset == innerHeight:
            break

    # 取得每一筆資訊
    youtubeRenderers = driver.find_elements(
        By.CSS_SELECTOR, 
        'ytd-video-renderer.style-scope.ytd-item-section-renderer'
    )
    
    linkInfo = []
    for youtubeRenderer in youtubeRenderers:
        # 取得資料名稱
        a = youtubeRenderer.find_element(By.CSS_SELECTOR, "a#video-title")
        aTitle = a.get_attribute('innerText')
        aLink = a.get_attribute('href')
        
        linkInfo.append({
            "linkTitle": aTitle.replace(' ', ''),
            "link": aLink
        })

    driver.quit()

    # 下載影片
    # 參考 https://github.com/yt-dlp/yt-dlp 以下為windows的下載點
    if not os.path.exists('./yt-dlp.exe'):
        wget.download('https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe', './yt-dlp.exe')
    
    folderPath = 'data'
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    for index, obj in enumerate(linkInfo[:5]):
        # 解析id中文字
        idEncoded = obj['linkTitle'].encode('utf-8').decode('utf-8', 'ignore')

        # 設定下command
        cmd = [
            './yt-dlp.exe', 
            obj['link'], 
            '-f', 'b[ext=mp4]', 
            '-o', f'{folderPath}/{idEncoded}.%(ext)s'
        ]
        result = subprocess.run(cmd)

        if result.returncode == 0:
            print(f"{obj['linkTitle']} download successfully")
        else:
            print(f"{obj['linkTitle']} download failed")