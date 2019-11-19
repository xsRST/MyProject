#include "pch.h"
#include "JNIHandler.h"
#include "GenusCTPTradeSpi.h"


GenusCTPTradeSpi* g_pTradeSpi = NULL;

GenusCTPTradeSpi::GenusCTPTradeSpi(void)
{
	if (NULL != t_pTradeApi)
	{
		t_pTradeApi->RegisterSpi(NULL);
		t_pTradeApi->Release();
		t_pTradeApi = NULL;
	}
	int m_iRequestID = 0;

}

GenusCTPTradeSpi::~GenusCTPTradeSpi(void)
{
	if (NULL != t_pTradeApi)
	{
		t_pTradeApi->RegisterSpi(NULL);
		t_pTradeApi->Release();
		t_pTradeApi = NULL;
	}
}


GenusCTPTradeSpi* GenusCTPTradeSpi::GetInstance(JNIEnv* pEnv, jobject obj, jobject jtradeSpiobj)
{
	if (NULL == g_pTradeSpi)
	{
		g_pTradeSpi = new GenusCTPTradeSpi();
	}
	JavaVM* pJavaVm = NULL;
	pEnv->GetJavaVM(&pJavaVm);
	jobject jtradeSpii = pEnv->NewGlobalRef(jtradeSpiobj);
	g_pTradeSpi->t_pJavaVm = pJavaVm;
	g_pTradeSpi->jtradeSpi = jtradeSpii;


	return g_pTradeSpi;
}

int  GenusCTPTradeSpi::StartTradeCTP(const char* t_strFrontAddr)
{
	if (NULL == t_pTradeApi)
	{
		t_pTradeApi = CThostFtdcTraderApi::CreateFtdcTraderApi();
	}
	t_pTradeApi->RegisterSpi(this);
	t_pTradeApi->RegisterFront(const_cast<char*>(t_strFrontAddr));
	t_pTradeApi->SubscribePublicTopic(THOST_TERT_RESTART);
	t_pTradeApi->SubscribePrivateTopic(THOST_TERT_RESUME);
	t_pTradeApi->Init();
	t_pTradeApi->Join();
	return 0;
}

const char* GenusCTPTradeSpi::GetApiVersion() {
	
	return t_pTradeApi->GetApiVersion();

}
const char* GenusCTPTradeSpi::GetTradingDay() {
	if (NULL == t_pTradeApi)
	{
		cout << "t_pTradeApi is Null" << endl;
		return "-1";
	}
	return t_pTradeApi->GetTradingDay();
}

bool GenusCTPTradeSpi::IsConnected() {
	return is_connected;
}
bool GenusCTPTradeSpi::IsLoginSuccessful() {
	return is_login_successful;
}


///客户端认证请求
int GenusCTPTradeSpi::ReqAuthenticate(CThostFtdcReqAuthenticateField* pReqAuthenticateField, int nRequestID) {
	if (NULL == t_pTradeApi)
	{
		cout << "m_pUserApi is Null" << endl;
		return NULL;;

	}
	return t_pTradeApi->ReqAuthenticate(pReqAuthenticateField,nRequestID);

}
///用户登录请求
int GenusCTPTradeSpi::ReqUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID) {

	if (NULL == t_pTradeApi)
	{
		cout << "m_pUserApi is Null" << endl;
		return NULL;;

	}
	return t_pTradeApi->ReqUserLogin(pReqUserLoginField, nRequestID);
}
///登出请求
int GenusCTPTradeSpi::ReqUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID) {
	if (NULL == t_pTradeApi)
	{
		cout << "m_pUserApi is Null" << endl;
		return NULL;;
	}
	return t_pTradeApi->ReqUserLogout(pUserLogout, nRequestID);
}
///请求查询合约
int GenusCTPTradeSpi::ReqQryInstrument(CThostFtdcQryInstrumentField* pQryInstrument, int nRequestID) {
	if (NULL == t_pTradeApi)
	{
		cout << "t_pTradeApi is Null" << endl;
		return -1;;

	}
	return t_pTradeApi->ReqQryInstrument(pQryInstrument, nRequestID);

}
///请求查询行情
int GenusCTPTradeSpi::ReqQryDepthMarketData(CThostFtdcQryDepthMarketDataField* pQryDepthMarketData, int nRequestID) {
	if (NULL == t_pTradeApi)
	{
		cout << "t_pTradeApi is Null" << endl;
		return -1;;
	}
	return t_pTradeApi->ReqQryDepthMarketData(pQryDepthMarketData, nRequestID);
}

