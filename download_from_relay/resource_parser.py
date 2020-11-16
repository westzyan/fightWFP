import re
import requests
import time
import urllib3
import logging
import os
from resource_scheduling import create_resource_data, save_resource_data, delete_resource_from_DB, read_resource_data
from concurrent.futures import ProcessPoolExecutor, as_completed
urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 输入网址url，获取对应的html
def get_html(url):
    proxies = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    # proxies = {
    #     'http': 'socks5h://127.0.0.1:9150',
    #     'https': 'socks5h://127.0.0.1:9150'
    # }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 '
                      'Safari/537.36 '
    }
    print(url)
    requests.DEFAULT_RETRIES = 5

    response = requests.get(url, headers=headers, proxies=proxies, verify=False)
    if response.status_code != 200:
        print(url, "status_code:", response.status_code)
        return ""
    print(response.status_code)
    html = str(response.text)
    return html


def match_resource(html):
    # 通过正则表达式获取网页资源，set去重并返回
    # 这里可以修改匹配规则，增加匹配规则
    # 目前只匹配 javascript 以及 css 资源，后期可能有[xml, html, jpg, jpeg, gif, png, svg, htm]
    js_set = set()
    css_set = set()

    patterns = [r"<link.*?href=\"(.*?)\"", r"src=\"(.*?)\""]
    for pattern in patterns:
        matchs = re.findall(pattern, html)
        print("matchs:", matchs)
        if matchs:
            for match in matchs:
                if '.js' in match and '.json' not in match:
                    js_set.add(str(match))
                if '.css' in match:
                    css_set.add(match)
    print(js_set)
    resources_list = [js_set, css_set]
    return resources_list


def url_fill(url, resources):
    # 填充非域名开头的资源连接，便于下载
    js_set = resources[0]
    css_set = resources[1]
    new_js_set = set()
    new_css_set = set()
    for item in js_set:
        if not item.startswith("http"):
            # 存在缺陷
            if item.startswith("//"):
                new_js_set.add("https:" + item)
            elif item.startswith("./"):
                new_js_set.add(url + item[1:])
            elif not item.startswith("/"):
                new_js_set.add(url + "/" + item)
            else:
                new_js_set.add(url + item)
        else:
            new_js_set.add(item)
    for item in css_set:
        if not item.startswith("http"):
            if item.startswith("//"):
                new_css_set.add("https:" + item)
            elif item.startswith("./"):
                new_css_set.add(url + item[1:])
            elif not item.startswith("/"):
                new_css_set.add(url + "/" + item)
            else:
                new_css_set.add(url + item)
        else:
            new_css_set.add(item)
    full_resources_list = [new_js_set, new_css_set]
    return full_resources_list


def download_file(url, filename=None, filepath=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0'
    }
    proxies = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    if filename is None:
        filename = url.split('/')[-1]
    response = requests.get(url, headers=headers, proxies=proxies, verify=False)
    with open(filepath + "/" + filename, "wb") as file:
        file.write(response.content)
    file.close()


def download_resource(resources_list):
    count = 0
    for item in resources_list:
        count += 1
        print("正在下载第", count)
        download_file(item[2], item[3], "../aleaxtop50/")
        print(item[2] + "下载完毕")


def download_resource_single(resource, i):
    logger.info("正在下载第%s个:%s", i, resource[2])
    download_file(resource[2], resource[3], "/media/zyan/文档/毕业设计/code/aleaxtop50/")
    logger.info("%s下载完毕", resource[2] )


if __name__ == '__main__':
    url_list = []
    save_list = []
    with open("../aleax_top.txt", "r") as f:
        for line in f.readlines():
            line = line.strip('\n')  # 去掉列表中每一个元素的换行符
            url_list.append(line)
    print(url_list)
    # url_list = ['https://www.tmall.com']
    for url in url_list:
        try:
            html = get_html(url)
            resources = match_resource(html)
            resources = url_fill(url, resources)
            print(url, resources)
            resource_list = create_resource_data(url, resources)
            save_list += resource_list
        except Exception as e:
            print(url, "遇到错误" + str(e))
    delete_resource_from_DB()
    time.sleep(5)
    save_resource_data(save_list)
    time.sleep(2)
    cmd = "rm -r /media/zyan/文档/毕业设计/code/aleaxtop50/*"
    os.system(cmd)
    r_list = read_resource_data()
    executor = ProcessPoolExecutor(max_workers=20)
    try:
        for i in range(len(r_list)):
            executor.submit(download_resource_single, r_list[i], i)
    except Exception as e:
        print(str(e))
    finally:
        executor.shutdown()



