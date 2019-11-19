package com.genus.ctp.callback;

import com.genus.ctp.GenusCTPCallBack;
import com.genus.ctp.GenusCTPServerManager;
import com.genus.ctp.mode.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import static com.genus.ctp.GenusCTPConfig.*;

public class GenusCTPTradeCallback extends GenusCTPCallBack {
    protected static Logger logger = LogManager.getLogger(GenusCTPTradeCallback.class);


    protected boolean receiveLast = false;

    public GenusCTPTradeCallback(GenusCTPServerManager manager) {
        super(manager);
    }


    public boolean isReceiveLast() {
        return receiveLast;
    }

    protected void OnRspUserLogin(GenusCTPRspUserLoginField rspUserLoginField, GenusCTPRspInfoField rspInfoField, int nRequestID, boolean bIsLast) {
        super.OnRspUserLogin(rspUserLoginField, rspInfoField, nRequestID, bIsLast);
        logger.info("登录交易 API:{}, {} >> {}", rspInfoField.getErrorID() == 0 ? "成功" : "失败", rspInfoField.getErrorID(), rspInfoField.getErrorMsg());
    }

    @Override
    protected void OnFrontConnected() {
        isConnected = true;
        logger.info("交易 Api 连接成功 开始进行验证...");
        GenusCTPReqAuthenticateField authenticateField = new GenusCTPReqAuthenticateField(tradeBrokerId, investorId,
                appId, authCode);
        int result = ctpServer.ReqTradeAuthenticate(authenticateField, ++tradeRequestID);
        logger.info("请求客户端认证:{},tradeBrokerId={},investorId={}.appId={},authCode={}", result == 0 ? "成功" : "失败",
                tradeBrokerId, investorId, appId, authCode);
    }

    protected void OnRspAuthenticate(GenusCTPRspAuthenticateField rspAuthenticateField, GenusCTPRspInfoField rspInfoField, int nRequestID, boolean bIsLast) {
        logger.info("交易 Api 验证:{}, {}>> {}", rspInfoField.getErrorID() == 0 && "正确".equals(rspInfoField.getErrorMsg()) ? "成功" : "失败",
                rspInfoField.getErrorID(), rspInfoField.getErrorMsg());
        if (rspInfoField.getErrorID() == 0 && "正确".equals(rspInfoField.getErrorMsg())) {
            GenusCTPReqUserLoginField userLoginField = new GenusCTPReqUserLoginField(tradeBrokerId, investorId, password);
            int result = ctpServer.ReqTradeUserLogin(userLoginField, ++tradeRequestID);
            logger.info("请求登录交易 Api:{}, marketBrokerId={} ", result == 0 ? "成功" : "失败", marketBrokerId);
        }
    }

    @Override
    protected void OnRspUserLogout(GenusCTPRspUserLogoutField rspUserLogoutField, GenusCTPRspInfoField rspInfoField, int nRequestID, boolean bIsLast) {
        super.OnRspUserLogout(rspUserLogoutField, rspInfoField, nRequestID, bIsLast);

    }

    ///请求查询合约响应
    protected void OnRspQryInstrument(GenusCTPInstrumentField instrumentField, GenusCTPRspInfoField rspUserLoginField, int RequestID, boolean bIsLast) {
        manager.OnRspQryInstrument(instrumentField, rspUserLoginField, bIsLast);
        if (bIsLast == true) {
            receiveLast = true;
        }

    }

    ///请求查询行情响应
    protected void OnRspQryDepthMarketData(GenusCTPDepthMarketDataField depthMarketDataField, GenusCTPRspInfoField rspUserLoginField, int RequestID, boolean bIsLast) {
        manager.OnRspQryDepthMarketData(depthMarketDataField, rspUserLoginField, bIsLast);

    }


}
