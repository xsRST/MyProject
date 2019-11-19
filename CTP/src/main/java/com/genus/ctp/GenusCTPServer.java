package com.genus.ctp;

import com.genus.ctp.callback.GenusCTPMarketDataCallback;
import com.genus.ctp.callback.GenusCTPTradeCallback;
import com.genus.ctp.mode.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.List;

public abstract class GenusCTPServer {
    private static Logger logger = LogManager.getLogger(GenusCTPServer.class);
    protected static boolean isValid = true;
    private GenusCTPTradeCallback tradeCallback;
    private GenusCTPMarketDataCallback marketDataCallback;
    private String tradeFontAddr;
    private String tradeBrokerId;
    private String investorId;
    private String password;
    private String appId;
    private String authCode;
    private String marketFontAddr;
    private String marketBrokerId;

    public GenusCTPServer() {
    }

    public GenusCTPServer(GenusCTPTradeCallback tradeCallback, GenusCTPMarketDataCallback marketDataCallback, String tradeFontAddr, String marketFontAddr) {
        this.tradeCallback = tradeCallback;
        this.marketDataCallback = marketDataCallback;
        this.tradeFontAddr = tradeFontAddr;
        this.marketFontAddr = marketFontAddr;

        this.tradeCallback.setCtpServer(this);
        this.marketDataCallback.setCtpServer(this);
    }


    public GenusCTPServer(GenusCTPTradeCallback tradeCallback, GenusCTPMarketDataCallback marketDataCallback, String tradeFontAddr, String tradeBrokerId, String investorId, String password, String appId, String authCode, String marketFontAddr, String marketBrokerId) {
        this.tradeCallback = tradeCallback;
        this.marketDataCallback = marketDataCallback;
        this.tradeFontAddr = tradeFontAddr;
        this.tradeBrokerId = tradeBrokerId;
        this.investorId = investorId;
        this.password = password;
        this.appId = appId;
        this.authCode = authCode;
        this.marketFontAddr = marketFontAddr;
        this.marketBrokerId = marketBrokerId;

        this.tradeCallback.setCtpServer(this);
        this.marketDataCallback.setCtpServer(this);
    }

    public void setField(GenusCTPTradeCallback tradeCallback, GenusCTPMarketDataCallback marketDataCallback, String tradeFontAddr, String marketFontAddr) {
        this.tradeCallback = tradeCallback;
        this.marketDataCallback = marketDataCallback;
        this.tradeFontAddr = tradeFontAddr;
        this.marketFontAddr = marketFontAddr;

        this.tradeCallback.setCtpServer(this);
        this.marketDataCallback.setCtpServer(this);
    }

    protected abstract void StartCTPMarketServer(GenusCTPMarketDataCallback marketDataCallback, String marketFontAddr);

    protected abstract void StartCTPTradeServer(GenusCTPTradeCallback tradeCallback, String tradeFontAddr);

    protected abstract void StopCTPServer();

    public void startCTPMarketServer() throws InterruptedException {
        if (this.marketFontAddr == null || this.marketFontAddr.length() > 0 == false) {
            logger.info("marketFontAddr is empty");
            return;
        }
        StartCTPMarketServer(this.marketDataCallback, this.marketFontAddr);
        Thread.sleep(4 * 1000);
    }

    public void startCTPTradeServer() throws InterruptedException {
        if (this.tradeFontAddr == null || this.tradeFontAddr.length() > 0 == false) {
            logger.info("tradeFontAddr is empty");
            return;
        }
        StartCTPTradeServer(this.tradeCallback, this.tradeFontAddr);
        Thread.sleep(3 * 1000);
    }

    public abstract String GetApiVersion();

    public abstract String GetTradingDay();

    public abstract int ReqTradeAuthenticate(GenusCTPReqAuthenticateField reqAuthenticateField, int nRequestID);

    public abstract int ReqMarketDataAuthenticate(GenusCTPReqAuthenticateField reqAuthenticateField, int nRequestID);

    public abstract int ReqTradeUserLogin(GenusCTPReqUserLoginField reqUserLoginField, int nRequestID);

    public abstract int ReqMarketDataUserLogin(GenusCTPReqUserLoginField reqUserLoginField, int nRequestID);

    public abstract int ReqTradeUserLogout(GenusCTPReqUserLogoutField reqUserLogoutField, int nRequestID);

    public abstract int ReqMarketDataUserLogout(GenusCTPReqUserLogoutField reqUserLogoutField, int nRequestID);

    public abstract int ReqQryInstrument(GenusCTPQryInstrumentField qryInstrumentField, int nRequestID);

    public abstract int ReqQryDepthMarketData(GenusCTPQryDepthMarketDataField qryDepthMarketDataField, int nRequestID);

    public abstract int SubscribeMarketData(List<String> instrumentIDs, int count);

    public abstract int UnSubscribeMarketData(List<String> instrumentIDs, int count);


    public String getTradeFontAddr() {
        return tradeFontAddr;
    }

    public String getTradeBrokerId() {
        return tradeBrokerId;
    }

    public String getPassword() {
        return password;
    }

    public String getAppId() {
        return appId;
    }

    public String getAuthCode() {
        return authCode;
    }

    public String getMarketFontAddr() {
        return marketFontAddr;
    }

    public String getMarketBrokerId() {
        return marketBrokerId;
    }


}
