package com.genus.ctp;

import org.apache.commons.lang.StringUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ApplicationContext {

    protected static Logger logger = LogManager.getLogger(ApplicationContext.class);


    private static final String PROPERTY_NAME_ROOTDIR = "ROOTDIR";

    private static final String PROPERTY_NAME_SAVELOGCOUNT = "SaveLogCount";

    public static final String CTP_CONFIG_NAME = "Config.properties";


    private static File rootDirectory = null;
    private static File cnfDirectory = null;
    private static File ctpConfigFile = null;
    private static File versionDirectory = null;
    private static File marketDataDirectory = null;
    private static File baseDataDirectory = null;
    public static Map<String, String> appProperties = new HashMap<>();

    public static void init() throws Exception {
        loadSystemProperties();
        buildDirectoryStructure();
        loadConfigProperties();

        delectLogFile();


    }

    public static void loadSystemProperties() {
        //read env variables first

        logger.info("Reading properties from OS environment variables ... ");
        for (String key : System.getenv().keySet()) {
            String val = System.getenv(key);
            updateAppProperties(key, val);
        }
        //read system properties
        logger.info("Reading properties from system properties ... ");
        for (Object key : System.getProperties().keySet()) {
            if (key instanceof String) {
                String val = System.getProperty((String) key);
                updateAppProperties((String) key, val);
            }
        }
    }

    public static void buildDirectoryStructure() throws Exception {
        rootDirectory = new File(System.getProperty(PROPERTY_NAME_ROOTDIR));
        logger.info("ROOTDIR >> {}", rootDirectory.getAbsolutePath());
        logger.info("LOGFILE >> {} ", System.getProperty("LOGFILE"));
        if (rootDirectory == null || rootDirectory.exists() == false || rootDirectory.isDirectory() == false) {
            throw new Exception(rootDirectory.getAbsolutePath() + "is Not Exists; Please Check ROOTDIR;");
        }
        versionDirectory = new File(rootDirectory.getAbsoluteFile() + File.separator + "version");
        logger.info("VersionDir >> {}", versionDirectory.getAbsolutePath());
        if (versionDirectory.exists() == false || versionDirectory.isDirectory() == false) {
            throw new Exception(versionDirectory.getAbsolutePath() + " is Not Exists; Please Check VersionDir ;");
        }
        cnfDirectory = new File(rootDirectory.getAbsoluteFile() + File.separator + "cnf");
        logger.info("CNFDirectory  >> {}", cnfDirectory.getAbsolutePath());
        if (cnfDirectory.exists() == false) {
            throw new Exception(cnfDirectory.getAbsolutePath() + " is Not Exists; Please Check CNFDirectory ;");
        }
        ctpConfigFile = new File(cnfDirectory.getAbsoluteFile() + File.separator + CTP_CONFIG_NAME);
        logger.info("CTPConfigFile  >> {}", ctpConfigFile.getAbsolutePath());
        if (ctpConfigFile.exists() == false) {
            throw new Exception(ctpConfigFile.getAbsolutePath() + " is Not Exists; Please Check ctpConfigFile ;");
        }

        File dataDirectory = new File(rootDirectory.getAbsoluteFile() + File.separator + "data");
        if (dataDirectory.exists() == false) {
            dataDirectory.mkdir();
        }
        marketDataDirectory = new File(rootDirectory.getAbsoluteFile() + File.separator + "data" + File.separator + "marketdata");
        if (marketDataDirectory.exists() == false) {
            marketDataDirectory.mkdir();
        }
        logger.info("MarketDataDirectory   >> {}", marketDataDirectory.getAbsolutePath());
        baseDataDirectory = new File(rootDirectory.getAbsoluteFile() + File.separator + "data" + File.separator + "basedata");
        if (baseDataDirectory.exists() == false) {
            baseDataDirectory.mkdir();
        }
        logger.info("BaseDataDirectory   >> {}", baseDataDirectory.getAbsolutePath());
    }

    public static void loadConfigProperties() throws IOException {

        logger.info("Reading properties from property file {}  ...", getCtpConfigFile().getAbsolutePath());
        Properties envProperties = new Properties();
        envProperties.load(new FileReader(getCtpConfigFile()));
        Enumeration<?> e = envProperties.propertyNames();
        while (e.hasMoreElements()) {
            String key = (String) e.nextElement();
            String value = envProperties.getProperty(key);
            updateAppProperties(key, value);
        }
    }

    private static void delectLogFile() {
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyyMMdd");
        int saveCount = 30;
        if (StringUtils.isNotEmpty(getProperty(PROPERTY_NAME_SAVELOGCOUNT))) {
            try {
                saveCount = Integer.parseInt(getProperty(PROPERTY_NAME_SAVELOGCOUNT));
            } catch (NumberFormatException e) {
                logger.error("Parse SaveLogCount is Failed", getProperty(PROPERTY_NAME_SAVELOGCOUNT));
            }
        }
        logger.info("Save Log File Count:{}", saveCount);
        Calendar calc = Calendar.getInstance();
        calc.add(Calendar.DAY_OF_MONTH, Integer.parseInt("-" + saveCount));
        String minDate = simpleDateFormat.format(calc.getTime());
        Pattern p = Pattern.compile("^(\\d{8}).*.log.*");
        if (System.getProperty("LOGFILE") != null && "".equals(System.getProperty("LOGFILE")) == false) {
            File file = new File(System.getProperty("LOGFILE"));
            if (file.getParentFile().exists()) {
                File[] files = file.getParentFile().listFiles();
                for (File file1 : files) {
                    if (file1.isDirectory() == false) {
                        try {
                            Matcher m = p.matcher(file1.getName());
                            if (m.find()) {
                                String str = m.group(1);
                                if (Integer.parseInt(str) <= Integer.parseInt(minDate)) {
                                    logger.info("will delete LogFile:{}", file1.getAbsolutePath());
                                    file1.delete();
                                }
                            }
                        } catch (NumberFormatException e) {
                        }
                    }
                }
            }
        }
        File[] files = marketDataDirectory.listFiles();
        p = Pattern.compile("ctp.(\\d{8})$");
        for (File file1 : files) {
            if (file1.isDirectory() == false) {
                try {
                    Matcher m = p.matcher(file1.getName());
                    if (m.find()) {
                        String str = m.group(1);
                        if (Integer.parseInt(str) <= Integer.parseInt(minDate)) {
                            logger.info("will delete CTPFile:{}", file1.getAbsolutePath());
                            file1.delete();
                        }
                    }
                } catch (NumberFormatException e) {
                }
            }
        }
    }


    public static void updateAppProperties(String key, String value) {
        appProperties.put(key, value);
    }


    public static String getProperty(String name) {
        return appProperties.get(name);
    }

    public static File getVersionDirectory() {
        return versionDirectory;
    }

    public static File getMarketDataDirectory() {
        return marketDataDirectory;
    }

    public static File getBaseDataDirectory() {
        return baseDataDirectory;
    }

    public static File getCnfDirectory() {
        return cnfDirectory;
    }

    public static File getCtpConfigFile() {
        return ctpConfigFile;
    }


}
