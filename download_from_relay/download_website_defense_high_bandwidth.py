import re
import requests
import urllib3
import logging
import random
import copy
import time
import configparser
import os
from DB_utils import get_resource_from_DB, get_resource_from_DB_by_website
from download_util import get_resource
from download_util import headers, proxies
from concurrent.futures import ProcessPoolExecutor, as_completed

from requests.adapters import HTTPAdapter

urllib3.disable_warnings()
s = requests.session()
s.keep_alive = True
s.mount('http://', HTTPAdapter(max_retries=1))
s.mount('https://', HTTPAdapter(max_retries=1))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

start_white_list = ["android-app:", "ios-app", "https://accounts.google.com/ServiceLogin?", "https:&#x2F;",
                    "//creativecommons", "https://chrome.google.com/webstore", "'+m[0].params.src+'", "'+r"]
end_white_list = ["/", ".com", ".mp4", ".mp3", ".net", ".org", ".cn", ".us", "p=iframe-alerts", ".ms", "/en-us"]

root_dir = os.path.dirname(os.path.abspath('.'))  # 获取当前文件所在目录的上一级目录，即项目所在目录E:\Crawler
configpath = os.path.join(root_dir, "config.ini")
cf = configparser.ConfigParser()
cf.read(configpath)  # 读取配置文件

eth_name = cf.get("eth", "name")
filepath = cf.get("eth", "path")
round_start = int(cf.get("eth", "start"))
round_end = int(cf.get("eth", "end"))
param = float(cf.get("eth", "param"))

def get_origin_website_html(url):
    logger.info("下载原始HTML，%s", url)
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



def search_resource_in_relay_param(host, resource_list, param):
    '''
    将解析到的资源列表拆分为两部分：可以在中继上下载的资源， 不能在中继上下载的资源
    根据参数，即在中继上下载资源数目占所有资源的比例，进行下一步拆分
    origin_set length: ori_len
    relay_resource_set: relay_len
    if relay_len < resource_len * param:
        relay_resource_set 全部随机在中继上补全URL
    else
        relay_resource_set 拆分成两个set,一个长度为resource_len * param，另一个长度为relay_len - resource_len * param
        长度为resource_len * param的，转换为带随机中继IP的完整URL，另一个set和origin_set合并，并填充为带原始域名的完整URL
    返回两个完整集合
    :param host: 域名
    :param resource_list: 资源集合
    :param param: 参数，即在中继上下载资源数目占所有资源的比例
    :return:
    '''
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
    logger.info("resource_list len: %s", len(resource_list))
    logger.info("origin_set len: %s", len(origin_set))
    logger.info("relay_resource_set len: %s", len(relay_resource_set))
    # 对origin_set里面元素进行填充，得到完整的URL，存到origin_full_set
    for item in origin_set:
        full_resource_url = fill_url(host, item)
        origin_full_set.add(full_resource_url)
    valid_len = len(origin_set) + len(relay_resource_set)
    if len(relay_resource_set) < valid_len * param:
        for item in relay_resource_set:
            value_list = DB_dict.get(item, "none")
            ip_list = value_list[1][1:-1].split(",")
            random_ip = random.choice(ip_list)
            full_resource_url = "http://" + random_ip + "/param/" + value_list[0]
            relay_full_set.add(full_resource_url)
    else:
        relay_resource_set = list(relay_resource_set)
        random.shuffle(relay_resource_set)
        true_relay_resource_set = relay_resource_set[0:int(valid_len * param)]
        false_relay_resource_set = relay_resource_set[int(valid_len * param):]
        for item in false_relay_resource_set:
            full_resource_url = fill_url(host, item)
            origin_full_set.add(full_resource_url)
        for item in true_relay_resource_set:
            value_list = DB_dict.get(item, "none")
            ip_list = value_list[1][1:-1].split(",")
            random_ip = random.choice(ip_list)
            full_resource_url = "http://" + random_ip + "/param/" + value_list[0]
            relay_full_set.add(full_resource_url)
    logger.info("origin_full_set len: %s", len(origin_full_set))
    logger.info("relay_full_set len: %s", len(relay_full_set))
    return origin_full_set, relay_full_set



def simulation_collect(url, round_number):
    # 模拟收集流量，并保存
    cmd = "tcpdump -i " + eth_name + " -w " + filepath + "round" + str(round_number) + "/" + url.split("/")[
        -1] + ".pcap &"
    logger.info(cmd)
    os.system(cmd)


def mkdir_save(filepath):
    for item in range(100):
        path = filepath + "/round" + str(item)
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        is_exists = os.path.exists(path)
        if not is_exists:
            os.makedirs(path)



if __name__ == '__main__':
    # 引入参数阿尔法，代表在中继节点上取资源的比例
    param_a = param
    url_list = []
    with open("../aleax_top.txt", "r") as f:
        for line in f.readlines():
            line = line.strip('\n')  # 去掉列表中每一个元素的换行符
            url_list.append(line)
    print(url_list)
    url_confusion_list = []
    with open("../aleax_confusion.txt", "r") as f:
        for line in f.readlines():
            line = line.strip('\n')  # 去掉列表中每一个元素的换行符
            url_confusion_list.append(line)
    print(url_confusion_list)
    f.close()
    mkdir_save(filepath)
    executor = ProcessPoolExecutor(max_workers=40)
    error_list = []
    for i in range(round_start, round_end):
        logger.info("开始第%s轮次捕获", i + 1)
        for item in url_list:
            simulation_collect(item, i)
            try:
                host = item
                # 获取原始HTML文本
                logger.info("%s start:", host)
                html = get_origin_website_html(host)
                executor.submit(get_origin_website_html, random.choice(url_confusion_list))
                executor.submit(get_origin_website_html, random.choice(url_confusion_list))
                executor.submit(get_origin_website_html, random.choice(url_confusion_list))
                logger.info("获取到原始HTML")
                # 初步解析里面的资源
                resources = parse_web_resource(html)
                logger.info("解析了所有资源")
                # 去除非法资源，分类不同下载渠道的资源，并填充对应的url,使得可以直接下载
                origin_set, relay_resource_set = search_resource_in_relay_param(host, resources, param_a)
                tmp1 = list(origin_set)
                tmp2 = list(relay_resource_set)
                last_list = tmp1 + tmp2
                random.shuffle(last_list)
                all_task = [executor.submit(get_resource, url, host) for url in last_list]
                for future in as_completed(all_task):
                    data = future.result()
            except Exception as e:
                error_list.append(str(i) + " " + item)
                logger.error("%s 遇到错误：%s", item, str(e))
            cmd = "ps -ef | grep 'tcpdump -i' | grep -v grep | awk '{print $2}' | xargs kill -9"
            logger.info("%s 抓取完毕", item)
            os.system(cmd)
            time.sleep(2)
        time.sleep(3)
        logger.info("结束第%s轮次捕获", i + 1)
    executor.shutdown()
    for item in error_list:
        print(item)
