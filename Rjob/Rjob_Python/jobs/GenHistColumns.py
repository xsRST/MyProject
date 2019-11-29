# coding=utf-8
import os
import time
import traceback

import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

import ConfigChina
import logger
from CommonFunc import parseTimeStr, retrieveHistInstrumentsFromFile, retrieveBusinessDayFromFile, \
    retrieveNextBusinessDayFromFile


def retrieveRawIntervalStatsFromFile(targetDate, region, outDir=ConfigChina.defaultDataDirectory):
    RawIntervalStatsSet = pd.DataFrame(columns=ConfigChina.RawIntervalStatsHeader)

    businessDays = retrieveBusinessDayFromFile(targetDate, region)
    businessDays = businessDays["TradeDay"].values.tolist()
    Raws = []
    for n in range(int(ConfigChina.defaultMaxBDtoUse)):
        day = businessDays[n]
        filename = os.path.join(outDir, "{0}-{1}{2}".format(region, "RawIntervalStats", day))
        if os.path.exists(filename):
            logger.write(
                "Reading RawIntervalStats file for {} :{} ; ready to open file:{}".format(region, day, filename))
            RawIntervalStats = pd.read_csv(filename, encoding="utf-8", engine='c')

        else:
            logger.write("not found. Skipping this RawIntervalStats file >> {0}".format(filename))
            continue
        Raws.append(RawIntervalStats)

    if len(Raws) > 0:
        RawIntervalStatsSet = pd.concat(Raws, ignore_index=True)
        RawIntervalStatsSet = RawIntervalStatsSet.sort_values(
            by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime], axis=0, ascending=True)
        RawIntervalStatsSet.reset_index(drop=True, inplace=True)

    return RawIntervalStatsSet

    pass


def retrieveRawACVolumeFromFile(targetDate, region, dir=ConfigChina.defaultDataDirectory):
    RawACVolumeRet = pd.DataFrame(columns=ConfigChina.ac_volume_header)
    businessDays = retrieveBusinessDayFromFile(targetDate, region)
    businessDays = businessDays["TradeDay"].values.tolist()
    Raws = []
    for n in range(int(ConfigChina.defaultMaxBDtoUse)):
        day = businessDays[n]
        filename = os.path.join(dir, "{0}-{1}{2}".format(region, "RawACVolume", day))
        if os.path.exists(filename):
            logger.write("Reading RawACVolume file for {} :{} ; ready to open file:{}".format(region, day, filename))
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


