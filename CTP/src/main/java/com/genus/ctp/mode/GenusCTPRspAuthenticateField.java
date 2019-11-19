package com.genus.ctp.mode;

import java.io.Serializable;

/**
 * 用户登录应答信息
 */
public class GenusCTPRspAuthenticateField implements Serializable {
    ///经纪公司代码
    private String BrokerID;
    ///用户代码
    private String UserID;
    ///用户端产品信息
    private String UserProductInfo;
    ///App代码
    private String AppID;
    ///App类型
    private char AppType;


    public String getBrokerID() {
        return BrokerID;
    }

    public String getUserID() {
        return UserID;
    }

    public String getUserProductInfo() {
        return UserProductInfo;
    }

    public String getAppID() {
        return AppID;
    }

    public char getAppType() {
        return AppType;
    }
}
