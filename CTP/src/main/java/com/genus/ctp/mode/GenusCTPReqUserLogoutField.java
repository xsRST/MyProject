package com.genus.ctp.mode;

import java.io.Serializable;

/**
 * 用户登录应答信息
 */
public class GenusCTPReqUserLogoutField implements Serializable {
    ///经纪公司代码
    private String BrokerID;
    ///用户代码
    private String UserID;

    public GenusCTPReqUserLogoutField(String brokerID, String userID) {
        BrokerID = brokerID;
        UserID = userID;
    }
}
