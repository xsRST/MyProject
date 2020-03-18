package com.genus.ctp.utils;


import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;

public class TimeUtils {

    public static final ThreadLocal<SimpleDateFormat> monthFormat = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("MM");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> instrumentIDFormat = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyMM");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> dateFormat = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyyyMMdd");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormatWithMilliSeconds = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("HH:mm:ss:SSS");
        }
    };

    public static synchronized String TODAY() {
        return dateFormat.get().format(new Date());
    }

    public static synchronized String Month() {
        return monthFormat.get().format(new Date());
    }

    public static synchronized boolean isFriday(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);
        return calendar.get(Calendar.DAY_OF_WEEK) == Calendar.FRIDAY;
    }

}
