package com.genus.ctp.utils;

import com.genus.ctp.ApplicationContext;
import com.genus.ctp.GenusCTPServerManager;
import com.genus.ctp.mode.GenusCTPDepthMarketDataField;
import com.genus.ctp.mode.GenusCTPInstrumentField;
import org.apache.commons.lang.StringUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static com.genus.ctp.GenusCTPConfig.*;

public class GenusCTPFileUtil {
    protected static Logger logger = LogManager.getLogger(GenusCTPFileUtil.class);
    private static PrintStream marketDataPrintSream = null;
    public static boolean writeStaticFileEnd = false;
    public static String ignoreDateStr = "16:00:00:000";


    public static Map<String, GenusCTPInstrumentField> retrieveStaticFromFile() {
        Map<String, GenusCTPInstrumentField> ctpStaticMap = new TreeMap<>();
        File baseDataFile = new File(ApplicationContext.getBaseDataDirectory().getAbsolutePath() + File.separator + baseDataFileName);
        if (baseDataFile.exists() && baseDataFile.isFile()) {
            FileInputStream inputStream = null;
            try {
                String line;
                inputStream = new FileInputStream(baseDataFile);
                BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
                while ((line = reader.readLine()) != null) {
                    String[] split = line.split(",");
                    if (split.length < 25 == false) {
                        GenusCTPInstrumentField instrumentField = new GenusCTPInstrumentField();
                        instrumentField.InstrumentID = split[1];
                        instrumentField.ExchangeID = split[2];
                        instrumentField.ExchangeInstID = split[5];
                        ctpStaticMap.put(instrumentField.InstrumentID, instrumentField);
                    }
                }
            } catch (Exception e) {
                logger.error(e);
            }
        }
        return ctpStaticMap;
    }

