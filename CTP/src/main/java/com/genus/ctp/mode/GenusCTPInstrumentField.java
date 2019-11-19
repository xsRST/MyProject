package com.genus.ctp.mode;

import java.io.Serializable;

public class GenusCTPInstrumentField implements Serializable {
    ///合约代码
    public String InstrumentID;
    ///交易所代码
    public String ExchangeID;
    ///合约名称
    public String InstrumentName;
    ///合约在交易所的代码
    public String ExchangeInstID;
    ///产品代码
    public String ProductID;
    ///产品类型
    public char ProductClass;
    ///交割年份
    public int DeliveryYear;
    ///交割月
    public int DeliveryMonth;
    ///市价单最大下单量
    public long MaxMarketOrderVolume;
    ///市价单最小下单量
    public long MinMarketOrderVolume;
    ///限价单最大下单量
    public long MaxLimitOrderVolume;
    ///限价单最小下单量
    public long MinLimitOrderVolume;
    ///合约数量乘数
    public long VolumeMultiple;
    ///最小变动价位
    public double PriceTick;
    ///创建日
    public String CreateDate;
    ///上市日
    public String OpenDate;
    ///到期日
    public String ExpireDate;
    ///开始交割日
    public String StartDelivDate;
    ///结束交割日
    public String EndDelivDate;
    ///合约生命周期状态 0-未上市,1-上市,2-停牌,3-到期
    public char InstLifePhase;
    ///当前是否交易
    public boolean IsTrading;
    ///持仓类型
    public char PositionType;
    ///持仓日期类型
    public char PositionDateType;
    ///多头保证金率
    public double LongMarginRatio;
    ///空头保证金率
    public double ShortMarginRatio;
    ///是否使用大额单边保证金算法
    public char MaxMarginSideAlgorithm;
    ///基础商品代码
    public String UnderlyingInstrID;
    ///执行价
    public double StrikePrice;
    ///期权类型
    public char OptionsType;
    ///合约基础商品乘数
    public double UnderlyingMultiple;
    ///组合类型
    public char CombinationType;


    public String getInstrumentID() {
        return InstrumentID;
    }

    public String getExchangeID() {
        return ExchangeID;
    }

    public String getInstrumentName() {
        return InstrumentName;
    }

    public String getExchangeInstID() {
        return ExchangeInstID;
    }

    public String getProductID() {
        return ProductID;
    }

    public char getProductClass() {
        return ProductClass;
    }

    public int getDeliveryYear() {
        return DeliveryYear;
    }

    public int getDeliveryMonth() {
        return DeliveryMonth;
    }

    public long getMaxMarketOrderVolume() {
        return MaxMarketOrderVolume;
    }

    public long getMinMarketOrderVolume() {
        return MinMarketOrderVolume;
    }

    public long getMaxLimitOrderVolume() {
        return MaxLimitOrderVolume;
    }

    public long getMinLimitOrderVolume() {
        return MinLimitOrderVolume;
    }

    public long getVolumeMultiple() {
        return VolumeMultiple;
    }

    public double getPriceTick() {
        return PriceTick;
    }

    public String getCreateDate() {
        return CreateDate;
    }

    public String getOpenDate() {
        return OpenDate;
    }

    public String getExpireDate() {
        return ExpireDate;
    }

    public String getStartDelivDate() {
        return StartDelivDate;
    }

    public String getEndDelivDate() {
        return EndDelivDate;
    }

    public char getInstLifePhase() {
        return InstLifePhase;
    }

    public boolean isTrading() {
        return IsTrading;
    }

    public char getPositionType() {
        return PositionType;
    }

    public char getPositionDateType() {
        return PositionDateType;
    }

    public double getLongMarginRatio() {
        return LongMarginRatio;
    }

    public double getShortMarginRatio() {
        return ShortMarginRatio;
    }

    public char getMaxMarginSideAlgorithm() {
        return MaxMarginSideAlgorithm;
    }

    public String getUnderlyingInstrID() {
        return UnderlyingInstrID;
    }

    public double getStrikePrice() {
        return StrikePrice;
    }

    public char getOptionsType() {
        return OptionsType;
    }

    public double getUnderlyingMultiple() {
        return UnderlyingMultiple;
    }

    public char getCombinationType() {
        return CombinationType;
    }
}
