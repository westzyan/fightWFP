import os
import configparser
import os
import logging
import csv
import pandas as pd
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 获取当前文件所在目录的上一级目录，即项目所在目录
root_dir = os.path.dirname(os.path.abspath('.'))
configpath = os.path.join(root_dir, "config.ini")
cf = configparser.ConfigParser()
cf.read(configpath)

parse_layer = cf.get("trace_parse", "layer")
remote_ip = cf.get("trace_parse", "remote_ip")
remote_port = cf.get("trace_parse", "remote_port")
save_filepath = cf.get("trace_parse", "save_filepath")
save_ttdl_filepath = cf.get("trace_parse", "save_ttdl_filepath")
origin_filepath = cf.get("trace_parse", "origin_filepath")
web_num_dict = {'adobe.com': '0', 'aliexpress.com': '1', 'amazon.com': '2', 'apple.com': '3', 'baidu.com': '4',
                'bing.com': '5', 'breitbart.com': '6', 'chaturbate.com': '7', 'cnn.com': '8', 'craigslist.org': '9',
                'csdn.net': '10', 'dropbox.com': '11', 'ebay.com': '12', 'espn.com': '13', 'etsy.com': '14',
                'foxnews.com': '15', 'hulu.com': '16', 'imdb.com': '17', 'indeed.com': '18', 'instagram.com': '19',
                'jd.com': '20', 'live.com': '21', 'livejasmin.com': '22', 'microsoft.com': '23', 'naver.com': '24',
                'netflix.com': '25', 'nytimes.com': '26', 'office.com': '27', 'okezone.com': '28', 'okta.com': '29',
                'qq.com': '30', 'reddit.com': '31', 'salesforce.com': '32', 'sina.com.cn': '33', 'sohu.com': '34',
                'stackoverflow.com': '35', 'tribunnews.com': '36', 'twitch.tv': '37', 'twitter.com': '38',
                'vk.com': '39', 'walmart.com': '40', 'washingtonpost.com': '41', 'wellsfargo.com': '42',
                'wikipedia.org': '43', 'www.alipay.com': '44', 'yahoo.com': '45', 'yandex.ru': '46',
                'youtube.com': '47', 'zhanqi.tv': '48', 'zillow.com': '49'}

local_ip_start = ["10.", "192."]

