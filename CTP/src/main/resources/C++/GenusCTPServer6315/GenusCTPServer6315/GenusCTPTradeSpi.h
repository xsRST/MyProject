#pragma once
#include "pch.h"
#include "ThostFtdcTraderApi.h"
#pragma comment(lib,"thosttraderapi_se.lib")
using namespace std;

class GenusCTPTradeSpi : public CThostFtdcTraderSpi
{

public:
	~GenusCTPTradeSpi(void);
	GenusCTPTradeSpi();

public:
	CThostFtdcTraderApi* t_pTradeApi;
	jobject jtradeSpi;
	JavaVM* t_pJavaVm;
	bool is_connected;
	bool is_login_successful;

public:
	static GenusCTPTradeSpi* GetInstance(JNIEnv* pEnv, jobject obj, jobject tradeSpi);
public:
	int StartTradeCTP(const char* pTradeFontAddr);
	const char* GetApiVersion();
	const char* GetTradingDay();
	
	bool IsConnected();
	bool IsLoginSuccessful();
public:

	///�ͻ�����֤����
	virtual int ReqAuthenticate(CThostFtdcReqAuthenticateField* pReqAuthenticateField, int nRequestID) ;
	///�û���¼����
	virtual int ReqUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID) ;
	///�ǳ�����
	virtual int ReqUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID);
	///�����ѯ��Լ
	virtual int ReqQryInstrument(CThostFtdcQryInstrumentField* pQryInstrument, int nRequestID) ;
	///�����ѯ����
	virtual int ReqQryDepthMarketData(CThostFtdcQryDepthMarketDataField* pQryDepthMarketData, int nRequestID) ;

	///���ͻ����뽻�׺�̨������ͨ������ʱ����δ��¼ǰ�����÷��������á�
	virtual void OnFrontConnected();
	///���ͻ����뽻�׺�̨ͨ�����ӶϿ�ʱ���÷��������á���������������API���Զ��������ӣ��ͻ��˿ɲ�������
	///@param nReason ����ԭ��
	///        0x1001 �����ʧ��
	///        0x1002 ����дʧ��
	///        0x2001 ����������ʱ
	///        0x2002 ��������ʧ��
	///        0x2003 �յ�������
	virtual void OnFrontDisconnected(int nReason);
	///������ʱ���档����ʱ��δ�յ�����ʱ���÷��������á�
	///@param nTimeLapse �����ϴν��ձ��ĵ�ʱ��
	virtual void OnHeartBeatWarning(int nTimeLapse);
	///�ͻ�����֤��Ӧ
	virtual void OnRspAuthenticate(CThostFtdcRspAuthenticateField* pRspAuthenticateField, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///��¼������Ӧ
	virtual void OnRspUserLogin(CThostFtdcRspUserLoginField* pRspUserLogin, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///����Ӧ��
	virtual void OnRspError(CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///�����ѯ��Լ��Ӧ
	virtual void OnRspQryInstrument(CThostFtdcInstrumentField* pInstrument, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);
	///�����ѯ������Ӧ
	virtual void OnRspQryDepthMarketData(CThostFtdcDepthMarketDataField* pDepthMarketData, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

};