///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
void GenusCTPTradeSpi::OnFrontConnected() {

	is_connected = true;
	JNIEnv* pEnv;
	t_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);


	jclass jClass = pEnv->GetObjectClass(jtradeSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnFrontConnected", "()V");
	pEnv->CallObjectMethod(jtradeSpi, methodID_func);
	pEnv->DeleteLocalRef(jClass);

}
///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
void GenusCTPTradeSpi::OnFrontDisconnected(int nReason) {

	JNIEnv* pEnv;
	t_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);


	jclass jClass = pEnv->GetObjectClass(jtradeSpi);
	jint jnReason = CJNIHandler::GetInstance()->intTojint(pEnv, nReason);


	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnFrontDisconnected", "(I)V");
	pEnv->CallObjectMethod(jtradeSpi, methodID_func, jnReason);
	pEnv->DeleteLocalRef(jClass);

}

///心跳超时警告。当长时间未收到报文时，该方法被调用。
	///@param nTimeLapse 距离上次接收报文的时间
void GenusCTPTradeSpi::OnHeartBeatWarning(int nTimeLapse) {

	JNIEnv* pEnv;
	t_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);


	jclass jClass = pEnv->GetObjectClass(jtradeSpi);
	jint jnTimeLapse = CJNIHandler::GetInstance()->intTojint(pEnv, nTimeLapse);


	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnHeartBeatWarning", "(I)V");
	pEnv->CallObjectMethod(jtradeSpi, methodID_func, jnTimeLapse);
	pEnv->DeleteLocalRef(jClass);

}

///客户端认证响应
void GenusCTPTradeSpi::OnRspAuthenticate(CThostFtdcRspAuthenticateField* pRspAuthenticateField, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast) {

	if (NULL == pRspInfo)
	{
		return;
	}
	if (NULL == t_pJavaVm)
	{
		return;
	}
	//cout<<"Tracker Log OnRspAuthenticate"<<endl;
	JNIEnv* pEnv;
	t_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);
	jobject jobjField = CJNIHandler::GetInstance()->CRspAuthenticateToJ(pEnv, pRspAuthenticateField);
	jobject jobjInfo = CJNIHandler::GetInstance()->CRspInfoToJ(pEnv, pRspInfo);
	jint jRequestID = CJNIHandler::GetInstance()->intTojint(pEnv, nRequestID);
	jboolean jIsLast = CJNIHandler::GetInstance()->boolToJboolean(pEnv, bIsLast);

	jclass jClass = pEnv->GetObjectClass(jtradeSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnRspAuthenticate", "(Lcom/genus/ctp/mode/GenusCTPRspAuthenticateField;Lcom/genus/ctp/mode/GenusCTPRspInfoField;IZ)V");
	pEnv->CallObjectMethod(jtradeSpi, methodID_func, jobjField, jobjInfo, jRequestID, jIsLast);
	pEnv->DeleteLocalRef(jobjField);
	pEnv->DeleteLocalRef(jobjInfo);
	pEnv->DeleteLocalRef(jClass);



}


