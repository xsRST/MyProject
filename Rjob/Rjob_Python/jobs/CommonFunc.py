# coding=utf-8
import os
import threading
import time

import pandas as pd

import ConfigChina
import logger
from MySQLDB import getInstrumentList


def parseTimeStr(time_str):
    time_int = 0
    if not len(time_str) < 8:
        time_int = int(time_str[0:2]) * 3600 + int(time_str[3:5]) * 60 + +int(time_str[6:7])
    return time_int
    pass


# ============================= init func =================================


# ============================ init func detail implement ================
def genTodayBusinessDay(today, configDir, region):
    logger.write("genTodayBusinessDay file for {0}".format(today))
    businessDays_file_path = os.path.join(configDir, "{0}.{1}".format("BusinessDaysFile", region))
    logger.write("Load BusinessDaysFile >>   " + str(businessDays_file_path))
    businessDays_list = pd.read_csv(businessDays_file_path, sep='\t', encoding="utf-8", engine='c', header=None, names=["TradeDay"])
    # business day check
    if businessDays_list[businessDays_list["TradeDay"] == int(today)].empty:
        logger.write("TargetDate {} is NOT a business day! Please Check".format(today))
        os._exit(0)

    nextBusinessDay = businessDays_list[businessDays_list["TradeDay"] > int(today)].min()
    nextBusinessDay = nextBusinessDay["TradeDay"]
    prev_business_days = businessDays_list[businessDays_list["TradeDay"] < int(today)]

    logger.write("getTodayBusinessDay  Done")
    return prev_business_days, nextBusinessDay
    pass



# =========================== Loading data from file =========================
def retrieveTickDataFromFile(targetDate, defaultTickFileDirectory, tickFileSuffix):
    tickfile = os.path.join(defaultTickFileDirectory, "{0}{1}".format(targetDate, tickFileSuffix))
    if os.path.exists(tickfile):
        lock = threading.Lock()
        lock.acquire()
        print("Loading below fields from tick file {0} ".format(tickfile))
        startTime = time.time()
        with open(tickfile, "r") as f_in:
            first_line = f_in.readline()
        if ConfigChina.tick_data_header_symbol in str(first_line):
            tickdata = pd.read_csv(tickfile, sep=",", encoding="utf-8", engine='c')
        else:
            tickdata = pd.read_csv(tickfile, sep=",", encoding="utf-8", engine='c', header=None, names=ConfigChina.tick_data_header)

        tickdata = tickdata.dropna()
        tickdata = tickdata.fillna(0)
        tickdata = tickdata[(tickdata[ConfigChina.tick_data_header_asksize] > 0) & (tickdata[ConfigChina.tick_data_header_trdvol] > 0)]
        tickdata[ConfigChina.tick_data_header_trdvol] = tickdata[ConfigChina.tick_data_header_trdvol].astype('int32')
        tickdata[ConfigChina.tick_data_header_trdprice] = tickdata[ConfigChina.tick_data_header_trdprice].astype('float32')
        tickdata[ConfigChina.tick_data_header_acvol] = tickdata[ConfigChina.tick_data_header_acvol].astype('int32')
        tickdata[ConfigChina.tick_data_header_askprice] = tickdata[ConfigChina.tick_data_header_askprice].astype('float32')
        tickdata[ConfigChina.tick_data_header_asksize] = tickdata[ConfigChina.tick_data_header_asksize].astype('int32')
        tickdata[ConfigChina.tick_data_header_bidprice] = tickdata[ConfigChina.tick_data_header_bidprice].astype('float32')
        tickdata[ConfigChina.tick_data_header_bidsize] = tickdata[ConfigChina.tick_data_header_bidsize].astype('int32')
        tickdata[ConfigChina.header_SpreadSize] = 2000 * ((tickdata[ConfigChina.tick_data_header_askprice] - tickdata[ConfigChina.tick_data_header_bidprice]) / (
                tickdata[ConfigChina.tick_data_header_askprice] + tickdata[ConfigChina.tick_data_header_bidprice]))

        read_csv_endTime = time.time()
        print("read_csv time cost {0:.2f} 秒:".format(int(read_csv_endTime) - int(startTime)))
        lock.release()
    else:
        raise RuntimeError("Could not find tickfile >> {0} aborting".format(tickfile))
    return tickdata
    pass


def retrieveHistIntervalStatsFromFile(prevBusinessDays, outputDir, region, defaultMaxBDtoUse):
    Raws = []
    RawIntervalStatsSet = pd.DataFrame(columns=ConfigChina.RawIntervalStatsHeader)
    prevBusinessDays = prevBusinessDays["TradeDay"].values.tolist()
    for n in range(int(defaultMaxBDtoUse)):
        day = prevBusinessDays[n]
        filename = os.path.join(outputDir, "{0}-{1}{2}".format(region, "RawIntervalStats", day))
        if os.path.exists(filename):
            logger.write(
                "Reading RawIntervalStats file for {} :{} ; ready to open file:{}".format(region, day, filename))
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


def retrieveHistACVolumeFromFile(prevBusinessDays, outputDir, region, defaultMaxBDtoUse):
    Raws = []
    RawACVolumeRet = pd.DataFrame(columns=ConfigChina.ac_volume_header)
    prevBusinessDays = prevBusinessDays["TradeDay"].values.tolist()
    for n in range(int(defaultMaxBDtoUse)):
        day = prevBusinessDays[n]
        filename = os.path.join(outputDir, "{0}-{1}{2}".format(region, "RawACVolume", day))
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


def retrieveHistInstrumentsFromFile(today, prevBusinessDays, outputDir, userExchnages, useInstrumentTypes, defaultMaxBDtoUse):
    prevBusinessDays = prevBusinessDays["TradeDay"].values.tolist()
    businessDays = [today] + prevBusinessDays
    instrumentDatas = []
    for n in range(int(defaultMaxBDtoUse)):
        day = businessDays[n]
        hist_instrument_path = ("{0}" + os.path.sep + "{1}{2}.{3}").format(outputDir, "GenusInstrument", day, "txt")
        data = pd.DataFrame()
        if not os.path.exists(hist_instrument_path):
            data = getInstrumentList(day, userExchnages, useInstrumentTypes)
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


def writeDataToFileAppend(filename, data):
    lock = threading.Lock()
    lock.acquire()
    if os.path.isfile(filename):
        data.to_csv(filename, encoding="utf-8", index=False, header=0, mode='ab+')
    else:
        data.to_csv(filename, encoding="utf-8", index=False)
        pass
    lock.release()
    pass