def generateHistStats(RawIntervalStatSet=pd.DataFrame(), RawACVolume=pd.DataFrame(), symbol="", interval=5, info=""):
    HistIntervalStatsData = pd.DataFrame(columns=ConfigChina.GenusHistIntervalStats_header)
    HistInstrumentProfile = pd.DataFrame(columns=ConfigChina.GenusInstrumentProfile_header)
    StatsDatas = []
    try:
        logger.write("Start generate Hist Stats : {0} ".format(info))
        for (start_time, end_time), RawIntervalStats in RawIntervalStatSet.groupby(
                by=[ConfigChina.header_StartTime, ConfigChina.header_EndTime]):
            isContTrading = RawIntervalStats[ConfigChina.header_isContTrading].tolist()[0]
            acvol = 0
            if isContTrading == "T":
                acvol = RawACVolume[ConfigChina.header_ADV].mean()
            dailyPercentageBucket = RawIntervalStats[ConfigChina.header_VolumePercent].tolist()
            data = {ConfigChina.header_Symbol: [symbol],
                    ConfigChina.header_StartTime: [start_time],
                    ConfigChina.header_EndTime: [end_time],
                    ConfigChina.header_TradeSize: [RawIntervalStats[ConfigChina.header_TradeSize].mean()],
                    ConfigChina.header_TradeSizeSD: [RawIntervalStats[ConfigChina.header_TradeSize].std()],
                    ConfigChina.header_BidSize: [RawIntervalStats[ConfigChina.header_BidSize].mean()],
                    ConfigChina.header_BidSizeSD: [RawIntervalStats[ConfigChina.header_BidSize].std()],
                    ConfigChina.header_AskSize: [RawIntervalStats[ConfigChina.header_AskSize].mean()],
                    ConfigChina.header_AskSizeSD: [RawIntervalStats[ConfigChina.header_AskSize].std()],
                    ConfigChina.header_SpreadSize: [RawIntervalStats[ConfigChina.header_SpreadSize].mean()],
                    ConfigChina.header_SpreadSizeSD: [RawIntervalStats[ConfigChina.header_SpreadSize].std()],

                    ConfigChina.header_Volume: [np.mean(dailyPercentageBucket) * acvol],
                    ConfigChina.header_VolumeSD: [np.std(dailyPercentageBucket) * acvol],

                    ConfigChina.header_VolumePercent: [np.mean(dailyPercentageBucket)],
                    ConfigChina.header_VolumePercentSD: [np.std(dailyPercentageBucket)],

                    ConfigChina.header_Volatility: [RawIntervalStats[ConfigChina.header_Volatility].mean()],
                    ConfigChina.header_VolatilitySD: [RawIntervalStats[ConfigChina.header_Volatility].std()],
                    ConfigChina.header_CCVolatility: [RawIntervalStats[ConfigChina.header_CCVolatility].mean()],
                    ConfigChina.header_CCVolatilitySD: [RawIntervalStats[ConfigChina.header_CCVolatility].std()],
                    }
            StatsDataInst = pd.DataFrame(data, columns=ConfigChina.GenusHistIntervalStats_header)
            StatsDataInst = StatsDataInst.fillna(0)
            StatsDatas.append(StatsDataInst)
            pass

        if len(StatsDatas) > 0:
            HistIntervalStatsData = pd.concat(StatsDatas, ignore_index=True)
            logger.write("Start generate Hist Profile : {0} ".format(info))
            BTR = 0
            HasValidCurve = "N"
            RawIntervalStatSet = RawIntervalStatSet[RawIntervalStatSet[ConfigChina.header_isContTrading] == "T"]
            AvgADV = RawACVolume[RawACVolume[ConfigChina.header_Symbol] == symbol][ConfigChina.header_ADV].mean()
            AvgVolatility = RawIntervalStatSet[ConfigChina.header_Volatility].mean()
            AvgBookSize = np.mean([RawIntervalStatSet[ConfigChina.header_BidSize].mean(), RawIntervalStatSet[
                ConfigChina.header_AskSize].mean()])
            AvgTradeSize = RawIntervalStatSet[ConfigChina.header_TradeSize].mean()
            AvgSpreadeSize = RawIntervalStatSet[ConfigChina.header_SpreadSize].mean()
            if (AvgBookSize and AvgBookSize > 0 and AvgTradeSize and AvgTradeSize > 0):
                BTR = np.min([(AvgBookSize / AvgTradeSize), 1000000])
            if (AvgADV and AvgADV > 0):
                HasValidCurve = "Y"
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
    return HistIntervalStatsData, HistInstrumentProfile, True
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


