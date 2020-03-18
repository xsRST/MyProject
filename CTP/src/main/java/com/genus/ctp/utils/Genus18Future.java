package com.genus.ctp.utils;

import com.genus.ctp.mode.GenusCTPDepthMarketDataField;
import com.genus.ctp.mode.GenusCTPInstrumentField;
import org.apache.commons.math3.util.Pair;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.text.ParseException;
import java.util.*;

/***
 * 获取18个 股指,国债期货
 */
public class Genus18Future {
    protected static Logger logger = LogManager.getLogger(Genus18Future.class);

    private static final long maxVolume = 1000000;
    private static final int minVolume = 1;
    private static final String future_ic = "IC";
    private static final String future_if = "IF";
    private static final String future_ih = "IH";
    private static final String future_tf = "TF";
    private static final String future_t = "T";

    private static final String exchange = "CFFEX";
    private static final double cons_price = -1;
    private static final double stop_high = 999999;
    private static final int[] quarter = {3, 6, 9, 12};
    private Map<String, GenusCTPInstrumentField> ctpStaticMap = new TreeMap<>();
    private Map<String, GenusCTPDepthMarketDataField> ctpDepthMDMap = new TreeMap<>();

    private static Map<String, List> future_i_map = new HashMap<>();
    private static Map<String, List> future_t_map = new HashMap<>();
    static {
        future_i_map.put(future_ic, Arrays.asList(new String[]{"中证", "中证500股指期货", "0.2", "200", "200", "0.12", "0.12"}));
        future_i_map.put(future_if, Arrays.asList(new String[]{"沪深", "沪深300股指期货", "0.2", "100", "300", "0.1", "0.1"}));
        future_i_map.put(future_ih, Arrays.asList(new String[]{"上证", "上证50股指期货", "0.2", "200", "300", "0.1", "0.1"}));

        future_t_map.put(future_tf, Arrays.asList(new String[]{"5年期国债期货", "票面利率为3%的名义中期国债", "0.005", "500", "10000", "0.012", "0.012"}));
        future_t_map.put(future_t, Arrays.asList(new String[]{"10年期国债期货", "10年期国债期货", "0.005", "500", "10000", "0.02", "0.02"}));

    }

    public int startWriter18Future() {
        logger.info("程序开始生成18个期货代码 .. ");
        try {
            Map<String, Pair<String, String>> i_contract_year_month_map = get_i_contract_year_month_map();
            Map<String, Pair<String, String>> t_contract_year_month_map = get_t_contract_year_month_map();
            //生成股指期货数据;
            writeData2Map(i_contract_year_month_map, future_i_map);
            writeData2Map(t_contract_year_month_map, future_t_map);
            logger.info("开始写入18个静态数据 ");
            GenusCTPFileUtil.writeTradeData2File(ctpStaticMap, ctpDepthMDMap);
            logger.info("生成数据完成...");
        } catch (Exception e) {
            logger.error("", e);
            return -1;
        }
        return 0;
    }

    private void writeData2Map(Map<String, Pair<String, String>> i_contract_year_month_map, Map<String, List> future_i_map) {
        for (Map.Entry<String, Pair<String, String>> entry : i_contract_year_month_map.entrySet()) {
            String instrumentIDData = entry.getKey();
            Pair<String, String> dateInfo = entry.getValue();
            String delivDate = dateInfo.getKey();
            String listDate = dateInfo.getValue();
            for (Map.Entry<String, List> iFutureEntry : future_i_map.entrySet()) {
                String preFID = iFutureEntry.getKey();
                List<String> infoList = iFutureEntry.getValue();
                if (infoList.size() == 7) {
                    GenusCTPInstrumentField instrumentField = new GenusCTPInstrumentField();

                    String instrumentID = preFID + instrumentIDData;
                    instrumentField.InstrumentID = instrumentID;
                    instrumentField.ExchangeID = exchange;
                    instrumentField.ExchangeInstID = instrumentID + "." + exchange;
                    instrumentField.InstrumentName = infoList.get(1) + instrumentID;
                    instrumentField.DeliveryYear = Integer.valueOf(delivDate.substring(0, 4));
                    instrumentField.DeliveryMonth = Integer.valueOf(delivDate.substring(4, 6));
                    instrumentField.MaxLimitOrderVolume = maxVolume;
                    instrumentField.MinLimitOrderVolume = minVolume;
                    instrumentField.MaxMarketOrderVolume = maxVolume;
                    instrumentField.MinMarketOrderVolume = minVolume;

                    instrumentField.VolumeMultiple = Integer.parseInt(infoList.get(3));
                    instrumentField.PriceTick = Double.parseDouble(infoList.get(2));
                    instrumentField.CreateDate = TimeUtils.TODAY();
                    instrumentField.OpenDate = listDate;
                    instrumentField.ExpireDate = delivDate;
                    instrumentField.StartDelivDate = delivDate;
                    instrumentField.EndDelivDate = delivDate;
                    instrumentField.InstLifePhase = '1';
                    instrumentField.IsTrading = true;
                    instrumentField.PositionType = '2';
                    instrumentField.PositionDateType = '2';
                    instrumentField.LongMarginRatio = Double.parseDouble(infoList.get(5));
                    instrumentField.ShortMarginRatio = Double.parseDouble(infoList.get(6));
                    instrumentField.MaxMarginSideAlgorithm = '1';

                    GenusCTPDepthMarketDataField depthMarketDataField = new GenusCTPDepthMarketDataField();
                    depthMarketDataField.PreSettlementPrice = cons_price;
                    depthMarketDataField.UpperLimitPrice = stop_high;
                    depthMarketDataField.LowerLimitPrice = cons_price;
                    ctpStaticMap.put(instrumentID, instrumentField);
                    ctpDepthMDMap.put(instrumentID, depthMarketDataField);

                } else {
                    logger.error("生成数据异常, 请联系相关人员 >> [{}] :{}\n{{}", preFID, infoList.toString());
                    continue;
                }
            }
        }
    }

