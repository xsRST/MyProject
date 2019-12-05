# coding=utf-8


from jobs.genusHandler import GenusHistHandler

from util import logger


class GenusHistManager:

    def __init__(self, date, volatilityPeriod=10, region='China'):
        # 初始化从config获取配置
        self.region = region
        self.today = date
        self.volatilityPeriod = volatilityPeriod
        pass

    def start(self):

        logger.write("startCalcData... ")
        self.hander = GenusHistHandler(self)
        self.hander.start()
        pass
    pass