///登录请求响应
void GenusCTPTradeSpi::OnRspUserLogin(CThostFtdcRspUserLoginField* pRspUserLogin, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast)
{
	if (pRspInfo->ErrorID == 0) {
		is_login_successful = true;
	}
	if (NULL == pRspInfo)
	{
		return;
	}
	if (NULL == t_pJavaVm)
	{
		return;
	}

	//cout << "Tracker Log OnRspUserLogin" << endl;
	JNIEnv* pEnv;
	t_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);
	jobject jobjField = CJNIHandler::GetInstance()->CRspUserLoginToJ(pEnv, pRspUserLogin);

	jobject jobjInfo = CJNIHandler::GetInstance()->CRspInfoToJ(pEnv, pRspInfo);
	jint jRequestID = CJNIHandler::GetInstance()->intTojint(pEnv, nRequestID);
	jboolean jIsLast = CJNIHandler::GetInstance()->boolToJboolean(pEnv, bIsLast);
	jclass jClass = pEnv->GetObjectClass(jtradeSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnRspUserLogin", "(Lcom/genus/ctp/mode/GenusCTPRspUserLoginField;Lcom/genus/ctp/mode/GenusCTPRspInfoField;IZ)V");
	pEnv->CallVoidMethod(jtradeSpi, methodID_func, jobjField, jobjInfo, jRequestID, jIsLast);
	pEnv->DeleteLocalRef(jobjField);
	pEnv->DeleteLocalRef(jobjInfo);
	pEnv->DeleteLocalRef(jClass);
}
///错误应答
void GenusCTPTradeSpi::OnRspError(CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast) {
	//cout << "Tracker Log OnRspError" << endl;
	if (NULL == pRspInfo)
	{
		return;
	}
	if (NULL == t_pJavaVm)
	{
		return;
	}
	JNIEnv* pEnv;
	t_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);

	jobject jobjInfo = CJNIHandler::GetInstance()->CRspInfoToJ(pEnv, pRspInfo);
	jint jnRequestID = CJNIHandler::GetInstance()->intTojint(pEnv, nRequestID);
	jboolean jIsLast = CJNIHandler::GetInstance()->boolToJboolean(pEnv, bIsLast);

	jclass jClass = pEnv->GetObjectClass(jtradeSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnRspError", "(Lcom/genus/ctp/mode/GenusCTPRspInfoField;IZ)V");
	pEnv->CallVoidMethod(jtradeSpi, methodID_func, jobjInfo, jnRequestID, jIsLast);
	pEnv->DeleteLocalRef(jClass);
	pEnv->DeleteLocalRef(jobjInfo);
}

///请求查询合约响应
void GenusCTPTradeSpi::OnRspQryInstrument(CThostFtdcInstrumentField* pInstrument, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast) {
	//cout << "Tracker Log OnRspQryInstrument" << endl;
	if (NULL == t_pJavaVm)
	{
		return;
	}
	JNIEnv* pEnv;
	t_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);
	jobject jobjField = CJNIHandler::GetInstance()->CInstrumentFieldeToJ(pEnv, pInstrument);
	jobject jobjInfo = CJNIHandler::GetInstance()->CRspInfoToJ(pEnv, pRspInfo);
	jint jnRequestID = CJNIHandler::GetInstance()->intTojint(pEnv, nRequestID);
	jboolean jIsLast = CJNIHandler::GetInstance()->boolToJboolean(pEnv, bIsLast);
	jclass jClass = pEnv->GetObjectClass(jtradeSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnRspQryInstrument", "(Lcom/genus/ctp/mode/GenusCTPInstrumentField;Lcom/genus/ctp/mode/GenusCTPRspInfoField;IZ)V");
	pEnv->CallVoidMethod(jtradeSpi, methodID_func, jobjField, jobjInfo, jnRequestID, jIsLast);
	pEnv->DeleteLocalRef(jClass);
	pEnv->DeleteLocalRef(jobjInfo);
	pEnv->DeleteLocalRef(jobjField);
}

///请求查询行情响应
void GenusCTPTradeSpi::OnRspQryDepthMarketData(CThostFtdcDepthMarketDataField* pDepthMarketData, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast){

//cout << "Tracker Log OnRspQryInstrument" << endl;
	if (NULL == t_pJavaVm)
	{
		return;
	}
	JNIEnv* pEnv;
	t_pJavaVm->AttachCurrentThread((void**)&pEnv, NULL);
	jobject jobjField = CJNIHandler::GetInstance()->CDepthMarketDataFieldeToJ(pEnv, pDepthMarketData);
	jobject jobjInfo = CJNIHandler::GetInstance()->CRspInfoToJ(pEnv, pRspInfo);
	jint jnRequestID = CJNIHandler::GetInstance()->intTojint(pEnv, nRequestID);
	jboolean jIsLast = CJNIHandler::GetInstance()->boolToJboolean(pEnv, bIsLast);
	jclass jClass = pEnv->GetObjectClass(jtradeSpi);
	jmethodID methodID_func = pEnv->GetMethodID(jClass, "OnRspQryDepthMarketData", "(Lcom/genus/ctp/mode/GenusCTPDepthMarketDataField;Lcom/genus/ctp/mode/GenusCTPRspInfoField;IZ)V");
	pEnv->CallVoidMethod(jtradeSpi, methodID_func, jobjField, jobjInfo, jnRequestID, jIsLast);
	pEnv->DeleteLocalRef(jClass);
	pEnv->DeleteLocalRef(jobjInfo);
	pEnv->DeleteLocalRef(jobjField);
}


