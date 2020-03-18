#pragma once
#include "GenusCTPMarketDataSpi.h"
#include "GenusCTPTradeSpi.h"
using namespace std;



class GenusMarketDataManager 
{
public:
	GenusMarketDataManager(void);
	~GenusMarketDataManager(void);
private:
	GenusCTPMarketDataSpi* m_pMarketDataSpi;
	GenusCTPTradeSpi* t_pTradeSpi;
	JavaVM* m_pJavaVm;
	jobject m_object;

public:
	static GenusMarketDataManager* GetInstance();

	void StartTradeCTP(JNIEnv* pEnv, jobject obj, jobject tradeSpi, const char* pTradeFrontAddr);
	void StartTradeCTP(const char* pParam);
	

	void StartMarketCTP(JNIEnv* pEnv, jobject obj, jobject marketDataSpi, const char* pMarketFontAddr);
	void StartMarketCTP(const char* pParam);
	const char* GetMarkeApiVersion();
	const char* GetTradeApiVersion();
	const char* GetTradingDay();

	///Trade客户端认证请求
	int ReqTradeAuthenticate(CThostFtdcReqAuthenticateField* pReqAuthenticateField, int nRequestID);
	///MarketData客户端认证请求
	int ReqMarketDataAuthenticate(CThostFtdcReqAuthenticateField* pReqAuthenticateField, int nRequestID);
	
	///Trade用户登录请求
	int ReqTradeUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID);
	///MarketData用户登录请求
	int ReqMarketDataUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID);
	///Trade登出请求
	int ReqTradeUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID);
	///MarketData登出请求
	int ReqMarketDataUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID);


	///请求查询合约
	int ReqQryInstrument(CThostFtdcQryInstrumentField* pQryInstrument, int nRequestID);
	///请求查询行情
	int ReqQryDepthMarketData(CThostFtdcQryDepthMarketDataField* pQryDepthMarketData, int nRequestID);


	///订阅行情。
	int SubscribeMarketData(char* ppInstrumentID[], int nCount);

	///退订行情。
	int UnSubscribeMarketData(char* ppInstrumentID[], int nCount);


};

DWORD WINAPI StartMarketCTPThread(LPVOID lpParam);
DWORD WINAPI StartTradeCTPThread(LPVOID lpParam);

