package com.genus.ctp;

import org.apache.commons.lang.StringUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.Calendar;
import java.util.Timer;
import java.util.TimerTask;


public class Application {

    private static Logger logger = LogManager.getLogger(Application.class);

    private static void init() throws Exception {
        ApplicationContext.init();
        GenusCTPConfig.init();
    }

    public static void main(String[] args) {

        try {
            init();
            stopTask();
            start();
        } catch (Exception e) {
            logger.error("", e);
            stop();
        }


    }

    private static void start() throws Exception {
        GenusCTPServerManager manager = new GenusCTPServerManager();
        manager.start();
    }

    private static void stop() {
        System.exit(0);
    }


    protected static void stopTask() {
        Calendar c = Calendar.getInstance();
        c.set(Calendar.HOUR_OF_DAY, 15);
        c.set(Calendar.MINUTE, 10);
        c.set(Calendar.SECOND, 0);

        if (StringUtils.isNotEmpty(GenusCTPConfig.endTime)) {
            String[] split = GenusCTPConfig.endTime.split(":");
            if (split.length == 3) {
                c.set(Calendar.HOUR_OF_DAY, Integer.valueOf(split[0]));
                c.set(Calendar.MINUTE, Integer.valueOf(split[1]));
                c.set(Calendar.SECOND, Integer.valueOf(split[2]));
            } else if (split.length == 2) {
                c.set(Calendar.HOUR_OF_DAY, Integer.valueOf(split[0]));
                c.set(Calendar.MINUTE, Integer.valueOf(split[1]));
            } else if (split.length == 1) {
                c.set(Calendar.HOUR_OF_DAY, Integer.valueOf(split[0]));
            }
        }
        Timer timer = new Timer();
        timer.schedule(new TimerTask() {
            public void run() {
                logger.info("结束时间到, 退出程序.....");
                stop();
            }
        }, c.getTime());
    }


}
