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
from GenExchangeSession import ExchangeSessionConfig
from MySQLDB import getInstrumentList


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
        self.exchnages = ConfigChina.Exchange
        self.instrumentTypes = ConfigChina.InstrumentTypeList
        self.defaultMaxBDtoUse = ConfigChina.defaultMaxBDtoUse
        self.discriminateExchange = ConfigChina.discriminateExchange
        self.prevBusinessDays, self.nextBusinessDay = CommonFunc.genTodayBusinessDay(self.today, dir, self.configDir, self.region)

        data_Instrument = getInstrumentList(self.today, self.exchnages, self.instrumentTypes)
        if data_Instrument.empty:
            raise Exception("")
        tickdata = CommonFunc.retrieveTickDataFromFile(date, self.defaultTickFileDirectory, self.tickFileSuffix)

        tickdata_symbols = list(set(tickdata[ConfigChina.tick_data_header_symbol].tolist()))
        instrument_symbols = list(set(data_Instrument[ConfigChina.instrument_header_Symbol].tolist()))
        process_symbols = list(set(tickdata_symbols).intersection(set(instrument_symbols)))
        data_Instrument = data_Instrument[data_Instrument[ConfigChina.instrument_header_Symbol].isin(process_symbols)]
        if data_Instrument.empty:
            raise Exception("Can`t Match Instrument From tick Data")
        tickdata = tickdata[tickdata[ConfigChina.tick_data_header_symbol].isin(process_symbols)]
        self.tick_group = tickdata.groupby(by=[ConfigChina.tick_data_header_symbol])

        self.todatyInstrument = data_Instrument
        genus_exchange_session_path = os.path.join(ConfigChina.defaultConfigDirectory, "GenusStrategyExchangeSessions.xml")
        self.exchangeSessionConfig = ExchangeSessionConfig(genus_exchange_session_path, self.interval)

        instrument_path = ("{0}" + os.path.sep + "{1}{2}.{3}").format(self.outputDir, "GenusInstrument", self.today, "txt")
        self.todatyInstrument.to_csv(instrument_path, encoding='utf-8', index=False)
        pass

    def start(self):
        logger.write("startCalcData... ")
        index = 0
        self.HistInterVal = self.retrieveHistIntervalStatsFromFile()
        self.HistACVolume = self.retrieveHistACVolumeStatsFromFile()
        self.HistInstrument = self.retrieveHistInstrumentsFromFile()
        self.filenameStats = os.path.join(self.outputDir, "{0}-{1}{2}".format(self.region, "RawIntervalStats", self.today))
        self.filenameACVolume = os.path.join(self.outputDir, "{0}-{1}{2}".format(self.region, "RawACVolume", self.today))
        self.HistIntervalStatsDatas = []
        self.HistInstrumentProfiles = []
        raw_task = []
        rawPool = ThreadPoolExecutor(max_workers=self.maxThreadsTotal)
        logger.write("start CalcRawData... ")
        # tickdata 数据,根据数据加到对应时间段上;减少
        for (symbol), tickdata in self.tick_group:
            index += 1
            static_info = self.todatyInstrument[self.todatyInstrument[ConfigChina.instrument_header_Symbol] == symbol]
            info = " [ {0} - {1} ] >> {2} ".format(len(self.todatyInstrument), index, symbol)
            raw_task.append(rawPool.submit(self.startCalcRawData, symbol, tickdata, static_info, info=info))
            pass

        if os.path.isfile(self.filenameStats):
            os.remove(self.filenameStats)
            pass
        if os.path.isfile(self.filenameACVolume):
            os.remove(self.filenameACVolume)
            pass
        hist_task = []
        histPool = ThreadPoolExecutor(max_workers=self.maxThreadsTotal)
        for future in raw_task:
            RawIntervalStats, RawACVolume, static_info, info = future.result()
            if os.path.isfile(self.filenameStats):
                RawIntervalStats.to_csv(self.filenameStats, encoding="utf-8", index=False, header=0, mode='ab+')
            else:
                RawIntervalStats.to_csv(self.filenameStats, encoding="utf-8", index=False)
                pass
            if os.path.isfile(self.filenameACVolume):
                RawACVolume.to_csv(self.filenameACVolume, encoding="utf-8", index=False, header=0, mode='ab+')
            else:
                RawACVolume.to_csv(self.filenameACVolume, encoding="utf-8", index=False)
                pass
            hist_task.append(histPool.submit(self.startCalcHistData, static_info, RawIntervalStats, RawACVolume, info=info))
            pass
        logger.write("End CalcRawData... ")
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
        symbol = str(static_info[ConfigChina.instrument_header_Symbol].values[0])
        HistInterVal = self.HistInterVal[self.HistInterVal[ConfigChina.header_Symbol] == symbol]
        HistACVolume = self.HistACVolume[self.HistACVolume[ConfigChina.header_Symbol] == symbol]

        RawIntervalStatsSet = pd.concat([HistInterVal, RawIntervalStats], ignore_index=True, sort=False)
        RawIntervalStatsSet = RawIntervalStatsSet.sort_values(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime], axis=0, ascending=True)
        RawIntervalStatsSet.reset_index(drop=True, inplace=True)
        ACVolumeData = pd.concat([HistACVolume, RawACVolume], ignore_index=True, sort=False)
        ACVolumeData = ACVolumeData.sort_values(by=[ConfigChina.header_Symbol], axis=0, ascending=True)
        HistIntervalStatsDataInst, HistInstrumentProfileInst = self.calculateHistIntervalStats(RawIntervalStatsSet, ACVolumeData, static_info=static_info, info=info)

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

    def startCalcRawData(self, symbol, tickData, static_info, volatilityPeriod=10, info=""):
        start_time = time.time()
        try:
            tickData = tickData.sort_values(by=[ConfigChina.tick_data_header_time], axis=0, ascending=True)
            tickData.reset_index(drop=True, inplace=True)
            bid_size = ask_size = spreade = trade_size = volume = median_trade_size = OHCLVolatility = CCVolatility = 0

            lastIntervalBidSize = lastIntervalAskSize = lastIntervalSpreadSize = lastIntervalTradeSize = lastIntervalVolume = 0
            prevVolatilityPeriodsOHCL = []
            prevVolatilityPeriodsCC = []
            next_index = 0
            exchange = str(static_info[ConfigChina.instrument_header_Exchange].values[0])
            InstrumentType = str(static_info[ConfigChina.instrument_header_InstrumentType].values[0])
            SessionConfigs = self.exchangeSessionConfig.getSessionConfigs(exchange, InstrumentType)
            RawIntervalStats = SessionConfigs.getSessions().get_raw_time_data_frame()
            RawIntervalStats[ConfigChina.header_Symbol] = symbol
            while next_index < tickData.shape[0]:
                rawData = tickData.iloc[next_index]
                tick_index = next_index
                next_index += 1
                trdvol = rawData[ConfigChina.tick_data_header_trdvol]
                acvol = rawData[ConfigChina.tick_data_header_acvol]

                rawTimeSec = rawData[ConfigChina.tick_data_header_time]

                if exchange == "TW" and trdvol == acvol:
                    rawTimeSec, isPMAution = SessionConfigs.getAutionTimeSec(rawTimeSec)
                    if isPMAution:
                        continue
                    tickData.loc[tick_index, ConfigChina.tick_data_header_time] = rawTimeSec
                    pass
                row = RawIntervalStats[RawIntervalStats[ConfigChina.tick_data_header_time] <= rawTimeSec]
                index = max(row.index.tolist())
                row = row.iloc[index]
                start_time_str = row[ConfigChina.header_StartTime]
                end_time_str = row[ConfigChina.header_EndTime]
                isTradable = row[ConfigChina.header_isTradable]
                isAuction = row[ConfigChina.header_isAuction]
                start_time_int = TimeUtils.getTimeStamp(start_time_str)
                end_time_int = TimeUtils.getTimeStamp(end_time_str)
                filter = False
                if exchange == "TW" and isAuction == "T":
                    isPMAution = SessionConfigs.isCloseAutionTimeSec(rawTimeSec)
                    if isPMAution:
                        tickDataInstrumentInterval = tickData[
                            (tickData[ConfigChina.tick_data_header_trdvol] != tickData[ConfigChina.tick_data_header_acvol]) & (tickData[ConfigChina.tick_data_header_time] >= rawTimeSec)]
                        next_index = tickData.shape[0]
                        if not tickDataInstrumentInterval.empty:
                            tickDataInstrumentInterval = tickDataInstrumentInterval.loc[[max(tickDataInstrumentInterval.index.tolist())]]
                            filter = True
                            pass
                        else:
                            continue
                    pass
                if not filter:
                    tickDataInstrumentInterval = tickData[(tickData[ConfigChina.tick_data_header_time] >= int(start_time_int)) & (tickData[ConfigChina.tick_data_header_time] < int(end_time_int))]
                    next_index = max(tickDataInstrumentInterval.index.tolist()) + 1
                    pass
                if isTradable == "T":
                    tickDataInstrumentInterval.reset_index(drop=True, inplace=True)
                    bid_size = (tickDataInstrumentInterval[ConfigChina.tick_data_header_bidsize].mean() + lastIntervalBidSize) / 2
                    ask_size = (tickDataInstrumentInterval[ConfigChina.tick_data_header_asksize].mean() + lastIntervalAskSize) / 2
                    spreade = (tickDataInstrumentInterval[ConfigChina.header_SpreadSize].mean() + lastIntervalSpreadSize) / 2
                    trade_size = (tickDataInstrumentInterval[ConfigChina.tick_data_header_trdvol].mean() + lastIntervalTradeSize) / 2
                    volume = tickDataInstrumentInterval[ConfigChina.tick_data_header_trdvol].sum() + lastIntervalVolume
                    median_trade_size = tickDataInstrumentInterval[ConfigChina.tick_data_header_trdvol].median()
                    Open = tickDataInstrumentInterval.ix[0][ConfigChina.tick_data_header_trdprice]
                    Close = tickDataInstrumentInterval.ix[len(tickDataInstrumentInterval) - 1][ConfigChina.tick_data_header_trdprice]

                    High = tickDataInstrumentInterval[ConfigChina.tick_data_header_trdprice].max()
                    Low = tickDataInstrumentInterval[ConfigChina.tick_data_header_trdprice].min()

                    prevVolatilityPeriodsCC = prevVolatilityPeriodsCC + [np.log(Close / Open)]
                    num1 = np.power(np.log(High / Low), 2)
                    num2 = np.power(np.log(Close / Open), 2)
                    num3 = np.log(4) - 1
                    prevVolatilityPeriodsOHCL = prevVolatilityPeriodsOHCL + [((0.5 * num1) - num3 * num2)]
                    if (len(prevVolatilityPeriodsOHCL) > volatilityPeriod):
                        prevVolatilityPeriodsOHCL = prevVolatilityPeriodsOHCL[1: len(prevVolatilityPeriodsOHCL) - 1]
                        prevVolatilityPeriodsCC = prevVolatilityPeriodsCC[1: len(prevVolatilityPeriodsCC) - 1]
                    avg = np.mean(prevVolatilityPeriodsOHCL)
                    if avg and (avg > 0):
                        OHCLVolatility = 100 * np.sqrt(avg)
                    if len(prevVolatilityPeriodsCC) > 2:
                        CCVolatility = 100 * np.std(prevVolatilityPeriodsCC)
                    lastIntervalBidSize = lastIntervalAskSize = lastIntervalSpreadSize = lastIntervalTradeSize = lastIntervalVolume = 0

                else:
                    lastIntervalBidSize = tickDataInstrumentInterval[ConfigChina.tick_data_header_bidsize].mean()
                    lastIntervalAskSize = tickDataInstrumentInterval[ConfigChina.tick_data_header_asksize].mean()
                    lastIntervalSpreadSize = tickDataInstrumentInterval[ConfigChina.header_SpreadSize].mean()
                    lastIntervalTradeSize = tickDataInstrumentInterval[ConfigChina.tick_data_header_trdvol].mean()
                    lastIntervalVolume = tickDataInstrumentInterval[ConfigChina.tick_data_header_trdvol].sum()
                    prevVolatilityPeriodsOHCL = []
                    prevVolatilityPeriodsCC = []
                    pass
                RawIntervalStats.loc[index, ConfigChina.header_BidSize] = bid_size
                RawIntervalStats.loc[index, ConfigChina.header_AskSize] = ask_size
                RawIntervalStats.loc[index, ConfigChina.header_SpreadSize] = spreade
                RawIntervalStats.loc[index, ConfigChina.header_TradeSize] = trade_size
                RawIntervalStats.loc[index, ConfigChina.header_Volume] = volume
                RawIntervalStats.loc[index, ConfigChina.header_Volatility] = OHCLVolatility
                RawIntervalStats.loc[index, ConfigChina.header_CCVolatility] = CCVolatility
                bid_size = ask_size = spreade = trade_size = volume = median_trade_size = OHCLVolatility = CCVolatility = 0
                pass
            ac_volume = tickData.iloc[len(tickData) - 1][ConfigChina.tick_data_header_acvol]
            RawACVolume = pd.DataFrame({ConfigChina.header_Symbol: [symbol], ConfigChina.header_ADV: ac_volume}, columns=ConfigChina.ac_volume_header)
            instrumentDailyVolume = np.sum(RawIntervalStats[ConfigChina.header_Volume].tolist())
            if instrumentDailyVolume and instrumentDailyVolume > 0:
                RawIntervalStats[ConfigChina.header_VolumePercent] = RawIntervalStats.Volume / instrumentDailyVolume
                pass
            RawIntervalStats = RawIntervalStats[ConfigChina.RawIntervalStatsHeader]
            RawIntervalStats = RawIntervalStats.sort_values(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime], axis=0, ascending=True)
            RawIntervalStats.reset_index(drop=True, inplace=True)
            RawACVolume = RawACVolume.drop_duplicates(ConfigChina.header_Symbol)
            RawACVolume.reset_index(drop=True, inplace=True)
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
        symbol = str(static_info[ConfigChina.instrument_header_Symbol].values[0])
        exchange = str(static_info[ConfigChina.instrument_header_Exchange].values[0])
        InstrumentType = str(static_info[ConfigChina.instrument_header_InstrumentType].values[0])
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
            HistIntervalStatsData = formatHistIntervalStatsData(HistIntervalStatsData)
            HistInstrumentProfile = formatHistInstrumentProfile(HistInstrumentProfile)
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

                instrumentUniverseExchange = self.HistInstrument[self.HistInstrument[ConfigChina.instrument_header_Exchange] == exchange]
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

    def retrieveHistInstrumentsFromFile(self):
        prevBusinessDays = self.prevBusinessDays["TradeDay"].values.tolist()
        if int(self.defaultMaxBDtoUse) <= 1:
            return self.todatyInstrument
        else:
            businessDays = [self.today] + prevBusinessDays
            instrumentDatas = []
            for n in range(int(self.defaultMaxBDtoUse)):
                day = businessDays[n]
                hist_instrument_path = ("{0}" + os.path.sep + "{1}{2}.{3}").format(self.outputDir, "GenusInstrument", day, "txt")
                if not os.path.exists(hist_instrument_path):
                    data = getInstrumentList(day, self.exchnages, self.instrumentTypes)
                    pass
                elif os.path.exists(hist_instrument_path):
                    logger.write("Reading HistInstruemnt file >>  {0} ".format(day))
                    data = pd.read_csv(hist_instrument_path, encoding="utf-8", engine='c')
                    pass
                instrumentDatas.append(data)
                pass

            if len(instrumentDatas) > 0:
                hist_instrument = pd.concat(instrumentDatas, ignore_index=True)
                hist_instrument = hist_instrument.drop_duplicates(ConfigChina.header_Symbol)
                hist_instrument.reset_index(drop=True, inplace=True)
            else:
                raise Exception("Not Find InstrumentData, Please check DB Host ")
        return hist_instrument
        pass


