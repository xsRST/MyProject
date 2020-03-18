package com.genus.xs.multicast.afe.messages;

import java.nio.charset.Charset;

/**
 * Created by Administrator on 2018/10/11.
 */
public interface Field {
    String getName();

    int getLength();

    int getValue();

    DataType getType();

    byte[] getBytes(Object obj, Charset charset);

    Object parse(byte[] bytes, int startPos, Charset charset);

    enum FieldDefinition implements Field {

        InstrumentNumber(2001, DataType.AFEDataType.UINT32),
        InstrumentCode(7001, DataType.AFEDataType.CharArray),
        SubMarketCode(2002, DataType.AFEDataType.UINT32),
        EnglishShortName(7002, DataType.AFEDataType.CharArray),
        TraditionalChineseName(7003, DataType.AFEDataType.CharArray) {
            @Override
            public Object parse(byte[] bytes, int startPos, Charset charset) {
                return getType().parse(bytes, startPos, Charset.forName("BIG5"));
            }

            @Override
            public byte[] getBytes(Object obj, Charset charset) {
                return getType().getBytes(obj, Charset.forName("BIG5"));
            }
        },
        SimplifiedChineseName(7004, DataType.AFEDataType.CharArray) {
            @Override
            public Object parse(byte[] bytes, int startPos, Charset charset) {
                return getType().parse(bytes, startPos, Charset.forName("GB2312"));
            }

            @Override
            public byte[] getBytes(Object obj, Charset charset) {
                return getType().getBytes(obj, Charset.forName("GB2312"));
            }
        },
        SimplifiedChineseNameUTF16(7007, DataType.AFEDataType.CharArray) {
            @Override
            public Object parse(byte[] bytes, int startPos, Charset charset) {
                return getType().parse(bytes, startPos, Charset.forName("UTF-16LE"));
            }

            @Override
            public byte[] getBytes(Object obj, Charset charset) {
                return getType().getBytes(obj, Charset.forName("UTF-16LE"));
            }
        },
        PreviousClose(12001, DataType.AFEDataType.INT32_D3),
        LotSize(2003, DataType.AFEDataType.UINT32),
        SpreadTableCode(3, DataType.AFEDataType.UINT8),
        InstrumentType(7005, DataType.AFEDataType.CharArray),
        CurrencyCode(7006, DataType.AFEDataType.CharArray),
        CurrencyFactor(1001, DataType.AFEDataType.UINT16),
        ShortSellFlag(17001, DataType.AFEDataType.Char8),
        StampDutyFlag(17002, DataType.AFEDataType.Char8),
        ListingDate(9501, DataType.AFEDataType.BDateYear),
        DelistingDate(9502, DataType.AFEDataType.BDateYear),
        CallPutFlag(17003, DataType.AFEDataType.Char8),
        VCMFlag(17004, DataType.AFEDataType.Char8),
        CASFlag(17005, DataType.AFEDataType.Char8),
        Nominal(12002, DataType.AFEDataType.INT32_D3),
        IEP(12003, DataType.AFEDataType.INT32_D3),
        IEV(3001, DataType.AFEDataType.UINT64),
        BestBidPrice(12004, DataType.AFEDataType.INT32_D3),
        NoOfBidOrder(2004, DataType.AFEDataType.UINT32),
        NoOfBidQty(3002, DataType.AFEDataType.UINT64),
        BestAskPrice(12005, DataType.AFEDataType.INT32_D3),
        NoOfAskOrder(2005, DataType.AFEDataType.UINT32),
        NoOfAskQty(3003, DataType.AFEDataType.UINT64),
        DayHigh(12006, DataType.AFEDataType.INT32_D3),
        DayLow(12007, DataType.AFEDataType.INT32_D3),
        DayClose(12008, DataType.AFEDataType.INT32_D3),
        TradingStatus(2, DataType.AFEDataType.UINT8),
        VCMLowerPrice(12009, DataType.AFEDataType.INT32_D3),
        VCMUpperPrice(12010, DataType.AFEDataType.INT32_D3),
        CoolingOffStartTime(9402, DataType.AFEDataType.BTimeSec),
        CoolingOffEndTime(9403, DataType.AFEDataType.BTimeSec),
        CASReferencePrice(12011, DataType.AFEDataType.INT32_D3),
        VCMReferencePrice(12012, DataType.AFEDataType.INT32_D3),
        CASUpperPrice(12013, DataType.AFEDataType.INT32_D3),
        CASLowerPrice(12014, DataType.AFEDataType.INT32_D3),
        WeightedVolume(6001, DataType.AFEDataType.INT64),
        WeightedTurnover(6002, DataType.AFEDataType.INT64),

        TradingSessionSubID(5, DataType.AFEDataType.UINT8),
        TradingSessionStatus(6, DataType.AFEDataType.UINT8),
        SystemDate(9503, DataType.AFEDataType.BDateYear),
        SystemTime(9401, DataType.AFEDataType.BTimeSec),
        Transaction(18001, DataType.AFEDataType.PriceVolTran),
        PacketSeqNumber(3000, DataType.AFEDataType.UINT32);


        private int fieldNo;
        private DataType type;

        FieldDefinition(int fieldNo, DataType type) {
            this.fieldNo = fieldNo;
            this.type = type;
        }

        public void resetField(int fieldNo, DataType type) {
            this.fieldNo = fieldNo;
            this.type = type;
        }

        @Override
        public String getName() {
            return this.name();
        }

        @Override
        public int getLength() {
            return type.getLength();
        }

        @Override
        public DataType getType() {
            return type;
        }

        @Override
        public byte[] getBytes(Object obj, Charset charset) {
            return type.getBytes(obj, charset);
        }

        @Override
        public Object parse(byte[] bytes, int startPos, Charset charset) {
            return type.parse(bytes, startPos, charset);
        }


        public static Field resolve(int value) {
            for (Field.FieldDefinition type : values()) {
                if (type.getValue() == value) {
                    return type;
                }
            }

            return null;
        }

        @Override
        public int getValue() {
            return fieldNo;
        }

    }
}