def processHistData(HistIntervalStatsDatas, HistInstrumentProfiles, targetDate, region, outDir,
                    NDays=ConfigChina.defaultMaxBDtoUse):
    logger.write("Generating Hist File file")
    start_time = time.time()
    HistIntervalStatsData = pd.DataFrame(columns=ConfigChina.GenusHistIntervalStats_header)
    HistInstrumentProfile = pd.DataFrame(columns=ConfigChina.GenusInstrumentProfile_header)

    NextBusinessDay = retrieveNextBusinessDayFromFile(targetDate, region)

    if len(HistIntervalStatsDatas) > 0 and len(HistInstrumentProfiles) > 0:
        HistIntervalStatsData = pd.concat(HistIntervalStatsDatas, ignore_index=True)
        HistInstrumentProfile = pd.concat(HistInstrumentProfiles, ignore_index=True)
        HistIntervalStatsData = HistIntervalStatsData.drop_duplicates(ConfigChina.symbol_start_end_header)
        HistIntervalStatsData = HistIntervalStatsData.sort_values(by=ConfigChina.symbol_start_end_header, axis=0,
                                                                  ascending=True)
        HistIntervalStatsData.reset_index(drop=True, inplace=True)
        HistInstrumentProfile = HistInstrumentProfile.drop_duplicates(ConfigChina.header_Symbol)
        HistInstrumentProfile = HistInstrumentProfile.sort_values(by=ConfigChina.header_Symbol, axis=0, ascending=True)
        HistInstrumentProfile.reset_index(drop=True, inplace=True)
        HistIntervalStatsData = formatHistIntervalStatsData(HistIntervalStatsData)
        HistInstrumentProfile = formatHistInstrumentProfile(HistInstrumentProfile)
    else:
        logger.write("Not Find Hist Data")

    IntervalStatsFileName = os.path.join(outDir, "{0}{1}{2}".format("GenusHistIntervalStats", NextBusinessDay, ".csv"))
    InstrumentProfileFileName = os.path.join(outDir,
                                             "{0}{1}{2}".format("GenusInstrumentProfile", NextBusinessDay, ".csv"))
    HistIntervalStatsData.to_csv(IntervalStatsFileName, encoding="utf-8", index=False, header=False)
    HistInstrumentProfile.to_csv(InstrumentProfileFileName, encoding="utf-8", index=False, header=False)
    logger.write(" Writer To File : {0}".format(IntervalStatsFileName))
    logger.write("Writer To File : {0}".format(InstrumentProfileFileName))

    if ConfigChina.discriminateExchange:
        instrumentUniverse = retrieveHistInstrumentsFromFile(targetDate, region, NDays)
        for exchange in ConfigChina.Exchange:
            IntervalStatsFileName = os.path.join(outDir,
                                                 "{0}{1}_{2}{3}".format("GenusHistIntervalStats", NextBusinessDay,
                                                                        exchange, ".csv"))
            InstrumentProfileFileName = os.path.join(outDir,
                                                     "{0}{1}_{2}{3}".format("GenusInstrumentProfile", NextBusinessDay,
                                                                            exchange, ".csv"))

            instrumentUniverseExchange = instrumentUniverse[instrumentUniverse[
                                                                ConfigChina.instrument_header_Exchange] == exchange]
            symbols_exchange = list(set(instrumentUniverseExchange[ConfigChina.header_Symbol].tolist()))
            HistIntervalStatsDataExchange = HistIntervalStatsData[
                HistIntervalStatsData[ConfigChina.header_Symbol].isin(symbols_exchange)]
            HistInstrumentProfileExchange = HistInstrumentProfile[
                HistInstrumentProfile[ConfigChina.header_Symbol].isin(symbols_exchange)]
            HistIntervalStatsDataExchange.to_csv(IntervalStatsFileName, encoding="utf-8", index=False, header=False)
            HistInstrumentProfileExchange.to_csv(InstrumentProfileFileName, encoding="utf-8", index=False, header=False)
            logger.write(" Writer To File : {0}".format(IntervalStatsFileName))
            logger.write("Writer To File : {0}".format(InstrumentProfileFileName))
    end_time = time.time()
    logger.write("generateEvoSchedClassificationsFile Done finish cost  {0:.2f} 秒 ".format(end_time - start_time))

    pass


