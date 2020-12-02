from os.path import join, abspath, dirname, pardir
BASE_DIR = abspath(join(dirname(__file__), pardir))
confdir = join(BASE_DIR,'conf.ini')
outputdir = join(BASE_DIR, '/media/zyan/文档/毕业设计/code/dataset/round9/kfp/')
randomdir = join(BASE_DIR, 'kfingerprinting/randomresults/')
LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"