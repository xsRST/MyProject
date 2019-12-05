# coding=utf-8
import sys
import time


def write(message):
    print("{0} : {1}".format(time.strftime("%Y%m%d-%H:%M:%S"), str(message)))
    sys.stdout.flush()
    pass
