#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 16:28:28 2018

@author: aaron
"""
from main import *
logger = logging.getLogger('cumul')



def parse_arguments():

    parser = argparse.ArgumentParser(description='Evaluate.')

    parser.add_argument('-m',
                        metavar='<model path>',
                        help='Path to the directory of the model')
    parser.add_argument('-p',
                        metavar='<feature path>',
                        help='Path to the directory of the extracted features')
    parser.add_argument('-o',
                        metavar='<feature path>',
                        help='Path to the directory of the extracted features')    

    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')
    # Parse arguments
    args = parser.parse_args()
    config_logger(args)
    return args

def score_func(ground_truths, predictions):
    global MON_SITE_NUM
    tp, wp, fp, p, n = 0, 0, 0, 0 ,0
    for truth,prediction in zip(ground_truths, predictions):
        if truth != MON_SITE_NUM:
            p += 1
        else:
            n += 1
        if prediction != MON_SITE_NUM:
            if truth == prediction:
                tp += 1
            else:
                if truth != MON_SITE_NUM:
                    wp += 1
                    # logger.info('Wrong positive:%d %d'%(truth, prediction))
                else:
                    fp += 1
                    # logger.info('False positive:%d %d'%(truth, prediction))
    print('{} {} {} {} {}'.format(tp, wp, fp, p, n))
    try:
        r_precision = tp*n / (tp*n+wp*n+r*p*fp)
        print(r_precision)
    except:
        r_precision = 0.0
    logger.info('r-precision:%.4f',r_precision)
    # return r_precision
    return tp/p




    
if __name__ == '__main__':    
    global MON_SITE_NUM
    args = parse_arguments()
    # logger.info("Arguments: %s" % (args))
    cf = read_conf(ct.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])

    
    
    model =  joblib.load(args.m)
    
    


    # logger.info('loading original data...')
    dic = np.load(args.o, allow_pickle=True).item()
    X = np.array(dic['feature'])
    y = np.array(dic['label'])    
    #normalize the data
    print(X)
    print(y)
    print(X.shape)
    print(y.shape)
    scaler = preprocessing.MinMaxScaler((-1,1))
    scaler.fit(X)

    # logger.info('loading test data...')
    dic = np.load(args.p, allow_pickle=True).item()
    X = np.array(dic['feature'])
    y = np.array(dic['label'])
    X = scaler.transform(X)
    # logger.info('data are transformed into [-1,1]')

    y_pred = model.predict(X)
    print(y_pred)
    count = 0
    for i in range(len(y)):
        if y[i] != y_pred[i]:
            print(y[i], y_pred[i])
            count += 1
    print(count)
    score_func(y, y_pred)