# coding=utf-8
import time

dateFormate = "%Y-%m-%d %H:%M:%S"


def getTimeStamp(time):
    if not time: return 0
    return int(int(time.split(":")[0]) * 3600 + int(time.split(":")[1]) * 60 + int(time.split(":")[2]))
    pass


def getCurrentTime():
    return time.strftime(dateFormate, time.localtime())
    pass
