package com.genus.ctp.mode;

import java.io.Serializable;

/**
 * 用户登录应答信息
 */
public class GenusCTPRspUserLoginField implements Serializable {
    ///交易日
    private String TradingDay;
    ///登录成功时间
    private String LoginTime;
    ///经纪公司代码
    private String BrokerID;
    ///用户代码
    private String UserID;
    ///交易系统名称
    private String SystemName;
    ///前置编号
    private int FrontID;
    ///会话编号
    private int SessionID;
    ///最大报单引用
    private String MaxOrderRef;
    ///上期所时间
    private String SHFETime;
    ///大商所时间
    private String DCETime;
    ///郑商所时间
    private String CZCETime;
    ///中金所时间
    private String FFEXTime;
    ///能源中心时间
    private String INETime;


    public String getTradingDay() {
        return TradingDay;
    }

    public String getLoginTime() {
        return LoginTime;
    }

    public String getBrokerID() {
        return BrokerID;
    }

    public String getUserID() {
        return UserID;
    }

    public String getSystemName() {
        return SystemName;
    }

    public int getFrontID() {
        return FrontID;
    }

    public int getSessionID() {
        return SessionID;
    }

    public String getMaxOrderRef() {
        return MaxOrderRef;
    }

    public String getSHFETime() {
        return SHFETime;
    }

    public String getDCETime() {
        return DCETime;
    }

    public String getCZCETime() {
        return CZCETime;
    }

    public String getFFEXTime() {
        return FFEXTime;
    }

    public String getINETime() {
        return INETime;
    }
}
