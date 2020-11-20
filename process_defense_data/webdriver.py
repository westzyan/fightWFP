from selenium import webdriver
import time
import os

# 抓取命令，可以修改网卡名，保存地址，后面的&是为了后台运行
cmd1 = "tcpdump -i enp0s31f6 -w a.pcap &"
# 终止tcpdump的命令
cmd2 = "ps -ef | grep 'tcpdump -i' | grep -v grep | awk '{print $2}' | xargs kill -9"
os.system(cmd1)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=socks5://localhost:9150')
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.set_page_load_timeout(20)  # 设置超时时间，
browser.set_script_timeout(20)#这两种设置都进行才有效
a = browser.get('http://myip.ms')
# 打开之后，关闭tcpdump
os.system(cmd2)
