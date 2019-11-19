package com.genus.ctp.impl;

import com.genus.ctp.ApplicationContext;
import com.genus.ctp.GenusCTPConfig;
import com.genus.ctp.GenusCTPServer;
import com.genus.ctp.callback.GenusCTPMarketDataCallback;
import com.genus.ctp.callback.GenusCTPTradeCallback;
import com.genus.ctp.exception.CTPException;
import com.genus.ctp.mode.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.util.List;

public class GenusCTPServerImpl extends GenusCTPServer {
    private static Logger logger = LogManager.getLogger(GenusCTPServerImpl.class);
    private static final String ServerVersion = GenusCTPConfig.getCtpVersion();

    static {
        File libPath = new File(ApplicationContext.getVersionDirectory() + File.separator + ServerVersion);
        File mduserpi_seFile = new File(libPath.getAbsolutePath() + File.separator + "thostmduserapi_se.dll");
        File traderapi_seFile = new File(libPath.getAbsolutePath() + File.separator + "thosttraderapi_se.dll");
        File ctpServerFile = new File(libPath.getAbsolutePath() + File.separator + "GenusCTPServer" + ServerVersion + ".dll");
        if (libPath.exists() == false || libPath.isDirectory() == false) {
            isValid = false;
            logger.error("文件夹不存在, 请联系相关人员... >> {}", libPath.getAbsolutePath());
            throw new CTPException(libPath.getAbsolutePath() + " >> 文件夹不存在, 请联系相关人员... ");
        } else if (mduserpi_seFile.exists() == false || mduserpi_seFile.isFile() == false
                || traderapi_seFile.exists() == false || traderapi_seFile.isFile() == false
                || ctpServerFile.exists() == false || ctpServerFile.isFile() == false) {
            isValid = false;
            throw new CTPException(" 读取dll文件失败, 请检查: : mduserpi_seFile=" + mduserpi_seFile.getAbsolutePath() + " ," +
                    "traderapi_seFile=" + traderapi_seFile.getAbsolutePath() + ",ctpServerFile=" + ctpServerFile.getAbsolutePath());
        } else {
            System.load(mduserpi_seFile.getAbsolutePath());
            System.load(traderapi_seFile.getAbsolutePath());
            System.load(ctpServerFile.getAbsolutePath());
            isValid = true;
        }

    }

    public GenusCTPServerImpl() {
    }

    public GenusCTPServerImpl(GenusCTPTradeCallback tradeCallback, GenusCTPMarketDataCallback marketDataCallback, String tradeFontAddr, String tradeBrokerId, String investorId, String password, String appId, String authCode, String marketFontAddr, String marketBrokerId) {
        super(tradeCallback, marketDataCallback, tradeFontAddr, tradeBrokerId, investorId, password, appId, authCode, marketFontAddr, marketBrokerId);
    }

    public GenusCTPServerImpl(GenusCTPTradeCallback tradeCallback, GenusCTPMarketDataCallback marketDataCallback, String tradeFontAddr, String marketFontAddr) {
        super(tradeCallback, marketDataCallback, tradeFontAddr, marketFontAddr);
    }

    @Override
    protected native void StartCTPTradeServer(GenusCTPTradeCallback tradeCallback, String tradeFontAddr);

    @Override
    protected native void StartCTPMarketServer(GenusCTPMarketDataCallback marketDataCallback, String marketFontAddr);

    @Override
    protected native void StopCTPServer();

    @Override
    public native String GetApiVersion();

    @Override
    public native String GetTradingDay();

    @Override
    public native int ReqTradeAuthenticate(GenusCTPReqAuthenticateField reqAuthenticateField, int nRequestID);

    @Override
    public native int ReqMarketDataAuthenticate(GenusCTPReqAuthenticateField reqAuthenticateField, int nRequestID);

    @Override
    public native int ReqTradeUserLogin(GenusCTPReqUserLoginField reqUserLoginField, int nRequestID);

    @Override
    public native int ReqMarketDataUserLogin(GenusCTPReqUserLoginField reqUserLoginField, int nRequestID);

    @Override
    public native int ReqTradeUserLogout(GenusCTPReqUserLogoutField reqUserLogoutField, int nRequestID);

    @Override
    public native int ReqMarketDataUserLogout(GenusCTPReqUserLogoutField reqUserLogoutField, int nRequestID);

    @Override
    public native int ReqQryInstrument(GenusCTPQryInstrumentField qryInstrumentField, int nRequestID);

    @Override
    public native int ReqQryDepthMarketData(GenusCTPQryDepthMarketDataField qryDepthMarketDataField, int nRequestID);

    @Override
    public native int SubscribeMarketData(List<String> instrumentIDs, int count);

    @Override
    public native int UnSubscribeMarketData(List<String> instrumentIDs, int count);

}
