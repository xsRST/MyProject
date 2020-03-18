#include "pch.h"

#include "JNIHandler.h"

CJNIHandler* m_pJNIHandler = NULL;
CJNIHandler::CJNIHandler(void)
{

}

CJNIHandler::~CJNIHandler(void)
{
}

CJNIHandler* CJNIHandler::GetInstance()
{
	if (NULL == m_pJNIHandler)
	{
		m_pJNIHandler = new CJNIHandler();
	}
	return m_pJNIHandler;
}

jstring CJNIHandler::charTojstring(JNIEnv* pEnv, const char* pPat)
{

	if (NULL == pEnv || NULL == pPat)
	{
		return (jstring)"";
	}
	jclass strClass = pEnv->FindClass("Ljava/lang/String;");
	jmethodID ctorID = pEnv->GetMethodID(strClass, "<init>", "([BLjava/lang/String;)V");
	jbyteArray bytes = pEnv->NewByteArray(strlen(pPat));
	pEnv->SetByteArrayRegion(bytes, 0, strlen(pPat), (jbyte*)pPat);
	jstring encoding = pEnv->NewStringUTF("GB2312");
	jstring jStringRtn = (jstring)pEnv->NewObject(strClass, ctorID, bytes, encoding);
	pEnv->DeleteLocalRef(strClass);
	pEnv->DeleteLocalRef(encoding);
	pEnv->DeleteLocalRef(bytes);
	return jStringRtn;
}

char* CJNIHandler::jstringToChar(JNIEnv* pEnv, jstring jStr) {
	int length = (pEnv)->GetStringLength(jStr);
	const jchar* jcstr = (pEnv)->GetStringChars(jStr, 0);
	char* rtn = (char*)malloc(length * 2 + 1);
	int size = 0;
	size = WideCharToMultiByte(CP_ACP, 0, (LPCWSTR)jcstr, length, rtn,
		(length * 2 + 1), NULL, NULL);
	if (size <= 0)
		return NULL;
	(pEnv)->ReleaseStringChars(jStr, jcstr);
	rtn[size] = 0;
	return rtn;
}
std::string CJNIHandler::jstringTostr(JNIEnv* env, jstring jstr)
{
	char* rtn = jstringToChar(env, jstr);
	string str(rtn);
	return   str;
}


jchar  CJNIHandler::charTojchar(JNIEnv* pEnv, char pPat)
{
	return   (jchar)pPat;
}

char  CJNIHandler::jcharTochar(JNIEnv* pEnv, char pPat)
{
	return   (char)pPat;
}


jint CJNIHandler::intTojint(JNIEnv* pEnv, int  pPat)
{
	if (NULL == pEnv || 0 == pPat)
	{
		return 0;
	}
	return (jint)pPat;
}

jlong CJNIHandler::intTojlong(JNIEnv* pEnv, int  pPat)
{
	if (NULL == pEnv || 0 == pPat)
	{
		return 0;
	}
	return (jlong)pPat;
}

int CJNIHandler::jintToint(JNIEnv* pEnv, jint jStr)
{
	if (NULL == pEnv || 0 == jStr)
	{
		return 0;
	}
	return (int)jStr;
}
jboolean CJNIHandler::boolToJboolean(JNIEnv* pEnv, bool  pPat)
{
	return pPat ? JNI_TRUE : JNI_FALSE;
}

bool CJNIHandler::jbooleanTobool(JNIEnv* pEnv, jboolean  pPat)
{
	return pPat == JNI_TRUE;

}

jdouble CJNIHandler::doubleTojdouble(JNIEnv* pEnv, double  pPat)
{
	if (NULL == pEnv || 0 == pPat)
	{
		return 0;
	}
	return (jdouble)pPat;
}

double CJNIHandler::jdoubleTodouble(JNIEnv* pEnv, jdouble  pPat)
{
	if (NULL == pEnv || 0 == pPat)
	{
		return 0;
	}
	return (double)pPat;

}



map<char*, char*> CJNIHandler::JMaptoCmap(JNIEnv* pEnv, jobject jobj) {
	std::map<char*, char*> cmap;
	jclass jMapclass = pEnv->FindClass("java/util/HashMap");
	jmethodID jKeysetmid = pEnv->GetMethodID(jMapclass, "keySet", "()Ljava/util/Set;");
	jmethodID jGetmid = pEnv->GetMethodID(jMapclass, "get", "(Ljava/lang/Object;)Ljava/lang/Object;");
	jobject jSetkey = pEnv->CallObjectMethod(jobj, jKeysetmid);
	jclass jSetclass = pEnv->FindClass("java/util/Set");
	jmethodID jToArrayMid = pEnv->GetMethodID(jSetclass, "toArray", "()[Ljava/lang/Object;");
	jobjectArray jJobArray = (jobjectArray)pEnv->CallObjectMethod(jSetkey, jToArrayMid);
	if (jJobArray == NULL) {
		return cmap;
	}
	jsize arraysize = pEnv->GetArrayLength(jJobArray);
	int i = 0;
	for (i = 0; i < arraysize; i++) {
		jstring jkey = (jstring)pEnv->GetObjectArrayElement(jJobArray, i);
		jstring jvalue = (jstring)pEnv->CallObjectMethod(jobj, jGetmid, jkey);
		char* key = (char*)pEnv->GetStringUTFChars(jkey, 0);
		char* value = (char*)pEnv->GetStringUTFChars(jvalue, 0);
		cmap[key] = value;
		pEnv->DeleteLocalRef(jkey);
		pEnv->DeleteLocalRef(jvalue);
	}
	pEnv->DeleteLocalRef(jMapclass);
	pEnv->DeleteLocalRef(jSetkey);
	pEnv->DeleteLocalRef(jSetclass);
	pEnv->DeleteLocalRef(jJobArray);
	return cmap;
}



char** CJNIHandler::JArrayListStrToC(JNIEnv* pEnv, jobject jobj) {
	//cout << "Track Info JArrayListStrToC" << endl;
	jclass cls_arraylist = pEnv->GetObjectClass(jobj);
	jmethodID arraylist_get = pEnv->GetMethodID(cls_arraylist, "get", "(I)Ljava/lang/Object;");
	jmethodID arraylist_size = pEnv->GetMethodID(cls_arraylist, "size", "()I");
	;
	jint len = pEnv->CallIntMethod(jobj, arraylist_size);
	int i;
	char** presult = (char**)malloc(len * sizeof(char*));

	for (i = 0; i < len; i++) {
		jstring jstr = (jstring)pEnv->CallObjectMethod(jobj, arraylist_get, i);

		presult[i] = jstringToChar(pEnv, jstr);
	}
	return presult;
}


