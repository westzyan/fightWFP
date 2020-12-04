from ServerResource import ServerResource
import uuid
import pymysql
import configparser
import os
from DBUtils.PooledDB import PooledDB
from random import choice
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

root_dir = os.path.dirname(os.path.abspath('.'))  # 获取当前文件所在目录的上一级目录，即项目所在目录E:\Crawler
configpath = os.path.join(root_dir, "config.ini")
cf = configparser.ConfigParser()
cf.read(configpath)  # 读取配置文件

host = cf.get("db", "host")
user = cf.get("db", "user")
password = cf.get("db", "password")
database = cf.get("db", "db")


POOL = PooledDB(
    # 使用链接数据库的模块
    creator=pymysql,
    # 连接池允许的最大连接数，0和None表示不限制连接数
    maxconnections=6,
    # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
    mincached=2,
    # 链接池中最多闲置的链接，0和None不限制
    maxcached=5,
    # 链接池中最多共享的链接数量，0和None表示全部共享。
    # 因为pymysql和MySQLdb等模块的 threadsafety都为1，
    # 所有值无论设置为多少，maxcached永远为0，所以永远是所有链接都共享。
    maxshared=3,
    # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    blocking=True,
    # 一个链接最多被重复使用的次数，None表示无限制
    maxusage=None,
    # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
    setsession=[],
    # ping MySQL服务端，检查是否服务可用。
    #  如：0 = None = never, 1 = default = whenever it is requested,
    # 2 = when a cursor is created, 4 = when a query is executed, 7 = always
    ping=0,
    # 主机地址
    host=host,
    # 端口
    port=3306,
    # 数据库用户名
    user=user,
    # 数据库密码
    password=password,
    # 数据库名
    database=database,
    # 字符编码
    charset='utf8'
)


def get_resource_from_DB(resource_name, like=True):
    # 从目录服务器上查询资源信息，可以采用模糊查询方法
    # 将查询结果封装成ServerResource类，并返回，如果未查询到，返回0
    if like is False:
        sql = "select * from resource_location_param where resource_origin like '%" + resource_name + "%';"
    else:
        sql = "select * from resource_location_param where resource_origin = '" + resource_name + "';"
    conn = POOL.connection()
    #print("查找resource_name:", resource_name)
    cursor = conn.cursor()
    result_number = cursor.execute(sql)
    #print("查找到的条数：", result_number)
    if result_number == 0:
        return 0
    result = cursor.fetchone()
    #print("数据库查找结果:", result)
    server_resource = ServerResource(result[0], result[1], result[2], result[3], result[4], result[5])
    return server_resource


def get_resource_from_DB_by_website(host):
    # 将查询结果封装成ServerResource类，并返回，如果未查询到，返回0
    sql = "select * from resource_location_param where website = '" + host + "'"
    conn = POOL.connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    logger.info("查询到了%s条数据", len(result))
    return result


def get_random_ip(locations):
    # 从ip集合中随机返回一个IP
    # 这里可以使用随机方法
    if len(locations) <= 2:
        raise Exception("无法查询到资源所在的IP")
    locations = locations[1:-1]
    ips = locations.split(',')
    return choice(ips)


def delete_resource_from_DB():
    conn = POOL.connection()
    cursor = conn.cursor()
    sql = "delete from  resource_location_param where id > 0"
    try:
        cursor.execute(sql)
        conn.commit()
        print("删除数据成功！")
    except Exception as e:
        print("删除数据失败：case%s" % e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def create_resource_data(url, resource):
    # 将传过来的url 以及resources资源 封装为ServerResource资源，并放到列表中
    server_resource_list = []
    js_set = resource[0]
    css_set = resource[1]
    other_set = resource[2]
    for item in js_set:
        server_resource = ServerResource(1, url, item, str(uuid.uuid4()) + ".js", "[108.61.89.249,207.246.88.214,"
                                                                                  "101.32.164.202]", str(uuid.uuid4()))
        server_resource_list.append(server_resource)
    for item in css_set:
        server_resource = ServerResource(1, url, item, str(uuid.uuid4()) + ".css", "[108.61.89.249,207.246.88.214,"
                                                                                   "101.32.164.202]", str(uuid.uuid4()))
        server_resource_list.append(server_resource)
    for item in other_set:
        suffix = item.split('.')[-1]
        server_resource = ServerResource(1, url, item, str(uuid.uuid4()) + "." + suffix, "[108.61.89.249,207.246.88.214,"
                                                                                   "101.32.164.202]", str(uuid.uuid4()))
        server_resource_list.append(server_resource)
    return server_resource_list


def save_resource_data(server_resource_list):
    # 将server_resource资源批量存到数据库中
    save_list = []
    for item in server_resource_list:
        data = (item.website, item.resource_origin, item.resource, item.locations, item.hash)
        save_list.append(data)
    print(save_list)

    conn = POOL.connection()
    cursor = conn.cursor()
    sql = "insert into resource_location_param(website,resource_origin,resource_new,locations,hash) values (%s,%s,%s,%s,%s)"
    result_number = cursor.executemany(sql, save_list)
    conn.commit()
    cursor.close()
    conn.close()
    print("插入了{}条数据".format(result_number))


def read_resource_data():
    # 将server_resource资源从数据库中读取出来
    conn = POOL.connection()
    cursor = conn.cursor()
    sql = "select * from resource_location_param"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    print(result)
    print("查询到了{}条数据".format(len(result)))
    return result


if __name__ == '__main__':
    # server_resource1 = ServerResource(1, "url", "ii", "new_name", "[108.61.89.249,207.246.88.214]", str(uuid.uuid4()))
    # server_resource2 = ServerResource(1, "url", "item", "new_name", "[108.61.89.249,207.246.88.214]", str(uuid.uuid4()))
    # a = [server_resource1, server_resource2]
    read_resource_data()