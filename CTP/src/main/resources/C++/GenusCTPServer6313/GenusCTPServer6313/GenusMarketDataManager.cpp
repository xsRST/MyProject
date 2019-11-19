#include "pch.h"
#include "GenusMarketDataManager.h"


GenusMarketDataManager* g_pMarketDataManager = NULL;

DWORD WINAPI StartMarketCTPThread(LPVOID pParam) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "g_pMarketDataManager  is Null  >> " << endl;
		return 0;
	}
	const char* pMarketFontAddr = (const char*)pParam;
	
	g_pMarketDataManager->StartMarketCTP(pMarketFontAddr);
}

DWORD WINAPI StartTradeCTPThread(LPVOID pParam) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "g_pMarketDataManager  is Null  >> " << endl;
		return 0;
	}
	const char* pTradeFrontAddr = (const char*)pParam;
	
	g_pMarketDataManager->StartTradeCTP(pTradeFrontAddr);

}


GenusMarketDataManager::GenusMarketDataManager(void)
{
	m_pJavaVm = NULL;
	m_object = NULL;
	m_pMarketDataSpi = NULL;
	

}

GenusMarketDataManager::~GenusMarketDataManager(void)
{
	
	if (NULL != m_object && NULL != m_pJavaVm)
	{
		JNIEnv* pEnv;
		m_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);
		pEnv->DeleteGlobalRef(m_object);
	}
}

GenusMarketDataManager* GenusMarketDataManager::GetInstance()
{
	if (NULL == g_pMarketDataManager)
	{
		g_pMarketDataManager = new GenusMarketDataManager();
	}
	return g_pMarketDataManager;
}
void GenusMarketDataManager::StartMarketCTP(JNIEnv* pEnv, jobject obj, jobject marketSpiobj, const char* pMarketFontAddr) {
	if (NULL == m_pMarketDataSpi)
	{
		m_pMarketDataSpi = GenusCTPMarketDataSpi::GetInstance(pEnv, obj, marketSpiobj);
	}

	HANDLE hThread;   //线程句柄
	DWORD  threadId;  //线程ID
	hThread = CreateThread(NULL, 0, StartMarketCTPThread, (LPVOID)pMarketFontAddr, 0, &threadId);


}
void GenusMarketDataManager::StartMarketCTP(const char* pMarketFontAddr) {
	
	if (NULL == pMarketFontAddr) {
		cout << "StartMarketCTP Failed: pMarketFontAddr is Null " << pMarketFontAddr << endl;
		return;

	}
	cout << "StartMarketCTP: " << pMarketFontAddr << endl;

	m_pMarketDataSpi->StartMarketCTP(pMarketFontAddr);
}
void GenusMarketDataManager::StartTradeCTP(JNIEnv* pEnv, jobject obj, jobject tradeSpi, const char* pTradeFrontAddr) {
	if (NULL == t_pTradeSpi)
	{
		t_pTradeSpi = GenusCTPTradeSpi::GetInstance(pEnv, obj, tradeSpi);
	}

	HANDLE hThread;   //线程句柄
	DWORD  threadId;  //线程ID
	hThread = CreateThread(NULL, 0, StartTradeCTPThread, (LPVOID)pTradeFrontAddr, 0, &threadId);

}

void GenusMarketDataManager::StartTradeCTP(const char* pTradeFrontAddr) {

	
	if (NULL== pTradeFrontAddr){
		cout << "StartTradeCTP Failed: pTradeFrontAddr is Null " << pTradeFrontAddr << endl;
	return;

	}
	cout << "StartTradeCTP: " << pTradeFrontAddr << endl;
	t_pTradeSpi->StartTradeCTP(pTradeFrontAddr);

}



const char* GenusMarketDataManager::GetMarkeApiVersion() {
	if (NULL == m_pMarketDataSpi)
	{
		m_pMarketDataSpi = new GenusCTPMarketDataSpi();
	
	}
	const char* version= m_pMarketDataSpi->GetApiVersion();
	m_pMarketDataSpi = NULL;
	return version;	
}
const char* GenusMarketDataManager::GetTradeApiVersion() {
	if (NULL == t_pTradeSpi)
	{
		t_pTradeSpi = new GenusCTPTradeSpi();

	}
	const char* version = t_pTradeSpi->GetApiVersion();
	t_pTradeSpi = NULL;
	return version;
	
}

