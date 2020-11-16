from ServerResource import ServerResource
from get_resource_location_pool import POOL
import uuid


def delete_resource_from_DB():
    conn = POOL.connection()
    cursor = conn.cursor()
    sql = "delete from  resource_location where id > 0"
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
    for item in js_set:
        server_resource = ServerResource(1, url, item, str(uuid.uuid4()) + ".js", "[108.61.89.249,207.246.88.214]",
                                         str(uuid.uuid4()))
        server_resource_list.append(server_resource)
    for item in css_set:
        server_resource = ServerResource(1, url, item, str(uuid.uuid4()) + ".css", "[108.61.89.249,207.246.88.214]",
                                         str(uuid.uuid4()))
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
    sql = "insert into resource_location(website,resource_origin,resource_new,locations,hash) values (%s,%s,%s,%s,%s)"
    result_number = cursor.executemany(sql, save_list)
    conn.commit()
    cursor.close()
    conn.close()
    print("插入了{}条数据".format(result_number))


def read_resource_data():
    # 将server_resource资源从数据库中读取出来
    conn = POOL.connection()
    cursor = conn.cursor()
    sql = "select * from resource_location"
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