def formatHistIntervalStatsData(HistIntervalStatsData):
    if not HistIntervalStatsData.empty:
        # HistIntervalStatsData[ConfigChina.header_TradeSize] = HistIntervalStatsData[ConfigChina.header_TradeSize].map(ConfigChina.defaultformat)
        # HistIntervalStatsData[ConfigChina.header_TradeSizeSD] = HistIntervalStatsData[ConfigChina.header_TradeSizeSD].map(ConfigChina.defaultformat)

        HistIntervalStatsData[ConfigChina.header_BidSize] = HistIntervalStatsData[ConfigChina.header_BidSize].map(
            ConfigChina.format)
        # HistIntervalStatsData[ConfigChina.header_BidSizeSD] = HistIntervalStatsData[ConfigChina.header_BidSizeSD].map(ConfigChina.format)
        HistIntervalStatsData[ConfigChina.header_AskSize] = HistIntervalStatsData[ConfigChina.header_AskSize].map(
            ConfigChina.format)
        # HistIntervalStatsData[ConfigChina.header_AskSizeSD] = HistIntervalStatsData[ConfigChina.header_AskSizeSD].map(ConfigChina.format)
        # HistIntervalStatsData[ConfigChina.header_SpreadSize] = HistIntervalStatsData[ConfigChina.header_SpreadSize].map(ConfigChina.format)
        # HistIntervalStatsData[ConfigChina.header_SpreadSizeSD] = HistIntervalStatsData[ConfigChina.header_SpreadSizeSD].map(ConfigChina.format)
        #
        # HistIntervalStatsData[ConfigChina.header_Volume] = HistIntervalStatsData[ConfigChina.header_Volume].map(ConfigChina.defaultformat)
        # HistIntervalStatsData[ConfigChina.header_VolumeSD] = HistIntervalStatsData[ConfigChina.header_VolumeSD].map(ConfigChina.defaultformat)
        # HistIntervalStatsData[ConfigChina.header_VolumePercent] = HistIntervalStatsData[ConfigChina.header_VolumePercent].map(ConfigChina.defaultformat)
        # HistIntervalStatsData[ConfigChina.header_VolumePercentSD] = HistIntervalStatsData[ConfigChina.header_VolumePercentSD].map(ConfigChina.defaultformat)
        # HistIntervalStatsData[ConfigChina.header_Volatility] = HistIntervalStatsData[ConfigChina.header_Volatility].map(ConfigChina.defaultformat)
        # HistIntervalStatsData[ConfigChina.header_VolatilitySD] = HistIntervalStatsData[ConfigChina.header_VolatilitySD].map(ConfigChina.defaultformat)
        # HistIntervalStatsData[ConfigChina.header_CCVolatility] = HistIntervalStatsData[ConfigChina.header_CCVolatility].map(ConfigChina.defaultformat)
        # HistIntervalStatsData[ConfigChina.header_CCVolatilitySD] = HistIntervalStatsData[ConfigChina.header_CCVolatilitySD].map(ConfigChina.defaultformat)

    return HistIntervalStatsData
    pass


def formatHistInstrumentProfile(HistInstrumentProfile):
    if not HistInstrumentProfile.empty:
        HistInstrumentProfile[ConfigChina.header_AvgSpread] = HistInstrumentProfile[ConfigChina.header_AvgSpread].map(
            ConfigChina.format_2)
        HistInstrumentProfile[ConfigChina.header_AvgVolatility] = HistInstrumentProfile[
            ConfigChina.header_AvgVolatility].map(ConfigChina.format_2)
        HistInstrumentProfile[ConfigChina.header_ADV] = HistInstrumentProfile[ConfigChina.header_ADV].map(
            ConfigChina.format)
        HistInstrumentProfile[ConfigChina.header_BTR] = HistInstrumentProfile[ConfigChina.header_BTR].map(
            ConfigChina.format)
    return HistInstrumentProfile
    pass
