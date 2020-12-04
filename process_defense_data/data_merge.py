import os
from concurrent.futures import ProcessPoolExecutor


def tcp_merge_single(origin_filepath, dst_filepath, offset, dir):
    files = os.listdir(origin_filepath + dir)
    for file in files:
        new_name = int(file[:-4]) + offset
        cmd = "cp " + origin_filepath + dir + "/" + file + " " + dst_filepath + dir + "/" + str(new_name) + ".csv"
        print(cmd)
        os.system(cmd)


def rm_single(origin_filepath, dst_filepath, offset, dir):
    files = os.listdir(origin_filepath + dir)
    for file in files:
        if 199 >= int(file[:-4]) >=100:
            cmd = "rm " + origin_filepath + dir + "/" + file
            print(cmd)
            os.system(cmd)


def tcp_merge(origin_filepath, dst_filepath, offset):
    executor = ProcessPoolExecutor(max_workers=30)
    dirs = os.listdir(origin_filepath)
    for dir in dirs:
        executor.submit(tcp_merge_single, origin_filepath, dst_filepath, offset, dir)
    executor.shutdown()


def merge_cw_ow(cw, ow, output):
    data_list = []
    with open(cw, 'r') as f1:
        a = f1.readlines()
    with open(ow, 'r') as f2:
        b = f2.readlines()
    data_list = a + b
    print(len(data_list))
    f1.close()
    f2.close()
    with open(output, 'w') as f3:
        f3.writelines(data_list)
    f3.close()


if __name__ == '__main__':
    # origin_filepath = "/media/zyan/文档/毕业设计/code/dataset/round3/tcp/"
    # dst_filepath = "/media/zyan/文档/毕业设计/code/dataset/round4/tcp/"
    # offset = 0
    # tcp_merge(origin_filepath, dst_filepath, offset)

    cw = '/media/zyan/文档/毕业设计/code/dataset/round4/df_tcp_15000.csv'
    ow = '/media/zyan/文档/毕业设计/code/dataset/round10/df_OW_800.csv'
    output = '/media/zyan/文档/毕业设计/code/dataset/round10/df_CW15000_OW_800.csv'
    merge_cw_ow(cw, ow, output)