def read_trace_locations():
    dict = {}
    with open("./trace_num_locations.txt", "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            tmp = line.split(",")
            dict[tmp[0]] = int(tmp[1])
    f.close()
    return dict

def save_trace_locations(dict):
    with open("./trace_num_locations.txt", "w") as f:
        for key in dict.keys():
            f.write(key + "," + str(dict.get(key)) + "\n")
    f.close()

def temp():
    filepath = "/media/zyan/文档/毕业设计/code/origin_traffic/round3/"
    # for root, dirs, files in os.walk(filepath):
    #     print(root)  # 当前目录路径
    #     print(dirs)  # 当前路径下所有子目录
    #     print(files)  # 当前路径下所有非目录子文件
    print(os.listdir(filepath))
    files = os.listdir(filepath)
    for file in files:
        new_name = file.split("_")[0] + ".pcap"
        cmd = "mv " + filepath + file + " " + filepath + new_name
        print(cmd)
        os.system(cmd)

def temp1():
    url_list = []
    with open("../aleax_top.txt", "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            line = line.split("/")[-1]
            url_list.append(line)
    web_number_dict = {}
    count = 0
    for i in url_list:
        web_number_dict[i] = 0
        count += 1
    print(web_number_dict)

def temp2():
    filepath = "/media/zyan/文档/毕业设计/code/origin_traffic/round3/"
    # for root, dirs, files in os.walk(filepath):
    #     print(root)  # 当前目录路径
    #     print(dirs)  # 当前路径下所有子目录
    #     print(files)  # 当前路径下所有非目录子文件
    print(os.listdir(filepath))
    files = os.listdir(filepath)
    for file in files:
        new_name = file.split("_")[0] + ".pcap"
        cmd = "mv " + filepath + file + " " + filepath + new_name
        print(cmd)
        os.system(cmd)

def parse_trace():
    '''
    将原始pcap文件转换为csv文件，csv文件内容为源IP，源端口，目的IP，目的端口，时间戳，长度
    trace_location_dict记录每个网站下次要保存的文件的number，由于记录number，暂时单线程
    :return:
    '''
    trace_location_dict = read_trace_locations()
    filepath = origin_filepath
    dirs = os.listdir(filepath)
    list.sort(dirs)
    for dir in dirs:
        full_dir = filepath + dir
        files = os.listdir(full_dir)
        list.sort(files)
        for file in files:
            full_file = full_dir + "/" + file
            logger.info("parse file: %s", full_file)
            web_num = web_num_dict.get(file[:-5])
            trace_num = trace_location_dict.get(file[:-5])
            cmd = 'tshark  -r ' + full_file + '  -T fields -Y "tcp.port==' + remote_port + ' " -E separator=, -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport  -e frame.time_epoch -e frame.len > ' + save_filepath + str(web_num) + '/' + str(trace_num) + '.csv'
            os.system(cmd)
            trace_location_dict[file[:-5]] = trace_num + 1
            logger.info(cmd)
    save_trace_locations(trace_location_dict)


def parse_trace_single_dir(dir):
    filepath = origin_filepath
    full_dir = filepath + dir
    files = os.listdir(full_dir)
    for file in files:
        full_file = full_dir + "/" + file
        logger.info("parse file: %s", full_file)
        web_num = web_num_dict.get(file[:-5])
        trace_num = dir[5:]
        cmd = 'tshark  -r ' + full_file + '  -T fields -Y "tcp.port==' + remote_port + ' " -E separator=, -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport  -e frame.time_epoch -e frame.len > ' + save_filepath + str(
            web_num) + '/' + str(trace_num) + '.csv'
        os.system(cmd)
        logger.info(cmd)


def parse_trace_mul_thread():
    '''
    将原始pcap文件转换为csv文件，csv文件内容为源IP，源端口，目的IP，目的端口，时间戳，长度
    trace_location_dict记录每个网站下次要保存的文件的number，由于记录number，暂时单线程
    :return:
    '''
    filepath = origin_filepath
    dirs = os.listdir(filepath)
    executor = ProcessPoolExecutor(max_workers=30)
    for dir in dirs:
        executor.submit(parse_trace_single_dir, dir)
    executor.shutdown()



def extract_trace_files(dir):
    '''
    将parse_trace一个目录下的csv文件，提取对应的特征信息，包含时间【从0开始】，方向，大小
    :param files:
    :return:
    '''
    remote_port_list = ["60868", "60858"]
    input_filepath = save_filepath
    output_filepath = save_ttdl_filepath
    files = os.listdir(input_filepath + "/" + dir)
    for file in files:
        try:
            full_file = save_filepath + dir + "/" + file
            logger.info("开始读取文件:%s", full_file)
            with open(full_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            f.close()
            standard_time = rows[0][-2]
            new_rows = []
            for row in rows:
                src_port = row[1]
                timestamp = float(row[4]) - float(standard_time)
                len = row[5]
                if src_port not in remote_port_list :
                    new_rows.append(str(timestamp) + ",+" + str(len))
                else:
                    new_rows.append(str(timestamp) + ",-" + str(len))
            full_save_file = output_filepath + dir + "/" + file
            logger.info("开始写入文件:%s", full_save_file)
            with open(full_save_file, 'w') as f:
                for row in new_rows:
                    f.write(row + "\n")
            f.close()

            logger.info("写入文件完毕:%s", full_save_file)
        except Exception as e:
            logger.error("文件失败：%s", file)

def extract_trace():
    '''
    提取trace流
    :return:
    '''
    executor = ProcessPoolExecutor(max_workers=30)
    dirs = os.listdir(save_filepath)
    logger.info("dirs: %s", dirs)
    for dir in dirs:
        executor.submit(extract_trace_files, dir)
    executor.shutdown()

def extract_feature_single_dir(dir):
    last_list = []
    input_filepath = save_ttdl_filepath
    files = os.listdir(input_filepath + "/" + dir)
    for file in files:
        last_single_list = [0] * 5000
        origin_single_list = []
        full_file = input_filepath + dir + "/" + file
        logger.info("开始读取文件:%s", full_file)
        with open(full_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        f.close()
        for row in rows:
            if row[1][0] == "+":
                origin_single_list.append(1)
            else:
                origin_single_list.append(-1)
        origin_length = 0
        if len(origin_single_list) < 5000:
            origin_length = len(origin_single_list)
        else:
            origin_length = 5000
        for i in range(origin_length):
            last_single_list[i] = origin_single_list[i]
        last_single_list.append(int(dir))
        last_list.append(last_single_list)
        logger.info("file %s, len: %s", full_file,len(last_list))
    return last_list

def extract_feature_single_dir_simulator(dir):
    last_list = []
    input_filepath = save_ttdl_filepath
    files = os.listdir(input_filepath + "/" + dir)
    for file in files:
        last_single_list = [0] * 5000
        origin_single_list = []
        full_file = input_filepath + dir + "/" + file
        # logger.info("开始读取文件:%s", full_file)
        with open(full_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        f.close()
        random.shuffle(rows)
        for row in rows:
            if row[1][0] == "+":
                origin_single_list.append(1)
            else:
                origin_single_list.append(-1)
        origin_length = 0
        if len(origin_single_list) < 5000:
            origin_length = len(origin_single_list)
        else:
            origin_length = 5000
        for i in range(origin_length):
            last_single_list[i] = origin_single_list[i]
        last_single_list.append(int(dir))
        last_list.append(last_single_list)
    logger.info("file %s, len: %s", input_filepath + "/" + dir,len(last_list))
    return last_list


def extract_feature():
    executor = ProcessPoolExecutor(max_workers=30)
    input_filepath = save_ttdl_filepath
    dirs = os.listdir(input_filepath)
    logger.info("dirs: %s", dirs)
    all_task = [executor.submit(extract_feature_single_dir_simulator, dir) for dir in dirs]
    last_list = []
    for future in as_completed(all_task):
        single_list = future.result()
        last_list = last_list + single_list
    print(len(last_list))
    executor.shutdown()
    data = pd.DataFrame(data=last_list)
    data.to_csv("/media/zyan/文档/毕业设计/code/dataset/round2/df_tcp_10000_round2.csv", index=False, header=False)


# a = {'adobe.com': 0, 'aliexpress.com': 0, 'amazon.com': 0, 'apple.com': 0, 'baidu.com': 0, 'bing.com': 0, 'breitbart.com': 0, 'chaturbate.com': 0, 'cnn.com': 0, 'craigslist.org': 0, 'csdn.net': 0, 'dropbox.com': 0, 'ebay.com': 0, 'espn.com': 0, 'etsy.com': 0, 'foxnews.com': 0, 'hulu.com': 0, 'imdb.com': 0, 'indeed.com': 0, 'instagram.com': 0, 'jd.com': 0, 'live.com': 0, 'livejasmin.com': 0, 'microsoft.com': 0, 'naver.com': 0, 'netflix.com': 0, 'nytimes.com': 0, 'office.com': 0, 'okezone.com': 0, 'okta.com': 0, 'qq.com': 0, 'reddit.com': 0, 'salesforce.com': 0, 'sina.com.cn': 0, 'sohu.com': 0, 'stackoverflow.com': 0, 'tribunnews.com': 0, 'twitch.tv': 0, 'twitter.com': 0, 'vk.com': 0, 'walmart.com': 0, 'washingtonpost.com': 0, 'wellsfargo.com': 0, 'wikipedia.org': 0, 'www.alipay.com': 0, 'yahoo.com': 0, 'yandex.ru': 0, 'youtube.com': 0, 'zhanqi.tv': 0, 'zillow.com': 0}
# save_trace_locations(a)


def extract_trace_files_test(dir):
    '''
    将parse_trace一个目录下的csv文件，提取对应的特征信息，包含时间【从0开始】，方向，大小
    :param files:
    :return:
    '''
    input_filepath = save_filepath
    output_filepath = save_ttdl_filepath
    files = os.listdir(input_filepath + "/" + dir)
    for file in files:
        full_file = save_filepath + dir + "/" + file
        logger.info("开始读取文件:%s", full_file)
        with open(full_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        f.close()
        standard_time = rows[0][-2]
        new_rows = []
        for row in rows:
            src_ip = row[0]
            timestamp = float(row[4]) - float(standard_time)
            len = row[5]
            if src_ip.startswith(local_ip_start[0]) or src_ip.startswith(local_ip_start[1]):
                new_rows.append(str(timestamp) + ",+" + str(len))
            else:
                new_rows.append(str(timestamp) + ",-" + str(len))
        full_save_file = output_filepath + dir + "/" + file
        logger.info("开始写入文件:%s", full_save_file)
        with open(full_save_file, 'w') as f:
            for row in new_rows:
                f.write(row + "\n")
        f.close()

        logger.info("写入文件完毕:%s", full_save_file)



if __name__ == '__main__':
    parse_trace_mul_thread()
    # extract_trace()
    # extract_feature()


