# coding=utf-8
import time
import traceback

import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from jobs import ConfigChina, TimeUtils, logger
from jobs.GenusProcesser import Processer, ProcesserTW


class Calculator:
    def __init__(self, handler, tickdata=pd.DataFrame(), HistRawInterVals=pd.DataFrame(), HistRawACVolumes=pd.DataFrame(), static_info=pd.DataFrame(), info="Null"):
        self.info = info
        self.handler = handler
        static_info.reset_index(drop=True, inplace=True)
        self.static_info = static_info.iloc[0]
        self.symbol = str(self.static_info[ConfigChina.instrument_header_Symbol])
        self.exchange = str(self.static_info[ConfigChina.instrument_header_Exchange]).strip()
        self.InstrumentType = str(self.static_info[ConfigChina.instrument_header_InstrumentType])
        self.SessionConfigs = self.handler.exchangeSessionConfig.getSessionConfigs(self.exchange, self.InstrumentType)
        self.HistIntervalStatsData = self.SessionConfigs.getSessions().get_hist_time_data_frame()
        self.HistIntervalStatsData[ConfigChina.header_Symbol] = self.symbol

        self.HistRawInterVals = HistRawInterVals
        self.HistRawACVolumes = HistRawACVolumes
        self.HistRawInterVals.reset_index(drop=True, inplace=True)
        self.HistRawACVolumes.reset_index(drop=True, inplace=True)
        if not tickdata.empty:
            self.tickdata = tickdata
            self.tickdata = self.tickdata.sort_values(by=[ConfigChina.tick_data_header_time], axis=0, ascending=True)
            self.tickdata.reset_index(drop=True, inplace=True)
            if self.exchange == "TW":
                self.processer = ProcesserTW(self.static_info, self.tickdata, self.SessionConfigs, self.handler.volatilityPeriod)
                pass
            else:
                self.processer = Processer(self.static_info, self.tickdata, self.SessionConfigs, self.handler.volatilityPeriod)
                pass
            pass
        pass

    def startCalcDataSymbol(self):
        start_time = time.time()
        try:
            histData = None
            rawData = self.processer.generatorRawData()
            self.handler.rawDataqueue.put(rawData)
            end_time_raw = time.time()
            logger.write("CalcRawData  done {0}>> cost time: {1:.2f}秒".format(self.info, end_time_raw - start_time))
            RawIntervalStats = rawData[0]
            RawAcvolume = rawData[1]

            RawIntervalStatsSet = pd.concat([self.HistRawInterVals, RawIntervalStats], ignore_index=True, sort=False)
            RawIntervalStatsSet = RawIntervalStatsSet.sort_values(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime], axis=0, ascending=True)
            RawIntervalStatsSet.reset_index(drop=True, inplace=True)
            ACVolumeDataSet = pd.concat([self.HistRawACVolumes, RawAcvolume], ignore_index=True, sort=False)
            ACVolumeDataSet = ACVolumeDataSet.sort_values(by=[ConfigChina.header_Symbol], axis=0, ascending=True)
            histData = self.generatorHistDataSymbol(RawIntervalStatsSet, ACVolumeDataSet)
        except:
            logger.write("traceback.format_exc():[{0}]\n{1}".format(self.info, traceback.format_exc()))
            pass
        end_time = time.time()
        logger.write("CalcData  done {0}>> cost time: {1:.2f}秒".format(self.info, end_time - start_time))
        return histData
        pass

    def processHistIntervalapply(self, startTime, endTime, intervalStat):
        isAuction = intervalStat[ConfigChina.header_isAuction].values.tolist()[0]
        isTradable = intervalStat[ConfigChina.header_isTradable].values.tolist()[0]
        add_data = {
            ConfigChina.header_Symbol: self.symbol,
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

    def generatorHistDataSymbol(self, IntervalStatSets, ACVolumes):
        HistInstrumentProfile = pd.DataFrame(columns=ConfigChina.GenusInstrumentProfile_header)
        start_time = time.time()
        try:
            acvol = ACVolumes[ConfigChina.header_ADV].mean()
            threads = []
            pool = ThreadPoolExecutor(max_workers=self.handler.maxThreadsTotal * 2)
            IntervalStatSet = IntervalStatSets[IntervalStatSets[ConfigChina.header_TradeSize] > 0]
            statsGroup = IntervalStatSet.groupby(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime, ConfigChina.header_EndTime])
            for (symbol, startTime, endTime), intervalStat in statsGroup:
                threads.append(pool.submit(self.processHistIntervalapply, startTime, endTime, intervalStat))
                pass
            for future in threads:
                add_data = future.result()
                startTime = add_data[ConfigChina.header_StartTime]
                row = self.HistIntervalStatsData[self.HistIntervalStatsData[ConfigChina.header_StartTime] == startTime]
                index = max(row.index.tolist())
                self.HistIntervalStatsData.loc[index] = pd.Series(add_data)
                pass
            HundredPercent = self.HistIntervalStatsData[ConfigChina.header_VolumePercent].sum()
            self.HistIntervalStatsData[ConfigChina.header_VolumePercent] = self.HistIntervalStatsData[ConfigChina.header_VolumePercent] / HundredPercent
            self.HistIntervalStatsData[ConfigChina.header_Volume] = self.HistIntervalStatsData[ConfigChina.header_VolumePercent] * acvol

            self.HistIntervalStatsData = self.HistIntervalStatsData[ConfigChina.GenusHistIntervalStats_header]
            self.HistIntervalStatsData = self.HistIntervalStatsData.fillna(0)
            self.HistIntervalStatsData = self.HistIntervalStatsData.round({ConfigChina.header_TradeSize: 2, ConfigChina.header_TradeSizeSD: 2,
                                                                           ConfigChina.header_BidSize: 2, ConfigChina.header_BidSizeSD: 2,
                                                                           ConfigChina.header_AskSize: 2, ConfigChina.header_AskSizeSD: 2,
                                                                           ConfigChina.header_SpreadSize: 2, ConfigChina.header_SpreadSizeSD: 2,
                                                                           ConfigChina.header_Volume: 2, ConfigChina.header_VolumeSD: 2,
                                                                           ConfigChina.header_VolumePercent: 2, ConfigChina.header_VolumePercentSD: 2,
                                                                           ConfigChina.header_Volatility: 2, ConfigChina.header_VolatilitySD: 2,
                                                                           ConfigChina.header_CCVolatility: 2, ConfigChina.header_CCVolatilitySD: 2,
                                                                           })
            if not self.HistIntervalStatsData.empty:
                BTR = 0
                HasValidCurve = "N"
                IntervalStatSet = IntervalStatSet[IntervalStatSet[ConfigChina.header_isTradable] == "T"]
                AvgADV = ACVolumes[ConfigChina.header_ADV].mean()
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
                    ConfigChina.header_Symbol: [self.symbol],
                    ConfigChina.header_AvgSpread: [AvgSpreadeSize],
                    ConfigChina.header_AvgVolatility: [AvgVolatility],
                    ConfigChina.header_ADV: [AvgADV],
                    ConfigChina.header_BTR: [BTR],
                    ConfigChina.header_HasValidCurve: [HasValidCurve]
                }
                HistInstrumentProfile = pd.DataFrame(data, columns=ConfigChina.GenusInstrumentProfile_header)
                HistInstrumentProfile = HistInstrumentProfile.fillna(0)
        except:
            logger.write("traceback.format_exc():[{0}]\n{1}".format(self.info, traceback.format_exc()))
            pass
        end_time_hist = time.time()
        logger.write("CalcHistData  done {0}>> cost time: {1:.2f}秒".format(self.info, end_time_hist - start_time))
        return self.HistIntervalStatsData, HistInstrumentProfile
        pass
