# coding=utf-8
import os
import sys
from multiprocessing import cpu_count

import pandas as pd

# 文件路径;
defaultConfigDirectory = os.path.join(sys.path[0], "conf")
defaultDataDirectory = os.path.join(sys.path[0], "output")
defaultTickFileDirectory = os.path.join(sys.path[0], "../input")
defaultLogDirectory = os.path.join(sys.path[0], "log")

defaultTickFileDirectory = "D:\\tickdata"

# 最大处理线程数, 默认 cpu核数*5
maxThreadsTotal = (cpu_count() or 1) * 10
# tickFileSuffix = ".tick.data.HK"

tickFileSuffix = ".tick.data"

# 股票处理间隔时间
interval = 5
# 历史数据天数
defaultMaxBDtoUse = 24

# 是否按交易所生成文件
discriminateExchange = False

InstrumentRepoType = "Repo"
InstrumentEquityType = "Equity"
InstrumentBondType = "Bond"
# 交易所
Exchange = ['SS','SZ']
# Exchange = ['HK']
# 股票类型
InstrumentTypeList = [InstrumentEquityType, InstrumentRepoType]
print(InstrumentTypeList)

MDLevel = os.getenv("MDLevel") if os.getenv("MDLevel") else "L1"
if (MDLevel.strip() == "L2"):
    defaultTickFileDirectory = os.path.join(sys.path[0], "input" + os.path.sep + "tickdata_L2")

print("MDLevel={} ".format(MDLevel))

if not os.path.exists(defaultConfigDirectory):
    print("Conf File Path is not Exist:{0}".format(defaultConfigDirectory))
    os._exit(0)
    pass
if not os.path.exists(defaultDataDirectory):
    os.mkdir(defaultDataDirectory)
    pass
if not os.path.exists(defaultTickFileDirectory):
    os.mkdir(defaultTickFileDirectory)
    pass
if not os.path.exists(defaultLogDirectory):
    os.mkdir(defaultLogDirectory)
    pass

print("Using the conf file under dir {}".format(defaultConfigDirectory))
print("Using the output file under dir {}".format(defaultDataDirectory))
print("Using the tick file under dir {}".format(defaultTickFileDirectory))

# --------instrument config-------
instrument_header_Symbol = "Symbol"
instrument_header_Exchange = "Exchange"
instrument_header_InstrumentType = "InstrumentType"
instrument_header = [instrument_header_Symbol, instrument_header_Exchange, instrument_header_InstrumentType]

# -------tick config --------
tick_data_header_time = "time"
tick_data_header_symbol = "symbol"
tick_data_header_trdprice = "trdprice"
tick_data_header_trdvol = "trdvol"
tick_data_header_acvol = "acvol"
tick_data_header_bidsize = "bidsize"
tick_data_header_asksize = "asksize"
tick_data_header_bidprice = "bidprice"
tick_data_header_askprice = "askprice"
tick_data_header = [tick_data_header_time, tick_data_header_symbol, tick_data_header_trdprice, tick_data_header_trdvol,
                    tick_data_header_acvol,
                    tick_data_header_bidsize, tick_data_header_asksize, tick_data_header_bidprice,
                    tick_data_header_askprice]

tickdata = pd.DataFrame(columns=tick_data_header)
# -------header config ----------

# ---------Indicator and IntervalStats header -----------------
header_TheDate = "TheDate"
header_IntervalID = "IntervalID"
header_Symbol = "Symbol"
header_StartTime = "StartTime"
header_EndTime = "EndTime"
header_BidSize = "BidSize"
header_BidSizeSD = "BidSizeSD"
header_AskSize = "AskSize"
header_AskSizeSD = "AskSizeSD"
header_SpreadSize = "SpreadSize"
header_SpreadSizeSD = "SpreadSizeSD"
header_isTradable = "isTradable"
header_isAuction = "isAuction"

header_TradeSize = "TradeSize"
header_TradeSizeSD = "TradeSizeSD"
header_Volume = "Volume"
header_VolumeSD = "VolumeSD"
header_VolumePercent = "VolumePercent"
header_VolumePercentSD = "VolumePercentSD"
header_FirstPrintTime = "FirstPrintTime"
header_ADV = "ADV"

header_Volatility = "Volatility"
header_VolatilitySD = "VolatilitySD"
header_CCVolatility = "CCVolatility"
header_CCVolatilitySD = "CCVolatilitySD"

# ---------InstrumentProfile header ---------------
header_AvgSpread = "AvgSpread"
header_BTR = "BTR"
header_AvgVolatility = "AvgVolatility"
header_HasValidCurve = "HasValidCurve"

# ----------------static header ---------------------------
time_start_end_header = [header_StartTime, header_EndTime]

symbol_start_end_header = [header_Symbol] + time_start_end_header

ac_volume_header = [header_Symbol, header_ADV]

RawIntervalStatsHeader = symbol_start_end_header + [header_TradeSize, header_BidSize, header_AskSize,
                                                    header_SpreadSize, header_Volume, header_VolumePercent,
                                                    header_Volatility, header_CCVolatility, header_isTradable, header_isAuction]

GenusHistIntervalStats_header = symbol_start_end_header + [header_TradeSize, header_TradeSizeSD, header_BidSize,
                                                           header_BidSizeSD, header_AskSize, header_AskSizeSD,
                                                           header_SpreadSize, header_SpreadSizeSD, header_Volume,
                                                           header_VolumeSD, header_VolumePercent,
                                                           header_VolumePercentSD,
                                                           header_Volatility, header_VolatilitySD, header_CCVolatility,
                                                           header_CCVolatilitySD]
GenusInstrumentProfile_header = [header_Symbol, header_AvgSpread, header_AvgVolatility, header_ADV, header_BTR,
                                 header_HasValidCurve]

format_4 = lambda x: "%.4f" % x
format_2 = lambda x: "%.2f" % x
format = lambda x: "%d" % x

defaultformat = format_4
