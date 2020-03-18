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

	///Trade�ͻ�����֤����
	int ReqTradeAuthenticate(CThostFtdcReqAuthenticateField* pReqAuthenticateField, int nRequestID);
	///MarketData�ͻ�����֤����
	int ReqMarketDataAuthenticate(CThostFtdcReqAuthenticateField* pReqAuthenticateField, int nRequestID);
	
	///Trade�û���¼����
	int ReqTradeUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID);
	///MarketData�û���¼����
	int ReqMarketDataUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID);
	///Trade�ǳ�����
	int ReqTradeUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID);
	///MarketData�ǳ�����
	int ReqMarketDataUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID);


	///�����ѯ��Լ
	int ReqQryInstrument(CThostFtdcQryInstrumentField* pQryInstrument, int nRequestID);
	///�����ѯ����
	int ReqQryDepthMarketData(CThostFtdcQryDepthMarketDataField* pQryDepthMarketData, int nRequestID);


	///�������顣
	int SubscribeMarketData(char* ppInstrumentID[], int nCount);

	///�˶����顣
	int UnSubscribeMarketData(char* ppInstrumentID[], int nCount);


};

DWORD WINAPI StartMarketCTPThread(LPVOID lpParam);
DWORD WINAPI StartTradeCTPThread(LPVOID lpParam);

