import re
import requests
import time
import urllib3
from directory_server_util.resource_scheduling import create_resource_data, save_resource_data

urllib3.disable_warnings()


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
            else:
                new_css_set.add(url + item)
        else:
            new_css_set.add(item)
    full_resources_list = [new_js_set, new_css_set]
    return full_resources_list


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
    save_resource_data(save_list)

