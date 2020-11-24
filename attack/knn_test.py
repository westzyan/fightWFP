# 用来导入一个样本数据
from sklearn import datasets
# 用来做数据集的分割，把数据分成训练集和测试集，这样做的目的是为了评估模型。
from sklearn.model_selection import train_test_split
# 导入了KNN的模块，是sklearn提供的现成的算法。
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

# 导入数据集,iris数据集为开源的数据集,数据包含了3个类别
iris=datasets.load_iris()
# X存储的是数据的特征，y存储的每一个样本的标签或者分类
X=iris.data
y=iris.target
# X拥有四个特征，并且标签y拥有0，1，2三种不同的值。
print(X,y)

X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=2003)

# 定义了一个KNN object，它带有一个参数叫做n_neighbors=3， 意思就是说我们选择的K值是3.
clf=KNeighborsClassifier(n_neighbors=3)
clf.fit(X_train,y_train)

# 做预测以及计算准确率,计算准确率的逻辑也很简单，就是判断预测和实际值有多少是相等的。如果相等则算预测正确，否则预测失败。
correct=np.count_nonzero((clf.predict(X_test)==y_test)==True)
print("正确率：%.3f"%(correct/len(X_test)))