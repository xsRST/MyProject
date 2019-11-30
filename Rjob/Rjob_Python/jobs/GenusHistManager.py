# coding=utf-8
import os

import ConfigChina
from GenusHandler import Handler
from jobs import logger
from jobs.GenusExchangeSession import ExchangeSessionConfig


class GenusHistManager:

    def __init__(self, date, region='China'):
        self.region = region
        self.today = date
        self.tickFileSuffix = ConfigChina.tickFileSuffix
        self.defaultTickFileDirectory = ConfigChina.defaultTickFileDirectory
        self.configDir = ConfigChina.defaultConfigDirectory
        self.outputDir = ConfigChina.defaultDataDirectory
        self.defaultMaxBDtoUse = ConfigChina.defaultMaxBDtoUse
        self.interval = ConfigChina.interval
        self.maxThreadsTotal = ConfigChina.maxThreadsTotal
        self.userExchnages = ConfigChina.Exchange
        self.useInstrumentTypes = ConfigChina.InstrumentTypeList
        self.defaultMaxBDtoUse = ConfigChina.defaultMaxBDtoUse
        self.discriminateExchange = ConfigChina.discriminateExchange
        self.volatilityPeriod = 10

        genus_exchange_session_path = os.path.join(ConfigChina.defaultConfigDirectory, "GenusStrategyExchangeSessions.xml")
        self.exchangeSessionConfig = ExchangeSessionConfig(genus_exchange_session_path, self.interval)
        self.handler = Handler(manager=self)
        pass

    def start(self):
        logger.write("startCalcData... ")
        self.handler.start()
        pass
    pass