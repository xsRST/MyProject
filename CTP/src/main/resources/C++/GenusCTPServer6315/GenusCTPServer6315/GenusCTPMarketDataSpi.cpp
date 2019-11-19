#include "pch.h"
#include "JNIHandler.h"
#include "GenusCTPMarketDataSpi.h"


GenusCTPMarketDataSpi* g_pMarketDataSpi = NULL;

GenusCTPMarketDataSpi::GenusCTPMarketDataSpi(void)
{
	if (NULL != m_pMarketDataApi)
	{
		m_pMarketDataApi->RegisterSpi(NULL);
		m_pMarketDataApi->Release();
		m_pMarketDataApi = NULL;
	}
	is_connected = false;
	is_login_successful = false;

}

GenusCTPMarketDataSpi::~GenusCTPMarketDataSpi(void)
{
	if (NULL != m_pMarketDataApi)
	{
		m_pMarketDataApi->RegisterSpi(NULL);
		m_pMarketDataApi->Release();
		m_pMarketDataApi = NULL;
	}
}

GenusCTPMarketDataSpi* GenusCTPMarketDataSpi::GetInstance(JNIEnv* pEnv, jobject obj, jobject jmarketSpiobj)
{
	if (NULL == g_pMarketDataSpi)
	{
		g_pMarketDataSpi = new GenusCTPMarketDataSpi();
	}
	JavaVM* pJavaVm = NULL;
	pEnv->GetJavaVM(&pJavaVm);
	jobject jmarketSpi = pEnv->NewGlobalRef(jmarketSpiobj);
	g_pMarketDataSpi->m_pJavaVm = pJavaVm;
	g_pMarketDataSpi->jmarketSpi = jmarketSpi;

	return g_pMarketDataSpi;
}


int  GenusCTPMarketDataSpi::StartMarketCTP(const char* m_strFrontAddr)
{
	
	if (NULL == m_pMarketDataApi)
	{
		m_pMarketDataApi = CThostFtdcMdApi::CreateFtdcMdApi();

	}
	m_pMarketDataApi->RegisterSpi(this);
	m_pMarketDataApi->RegisterFront(const_cast<char*>(m_strFrontAddr));
	m_pMarketDataApi->Init();
	m_pMarketDataApi->Join();
	return 0;
}

const char* GenusCTPMarketDataSpi::GetApiVersion() {
	if (NULL == m_pMarketDataApi)
	{
		m_pMarketDataApi = CThostFtdcMdApi::CreateFtdcMdApi();

	}
	return m_pMarketDataApi->GetApiVersion();
}

const char* GenusCTPMarketDataSpi::GetTradingDay() {
	if (NULL == m_pMarketDataApi)
	{
		cout << "m_pUserApi is Null" << endl;
		return "-1";
	}
	return m_pMarketDataApi->GetTradingDay();
}

bool GenusCTPMarketDataSpi::IsConnected() {
	return is_connected;
}
bool GenusCTPMarketDataSpi::IsLoginSuccessful() {
	return is_login_successful;
}

///用户登录请求
int GenusCTPMarketDataSpi::ReqUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID) {

	if (NULL == m_pMarketDataApi)
	{
		cout << "m_pMarketDataApi is Null" << endl;
		return -1;
	}
	return m_pMarketDataApi->ReqUserLogin(pReqUserLoginField, nRequestID);
}
///登出请求
int GenusCTPMarketDataSpi::ReqUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID) {
	if (NULL == m_pMarketDataApi)
	{
		cout << "m_pMarketDataApi is Null" << endl;
		return -1;
	}
	return m_pMarketDataApi->ReqUserLogout(pUserLogout, nRequestID);
}


///订阅行情。
int GenusCTPMarketDataSpi::SubscribeMarketData(char* ppInstrumentID[], int nCount) {
	if (NULL == m_pMarketDataApi)
	{
		cout << "m_pMarketDataApi is Null" << endl;
		return -1;
	}
	return m_pMarketDataApi->SubscribeMarketData(ppInstrumentID, nCount);
}

///退订行情。
int GenusCTPMarketDataSpi::UnSubscribeMarketData(char* ppInstrumentID[], int nCount) {
	if (NULL == m_pMarketDataApi)
	{
		cout << "m_pMarketDataApi is Null" << endl;
		return -1;
	}
	return m_pMarketDataApi->UnSubscribeMarketData(ppInstrumentID, nCount);
}

