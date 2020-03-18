package com.genus.ctp;

import com.genus.ctp.handle.GenusCTPHandle;
import com.genus.ctp.mode.GenusCTPDepthMarketDataField;
import com.genus.ctp.mode.GenusCTPInstrumentField;
import com.genus.ctp.mode.GenusCTPRspInfoField;
import com.genus.ctp.option.GenusCTPOption;
import com.genus.ctp.utils.GenusCTPFileUtil;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Pattern;

import static com.genus.ctp.GenusCTPConfig.*;


public class GenusCTPServerManager {
    private static Logger logger = LogManager.getLogger(GenusCTPServerManager.class);
    private static GenusCTPHandle handle;
    public static Map<String, GenusCTPInstrumentField> ctpStaticMap = new TreeMap<>();
    protected static Map<String, GenusCTPDepthMarketDataField> ctpDepthMDMap = new TreeMap<>();
    private static Pattern p = Pattern.compile("([A-Za-z]+)(\\d+)");
    protected long receiveMdsCount = 0;
    protected long receiveStaticCount = 0;

    public void start() throws Exception {
        handle = new GenusCTPHandle(this);
        if (GenusCTPOption.Mode.Normal == mode) {
            handle.generatorAndSubscribe();
        } else if (GenusCTPOption.Mode.StaticOnly == mode) {
            handle.generatorStatic();
        } else if (GenusCTPOption.Mode.SubscribeOnly == mode) {
            ctpStaticMap = GenusCTPFileUtil.retrieveStaticFromFile();
            handle.subscribeOnly();
        }
    }

    public void OnRspQryDepthMarketData(GenusCTPDepthMarketDataField depthMarketDataField, GenusCTPRspInfoField rspUserLoginField, boolean bIsLast) {
        if (null != depthMarketDataField) {
            String instrumentID = depthMarketDataField.getInstrumentID();
            String exchangeInstID = depthMarketDataField.getExchangeInstID();
            String exchangeID = depthMarketDataField.getExchangeID();
            if (ctpStaticMap.containsKey(instrumentID)) {
                if (ctpDepthMDMap.containsKey(instrumentID) == true) {
                    logger.info("[{}]合约信息已存在,更新数据 ;  ", exchangeInstID);
                }
                ctpDepthMDMap.put(instrumentID, depthMarketDataField);
            }
            receiveMdsCount++;
        }
        if (bIsLast == true) {
            logger.info("接收合约行情数量={} ,实际写入={}", receiveMdsCount, ctpDepthMDMap.size());
            GenusCTPFileUtil.writeTradeData2File(ctpStaticMap, ctpDepthMDMap);
        }
    }

    public void OnRspQryInstrument(GenusCTPInstrumentField instrumentField, GenusCTPRspInfoField rspUserLoginField, boolean bIsLast) {
        if (null != instrumentField) {
            String instrumentID = instrumentField.getInstrumentID();
            String exchangeID = instrumentField.getExchangeID();
            GenusCTPOption.ProductClassType optionsType = GenusCTPOption.ProductClassType.getOption(instrumentField.getProductClass());
            if (filterExchangeMap.containsKey(exchangeID) == true && productClassTypeList.contains(optionsType.getTheValue())) {
                if (ctpStaticMap.containsKey(instrumentID) == true) {
                    logger.info("[{}]合约代码已存在,更新数据;  ", instrumentID);
                }
                ctpStaticMap.put(instrumentID, instrumentField);
            }
            receiveStaticCount++;
        }
        if (bIsLast == true) {
            logger.info("接收到的合约代码数量 ={}, 实际写入数量={}", receiveStaticCount, ctpStaticMap.size());
        }
    }
}