    public static void writeTradeData2File(Map<String, GenusCTPInstrumentField> ctpStaticMap, Map<String, GenusCTPDepthMarketDataField> ctpDepthMDMap) {

        if (null != ctpStaticMap && ctpStaticMap.size() > 0 && null != ctpDepthMDMap && ctpDepthMDMap.size() > 0 &&
                StringUtils.isNotEmpty(baseDataFileName) && StringUtils.isNotEmpty(baseMarketDataFileName)) {
            PrintStream baseDataPrintStream = null;
            PrintStream baseMarketDataPrintStream = null;
            try {
                File baseDataFile = new File(ApplicationContext.getBaseDataDirectory().getAbsolutePath() + File.separator + baseDataFileName);
                File baseMarketDataFile = new File(ApplicationContext.getBaseDataDirectory().getAbsolutePath() + File.separator + baseMarketDataFileName);
                File instrumentTxtFile = getInstrumentTxtFile();
                if (baseDataFile.exists() && baseDataFile.isFile()) {
                    baseDataFile.delete();
                }
                if (baseMarketDataFile.exists() && baseMarketDataFile.isFile()) {
                    baseMarketDataFile.delete();
                }
                Set<String> subscribeInstrumentIDs = new HashSet<>();
                List<String> existsInstrument = new ArrayList<>();
                if (instrumentTxtFile.exists() == false || instrumentTxtFile.isFile() == false) {
                    instrumentTxtFile.createNewFile();
                } else {
                    BufferedReader fileReader = new BufferedReader(new FileReader(instrumentTxtFile));
                    String lineStr = fileReader.readLine();
                    if (lineStr.split("=").length == 2 && StringUtils.isNotEmpty(lineStr.split("=")[1])) {
                        String instrumentStr = lineStr.split("=")[1];
                        String[] instrumentIds = instrumentStr.split(",");
                        existsInstrument = (Arrays.asList(instrumentIds));
                    }
                }
                String minDate = TimeUtils.TODAY().substring(2, 6);
                Pattern p = Pattern.compile("([0-9]{3,4})");
                existsInstrument.forEach(instrumentIDStr -> {
                    try {
                        Matcher m = p.matcher(instrumentIDStr);
                        if (m.find()) {
                            String str = m.group(1);
                            String perfermanceDate = minDate;
                            if (str.length() == 3) {
                                if (str.startsWith("0") && Integer.parseInt(TimeUtils.TODAY().substring(3, 4)) == 9) {
                                    str = (Integer.parseInt(TimeUtils.TODAY().substring(2, 3)) + 1) + str;
                                } else {
                                    str = TimeUtils.TODAY().substring(2, 3) + str;
                                }
                            }
                            if (Integer.parseInt(str) >= Integer.parseInt(perfermanceDate)) {
                                subscribeInstrumentIDs.add(instrumentIDStr);
                            } else {
                                logger.info("过滤掉过期instrument.txt 中的合约代码: {};", instrumentIDStr);
                            }
                        }
                    } catch (NumberFormatException e) {
                        logger.error("", e);
                    }
                });
                logger.info("添加历史合约代码:{};\n{}", subscribeInstrumentIDs.size(), StringUtils.join(subscribeInstrumentIDs, ","));
                logger.info("添加新数据:{};\n{}", ctpStaticMap.size(), StringUtils.join(ctpStaticMap.keySet(), ","));
                subscribeInstrumentIDs.addAll(ctpStaticMap.keySet());
                StringBuffer instrumentIDs = new StringBuffer("instrumentList=");
                subscribeInstrumentIDs.forEach(str -> {
                    instrumentIDs.append(str).append(",");
                });
                instrumentIDs.substring(0, instrumentIDs.length() - 1);

                //String instrumentIDs = "instrumentList="+ StringUtils.join(subscribeInstrumentIDs, ",");
                FileOutputStream buf = new FileOutputStream(instrumentTxtFile, false);
                buf.write(instrumentIDs.toString().getBytes());
                buf.close();
                logger.info("生成instrumentList 数据: {} ", instrumentTxtFile.getAbsolutePath());

                baseDataPrintStream = new PrintStream(new FileOutputStream(baseDataFile, true), true);
                baseMarketDataPrintStream = new PrintStream(new FileOutputStream(baseMarketDataFile, true), true);
                for (Map.Entry<String, GenusCTPInstrumentField> entry : ctpStaticMap.entrySet()) {
                    String instrumentID = entry.getKey();
                    if (ctpDepthMDMap.containsKey(instrumentID)) {
                        GenusCTPInstrumentField instrumentField = entry.getValue();
                        String instrumentname = instrumentField.getInstrumentName();
                        String exchangeID = instrumentField.getExchangeID();
                        String exchange = parseCTPExchange(instrumentID, exchangeID);
                        if (StringUtils.isNotEmpty(exchange) == false) {
                            continue;
                        }
                        String symbol = instrumentID + "." + exchange;
                        int deliveryYear = instrumentField.getDeliveryYear();
                        int deliveryMonth = instrumentField.getDeliveryMonth();

                        long maxMarketOrderVolume = instrumentField.getMaxMarketOrderVolume();
                        long minMarketOrderVolume = instrumentField.getMinMarketOrderVolume();
                        long maxLimitOrderVolume = instrumentField.getMaxLimitOrderVolume();
                        long minLimitOrderVolume = instrumentField.getMinLimitOrderVolume();
                        long volumeMultiple = instrumentField.getVolumeMultiple();
                        double priceTick = instrumentField.getPriceTick();
                        String createDate = instrumentField.getCreateDate();
                        String openDate = instrumentField.getOpenDate();
                        String expireDate = instrumentField.getExpireDate();
                        String startDelivDate = instrumentField.getStartDelivDate();
                        String endDelivDate = instrumentField.getEndDelivDate();
                        char instLifePhase = instrumentField.getInstLifePhase();
                        int isTrading = instrumentField.isTrading() ? 1 : 0;
                        char positionType = instrumentField.getPositionType();
                        char positionDateType = instrumentField.getPositionDateType();
                        double longMarginRatio = instrumentField.getLongMarginRatio();
                        double shortMarginRatio = instrumentField.getShortMarginRatio();
                        char maxMarginSideAlgorithm = instrumentField.getMaxMarginSideAlgorithm();
                        String underlyingInstrID = instrumentField.getUnderlyingInstrID();
                        double strikePrice = instrumentField.getStrikePrice();
                        char optionsType = instrumentField.getOptionsType();
                        double underlyingMultiple = instrumentField.getUnderlyingMultiple();


                        StringBuffer baseDataSb = new StringBuffer();
                        baseDataSb.append(symbol).append(",").append(instrumentID).append(",").append(exchange).append(",").
                                append(instrumentname).append(",").append(exchangeID).append(",").append(symbol).append(",").append(exchangeID).append(",");
                        baseDataSb.append(deliveryYear).append(",").append(deliveryMonth).append(",");
                        baseDataSb.append(maxMarketOrderVolume).append(",").append(minMarketOrderVolume).append(",");
                        baseDataSb.append(maxLimitOrderVolume).append(",").append(minLimitOrderVolume).append(",");

                        baseDataSb.append(volumeMultiple).append(",");
                        baseDataSb.append((priceTick)).append(",");
                        baseDataSb.append(createDate).append(",").append(openDate).append(",").append(expireDate).append(",");
                        baseDataSb.append(startDelivDate).append(",").append(endDelivDate).append(",");
                        baseDataSb.append(instLifePhase).append(",").append(isTrading).append(",");
                        baseDataSb.append(positionType).append(",").append(positionDateType).append(",");
                        baseDataSb.append((longMarginRatio)).append(",").append(shortMarginRatio).append(",");
                        baseDataSb.append((maxMarginSideAlgorithm)).append(",");
                        baseDataSb.append(underlyingInstrID).append(",");
                        baseDataSb.append((strikePrice)).append(",");
                        baseDataSb.append(optionsType).append(",");
                        baseDataSb.append((underlyingMultiple));

                        GenusCTPDepthMarketDataField depthMarketDataField = ctpDepthMDMap.get(instrumentID);
                        double preSettlementPrice = depthMarketDataField.getPreSettlementPrice();
                        double upperLimitPrice = depthMarketDataField.getUpperLimitPrice();
                        double lowerLimitPrice = depthMarketDataField.getLowerLimitPrice();
                        double openPrice = depthMarketDataField.getOpenPrice();

                        StringBuffer marketDataSb = new StringBuffer();
                        marketDataSb.append(instrumentID).append(",");
                        marketDataSb.append((preSettlementPrice)).append(",");
                        marketDataSb.append((upperLimitPrice)).append(",");
                        marketDataSb.append((lowerLimitPrice)).append(",");
                        marketDataSb.append((openPrice));

                        baseDataPrintStream.println(baseDataSb.toString());
                        baseMarketDataPrintStream.println(marketDataSb.toString());
                    } else {
                        logger.info("过滤 {} : 原因: 没有对应行情数据", instrumentID);
                    }
                }
                logger.info("静态数据写入完成: 数量={}", ctpStaticMap.size());
                writeStaticFileEnd = true;

            } catch (Exception e) {
                logger.error("静态数据写入失败", e);
                writeStaticFileEnd = true;
            } finally {
                if (null != baseDataPrintStream) {
                    baseDataPrintStream.close();
                }
                if (null != baseMarketDataPrintStream) {
                    baseMarketDataPrintStream.close();
                }
            }


        }

    }

