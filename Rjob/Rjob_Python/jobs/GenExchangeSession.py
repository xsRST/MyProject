# -*- coding: UTF-8 -*-
import copy
import datetime
import threading
import xml.dom.minidom

import pandas as pd
from jobs import logger

import ConfigChina
import TimeUtils

Default_str = "Default"


class ExchangeSessionConfig:
    exchange_session_configs = {}

    def __init__(self, file_path, interval):
        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(file_path)
        collection = DOMTree.documentElement
        # 在集合中获取所有电影
        entrys = collection.getElementsByTagName("entry")
        for entry in entrys:
            marketNode = entry.getElementsByTagName("Market")[0]
            market_name = marketNode.childNodes[0].data
            sessionsConfigsEle = entry.getElementsByTagName("SessionsConfigs")[0]

            session_configs = SessionConfigs(sessionsConfigsEle, market_name, interval)
            if market_name and session_configs:
                self.exchange_session_configs[market_name] = session_configs

    pass

    def getSessionsConfigs(self, market_name):
        if market_name and self.exchange_session_configs.has_key(market_name):
            return self.exchange_session_configs.get(market_name)

        print ("not find {0} market session configs".format(market_name))
        return None
        pass

    pass

    def exist_market_session(self, market):
        return self.exchange_session_configs.has_key(market)
        pass

    def getSessionConfigs(self, market, instrument_type):

        if self.exist_market_session(market) and self.getSessionsConfigs(market).existSessionConfig(instrument_type):
            return self.getSessionsConfigs(market).getSessionConfig(instrument_type)
        else:
            raise Exception("Con`t find {0}--{1} or Default Exchange".format(market, instrument_type))
        pass

    def getSessions(self, market, instrument_type):
        return self.getSessionConfigs(market, instrument_type).getSessions()

    def getTimeDataFrame(self, market, instrument_type):
        if self.exist_market_session(market) and self.getSessionsConfigs(market).existSessionConfig(instrument_type):
            time_data_frame = self.getSessionsConfigs(market).getSessionConfig(instrument_type).sessions.time_data_frame
        else:
            raise Exception("Con`t find {0}--{1} or Default Exchange Session".format(market, instrument_type))
        return time_data_frame
        pass


class SessionConfigs:

    def __init__(self, session_configs_element, market_name, interval):
        if session_configs_element:
            session_config_elments = session_configs_element.getElementsByTagName("SessionsConfig")

            for session_config_elment in session_config_elments:
                instrument_type = session_config_elment.getAttribute('instrumentType')
                session_config = SessionConfig(session_config_elment, market_name, interval)
                if instrument_type and session_config:
                    if not hasattr(self, "sessionConfigs"): self.sessionConfigs = {}
                    self.sessionConfigs[instrument_type] = session_config

        pass

    def getSessionConfig(self, instrument_type):
        if instrument_type and self.sessionConfigs.has_key(instrument_type):
            return self.sessionConfigs.get(instrument_type)
        elif self.sessionConfigs.has_key(Default_str):
            return self.sessionConfigs.get(Default_str)
        print (
            "not find {0} instrument_session configs or not {1} session coonfig".format(instrument_type, Default_str))
        return None

    def existSessionConfig(self, instrument_type):
        return self.sessionConfigs.has_key(instrument_type) or self.sessionConfigs.has_key(Default_str)

    pass


