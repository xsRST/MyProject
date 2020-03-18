#pragma once
#include "ThostFtdcMdApi.h"
#pragma comment(lib,"thostmduserapi_se.lib")
using namespace std;

class GenusCTPMarketDataSpi : public CThostFtdcMdSpi
{
public:
	~GenusCTPMarketDataSpi(void);
	GenusCTPMarketDataSpi();
private:
	CThostFtdcMdApi* m_pMarketDataApi;
	jobject jmarketSpi;
	JavaVM* m_pJavaVm;
	int m_iRequestID;
	bool is_connected;
	bool is_login_successful;
	
public:
	static GenusCTPMarketDataSpi* GetInstance(JNIEnv* pEnv, jobject obj, jobject marketSpi);
public:

	const char* GetApiVersion();
	const char* GetTradingDay();
	int StartMarketCTP(const char* pMarketFontAddr);
	bool IsConnected();
	bool IsLoginSuccessful();
public:
	
	///�û���¼����
	virtual int ReqUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID) ;
	///�ǳ�����
	virtual int ReqUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID) ;
	///�������顣
	///@param ppInstrumentID ��ԼID  
	///@param nCount Ҫ����/�˶�����ĺ�Լ����
	///@remark 
	virtual int SubscribeMarketData(char* ppInstrumentID[], int nCount);

	///�˶����顣
	///@param ppInstrumentID ��ԼID  
	///@param nCount Ҫ����/�˶�����ĺ�Լ����
	///@remark 
	virtual int UnSubscribeMarketData(char* ppInstrumentID[], int nCount);


	///���ͻ����뽻�׺�̨������ͨ������ʱ����δ��¼ǰ�����÷��������á�
	virtual void OnFrontConnected();
	///���ͻ����뽻�׺�̨ͨ�����ӶϿ�ʱ���÷��������á���������������API���Զ��������ӣ��ͻ��˿ɲ�������
	///@param nReason ����ԭ��
	///        0x1001 �����ʧ��
	///        0x1002 ����дʧ��
	///        0x2001 ����������ʱ
	///        0x2002 ��������ʧ��
	///        0x2003 �յ�������
	virtual void OnFrontDisconnected(int nReason) ;
	///������ʱ���档����ʱ��δ�յ�����ʱ���÷��������á�
	///@param nTimeLapse �����ϴν��ձ��ĵ�ʱ��
	virtual void OnHeartBeatWarning(int nTimeLapse);
	///��¼������Ӧ
	virtual void OnRspUserLogin(CThostFtdcRspUserLoginField* pRspUserLogin, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///����Ӧ��
	virtual void OnRspError(CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///��������Ӧ��
	void OnRspSubMarketData(CThostFtdcSpecificInstrumentField* pSpecificInstrument, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///�������֪ͨ
	virtual void OnRtnDepthMarketData(CThostFtdcDepthMarketDataField* pDepthMarketData);
};

