package com.genus.xs.multicast.afe.messages;

/**
 * Created by Administrator on 2018/10/18.
 */
public class TransactionData {
    public String time;
    public long vl;
    public double tp;
    public char tradeType;

    @Override
    public String toString() {
        StringBuffer buffer = new StringBuffer();
        buffer.append("(").append(time)
                .append("|")
                .append(vl)
                .append("|")
                .append(tp)
                .append("|")
                .append(tradeType)
                .append(")");
        return buffer.toString();
    }
}
