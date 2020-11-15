import re
import requests
import urllib3
import logging
import random
import copy
import time
from get_resource_location_pool import get_resource_from_DB, get_resource_from_DB_by_website
from download_util import get_resource
from download_util import headers, proxies
from concurrent.futures import ProcessPoolExecutor, as_completed

urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


start_white_list = ["android-app:", "ios-app", "https://accounts.google.com/ServiceLogin?", "https:&#x2F;",
                    "//creativecommons", "https://chrome.google.com/webstore", "'+m[0].params.src+'", "'+r"]
end_white_list = ["/", ".com", ".mp4", ".mp3", ".net", ".org", ".cn", ".us", "p=iframe-alerts", ".ms", "/en-us"]


def get_origin_website_html(url):
    response = requests.get(url, headers=headers, proxies=proxies, verify=False)
    if response.status_code != 200:
        logger.error("下载原始HTML遇到错误，status_code: %s", response.status_code)
    return str(response.text)


def parse_web_resource(html):
    regex = [r"<link.*?href=\"(.*?)\"", r"src=\"(.*?)\""]
    resource_list = []
    for item in regex:
        matchs = re.findall(item, html)
        resource_list = resource_list + matchs
    resource_list = set(resource_list)
    return resource_list


def search_resource_in_relay(host, resource_list):
    """
    输入域名和解析到的资源列表，然后去数据库查找对应的修改后的文件地址，分离正常文件和修改后的文件
    :param host:
    :param resource_list:
    :return:
    """
    relay_resource_set = set()
    normal_set = set(copy.deepcopy(resource_list))
    origin_set = set()
    remove_flag = False
    for resource in resource_list:
        if resource == "":
            normal_set.remove("")
            continue
        result = get_resource_from_DB(resource, False)
        if result != 0:
            # 找到修改后资源所在位置，并放到set里面
            tmp1 = str(result.locations)[1:-1]
            tmp2 = tmp1.split(",")
            ip = random.choice(tmp2)
            relay_resource_set.add("http://" + ip + "/" + result.resource)
        else:
            # 先去除非正常资源
            remove_flag = False
            for start_item in start_white_list:
                if resource.startswith(start_item):
                    remove_flag = True
                    break
            for end_item in end_white_list:
                if resource.endswith(end_item):
                    remove_flag = True
                    break
            if remove_flag is True:
                normal_set.remove(resource)
    for item in normal_set:
        full_resource_url = fill_url(host, item)
        origin_set.add(full_resource_url)
    normal_set.clear()
    return origin_set, relay_resource_set


def fill_url(host, part_url):
    """
    补全URL
    :param part_url:
    :param host:
    :return:
    """
    if not part_url.startswith("http"):
        if part_url.startswith("//"):
            full_url = "https:" + part_url
        elif part_url.startswith("./"):
            full_url = "https:" + part_url[1:]
        elif not part_url.startswith("/"):
            full_url = host + "/" + part_url
        else:
            full_url = host + part_url
    else:
        full_url = part_url
    return full_url


def simulation_browsing_website(host, filepath):
    # 获取原始HTML文本
    logger.info("%s start: %s", host, time.time())
    html = get_origin_website_html(host)
    # 初步解析里面的资源
    logger.info("获取到原始HTML: %s", time.time())
    resources = parse_web_resource(html)
    logger.info("解析了所有资源: %s", time.time())
    # 去除非法资源，分类不同下载渠道的资源，并填充对应的url,使得可以直接下载
    origin_set, relay_resource_set = search_resource_in_relay(host, resources)
    logger.info("获取到了所有的URL: %s", time.time())
    resource_list = [origin_set, relay_resource_set]
    for resource_set in resource_list:
        for resource in resource_set:
            # download_file(resource, filename=None, filepath=filepath)
            get_resource(resource)
            print(resource)
    logger.info("完成: %s", time.time())


