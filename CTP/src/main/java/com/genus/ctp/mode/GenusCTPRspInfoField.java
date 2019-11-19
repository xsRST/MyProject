package com.genus.ctp.mode;

import java.io.Serializable;

public class GenusCTPRspInfoField implements Serializable {
    ///错误代码
    private int ErrorID;
    ///错误信息
    private String ErrorMsg;

    public int getErrorID() {
        return this.ErrorID;
    }

    public String getErrorMsg() {
        return this.ErrorMsg;
    }
}
