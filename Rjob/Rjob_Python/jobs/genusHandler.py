#!/usr/bin/env python
# coding=utf-8
import Queue
import os
import time
import traceback
from threading import Thread

import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from conf import ConfigChina
from jobs.genusCalculator import GenusHistCalclator
from jobs.genusCommonFunc import retrievePreHistInstrumentsFromFile, retrieveTickDataFromFile, retrievePreHistIntervalStatsFromFile, retrievePreHistACVolumeFromFile
from jobs.genusExchangeSession import ExchangeSessionConfig
from util import logger
from util.dbutil import genTodayBusinessDay


class GenusHistHandler:

    def __init__(self, manager):
        self.rawDataQueue = Queue.Queue()
        self.histDataQueue = Queue.Queue()
        self.manager = manager
        self.today = manager.today
        self.region = manager.region
        self.volatilityPeriod = manager.volatilityPeriod

        self.initFromConfig()
        self.initBusiness()

        self.getTickDataGroup()
        self.getPreHistDataFromMaxDB()

        self.getExchangeSession()

        pass

    def initFromConfig(self):
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
        pass

    def initBusiness(self):
        self.prevBusinessDays, self.nextBusinessDay = genTodayBusinessDay(self.today)
        pass

    def getTickDataGroup(self):
        logger.write("retrieve Tick Data Group... ")
        data_Instrument = retrievePreHistInstrumentsFromFile([int(self.today)], self.outputDir, self.userExchnages,
                                                             self.useInstrumentTypes, self.defaultMaxBDtoUse)
        if data_Instrument.empty:
            raise Exception("")
        tickdata = retrieveTickDataFromFile(self.today, self.defaultTickFileDirectory, self.tickFileSuffix)

        tickdata_symbols = list(set(tickdata[ConfigChina.tick_data_header_symbol].tolist()))
        instrument_symbols = list(set(data_Instrument[ConfigChina.instrument_header_Symbol].tolist()))
        process_symbols = list(set(tickdata_symbols).intersection(set(instrument_symbols)))
        data_Instrument = data_Instrument[data_Instrument[ConfigChina.instrument_header_Symbol].isin(process_symbols)]
        self.todatyInstrument = data_Instrument
        if data_Instrument.empty:
            raise Exception("Can`t Match Instrument From tick Data")
        instrument_path = ("{0}" + os.path.sep + "{1}{2}.{3}").format(self.outputDir, "GenusInstrument", self.today, "txt")
        self.todatyInstrument.to_csv(instrument_path, encoding='utf-8', index=False)
        tickdata = tickdata[tickdata[ConfigChina.tick_data_header_symbol].isin(process_symbols)]
        self.tick_group = tickdata.groupby(by=[ConfigChina.tick_data_header_symbol])
        logger.write("retrieve Tick Data Group  Done... ")
        pass

    def getExchangeSession(self):
        logger.write("getExchangeSession... ")
        genus_exchange_session_path = os.path.join(ConfigChina.defaultConfigDirectory, "GenusStrategyExchangeSessions.xml")
        self.exchangeSessionConfig = ExchangeSessionConfig(genus_exchange_session_path, self.interval)
        pass

    def getPreHistDataFromMaxDB(self):
        logger.write("getPreHistDataFromMaxDB... ")
        self.PreAllHistInstrument = retrievePreHistInstrumentsFromFile(self.prevBusinessDays["TradeDay"].values.tolist(), self.outputDir, self.userExchnages,
                                                                       self.useInstrumentTypes, self.defaultMaxBDtoUse)
        self.preHistRawInterVals = retrievePreHistIntervalStatsFromFile(self.prevBusinessDays, self.outputDir, self.region, self.defaultMaxBDtoUse)
        self.preHistRawACVolumes = retrievePreHistACVolumeFromFile(self.prevBusinessDays, self.outputDir, self.region, self.defaultMaxBDtoUse)

        self.AllHistInstrument = pd.concat([self.todatyInstrument, self.PreAllHistInstrument], ignore_index=True)
        self.AllHistInstrument = self.AllHistInstrument.drop_duplicates(ConfigChina.header_Symbol)
        pass

    def start(self):

        self.HistIntervalStatsDatas = []
        self.HistInstrumentProfiles = []

        t = Thread(target=self.startWriteRawDtaThread, args=())
        t.start()
        t = Thread(target=self.startReceiveHistDtaThread, args=())
        t.start()
        t = Thread(target=self.startAddRemainData, args=())
        t.start()
        # self.startAddRemainData()
        self.startCalcData()
        while not (self.histDataQueue.empty() and self.rawDataQueue.empty()):
            logger.write("waiting histDataQueue and rawDataQueue ... ")
            time.sleep(1)
            pass
        if len(self.HistIntervalStatsDatas) > 0 and len(self.HistInstrumentProfiles) > 0:
            self.processHistData(self.HistIntervalStatsDatas, self.HistInstrumentProfiles)
            pass
        pass

    def startWriteRawDtaThread(self):
        filenameStats = os.path.join(self.outputDir, "{0}-{1}{2}".format(self.region, "RawIntervalStats", self.today))
        filenameACVolume = os.path.join(self.outputDir, "{0}-{1}{2}".format(self.region, "RawACVolume", self.today))
        if os.path.isfile(filenameStats):
            os.remove(filenameStats)
            pass
        if os.path.isfile(filenameACVolume):
            os.remove(filenameACVolume)
            pass
        while True:
            rawData = self.rawDataQueue.get()

            RawIntervalStats = rawData[0]
            RawACVolume = rawData[1]
            if os.path.isfile(filenameStats):
                RawIntervalStats.to_csv(filenameStats, encoding="utf-8", index=False, header=0, mode='ab+')
            else:
                RawIntervalStats.to_csv(filenameStats, encoding="utf-8", index=False)
                pass
            if os.path.isfile(filenameACVolume):
                RawACVolume.to_csv(filenameACVolume, encoding="utf-8", index=False, header=0, mode='ab+')
            else:
                RawACVolume.to_csv(filenameACVolume, encoding="utf-8", index=False)
                pass
            self.rawDataQueue.task_done()
            pass

        pass

    def startReceiveHistDtaThread(self):
        self.HistIntervalStatsDatas = []
        self.HistInstrumentProfiles = []
        while True:
            histData = self.histDataQueue.get()
            HistIntervalStatsDataInst = histData[0]
            HistInstrumentProfileInst = histData[1]
            self.HistIntervalStatsDatas.append(HistIntervalStatsDataInst)
            self.HistInstrumentProfiles.append(HistInstrumentProfileInst)

            self.histDataQueue.task_done()
            pass
        pass

    def startAddRemainData(self):
        logger.write("start Add RemainData... ")
        remainCount =0
        start_time = time.time()
        preHistSymbols = list(set(self.PreAllHistInstrument[ConfigChina.instrument_header_Symbol].tolist()))
        today_symbols = list(set(self.todatyInstrument[ConfigChina.instrument_header_Symbol].tolist()))
        preHistSymbols = list(set(preHistSymbols).difference(set(today_symbols)))
        preHistRawInterVal = self.preHistRawInterVals[self.preHistRawInterVals[ConfigChina.instrument_header_Symbol].isin(preHistSymbols)]
        preHistRawACVolume = self.preHistRawACVolumes[self.preHistRawACVolumes[ConfigChina.instrument_header_Symbol].isin(preHistSymbols)]
        if not preHistRawInterVal.empty:
            remainCount = preHistRawACVolume.shape[0]
            info = "No. of  Remain [{0}] ".format(remainCount)
            self.mergeRawDatas(RawInterVals=preHistRawInterVal, RawACVolumes=preHistRawACVolume, info=info)
            pass
        end_time = time.time()
        logger.write("Add RemainData [{0}]  done >> cost time: {1:.2f}秒".format(remainCount, end_time - start_time))
        pass

    def startCalcData(self):
        logger.write("start CalcRawData ... ")
        start_time = time.time()
        index = 0
        # tickdata 数据,根据数据加到对应时间段上;减少
        tick_count = self.todatyInstrument.shape[0] + 2
        rawPool = ThreadPoolExecutor(max_workers=min(self.maxThreadsTotal, tick_count))
        for (symbol), tickdata in self.tick_group:
            index += 1
            static_info = self.todatyInstrument[self.todatyInstrument[ConfigChina.instrument_header_Symbol] == symbol]
            static_info = static_info.iloc[0]
            info = " [ {0} - {1} ] >> {2} ".format(len(self.todatyInstrument), index, symbol)
            rawPool.submit(self.calcRawData, tickdata=tickdata, static_info=static_info, volatilityPeriod=self.volatilityPeriod, info=info).add_done_callback(self.calcHistData)
            pass
        rawPool.shutdown(wait=True)
        end_time = time.time()
        logger.write("CalcRawData  done >> cost time: {0:.2f}秒".format(end_time - start_time))
        pass

    def calcRawData(self, tickdata, static_info, volatilityPeriod=10, info=""):
        start_time = time.time()
        RawIntervalStats = pd.DataFrame()
        RawACVolume = pd.DataFrame()
        try:
            symbol = str(static_info[ConfigChina.instrument_header_Symbol])
            exchange = str(static_info[ConfigChina.instrument_header_Exchange])
            InstrumentType = str(static_info[ConfigChina.instrument_header_InstrumentType])
            SessionConfigs = self.exchangeSessionConfig.getSessionConfigs(exchange, InstrumentType)
            if not SessionConfigs:
                msg = "SessionConfigs is Null >> {0},{1}".format(exchange, InstrumentType)
                logger.write(msg)
                raise RuntimeError(msg)
                pass
            tickdata = tickdata.sort_values(by=[ConfigChina.tick_data_header_time], axis=0, ascending=True)
            tickdata.reset_index(drop=True, inplace=True)
            calclator = GenusHistCalclator(static_info=static_info, tickdata=tickdata, SessionConfigs=SessionConfigs, volatilityPeriod=volatilityPeriod)
            RawIntervalStats, RawACVolume = calclator.generatorRawData()
            self.rawDataQueue.put([RawIntervalStats, RawACVolume])
        except:
            logger.write("Failed calcRawData {0}:\n{1}".format(info, traceback.format_exc()))
            pass
        end_time = time.time()
        logger.write("CalcRawData  done {0}>> cost time: {1:.2f}秒".format(info, end_time - start_time))
        return RawIntervalStats, RawACVolume, static_info, info
        pass

    def calcHistData(self, future):
        info = ""
        try:
            result = future.result()
            RawIntervalStats = result[0]
            RawACVolume = result[1]
            static_info = result[2]
            info = result[3]
            if RawIntervalStats.empty or RawACVolume.empty:
                logger.write("Data is Empty Skipping {0} ".format(info))
                return
            symbol = str(static_info[ConfigChina.instrument_header_Symbol])

            RawInterVals = self.preHistRawInterVals[self.preHistRawInterVals[ConfigChina.header_Symbol] == symbol]
            RawACVolumes = self.preHistRawACVolumes[self.preHistRawACVolumes[ConfigChina.header_Symbol] == symbol]

            RawInterVals = pd.concat([RawInterVals, RawIntervalStats], ignore_index=True, sort=False)
            RawInterVals = RawInterVals.sort_values(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime], axis=0, ascending=True)
            RawInterVals.reset_index(drop=True, inplace=True)

            RawACVolumes = pd.concat([RawACVolumes, RawACVolume], ignore_index=True, sort=False)
            RawACVolumes = RawACVolumes.sort_values(by=[ConfigChina.header_Symbol], axis=0, ascending=True)
            self.mergeRawDatas(RawInterVals=RawInterVals, RawACVolumes=RawACVolumes, info=info)
        except:
            logger.write(" Failed CalcHistData {0} :\n{1}".format(info, traceback.format_exc()))
            pass
        pass

    def handler_percentile(self, df):
        return np.percentile(df.values, ConfigChina.defaultQuantileValue)
        pass

    def handler_agg(self, data, func, clolume_name):

        data_frame = data.agg(func)
        data_frame = data_frame.to_frame()
        data_frame.columns = [clolume_name]

        return data_frame
        pass

    def handler_InterVal_Apply(self, StatsData, HistIntervalStatsData, HistInstrumentProfile):
        symbol = StatsData[ConfigChina.header_Symbol]
        HistIntervalStatsData = HistIntervalStatsData[HistIntervalStatsData[ConfigChina.header_Symbol] == symbol]
        ac_volume = HistIntervalStatsData[ConfigChina.header_Volume].sum()
        volume = StatsData[ConfigChina.header_Volume]
        volumePercent = volume / ac_volume
        HistInstrumentProfile = HistInstrumentProfile[HistInstrumentProfile[ConfigChina.header_Symbol] == symbol]
        if not HistInstrumentProfile.empty:
            acVol = HistInstrumentProfile[ConfigChina.header_ADV].values.tolist()[0]
            volume = volumePercent * acVol
            pass
        StatsData[ConfigChina.header_Volume] = volume
        StatsData[ConfigChina.header_VolumePercent] = volumePercent
        return StatsData
        pass

    def mergeRawDatas(self, RawInterVals, RawACVolumes, info=""):
        start_time = time.time()
        HistInstrumentProfile = pd.DataFrame(columns=ConfigChina.GenusInstrumentProfile_header)
        HistIntervalStatsData = pd.DataFrame(columns=ConfigChina.GenusHistIntervalStats_header)
        try:
            if RawInterVals.empty or RawACVolumes.empty:
                return
                pass
            RawInterVals = RawInterVals.fillna(0)
            volGroup = RawACVolumes.groupby(by=[ConfigChina.header_Symbol])
            # Profile
            eligible_RawInterVals = RawInterVals[(RawInterVals[ConfigChina.header_TradeSize] > 0) & (RawInterVals[ConfigChina.header_isTradable] == "T")]
            statsGroup = eligible_RawInterVals.groupby(by=[ConfigChina.header_Symbol])

            AvgADV = self.handler_agg(volGroup[ConfigChina.header_ADV], np.mean, ConfigChina.header_ADV)
            AvgVolatility = self.handler_agg(statsGroup[ConfigChina.header_Volatility], np.mean, ConfigChina.header_AvgVolatility)
            AvgTradeSize = self.handler_agg(statsGroup[ConfigChina.header_TradeSize], np.mean, ConfigChina.header_TradeSize)
            AvgSpreadeSize = self.handler_agg(statsGroup[ConfigChina.header_SpreadSize], np.mean, ConfigChina.header_AvgSpread)
            AvgAskSize = self.handler_agg(statsGroup[ConfigChina.header_AskSize], np.mean, ConfigChina.header_AskSize)
            AvgBidSize = self.handler_agg(statsGroup[ConfigChina.header_BidSize], np.mean, ConfigChina.header_BidSize)
            HistInstrumentProfile = pd.concat([AvgADV, AvgVolatility, AvgTradeSize, AvgSpreadeSize, AvgAskSize, AvgBidSize], axis=1)
            HistInstrumentProfile = HistInstrumentProfile.reset_index()

            HistInstrumentProfile[ConfigChina.header_HasValidCurve] = "N"
            HistInstrumentProfile[ConfigChina.header_HasValidCurve] = HistInstrumentProfile[ConfigChina.header_HasValidCurve].mask(HistInstrumentProfile[ConfigChina.header_ADV] > 0, "Y")
            HistInstrumentProfile[ConfigChina.header_BTR] = (HistInstrumentProfile[ConfigChina.header_AskSize] + HistInstrumentProfile[ConfigChina.header_BidSize]) / 2 / HistInstrumentProfile[ConfigChina.header_TradeSize]
            HistInstrumentProfile[ConfigChina.header_BTR] = HistInstrumentProfile[ConfigChina.header_BTR].mask(HistInstrumentProfile[ConfigChina.header_BTR] > 1000000, 1000000)
            HistInstrumentProfile = HistInstrumentProfile[ConfigChina.GenusInstrumentProfile_header]
            HistInstrumentProfile = HistInstrumentProfile.fillna(0)

            # Intervals
            statsGroup = RawInterVals.groupby(by=ConfigChina.symbol_start_end_header)
            tradeSize_avg = self.handler_agg(statsGroup[ConfigChina.header_TradeSize], np.mean, ConfigChina.header_TradeSize)
            tradeSize_std = self.handler_agg(statsGroup[ConfigChina.header_TradeSize], np.std, ConfigChina.header_TradeSizeSD)

            bidSize_avg = self.handler_agg(statsGroup[ConfigChina.header_BidSize], np.mean, ConfigChina.header_BidSize)
            bidSize_std = self.handler_agg(statsGroup[ConfigChina.header_BidSize], np.std, ConfigChina.header_BidSizeSD)

            askSize_avg = self.handler_agg(statsGroup[ConfigChina.header_AskSize], np.mean, ConfigChina.header_AskSize)
            askSize_std = self.handler_agg(statsGroup[ConfigChina.header_AskSize], np.std, ConfigChina.header_AskSizeSD)

            spreadSize_avg = self.handler_agg(statsGroup[ConfigChina.header_SpreadSize], np.mean, ConfigChina.header_SpreadSize)
            spreadSize_std = self.handler_agg(statsGroup[ConfigChina.header_SpreadSize], np.std, ConfigChina.header_SpreadSizeSD)

            volume_avg = self.handler_agg(statsGroup[ConfigChina.header_Volume], np.mean, ConfigChina.header_Volume)
            volume_std = self.handler_agg(statsGroup[ConfigChina.header_Volume], np.std, ConfigChina.header_VolumeSD)
            volume_quantile = self.handler_agg(statsGroup[ConfigChina.header_Volume], self.handler_percentile, ConfigChina.header_VolumeQuant)
            volumePercent_avg = self.handler_agg(statsGroup[ConfigChina.header_VolumePercent], np.mean, ConfigChina.header_VolumePercent)
            volumePercent_std = self.handler_agg(statsGroup[ConfigChina.header_VolumePercent], np.std, ConfigChina.header_VolumePercentSD)

            volatility_avg = self.handler_agg(statsGroup[ConfigChina.header_Volatility], np.mean, ConfigChina.header_Volatility)
            volatility_std = self.handler_agg(statsGroup[ConfigChina.header_Volatility], np.std, ConfigChina.header_VolatilitySD)

            ccVolatility_avg = self.handler_agg(statsGroup[ConfigChina.header_CCVolatility], np.mean, ConfigChina.header_CCVolatility)
            ccVolatility_std = self.handler_agg(statsGroup[ConfigChina.header_CCVolatility], np.std, ConfigChina.header_CCVolatilitySD)

            auction = self.handler_agg(statsGroup[ConfigChina.header_isAuction], "first", ConfigChina.header_isAuction)
            tradable = self.handler_agg(statsGroup[ConfigChina.header_isTradable], "first", ConfigChina.header_isTradable)

            HistIntervalStatsData = pd.concat([tradeSize_avg, tradeSize_std, bidSize_avg, bidSize_std, askSize_avg, askSize_std,
                                               spreadSize_avg, spreadSize_std, volume_avg, volume_std, volumePercent_avg, volumePercent_std,
                                               volatility_avg, volatility_std, ccVolatility_avg, volume_quantile, ccVolatility_std,
                                               auction, tradable], axis=1)
            HistIntervalStatsData = HistIntervalStatsData.reset_index()
            HistIntervalStatsData[ConfigChina.header_Volume] = HistIntervalStatsData[ConfigChina.header_Volume].mask(HistIntervalStatsData[ConfigChina.header_isAuction] == "T", HistIntervalStatsData[ConfigChina.header_VolumeQuant])

            HistIntervalStatsData = HistIntervalStatsData.apply(self.handler_InterVal_Apply, axis=1, HistIntervalStatsData=HistIntervalStatsData, HistInstrumentProfile=HistInstrumentProfile)

            HistIntervalStatsData = HistIntervalStatsData[ConfigChina.GenusHistIntervalStats_header]
            HistIntervalStatsData = HistIntervalStatsData.fillna(0)
        except:
            logger.write("traceback.format_exc():\n{0}".format(traceback.format_exc()))
            pass
        self.histDataQueue.put([HistIntervalStatsData, HistInstrumentProfile])
        end_time = time.time()
        logger.write("mergeRawDatas  done {0}>> cost time: {1:.2f}秒".format(info, end_time - start_time))
        pass

    def processHistData(self, HistIntervalStatsDatas, HistInstrumentProfiles):
        logger.write("Generating Hist File file")
        start_time = time.time()
        HistIntervalStatsData = pd.DataFrame(columns=ConfigChina.GenusHistIntervalStats_header)
        HistInstrumentProfile = pd.DataFrame(columns=ConfigChina.GenusInstrumentProfile_header)

        if len(HistIntervalStatsDatas) > 0 and len(HistInstrumentProfiles) > 0:
            HistIntervalStatsData = pd.concat(HistIntervalStatsDatas, ignore_index=True)
            HistInstrumentProfile = pd.concat(HistInstrumentProfiles, ignore_index=True)
            HistIntervalStatsData = HistIntervalStatsData.drop_duplicates(ConfigChina.symbol_start_end_header)
            HistIntervalStatsData = HistIntervalStatsData.sort_values(by=ConfigChina.symbol_start_end_header, axis=0, ascending=True)
            HistIntervalStatsData.reset_index(drop=True, inplace=True)
            HistInstrumentProfile = HistInstrumentProfile.drop_duplicates(ConfigChina.header_Symbol)
            HistInstrumentProfile = HistInstrumentProfile.sort_values(by=ConfigChina.header_Symbol, axis=0, ascending=True)
            HistInstrumentProfile.reset_index(drop=True, inplace=True)
        else:
            logger.write("Not Find Hist Data")
            pass
        HistIntervalStatsData = HistIntervalStatsData.round({ConfigChina.header_TradeSize: 2, ConfigChina.header_TradeSizeSD: 2,
                                                             ConfigChina.header_BidSize: 2, ConfigChina.header_BidSizeSD: 2,
                                                             ConfigChina.header_AskSize: 2, ConfigChina.header_AskSizeSD: 2,
                                                             ConfigChina.header_SpreadSize: 2, ConfigChina.header_SpreadSizeSD: 2,
                                                             ConfigChina.header_Volume: 2, ConfigChina.header_VolumeSD: 2,
                                                             # ConfigChina.header_VolumePercent: 3, ConfigChina.header_VolumePercentSD: 2,
                                                             ConfigChina.header_Volatility: 2, ConfigChina.header_VolatilitySD: 2,
                                                             ConfigChina.header_CCVolatility: 2, ConfigChina.header_CCVolatilitySD: 2,
                                                             })

        HistInstrumentProfile = HistInstrumentProfile.round({ConfigChina.header_AvgSpread: 2, ConfigChina.header_AvgVolatility: 2,
                                                             ConfigChina.header_BTR: 2
                                                             })

        IntervalStatsFileName = os.path.join(self.outputDir, "{0}{1}{2}".format("GenusHistIntervalStats", self.nextBusinessDay, ".csv"))
        InstrumentProfileFileName = os.path.join(self.outputDir, "{0}{1}{2}".format("GenusInstrumentProfile", self.nextBusinessDay, ".csv"))
        HistIntervalStatsData.to_csv(IntervalStatsFileName, encoding="utf-8", index=False, header=False)
        HistInstrumentProfile.to_csv(InstrumentProfileFileName, encoding="utf-8", index=False, header=False)
        logger.write(" Writer To File : {0}".format(IntervalStatsFileName))
        logger.write("Writer To File : {0}".format(InstrumentProfileFileName))

        if self.discriminateExchange:
            for exchange in ConfigChina.Exchange:
                IntervalStatsFileName = os.path.join(self.outputDir, "{0}{1}_{2}{3}".format("GenusHistIntervalStats", self.nextBusinessDay, exchange, ".csv"))
                InstrumentProfileFileName = os.path.join(self.outputDir, "{0}{1}_{2}{3}".format("GenusInstrumentProfile", self.nextBusinessDay, exchange, ".csv"))

                instrumentUniverseExchange = self.AllHistInstrument[self.AllHistInstrument[ConfigChina.instrument_header_Exchange] == exchange]
                symbols = list(set(instrumentUniverseExchange[ConfigChina.header_Symbol].tolist()))
                HistIntervalStatsDataExchange = HistIntervalStatsData[HistIntervalStatsData[ConfigChina.header_Symbol].isin(symbols)]
                HistInstrumentProfileExchange = HistInstrumentProfile[HistInstrumentProfile[ConfigChina.header_Symbol].isin(symbols)]
                HistIntervalStatsDataExchange.to_csv(IntervalStatsFileName, encoding="utf-8", index=False, header=False)
                HistInstrumentProfileExchange.to_csv(InstrumentProfileFileName, encoding="utf-8", index=False, header=False)
                logger.write(" Writer To File : {0}".format(IntervalStatsFileName))
                logger.write("Writer To File : {0}".format(InstrumentProfileFileName))
                pass
            pass
        end_time = time.time()
        logger.write("generateEvoSchedClassificationsFile Done finish cost  {0:.2f} 秒 ".format(end_time - start_time))

        pass

    pass
