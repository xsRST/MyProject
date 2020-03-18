package com.genus.ctp;

import com.genus.ctp.mode.GenusCTPRspInfoField;
import com.genus.ctp.mode.GenusCTPRspUserLoginField;
import com.genus.ctp.mode.GenusCTPRspUserLogoutField;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public abstract class GenusCTPCallBack {
    protected static Logger logger = LogManager.getLogger(GenusCTPCallBack.class);
    protected boolean isConnected = false;
    protected boolean isAction = false;
    protected GenusCTPServerManager manager = null;

    protected GenusCTPServer ctpServer = null;

    public GenusCTPCallBack() {
    }

    public GenusCTPCallBack(GenusCTPServerManager manager) {
        this.manager = manager;
    }

    public void setCtpServer(GenusCTPServer ctpServer) {
        this.ctpServer = ctpServer;
    }

    public boolean isAction() {
        return isAction;
    }

    public boolean isConnected() {
        return isConnected;
    }
    /**
     * 当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
     */
    protected void OnFrontConnected() {
        isConnected = true;

    }

    /**
     * ///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
     *
     * @param nReason 错误原因
     *                ///        0x1001 网络读失败
     *                ///        0x1002 网络写失败
     *                ///        0x2001 接收心跳超时
     *                ///        0x2002 发送心跳失败
     *                ///        0x2003 收到错误报文
     */
    protected void OnFrontDisconnected(int nReason) {
        isConnected = false;
        logger.info("OnFrontDisconnected: 0x{}", Integer.toHexString(nReason));
    }

    /**
     * ///心跳超时警告。当长时间未收到报文时，该方法被调用。
     *
     * @param nTimeLapse 距离上次接收报文的时间
     */
    protected void OnHeartBeatWarning(int nTimeLapse) {
        logger.info("OnHeartBeatWarning :{}", nTimeLapse);
    }

    /**
     * 登录请求响应
     *
     * @param rspUserLoginField
     * @param rspInfoField
     * @param nRequestID
     * @param bIsLast
     */
    protected void OnRspUserLogin(GenusCTPRspUserLoginField rspUserLoginField, GenusCTPRspInfoField rspInfoField, int nRequestID, boolean bIsLast) {
        if (rspInfoField.getErrorID() == 0) {
            isAction = true;
        } else {
            isAction = false;
        }


    }

    /**
     * 登出请求响应
     *
     * @param rspUserLogoutField
     * @param rspInfoField
     * @param nRequestID
     * @param bIsLast
     */
    protected void OnRspUserLogout(GenusCTPRspUserLogoutField rspUserLogoutField, GenusCTPRspInfoField rspInfoField, int nRequestID, boolean bIsLast) {
        logger.info("OnRspUserLogout");
    }

    /**
     * 错误应答
     *
     * @param rspInfoField
     * @param nRequestID
     * @param bIsLast
     */
    void OnRspError(GenusCTPRspInfoField rspInfoField, int nRequestID, boolean bIsLast) {
        logger.info("OnRspError: {} >>{} ", rspInfoField.getErrorID(), rspInfoField.getErrorMsg());
    }


}
