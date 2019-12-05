# coding=utf-8
import numpy as np
import pandas as pd
from conf import ConfigChina
from util.timeUtils import getTimeStamp


def generatorRawData(static_info, tickdata, SessionConfigs, volatilityPeriod):
    bid_size = ask_size = spreade = trade_size = volume = median_trade_size = OHCLVolatility = CCVolatility = 0
    symbol = str(static_info[ConfigChina.instrument_header_Symbol])
    exchange = str(static_info[ConfigChina.instrument_header_Exchange])
    InstrumentType = str(static_info[ConfigChina.instrument_header_InstrumentType])
    RawIntervalStatsData = SessionConfigs.getSessions().get_raw_time_data_frame()
    RawIntervalStatsData[ConfigChina.header_Symbol] = symbol

    prevVolatilityPeriodsOHCL = []
    prevVolatilityPeriodsCC = []
    next_index = 0
    tickdata_count = tickdata.shape[0]
    while next_index < tickdata_count:

        if exchange == "TW" or exchange == "HK":
            tickDataInstrumentInterval, intervalIndex = getTickDatasFromIntervalHeadAndtail(next_index=next_index, tickdata=tickdata, SessionConfigs=SessionConfigs, RawIntervalStatsData=RawIntervalStatsData)
            pass
        else:
            tickDataInstrumentInterval, intervalIndex = getTickDatasFromInterval(next_index=next_index, tickdata=tickdata, SessionConfigs=SessionConfigs, RawIntervalStatsData=RawIntervalStatsData)
            pass

        next_index += 1
        if tickDataInstrumentInterval.empty:
            continue
            pass
        next_index = max(tickDataInstrumentInterval.index.tolist()) + 1

        row = RawIntervalStatsData.iloc[intervalIndex]
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
            if (len(prevVolatilityPeriodsOHCL) > volatilityPeriod):
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
        RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_BidSize] = bid_size
        RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_AskSize] = ask_size
        RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_SpreadSize] = spreade
        RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_TradeSize] = trade_size
        RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_Volume] = volume
        RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_Volatility] = OHCLVolatility
        RawIntervalStatsData.loc[intervalIndex, ConfigChina.header_CCVolatility] = CCVolatility
        bid_size = ask_size = spreade = trade_size = volume = median_trade_size = OHCLVolatility = CCVolatility = 0
        pass
    ac_volume = tickdata.iloc[len(tickdata) - 1][ConfigChina.tick_data_header_acvol]
    RawACVolume = pd.DataFrame({ConfigChina.header_Symbol: [symbol], ConfigChina.header_ADV: ac_volume}, columns=ConfigChina.ac_volume_header)
    # instrumentDailyVolume = np.sum(RawIntervalStatsData[ConfigChina.header_Volume].tolist())
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


def getTickDatasFromInterval(next_index, tickdata, SessionConfigs, RawIntervalStatsData):
    rawData = tickdata.iloc[next_index]
    timeSec = rawData[ConfigChina.tick_data_header_time]
    isAutionTime, isCloseAuction = SessionConfigs.isAutionTimeSecPoint(timeSec)
    if isAutionTime:
        autionTimeSec, isPMAution = SessionConfigs.getAutionTimeSec(timeSec)
        tickdata.loc[tickdata[ConfigChina.tick_data_header_time] == timeSec, ConfigChina.tick_data_header_time] = autionTimeSec
        timeSec = autionTimeSec
        pass

    row = RawIntervalStatsData[RawIntervalStatsData[ConfigChina.tick_data_header_time] <= timeSec]
    intervalIndex = max(row.index.tolist())
    row = row.iloc[intervalIndex]
    start_time_str = row[ConfigChina.header_StartTime]
    end_time_str = row[ConfigChina.header_EndTime]

    start_time_int = getTimeStamp(start_time_str)
    end_time_int = getTimeStamp(end_time_str)
    tickDataInstrumentInterval = tickdata[(tickdata[ConfigChina.tick_data_header_time] >= int(start_time_int)) & (tickdata[ConfigChina.tick_data_header_time] < int(end_time_int))]
    return tickDataInstrumentInterval, intervalIndex
    pass


def getTickDatasFromIntervalHeadAndtail(next_index, tickdata, SessionConfigs, RawIntervalStatsData):
    tickDataInstrumentInterval = pd.DataFrame()
    intervalIndex = None
    rawData = tickdata.iloc[next_index]
    maxIndexTick = max(tickdata.index.tolist())
    timeSec = rawData[ConfigChina.tick_data_header_time]
    trdvol = rawData[ConfigChina.tick_data_header_trdvol]
    acvol = rawData[ConfigChina.tick_data_header_acvol]
    if next_index == 0:
        autionTimeSec, isPMAution = SessionConfigs.getAutionTimeSec(0)
        tickdata.loc[next_index, ConfigChina.tick_data_header_time] = autionTimeSec
        timeSec = autionTimeSec
        pass
    elif trdvol == acvol:
        timeSec = None
        pass
    else:
        isAutionPoint, isCloseAuction = SessionConfigs.isAutionTimeSecPoint(timeSec)
        if isAutionPoint:
            autionTimeSec, isPMAution = SessionConfigs.getAutionTimeSec(timeSec)
            tickdata.loc[tickdata[ConfigChina.tick_data_header_time] == timeSec, ConfigChina.tick_data_header_time] = autionTimeSec
            timeSec = autionTimeSec
            pass
        pass
    if timeSec:
        row = RawIntervalStatsData[RawIntervalStatsData[ConfigChina.tick_data_header_time] <= timeSec]
        intervalIndex = max(row.index.tolist())
        row = row.iloc[intervalIndex]
        isAuction = row[ConfigChina.header_isAuction]
        if (isAuction == "T" and SessionConfigs.isCloseAutionTimeSec(timeSec)):
            timeSec, isPMAution = SessionConfigs.getAutionTimeSec(timeSec)
            tickDataInstrumentInterval = tickdata.tail(1)
            row = RawIntervalStatsData[RawIntervalStatsData[ConfigChina.tick_data_header_time] <= timeSec]
            intervalIndex = max(row.index.tolist())
            pass
        else:
            start_time_str = row[ConfigChina.header_StartTime]
            end_time_str = row[ConfigChina.header_EndTime]
            start_time_int = getTimeStamp(start_time_str)
            end_time_int = getTimeStamp(end_time_str)
            tickDataInstrumentInterval = tickdata[(tickdata[ConfigChina.tick_data_header_time] >= int(start_time_int)) & (tickdata[ConfigChina.tick_data_header_time] < int(end_time_int))]
            pass
        pass
    return tickDataInstrumentInterval, intervalIndex
    pass