class SessionConfig():
    def __init__(self, session_config_elment, market_name, interval):
        self.market = market_name
        self.instrument_type = session_config_elment.getAttribute('instrumentType')
        self.amPreOpenTime = session_config_elment.getElementsByTagName("amPreOpenTime")[0].childNodes[0].data
        self.amOpenTime = session_config_elment.getElementsByTagName("amOpenTime")[0].childNodes[0].data
        self.amCloseTime = session_config_elment.getElementsByTagName("amCloseTime")[0].childNodes[0].data
        if session_config_elment.getElementsByTagName("pmPreOpenTime"):
            self.pmPreOpenTime = session_config_elment.getElementsByTagName("pmPreOpenTime")[0].childNodes[0].data
            pass
        if session_config_elment.getElementsByTagName("pmOpenTime"):
            self.pmOpenTime = session_config_elment.getElementsByTagName("pmOpenTime")[0].childNodes[0].data
            pass
        if session_config_elment.getElementsByTagName("pmCloseTime"):
            self.pmCloseTime = session_config_elment.getElementsByTagName("pmCloseTime")[0].childNodes[0].data
            pass
        sessions_element = session_config_elment.getElementsByTagName("sessions")[0]
        self.sessions = Sessions(sessions_element, self.market, self.instrument_type, interval)
        pass

    def getSessions(self):
        return self.sessions
        pass

    def isCloseAutionTimeSec(self, timeInt):
        lock = threading.Lock()
        lock.acquire()
        isPMAution = False
        try:
            if self.sessions.getSessionFromKey("ContTradingPM"):
                openTimeSec = TimeUtils.getTimeStamp(self.sessions.getSessionFromKey("ContTradingPM").closeTime)
                pass
            else:
                openTimeSec = TimeUtils.getTimeStamp(self.sessions.getSessionFromKey("ContTradingAM").closeTime)
                pass
            closeTimeSec = TimeUtils.getTimeStamp(self.sessions.getSessionFromType("MarketClose").openTime)
            if timeInt > openTimeSec and timeInt < closeTimeSec:
                isPMAution = True
                pass
        except Exception as e:
            logger.write(e)
        finally:
            lock.release()
            pass
        return isPMAution
        pass

        pass

    def getAutionTimeSec(self, timeInt):
        lock = threading.Lock()
        lock.acquire()
        autionTimeSec = 0
        isPMAution = False
        try:
            amCloseTimeInt = TimeUtils.getTimeStamp(self.amCloseTime)
            if timeInt < amCloseTimeInt:
                autionTimeSec = TimeUtils.getTimeStamp(self.sessions.getSessionFromType("OpenAuction").closeTime) - 100
            else:
                autionTimeSec = TimeUtils.getTimeStamp(self.sessions.getSessionFromType("CloseAuction").openTime)
                isPMAution = True
        except Exception as e:
            logger.write(e)
        finally:
            lock.release()
            pass
        return autionTimeSec, isPMAution
        pass

    pass


