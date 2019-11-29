package com.genus.ctp.tushare;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import org.apache.commons.lang.StringUtils;
import org.apache.http.HttpEntity;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.util.EntityUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

public class GenusTushareManager {
    protected static Logger logger = LogManager.getLogger(GenusTushareManager.class);
    private static Gson gson = new Gson();
    private static final String token = "437a211949d1fa91cfb915b64d4aaaea5d54f9654ea2496f8cab9040";
    private static final String httpAddr = "http://api.tushare.pro";

    public GenusTushareManager() {

    }


    public boolean getFutureInfo() {
        boolean isConnected = false;
        Map<String, Object> paramsMap = new HashMap<>();
        Map<String, Object> entityMap = new HashMap<>();
        paramsMap.put("exchange", "CFFEX");
        entityMap.put("api_name", "fut_basic");
        entityMap.put("token", token);
        entityMap.put("params", paramsMap);
        String result = sendPostRequest(entityMap);
        if (StringUtils.isNotEmpty(result)) {
            isConnected = true;
        }
        return isConnected;
    }

    private String sendPostRequest(Map<String, Object> entityMap) {
        String result = null;
        CloseableHttpClient client = null;
        CloseableHttpResponse res = null;
        try {
            client = HttpClientBuilder.create().build();
            String postBody = gson.toJson(entityMap, new TypeToken<Map<String, Object>>() {
            }.getType());

            HttpPost httpPost = new HttpPost(httpAddr);
            RequestConfig requestConfig = RequestConfig.custom().setConnectTimeout(30000)
                    .setConnectionRequestTimeout(30000)
                    .setSocketTimeout(60000)
                    .build();
            httpPost.setConfig(requestConfig);


            httpPost.setEntity(new StringEntity(postBody));
            res = client.execute(httpPost);
            HttpEntity resEntity = res.getEntity();
            result = EntityUtils.toString(resEntity);

        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (client != null) {
                    client.close();
                }
            } catch (IOException e) {
            }
            try {
                if (res != null) {
                    res.close();
                }
            } catch (IOException e) {
            }

        }


        return result;
    }


    public static void main(String[] args) {

        try {
            URL url = new URL(httpAddr);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            System.out.println(connection.getResponseCode());
            InetAddress inetAddress = InetAddress.getByName(httpAddr);
            System.out.println(inetAddress.isReachable(5000));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