    //国债; 最近三个季月;  交割日为到期月份的第二个星期五
    private Map<String, Pair<String, String>> get_t_contract_year_month_map() {
        Map<String, Pair<String, String>> contract_year_month_map = new TreeMap<>();
        List<String> keyList = new ArrayList<>();
        String nowMonth = TimeUtils.Month();
        for (int i = 0; i < quarter.length; i++) {
            Calendar calendar = Calendar.getInstance();
            if (Integer.parseInt(nowMonth) > quarter[i]) {
                calendar.add(Calendar.YEAR, 1);
            }
            calendar.set(Calendar.MONTH, quarter[i] - 1);
            String instrumentIDData = TimeUtils.instrumentIDFormat.get().format(calendar.getTime());
            String delivDate = getStartDelivDate(calendar, 2);
            String listData = getListData(delivDate, 9);
            contract_year_month_map.put(instrumentIDData, new Pair<String, String>(delivDate, listData));
        }
        keyList.addAll(contract_year_month_map.keySet());
        contract_year_month_map.remove(keyList.get(keyList.size() - 1));
        return contract_year_month_map;
    }


    //当月,下月,及随后两个季月,最后交易日, 合约到期月份第三个周五,遭国家法定节假日顺延
    private Map<String, Pair<String, String>> get_i_contract_year_month_map() throws Exception {

        Map<String, Pair<String, String>> contract_year_month_map = new TreeMap<>();
        String listData = null;
        //当月
        Calendar calendar = Calendar.getInstance();

        String instrumentIDData = TimeUtils.instrumentIDFormat.get().format(calendar.getTime());
        String delivDate = getStartDelivDate(calendar, 3);

        if (calendar.get(Calendar.MONTH) % 3 == 0) {
            listData = getListData(delivDate, 8);
        } else {
            listData = getListData(delivDate, 2);
        }
        contract_year_month_map.put(instrumentIDData, new Pair<String, String>(delivDate, listData));
        //下个月
        calendar.add(Calendar.MONTH, 1);
        instrumentIDData = TimeUtils.instrumentIDFormat.get().format(calendar.getTime());
        delivDate = getStartDelivDate(calendar, 3);
        if (calendar.get(Calendar.MONTH) % 3 == 0) {
            listData = getListData(delivDate, 8);
        } else {
            listData = getListData(delivDate, 2);
        }
        contract_year_month_map.put(instrumentIDData, new Pair<String, String>(delivDate, listData));

        String month = TimeUtils.monthFormat.get().format(calendar.getTime());
        List<String> keyList = new ArrayList<>();
        for (int i = 0; i < quarter.length; i++) {
            calendar = Calendar.getInstance();

            if (Integer.parseInt(month) >= quarter[i]) {
                calendar.add(Calendar.YEAR, 1);
            }
            calendar.set(Calendar.MONTH, quarter[i] - 1);
            instrumentIDData = TimeUtils.instrumentIDFormat.get().format(calendar.getTime());
            delivDate = getStartDelivDate(calendar, 3);
            if (calendar.get(Calendar.MONTH) % 3 == 0) {
                listData = getListData(delivDate, 8);
            } else {
                listData = getListData(delivDate, 2);
            }
            contract_year_month_map.put(instrumentIDData, new Pair<String, String>(delivDate, listData));
            keyList.add(instrumentIDData);
        }
        Collections.sort(keyList);
        keyList.remove(0);
        keyList.remove(0);
        keyList.forEach(key -> {
            contract_year_month_map.remove(key);
        });
        return contract_year_month_map;

    }

    private String getStartDelivDate(Calendar calendar, int friday_sequence) {

        calendar.set(Calendar.DATE, 1);
        int count = 0;
        while (count < friday_sequence) {
            if (TimeUtils.isFriday(calendar.getTime())) {
                count++;
            }
            if (count < friday_sequence == true) {
                calendar.add(Calendar.DATE, 1);
            }
        }
        return TimeUtils.dateFormat.get().format(calendar.getTime());
    }

    private String getListData(String delivDateStr, int monthGap) {
        String listData = null;
        try {
            Date delivDate = TimeUtils.dateFormat.get().parse(delivDateStr);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(delivDate);
            calendar.add(Calendar.MONTH, -monthGap);
            calendar.set(Calendar.YEAR, Integer.parseInt(delivDateStr.substring(0, 4)));
            delivDateStr = getStartDelivDate(calendar, 3);
            delivDate = TimeUtils.dateFormat.get().parse(delivDateStr);
            calendar.setTime(delivDate);
            calendar.add(Calendar.DATE, 3);
            listData = TimeUtils.dateFormat.get().format(calendar.getTime());
        } catch (ParseException e) {
            e.printStackTrace();
        }

        return listData;
    }


}