const char* GenusMarketDataManager::GetTradingDay() {
	if (t_pTradeSpi->IsLoginSuccessful())
	{
		return t_pTradeSpi->GetTradingDay();
	}
	else if (m_pMarketDataSpi->IsLoginSuccessful()) {
		return m_pMarketDataSpi->GetTradingDay();
	}
	return "-1";

}

///Trade客户端认证请求
int GenusMarketDataManager::ReqTradeAuthenticate(CThostFtdcReqAuthenticateField* pReqAuthenticateField, int nRequestID) {
	if (NULL == t_pTradeSpi)
	{
		cout << "t_pTradeSpi is Null" << endl;
		return -1;;

	}
	return t_pTradeSpi->ReqAuthenticate(pReqAuthenticateField, nRequestID);
}
///MarketData客户端认证请求
int GenusMarketDataManager::ReqMarketDataAuthenticate(CThostFtdcReqAuthenticateField* pReqAuthenticateField, int nRequestID) {
	if (NULL == t_pTradeSpi)
	{
		cout << "t_pTradeSpi is Null" << endl;
		return -1;;

	}
	cout << "MarketData Track Info ReqAuthenticate" << endl;
	return t_pTradeSpi->ReqAuthenticate(pReqAuthenticateField, nRequestID);
}

///Trade用户登录请求
int GenusMarketDataManager::ReqTradeUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID) {
	if (NULL == t_pTradeSpi )
	{
		cout << "t_pTradeSpi is Null" << endl;
		return -1;;

	}
	return t_pTradeSpi->ReqUserLogin(pReqUserLoginField, nRequestID);
}
///MarketData用户登录请求
int GenusMarketDataManager::ReqMarketDataUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID) {
	if (NULL == m_pMarketDataSpi)
	{
		cout << "m_pMarketDataSpi is Null" << endl;
		return -1;;

	}
	return m_pMarketDataSpi->ReqUserLogin(pReqUserLoginField, nRequestID);
}
///Trade登出请求
int GenusMarketDataManager::ReqTradeUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID) {
	if (NULL == t_pTradeSpi)
	{
		cout << "t_pTradeSpi is Null" << endl;
		return NULL;;
	}
	return t_pTradeSpi->ReqUserLogout(pUserLogout, nRequestID);
}
///MarketData登出请求
int GenusMarketDataManager::ReqMarketDataUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID) {
	if (NULL == m_pMarketDataSpi)
	{
		cout << "m_pMarketDataSpi is Null" << endl;
		return NULL;;
	}
	return m_pMarketDataSpi->ReqUserLogout(pUserLogout, nRequestID);
}



///请求查询合约
int GenusMarketDataManager::ReqQryInstrument(CThostFtdcQryInstrumentField* pQryInstrument, int nRequestID) {
	if (NULL == t_pTradeSpi)
	{
		cout << "t_pTradeSpi is Null" << endl;
		return -1;;
	}
	return t_pTradeSpi->ReqQryInstrument(pQryInstrument, nRequestID);
}
///请求查询行情
int GenusMarketDataManager::ReqQryDepthMarketData(CThostFtdcQryDepthMarketDataField* pQryDepthMarketData, int nRequestID) {
	if (NULL == t_pTradeSpi)
	{
		cout << "m_pUserApi is Null" << endl;
		return -1;
	}
	return t_pTradeSpi->ReqQryDepthMarketData(pQryDepthMarketData, nRequestID);
}


///订阅行情。
int GenusMarketDataManager::SubscribeMarketData(char* ppInstrumentID[], int nCount) {
	if (NULL == m_pMarketDataSpi)
	{
		cout << "m_pMarketDataApi is Null" << endl;
		return -1;;
	}
	return m_pMarketDataSpi->SubscribeMarketData(ppInstrumentID, nCount);
}

///退订行情。
int GenusMarketDataManager::UnSubscribeMarketData(char* ppInstrumentID[], int nCount) {
	if (NULL == m_pMarketDataSpi)
	{
		cout << "m_pMarketDataApi is Null" << endl;
		return NULL;;
	}
	return m_pMarketDataSpi->UnSubscribeMarketData(ppInstrumentID, nCount);
}



