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

def genTodayBusinessDay(targetDate, dir=ConfigChina.defaultDataDirectory, configDir=ConfigChina.defaultConfigDirectory, region='China'):
    logger.write("genTodayBusinessDay file for {0}".format(targetDate))
    businessDays_file_path = os.path.join(configDir, "{0}.{1}".format("BusinessDaysFile", region))
    logger.write("Load BusinessDaysFile >>   " + str(businessDays_file_path))
    businessDays_list = pd.read_csv(businessDays_file_path, sep='\t', encoding="utf-8", engine='c', header=None,
                                    names=["TradeDay"])
    # business day check
    if businessDays_list[businessDays_list["TradeDay"] == int(targetDate)].empty:
        logger.write("TargetDate {} is NOT a business day! Please Check".format(targetDate))
        os._exit(0)

    nextBusinessDay = businessDays_list[businessDays_list["TradeDay"] > int(targetDate)].min()
    nextBusinessDay = nextBusinessDay["TradeDay"]
    prev_business_days = businessDays_list[businessDays_list["TradeDay"] < int(targetDate)]

    logger.write("getTodayBusinessDay  Done")
    return prev_business_days, nextBusinessDay
    pass


def genTodayHistInstruments(targetDate):
    todatyInstrument = getInstrumentList(targetDate)

    return todatyInstrument
    pass


# =========================== Loading data from file =========================
def retrieveTickDataFromFile(targetDate, defaultTickFileDirectory, tickFileSuffix):
    tickfile = os.path.join(defaultTickFileDirectory, "{0}{1}".format(targetDate, tickFileSuffix))
    lock = threading.Lock()
    lock.acquire()
    if os.path.exists(tickfile):
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
    else:
        raise RuntimeError("Could not find tickfile >> {0} aborting".format(tickfile))
    return tickdata
    pass


def retrieveNextBusinessDayFromFile(targetDate, region='China', dir=ConfigChina.defaultDataDirectory):
    logger.write("Loading Next Business Days file for {0} : {1}".format(region, targetDate))
    next_business_day_path = ("{0}" + os.path.sep + "{1}-{2}{3}").format(dir, region, "NextBusinessDay", targetDate)
    next_business_day = pd.read_csv(next_business_day_path, encoding='utf-8', engine='c')
    return (next_business_day["TradeDay"].values[0])
    pass


def retrieveBusinessDayFromFile(targetDate, region='China', dir=ConfigChina.defaultDataDirectory):
    logger.write("Loading Previous Business Days file for {0} : {1}".format(region, targetDate))
    prev_business_days_path = ("{0}" + os.path.sep + "{1}-{2}{3}").format(dir, region, "PrevBusinessDays", targetDate)
    return (pd.read_csv(prev_business_days_path, encoding='utf-8', engine='c'))
    pass


def retrieveHistInstrumentsFromFile(targetDate, region='China', NDays=1, dir=ConfigChina.defaultDataDirectory):
    hist_instrument = pd.DataFrame(columns=ConfigChina.instrument_header)
    if int(NDays) <= 1:
        hist_instrument_path = ("{0}" + os.path.sep + "{1}{2}.{3}").format(dir, "GenusInstrument", targetDate, "txt")
        if os.path.exists(hist_instrument_path):
            logger.write("Reading HistInstruemnt file >>  {0} : {1}".format(region, targetDate))
            hist_instrument = pd.read_csv(hist_instrument_path, encoding="utf-8", engine='c')
            hist_instrument = hist_instrument.drop_duplicates(ConfigChina.header_Symbol)
        else:
            logger.write("not found. Skipping this RawIntervalStats file >> {0}".format(hist_instrument_path))
    else:
        businessDays = retrieveBusinessDayFromFile(targetDate, region)
        businessDays = businessDays["TradeDay"].values.tolist()
        instrumentDatas = []
        for n in range(int(NDays)):
            day = businessDays[n]
            hist_instrument_path = ("{0}" + os.path.sep + "{1}{2}.{3}").format(dir, "GenusInstrument", day, "txt")
            if not os.path.exists(hist_instrument_path):
                genTodayHistInstruments(day, dir)
                pass
            if os.path.exists(hist_instrument_path):
                logger.write("Reading HistInstruemnt file >>  {0} : {1}".format(region, day))
                data = pd.read_csv(hist_instrument_path, encoding="utf-8", engine='c')
                instrumentDatas.append(data)
            pass
        if len(instrumentDatas) > 0:
            hist_instrument = pd.concat(instrumentDatas, ignore_index=True)
            hist_instrument = hist_instrument.drop_duplicates(ConfigChina.header_Symbol)
            hist_instrument.reset_index(drop=True, inplace=True)
        else:
            logger.write("Not Find InstrumentData, Please check DB Host ")
            os._exit(0)
    return hist_instrument
    pass
