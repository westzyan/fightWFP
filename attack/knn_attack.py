import os
import numpy as np
# 用来导入一个样本数据
from sklearn import datasets
# 用来做数据集的分割，把数据分成训练集和测试集，这样做的目的是为了评估模型。
from sklearn.model_selection import train_test_split
# 导入了KNN的模块，是sklearn提供的现成的算法。
from sklearn.neighbors import KNeighborsClassifier
from concurrent.futures import ProcessPoolExecutor, as_completed


def feature_transform_single_dir(dir, filepath, output_path):
    filepath = filepath + dir + "/"
    files = os.listdir(filepath)
    for file in files:
        single_file_list = []
        with open(filepath + file, 'r') as f:
            for line in f.readlines():
                line = line.strip('\n')  # 去掉列表中每一个元素的换行符
                lines = line.split(",")
                if lines[1].startswith("+"):
                    single_file_list.append(lines[0] + "\t" + "1\n")
                else:
                    single_file_list.append(lines[0] + "\t" + "-1\n")
        f.close()
        with open(output_path + dir + "-" + file[:-4], 'w') as f:
            for item in single_file_list:
                f.write(item)
        f.close()


def feature_transform():
    filepath = "/media/zyan/文档/毕业设计/code/dataset/round2/tcp_time_direction_len/"
    output_path = "/media/zyan/文档/毕业设计/code/dataset/round2/my_knn_data/"
    dirs = os.listdir(filepath)
    executor = ProcessPoolExecutor(max_workers=30)
    for dir in dirs:
        executor.submit(feature_transform_single_dir, dir, filepath, output_path)
    executor.shutdown()


def feature_extraction():
    filepath = "/media/zyan/文档/毕业设计/code/dataset/my_knn_output/my_knn_data/"
    files = os.listdir(filepath)
    feature_label_list = []
    for file in files:
        if file.__contains__('-'):
            label = file.split('-')[0]
            feature_label = []
            with open(filepath + file, 'r') as f:
                for line in f.readlines():
                    line = line.strip('\n')  # 去掉列表中每一个元素的换行符
                    feature_label.append(line)
            f.close()
            feature_label.append(label)
            feature_label_list.append(feature_label)
    with open('my_knn_5000.csv', 'w') as f:
        for features in feature_label_list:
            print(features)
            for i in range(len(features) - 1):
                f.write(features[i])
                f.write(',')
            f.write(features[-1])
            f.write('\n')
    f.close()


def load_data():
    filepath = '/media/zyan/文档/毕业设计/code/dataset/round2/my_knn_5000.csv'
    data = np.loadtxt(filepath, delimiter=",")
    X = data[:, :-1]
    y = data[:, -1]
    return X, y


def w_dist(x, y, **kwargs):
    return sum(((x - y) * (x - y)))


def attack():
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=2003)

    # 定义了一个KNN object，它带有一个参数叫做n_neighbors=3， 意思就是说我们选择的K值是3.
    clf = KNeighborsClassifier(n_neighbors=1)
    clf.fit(X_train, y_train)

    # 做预测以及计算准确率,计算准确率的逻辑也很简单，就是判断预测和实际值有多少是相等的。如果相等则算预测正确，否则预测失败。
    correct = np.count_nonzero((clf.predict(X_test) == y_test) == True)
    print("正确率：%.3f" % (correct / len(X_test)))


if __name__ == '__main__':
    # feature_extraction()
    # feature_transform()
    attack()