CThostFtdcReqAuthenticateField CJNIHandler::JReqAuthenticateToC(JNIEnv* pEnv, jobject jobj) {
	//cout << "Track Info JReqAuthenticateToC" << endl;
	jclass reqClz = pEnv->GetObjectClass(jobj);
	jfieldID jfieldBrokerID = pEnv->GetFieldID(reqClz, "BrokerID", "Ljava/lang/String;");
	jfieldID jfieldUserID = pEnv->GetFieldID(reqClz, "UserID", "Ljava/lang/String;");
	jfieldID jfieldUserProductInfo = pEnv->GetFieldID(reqClz, "UserProductInfo", "Ljava/lang/String;");
	jfieldID  jfieldAuthCode = pEnv->GetFieldID(reqClz, "AuthCode", "Ljava/lang/String;");
	jfieldID jfieldAppID = pEnv->GetFieldID(reqClz, "AppID", "Ljava/lang/String;");

	jstring jBrokerID = (jstring)pEnv->GetObjectField(jobj, jfieldBrokerID);
	jstring jUserID = (jstring)pEnv->GetObjectField(jobj, jfieldUserID);
	jstring jUserProductInfo = (jstring)pEnv->GetObjectField(jobj, jfieldUserProductInfo);
	jstring jAuthCode = (jstring)pEnv->GetObjectField(jobj, jfieldAuthCode);
	jstring jAppID = (jstring)pEnv->GetObjectField(jobj, jfieldAppID);

	pEnv->DeleteLocalRef(reqClz);
	CThostFtdcReqAuthenticateField field;
	memset(&field, 0, sizeof(field));
	if (jBrokerID != NULL) {
		char* BrokerID = jstringToChar(pEnv, jBrokerID);
		strcpy_s(field.BrokerID, strlen(BrokerID) + 1, BrokerID);
		pEnv->DeleteLocalRef(jBrokerID);

	}
	if (jUserID != NULL) {
		char* UserID = jstringToChar(pEnv, jUserID);
		strcpy_s(field.UserID, strlen(UserID) + 1, UserID);
		pEnv->DeleteLocalRef(jUserID);
	}
	if (jUserProductInfo != NULL) {
		char* UserProductInfo = jstringToChar(pEnv, jUserProductInfo);
		strcpy_s(field.UserProductInfo, strlen(UserProductInfo) + 1, UserProductInfo);
		pEnv->DeleteLocalRef(jUserProductInfo);

	}
	if (jAuthCode != NULL) {

		char* AuthCode = jstringToChar(pEnv, jAuthCode);
		//cout << "Track Info JReqAuthenticateToC AuthCode >> " << AuthCode << endl;
		strcpy_s(field.AuthCode, strlen(AuthCode) + 1, AuthCode);
		pEnv->DeleteLocalRef(jAuthCode);
	}
	if (jAppID != NULL) {

		char* AppID = jstringToChar(pEnv, jAppID);
		strcpy_s(field.AppID, strlen(AppID) + 1, AppID);
		//cout << "Track Info JReqAuthenticateToC AppID >> " << AppID << endl;
		pEnv->DeleteLocalRef(jAppID);
	}
	//cout << "Track Info JReqAuthenticateToC End  "  << endl;
	return field;
}


CThostFtdcReqUserLoginField CJNIHandler::JReqUserLoginToC(JNIEnv* pEnv, jobject jobj) {
	//cout << "Track Info JReqUserLoginToC" << endl;

	jclass reqClz = pEnv->GetObjectClass(jobj);
	jfieldID jfieldTradingDay = pEnv->GetFieldID(reqClz, "TradingDay", "Ljava/lang/String;");
	jfieldID jfieldBrokerID = pEnv->GetFieldID(reqClz, "BrokerID", "Ljava/lang/String;");
	jfieldID jfieldUserID = pEnv->GetFieldID(reqClz, "UserID", "Ljava/lang/String;");
	jfieldID jfieldPassword = pEnv->GetFieldID(reqClz, "Password", "Ljava/lang/String;");
	jfieldID jfieldUserProductInfo = pEnv->GetFieldID(reqClz, "UserProductInfo", "Ljava/lang/String;");
	jfieldID jfieldInterfaceProductInfo = pEnv->GetFieldID(reqClz, "InterfaceProductInfo", "Ljava/lang/String;");
	jfieldID jfieldProtocolInfo = pEnv->GetFieldID(reqClz, "ProtocolInfo", "Ljava/lang/String;");
	jfieldID jfieldMacAddress = pEnv->GetFieldID(reqClz, "MacAddress", "Ljava/lang/String;");
	jfieldID jfieldOneTimePassword = pEnv->GetFieldID(reqClz, "OneTimePassword", "Ljava/lang/String;");
	jfieldID jfieldClientIPAddress = pEnv->GetFieldID(reqClz, "ClientIPAddress", "Ljava/lang/String;");
	jfieldID jfieldUserLoginRemark = pEnv->GetFieldID(reqClz, "LoginRemark", "Ljava/lang/String;");
	jfieldID jfieldUserClientIPPort = pEnv->GetFieldID(reqClz, "ClientIPPort", "I");


	jstring jTradingDay = (jstring)pEnv->GetObjectField(jobj, jfieldTradingDay);
	jstring jBrokerID = (jstring)pEnv->GetObjectField(jobj, jfieldBrokerID);
	jstring jUserID = (jstring)pEnv->GetObjectField(jobj, jfieldUserID);
	jstring jPassword = (jstring)pEnv->GetObjectField(jobj, jfieldPassword);
	jstring jUserProductInfo = (jstring)pEnv->GetObjectField(jobj, jfieldUserProductInfo);
	jstring jInterfaceProductInfo = (jstring)pEnv->GetObjectField(jobj, jfieldInterfaceProductInfo);
	jstring jProtocolInfo = (jstring)pEnv->GetObjectField(jobj, jfieldProtocolInfo);
	jstring jMacAddress = (jstring)pEnv->GetObjectField(jobj, jfieldMacAddress);
	jstring jOneTimePassword = (jstring)pEnv->GetObjectField(jobj, jfieldOneTimePassword);
	jstring jClientIPAddress = (jstring)pEnv->GetObjectField(jobj, jfieldClientIPAddress);
	jstring jLoginRemark = (jstring)pEnv->GetObjectField(jobj, jfieldUserLoginRemark);
	jint jClientIPPort = pEnv->GetIntField(jobj, jfieldUserClientIPPort);

	pEnv->DeleteLocalRef(reqClz);
	CThostFtdcReqUserLoginField field;
	memset(&field, 0, sizeof(field));
	if (jTradingDay != NULL) {
		char* TradingDay = jstringToChar(pEnv, jTradingDay);
		strcpy_s(field.TradingDay, strlen(TradingDay) + 1, TradingDay);
		pEnv->DeleteLocalRef(jTradingDay);
	}
	if (jBrokerID != NULL) {
		char* BrokerID = jstringToChar(pEnv, jBrokerID);
		strcpy_s(field.BrokerID, strlen(BrokerID) + 1, BrokerID);
		pEnv->DeleteLocalRef(jBrokerID);

	}
	if (jUserID != NULL) {
		char* UserID = jstringToChar(pEnv, jUserID);
		strcpy_s(field.UserID, strlen(UserID) + 1, UserID);
		pEnv->DeleteLocalRef(jUserID);
	}
	if (jPassword != NULL) {
		char* Password = jstringToChar(pEnv, jPassword);
		strcpy_s(field.Password, strlen(Password) + 1, Password);
		pEnv->DeleteLocalRef(jPassword);
	}
	if (jUserProductInfo != NULL) {
		char* UserProductInfo = jstringToChar(pEnv, jUserProductInfo);
		strcpy_s(field.UserProductInfo, strlen(UserProductInfo) + 1, UserProductInfo);
		pEnv->DeleteLocalRef(jUserProductInfo);
	}
	if (jInterfaceProductInfo != NULL) {
		char* InterfaceProductInfo = jstringToChar(pEnv, jInterfaceProductInfo);
		strcpy_s(field.InterfaceProductInfo, strlen(InterfaceProductInfo) + 1, InterfaceProductInfo);
		pEnv->DeleteLocalRef(jInterfaceProductInfo);
	}
	if (jProtocolInfo != NULL) {
		char* ProtocolInfo = jstringToChar(pEnv, jProtocolInfo);
		strcpy_s(field.ProtocolInfo, strlen(ProtocolInfo) + 1, ProtocolInfo);
		pEnv->DeleteLocalRef(jProtocolInfo);
	}
	if (jMacAddress != NULL) {
		char* MacAddress = jstringToChar(pEnv, jMacAddress);
		strcpy_s(field.MacAddress, strlen(MacAddress) + 1, MacAddress);
		pEnv->DeleteLocalRef(jMacAddress);
	}
	if (jOneTimePassword != NULL) {
		char* OneTimePassword = jstringToChar(pEnv, jOneTimePassword);
		strcpy_s(field.OneTimePassword, strlen(OneTimePassword) + 1, OneTimePassword);
		pEnv->DeleteLocalRef(jOneTimePassword);
	}

	if (jClientIPAddress != NULL) {
		char* ClientIPAddress = jstringToChar(pEnv, jClientIPAddress);
		strcpy_s(field.ClientIPAddress, strlen(ClientIPAddress) + 1, ClientIPAddress);
		pEnv->DeleteLocalRef(jClientIPAddress);
	}

	if (jLoginRemark != NULL) {
		char* LoginRemark = jstringToChar(pEnv, jLoginRemark);
		strcpy_s(field.LoginRemark, strlen(LoginRemark) + 1, LoginRemark);
		pEnv->DeleteLocalRef(jLoginRemark);
	}

	if (jClientIPPort != NULL || jClientIPPort != 0) {
		int ClientIPPort = jintToint(pEnv, jClientIPPort);
		field.ClientIPPort = ClientIPPort;
	}


	return field;
}





