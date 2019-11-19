package com.genus.ctp.option;

public class GenusCTPOption {


    public enum Mode {
        Normal("Normal"),
        StaticOnly("StaticOnly"),
        SubscribeOnly("SubscribeOnly");

        private String theValue = "";

        Mode(String theValue) {
            this.theValue = theValue;
        }

        public String getTheValue() {
            return theValue;
        }

        public static Mode getOptionValue(String value) {
            for (Mode type : values())
                if (type.theValue.trim().equals(value.trim())) {
                    return type;
                }
            return null;
        }
    }

    public enum ProductClassType {

        ///期货
        THOST_FTDC_PC_Futures('1'),
        ///期货期权
        THOST_FTDC_PC_Options('2'),
        ///组合
        THOST_FTDC_PC_Combination('3'),
        ///即期
        THOST_FTDC_PC_Spot('4'),
        ///期转现
        THOST_FTDC_PC_EFP('5'),
        ///现货期权
        THOST_FTDC_PC_SpotOption('6'),
        ;
        private char theValue;

        public String getTheValue() {
            return String.valueOf(theValue);
        }

        ProductClassType(char theValue) {
            this.theValue = theValue;
        }

        public static ProductClassType getOption(char value) {
            for (ProductClassType type : values()) {
                if (type.theValue == value) {
                    return type;
                }
            }
            return null;
        }

    }


    public enum CombinationType {

        ///期货对锁组合
        THOST_FTDC_DCECOMBT_SPL('0'),
        ///期权对锁组合
        THOST_FTDC_DCECOMBT_OPL('1'),
        ///期货跨期组合
        THOST_FTDC_DCECOMBT_SP('2'),
        ///期货跨品种组合
        THOST_FTDC_DCECOMBT_SPC('3'),
        ///买入期权垂直价差组合
        THOST_FTDC_DCECOMBT_BLS('4'),
        ///卖出期权垂直价差组合
        THOST_FTDC_DCECOMBT_BES('5'),
        ///期权日历价差组合
        THOST_FTDC_DCECOMBT_CAS('6'),
        ///期权跨式组合
        THOST_FTDC_DCECOMBT_STD('7'),
        ///期权宽跨式组合
        THOST_FTDC_DCECOMBT_STG('8'),
        ///买入期货期权组合
        THOST_FTDC_DCECOMBT_BFO('9'),
        ///卖出期货期权组合
        THOST_FTDC_DCECOMBT_SFO('a'),
        ;
        private char theValue;

        CombinationType(char theValue) {
            this.theValue = theValue;
        }

        public static CombinationType getOption(char value) {
            for (CombinationType type : values()) {
                if (type.theValue == value) {
                    return type;
                }
            }
            return null;
        }

    }
}