class Sessions():

    def __init__(self, sessions_element, market, instrument_type, interval):
        self.market = market
        self.instrument_type = instrument_type
        self.interval = interval
        self.raw_time_data_frame = pd.DataFrame()
        self.hist_time_data_frame = pd.DataFrame()
        self.sessions_type = {}
        self.sessions_key = {}
        if sessions_element:
            session_elments = sessions_element.getElementsByTagName("session")
            for session_elment in session_elments:
                sessionKey = str(session_elment.getAttribute('sessionKey'))
                sessionType = str(session_elment.getAttribute('sessionType'))
                session = Session(session_elment)
                if session:
                    self.sessions_type[sessionType] = session
                    self.sessions_key[sessionKey] = session

                    pass
                pass
            pass
        self.create_time_data_frame()
        pass

    def getSessionFromType(self, sessions_type):
        return self.sessions_type.get(sessions_type)
        pass

    def getSessionFromKey(self, sessions_key):
        return self.sessions_key.get(sessions_key)
        pass

    def get_raw_time_data_frame(self):
        if self.raw_time_data_frame.empty:
            self.create_time_data_frame()
            pass
        return copy.deepcopy(self.raw_time_data_frame)
        pass

    def get_hist_time_data_frame(self):
        if self.hist_time_data_frame.empty:
            self.create_time_data_frame()
            pass
        return copy.deepcopy(self.hist_time_data_frame)
        pass

    def create_time_data_frame(self):
        if self.raw_time_data_frame.empty or self.hist_time_data_frame.empty:
            lock = threading.Lock()
            lock.acquire()
            try:
                dataList = []
                histdataList = []
                for session in self.sessions_key.values():
                    start_time = datetime.datetime.strptime(session.openTime, '%H:%M:%S')
                    end_time = datetime.datetime.strptime(session.closeTime, '%H:%M:%S')
                    isTradable = session.isTradable
                    isAuction = session.isAuction
                    while not start_time.__ge__(end_time):
                        if (session.sessionType in ["MarketClose", "IntraDayClose"]) or (str(self.market).upper().strip() == "TW" and session.sessionType == "OpenAuction"):
                            start_time_str = datetime.datetime.strftime(start_time, '%H:%M:%S')
                            end_time_str = datetime.datetime.strftime(end_time, '%H:%M:%S')
                            start_time = end_time_str
                        else:
                            start_time_str = datetime.datetime.strftime(start_time, '%H:%M:%S')
                            start_time = (start_time + datetime.timedelta(minutes=self.interval))
                            end_time_str = datetime.datetime.strftime(start_time, '%H:%M:%S')
                            if start_time.__ge__(end_time):
                                end_time_str = datetime.datetime.strftime(end_time, '%H:%M:%S')
                                pass
                            pass
                        pass
                        add_data = pd.DataFrame({ConfigChina.tick_data_header_time: TimeUtils.getTimeStamp(start_time_str),
                                                 ConfigChina.header_StartTime: start_time_str,
                                                 ConfigChina.header_EndTime: end_time_str,
                                                 ConfigChina.header_BidSize: 0,
                                                 ConfigChina.header_AskSize: 0,
                                                 ConfigChina.header_SpreadSize: 0,
                                                 ConfigChina.header_TradeSize: 0,
                                                 ConfigChina.header_Volume: 0,
                                                 ConfigChina.header_VolumePercent: 0,
                                                 ConfigChina.header_Volatility: 0,
                                                 ConfigChina.header_CCVolatility: 0,
                                                 ConfigChina.header_isAuction: isAuction,
                                                 ConfigChina.header_isTradable: isTradable
                                                 }, index=[0])
                        dataList.append(add_data)

                        add_hist_data = pd.DataFrame({ConfigChina.tick_data_header_time: TimeUtils.getTimeStamp(start_time_str),
                                                      ConfigChina.header_StartTime: start_time_str,
                                                      ConfigChina.header_EndTime: end_time_str,
                                                      ConfigChina.header_TradeSize: 0,
                                                      ConfigChina.header_TradeSizeSD: 0,
                                                      ConfigChina.header_BidSize: 0,
                                                      ConfigChina.header_BidSizeSD: 0,
                                                      ConfigChina.header_AskSize: 0,
                                                      ConfigChina.header_AskSizeSD: 0,
                                                      ConfigChina.header_SpreadSize: 0,
                                                      ConfigChina.header_SpreadSizeSD: 0,
                                                      ConfigChina.header_Volume: 0,
                                                      ConfigChina.header_VolumeSD: 0,
                                                      ConfigChina.header_VolumePercent: 0,
                                                      ConfigChina.header_VolumePercentSD: 0,
                                                      ConfigChina.header_Volatility: 0,
                                                      ConfigChina.header_VolatilitySD: 0,
                                                      ConfigChina.header_CCVolatility: 0,
                                                      ConfigChina.header_CCVolatilitySD: 0,
                                                      ConfigChina.header_isAuction: isAuction,
                                                      ConfigChina.header_isTradable: isTradable
                                                      }, index=[0])
                        histdataList.append(add_hist_data)
                        pass
                    pass
                self.raw_time_data_frame = pd.concat(dataList, ignore_index=True)
                self.raw_time_data_frame = self.raw_time_data_frame.sort_values(by=ConfigChina.header_StartTime, axis=0, ascending=True)
                self.raw_time_data_frame.reset_index(drop=True, inplace=True)
                self.hist_time_data_frame = pd.concat(histdataList, ignore_index=True)
                self.hist_time_data_frame = self.hist_time_data_frame.sort_values(by=ConfigChina.header_StartTime, axis=0, ascending=True)
                self.hist_time_data_frame.reset_index(drop=True, inplace=True)
            except Exception as e:
                logger.write(e)
                self.raw_time_data_frame = pd.DataFrame()
                self.hist_time_data_frame = pd.DataFrame()
            finally:
                lock.release()
                pass
            pass
        pass


class Session():

    def __init__(self, session_element):
        self.sessionKey = str(session_element.getAttribute('sessionKey'))
        self.sessionType = str(session_element.getAttribute('sessionType'))
        self.openTime = str(session_element.getAttribute('openTime'))
        self.closeTime = str(session_element.getAttribute('closeTime'))

        self.isTradable = self.parseBoolean(session_element.getAttribute('isTradable'))
        self.isCancellable = self.parseBoolean(session_element.getAttribute('isCancellable'))
        self.isAmendable = self.parseBoolean(session_element.getAttribute('isAmendable'))
        self.isSupportMarketOrder = self.parseBoolean(session_element.getAttribute('isSupportMarketOrder'))
        self.isSupportLmtOrder = self.parseBoolean(session_element.getAttribute('isSupportLmtOrder'))
        self.isAuction = self.parseBoolean(session_element.getAttribute('isAuction'))
        pass

    pass

    def parseBoolean(self, param):
        if param and param.strip().upper().startswith("T"):
            return "T"
        else:
            return "F"
        pass
