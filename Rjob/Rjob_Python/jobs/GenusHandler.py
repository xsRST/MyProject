# coding=utf-8


import numpy as np
import pandas as pd
from jobs import ConfigChina, TimeUtils


class Handler(object):
    def __init__(self, static_info, tickdata, SessionConfigs, volatilityPeriod):
        self.static_info = static_info
        self.tickdata = tickdata
        self.symbol = str(self.static_info[ConfigChina.instrument_header_Symbol])
        self.exchange = str(self.static_info[ConfigChina.instrument_header_Exchange])
        self.InstrumentType = str(self.static_info[ConfigChina.instrument_header_InstrumentType])
        self.SessionConfigs = SessionConfigs
        self.volatilityPeriod = volatilityPeriod
        ## createTimeIntervalData
        self.RawIntervalStatsData = self.SessionConfigs.getSessions().get_raw_time_data_frame()
        self.RawIntervalStatsData[ConfigChina.header_Symbol] = self.symbol

        pass

    def generatorRawData(self):
        bid_size = ask_size = spreade = trade_size = volume = median_trade_size = OHCLVolatility = CCVolatility = 0

        prevVolatilityPeriodsOHCL = []
        prevVolatilityPeriodsCC = []
        next_index = 0
        while next_index < self.tickdata.shape[0]:

            rawTimeSec = self.getcurrencyTimeSec(next_index)
            next_index += 1
            if not rawTimeSec:
                continue

            tickDataInstrumentInterval, row, intervalIndex = self.getTickDatasFromInterval(rawTimeSec)
            if tickDataInstrumentInterval.empty:
                continue
                pass
            next_index = max(tickDataInstrumentInterval.index.tolist()) + 1

            isTradable = row[ConfigChina.header_isTradable]
            isAuction = row[ConfigChina.header_isAuction]

            if isTradable == "T":
                tickDataInstrumentInterval.reset_index(drop=True, inplace=True)
                bid_size = (tickDataInstrumentInterval[ConfigChina.tick_data_header_bidsize].mean())
                ask_size = (tickDataInstrumentInterval[ConfigChina.tick_data_header_asksize].mean())
                spreade = (tickDataInstrumentInterval[ConfigChina.header_SpreadSize].mean())
                trade_size = (tickDataInstrumentInterval[ConfigChina.tick_data_header_trdvol].mean())
                volume = tickDataInstrumentInterval[ConfigChina.tick_data_header_trdvol].sum()
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
                if (len(prevVolatilityPeriodsOHCL) > self.volatilityPeriod):
                    prevVolatilityPeriodsOHCL = prevVolatilityPeriodsOHCL[1: len(prevVolatilityPeriodsOHCL) - 1]
                    prevVolatilityPeriodsCC = prevVolatilityPeriodsCC[1: len(prevVolatilityPeriodsCC) - 1]
                avg = np.mean(prevVolatilityPeriodsOHCL)
                if avg and (avg > 0):
                    OHCLVolatility = 100 * np.sqrt(avg)
                if len(prevVolatilityPeriodsCC) > 2:
                    CCVolatility = 100 * np.std(prevVolatilityPeriodsCC)

            else:
                prevVolatilityPeriodsOHCL = []
                prevVolatilityPeriodsCC = []
                pass
            self.RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_BidSize] = bid_size
            self.RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_AskSize] = ask_size
            self.RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_SpreadSize] = spreade
            self.RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_TradeSize] = trade_size
            self.RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_Volume] = volume
            self.RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_Volatility] = OHCLVolatility
            self.RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_CCVolatility] = CCVolatility
            bid_size = ask_size = spreade = trade_size = volume = median_trade_size = OHCLVolatility = CCVolatility = 0
            pass
        ac_volume = self.tickdata.iloc[len(self.tickdata) - 1][ConfigChina.tick_data_header_acvol]
        RawACVolume = pd.DataFrame({ConfigChina.header_Symbol: [self.symbol], ConfigChina.header_ADV: ac_volume}, columns=ConfigChina.ac_volume_header)
        instrumentDailyVolume = np.sum(self.RawIntervalStatsData[ConfigChina.header_Volume].tolist())
        if instrumentDailyVolume and instrumentDailyVolume > 0:
            self.RawIntervalStatsData[ConfigChina.header_VolumePercent] = self.RawIntervalStatsData.Volume / instrumentDailyVolume
            pass
        self.RawIntervalStatsData = self.RawIntervalStatsData[ConfigChina.RawIntervalStatsHeader]
        self.RawIntervalStatsData = self.RawIntervalStatsData.sort_values(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime], axis=0, ascending=True)
        self.RawIntervalStatsData.reset_index(drop=True, inplace=True)
        RawACVolume = RawACVolume.drop_duplicates(ConfigChina.header_Symbol)
        RawACVolume.reset_index(drop=True, inplace=True)
        return self.RawIntervalStatsData, RawACVolume
        pass

    pass

    def getcurrencyTimeSec(self, next_index):
        rawData = self.tickdata.iloc[next_index]
        rawTimeSec = rawData[ConfigChina.tick_data_header_time]
        return rawTimeSec
        pass

    def getTickDatasFromInterval(self, rawTimeSec):
        row = self.RawIntervalStatsData[self.RawIntervalStatsData[ConfigChina.tick_data_header_time] <= rawTimeSec]
        index = max(row.index.tolist())
        row = row.iloc[index]
        start_time_str = row[ConfigChina.header_StartTime]
        end_time_str = row[ConfigChina.header_EndTime]

        start_time_int = TimeUtils.getTimeStamp(start_time_str)
        end_time_int = TimeUtils.getTimeStamp(end_time_str)
        tickDataInstrumentInterval = self.tickdata[(self.tickdata[ConfigChina.tick_data_header_time] >= int(start_time_int)) & (self.tickdata[ConfigChina.tick_data_header_time] < int(end_time_int))]

        return tickDataInstrumentInterval, row, index
        pass

    pass