///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
void GenusCTPMarketDataSpi::OnFrontConnected() {
	is_connected = true;
	JNIEnv* pEnv;
	m_pJavaVm->AttachCurrentThread((void**)& pEnv, NULL);


	jclass jClass = pEnv->GetObjectClass(jmarketSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnFrontConnected", "()V");
	pEnv->CallVoidMethod(jmarketSpi, methodID_func);
	pEnv->DeleteLocalRef(jClass);
	

}
///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
void GenusCTPMarketDataSpi::OnFrontDisconnected(int nReason) {

	JNIEnv* pEnv;
	m_pJavaVm->AttachCurrentThread((void**)& pEnv, NULL);


	jclass jClass = pEnv->GetObjectClass(jmarketSpi);
	jint jnReason = CJNIHandler::GetInstance()->intTojint(pEnv, nReason);


	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnFrontDisconnected", "(I)V");
	pEnv->CallObjectMethod(jmarketSpi, methodID_func, jnReason);
	pEnv->DeleteLocalRef(jClass);

}

///心跳超时警告。当长时间未收到报文时，该方法被调用。
	///@param nTimeLapse 距离上次接收报文的时间
void GenusCTPMarketDataSpi::OnHeartBeatWarning(int nTimeLapse) {

	JNIEnv* pEnv;
	m_pJavaVm->AttachCurrentThread((void**)& pEnv, NULL);


	jclass jClass = pEnv->GetObjectClass(jmarketSpi);
	jint jnTimeLapse = CJNIHandler::GetInstance()->intTojint(pEnv, nTimeLapse);


	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnHeartBeatWarning", "(I)V");
	pEnv->CallObjectMethod(jmarketSpi, methodID_func, jnTimeLapse);
	pEnv->DeleteLocalRef(jClass);

}

///登录请求响应
void GenusCTPMarketDataSpi::OnRspUserLogin(CThostFtdcRspUserLoginField* pRspUserLogin, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast)
{
	if (NULL == pRspInfo)
	{
		return;
	}
	if (NULL == m_pJavaVm)
	{
		return;
	}
	if (pRspInfo->ErrorID == 0) {
		is_login_successful = true;
	}
	JNIEnv* pEnv;
	m_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);
	jobject jobjUserLoginField=CJNIHandler::GetInstance()->CRspUserLoginToJ(pEnv, pRspUserLogin);

	jobject jobjInfo= CJNIHandler::GetInstance()->CRspInfoToJ(pEnv,pRspInfo);
	jint jRequestID = CJNIHandler::GetInstance()->intTojint(pEnv, nRequestID);
	jboolean jIsLast = CJNIHandler::GetInstance()->boolToJboolean(pEnv, bIsLast);
	jclass jClass = pEnv->GetObjectClass(jmarketSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnRspUserLogin", "(Lcom/genus/ctp/mode/GenusCTPRspUserLoginField;Lcom/genus/ctp/mode/GenusCTPRspInfoField;IZ)V");
	pEnv->CallVoidMethod(jmarketSpi, methodID_func, jobjUserLoginField, jobjInfo, jRequestID, jIsLast);
	pEnv->DeleteLocalRef(jobjUserLoginField);
	pEnv->DeleteLocalRef(jobjInfo);
	pEnv->DeleteLocalRef(jClass);

}
///错误应答
void GenusCTPMarketDataSpi::OnRspError(CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast) {
	if (NULL == pRspInfo)
	{
		return;
	}
	if (NULL == m_pJavaVm)
	{
		return;
	}
	JNIEnv* pEnv;
	m_pJavaVm->AttachCurrentThread((void**)& pEnv, NULL);

	jobject jobjInfo = CJNIHandler::GetInstance()->CRspInfoToJ(pEnv, pRspInfo);
	jint jnRequestID = CJNIHandler::GetInstance()->intTojint(pEnv, nRequestID);
	jboolean jIsLast = CJNIHandler::GetInstance()->boolToJboolean(pEnv, bIsLast);

	jclass jClass = pEnv->GetObjectClass(jmarketSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnRspError", "(Lcom/genus/ctp/mode/GenusCTPRspInfoField;IZ)V");
	pEnv->CallVoidMethod(jmarketSpi, methodID_func, jobjInfo, jnRequestID, jIsLast);
	pEnv->DeleteLocalRef(jClass);
	pEnv->DeleteLocalRef(jobjInfo);


}
///订阅行情应答
void GenusCTPMarketDataSpi::OnRspSubMarketData(CThostFtdcSpecificInstrumentField* pSpecificInstrument, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast) {
	if (NULL == pRspInfo)
	{
		return;
	}
	if (NULL == m_pJavaVm)
	{
		return;
	}
	JNIEnv* pEnv;
	m_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);

	jobject jobjField = CJNIHandler::GetInstance()->CSpecificInstrumentFieldeToJ(pEnv, pSpecificInstrument);
	jobject jobjInfo = CJNIHandler::GetInstance()->CRspInfoToJ(pEnv, pRspInfo);
	jint jnRequestID = CJNIHandler::GetInstance()->intTojint(pEnv, nRequestID);
	jboolean jIsLast = CJNIHandler::GetInstance()->boolToJboolean(pEnv, bIsLast);

	jclass jClass = pEnv->GetObjectClass(jmarketSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnRspSubMarketData", "(Lcom/genus/ctp/mode/GenusCTPSpecificInstrumentField;Lcom/genus/ctp/mode/GenusCTPRspInfoField;IZ)V");
	pEnv->CallVoidMethod(jmarketSpi, methodID_func, jobjField, jobjInfo, jnRequestID, jIsLast);
	pEnv->DeleteLocalRef(jClass);
	pEnv->DeleteLocalRef(jobjInfo);


}
///深度行情通知
void GenusCTPMarketDataSpi::OnRtnDepthMarketData(CThostFtdcDepthMarketDataField* pDepthMarketData) {
	//cout << "Tracker Log OnRtnDepthMarketData" << endl;
	if (NULL == pDepthMarketData)
	{
		return;
	}
	if (NULL == m_pJavaVm)
	{
		return;
	}
	JNIEnv* pEnv;
	m_pJavaVm->AttachCurrentThread((void**)& pEnv, NULL);
	jobject jobjField = CJNIHandler::GetInstance()->CDepthMarketDataFieldeToJ(pEnv, pDepthMarketData);
	//cout << "Tracker Log OnRtnDepthMarketData1" << endl;
	jclass jClass = pEnv->GetObjectClass(jmarketSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnRtnDepthMarketData", "(Lcom/genus/ctp/mode/GenusCTPDepthMarketDataField;)V");
	//cout << "Tracker Log OnRtnDepthMarketData2" << endl;
	pEnv->CallVoidMethod(jmarketSpi, methodID_func, jobjField);
	pEnv->DeleteLocalRef(jClass);
	pEnv->DeleteLocalRef(jobjField);




}
