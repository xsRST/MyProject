package com.genus.ctp.tushare;

import org.apache.commons.lang.StringUtils;

public class Type {


    public static enum FutureExchangeType {
        CFFEX("I-CF,T-CF2"),
        DCE("DLC"),
        CZCE("ZZC"),
        SHFE("SSC"),
        INE("SE");

        private String genusExchange;

        FutureExchangeType(String genusExchange) {
            this.genusExchange = genusExchange;
        }

        public static FutureExchangeType getOptionValueFromGenusExchange(String genusExchange) {
            if (StringUtils.isNotEmpty(genusExchange) == false) return null;
            for (FutureExchangeType type : FutureExchangeType.values()) {
                String[] genusExchanges = type.genusExchange.split(",");
                if (genusExchanges.length > 1) {
                    for (String exchange : genusExchanges) {
                        String[] realExchanges = exchange.split("-");
                        if (realExchanges.length > 1) {
                            if (genusExchange.equalsIgnoreCase(realExchanges[1])) {
                                return type;
                            }
                        } else if (genusExchange.equalsIgnoreCase(realExchanges[0])) {
                            return type;
                        }
                    }
                } else if (genusExchange.equalsIgnoreCase(genusExchanges[0])) {
                    return type;
                }
            }
            return null;
        }

        public static FutureExchangeType getOptionValueFromExchange(String exchange) {
            if (StringUtils.isNotEmpty(exchange) == false) return null;
            for (FutureExchangeType type : FutureExchangeType.values()) {
                if (type.name().equalsIgnoreCase(exchange)) {
                    return type;
                }
            }
            return null;
        }

    }
}
