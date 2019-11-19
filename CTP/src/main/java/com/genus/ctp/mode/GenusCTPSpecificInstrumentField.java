package com.genus.ctp.mode;

import java.io.Serializable;

public class GenusCTPSpecificInstrumentField implements Serializable {
    ///合约代码
    public String InstrumentID;

    public void setInstrumentID(String instrumentID) {
        InstrumentID = instrumentID;
    }
}
