#pragma once
#include "ThostFtdcMdApi.h"
using namespace std;


class CJNIHandler
{
private:
	CJNIHandler(void);
	~CJNIHandler(void);
private:

public:
	static CJNIHandler* GetInstance();
public:

	char* jstringToChar(JNIEnv* pEnv, jstring jStr);
	jstring charTojstring(JNIEnv* pEnv, const char* pPat);

	string jstringTostr(JNIEnv* pEnv, jstring jStr);
	jchar charTojchar(JNIEnv* pEnv, char pPat);
	char jcharTochar(JNIEnv* pEnv, char pPat);

	int jintToint(JNIEnv* pEnv, jint jStr);
	jint intTojint(JNIEnv* pEnv, const int pPat);
	jlong intTojlong(JNIEnv* pEnv, const int pPat);
	bool jbooleanTobool(JNIEnv* pEnv, jboolean jStr);
	jboolean boolToJboolean(JNIEnv* pEnv, bool jStr);
	jdouble doubleTojdouble(JNIEnv* pEnv, double pPat);
	double jdoubleTodouble(JNIEnv* pEnv, jdouble pPat);
	map<char*,char*>JMaptoCmap(JNIEnv* pEnv, jobject jobj);
	char**  JArrayListStrToC(JNIEnv* pEnv, jobject jobj);
	CThostFtdcReqAuthenticateField JReqAuthenticateToC(JNIEnv* pEnv, jobject jobj);
	CThostFtdcReqUserLoginField JReqUserLoginToC(JNIEnv* pEnv, jobject jobj);


	CThostFtdcUserLogoutField JReqUserLogoutToC(JNIEnv* pEnv, jobject jobj);

	CThostFtdcQryInstrumentField JQryInstrumentToC(JNIEnv* pEnv, jobject jobj);

	CThostFtdcQryDepthMarketDataField JQryDepthMarketDataToC(JNIEnv* pEnv, jobject jobj);

	jobject CRspAuthenticateToJ(JNIEnv* pEnv, CThostFtdcRspAuthenticateField* pRspInfo);
	jobject CRspInfoToJ(JNIEnv* pEnv, CThostFtdcRspInfoField* pRspInfo);

	jobject CRspUserLoginToJ(JNIEnv* pEnv, CThostFtdcRspUserLoginField* pRspUserLogin);

	jobject CSpecificInstrumentFieldeToJ(JNIEnv* pEnv, CThostFtdcSpecificInstrumentField* pRspInstrumnet);
	jobject CInstrumentFieldeToJ(JNIEnv* pEnv, CThostFtdcInstrumentField* pRspUserLogin);
	jobject CDepthMarketDataFieldeToJ(JNIEnv* pEnv, CThostFtdcDepthMarketDataField* pDepthMarketData);
	
	
	
};

