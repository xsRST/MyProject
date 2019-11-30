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
    return data_Instrument
    pass
