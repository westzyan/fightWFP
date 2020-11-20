from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
import time
import random
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_resource(url, number):
    num = random.randint(5, 20)
    time.sleep(num)
    logger.info("sleep: %s ,get resouce  url:%s, round: %s", num, url, number)
    return 0


def simulation_collect(url, round_number):
    # 模拟收集流量，并保存
    cmd = "tcpdump -i enp0s31f6 " + " -w " + str(round_number) + ".pcap"
    logger.info("cmd: %s, :round: %s", cmd, round_number)
    os.system(cmd)


def get_defense_traffic(number):
    executor = ProcessPoolExecutor(max_workers=10)
    logger.info("get traffic start round: %s", number)
    time.sleep(10)
    all_task = [executor.submit(get_resource, url, number) for url in range(1, 10)]
    for future in as_completed(all_task):
        data = future.result()


if __name__ == '__main__':
    # executor = ProcessPoolExecutor(max_workers=10)
    # for item in range(0, 5):
    #     executor.submit(simulation_collect, item, item)
    #     get_defense_traffic(item)
    #     time.sleep(15)
    #     cmd = "ps -ef | grep 'tcpdump -i' | grep -v grep | awk '{print $2}' | xargs kill -9"
    #     os.system(cmd)
    #     logger.info("第%s轮次终止了收集", item)
    #     time.sleep(2)
    # for i in range(10):
    #     print(random.randint(1, 10))
    import pandas as pd
    a = [
        [1,2,3,4,5,6],
        [3,6,9,5,2,]
    ]
    data = pd.DataFrame(data=a)
    data.to_csv("./b.csv", index=False, header=False)
    for i in a:
        print(i)
        print(str(i)[1:-1])