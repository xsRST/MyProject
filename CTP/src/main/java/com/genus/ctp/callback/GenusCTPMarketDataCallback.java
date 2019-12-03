package com.genus.ctp.callback;

import com.genus.ctp.GenusCTPCallBack;
import com.genus.ctp.GenusCTPServerManager;
import com.genus.ctp.mode.*;
import com.genus.ctp.utils.GenusCTPFileWriter;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import static com.genus.ctp.GenusCTPConfig.marketBrokerId;
import static com.genus.ctp.GenusCTPConfig.marketDataRequestID;


public class GenusCTPMarketDataCallback extends GenusCTPCallBack {
    protected static Logger logger = LogManager.getLogger(GenusCTPMarketDataCallback.class);

    public GenusCTPMarketDataCallback(GenusCTPServerManager manager) {
        super(manager);
    }

    private Long receiveCount = 0L;
    protected void OnRspUserLogin(GenusCTPRspUserLoginField rspUserLoginField, GenusCTPRspInfoField rspInfoField, int nRequestID, boolean bIsLast) {
        super.OnRspUserLogin(rspUserLoginField, rspInfoField, nRequestID, bIsLast);
        logger.info("登录行情 Api:{}, {} >> {}", rspInfoField.getErrorID() == 0 ? "成功" : "失败", rspInfoField.getErrorID(), rspInfoField.getErrorMsg());
    }

    @Override
    protected void OnFrontConnected() {
        super.OnFrontConnected();
        logger.info("行情 Api 连接成功, 开始进行登陆...");
        GenusCTPReqUserLoginField userLoginField = new GenusCTPReqUserLoginField(marketBrokerId);
        int result = ctpServer.ReqMarketDataUserLogin(userLoginField, ++marketDataRequestID);
        logger.info("请求登录行情Api:{}  marketBrokerId={} ", result == 0 ? "成功" : "失败", marketBrokerId);
    }

    protected void OnRspSubMarketData(GenusCTPSpecificInstrumentField specificInstrumentField, GenusCTPRspInfoField rspInfoField, int nRequestID, boolean bIsLast) {
        if (nRequestID != 0) {
            logger.info("订阅失败 [{}]:{} >> {}", specificInstrumentField.InstrumentID, rspInfoField.getErrorID(), rspInfoField.getErrorMsg());
        }
    }

    protected void OnRtnDepthMarketData(GenusCTPDepthMarketDataField depthMarketDataField) {
        logger.debug("OnRtnDepthMarketData");
        if (receiveCount % 100000 == 0) {
            logger.info(depthMarketDataField.toString());
        }
        receiveCount++;
        GenusCTPFileWriter.writeMarketData2File(depthMarketDataField);
    }
}