CThostFtdcUserLogoutField CJNIHandler::JReqUserLogoutToC(JNIEnv* pEnv, jobject jobj) {
	//cout << "Track Info JReqUserLogoutToC" << endl;

	CThostFtdcUserLogoutField field;
	memset(&field, 0, sizeof(field));


	return field;
}

CThostFtdcQryInstrumentField CJNIHandler::JQryInstrumentToC(JNIEnv* pEnv, jobject jobj) {

	//cout << "Track Info JQryInstrumentToC" << endl;
	CThostFtdcQryInstrumentField field;
	memset(&field, 0, sizeof(field));


	return field;
}

CThostFtdcQryDepthMarketDataField CJNIHandler::JQryDepthMarketDataToC(JNIEnv* pEnv, jobject jobj) {

	//cout << "Track Info JQryDepthMarketDataToC" << endl;
	CThostFtdcQryDepthMarketDataField field;
	memset(&field, 0, sizeof(field));


	return field;
}


jobject CJNIHandler::CRspUserLoginToJ(JNIEnv* pEnv, CThostFtdcRspUserLoginField* pRspUserLogin) {
	//cout << "Track Info CRspUserLoginToJ" << endl;
	if (pRspUserLogin == NULL) {
		return NULL;
	}
	jclass jUserLoginFieldClass = pEnv->FindClass("com/genus/ctp/mode/GenusCTPRspUserLoginField");
	jmethodID jmethodUserLoginConstruction = pEnv->GetMethodID(jUserLoginFieldClass, "<init>", "()V");
	jobject jobjUserLoginField = pEnv->NewObject(jUserLoginFieldClass, jmethodUserLoginConstruction);
	jstring jstrTradingDay = charTojstring(pEnv, pRspUserLogin->TradingDay);
	jstring jstrLoginTime = charTojstring(pEnv, pRspUserLogin->LoginTime);
	jstring jstrBrokerID = charTojstring(pEnv, pRspUserLogin->BrokerID);
	jstring jstrUserID = charTojstring(pEnv, pRspUserLogin->UserID);
	jstring jstrSystemName = charTojstring(pEnv, pRspUserLogin->SystemName);
	jint jstrFrontID = intTojint(pEnv, pRspUserLogin->FrontID);
	jint jstrSessionID = intTojint(pEnv, pRspUserLogin->SessionID);
	jstring jstrMaxOrderRef = charTojstring(pEnv, pRspUserLogin->MaxOrderRef);
	jstring jstrSHFETime = charTojstring(pEnv, pRspUserLogin->SHFETime);
	jstring jstrDCETime = charTojstring(pEnv, pRspUserLogin->DCETime);
	jstring jstrCZCETime = charTojstring(pEnv, pRspUserLogin->CZCETime);
	jstring jstrFFEXTime = charTojstring(pEnv, pRspUserLogin->FFEXTime);
	jstring jstrINETime = charTojstring(pEnv, pRspUserLogin->INETime);

	jfieldID jfieldTradingDay = pEnv->GetFieldID(jUserLoginFieldClass, "TradingDay", "Ljava/lang/String;");
	jfieldID jfieldLoginTime = pEnv->GetFieldID(jUserLoginFieldClass, "LoginTime", "Ljava/lang/String;");
	jfieldID jfieldBrokerID = pEnv->GetFieldID(jUserLoginFieldClass, "BrokerID", "Ljava/lang/String;");
	jfieldID jfieldUserID = pEnv->GetFieldID(jUserLoginFieldClass, "UserID", "Ljava/lang/String;");
	jfieldID jfieldSystemName = pEnv->GetFieldID(jUserLoginFieldClass, "SystemName", "Ljava/lang/String;");
	jfieldID jfieldFrontID = pEnv->GetFieldID(jUserLoginFieldClass, "FrontID", "I");
	jfieldID jfieldSessionID = pEnv->GetFieldID(jUserLoginFieldClass, "SessionID", "I");
	jfieldID jfieldMaxOrderRef = pEnv->GetFieldID(jUserLoginFieldClass, "MaxOrderRef", "Ljava/lang/String;");
	jfieldID jfieldSHFETime = pEnv->GetFieldID(jUserLoginFieldClass, "SHFETime", "Ljava/lang/String;");
	jfieldID jfieldDCETime = pEnv->GetFieldID(jUserLoginFieldClass, "DCETime", "Ljava/lang/String;");
	jfieldID jfieldCZCETime = pEnv->GetFieldID(jUserLoginFieldClass, "CZCETime", "Ljava/lang/String;");
	jfieldID jfieldFFEXTime = pEnv->GetFieldID(jUserLoginFieldClass, "FFEXTime", "Ljava/lang/String;");
	jfieldID jfieldINETime = pEnv->GetFieldID(jUserLoginFieldClass, "INETime", "Ljava/lang/String;");

	pEnv->SetObjectField(jobjUserLoginField, jfieldTradingDay, jstrTradingDay);
	pEnv->SetObjectField(jobjUserLoginField, jfieldLoginTime, jstrLoginTime);
	pEnv->SetObjectField(jobjUserLoginField, jfieldBrokerID, jstrBrokerID);
	pEnv->SetObjectField(jobjUserLoginField, jfieldUserID, jstrUserID);
	pEnv->SetObjectField(jobjUserLoginField, jfieldSystemName, jstrSystemName);
	pEnv->SetIntField(jobjUserLoginField, jfieldFrontID, jstrFrontID);
	pEnv->SetIntField(jobjUserLoginField, jfieldSessionID, jstrSessionID);
	pEnv->SetObjectField(jobjUserLoginField, jfieldMaxOrderRef, jstrMaxOrderRef);
	pEnv->SetObjectField(jobjUserLoginField, jfieldSHFETime, jstrSHFETime);
	pEnv->SetObjectField(jobjUserLoginField, jfieldDCETime, jstrDCETime);
	pEnv->SetObjectField(jobjUserLoginField, jfieldCZCETime, jstrCZCETime);
	pEnv->SetObjectField(jobjUserLoginField, jfieldFFEXTime, jstrFFEXTime);
	pEnv->SetObjectField(jobjUserLoginField, jfieldINETime, jstrINETime);

	pEnv->DeleteLocalRef(jUserLoginFieldClass);
	pEnv->DeleteLocalRef(jstrLoginTime);
	pEnv->DeleteLocalRef(jstrBrokerID);
	pEnv->DeleteLocalRef(jstrUserID);
	pEnv->DeleteLocalRef(jstrSystemName);
	pEnv->DeleteLocalRef(jstrMaxOrderRef);
	pEnv->DeleteLocalRef(jstrSHFETime);
	pEnv->DeleteLocalRef(jstrDCETime);
	pEnv->DeleteLocalRef(jstrCZCETime);
	pEnv->DeleteLocalRef(jstrFFEXTime);
	pEnv->DeleteLocalRef(jstrFFEXTime);
	return jobjUserLoginField;
}

