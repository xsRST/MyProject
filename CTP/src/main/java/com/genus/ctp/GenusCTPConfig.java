package com.genus.ctp;

import com.genus.ctp.option.GenusCTPOption;
import com.genus.ctp.utils.TimeUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.util.*;

import static com.genus.ctp.ApplicationContext.getCnfDirectory;
import static com.genus.ctp.ApplicationContext.getProperty;


public class GenusCTPConfig {
    protected static Logger logger = LogManager.getLogger(GenusCTPConfig.class);
    private static final String PROPERTY_NAME_Version = "Version";
    private static final String PROPERTY_NAME_TRADEFONTADDR = "TradeFontAddr";
    private static final String PROPERTY_NAME_TRADEBROKERID = "TradeBrokerId";
    private static final String PROPERTY_NAME_INVESTORID = "InvestorId";
    private static final String PROPERTY_NAME_PASSWORD = "Password";
    private static final String PROPERTY_NAME_APPID = "AppId";
    private static final String PROPERTY_NAME_AUTHCODE = "AuthCode";
    private static final String PROPERTY_NAME_MARKETFONTADDR = "MarketFontAddr";
    private static final String PROPERTY_NAME_MARKETBROKERID = "MarketBrokerId";
    private static final String PROPERTY_NAME_TRADERCORRESPONEDEXCHANGEID = "TraderCorrespondedExchangeID";
    private static final String PROPERTY_NAME_PRODUCTCLASSTYPE = "ProductClassType";

    private static final String PROPERTY_NAME_MODE = "Mode";
    private static final String PROPERTY_NAME_ENDTIME = "EndTime";
    public static final String INSTRUMENT_TXT_NAME = "instrument.txt";
    public static String marketDataFileName = "ctp." + TimeUtils.TODAY();
    public static String traderCorrespondedExchangeID = "SHFE:SSC;DCE:DLC;CZCE:ZZC;CFFEX:I-CF,T-CF2;INE:SE";
    public static String endTime = "15:30:00";
    public static List<String> productClassTypeList = new ArrayList();

    public static GenusCTPOption.Mode mode = GenusCTPOption.Mode.Normal;
    private static String ctpVersion = null;
    public static String baseDataFileName = "commodityfuture_basedata.csv";
    public static String baseMarketDataFileName = "commodityfuture_marketdata.csv";

    public static int marketDataRequestID = 0;
    public static int tradeRequestID = 0;

    public static String tradeFontAddr;
    public static String tradeBrokerId;
    public static String investorId;
    public static String password;
    public static String appId;
    public static String authCode;
    public static String marketFontAddr;
    public static String marketBrokerId;
    public static Map<String, String> filterExchangeMap = new HashMap<>();



    public static void init() throws Exception {
        fillCTPConfig();
    }


    private static void fillCTPConfig() throws Exception {
        tradeFontAddr = getProperty(PROPERTY_NAME_TRADEFONTADDR);
        tradeBrokerId = getProperty(PROPERTY_NAME_TRADEBROKERID);
        investorId = getProperty(PROPERTY_NAME_INVESTORID);
        password = getProperty(PROPERTY_NAME_PASSWORD);
        appId = getProperty(PROPERTY_NAME_APPID);
        authCode = getProperty(PROPERTY_NAME_AUTHCODE);
        marketFontAddr = getProperty(PROPERTY_NAME_MARKETFONTADDR);
        marketBrokerId = getProperty(PROPERTY_NAME_MARKETBROKERID);

        ctpVersion = getProperty(PROPERTY_NAME_Version);
        if (StringUtils.isNotEmpty(ctpVersion) == false) {
            throw new Exception("please Config Version: " + ctpVersion);
        }

        if (StringUtils.isNotEmpty(getProperty(PROPERTY_NAME_TRADERCORRESPONEDEXCHANGEID))) {
            traderCorrespondedExchangeID = getProperty(PROPERTY_NAME_TRADERCORRESPONEDEXCHANGEID);
        }
        logger.info("{} >> {}", PROPERTY_NAME_TRADERCORRESPONEDEXCHANGEID, traderCorrespondedExchangeID);
        for (String exchangeStr : traderCorrespondedExchangeID.split(";")) {
            String[] exchange2 = exchangeStr.split(":");
            if (exchange2.length == 2) {
                filterExchangeMap.put(exchange2[0], exchange2[1]);
            } else {
                logger.error("Parse Exchange Failed: {}", exchangeStr);
            }
        }
        String modeStr = getProperty(PROPERTY_NAME_MODE);
        if (StringUtils.isNotEmpty(modeStr) && null != GenusCTPOption.Mode.getOptionValue(modeStr)) {
            mode = GenusCTPOption.Mode.getOptionValue(modeStr);
        } else if (StringUtils.isNotEmpty(modeStr)) {
            logger.error("模式没有设置正确  >> {}", modeStr);
        }
        logger.info("{} >> {}", PROPERTY_NAME_MODE, mode.getTheValue());
        if (StringUtils.isNotEmpty(getProperty(PROPERTY_NAME_ENDTIME)) == true) {
            endTime = getProperty(PROPERTY_NAME_ENDTIME);
        }
        logger.info("{} >> {}", PROPERTY_NAME_ENDTIME, endTime);
        String productTypeStr = GenusCTPOption.ProductClassType.THOST_FTDC_PC_Futures.getTheValue();
        if (StringUtils.isNotEmpty(getProperty(PROPERTY_NAME_PRODUCTCLASSTYPE))) {
            productTypeStr = getProperty(PROPERTY_NAME_PRODUCTCLASSTYPE);
        }
        productClassTypeList.addAll(Arrays.asList(productTypeStr.split(",")));

        logger.info("{} >> {}", PROPERTY_NAME_PRODUCTCLASSTYPE, productTypeStr);
    }

    public static String parseExchangeID(String exchangeID) {
        if (StringUtils.isNotEmpty(exchangeID) == false) {
            return null;
        }
        return filterExchangeMap.get(exchangeID);
    }


    public static String getCtpVersion() {
        return ctpVersion;
    }


    public static File getInstrumentTxtFile() {
        return new File(getCnfDirectory().getAbsoluteFile() + File.separator + INSTRUMENT_TXT_NAME);
    }

}
