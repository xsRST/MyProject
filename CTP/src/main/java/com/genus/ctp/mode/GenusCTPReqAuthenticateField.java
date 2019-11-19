package com.genus.ctp.mode;

import java.io.Serializable;

/**
 * 用户登录应答信息
 */
public class GenusCTPReqAuthenticateField implements Serializable {
    ///经纪公司代码
    private String BrokerID;
    ///用户代码
    private String UserID;
    ///用户端产品信息
    private String UserProductInfo;
    ///认证码
    private String AuthCode;
    ///App代码
    private String AppID;

    public GenusCTPReqAuthenticateField(String brokerID, String userID, String appID, String authCode) {
        this.BrokerID = brokerID;
        this.UserID = userID;
        this.AppID = appID;
        this.AuthCode = authCode;
    }

    public GenusCTPReqAuthenticateField(String brokerID, String userID, String userProductInfo, String authCode, String appID) {
        this.BrokerID = brokerID;
        this.UserID = userID;
        this.UserProductInfo = userProductInfo;
        this.AuthCode = authCode;
        this.AppID = appID;
    }
}
