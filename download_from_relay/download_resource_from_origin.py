from resource_scheduling import read_resource_data
from download_util import download_file


def download_resource(resources_list):
    count = 0
    for item in resources_list:
        count += 1
        print("正在下载第", count)
        download_file(item[2], item[3], "../aleaxtop50/")
        print(item[2] + "下载完毕")


if __name__ == '__main__':
    r_list = read_resource_data()
    try:
        download_resource(r_list)
    except Exception as e:
        print(str(e))
