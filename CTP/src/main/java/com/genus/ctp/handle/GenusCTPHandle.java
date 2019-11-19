package com.genus.ctp.handle;

import com.genus.ctp.GenusCTPConfig;
import com.genus.ctp.GenusCTPServer;
import com.genus.ctp.GenusCTPServerManager;
import com.genus.ctp.callback.GenusCTPMarketDataCallback;
import com.genus.ctp.callback.GenusCTPTradeCallback;
import com.genus.ctp.exception.CTPException;
import com.genus.ctp.impl.GenusCTPServerImpl;
import com.genus.ctp.mode.GenusCTPQryDepthMarketDataField;
import com.genus.ctp.mode.GenusCTPQryInstrumentField;
import com.genus.ctp.utils.Genus18Future;
import com.genus.ctp.utils.GenusCTPFileWriter;
import org.apache.commons.lang.StringUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.Arrays;

import static com.genus.ctp.GenusCTPConfig.*;

public class GenusCTPHandle {
    private static Logger logger = LogManager.getLogger(GenusCTPHandle.class);
    private GenusCTPServerManager manager = null;
    private static GenusCTPTradeCallback tradeCallback;

    private static GenusCTPMarketDataCallback marketDataCallback;
    private static GenusCTPServer ctpServer;

    public GenusCTPHandle(GenusCTPServerManager manager) {
        this.manager = manager;
        tradeCallback = new GenusCTPTradeCallback(manager);
        marketDataCallback = new GenusCTPMarketDataCallback(manager);
        ctpServer = new GenusCTPServerImpl(tradeCallback, marketDataCallback, tradeFontAddr, marketFontAddr);
        logger.info("设置版本信息 {} >>  实际CTP版本信息: {}", GenusCTPConfig.getCtpVersion(), ctpServer.GetApiVersion());
    }


    public void generatorAndSubscribe() throws Exception {
        ctpServer.startCTPTradeServer();
        ctpServer.startCTPMarketServer();
        if (marketDataCallback.isConnected() == false && tradeCallback.isConnected() == false) {
            throw new CTPException("Trade 和 Market Data 全部连接失败, 请检查 Front,BrokerID");
        }

        generatorStatic();
        subscribeDataFromInstrumentTxt();
    }

    public void subscribeOnly() throws Exception {
        ctpServer.startCTPMarketServer();
        if (marketDataCallback.isConnected() == false) {
            throw new CTPException(" Market Data 连接失败, 请检查 Front,BrokerID");
        }
        subscribeDataFromInstrumentTxt();
    }

    public static void generatorStatic() throws Exception {
        if (tradeCallback.isAction() == false) {
            logger.info("交易 Api 登录或验证失败, 生成instrument.txt  文件, 并进行订阅 >> {} ", getInstrumentTxtFile().getAbsolutePath());
            Genus18Future future = new Genus18Future();
            int result = future.startWriter18Future();
            if (result != 0) {
                throw new CTPException("生成数据失败, 退出程序");
            }
        }
        if (tradeCallback.isAction() == true) {
            logger.info("期货交易日: {}", ctpServer.GetTradingDay());
            GenusCTPQryInstrumentField qryInstrumentField = new GenusCTPQryInstrumentField();
            int result = ctpServer.ReqQryInstrument(qryInstrumentField, ++tradeRequestID);
            logger.info("请求查询合约代码 :{} ", result == 0 ? "Success" : "Failed");
            while (true) {
                if (tradeCallback.isReceiveLast()) {
                    GenusCTPQryDepthMarketDataField qryDepthMarketDataField = new GenusCTPQryDepthMarketDataField();
                    result = ctpServer.ReqQryDepthMarketData(qryDepthMarketDataField, ++tradeRequestID);
                    logger.info("请求查询合约代码行情 :{} ", result == 0 ? "Success" : "Failed");
                    break;
                } else {
                    Thread.sleep(10 * 1000);
                    logger.info("等待合约代码查询完成");
                }
            }
        }

        while (GenusCTPFileWriter.writeStaticFileEnd == false) {
            Thread.sleep(4 * 1000);
            logger.info("等待静态静态数据文件写入完成 ...");
        }

    }

    private static void subscribeDataFromInstrumentTxt() throws Exception {
        logger.info("开始订阅期货行情... ");
        if (getInstrumentTxtFile().exists() == false || getInstrumentTxtFile().isFile() == false) {
            throw new CTPException("instrument.txt  不存在 或不是文件, 无法订阅行情, >> :" + getInstrumentTxtFile().getAbsolutePath());
        }
        logger.info("正在从 {} 文件中获取 合约代码", getInstrumentTxtFile().getAbsolutePath());
        BufferedReader fileReader = new BufferedReader(new FileReader(getInstrumentTxtFile()));
        String lineStr = fileReader.readLine();
        if (lineStr.split("=").length == 2 && StringUtils.isNotEmpty(lineStr.split("=")[1])) {
            String instrumentStr = lineStr.split("=")[1];
            String[] instrumentIds = instrumentStr.split(",");
            int result = ctpServer.SubscribeMarketData(Arrays.asList(instrumentIds), instrumentIds.length);
            logger.info("订阅行情:{} :{} \n{} ", result == 0 ? "成功" : "失败", instrumentIds.length, instrumentStr);
            if (result != 0) {
                throw new CTPException("订阅行情失败 >> :" + lineStr);
            }
        } else {
            throw new CTPException("instrumentList  缺少值:" + lineStr);
        }
    }


}