    private static String parseCTPExchange(String instrumentID, String exchangeID) {
        String exchange = parseExchangeID(exchangeID);
        if (StringUtils.isNotEmpty(exchange) == false) {
            return null;
        }
        if (exchange.split("-").length > 1) {
            for (String preExchange : exchange.split(",")) {
                String preInstrumentID = preExchange.split("-")[0];
                String realEx = preExchange.split("-")[1];
                if (instrumentID.startsWith(preInstrumentID)) {
                    return realEx;
                }
            }
            return null;
        }
        return exchange;
    }

    public static void writeMarketData2File(GenusCTPDepthMarketDataField depthMarketDataField) {

        try {
            if (marketDataPrintSream == null) {
                File baseDataFile = new File(ApplicationContext.getMarketDataDirectory().getAbsolutePath() + File.separator + marketDataFileName);
                marketDataPrintSream = new PrintStream(new FileOutputStream(baseDataFile, true), true);

                String header = "#UpdateTime|InstrumentID|ExchangeID|ExchangeInstID|LastPrice|PreSettlementPrice|PreClosePrice|PreOpenInterest|" +
                        "OpenPrice|HighestPrice|LowestPrice|Volume|Turnover|OpenInterest|ClosePrice|SettlementPrice|UpperLimitPrice|LowerLimitPrice|" +
                        "PreDelta|CurrDelta|BidPrice1|BidVolume1|AskPrice1|AskVolume1|AveragePrice|";
                marketDataPrintSream.println(header);
            }

            String updateTimeWithMill = depthMarketDataField.getUpdateTime() + ":" + StringUtils.rightPad(String.valueOf(depthMarketDataField.getUpdateMillisec()), 3, "0");


            //TODO 解析夜盘对应时间戳
            Date dataTime = TimeUtils.timeFormatWithMilliSeconds.get().parse(updateTimeWithMill);
            Date ignoreDate = TimeUtils.timeFormatWithMilliSeconds.get().parse(ignoreDateStr);
            if (dataTime.after(ignoreDate)) {
                return;
            }
            StringBuffer marketDataStr = new StringBuffer();
            String updateTime = TimeUtils.TODAY() + "." + updateTimeWithMill;

            String instrumentID = depthMarketDataField.getInstrumentID();
            String exchangeID = depthMarketDataField.getExchangeID();
            String exchangeInstID = depthMarketDataField.getExchangeInstID();
            if (GenusCTPServerManager.ctpStaticMap.containsKey(instrumentID)) {
                GenusCTPInstrumentField instrumentField = GenusCTPServerManager.ctpStaticMap.get(instrumentID);
                exchangeID = instrumentField.getExchangeID();
                exchangeInstID = instrumentField.getExchangeInstID();
            }
            String exchange = parseCTPExchange(instrumentID, exchangeID);
            marketDataStr.append(updateTime).append("|")
                    .append(instrumentID).append("|").append(exchange).append("|").append(exchangeInstID).append("|")
                    .append(depthMarketDataField.getLastPrice()).append("|").append(depthMarketDataField.getPreSettlementPrice()).append("|")
                    .append(depthMarketDataField.getPreClosePrice()).append("|").append(depthMarketDataField.getPreOpenInterest()).append("|")
                    .append(depthMarketDataField.getOpenPrice()).append("|").append(depthMarketDataField.getHighestPrice()).append("|").append(depthMarketDataField.getLowestPrice()).append("|")
                    .append(depthMarketDataField.getVolume()).append("|").append(depthMarketDataField.getTurnover()).append("|")
                    .append(depthMarketDataField.getOpenInterest()).append("|").append(depthMarketDataField.getClosePrice()).append("|")
                    .append(depthMarketDataField.getSettlementPrice()).append("|").append(depthMarketDataField.getUpperLimitPrice()).append("|")
                    .append(depthMarketDataField.getLowerLimitPrice()).append("|").append(depthMarketDataField.getPreDelta()).append("|").append(depthMarketDataField.getCurrDelta()).append("|")
                    .append(depthMarketDataField.getBidPrice1()).append("|").append(depthMarketDataField.getBidVolume1()).append("|").append(depthMarketDataField.getAskPrice1()).append("|").append(depthMarketDataField.getAskVolume1()).append("|")
                    .append(depthMarketDataField.getAveragePrice());

            marketDataPrintSream.println(marketDataStr.toString());
        } catch (Exception e) {
            logger.info("", e);
        }

    }
}
