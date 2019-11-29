# -*- coding: UTF-8 -*-
import os
import sys

import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from jobs import ConfigChina
from jobs.GenExchangeSession import ExchangeSessionConfig

sys.path.append(os.getenv("HOME") + "/Python/monitor")

s = "\xe6\xad\xa3\xe5\xb8\xb8"
print s.decode('utf8')


def handleHistInterval(symbol, startTime, endTime, intervalStat, acvol):
    add_data = {
        ConfigChina.header_Symbol: symbol,
        ConfigChina.header_StartTime: startTime,
        ConfigChina.header_EndTime: endTime,
        ConfigChina.header_TradeSize: intervalStat[ConfigChina.header_TradeSize].mean(),
        ConfigChina.header_TradeSizeSD: intervalStat[ConfigChina.header_TradeSize].std(),
        ConfigChina.header_BidSize: intervalStat[ConfigChina.header_BidSize].mean(),
        ConfigChina.header_BidSizeSD: intervalStat[ConfigChina.header_BidSize].std(),
        ConfigChina.header_AskSize: intervalStat[ConfigChina.header_AskSize].mean(),
        ConfigChina.header_AskSizeSD: intervalStat[ConfigChina.header_AskSize].std(),
        ConfigChina.header_SpreadSize: intervalStat[ConfigChina.header_SpreadSize].mean(),
        ConfigChina.header_SpreadSizeSD: intervalStat[ConfigChina.header_SpreadSize].std(),
        ConfigChina.header_Volume: intervalStat[ConfigChina.header_Volume].mean(),
        ConfigChina.header_VolumeSD: intervalStat[ConfigChina.header_Volume].std(),
        ConfigChina.header_VolumePercent: intervalStat[ConfigChina.header_VolumePercent].mean() * acvol,
        ConfigChina.header_VolumePercentSD: intervalStat[ConfigChina.header_VolumePercent].std() * acvol,
        ConfigChina.header_Volatility: intervalStat[ConfigChina.header_Volatility].mean(),
        ConfigChina.header_VolatilitySD: intervalStat[ConfigChina.header_Volatility].std(),
        ConfigChina.header_CCVolatility: intervalStat[ConfigChina.header_CCVolatility].mean(),
        ConfigChina.header_CCVolatilitySD: intervalStat[ConfigChina.header_CCVolatility].std(),
    }
    return add_data

    pass


def testApply():
    data = pd.read_csv("D:\project\Genus\GenusOwn\Rjob\Rjob_Python\output\China-RawIntervalStats20191122", encoding="utf-8", engine='c')
    data = data[data[ConfigChina.header_Symbol] == "0050.TW"]
    data.reset_index(drop=True, inplace=True)
    threads = []
    pool = ThreadPoolExecutor(max_workers=24)
    statsGroup = data.groupby(by=[ConfigChina.header_Symbol, ConfigChina.header_StartTime, ConfigChina.header_EndTime])

    for (symbol, startTime, endTime), intervalStat in statsGroup:
        threads.append(pool.submit(handleHistInterval, symbol, startTime, endTime, intervalStat, 1000))
    pass
    HistIntervalStatsData = pd.DataFrame(columns=ConfigChina.GenusHistIntervalStats_header)

    for future in threads:
        add_data = future.result()
        HistIntervalStatsData = HistIntervalStatsData.append(add_data, ignore_index=True)
        pass

    print HistIntervalStatsData
    pass


def testNoDataDeplay():
    data = pd.read_csv("D:\project\Genus\GenusOwn\Rjob\Rjob_Python\output\China-RawIntervalStats20191122", encoding="utf-8", engine='c')
    genus_exchange_session_path = os.path.join(ConfigChina.defaultConfigDirectory, "GenusStrategyExchangeSessions.xml")
    interval = 5
    exchangeSessionConfig = ExchangeSessionConfig(genus_exchange_session_path, interval)
    time_frame = exchangeSessionConfig.getSessions("TW", "D").create_time_data_frame()
    time_frame = time_frame[ConfigChina.GenusHistIntervalStats_header]
    print time_frame

    pass


# testApply()
# testNoDataDeplay()


# checker = DbInstrumentChecker("100", "HK", 20191128, "check_db_instrument.result")
# checker.get_check_notify_persist()


def testAccuracy():
    data = pd.read_csv("D:\project\Genus\GenusOwn\Rjob\Rjob_Python\output\GenusHistIntervalStats20191125.csv", names=ConfigChina.GenusHistIntervalStats_header, encoding="utf-8", engine='c')
    data = data.round({ConfigChina.header_TradeSize: 2, ConfigChina.header_TradeSizeSD: 2,
                       ConfigChina.header_BidSize: 2, ConfigChina.header_BidSizeSD: 2,
                       ConfigChina.header_AskSize: 2, ConfigChina.header_AskSizeSD: 2,
                       ConfigChina.header_SpreadSize: 2, ConfigChina.header_SpreadSizeSD: 2,
                       ConfigChina.header_Volume: 2, ConfigChina.header_VolumeSD: 2,
                       ConfigChina.header_VolumePercent: 2, ConfigChina.header_VolumePercentSD: 2,
                       ConfigChina.header_Volatility: 2, ConfigChina.header_VolatilitySD: 2,
                       ConfigChina.header_CCVolatility: 2, ConfigChina.header_CCVolatilitySD: 2,
                       })
    data.to_csv("D:\project\Genus\GenusOwn\Rjob\Rjob_Python\output\GenusHistIntervalStatsTest.csv", encoding="utf-8", index=False, header=False)

    print data

    pass

# testAccuracy()
# line="Cpu(s): 50.0%us,  9.1%sy,  0.0%ni,  9.1%id, 31.8%wa,  0.0%hi,  0.0%si,  0.0%st"
# ratio = line.split()[1]
# ratio = str(ratio[0: len(ratio) - 3]).strip()
# ratio=ratio+"%" if not ratio.endswith("%") else ratio
# print ratio
