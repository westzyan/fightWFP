import numpy as np
import sys
#for calculate the loss
from sklearn.metrics import log_loss
from sklearn.metrics.scorer import make_scorer

#import three machine learning models
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit

#for standardizing the data
from sklearn import preprocessing
from sklearn.model_selection import GridSearchCV


def GridSearch(train_X,train_Y):
    #find the optimal gamma
    param_grid = [
    {
     'C': [2**11,2**13,2**15,2**17],
     'gamma' : [2**-3,2**-1,2**1,2**3]
    }
    ]

    # my_scorer = make_scorer(score_func, greater_is_better=True)

    clf = GridSearchCV(estimator = SVC(kernel = 'rbf'), param_grid = param_grid, \
        scoring = 'accuracy', cv = 10, verbose = 2, n_jobs = -1)
    # clf = GridSearchCV(estimator = SVC(kernel = 'rbf'), param_grid = param_grid, \
    #     scoring = my_scorer, cv = 5, verbose = 0, n_jobs = -1)
    clf.fit(train_X, train_Y)
    # logger.info('Best estimator:%s'%clf.best_estimator_)
    # logger.info('Best_score_:%s'%clf.best_score_)
    return clf


dic = np.load("./results/round2.npy", allow_pickle=True).item()
X = np.array(dic['feature'])
y = np.array(dic['label'])

# normalize the data
scaler = preprocessing.MinMaxScaler((-1, 1))
X = scaler.fit_transform(X)

clf = GridSearch(X, y)

C = clf.best_params_['C']
gamma = clf.best_params_['gamma']

model = SVC(C = C, gamma = gamma, kernel = 'rbf')
# model.fit(X, y)

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=2003)

model.fit(X_train, y_train)

# 做预测以及计算准确率,计算准确率的逻辑也很简单，就是判断预测和实际值有多少是相等的。如果相等则算预测正确，否则预测失败。
correct = np.count_nonzero((model.predict(X_test) == y_test) == True)
print("正确率：%.8f" % (correct / len(X_test)))
