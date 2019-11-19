package com.genus.ctp.mode;

import java.io.Serializable;

public class GenusCTPQryDepthMarketDataField implements Serializable {
    ///合约代码
    private String InstrumentID;
    ///交易所代码
    private String ExchangeID;


    public GenusCTPQryDepthMarketDataField() {
    }

    public GenusCTPQryDepthMarketDataField(String instrumentID, String exchangeID) {
        InstrumentID = instrumentID;
        ExchangeID = exchangeID;
    }
}