def generateFile(targetDate, interval=ConfigChina.interval, outDir=ConfigChina.defaultDataDirectory, region='China'):
    logger.write("Generating  file for {0}:{1}".format(region, targetDate))
    start_time = time.time()
    instrumentUniverse = retrieveHistInstrumentsFromFile(targetDate, region)
    process_symbols = list(set(ConfigChina.tickdata[ConfigChina.tick_data_header_symbol].tolist()))
    instrumentUniverse = instrumentUniverse[instrumentUniverse[ConfigChina.header_Symbol].isin(process_symbols)]
    filenameStats = os.path.join(outDir, "{0}-{1}{2}".format(region, "RawIntervalStats", targetDate))
    filenameACVolume = os.path.join(outDir, "{0}-{1}{2}".format(region, "RawACVolume", targetDate))
    exist_symbols = []
    if os.path.exists(filenameStats):
        RawIntervalStatsToday = pd.read_csv(filenameStats, encoding="utf-8", engine='c')
        exist_symbols = exist_symbols + RawIntervalStatsToday[ConfigChina.header_Symbol].tolist()
    if os.path.exists(filenameACVolume):
        RawACVolumeToday = pd.read_csv(filenameACVolume, encoding="utf-8", engine='c')
        exist_symbols = exist_symbols + RawACVolumeToday[ConfigChina.header_Symbol].tolist()
    exist_symbols = list(set(exist_symbols))
    AllIntervalStatsSet = retrieveRawIntervalStatsFromFile(targetDate, region, outDir=outDir)
    AllACVolumeSet = retrieveRawACVolumeFromFile(targetDate, region, dir=outDir)

    pool = ThreadPoolExecutor(max_workers=ConfigChina.maxThreadsTotal)
    tick_group = ConfigChina.tickdata.groupby(by=[ConfigChina.tick_data_header_symbol])
    ConfigChina.tickdata = None
    raw_data_threads = []
    hist_data_threads = []
    exist_time_interval = {}
    index = 0
    for (symbol), tickdata in tick_group:
        instrument_single = instrumentUniverse[instrumentUniverse[ConfigChina.header_Symbol] == symbol]
        if instrument_single.empty:
            logger.write("Not Find Instrument Data >> " + str(symbol))
            continue
        index += 1
        if symbol in exist_symbols:
            logger.write("[generateRawFile] Already populated. Skipping... {}".format(symbol))
        else:
            tickdata.reset_index(drop=True, inplace=True)
            exchange = str(instrument_single[ConfigChina.instrument_header_Exchange].values[0])
            InstrumentType = str(instrument_single[ConfigChina.instrument_header_InstrumentType].values[0])
            time_key = "{0}-{1}-{2}".format(exchange, InstrumentType, interval)
            if exist_time_interval.has_key(time_key):
                time_data_frame = exist_time_interval.get(time_key)
            else:
                time_data_frame = ConfigChina.exchangeSessionConfig.getTimeDataFrame(exchange, InstrumentType, interval)
                exist_time_interval[time_key] = time_data_frame
                pass
            info = " [ {0} - {1} ] >> {2} ".format(len(instrumentUniverse), index, symbol)
            raw_data_threads.append(
                pool.submit(calculateInstrumentRawIntervalStats, symbol, tickdata, time_data_frame, info=info))
            pass
        pass

    for calculate_thread in raw_data_threads:
        IntervalStatsData, ACVolumeData, info = calculate_thread.result()
        if not IntervalStatsData.empty and not ACVolumeData.empty:

            if os.path.isfile(filenameStats):
                IntervalStatsData.to_csv(filenameStats, encoding="utf-8", index=False, header=0, mode='ab+')
            else:
                IntervalStatsData.to_csv(filenameStats, encoding="utf-8", index=False)
            if os.path.isfile(filenameACVolume):
                ACVolumeData.to_csv(filenameACVolume, encoding="utf-8", index=False, header=0, mode='ab+')
            else:
                ACVolumeData.to_csv(filenameACVolume, encoding="utf-8", index=False)
            symbol = IntervalStatsData.loc[0][ConfigChina.header_Symbol]

            RawIntervalStatsOld = AllIntervalStatsSet[AllIntervalStatsSet[ConfigChina.header_Symbol] == symbol]
            RawACVolumeSetOld = AllACVolumeSet[AllACVolumeSet[ConfigChina.header_Symbol] == symbol]
            IntervalStatsData = pd.concat([RawIntervalStatsOld, IntervalStatsData], ignore_index=True)
            ACVolumeData = pd.concat([RawACVolumeSetOld, ACVolumeData], ignore_index=True)
            hist_data_threads.append(
                pool.submit(generateHistStats, IntervalStatsData, ACVolumeData, symbol=symbol, info=info))
            AllIntervalStatsSet = AllIntervalStatsSet[AllIntervalStatsSet[ConfigChina.header_Symbol] != symbol]
            AllACVolumeSet = AllACVolumeSet[AllACVolumeSet[ConfigChina.header_Symbol] != symbol]
            pass
        pass
    index = 0
    if not AllIntervalStatsSet.empty and not AllACVolumeSet.empty:
        for (symbol), IntervalStatsData in AllIntervalStatsSet.groupby(by=[ConfigChina.header_Symbol]):
            index += 1
            info = "Old Symbol:{0}".format(symbol)
            ACVolumeData = AllACVolumeSet[AllACVolumeSet[ConfigChina.header_Symbol] == symbol]
            hist_data_threads.append(
                pool.submit(generateHistStats, IntervalStatsData, ACVolumeData, symbol=symbol, info=info))
            pass
        pass
    HistIntervalStatsDatas = []
    HistInstrumentProfiles = []
    for calculate_thread in hist_data_threads:
        HistIntervalStatsDataInst, HistInstrumentProfileInst, isHistData = calculate_thread.result()
        if not HistIntervalStatsDataInst.empty and not HistInstrumentProfileInst.empty:
            HistIntervalStatsDatas.append(HistIntervalStatsDataInst)
            HistInstrumentProfiles.append(HistInstrumentProfileInst)
            pass
        pass

    pool.shutdown()
    if len(HistIntervalStatsDatas) > 0 and len(HistInstrumentProfiles) > 0:
        processHistData(HistIntervalStatsDatas, HistInstrumentProfiles, targetDate, region, outDir)
    end_time = time.time()
    logger.write("Generating  file done >> cost time: {0:.2f}秒".format(end_time - start_time))
    pass