class HandlerTW(Handler):
    def getcurrencyTimeSec(self, next_index):
        rawData = self.tickdata.iloc[next_index]
        timeSec = rawData[ConfigChina.tick_data_header_time]
        trdvol = rawData[ConfigChina.tick_data_header_trdvol]
        acvol = rawData[ConfigChina.tick_data_header_acvol]
        if trdvol == acvol:
            if next_index == 0:
                rawTimeSec, isPMAution = self.SessionConfigs.getAutionTimeSec(0)
                pass
            else:
                rawTimeSec = None
                pass
            self.tickdata.loc[next_index, ConfigChina.tick_data_header_time] = rawTimeSec
            pass

        else:
            rawTimeSec = super(HandlerTW, self).getcurrencyTimeSec(next_index)

        if rawTimeSec and self.SessionConfigs.isPMMarketCloseTimeSec(rawTimeSec):
            rawTimeSec, isPMAution = self.SessionConfigs.getAutionTimeSec(rawTimeSec)
            self.tickdata.loc[next_index, ConfigChina.tick_data_header_time] = rawTimeSec
            pass
        return rawTimeSec
        pass

    def getTickDatasFromInterval(self, rawTimeSec):

        row = self.RawIntervalStatsData[self.RawIntervalStatsData[ConfigChina.tick_data_header_time] <= rawTimeSec]
        index = max(row.index.tolist())
        row = row.iloc[index]
        isAuction = row[ConfigChina.header_isAuction]
        if (isAuction == "T" and self.SessionConfigs.isCloseAutionTimeSec(rawTimeSec)):
            tickDataInstrumentInterval = self.tickdata.tail(1)
            pass
        else:
            return super(HandlerTW, self).getTickDatasFromInterval(rawTimeSec)
            pass
        return tickDataInstrumentInterval, row, index
        pass

    pass
