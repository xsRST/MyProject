#include "pch.h"
#include "JNIHandler.h"

#include "com_genus_ctp_impl_GenusCTPServerImpl.h"

#include "GenusMarketDataManager.h"

extern GenusMarketDataManager* g_pMarketDataManager;

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    StartCTPTradeServer
 * Signature: (Lcom/genus/ctp/GenusCTPTradeCallback;Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_StartCTPTradeServer
(JNIEnv* pEnv, jobject obj, jobject tradeSpi, jstring tradeFontAddr) {
	if (NULL == g_pMarketDataManager)
	{
		g_pMarketDataManager = GenusMarketDataManager::GetInstance();
	}
	//cout << "-TraderData: Start Now" << endl;
	JavaVM* pJavaVm = NULL;
	pEnv->GetJavaVM(&pJavaVm);
	jobject object = pEnv->NewGlobalRef(obj);
	
	char* strTadeFontAddr = CJNIHandler::GetInstance()->jstringToChar(pEnv, tradeFontAddr);
	g_pMarketDataManager->StartTradeCTP(pEnv, obj, tradeSpi, strTadeFontAddr);
	return;
}

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    StartCTPMarketServer
 * Signature: (Lcom/genus/ctp/GenusCTPMarketDataCallback;Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_StartCTPMarketServer
(JNIEnv* pEnv, jobject obj, jobject marketSpi, jstring marketFontAddr) {
	if (NULL == g_pMarketDataManager)
	{
		g_pMarketDataManager = GenusMarketDataManager::GetInstance();
	}
	JavaVM* pJavaVm = NULL;
	pEnv->GetJavaVM(&pJavaVm);
	jobject object = pEnv->NewGlobalRef(obj);
	cout << "-MarketData: Start Now" << endl;
	char* strMarketFontAddr = CJNIHandler::GetInstance()->jstringToChar(pEnv, marketFontAddr);

	g_pMarketDataManager->StartMarketCTP(pEnv, obj,  marketSpi, strMarketFontAddr);
	return;

}



/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    StopCTPServer
 * Signature:
 */
JNIEXPORT void JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_StopCTPServer
(JNIEnv* pEnv, jobject obj ) {
	cout << "StopCTPServer" << endl;
	exit(0);
}

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    GetApiVersion
 * Signature:
 */
JNIEXPORT jstring JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_GetApiVersion
(JNIEnv* pEnv, jobject obj) {
	if (NULL == g_pMarketDataManager)
	{
		g_pMarketDataManager = GenusMarketDataManager::GetInstance();
	}
	const char* markeApiVersion =g_pMarketDataManager->GetMarkeApiVersion();
	string markeApiVersionStr(markeApiVersion);
	const char* tradeApiVersion = g_pMarketDataManager->GetTradeApiVersion();
	string tradeApiVersionStr(tradeApiVersion);
	string apiVersionInfo = "markeApiVersion: "+markeApiVersionStr +". tradeApiVersion:"+ tradeApiVersionStr;
	jstring jApiVersionInfo=CJNIHandler::GetInstance()->charTojstring(pEnv, apiVersionInfo.c_str());
	return jApiVersionInfo;
	
}


/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    GetTradingDay
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_GetTradingDay
(JNIEnv* pEnv, jobject obj) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->charTojstring(pEnv, "-1");
	}
	else {
		const char* c_tradingday = g_pMarketDataManager->GetTradingDay();
		string tradingday(c_tradingday);
		jstring jApTradingDay = CJNIHandler::GetInstance()->charTojstring(pEnv, tradingday.c_str());
		return jApTradingDay;
	}
}

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    ReqAuthenticate
 * Signature: (Lcom/genus/ctp/mode/GenusCTPReqAuthenticateField;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_ReqTradeAuthenticate
(JNIEnv* pEnv, jobject obj, jobject reqAuthenticate, jint jRequestID) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}
	CThostFtdcReqAuthenticateField pReqAuthenticateField = CJNIHandler::GetInstance()->JReqAuthenticateToC(pEnv, reqAuthenticate);
	int nRequestID = CJNIHandler::GetInstance()->jintToint(pEnv, jRequestID);
	return g_pMarketDataManager->ReqTradeAuthenticate(&pReqAuthenticateField, nRequestID);
}
/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    ReqAuthenticate
 * Signature: (Lcom/genus/ctp/mode/GenusCTPReqAuthenticateField;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_ReqMarketDataAuthenticate
(JNIEnv* pEnv, jobject obj, jobject reqAuthenticate, jint jRequestID) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}
	CThostFtdcReqAuthenticateField pReqAuthenticateField = CJNIHandler::GetInstance()->JReqAuthenticateToC(pEnv, reqAuthenticate);
	int nRequestID = CJNIHandler::GetInstance()->jintToint(pEnv, jRequestID);
	return g_pMarketDataManager->ReqMarketDataAuthenticate(&pReqAuthenticateField, nRequestID);
}

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    ReqUserLogin
 * Signature: (Lcom/genus/ctp/mode/GenusCTPReqUserLoginField;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_ReqTradeUserLogin
(JNIEnv* pEnv, jobject obj, jobject reqUserLogin, jint jRequestID) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}
	CThostFtdcReqUserLoginField pReqUserLoginField = CJNIHandler::GetInstance()->JReqUserLoginToC(pEnv, reqUserLogin);
	int nRequestID = CJNIHandler::GetInstance()->jintToint(pEnv, jRequestID);
	return g_pMarketDataManager->ReqTradeUserLogin(&pReqUserLoginField, nRequestID);

}/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    ReqUserLogin
 * Signature: (Lcom/genus/ctp/mode/GenusCTPReqUserLoginField;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_ReqMarketDataUserLogin
(JNIEnv* pEnv, jobject obj, jobject reqUserLogin, jint jRequestID) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}
	CThostFtdcReqUserLoginField pReqUserLoginField = CJNIHandler::GetInstance()->JReqUserLoginToC(pEnv, reqUserLogin);
	int nRequestID = CJNIHandler::GetInstance()->jintToint(pEnv, jRequestID);
	return g_pMarketDataManager->ReqMarketDataUserLogin(&pReqUserLoginField, nRequestID);

}

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    ReqUserLogout
 * Signature: (Lcom/genus/ctp/mode/GenusCTPReqUserLogoutField;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_ReqTradeUserLogout
(JNIEnv* pEnv, jobject obj, jobject reqUserLogout, jint jRequestID) {

	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}
	CThostFtdcUserLogoutField pReqUserLoginField = CJNIHandler::GetInstance()->JReqUserLogoutToC(pEnv, reqUserLogout);
	int nRequestID = CJNIHandler::GetInstance()->jintToint(pEnv, jRequestID);
	return g_pMarketDataManager->ReqTradeUserLogout(&pReqUserLoginField, nRequestID);
}
/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    ReqUserLogout
 * Signature: (Lcom/genus/ctp/mode/GenusCTPReqUserLogoutField;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_ReqMarketDataUserLogout
(JNIEnv* pEnv, jobject obj, jobject reqUserLogout, jint jRequestID) {

	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}
	CThostFtdcUserLogoutField pReqUserLoginField = CJNIHandler::GetInstance()->JReqUserLogoutToC(pEnv, reqUserLogout);
	int nRequestID = CJNIHandler::GetInstance()->jintToint(pEnv, jRequestID);
	return g_pMarketDataManager->ReqMarketDataUserLogout(&pReqUserLoginField, nRequestID);
}

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    ReqQryInstrument
 * Signature: (Lcom/genus/ctp/mode/GenusCTPQryInstrumentField;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_ReqQryInstrument
(JNIEnv* pEnv, jobject obj, jobject qryInstrumentField, jint jRequestID) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}
	CThostFtdcQryInstrumentField pReqUserLoginField = CJNIHandler::GetInstance()->JQryInstrumentToC(pEnv, qryInstrumentField);
	int nRequestID = CJNIHandler::GetInstance()->jintToint(pEnv, jRequestID);
	//cout << "Tracker Log ReqQryInstrument" << endl;
	return g_pMarketDataManager->ReqQryInstrument(&pReqUserLoginField, nRequestID);
}

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    ReqQryDepthMarketData
 * Signature: (Lcom/genus/ctp/mode/GenusCTPQryDepthMarketDataField;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_ReqQryDepthMarketData
(JNIEnv* pEnv, jobject obj, jobject qryDepthMarketData, jint jRequestID) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}
	CThostFtdcQryDepthMarketDataField pReqUserLoginField = CJNIHandler::GetInstance()->JQryDepthMarketDataToC(pEnv, qryDepthMarketData);
	int nRequestID = CJNIHandler::GetInstance()->jintToint(pEnv, jRequestID);
	return g_pMarketDataManager->ReqQryDepthMarketData(&pReqUserLoginField, nRequestID);
}

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    SubscribeMarketData
 * Signature: (Ljava/util/List;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_SubscribeMarketData
(JNIEnv* pEnv, jobject obj, jobject instrumentIDs, jint jcount) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}
	char** pInstrumentIDs = CJNIHandler::GetInstance()->JArrayListStrToC(pEnv, instrumentIDs);

	int count = CJNIHandler::GetInstance()->jintToint(pEnv, jcount);
	return g_pMarketDataManager->SubscribeMarketData(pInstrumentIDs, count);
}

/*
 * Class:     com_genus_ctp_impl_GenusCTPServerImpl
 * Method:    UnSubscribeMarketData
 * Signature: (Ljava/util/List;I)I
 */
JNIEXPORT jint JNICALL Java_com_genus_ctp_impl_GenusCTPServerImpl_UnSubscribeMarketData
(JNIEnv* pEnv, jobject obj, jobject instrumentIDs, jint jcount) {
	if (NULL == g_pMarketDataManager)
	{
		cout << "please StartServer First or checking " << endl;
		return CJNIHandler::GetInstance()->intTojint(pEnv, -1);
	}


	char** pInstrumentIDs = CJNIHandler::GetInstance()->JArrayListStrToC(pEnv, instrumentIDs);

	int count = CJNIHandler::GetInstance()->jintToint(pEnv, jcount);
	return g_pMarketDataManager->UnSubscribeMarketData(pInstrumentIDs, count);
}





