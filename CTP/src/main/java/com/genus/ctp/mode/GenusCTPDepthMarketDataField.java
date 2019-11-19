package com.genus.ctp.mode;

import java.io.Serializable;

public class GenusCTPDepthMarketDataField implements Serializable {

    ///交易日
    public String TradingDay;
    ///合约代码
    public String InstrumentID;
    ///交易所代码
    public String ExchangeID;
    ///合约在交易所的代码
    public String ExchangeInstID;
    ///最新价
    public double LastPrice;
    ///上次结算价
    public double PreSettlementPrice;
    ///昨收盘
    public double PreClosePrice;
    ///昨持仓量
    public double PreOpenInterest;
    ///今开盘
    public double OpenPrice;
    ///最高价
    public double HighestPrice;
    ///最低价
    public double LowestPrice;
    ///数量
    public long Volume;
    ///成交金额
    public double Turnover;
    ///持仓量
    public double OpenInterest;
    ///今收盘
    public double ClosePrice;
    ///本次结算价
    public double SettlementPrice;
    ///涨停板价
    public double UpperLimitPrice;
    ///跌停板价
    public double LowerLimitPrice;
    ///昨虚实度
    public double PreDelta;
    ///今虚实度
    public double CurrDelta;
    ///最后修改时间
    public String UpdateTime;
    ///最后修改毫秒
    public long UpdateMillisec;
    ///申买价一~五 ,
    public double BidPrice1;
    public double BidPrice2;
    public double BidPrice3;
    public double BidPrice4;
    public double BidPrice5;
    /// 申买量一~五
    public long BidVolume1;
    public long BidVolume2;
    public long BidVolume3;
    public long BidVolume4;
    public long BidVolume5;
    ///申卖价一~五
    public double AskPrice1;
    public double AskPrice2;
    public double AskPrice3;
    public double AskPrice4;
    public double AskPrice5;
    ///申卖量一~五
    public long AskVolume1;
    public long AskVolume2;
    public long AskVolume3;
    public long AskVolume4;
    public long AskVolume5;

    ///当日均价
    public double AveragePrice;
    ///业务日期
    public String ActionDay;

    public String getTradingDay() {
        return TradingDay;
    }

    public String getInstrumentID() {
        return InstrumentID;
    }

    public String getExchangeID() {
        return ExchangeID;
    }

    public String getExchangeInstID() {
        return ExchangeInstID;
    }

    public double getLastPrice() {
        return LastPrice;
    }

    public double getPreSettlementPrice() {
        return PreSettlementPrice;
    }

    public double getPreClosePrice() {
        return PreClosePrice;
    }

    public double getPreOpenInterest() {
        return PreOpenInterest;
    }

    public double getOpenPrice() {
        return OpenPrice;
    }

    public double getHighestPrice() {
        return HighestPrice;
    }

    public double getLowestPrice() {
        return LowestPrice;
    }

    public long getVolume() {
        return Volume;
    }

    public double getTurnover() {
        return Turnover;
    }

    public double getOpenInterest() {
        return OpenInterest;
    }

    public double getClosePrice() {
        return ClosePrice;
    }

    public double getSettlementPrice() {
        return SettlementPrice;
    }

    public double getUpperLimitPrice() {
        return UpperLimitPrice;
    }

    public double getLowerLimitPrice() {
        return LowerLimitPrice;
    }

    public double getPreDelta() {
        return PreDelta;
    }

    public double getCurrDelta() {
        return CurrDelta;
    }

    public String getUpdateTime() {
        return UpdateTime;
    }

    public long getUpdateMillisec() {
        return UpdateMillisec;
    }

    public double getBidPrice1() {
        return BidPrice1;
    }

    public double getBidPrice2() {
        return BidPrice2;
    }

    public double getBidPrice3() {
        return BidPrice3;
    }

    public double getBidPrice4() {
        return BidPrice4;
    }

    public double getBidPrice5() {
        return BidPrice5;
    }

    public long getBidVolume1() {
        return BidVolume1;
    }

    public long getBidVolume2() {
        return BidVolume2;
    }

    public long getBidVolume3() {
        return BidVolume3;
    }

    public long getBidVolume4() {
        return BidVolume4;
    }

    public long getBidVolume5() {
        return BidVolume5;
    }

    public double getAskPrice1() {
        return AskPrice1;
    }

    public double getAskPrice2() {
        return AskPrice2;
    }

    public double getAskPrice3() {
        return AskPrice3;
    }

    public double getAskPrice4() {
        return AskPrice4;
    }

    public double getAskPrice5() {
        return AskPrice5;
    }

    public long getAskVolume1() {
        return AskVolume1;
    }

    public long getAskVolume2() {
        return AskVolume2;
    }

    public long getAskVolume3() {
        return AskVolume3;
    }

    public long getAskVolume4() {
        return AskVolume4;
    }

    public long getAskVolume5() {
        return AskVolume5;
    }

    public double getAveragePrice() {
        return AveragePrice;
    }

    public String getActionDay() {
        return ActionDay;
    }
}
