# coding=utf-8
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from conf import ConfigChina
from util.timeUtils import getTimeStamp


class GenusHistCalclator:
    def __init__(self, static_info, tickdata, SessionConfigs, volatilityPeriod):
        self.prevVolatilityPeriodsOHCL = []
        self.prevVolatilityPeriodsCC = []
        self.symbol = str(static_info[ConfigChina.instrument_header_Symbol])
        self.exchange = str(static_info[ConfigChina.instrument_header_Exchange])
        self.tickdata = self.parseTickData(tickdata, self.exchange, SessionConfigs=SessionConfigs)
        RawIntervalStatsData = SessionConfigs.getSessions().get_raw_time_data_frame()
        RawIntervalStatsData[ConfigChina.header_Symbol] = self.symbol
        self.data_group = RawIntervalStatsData.groupby(by=ConfigChina.time_start_end_header)
        self.volatilityPeriod = volatilityPeriod
        pass

    def parseTickData(self, tickdata, exchange, SessionConfigs):
        tickdata_count = tickdata.shape[0]
        first_tick = tickdata.iloc[0]
        last_tick = tickdata.iloc[-1]
        symbol = first_tick[ConfigChina.tick_data_header_symbol]
        fist_time = first_tick[ConfigChina.tick_data_header_time]
        last_time = last_tick[ConfigChina.tick_data_header_time]
        if exchange == "TW":
            last_trdvol = last_tick[ConfigChina.tick_data_header_trdvol]
            last_acvol = last_tick[ConfigChina.tick_data_header_acvol]
            if tickdata_count == 2 and last_trdvol == last_acvol:
                tickdata.drop([tickdata_count - 1], inplace=True)
                pass
            fist_time = int(fist_time) - 10
            tickdata.loc[0, ConfigChina.tick_data_header_time] = fist_time
            pass
        isAutionTime = SessionConfigs.isAutionTime(fist_time)
        if isAutionTime:
            autionTimeSec, isPMAution = SessionConfigs.getAutionTimeSec(fist_time, symbol)
            tickdata.loc[tickdata[tickdata[ConfigChina.tick_data_header_time] == fist_time].index, ConfigChina.tick_data_header_time] = autionTimeSec
            pass
        isAutionTime = SessionConfigs.isAutionTime(last_time)
        if isAutionTime:
            autionTimeSec, isPMAution = SessionConfigs.getAutionTimeSec(last_time, symbol)
            tickdata.loc[tickdata[tickdata[ConfigChina.tick_data_header_time] == last_time].index, ConfigChina.tick_data_header_time] = autionTimeSec
            pass
        return tickdata
        pass

    def calclatorRawData(self, start_time_str, end_time_str, rawIntervalData):
        isAuction = rawIntervalData[ConfigChina.header_isAuction].values.tolist()[0]
        isTradable = rawIntervalData[ConfigChina.header_isTradable].values.tolist()[0]
        bid_size = ask_size = spreade = trade_size = volume = median_trade_size = OHCLVolatility = CCVolatility = 0

        if isTradable == "T":
            start_time_int = getTimeStamp(start_time_str)
            end_time_int = getTimeStamp(end_time_str)
            tickDataInstrumentInterval = self.tickdata[(self.tickdata[ConfigChina.tick_data_header_time] >= int(start_time_int)) & (self.tickdata[ConfigChina.tick_data_header_time] < int(end_time_int))]
            if not tickDataInstrumentInterval.empty:
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

                self.prevVolatilityPeriodsCC = self.prevVolatilityPeriodsCC + [np.log(Close / Open)]
                num1 = np.power(np.log(High / Low), 2)
                num2 = np.power(np.log(Close / Open), 2)
                num3 = np.log(4) - 1
                self.prevVolatilityPeriodsOHCL = self.prevVolatilityPeriodsOHCL + [((0.5 * num1) - num3 * num2)]
                if (len(self.prevVolatilityPeriodsOHCL) > self.volatilityPeriod):
                    self.prevVolatilityPeriodsOHCL = self.prevVolatilityPeriodsOHCL[1: len(self.prevVolatilityPeriodsOHCL) - 1]
                    self.prevVolatilityPeriodsCC = self.prevVolatilityPeriodsCC[1: len(self.prevVolatilityPeriodsCC) - 1]
                avg = np.mean(self.prevVolatilityPeriodsOHCL)
                if avg and (avg > 0):
                    OHCLVolatility = 100 * np.sqrt(avg)
                    pass
                if len(self.prevVolatilityPeriodsCC) > 2:
                    CCVolatility = 100 * np.std(self.prevVolatilityPeriodsCC)
                    pass
                pass
            pass
        add_data = pd.DataFrame({
            ConfigChina.header_Symbol: [self.symbol],
            ConfigChina.header_StartTime: [start_time_str],
            ConfigChina.header_EndTime: [end_time_str],
            ConfigChina.header_BidSize: [bid_size],
            ConfigChina.header_AskSize: [ask_size],
            ConfigChina.header_SpreadSize: [spreade],
            ConfigChina.header_TradeSize: [trade_size],
            ConfigChina.header_Volume: [volume],
            ConfigChina.header_Volatility: [OHCLVolatility],
            ConfigChina.header_CCVolatility: [CCVolatility],
            ConfigChina.header_isAuction: [str(isAuction)],
            ConfigChina.header_isTradable: [str(isTradable)],
        })
        return add_data

        pass

    def generatorRawData(self):
        raw_datas = []
        threads = []
        pool = ThreadPoolExecutor(max_workers=len(self.data_group.count()))
        RawIntervalStatsData = pd.DataFrame(columns=ConfigChina.RawIntervalStatsHeader)
        for (start_time_str, end_time_str), rawIntervalData in self.data_group:
            threads.append(pool.submit(self.calclatorRawData, start_time_str, end_time_str, rawIntervalData))
            pass
        for future in threads:
            add_data = future.result()
            raw_datas.append(add_data)
            pass
        if len(raw_datas) > 0:
            RawIntervalStatsData = pd.concat(raw_datas)
            pass
        ac_volume = self.tickdata.iloc[len(self.tickdata) - 1][ConfigChina.tick_data_header_acvol]
        RawACVolume = pd.DataFrame({ConfigChina.header_Symbol: [self.symbol], ConfigChina.header_ADV: [ac_volume]}, columns=ConfigChina.ac_volume_header)
        if ac_volume and ac_volume > 0:
            RawIntervalStatsData[ConfigChina.header_VolumePercent] = RawIntervalStatsData.Volume / ac_volume
            pass
        RawIntervalStatsData = RawIntervalStatsData[ConfigChina.RawIntervalStatsHeader]
        RawIntervalStatsData = RawIntervalStatsData.sort_values(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime], axis=0, ascending=True)
        RawIntervalStatsData.reset_index(drop=True, inplace=True)
        RawACVolume = RawACVolume.drop_duplicates(ConfigChina.header_Symbol)
        RawACVolume.reset_index(drop=True, inplace=True)
        return RawIntervalStatsData, RawACVolume
        pass

    pass

