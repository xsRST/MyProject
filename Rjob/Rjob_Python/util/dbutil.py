# coding=utf-8
import os
import sys

import pandas as pd

import logger

sys.path.append(os.getenv("HOME") + "/Python/util")
import config
from newdbutil import DBConnectionManger

engine = DBConnectionManger().conn


def execute_and_fetchall(sql):
    results = engine.execute(sql)
    return results
    pass


def excute_dml(sql):
    results = engine.execute(sql)
    return results
    pass


def data_frame_to_sql(data, tables):
    data.to_sql(tables, con=engine, index=False, if_exists="append")
    return data
    pass


def data_frame_read_sql(sql):
    logger.write(sql)
    data = pd.read_sql_query(sql, con=engine)
    return data
    pass


def getInstrumentList(targetDate, exchanges, instrumentTypes):
    querySQL = "select distinct REPLACE( REPLACE(Symbol,'HS','HK'),'HZ','HK') as Symbol ,REPLACE( REPLACE(Exchange,'HS','HK'),'HZ','HK') as Exchange, InstrumentType " \
               "from GenusInstrument where  TheDate ={0} and InstrumentType in (".format(targetDate)

    # querySQL = "select distinct Symbol  Exchange, InstrumentType from GenusInstrument where  TheDate = " + targetDate + " and InstrumentType in ( "
    for instrument_type in instrumentTypes:
        querySQL += "'" + instrument_type + "',"
    querySQL = querySQL[0:len(querySQL) - 1]
    querySQL += ")  and Exchange in ( "
    for exchange in exchanges:
        if exchange == "HK":
            querySQL += "'HS','HZ','HK',"
            pass
        querySQL += "'" + exchange + "',"
        pass

    querySQL = querySQL[0:len(querySQL) - 1]
    querySQL += " )  order By Symbol"
    data_Instrument = data_frame_read_sql(querySQL)
    if data_Instrument.empty:
        logger.write("Not Found GenusInstrument From DB :{} - {} ".format(config.dbhost, config.dbname))
        pass
    return data_Instrument
    pass


def genBusinessDay(today):
    logger.write("getBusinessDay from DB: Today>>  {0}".format(today))
    year = str(today)[0:4]
    preDate = str(int(year) - 1) + str(today)[4:]
    querySQL = "select TheDate From GenusTradingDays WHERE  TheDate >='{0}' Order BY  TheDate DESC ".format(preDate)
    data_Instrument = data_frame_read_sql(querySQL)
    if data_Instrument.empty:
        logger.write("Not Found GenusTradingDays From DB :{} - {} ".format(config.dbhost, config.dbname))
        os._exit(0)
        pass

    if data_Instrument[data_Instrument["TheDate"] == int(today)].empty:
        logger.write("TargetDate {} is NOT a business day! Please Check".format(today))
        os._exit(0)
        pass
    if data_Instrument[data_Instrument["TheDate"] > int(today)].empty:
        logger.write("Nex business day is Null! Please Check".format(today))
        os._exit(0)
        pass

    data_Instrument.sort_values(by=["TheDate"], axis=0, ascending=True, inplace=True)

    nextBusinessDay = data_Instrument[data_Instrument["TheDate"] > int(today)].head(1)
    prev_business_days = data_Instrument[data_Instrument["TheDate"] <= int(today)]
    prev_business_days.columns = ['TradeDay']
    nextBusinessDay.columns = ['TradeDay']
    nextBusinessDay.reset_index(drop=True, inplace=True)
    prev_business_days.reset_index(drop=True, inplace=True)
    logger.write("getBusinessDay  Done")
    return prev_business_days, nextBusinessDay
    pass