jobject CJNIHandler::CRspInfoToJ(JNIEnv* pEnv, CThostFtdcRspInfoField* pRspInfo) {
	//cout << "Track Info CRspInfoToJ" << endl;
	if (pRspInfo == NULL) {
		return NULL;
	}
	//cout << "Track Info CRspInfoToJ : " << pRspInfo->ErrorID << " >> "<<pRspInfo->ErrorMsg << endl;
	jclass jInfoClass = pEnv->FindClass("com/genus/ctp/mode/GenusCTPRspInfoField");
	jmethodID jmethodInfoConstruction = pEnv->GetMethodID(jInfoClass, "<init>", "()V");
	jobject jobj = pEnv->NewObject(jInfoClass, jmethodInfoConstruction);
	jint jstrErrorID = intTojint(pEnv, pRspInfo->ErrorID);
	jstring jstrErrorMsg = charTojstring(pEnv, pRspInfo->ErrorMsg);

	jfieldID jfieldErrorID = pEnv->GetFieldID(jInfoClass, "ErrorID", "I");
	jfieldID jfieldErrorMsg = pEnv->GetFieldID(jInfoClass, "ErrorMsg", "Ljava/lang/String;");
	pEnv->SetIntField(jobj, jfieldErrorID, jstrErrorID);
	pEnv->SetObjectField(jobj, jfieldErrorMsg, jstrErrorMsg);

	pEnv->DeleteLocalRef(jInfoClass);
	pEnv->DeleteLocalRef(jstrErrorMsg);
	return jobj;

}

jobject CJNIHandler::CRspAuthenticateToJ(JNIEnv* pEnv, CThostFtdcRspAuthenticateField* pRspInfo) {
	//cout << "Tracker Log CRspAuthenticateToJ" << endl;
	jclass jInfoClass = pEnv->FindClass("com/genus/ctp/mode/GenusCTPRspAuthenticateField");
	jmethodID jmethodInfoConstruction = pEnv->GetMethodID(jInfoClass, "<init>", "()V");
	jobject jobj = pEnv->NewObject(jInfoClass, jmethodInfoConstruction);

	jstring jstrBrokerID = charTojstring(pEnv, pRspInfo->BrokerID);
	jstring jstrUserID = charTojstring(pEnv, pRspInfo->UserID);
	jstring jstrUserProductInfo = charTojstring(pEnv, pRspInfo->UserProductInfo);
	jstring jstrAppID = charTojstring(pEnv, pRspInfo->AppID);
	jchar jstrAppType = charTojchar(pEnv, pRspInfo->AppType);

	jfieldID jfieldBrokerID = pEnv->GetFieldID(jInfoClass, "BrokerID", "Ljava/lang/String;");
	jfieldID jfieldUserID = pEnv->GetFieldID(jInfoClass, "UserID", "Ljava/lang/String;");
	jfieldID jfieldUserProductInfo = pEnv->GetFieldID(jInfoClass, "UserProductInfo", "Ljava/lang/String;");
	jfieldID jfieldAppID = pEnv->GetFieldID(jInfoClass, "AppID", "Ljava/lang/String;");
	jfieldID jfieldjstrAppType = pEnv->GetFieldID(jInfoClass, "jstrAppType", "C");

	pEnv->SetObjectField(jobj, jfieldBrokerID, jstrBrokerID);
	pEnv->SetObjectField(jobj, jfieldUserID, jstrUserID);
	pEnv->SetObjectField(jobj, jfieldUserProductInfo, jstrUserProductInfo);
	pEnv->SetObjectField(jobj, jfieldAppID, jstrAppID);
	pEnv->SetCharField(jobj, jfieldjstrAppType, jstrAppType);

	pEnv->DeleteLocalRef(jInfoClass);
	pEnv->DeleteLocalRef(jstrBrokerID);
	pEnv->DeleteLocalRef(jstrUserID);
	pEnv->DeleteLocalRef(jstrUserProductInfo);
	pEnv->DeleteLocalRef(jstrAppID);
	return jobj;
}

