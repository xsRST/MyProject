# coding=utf-8
import os
import time
import traceback
from multiprocessing import Queue

import jobs.ConfigChina as ConfigChina
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from jobs import logger

import CommonFunc
import TimeUtils
from GenusExchangeSession import ExchangeSessionConfig
from MySQLDB import getInstrumentList
from jobs.GenusHandler import Handler, HandlerTW


class GenusHistManager:

    def __init__(self, date, region='China'):
        self.queue = Queue()
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
        self.prevBusinessDays, self.nextBusinessDay = CommonFunc.genTodayBusinessDay(self.today,  self.configDir, self.region)

        data_Instrument = getInstrumentList(self.today, self.userExchnages, self.useInstrumentTypes)
        if data_Instrument.empty:
            raise Exception("")
        tickdata = CommonFunc.retrieveTickDataFromFile(date, self.defaultTickFileDirectory, self.tickFileSuffix)


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
        genus_exchange_session_path = os.path.join(ConfigChina.defaultConfigDirectory, "GenusStrategyExchangeSessions.xml")
        self.exchangeSessionConfig = ExchangeSessionConfig(genus_exchange_session_path, self.interval)

        self.AllHistInstrument = CommonFunc.retrieveHistInstrumentsFromFile(self.today, self.prevBusinessDays, self.outputDir, self.userExchnages,
                                                                            self.useInstrumentTypes, self.defaultMaxBDtoUse)
        self.AllHistRawInterVal = CommonFunc.retrieveHistIntervalStatsFromFile(self.prevBusinessDays, self.outputDir, self.region, self.defaultMaxBDtoUse)
        self.AllHistRawACVolume = CommonFunc.retrieveHistACVolumeFromFile(self.prevBusinessDays, self.outputDir, self.region, self.defaultMaxBDtoUse)
        pass

    def start(self):
        logger.write("startCalcData... ")
        index = 0
        self.HistIntervalStatsDatas = []
        self.HistInstrumentProfiles = []
        raw_task = []
        rawPool = ThreadPoolExecutor(max_workers=self.maxThreadsTotal)
        logger.write("start CalcRawData... ")
        # tickdata 数据,根据数据加到对应时间段上;减少
        for (symbol), tickdata in self.tick_group:
            index += 1
            static_info = self.todatyInstrument[self.todatyInstrument[ConfigChina.instrument_header_Symbol] == symbol]
            static_info.reset_index(drop=True, inplace=True)
            static_info = static_info.iloc[0]
            info = " [ {0} - {1} ] >> {2} ".format(len(self.todatyInstrument), index, symbol)
            raw_task.append(rawPool.submit(self.startCalcRawData,  tickdata, static_info, info=info))
            pass


        hist_task = []
        histPool = ThreadPoolExecutor(max_workers=self.maxThreadsTotal)
        filenameStats = os.path.join(self.outputDir, "{0}-{1}{2}".format(self.region, "RawIntervalStats", self.today))
        filenameACVolume = os.path.join(self.outputDir, "{0}-{1}{2}".format(self.region, "RawACVolume", self.today))
        if os.path.isfile(filenameStats):
            os.remove(filenameStats)
            pass
        if os.path.isfile(filenameACVolume):
            os.remove(filenameACVolume)
            pass
        for future in raw_task:
            RawIntervalStats, RawACVolume, static_info, info = future.result()
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
            symbol = str(static_info[ConfigChina.instrument_header_Symbol])

            HistInterVal = self.AllHistRawInterVal[self.AllHistRawInterVal[ConfigChina.header_Symbol] == symbol]
            HistACVolume = self.AllHistRawACVolume[self.AllHistRawACVolume[ConfigChina.header_Symbol] == symbol]

            RawIntervalStatsSet = pd.concat([HistInterVal, RawIntervalStats], ignore_index=True, sort=False)
            RawIntervalStatsSet = RawIntervalStatsSet.sort_values(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime], axis=0, ascending=True)
            RawIntervalStatsSet.reset_index(drop=True, inplace=True)
            ACVolumeData = pd.concat([HistACVolume, RawACVolume], ignore_index=True, sort=False)
            ACVolumeData = ACVolumeData.sort_values(by=[ConfigChina.header_Symbol], axis=0, ascending=True)
            hist_task.append(histPool.submit(self.startCalcHistData, static_info, RawIntervalStatsSet, ACVolumeData, info=info))
            pass
        logger.write("End CalcRawData... ")
        logger.write("start Add RemainData... ")
        hist_symbols = list(set(self.AllHistInstrument[ConfigChina.instrument_header_Symbol].tolist()))
        self.AllHistRawInterVal = self.AllHistRawInterVal[self.AllHistRawInterVal[ConfigChina.instrument_header_Symbol].isin(hist_symbols)]
        self.AllHistRawACVolume = self.AllHistRawACVolume[self.AllHistRawACVolume[ConfigChina.instrument_header_Symbol].isin(hist_symbols)]
        process_symbols = list(set(self.todatyInstrument[ConfigChina.instrument_header_Symbol].tolist()))
        remainHistRawInterVals = self.AllHistRawInterVal[~self.AllHistRawInterVal[ConfigChina.instrument_header_Symbol].isin(process_symbols)]
        remainHistRawACVolume = self.AllHistRawACVolume[~self.AllHistRawACVolume[ConfigChina.instrument_header_Symbol].isin(process_symbols)]
        remainCount = remainHistRawACVolume.shape[0]
        index = 0
        for (symbol), RawACVolumes in remainHistRawACVolume.groupby(by=[ConfigChina.instrument_header_Symbol]):
            index += 1
            RawInterVals = remainHistRawInterVals[remainHistRawInterVals[ConfigChina.header_Symbol] == symbol]
            HistInstruments = self.AllHistInstrument[self.AllHistInstrument[ConfigChina.header_Symbol] == symbol]
            info = " [ {0} - {1} ] >> Remain {2} ".format(remainCount, index, symbol)
            hist_task.append(histPool.submit(self.startCalcHistData, HistInstruments, RawInterVals, RawACVolumes, info=info))
            pass

        logger.write("start CalcHistData... ")
        for future in hist_task:
            HistIntervalStatsDataInst, HistInstrumentProfileInst = future.result()
            self.HistIntervalStatsDatas.append(HistIntervalStatsDataInst)
            self.HistInstrumentProfiles.append(HistInstrumentProfileInst)
            pass
        logger.write("End CalcHistData... ")
        if len(self.HistIntervalStatsDatas) > 0 and len(self.HistInstrumentProfiles) > 0:
            self.processHistData(self.HistIntervalStatsDatas, self.HistInstrumentProfiles)
            pass
        pass

    def startCalcHistData(self, static_info, RawIntervalStats, RawACVolume, info):
        start_time = time.time()
        HistIntervalStatsDataInst, HistInstrumentProfileInst = self.calculateHistIntervalStats(RawIntervalStats, RawACVolume, static_info=static_info, info=info)
        end_time = time.time()
        logger.write("CalcHistData  done {0}>> cost time: {1:.2f}秒".format(info, end_time - start_time))
        return HistIntervalStatsDataInst, HistInstrumentProfileInst
        pass

    pass

    def retrieveHistIntervalStatsFromFile(self):
        Raws = []
        RawIntervalStatsSet = pd.DataFrame(columns=ConfigChina.RawIntervalStatsHeader)
        prevBusinessDays = self.prevBusinessDays["TradeDay"].values.tolist()
        for n in range(int(self.defaultMaxBDtoUse)):
            day = prevBusinessDays[n]
            filename = os.path.join(self.outputDir, "{0}-{1}{2}".format(self.region, "RawIntervalStats", day))
            if os.path.exists(filename):
                logger.write(
                    "Reading RawIntervalStats file for {} :{} ; ready to open file:{}".format(self.region, day, filename))
                RawIntervalStats = pd.read_csv(filename, encoding="utf-8", engine='c')

            else:
                logger.write("not found. Skipping this RawIntervalStats file >> {0}".format(filename))
                continue
            Raws.append(RawIntervalStats)
            pass
        if len(Raws) > 0:
            RawIntervalStatsSet = pd.concat(Raws, ignore_index=True)
            RawIntervalStatsSet = RawIntervalStatsSet.sort_values(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime], axis=0, ascending=True)
            RawIntervalStatsSet.reset_index(drop=True, inplace=True)
        return RawIntervalStatsSet
        pass

    def retrieveHistACVolumeStatsFromFile(self):
        Raws = []
        RawACVolumeRet = pd.DataFrame(columns=ConfigChina.ac_volume_header)
        prevBusinessDays = self.prevBusinessDays["TradeDay"].values.tolist()
        for n in range(int(self.defaultMaxBDtoUse)):
            day = prevBusinessDays[n]
            filename = os.path.join(self.outputDir, "{0}-{1}{2}".format(self.region, "RawACVolume", day))
            if os.path.exists(filename):
                logger.write("Reading RawACVolume file for {} :{} ; ready to open file:{}".format(self.region, day, filename))
                RawACVolume = pd.read_csv(filename, encoding="utf-8", engine='c')

            else:
                logger.write("not found. Skipping this RawACVolume file >> {0}".format(filename))
                continue
            Raws.append(RawACVolume)
            pass
        if len(Raws) > 0:
            RawACVolumeRet = pd.concat(Raws, ignore_index=True)
            RawACVolumeRet = RawACVolumeRet.sort_values(by=[ConfigChina.header_Symbol], axis=0, ascending=True)
            RawACVolumeRet.reset_index(drop=True, inplace=True)
            pass
        return RawACVolumeRet
        pass

    def startCalcRawData(self,  tickdata, static_info, volatilityPeriod=10, info=""):
        start_time = time.time()
        try:
            symbol = str(static_info[ConfigChina.instrument_header_Symbol])
            exchange = str(static_info[ConfigChina.instrument_header_Exchange])
            InstrumentType = str(static_info[ConfigChina.instrument_header_InstrumentType])
            SessionConfigs = self.exchangeSessionConfig.getSessionConfigs(exchange, InstrumentType)
            tickdata = tickdata.sort_values(by=[ConfigChina.tick_data_header_time], axis=0, ascending=True)
            tickdata.reset_index(drop=True, inplace=True)
            if "TW"==exchange:
                handler = HandlerTW(static_info=static_info, tickdata=tickdata, SessionConfigs=SessionConfigs, volatilityPeriod=volatilityPeriod)
            else:
                handler=Handler(static_info=static_info,tickdata=tickdata,SessionConfigs=SessionConfigs,volatilityPeriod=volatilityPeriod)

            RawIntervalStats, RawACVolume=handler.generatorRawData()
        except:
            logger.write("traceback.format_exc():\n{0}".format(traceback.format_exc()))
            pass
        end_time = time.time()
        logger.write("CalcRawData  done {0}>> cost time: {1:.2f}秒".format(info, end_time - start_time))
        return RawIntervalStats, RawACVolume, static_info, info
        pass

    def handleHistInterval(self, symbol, startTime, endTime, intervalStat):

        isAuction = intervalStat[ConfigChina.header_isAuction].values.tolist()[0]
        isTradable = intervalStat[ConfigChina.header_isTradable].values.tolist()[0]
        add_data = {
            ConfigChina.header_Symbol: symbol,
            ConfigChina.header_StartTime: startTime,
            ConfigChina.header_EndTime: endTime,
            ConfigChina.header_TradeSize: intervalStat[ConfigChina.header_TradeSize].mean(),
            ConfigChina.header_TradeSizeSD: intervalStat[ConfigChina.header_TradeSize].std(),
            ConfigChina.header_BidSize: intervalStat[ConfigChina.header_BidSize].mean(),
            ConfigChina.header_BidSizeSD: intervalStat[ConfigChina.header_BidSize].std(),
            ConfigChina.header_AskSize: intervalStat[ConfigChina.header_AskSize].mean(),
            ConfigChina.header_AskSizeSD: intervalStat[ConfigChina.header_AskSize].std(),
            ConfigChina.header_SpreadSize: intervalStat[ConfigChina.header_SpreadSize].mean(),
            ConfigChina.header_SpreadSizeSD: intervalStat[ConfigChina.header_SpreadSize].std(),
            ConfigChina.header_Volume: intervalStat[ConfigChina.header_Volume].mean(),
            ConfigChina.header_VolumeSD: intervalStat[ConfigChina.header_Volume].std(),
            ConfigChina.header_VolumePercent: intervalStat[ConfigChina.header_VolumePercent].mean(),
            ConfigChina.header_VolumePercentSD: intervalStat[ConfigChina.header_VolumePercent].std(),
            ConfigChina.header_Volatility: intervalStat[ConfigChina.header_Volatility].mean(),
            ConfigChina.header_VolatilitySD: intervalStat[ConfigChina.header_Volatility].std(),
            ConfigChina.header_CCVolatility: intervalStat[ConfigChina.header_CCVolatility].mean(),
            ConfigChina.header_CCVolatilitySD: intervalStat[ConfigChina.header_CCVolatility].std(),
            ConfigChina.tick_data_header_time: TimeUtils.getTimeStamp(startTime),
            ConfigChina.header_isAuction: isAuction,
            ConfigChina.header_isTradable: isTradable
        }
        return add_data

        pass

    def calculateHistIntervalStats(self, IntervalStatSet=pd.DataFrame(), ACVolume=pd.DataFrame(), static_info="", info=""):
        symbol = str(static_info[ConfigChina.instrument_header_Symbol])
        exchange = str(static_info[ConfigChina.instrument_header_Exchange])
        InstrumentType = str(static_info[ConfigChina.instrument_header_InstrumentType])
        SessionConfigs = self.exchangeSessionConfig.getSessionConfigs(exchange, InstrumentType)
        HistIntervalStatsData = SessionConfigs.getSessions().get_hist_time_data_frame()
        HistIntervalStatsData[ConfigChina.header_Symbol] = symbol

        # HistIntervalStatsData = pd.DataFrame(columns=ConfigChina.GenusHistIntervalStats_header)
        HistInstrumentProfile = pd.DataFrame(columns=ConfigChina.GenusInstrumentProfile_header)
        try:
            acvol = ACVolume[ConfigChina.header_ADV].mean()
            threads = []
            pool = ThreadPoolExecutor(max_workers=self.maxThreadsTotal * 2)
            IntervalStatSet = IntervalStatSet[IntervalStatSet[ConfigChina.header_TradeSize] > 0]
            statsGroup = IntervalStatSet.groupby(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime, ConfigChina.header_EndTime])
            for (symbol, startTime, endTime), intervalStat in statsGroup:
                threads.append(pool.submit(self.handleHistInterval, symbol, startTime, endTime, intervalStat))
                pass
            for future in threads:
                add_data = future.result()
                startTime = add_data[ConfigChina.header_StartTime]
                row = HistIntervalStatsData[HistIntervalStatsData[ConfigChina.header_StartTime] == startTime]
                index = max(row.index.tolist())
                HistIntervalStatsData.loc[index] = pd.Series(add_data)
                pass
            HundredPercent = HistIntervalStatsData[ConfigChina.header_VolumePercent].sum()
            HistIntervalStatsData[ConfigChina.header_VolumePercent] = HistIntervalStatsData[ConfigChina.header_VolumePercent] / HundredPercent
            HistIntervalStatsData[ConfigChina.header_Volume] = HistIntervalStatsData[ConfigChina.header_VolumePercent] * acvol

            HistIntervalStatsData = HistIntervalStatsData[ConfigChina.GenusHistIntervalStats_header]
            HistIntervalStatsData = HistIntervalStatsData.fillna(0)
            HistIntervalStatsData = HistIntervalStatsData.round({ConfigChina.header_TradeSize: 2, ConfigChina.header_TradeSizeSD: 2,
                                                                 ConfigChina.header_BidSize: 2, ConfigChina.header_BidSizeSD: 2,
                                                                 ConfigChina.header_AskSize: 2, ConfigChina.header_AskSizeSD: 2,
                                                                 ConfigChina.header_SpreadSize: 2, ConfigChina.header_SpreadSizeSD: 2,
                                                                 ConfigChina.header_Volume: 2, ConfigChina.header_VolumeSD: 2,
                                                                 ConfigChina.header_VolumePercent: 2, ConfigChina.header_VolumePercentSD: 2,
                                                                 ConfigChina.header_Volatility: 2, ConfigChina.header_VolatilitySD: 2,
                                                                 ConfigChina.header_CCVolatility: 2, ConfigChina.header_CCVolatilitySD: 2,
                                                                 })

            if not HistIntervalStatsData.empty:
                BTR = 0
                HasValidCurve = "N"
                IntervalStatSet = IntervalStatSet[IntervalStatSet[ConfigChina.header_isTradable] == "T"]
                AvgADV = ACVolume[ConfigChina.header_ADV].mean()
                AvgVolatility = IntervalStatSet[ConfigChina.header_Volatility].mean()
                AvgBookSize = np.mean([IntervalStatSet[ConfigChina.header_BidSize].mean(), IntervalStatSet[ConfigChina.header_AskSize].mean()])
                AvgTradeSize = IntervalStatSet[ConfigChina.header_TradeSize].mean()
                AvgSpreadeSize = IntervalStatSet[ConfigChina.header_SpreadSize].mean()
                if (AvgBookSize and AvgBookSize > 0 and AvgTradeSize and AvgTradeSize > 0):
                    BTR = np.min([(AvgBookSize / AvgTradeSize), 1000000])
                    pass
                if (AvgADV and AvgADV > 0):
                    HasValidCurve = "Y"
                    pass
                data = {
                    ConfigChina.header_Symbol: [symbol],
                    ConfigChina.header_AvgSpread: [AvgSpreadeSize],
                    ConfigChina.header_AvgVolatility: [AvgVolatility],
                    ConfigChina.header_ADV: [AvgADV],
                    ConfigChina.header_BTR: [BTR],
                    ConfigChina.header_HasValidCurve: [HasValidCurve]
                }
                HistInstrumentProfile = pd.DataFrame(data, columns=ConfigChina.GenusInstrumentProfile_header)
                HistInstrumentProfile = HistInstrumentProfile.fillna(0)
        except:
            logger.write("traceback.format_exc():\n{0}".format(traceback.format_exc()))
            pass
        return HistIntervalStatsData, HistInstrumentProfile
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


