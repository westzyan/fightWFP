# coding: UTF-8
import requests
import urllib3
import logging
from requests.adapters import HTTPAdapter
from resource_scheduling import read_resource_data
urllib3.disable_warnings()
s = requests.session()
s.keep_alive = False
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}
# proxies = {
#     'http': 'socks5h://127.0.0.1:1080',
#     'https': 'socks5h://127.0.0.1:1080'
# }
# proxies = {
#     'http': 'http://127.0.0.1:12333',
#     'https': 'http://127.0.0.1:12333'
# }

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0'
}


def download_file(url, filename=None, filepath=None):
    if filename is None:
        filename = url.split('/')[-1]
    response = requests.get(url, headers=headers, proxies=proxies, verify=False)
    with open(filepath + "/" + filename, "wb") as file:
        file.write(response.content)
    file.close()


def get_resource(url, host=None):
    try:
        logger.info("host:%s,正在请求资源：%s", host, url)
        requests.get(url, headers=headers, proxies=proxies, verify=False, timeout=8)
        return 0
    except Exception as e:
        logger.error("请求资源失败：%s, error:%s", url, str(e))
        return 1


if __name__ == '__main__':
    import time

    time1 = time.time()
    download_file("https://youtube.com", filepath="/home/zyan/test")
    time2 = time.time()
    print("共用时：", time2 - time1)