jobject CJNIHandler::CSpecificInstrumentFieldeToJ(JNIEnv* pEnv, CThostFtdcSpecificInstrumentField* pRspInstrumnet) {
	//cout << "Tracker Log CSpecificInstrumentFieldeToJ" << endl;
	if (pRspInstrumnet == NULL) {
		return NULL;
	}

	jclass jClass = pEnv->FindClass("com/genus/ctp/mode/GenusCTPSpecificInstrumentField");
	jmethodID jmethodInfoConstruction = pEnv->GetMethodID(jClass, "<init>", "()V");
	jobject jobj = pEnv->NewObject(jClass, jmethodInfoConstruction);

	jstring jstrInstrumentID = charTojstring(pEnv, pRspInstrumnet->InstrumentID);
	jfieldID jfieldInstrumentID = pEnv->GetFieldID(jClass, "InstrumentID", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldInstrumentID, jstrInstrumentID);
	pEnv->DeleteLocalRef(jstrInstrumentID);

	pEnv->DeleteLocalRef(jClass);

	//cout << "Tracker Log   Over " << endl;
	return jobj;

}

jobject CJNIHandler::CInstrumentFieldeToJ(JNIEnv* pEnv, CThostFtdcInstrumentField* pRspInstrumnet) {
	//cout << "Tracker Log CInstrumentFieldeToJ" << endl;
	if (pRspInstrumnet == NULL) {
		return NULL;
	}
	jclass jClass = pEnv->FindClass("com/genus/ctp/mode/GenusCTPInstrumentField");
	jmethodID jmethodInfoConstruction = pEnv->GetMethodID(jClass, "<init>", "()V");
	jobject jobj = pEnv->NewObject(jClass, jmethodInfoConstruction);

	jstring jstrInstrumentID = charTojstring(pEnv, pRspInstrumnet->InstrumentID);
	jfieldID jfieldInstrumentID = pEnv->GetFieldID(jClass, "InstrumentID", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldInstrumentID, jstrInstrumentID);
	pEnv->DeleteLocalRef(jstrInstrumentID);

	jstring jstrExchangeID = charTojstring(pEnv, pRspInstrumnet->ExchangeID);
	jfieldID jfieldExchangeID = pEnv->GetFieldID(jClass, "ExchangeID", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldExchangeID, jstrExchangeID);
	pEnv->DeleteLocalRef(jstrExchangeID);



	jstring jstrInstrumentName = charTojstring(pEnv, pRspInstrumnet->InstrumentName);
	jfieldID jfieldInstrumentName = pEnv->GetFieldID(jClass, "InstrumentName", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldInstrumentName, jstrInstrumentName);
	pEnv->DeleteLocalRef(jstrInstrumentName);

	jstring jstrProductID = charTojstring(pEnv, pRspInstrumnet->ProductID);
	jfieldID jfieldProductID = pEnv->GetFieldID(jClass, "ProductID", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldProductID, jstrProductID);
	pEnv->DeleteLocalRef(jstrProductID);

	jchar jcharProductClass = charTojchar(pEnv, pRspInstrumnet->ProductClass);
	jfieldID jfieldProductClass = pEnv->GetFieldID(jClass, "ProductClass", "C");
	pEnv->SetCharField(jobj, jfieldProductClass, jcharProductClass);

	jint jintDeliveryYear = intTojint(pEnv, pRspInstrumnet->DeliveryYear);
	jfieldID jfieldDeliveryYear = pEnv->GetFieldID(jClass, "DeliveryYear", "I");
	pEnv->SetIntField(jobj, jfieldDeliveryYear, jintDeliveryYear);

	jint jintDeliveryMonth = intTojint(pEnv, pRspInstrumnet->DeliveryMonth);
	jfieldID jfieldDeliveryMonth = pEnv->GetFieldID(jClass, "DeliveryMonth", "I");
	pEnv->SetIntField(jobj, jfieldDeliveryMonth, jintDeliveryMonth);

	jlong jlongMaxMarketOrderVolume = intTojlong(pEnv, pRspInstrumnet->MaxMarketOrderVolume);
	jfieldID jfieldMaxMarketOrderVolume = pEnv->GetFieldID(jClass, "MaxMarketOrderVolume", "J");
	pEnv->SetLongField(jobj, jfieldMaxMarketOrderVolume, jlongMaxMarketOrderVolume);

	jlong jlongMinMarketOrderVolume = intTojlong(pEnv, pRspInstrumnet->MinMarketOrderVolume);
	jfieldID jfieldMinMarketOrderVolume = pEnv->GetFieldID(jClass, "MinMarketOrderVolume", "J");
	pEnv->SetLongField(jobj, jfieldMinMarketOrderVolume, jlongMinMarketOrderVolume);

	jlong jlongMaxLimitOrderVolume = intTojlong(pEnv, pRspInstrumnet->MaxLimitOrderVolume);
	jfieldID jfieldMaxLimitOrderVolume = pEnv->GetFieldID(jClass, "MaxLimitOrderVolume", "J");
	pEnv->SetLongField(jobj, jfieldMaxLimitOrderVolume, jlongMaxLimitOrderVolume);

	jlong jlongrMinLimitOrderVolume = intTojlong(pEnv, pRspInstrumnet->MinLimitOrderVolume);
	jfieldID jfieldMinLimitOrderVolume = pEnv->GetFieldID(jClass, "MinLimitOrderVolume", "J");
	pEnv->SetLongField(jobj, jfieldMinLimitOrderVolume, jlongrMinLimitOrderVolume);

	jlong jlongrVolumeMultiple = intTojlong(pEnv, pRspInstrumnet->VolumeMultiple);
	jfieldID jfieldVolumeMultiple = pEnv->GetFieldID(jClass, "VolumeMultiple", "J");
	pEnv->SetLongField(jobj, jfieldVolumeMultiple, jlongrVolumeMultiple);




	jdouble jdouPriceTick = doubleTojdouble(pEnv, pRspInstrumnet->PriceTick);
	jfieldID jfieldPriceTick = pEnv->GetFieldID(jClass, "PriceTick", "D");
	pEnv->SetDoubleField(jobj, jfieldPriceTick, jdouPriceTick);

	jstring jstrCreateDate = charTojstring(pEnv, pRspInstrumnet->CreateDate);
	jfieldID jfieldCreateDate = pEnv->GetFieldID(jClass, "ProductID", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldCreateDate, jstrCreateDate);
	pEnv->DeleteLocalRef(jstrCreateDate);

	jstring jstrOpenDate = charTojstring(pEnv, pRspInstrumnet->OpenDate);
	jfieldID jfieldOpenDate = pEnv->GetFieldID(jClass, "OpenDate", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldOpenDate, jstrOpenDate);
	pEnv->DeleteLocalRef(jstrOpenDate);

	jstring jstrExpireDate = charTojstring(pEnv, pRspInstrumnet->ExpireDate);
	jfieldID jfieldExpireDate = pEnv->GetFieldID(jClass, "ExpireDate", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldExpireDate, jstrExpireDate);
	pEnv->DeleteLocalRef(jstrExpireDate);

	jstring jstrStartDelivDate = charTojstring(pEnv, pRspInstrumnet->StartDelivDate);
	jfieldID jfieldStartDelivDate = pEnv->GetFieldID(jClass, "StartDelivDate", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldStartDelivDate, jstrStartDelivDate);
	pEnv->DeleteLocalRef(jstrStartDelivDate);

	jstring jstrEndDelivDate = charTojstring(pEnv, pRspInstrumnet->EndDelivDate);
	jfieldID jfieldEndDelivDate = pEnv->GetFieldID(jClass, "EndDelivDate", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldEndDelivDate, jstrEndDelivDate);
	pEnv->DeleteLocalRef(jstrEndDelivDate);

	jchar jcharInstLifePhase = charTojchar(pEnv, pRspInstrumnet->InstLifePhase);
	jfieldID jfieldInstLifePhase = pEnv->GetFieldID(jClass, "InstLifePhase", "C");
	pEnv->SetCharField(jobj, jfieldInstLifePhase, jcharInstLifePhase);

	jboolean jboolIsTrading = boolToJboolean(pEnv, pRspInstrumnet->IsTrading);
	jfieldID jfieldIsTrading = pEnv->GetFieldID(jClass, "IsTrading", "Z");
	pEnv->SetBooleanField(jobj, jfieldIsTrading, jboolIsTrading);

	jchar jcharPositionType = charTojchar(pEnv, pRspInstrumnet->PositionType);
	jfieldID jfieldPositionType = pEnv->GetFieldID(jClass, "PositionType", "C");
	pEnv->SetCharField(jobj, jfieldPositionType, jcharPositionType);

	jchar jcharPositionDateType = charTojchar(pEnv, pRspInstrumnet->PositionDateType);
	jfieldID jfieldPositionDateType = pEnv->GetFieldID(jClass, "PositionDateType", "C");
	pEnv->SetCharField(jobj, jfieldPositionDateType, jcharPositionDateType);



	jdouble jdouLongMarginRatio = doubleTojdouble(pEnv, pRspInstrumnet->LongMarginRatio);
	jfieldID jfieldLongMarginRatio = pEnv->GetFieldID(jClass, "LongMarginRatio", "D");
	pEnv->SetDoubleField(jobj, jfieldLongMarginRatio, jdouLongMarginRatio);

	jdouble jdouShortMarginRatio = doubleTojdouble(pEnv, pRspInstrumnet->ShortMarginRatio);
	jfieldID jfieldShortMarginRatio = pEnv->GetFieldID(jClass, "ShortMarginRatio", "D");
	pEnv->SetDoubleField(jobj, jfieldShortMarginRatio, jdouShortMarginRatio);





	jchar jcharMaxMarginSideAlgorithm = charTojchar(pEnv, pRspInstrumnet->MaxMarginSideAlgorithm);
	jfieldID jfieldMaxMarginSideAlgorithm = pEnv->GetFieldID(jClass, "MaxMarginSideAlgorithm", "C");
	pEnv->SetCharField(jobj, jfieldMaxMarginSideAlgorithm, jcharMaxMarginSideAlgorithm);


	jstring jstrUnderlyingInstrID = charTojstring(pEnv, pRspInstrumnet->UnderlyingInstrID);
	jfieldID jfieldUnderlyingInstrID = pEnv->GetFieldID(jClass, "UnderlyingInstrID", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldUnderlyingInstrID, jstrUnderlyingInstrID);
	pEnv->DeleteLocalRef(jstrUnderlyingInstrID);



	jdouble jdouStrikePrice = doubleTojdouble(pEnv, pRspInstrumnet->StrikePrice);
	jfieldID jfieldStrikePrice = pEnv->GetFieldID(jClass, "StrikePrice", "D");
	pEnv->SetDoubleField(jobj, jfieldStrikePrice, jdouStrikePrice);






	jchar jcharOptionsType = charTojchar(pEnv, pRspInstrumnet->OptionsType);
	jfieldID jfieldOptionsType = pEnv->GetFieldID(jClass, "OptionsType", "C");
	pEnv->SetCharField(jobj, jfieldPositionType, jcharOptionsType);


	jdouble jdouUnderlyingMultiple = doubleTojdouble(pEnv, pRspInstrumnet->UnderlyingMultiple);
	jfieldID jfieldUnderlyingMultiple = pEnv->GetFieldID(jClass, "UnderlyingMultiple", "D");
	pEnv->SetDoubleField(jobj, jfieldUnderlyingMultiple, jdouUnderlyingMultiple);


	jchar jcharCombinationType = charTojchar(pEnv, pRspInstrumnet->CombinationType);
	jfieldID jfieldCombinationType = pEnv->GetFieldID(jClass, "CombinationType", "C");
	pEnv->SetCharField(jobj, jfieldCombinationType, jcharCombinationType);

	pEnv->DeleteLocalRef(jClass);

	//cout << "Tracker Log CInstrumentFieldeToJ  Over " << endl;
	return jobj;

}



