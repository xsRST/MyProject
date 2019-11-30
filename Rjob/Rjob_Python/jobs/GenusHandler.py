# coding=utf-8
import Queue
import os
import threading
import time

import pandas as pd
from concurrent.futures import ThreadPoolExecutor

import ConfigChina
from GenusCalculator import Calculator
from MySQLDB import getInstrumentList
from jobs import logger, CommonFunc


class Handler:
    def __init__(self, manager):
        self.rawDataqueue = Queue.Queue()
        self.manager = manager
        self.today = self.manager.today
        self.maxThreadsTotal = self.manager.maxThreadsTotal
        self.volatilityPeriod = self.manager.volatilityPeriod
        self.prevBusinessDays, self.nextBusinessDay = CommonFunc.genTodayBusinessDay(self.today, self.manager.configDir, self.manager.region)

        data_Instrument = getInstrumentList(self.today, self.manager.userExchnages, self.manager.useInstrumentTypes)
        if data_Instrument.empty:
            raise Exception("")
        tickdata = CommonFunc.retrieveTickDataFromFile(self.today, self.manager.defaultTickFileDirectory, self.manager.tickFileSuffix)

        tickdata_symbols = list(set(tickdata[ConfigChina.tick_data_header_symbol].tolist()))
        instrument_symbols = list(set(data_Instrument[ConfigChina.instrument_header_Symbol].tolist()))
        process_symbols = list(set(tickdata_symbols).intersection(set(instrument_symbols)))
        data_Instrument = data_Instrument[data_Instrument[ConfigChina.instrument_header_Symbol].isin(process_symbols)]
        self.todatyInstrument = data_Instrument
        if data_Instrument.empty:
            raise Exception("Can`t Match Instrument From tick Data")
        instrument_path = ("{0}" + os.path.sep + "{1}{2}.{3}").format(self.manager.outputDir, "GenusInstrument", self.today, "txt")
        self.todatyInstrument.to_csv(instrument_path, encoding='utf-8', index=False)
        tickdata = tickdata[tickdata[ConfigChina.tick_data_header_symbol].isin(process_symbols)]
        self.tick_group = tickdata.groupby(by=[ConfigChina.tick_data_header_symbol])
        self.exchangeSessionConfig = self.manager.exchangeSessionConfig
        self.AllHistInstrument = CommonFunc.retrieveHistInstrumentsFromFile(self.today, self.prevBusinessDays, self.manager.outputDir, self.manager.userExchnages,
                                                                            self.manager.useInstrumentTypes, self.manager.defaultMaxBDtoUse)
        pass

    def start(self):
        logger.write("start CalcRawData... ")
        pool = ThreadPoolExecutor(max_workers=self.maxThreadsTotal)

        AllHistRawInterVal = CommonFunc.retrieveHistIntervalStatsFromFile(self.prevBusinessDays, self.manager.outputDir, self.manager.region, self.manager.defaultMaxBDtoUse)
        AllHistRawACVolume = CommonFunc.retrieveHistACVolumeFromFile(self.prevBusinessDays, self.manager.outputDir, self.manager.region, self.manager.defaultMaxBDtoUse)

        t = threading.Thread(target=self.startRawDataWriterThread, args=())
        t.start()
        index = 0
        task = []
        # tickdata 数据,根据数据加到对应时间段上;减少
        for (symbol), tickdata in self.tick_group:
            index += 1
            HistRawInterVals = AllHistRawInterVal[AllHistRawInterVal[ConfigChina.header_Symbol] == symbol]
            HistRawACVolumes = AllHistRawACVolume[AllHistRawACVolume[ConfigChina.header_Symbol] == symbol]
            HistInstruments = self.AllHistInstrument[self.AllHistInstrument[ConfigChina.header_Symbol] == symbol]

            info = " [ {0} - {1} ] >> {2} ".format(len(self.todatyInstrument), index, symbol)
            calculator = Calculator(self, tickdata, HistRawInterVals, HistRawACVolumes, HistInstruments, info=info)
            task.append(pool.submit(calculator.startCalcDataSymbol))
            pass

        logger.write("End CalcRawData... ")
        logger.write("start Add RemainData... ")
        hist_symbols = list(set(self.AllHistInstrument[ConfigChina.instrument_header_Symbol].tolist()))
        AllHistRawInterVal = AllHistRawInterVal[AllHistRawInterVal[ConfigChina.instrument_header_Symbol].isin(hist_symbols)]
        AllHistRawACVolume = AllHistRawACVolume[AllHistRawACVolume[ConfigChina.instrument_header_Symbol].isin(hist_symbols)]
        process_symbols = list(set(self.todatyInstrument[ConfigChina.instrument_header_Symbol].tolist()))
        remainHistRawInterVals = AllHistRawInterVal[~AllHistRawInterVal[ConfigChina.instrument_header_Symbol].isin(process_symbols)]
        remainHistRawACVolume = AllHistRawACVolume[~AllHistRawACVolume[ConfigChina.instrument_header_Symbol].isin(process_symbols)]
        remainHistRawInterVals.reset_index(drop=True, inplace=True)
        remainHistRawACVolume.reset_index(drop=True, inplace=True)

        remainCount = remainHistRawACVolume.shape[0]
        index = 0
        for (symbol), RawACVolumes in remainHistRawACVolume.groupby(by=[ConfigChina.instrument_header_Symbol]):
            index += 1
            RawInterVals = remainHistRawInterVals[remainHistRawInterVals[ConfigChina.header_Symbol] == symbol]
            HistInstruments = self.AllHistInstrument[self.AllHistInstrument[ConfigChina.header_Symbol] == symbol]
            info = " [ {0} - {1} ] >> Remain {2} ".format(remainCount, index, symbol)
            calculator = Calculator(self, static_info=HistInstruments, info=info)
            task.append(pool.submit(calculator.generatorHistDataSymbol, RawInterVals, RawACVolumes))
            pass
        logger.write("start CalcHistData... ")
        HistIntervalStatsDatas = []
        HistInstrumentProfiles = []
        for future in task:
            histData = future.result()
            HistIntervalStatsDataInst = histData[0]
            HistInstrumentProfileInst = histData[1]
            HistIntervalStatsDatas.append(HistIntervalStatsDataInst)
            HistInstrumentProfiles.append(HistInstrumentProfileInst)
            pass
        logger.write("End CalcHistData... ")
        if len(HistIntervalStatsDatas) > 0 and len(HistInstrumentProfiles) > 0:
            self.processHistData(HistIntervalStatsDatas, HistInstrumentProfiles)
            pass
        logger.write("Wait Queue To End...")
        self.rawDataqueue.join()
        pass

    def startRawDataWriterThread(self):

        filenameStats = os.path.join(self.manager.outputDir, "{0}-{1}{2}".format(self.manager.region, "RawIntervalStats", self.today))
        filenameACVolume = os.path.join(self.manager.outputDir, "{0}-{1}{2}".format(self.manager.region, "RawACVolume", self.today))
        if os.path.isfile(filenameStats):
            os.remove(filenameStats)
            pass
        if os.path.isfile(filenameACVolume):
            os.remove(filenameACVolume)
            pass
        while True:
            rawData = self.rawDataqueue.get()
            self.rawDataqueue.task_done()
            RawIntervalStats = rawData[0]
            RawAcvolume = rawData[1]
            CommonFunc.writeDataToFileAppend(filenameStats, RawIntervalStats)
            CommonFunc.writeDataToFileAppend(filenameACVolume, RawAcvolume)
            pass
        pass

    def processHistData(self, HistIntervalStatsDatas, HistInstrumentProfiles):
        logger.write("Generating Hist File file")
        start_time = time.time()
        HistIntervalStatsData = pd.DataFrame(columns=ConfigChina.GenusHistIntervalStats_header)
        HistInstrumentProfile = pd.DataFrame(columns=ConfigChina.GenusInstrumentProfile_header)

        if len(HistIntervalStatsDatas) > 0 and len(HistInstrumentProfiles) > 0:
            HistIntervalStatsData = pd.concat(HistIntervalStatsDatas, ignore_index=True)
            HistInstrumentProfile = pd.concat(HistInstrumentProfiles, ignore_index=True)
            HistIntervalStatsData = HistIntervalStatsData.drop_duplicates(ConfigChina.symbol_start_end_header)
            HistIntervalStatsData = HistIntervalStatsData.sort_values(by=ConfigChina.symbol_start_end_header, axis=0, ascending=True)
            HistIntervalStatsData.reset_index(drop=True, inplace=True)
            HistInstrumentProfile = HistInstrumentProfile.drop_duplicates(ConfigChina.header_Symbol)
            HistInstrumentProfile = HistInstrumentProfile.sort_values(by=ConfigChina.header_Symbol, axis=0, ascending=True)
            HistInstrumentProfile.reset_index(drop=True, inplace=True)
        else:
            logger.write("Not Find Hist Data")

        IntervalStatsFileName = os.path.join(self.manager.outputDir, "{0}{1}{2}".format("GenusHistIntervalStats", self.nextBusinessDay, ".csv"))
        InstrumentProfileFileName = os.path.join(self.manager.outputDir, "{0}{1}{2}".format("GenusInstrumentProfile", self.nextBusinessDay, ".csv"))
        HistIntervalStatsData.to_csv(IntervalStatsFileName, encoding="utf-8", index=False, header=False)
        HistInstrumentProfile.to_csv(InstrumentProfileFileName, encoding="utf-8", index=False, header=False)
        logger.write(" Writer To File : {0}".format(IntervalStatsFileName))
        logger.write("Writer To File : {0}".format(InstrumentProfileFileName))

        if self.manager.discriminateExchange:
            for exchange in ConfigChina.Exchange:
                IntervalStatsFileName = os.path.join(self.manager.outputDir, "{0}{1}_{2}{3}".format("GenusHistIntervalStats", self.nextBusinessDay, exchange, ".csv"))
                InstrumentProfileFileName = os.path.join(self.manager.outputDir, "{0}{1}_{2}{3}".format("GenusInstrumentProfile", self.nextBusinessDay, exchange, ".csv"))

                instrumentUniverseExchange = self.AllHistInstrument[self.AllHistInstrument[ConfigChina.instrument_header_Exchange] == exchange]
                symbols = list(set(instrumentUniverseExchange[ConfigChina.header_Symbol].tolist()))
                HistIntervalStatsDataExchange = HistIntervalStatsData[HistIntervalStatsData[ConfigChina.header_Symbol].isin(symbols)]
                HistInstrumentProfileExchange = HistInstrumentProfile[HistInstrumentProfile[ConfigChina.header_Symbol].isin(symbols)]
                HistIntervalStatsDataExchange.to_csv(IntervalStatsFileName, encoding="utf-8", index=False, header=False)
                HistInstrumentProfileExchange.to_csv(InstrumentProfileFileName, encoding="utf-8", index=False, header=False)
                logger.write(" Writer To File : {0}".format(IntervalStatsFileName))
                logger.write("Writer To File : {0}".format(InstrumentProfileFileName))
                pass
            pass
        end_time = time.time()
        logger.write("generateEvoSchedClassificationsFile Done finish cost  {0:.2f} 秒 ".format(end_time - start_time))

        pass
