# import os
# url_list = []
# filepath = "/media/zyan/新加卷/trace_workstation2/origin_traffic"
# with open("./error.txt", "r") as f:
#     for line in f.readlines():
#         line = line.strip('\n')  # 去掉列表中每一个元素的换行符
#         round = line[7:9]
#         web = line[16:]
#         web = web.split("/")[-1]
#         cmd = "rm " + filepath + "/" + "round" + round + "/" + web + ".pcap"
#         print(cmd)
#         os.system(cmd)
# f.close()

# import os
# url_list = []
# filepath = "/media/zyan/新加卷/trace_workstation2/origin_data9"
# files = os.listdir(filepath)
# print(files)
# for file in files:
#     cmd = "mv " + filepath + "/" + file + " " + filepath + "/" + file[:-7] + ".pcap"
#     print(cmd)
#     os.system(cmd)

a = 11 * 0.2
b= 2
print(int(a))