def search_resource_in_relay2(host, resource_list):
    relay_resource_set = set()
    # 过滤开头
    # 保存无效url
    tmp_set = set()
    # 保存能在目录服务器中查找到的URL
    origin_set = set()
    # 获取到原始读取数据
    DB_set = get_resource_from_DB_by_website(host)
    DB_dict = {}
    for item in DB_set:
        DB_dict[item[2]] = [item[3], item[4]]
    for SR in resource_list:
        if SR == "":
            tmp_set.add("")
            continue
        for start_item in start_white_list:
            if SR.startswith(start_item):
                tmp_set.add(SR)
                break
        for end_item in end_white_list:
            if SR.endswith(end_item):
                tmp_set.add(SR)
                break
        if DB_dict.get(SR, "none") != "none":
            relay_resource_set.add(SR)
    # 暂存差集
    tmp2_set = set(resource_list).difference(tmp_set)
    # origin_set 得到需要从原始网站下载的不完整URL
    origin_set = tmp2_set.difference(relay_resource_set)

    origin_full_set = set()
    relay_full_set = set()
    # 对origin_set里面元素进行填充，得到完整的URL，存到origin_full_set
    for item in origin_set:
        full_resource_url = fill_url(host, item)
        origin_full_set.add(full_resource_url)
    # 对relay_resource_set里面数据处理，即获取IP以及资源名称，得到完整的URL路径
    for item in relay_resource_set:
        value_list = DB_dict.get(item, "none")
        ip_list = value_list[1][1:-1].split(",")
        random_ip = random.choice(ip_list)
        full_resource_url = "http://" + random_ip + "/" + value_list[0]
        relay_full_set.add(full_resource_url)
    return origin_full_set, relay_full_set


def get_defense_traffic(host):
    # 获取原始HTML文本
    logger.info("%s start:", host)
    html = get_origin_website_html(host)
    logger.info("获取到原始HTML")
    # 初步解析里面的资源
    resources = parse_web_resource(html)
    logger.info("解析了所有资源")
    # for item in resources:
    #     print(item)
    # print("-------------------------------------")
    # 去除非法资源，分类不同下载渠道的资源，并填充对应的url,使得可以直接下载
    origin_set, relay_resource_set = search_resource_in_relay2(host, resources)
    tmp1 = list(origin_set)
    tmp2 = list(relay_resource_set)
    last_list = tmp1 + tmp2
    executor = ProcessPoolExecutor(max_workers=10)
    # for item in origin_set:
    #     future = executor.submit(get_resource, item, host)
    # for item in relay_resource_set:
    #     future = executor.submit(get_resource, item, host)

    all_task = [executor.submit(get_resource, url, host) for url in last_list]
    for future in as_completed(all_task):
        data = future.result()


import configparser
import os

root_dir = os.path.dirname(os.path.abspath('.'))  # 获取当前文件所在目录的上一级目录，即项目所在目录E:\Crawler
configpath = os.path.join(root_dir, "config.ini")
cf = configparser.ConfigParser()
cf.read(configpath)  # 读取配置文件

eth_name = cf.get("eth", "name")
filepath = cf.get("eth", "path")


def simulation_collect(url, round):
    # 模拟收集流量，并保存
    cmd = "tcpdump -i " + eth_name + " -w " + filepath + url.split("/")[-1] + "_" + str(round) + ".pcap"
    logger.info(cmd)
    os.system(cmd)


if __name__ == '__main__':
    # host = "https://amazon.com"
    # # 获取原始HTML文本
    # html = get_origin_website_html(host)
    # # 初步解析里面的资源
    # resources = parse_web_resource(html)
    # for item in resources:
    #     print(item)
    # print("-------------------------------------")
    # # 去除非法资源，分类不同下载渠道的资源，并填充对应的url,使得可以直接下载
    # origin_set, relay_resource_set = search_resource_in_relay2(host, resources)
    # print("-------------------------------------")
    # for item in origin_set:
    #     print(item)
    #     get_resource(item)
    # print("---------------------------------------")
    # for item in relay_resource_set:
    #     print(item)
    #     get_resource(item)
    # time1 = time.time()
    # simulation_browsing_website("http://youtube.com", "/home/zyan/test")
    # time2 = time.time()
    # print("共用时：", time2 - time1)
    # a = "fdasfaf"
    # print(a[1:-1])
    # time1 = time.time()
    # get_defense_traffic("https://adobe.com")
    # time2 = time.time()
    # print("共用时：", time2 - time1)
    url_list = []
    with open("../aleax_top.txt", "r") as f:
        for line in f.readlines():
            line = line.strip('\n')  # 去掉列表中每一个元素的换行符
            url_list.append(line)
    print(url_list)
    executor = ProcessPoolExecutor(max_workers=10)
    for item in url_list:
        executor.submit(simulation_collect, item, 7)
        try:
            get_defense_traffic(item)
        except Exception as e:
            logger.error("%s 遇到错误：%s", item, str(e))
        time.sleep(20)
        cmd = "ps -ef | grep 'tcpdump -i' | grep -v grep | awk '{print $2}' | xargs kill -9"
        os.system(cmd)
        time.sleep(2)
