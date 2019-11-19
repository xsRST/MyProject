package com.genus.ctp.utils;


import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.SimpleTimeZone;

public class TimeUtils {

    public static final ThreadLocal<SimpleDateFormat> yearFormat = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyyy");
        }
    };
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
    public static final ThreadLocal<SimpleDateFormat> dateFormat2 = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyMMdd");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormat = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyyyMMdd-HH:mm:ss");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormat2 = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyyyMMddHHmmSSS");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> datetimeFormatWithoutColon = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyyyMMdd-HHmmss");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormatMilli = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyyyMMdd-HH:mm:ss.SSS");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormatWithoutDate = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("HH:mm:ss");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormatWithHourMinute = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("HH:mm");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormatWithHourMinuteForInput = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("HHmm");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormatWithoutColon = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("HHmmss");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormatWithoutColon1 = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("Hmmss");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormatWithoutColon2 = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("HHmmssSSS");
        }
    };
    public static final ThreadLocal<SimpleDateFormat> timeFormatWithMilliSeconds = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("HH:mm:ss.SSS");
        }
    };

    public static final ThreadLocal<SimpleDateFormat> GMTTimeFormat = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            SimpleDateFormat rt = new SimpleDateFormat("yyyyMMdd-HH:mm:ss");
            rt.setCalendar(Calendar.getInstance(new SimpleTimeZone(0, "GMT")));
            return rt;
        }
    };

    public static final ThreadLocal<SimpleDateFormat> GMTTimeFormatWithoutDate = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            SimpleDateFormat rt = new SimpleDateFormat("HH:mm:ss");
            rt.setCalendar(Calendar.getInstance(new SimpleTimeZone(0, "GMT")));
            return rt;
        }
    };
    public static final ThreadLocal<SimpleDateFormat> postTimeFormat = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyyy/MM/dd HH:mm");
        }
    };


    public static synchronized String getCurrentTimeGMT() {
        return GMTTimeFormat.get().format(new Date());
    }

    public static synchronized String getCurrentTime() {
        return timeFormat.get().format(new Date());
    }

    public static synchronized String getSendingTime() {
        return timeFormat2.get().format(new Date());
    }

    public static synchronized String getTimestamp() {
        return timeFormatWithMilliSeconds.get().format(new Date());
    }

    public static synchronized String getTimestamp2() {
        return timeFormatWithoutDate.get().format(new Date());
    }

    //hs20130818
    public static synchronized String TODAY() {
        return dateFormat.get().format(new Date());
    }

    public static synchronized String YEAR() {
        return yearFormat.get().format(new Date());
    }

    public static synchronized String Month() {
        return monthFormat.get().format(new Date());
    }

    public static synchronized boolean isWeekend(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.SATURDAY)
            return true;
        return calendar.get(Calendar.DAY_OF_WEEK) == Calendar.SUNDAY;
    }

    public static synchronized boolean isMorning() {
        return Calendar.getInstance().getTime().getHours() - 12 > 0;
    }

    public static synchronized Date nextDay(Date inDate) {
        return new Date(inDate.getTime() + 24 * 3600 * 1000);
    }

    public static synchronized Date nextBusinessDay(Date inDate) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(inDate);
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.FRIDAY) {
            return new Date(inDate.getTime() + 3 * 24 * 3600 * 1000);
        } else if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.SATURDAY) {
            return new Date(inDate.getTime() + 2 * 24 * 3600 * 1000);
        } else {
            return new Date(inDate.getTime() + 24 * 3600 * 1000);
        }
    }

    public static synchronized Date nextDay(Date inDate, long numberOfDays) {
        return new Date(inDate.getTime() + numberOfDays * 24 * 3600 * 1000);
    }

    public static synchronized Date prevDay(Date inDate) {
        return new Date(inDate.getTime() - 24 * 3600 * 1000);
    }

    public static synchronized Date prevBusinessDay(Date inDate) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(inDate);
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.MONDAY) {
            return new Date(inDate.getTime() - 3 * 24 * 3600 * 1000);
        } else {
            return new Date(inDate.getTime() - 24 * 3600 * 1000);
        }
    }

    public static long getCountBetweenTwoDate(String beginDate, String endDate) throws Exception {
        Date begin = TimeUtils.dateFormat.get().parse(beginDate);
        Date end = TimeUtils.dateFormat.get().parse(endDate);

        long timeBgn = begin.getTime();
        long timeEnd = end.getTime();
        long between_days = (timeEnd - timeBgn) / (1000 * 3600 * 24);
        return between_days;
    }

    public static String getNextDay(String date) throws Exception {
        Calendar c = Calendar.getInstance();
        c.setTime(TimeUtils.dateFormat.get().parse(date));
        c.add(Calendar.DATE, 1);
        return TimeUtils.dateFormat.get().format(c.getTime());
    }

    public static synchronized Date prevDay(Date inDate, long numberOfDays) {
        return new Date(inDate.getTime() - numberOfDays * 24 * 3600 * 1000);
    }

    public static synchronized String getWeekdayInString() {
        return getWeekdayInString(new Date());
    }

    public static synchronized int getWeekdayInNumber() {
        return getWeekdayInNumber(new Date());
    }

    public static synchronized String getWeekdayInString(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);

        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.MONDAY) return "MON";
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.TUESDAY) return "TUE";
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.WEDNESDAY) return "WED";
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.THURSDAY) return "THR";
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.FRIDAY) return "FRI";
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.SATURDAY) return "SAT";
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.SUNDAY) return "SUN";

        return "XXX";
    }

    public static synchronized int getWeekdayInNumber(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);

        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.MONDAY) return 1;
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.TUESDAY) return 2;
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.WEDNESDAY) return 3;
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.THURSDAY) return 4;
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.FRIDAY) return 5;
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.SATURDAY) return 6;
        if (calendar.get(Calendar.DAY_OF_WEEK) == Calendar.SUNDAY) return 0;

        return 0;
    }

    public static synchronized boolean isMonday(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);
        return calendar.get(Calendar.DAY_OF_WEEK) == Calendar.MONDAY;
    }

    public static synchronized boolean isTuesday(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);
        return calendar.get(Calendar.DAY_OF_WEEK) == Calendar.TUESDAY;
    }

    public static synchronized boolean isWendesday(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);
        return calendar.get(Calendar.DAY_OF_WEEK) == Calendar.WEDNESDAY;
    }

    public static synchronized boolean isThursday(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);
        return calendar.get(Calendar.DAY_OF_WEEK) == Calendar.THURSDAY;
    }

    public static synchronized boolean isFriday(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);
        return calendar.get(Calendar.DAY_OF_WEEK) == Calendar.FRIDAY;
    }

    public static synchronized boolean isSaturday(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);
        return calendar.get(Calendar.DAY_OF_WEEK) == Calendar.SATURDAY;
    }

    public static synchronized boolean isSunday(Date date) {
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTime(date);
        return calendar.get(Calendar.DAY_OF_WEEK) == Calendar.SUNDAY;
    }


    public static synchronized String getNextMonth(String yearMonth) throws Exception {

        Date workDay = dateFormat.get().parse(yearMonth.substring(0, 6) + "15");

        Date nextMonth = new Date(workDay.getTime() + (long) 30 * (long) 24 * (long) 3600 * (long) 1000);

        return dateFormat.get().format(nextMonth).substring(0, 6);

    }

    public static synchronized String timeZoneConvert(String sTime, String fromZone, String toZone) throws Exception {
        LocalTime actionLocalTime = LocalTime.of(Integer.parseInt(sTime.substring(0, 2)), Integer.parseInt(sTime.substring(3, 5)), Integer.parseInt(sTime.substring(6, 8)));
        ZonedDateTime time = ZonedDateTime.of(LocalDate.now(), actionLocalTime, ZoneId.of(fromZone));
        return time.withZoneSameInstant(ZoneId.of(toZone)).toLocalTime().format(DateTimeFormatter.ISO_LOCAL_TIME);
    }


}