def calculateInstrumentRawIntervalStats(symbol, tickData=pd.DataFrame(),
                                        time_data_frame=pd.DataFrame(), volatilityPeriod=10, info=""):
    RawIntervalStats = pd.DataFrame(columns=ConfigChina.RawIntervalStatsHeader)
    RawACVolume = pd.DataFrame(columns=ConfigChina.ac_volume_header)
    if not time_data_frame.empty and not tickData.empty:
        logger.write("calculateInstrumentRawIntervalStats: {0} ".format(info))
        RawIntervalStatList = []
        bid_size = ask_size = spreade = trade_size = volume = median_trade_size = OHCLVolatility = CCVolatility = 0

        lastIntervalBidSize = lastIntervalAskSize = lastIntervalSpreadSize = lastIntervalTradeSize = lastIntervalVolume = 0
        prevVolatilityPeriodsOHCL = [float(0)]
        prevVolatilityPeriodsCC = [float(0)]
        for index, row in time_data_frame.iterrows():
            start_time_str = row[ConfigChina.header_StartTime]
            end_time_str = row[ConfigChina.header_EndTime]
            isTradable = row[ConfigChina.header_isTradable]
            isAuction = row[ConfigChina.header_isAuction]
            start_time_int = parseTimeStr(start_time_str)
            end_time_int = parseTimeStr(end_time_str)

            if isAuction == "T":
                tickDataInstrumentInterval = tickData[
                    (tickData[ConfigChina.tick_data_header_time] >= int(start_time_int)) & (tickData[
                                                                                                ConfigChina.tick_data_header_time] <= int(
                        end_time_int))]
            else:
                tickDataInstrumentInterval = tickData[
                    (tickData[ConfigChina.tick_data_header_time] >= int(start_time_int)) & (tickData[
                                                                                                ConfigChina.tick_data_header_time] < int(
                        end_time_int))]
            tickDataInstrumentInterval.reset_index(drop=True, inplace=True)

            if not tickDataInstrumentInterval.empty:
                if isTradable == "T":
                    bid_size = (tickDataInstrumentInterval[
                                    ConfigChina.tick_data_header_bidsize].mean() + lastIntervalBidSize) / 2
                    ask_size = (tickDataInstrumentInterval[
                                    ConfigChina.tick_data_header_asksize].mean() + lastIntervalAskSize) / 2

                    spreade = (tickDataInstrumentInterval[
                                   ConfigChina.header_SpreadSize].mean() + lastIntervalSpreadSize) / 2

                    trade_size = (tickDataInstrumentInterval[
                                      ConfigChina.tick_data_header_trdvol].mean() + lastIntervalTradeSize) / 2
                    volume = tickDataInstrumentInterval[ConfigChina.tick_data_header_trdvol].sum() + lastIntervalVolume
                    median_trade_size = tickDataInstrumentInterval[ConfigChina.tick_data_header_trdvol].median()
                    Open = tickDataInstrumentInterval.ix[0][ConfigChina.tick_data_header_trdprice]
                    Close = tickDataInstrumentInterval.ix[len(tickDataInstrumentInterval) - 1][
                        ConfigChina.tick_data_header_trdprice]

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
                    prevVolatilityPeriodsOHCL = [float(0)]
                    prevVolatilityPeriodsCC = [float(0)]

            add_data = pd.DataFrame({ConfigChina.header_Symbol: symbol,
                                     ConfigChina.header_StartTime: start_time_str,
                                     ConfigChina.header_EndTime: end_time_str,
                                     ConfigChina.header_BidSize: bid_size,
                                     ConfigChina.header_AskSize: ask_size,
                                     ConfigChina.header_SpreadSize: spreade,
                                     ConfigChina.header_TradeSize: trade_size,
                                     ConfigChina.header_Volume: volume,
                                     ConfigChina.header_VolumePercent: 0,
                                     ConfigChina.header_Volatility: OHCLVolatility,
                                     ConfigChina.header_CCVolatility: CCVolatility,
                                     ConfigChina.header_isAuction: isAuction
                                     }, columns=ConfigChina.RawIntervalStatsHeader, index=[0])
            add_data = add_data.fillna(0)
            RawIntervalStatList.append(add_data)
            bid_size = ask_size = spreade = trade_size = volume = median_trade_size = OHCLVolatility = CCVolatility = 0
            pass
        ac_volume = tickData.loc[len(tickData) - 1][ConfigChina.tick_data_header_acvol]
        RawACVolume = pd.DataFrame({ConfigChina.header_Symbol: [symbol],
                                    ConfigChina.header_ADV: ac_volume}, columns=ConfigChina.ac_volume_header)
        RawIntervalStats = pd.concat(RawIntervalStatList, ignore_index=True)
        instrumentDailyVolume = np.sum(RawIntervalStats[ConfigChina.header_Volume].tolist())
        if instrumentDailyVolume and instrumentDailyVolume > 0:
            RawIntervalStats[ConfigChina.header_VolumePercent] = RawIntervalStats.Volume / instrumentDailyVolume
        RawIntervalStats = RawIntervalStats.sort_values(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime],
                                                        axis=0, ascending=True)
        RawIntervalStats.reset_index(drop=True, inplace=True)
        RawACVolume = RawACVolume.drop_duplicates(ConfigChina.header_Symbol)
        RawACVolume.reset_index(drop=True, inplace=True)
        pass
    else:
        logger.write("Fail calculateInstrumentRawIntervalStats [ {0} ] not Tick Data Skipping.... ".format(symbol))
        pass
    return RawIntervalStats, RawACVolume, info
    pass