jobject CJNIHandler::CDepthMarketDataFieldeToJ(JNIEnv* pEnv, CThostFtdcDepthMarketDataField* pDepthMarketData) {
	//cout << "Tracker Log CDepthMarketDataFieldeToJ" << endl;
	if (pDepthMarketData == NULL) {
		return NULL;
	}
	jclass jClass = pEnv->FindClass("com/genus/ctp/mode/GenusCTPDepthMarketDataField");
	jmethodID jmethodInfoConstruction = pEnv->GetMethodID(jClass, "<init>", "()V");
	jobject jobj = pEnv->NewObject(jClass, jmethodInfoConstruction);

	jstring jstrTradingDay = charTojstring(pEnv, pDepthMarketData->TradingDay);
	jfieldID jfieldTradingDay = pEnv->GetFieldID(jClass, "TradingDay", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldTradingDay, jstrTradingDay);
	pEnv->DeleteLocalRef(jstrTradingDay);

	jstring jstrInstrumentID = charTojstring(pEnv, pDepthMarketData->InstrumentID);
	jfieldID jfieldInstrumentID = pEnv->GetFieldID(jClass, "InstrumentID", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldInstrumentID, jstrInstrumentID);
	pEnv->DeleteLocalRef(jstrInstrumentID);

	jstring jstrExchangeID = charTojstring(pEnv, pDepthMarketData->ExchangeID);
	jfieldID jfieldExchangeID = pEnv->GetFieldID(jClass, "ExchangeID", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldExchangeID, jstrExchangeID);
	pEnv->DeleteLocalRef(jstrExchangeID);

	jstring jstrIExchangeInstID = charTojstring(pEnv, pDepthMarketData->ExchangeInstID);
	jfieldID jfieldExchangeInstID = pEnv->GetFieldID(jClass, "ExchangeInstID", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldExchangeInstID, jstrIExchangeInstID);
	pEnv->DeleteLocalRef(jstrIExchangeInstID);

	jdouble jdouLastPrice = doubleTojdouble(pEnv, pDepthMarketData->LastPrice);
	jfieldID jfieldLastPrice = pEnv->GetFieldID(jClass, "LastPrice", "D");
	pEnv->SetDoubleField(jobj, jfieldLastPrice, jdouLastPrice);

	jdouble jdouPreSettlementPrice = doubleTojdouble(pEnv, pDepthMarketData->PreSettlementPrice);
	jfieldID jfieldPreSettlementPrice = pEnv->GetFieldID(jClass, "PreSettlementPrice", "D");
	pEnv->SetDoubleField(jobj, jfieldPreSettlementPrice, jdouPreSettlementPrice);

	jdouble jdouPreClosePrice = doubleTojdouble(pEnv, pDepthMarketData->PreClosePrice);
	jfieldID jfieldPreClosePrice = pEnv->GetFieldID(jClass, "PreClosePrice", "D");
	pEnv->SetDoubleField(jobj, jfieldPreClosePrice, jdouPreClosePrice);

	jdouble jdouPreOpenInterest = doubleTojdouble(pEnv, pDepthMarketData->PreOpenInterest);
	jfieldID jfieldPreOpenInterest = pEnv->GetFieldID(jClass, "PreOpenInterest", "D");
	pEnv->SetDoubleField(jobj, jfieldPreOpenInterest, jdouPreOpenInterest);

	jdouble jdouOpenPrice = doubleTojdouble(pEnv, pDepthMarketData->OpenPrice);
	jfieldID jfieldOpenPrice = pEnv->GetFieldID(jClass, "OpenPrice", "D");
	pEnv->SetDoubleField(jobj, jfieldOpenPrice, jdouOpenPrice);

	jdouble jdouHighestPrice = doubleTojdouble(pEnv, pDepthMarketData->HighestPrice);
	jfieldID jfieldHighestPrice = pEnv->GetFieldID(jClass, "HighestPrice", "D");
	pEnv->SetDoubleField(jobj, jfieldHighestPrice, jdouHighestPrice);

	jdouble jdouLowestPrice = doubleTojdouble(pEnv, pDepthMarketData->LowestPrice);
	jfieldID jfieldLowestPrice = pEnv->GetFieldID(jClass, "LowestPrice", "D");
	pEnv->SetDoubleField(jobj, jfieldLowestPrice, jdouLowestPrice);

	jlong jlongVolume = intTojlong(pEnv, pDepthMarketData->Volume);
	jfieldID jfieldVolume = pEnv->GetFieldID(jClass, "Volume", "J");
	pEnv->SetLongField(jobj, jfieldVolume, jlongVolume);

	jdouble jdouTurnover = doubleTojdouble(pEnv, pDepthMarketData->Turnover);
	jfieldID jfieldTurnover = pEnv->GetFieldID(jClass, "Turnover", "D");
	pEnv->SetDoubleField(jobj, jfieldTurnover, jdouTurnover);

	jdouble jdouOpenInterest = doubleTojdouble(pEnv, pDepthMarketData->OpenInterest);
	jfieldID jfieldOpenInterest = pEnv->GetFieldID(jClass, "OpenInterest", "D");
	pEnv->SetDoubleField(jobj, jfieldOpenInterest, jdouOpenInterest);

	jdouble jdouClosePrice = doubleTojdouble(pEnv, pDepthMarketData->ClosePrice);
	jfieldID jfieldClosePrice = pEnv->GetFieldID(jClass, "ClosePrice", "D");
	pEnv->SetDoubleField(jobj, jfieldClosePrice, jdouClosePrice);

	jdouble jdouSettlementPrice = doubleTojdouble(pEnv, pDepthMarketData->SettlementPrice);
	jfieldID jfieldSettlementPrice = pEnv->GetFieldID(jClass, "SettlementPrice", "D");
	pEnv->SetDoubleField(jobj, jfieldSettlementPrice, jdouSettlementPrice);

	jdouble jdouUpperLimitPrice = doubleTojdouble(pEnv, pDepthMarketData->UpperLimitPrice);
	jfieldID jfieldUpperLimitPrice = pEnv->GetFieldID(jClass, "UpperLimitPrice", "D");
	pEnv->SetDoubleField(jobj, jfieldUpperLimitPrice, jdouUpperLimitPrice);

	jdouble jdouLowerLimitPrice = doubleTojdouble(pEnv, pDepthMarketData->LowerLimitPrice);
	jfieldID jfieldLowerLimitPrice = pEnv->GetFieldID(jClass, "LowerLimitPrice", "D");
	pEnv->SetDoubleField(jobj, jfieldLowerLimitPrice, jdouLowerLimitPrice);

	jdouble jdouPreDelta = doubleTojdouble(pEnv, pDepthMarketData->PreDelta);
	jfieldID jfieldPreDelta = pEnv->GetFieldID(jClass, "PreDelta", "D");
	pEnv->SetDoubleField(jobj, jfieldPreDelta, jdouPreDelta);


	jdouble jdouCurrDelta = doubleTojdouble(pEnv, pDepthMarketData->CurrDelta);
	jfieldID jfieldCurrDelta = pEnv->GetFieldID(jClass, "CurrDelta", "D");
	pEnv->SetDoubleField(jobj, jfieldCurrDelta, jdouCurrDelta);

	jstring jstrUpdateTime = charTojstring(pEnv, pDepthMarketData->UpdateTime);
	jfieldID jfieldUpdateTime = pEnv->GetFieldID(jClass, "UpdateTime", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldUpdateTime, jstrUpdateTime);
	pEnv->DeleteLocalRef(jstrUpdateTime);

	jlong jlongUpdateMillisec = intTojlong(pEnv, pDepthMarketData->UpdateMillisec);
	jfieldID jfieldUpdateMillisec = pEnv->GetFieldID(jClass, "UpdateMillisec", "J");
	pEnv->SetLongField(jobj, jfieldUpdateMillisec, jlongUpdateMillisec);

	jdouble jdouBidPrice1 = doubleTojdouble(pEnv, pDepthMarketData->BidPrice1);
	jfieldID jfieldBidPrice1 = pEnv->GetFieldID(jClass, "BidPrice1", "D");
	pEnv->SetDoubleField(jobj, jfieldBidPrice1, jdouBidPrice1);
	jdouble jdouBidPrice2 = doubleTojdouble(pEnv, pDepthMarketData->BidPrice2);
	jfieldID jfieldBidPrice2 = pEnv->GetFieldID(jClass, "BidPrice2", "D");
	pEnv->SetDoubleField(jobj, jfieldBidPrice2, jdouBidPrice2);
	jdouble jdouBidPrice3 = doubleTojdouble(pEnv, pDepthMarketData->BidPrice3);
	jfieldID jfieldBidPrice3 = pEnv->GetFieldID(jClass, "BidPrice3", "D");
	pEnv->SetDoubleField(jobj, jfieldBidPrice3, jdouBidPrice3);
	jdouble jdouBidPrice4 = doubleTojdouble(pEnv, pDepthMarketData->BidPrice4);
	jfieldID jfieldBidPrice4 = pEnv->GetFieldID(jClass, "BidPrice4", "D");
	pEnv->SetDoubleField(jobj, jfieldBidPrice4, jdouBidPrice4);
	jdouble jdouBidPrice5 = doubleTojdouble(pEnv, pDepthMarketData->BidPrice5);
	jfieldID jfieldBidPrice5 = pEnv->GetFieldID(jClass, "BidPrice5", "D");
	pEnv->SetDoubleField(jobj, jfieldBidPrice5, jdouBidPrice5);

	jlong jlongBidVolume1 = intTojlong(pEnv, pDepthMarketData->BidVolume1);
	jfieldID jfieldBidVolume1 = pEnv->GetFieldID(jClass, "BidVolume1", "J");
	pEnv->SetLongField(jobj, jfieldBidVolume1, jlongBidVolume1);
	jlong jlongBidVolume2 = intTojlong(pEnv, pDepthMarketData->BidVolume2);
	jfieldID jfieldBidVolume2 = pEnv->GetFieldID(jClass, "BidVolume2", "J");
	pEnv->SetLongField(jobj, jfieldBidVolume2, jlongBidVolume2);
	jlong jlongBidVolume3 = intTojlong(pEnv, pDepthMarketData->BidVolume3);
	jfieldID jfieldBidVolume3 = pEnv->GetFieldID(jClass, "BidVolume3", "J");
	pEnv->SetLongField(jobj, jfieldBidVolume3, jlongBidVolume3);
	jlong jlongBidVolume4 = intTojlong(pEnv, pDepthMarketData->BidVolume4);
	jfieldID jfieldBidVolume4 = pEnv->GetFieldID(jClass, "BidVolume4", "J");
	pEnv->SetLongField(jobj, jfieldBidVolume4, jlongBidVolume4);
	jlong jlongBidVolume5 = intTojlong(pEnv, pDepthMarketData->BidVolume5);
	jfieldID jfieldBidVolume5 = pEnv->GetFieldID(jClass, "BidVolume5", "J");
	pEnv->SetLongField(jobj, jfieldBidVolume5, jlongBidVolume5);

	jdouble jdouAskPrice1 = doubleTojdouble(pEnv, pDepthMarketData->AskPrice1);
	jfieldID jfieldAskPrice1 = pEnv->GetFieldID(jClass, "AskPrice1", "D");
	pEnv->SetDoubleField(jobj, jfieldAskPrice1, jdouAskPrice1);
	jdouble jdouAskPrice2 = doubleTojdouble(pEnv, pDepthMarketData->AskPrice2);
	jfieldID jfieldAskPrice2 = pEnv->GetFieldID(jClass, "AskPrice2", "D");
	pEnv->SetDoubleField(jobj, jfieldAskPrice2, jdouAskPrice2);
	jdouble jdouAskPrice3 = doubleTojdouble(pEnv, pDepthMarketData->AskPrice3);
	jfieldID jfieldAskPrice3 = pEnv->GetFieldID(jClass, "AskPrice3", "D");
	pEnv->SetDoubleField(jobj, jfieldAskPrice3, jdouAskPrice3);
	jdouble jdouAskPrice4 = doubleTojdouble(pEnv, pDepthMarketData->AskPrice4);
	jfieldID jfieldAskPrice4 = pEnv->GetFieldID(jClass, "AskPrice4", "D");
	pEnv->SetDoubleField(jobj, jfieldAskPrice4, jdouAskPrice4);
	jdouble jdouAskPrice5 = doubleTojdouble(pEnv, pDepthMarketData->AskPrice5);
	jfieldID jfieldAskPrice5 = pEnv->GetFieldID(jClass, "AskPrice5", "D");
	pEnv->SetDoubleField(jobj, jfieldAskPrice5, jdouAskPrice5);

	jlong jlongAskVolume1 = intTojlong(pEnv, pDepthMarketData->AskVolume1);
	jfieldID jfieldAskVolume1 = pEnv->GetFieldID(jClass, "AskVolume1", "J");
	pEnv->SetLongField(jobj, jfieldAskVolume1, jlongAskVolume1);
	jlong jlongAskVolume2 = intTojlong(pEnv, pDepthMarketData->AskVolume2);
	jfieldID jfieldAskVolume2 = pEnv->GetFieldID(jClass, "AskVolume2", "J");
	pEnv->SetLongField(jobj, jfieldAskVolume2, jlongAskVolume2);
	jlong jlongAskVolume3 = intTojlong(pEnv, pDepthMarketData->AskVolume3);
	jfieldID jfieldAskVolume3 = pEnv->GetFieldID(jClass, "AskVolume3", "J");
	pEnv->SetLongField(jobj, jfieldAskVolume3, jlongAskVolume3);
	jlong jlongAskVolume4 = intTojlong(pEnv, pDepthMarketData->AskVolume4);
	jfieldID jfieldAskVolume4 = pEnv->GetFieldID(jClass, "AskVolume4", "J");
	pEnv->SetLongField(jobj, jfieldAskVolume4, jlongAskVolume4);
	jlong jlongAskVolume5 = intTojlong(pEnv, pDepthMarketData->AskVolume5);
	jfieldID jfieldAskVolume5 = pEnv->GetFieldID(jClass, "AskVolume5", "J");
	pEnv->SetLongField(jobj, jfieldAskVolume5, jlongAskVolume5);

	jdouble jdouAveragePrice = doubleTojdouble(pEnv, pDepthMarketData->AveragePrice);
	jfieldID jfieldAveragePrice = pEnv->GetFieldID(jClass, "AveragePrice", "D");
	pEnv->SetDoubleField(jobj, jfieldAveragePrice, jdouAveragePrice);

	jstring jstrActionDay = charTojstring(pEnv, pDepthMarketData->ActionDay);
	jfieldID jfieldActionDay = pEnv->GetFieldID(jClass, "ActionDay", "Ljava/lang/String;");
	pEnv->SetObjectField(jobj, jfieldActionDay, jstrActionDay);
	pEnv->DeleteLocalRef(jstrActionDay);




	pEnv->DeleteLocalRef(jClass);
	//cout << "Tracker Log CDepthMarketDataFieldeToJ  Over " << endl;
	return jobj;

}






