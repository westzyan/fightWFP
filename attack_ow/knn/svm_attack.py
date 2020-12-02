import os
import numpy as np
# 用来导入一个样本数据
from sklearn import datasets
# 用来做数据集的分割，把数据分成训练集和测试集，这样做的目的是为了评估模型。
from sklearn.model_selection import train_test_split
# 导入了KNN的模块，是sklearn提供的现成的算法。
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier

def feature_extraction():
    filepath = "/media/zyan/文档/毕业设计/code/参考代码/knn_output/knn_data/"
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
    with open('wang_knn.csv', 'w') as f:
        for features in feature_label_list:
            print(features)
            for i in range(len(features) - 1):
                f.write(features[i])
                f.write(',')
            f.write(features[-1])
            f.write('\n')
    f.close()


def load_data():
    filepath = './wang_knn.csv'
    data = np.loadtxt(filepath, delimiter=",")
    X = data[:, :-1]
    y = data[:, -1]
    return X, y


def w_dist(x, y, **kwargs):
   return sum(((x-y)*(x-y)))

def attack():
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=2003)

    # 训练模型
    # Learn to predict each class against the other
    model = OneVsRestClassifier(svm.SVC(kernel='linear', probability=True, random_state=0))
    clt = model.fit(X_train, y_train)

    # 性能评估
    # 1.在训练集上的得分
    clt.score(X_train, y_train)
    print(clt.score(X_train, y_train))

    # 2.在测试集上的评分
    clt.score(X_test, y_test)
    print(clt.score(X_test, y_test))

    # 查看各类别的预测情况
    y_predict_scores = clt.decision_function(X_test)
    print(y_predict_scores[:100])

    # 转化为原始标签模式
    result = np.argmax(clt.decision_function(X_test), axis=1)[:100]
    # print(result)
    # 转化为老师需要的 1，2，3类标
    for i in range(result.__len__()):
        result[i] = result[i] + 1

    print(result)

    # 做预测以及计算准确率,计算准确率的逻辑也很简单，就是判断预测和实际值有多少是相等的。如果相等则算预测正确，否则预测失败。
    correct = np.count_nonzero((clt.predict(X_test) == y_test) == True)
    print("正确率：%.3f" % (correct / len(X_test)))



if __name__ == '__main__':
    attack()