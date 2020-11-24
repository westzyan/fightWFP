# coding=utf-8
from selenium import webdriver
import time
import os

list = ["https://www.Reddit.com", "https://www.Myshopify.com", "https://www.Ebay.com", "https://www.Office.com",
        "https://www.Instructure.com", "https://www.Netflix.com", "https://www.Cnn.com", "https://www.Bing.com",
        "https://www.Live.com", "https://www.Microsoft.com", "https://www.Nytimes.com", "https://www.Twitch.tv",
        "https://www.Apple.com", "https://www.Instagram.com", "https://www.Microsoftonline.com",
        "https://www.Walmart.com", "https://www.Chaturbate.com", "https://www.Espn.com", "https://www.Zillow.com",
        "https://www.Salesforce.com", "https://www.Etsy.com", "https://www.Chase.com", "https://www.Dropbox.com",
        "https://www.Linkedin.com", "https://www.Adobe.com", "https://www.Foxnews.com", "https://www.Twitter.com",
        "https://www.Okta.com", "https://www.Force.com", "https://www.Craigslist.org", "https://www.Quizlet.com",
        "https://www.Aliexpress.com", "https://www.Bestbuy.com", "https://www.Livejasmin.com",
        "https://www.Amazonaws.com", "https://www.Wellsfargo.com", "https://www.Tmall.com", "https://www.Breitbart.com",
        "https://www.Hulu.com", "https://www.Target.com", "https://www.Indeed.com", "https://www.Imdb.com"]
# cmd2 = "ps -ef | grep 'tcpdump -i' | grep -v grep | cut -c 9-15 | xargs kill -s 9"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=socks5://localhost:9150')
chrome_options.add_argument("enable-automation")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--dns-prefetch-disable")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("service_args=[’–ignore-ssl-errors=true’, ‘–ssl-protocol=TLSv1’]")
browser = webdriver.Chrome(chrome_options=chrome_options)
# browser.set_page_load_timeout(20)  # 设置超时时间，
# browser.set_script_timeout(20)  # 这两种设置都进行才有效



for j in range(10):
    cmd1 = "tcpdump  -i enp0s31f6 -w a" + str(j) + ".pcap &"
    cmd2 = "ps -ef | grep 'tcpdump' | grep -v grep | awk '{print $2}' | xargs kill -9"
    # print(cmd1)
    os.system(cmd1)
    a = browser.get(list[j])
    # 打开之后，关闭tcpdump
    os.system(cmd2)
    time.sleep(2)
