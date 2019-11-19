package com.genus.ctp.mode;

import java.io.Serializable;

/**
 * 用户登录应答信息
 */
public class GenusCTPReqUserLoginField implements Serializable {
    ///交易日
    private String TradingDay;
    ///经纪公司代码
    private String BrokerID;
    ///用户代码
    private String UserID;
    ///密码
    private String Password;
    ///用户端产品信息
    private String UserProductInfo;
    ///接口端产品信息
    private String InterfaceProductInfo;
    ///协议信息
    private String ProtocolInfo;
    ///Mac地址
    private String MacAddress;
    ///动态密码
    private String OneTimePassword;
    ///终端IP地址
    private String ClientIPAddress;
    ///登录备注
    private String LoginRemark;
    ///终端IP端口
    private int ClientIPPort;

    public GenusCTPReqUserLoginField(String brokerID) {
        BrokerID = brokerID;
    }

    public GenusCTPReqUserLoginField(String brokerID, String userID, String password) {
        BrokerID = brokerID;
        UserID = userID;
        Password = password;
    }

    public GenusCTPReqUserLoginField(String tradingDay, String brokerID, String userID, String password) {
        TradingDay = tradingDay;
        BrokerID = brokerID;
        UserID = userID;
        Password = password;
    }

    public GenusCTPReqUserLoginField(String tradingDay, String brokerID, String userID, String password, String userProductInfo, String interfaceProductInfo, String protocolInfo, String macAddress, String oneTimePassword, String clientIPAddress, String loginRemark, int clientIPPort) {
        TradingDay = tradingDay;
        BrokerID = brokerID;
        UserID = userID;
        Password = password;
        UserProductInfo = userProductInfo;
        InterfaceProductInfo = interfaceProductInfo;
        ProtocolInfo = protocolInfo;
        MacAddress = macAddress;
        OneTimePassword = oneTimePassword;
        ClientIPAddress = clientIPAddress;
        LoginRemark = loginRemark;
        ClientIPPort = clientIPPort;
    }
}
