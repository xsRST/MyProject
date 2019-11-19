package com.genus.ctp.mode;

import java.io.Serializable;

public class GenusCTPQryInstrumentField implements Serializable {
    ///合约代码
    private String InstrumentID;
    ///交易所代码
    private String ExchangeID;
    ///合约在交易所的代码
    private String ExchangeInstID;
    ///产品代码
    private String ProductID;

    public GenusCTPQryInstrumentField() {
    }

    public GenusCTPQryInstrumentField(String instrumentID, String exchangeID, String exchangeInstID, String productID) {
        InstrumentID = instrumentID;
        ExchangeID = exchangeID;
        ExchangeInstID = exchangeInstID;
        ProductID = productID;
    }
}
