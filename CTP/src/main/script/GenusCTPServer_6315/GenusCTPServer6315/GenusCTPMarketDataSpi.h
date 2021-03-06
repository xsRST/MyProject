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
	
	///用户登录请求
	virtual int ReqUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID) ;
	///登出请求
	virtual int ReqUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID) ;
	///订阅行情。
	///@param ppInstrumentID 合约ID  
	///@param nCount 要订阅/退订行情的合约个数
	///@remark 
	virtual int SubscribeMarketData(char* ppInstrumentID[], int nCount);

	///退订行情。
	///@param ppInstrumentID 合约ID  
	///@param nCount 要订阅/退订行情的合约个数
	///@remark 
	virtual int UnSubscribeMarketData(char* ppInstrumentID[], int nCount);


	///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
	virtual void OnFrontConnected();
	///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
	///@param nReason 错误原因
	///        0x1001 网络读失败
	///        0x1002 网络写失败
	///        0x2001 接收心跳超时
	///        0x2002 发送心跳失败
	///        0x2003 收到错误报文
	virtual void OnFrontDisconnected(int nReason) ;
	///心跳超时警告。当长时间未收到报文时，该方法被调用。
	///@param nTimeLapse 距离上次接收报文的时间
	virtual void OnHeartBeatWarning(int nTimeLapse);
	///登录请求响应
	virtual void OnRspUserLogin(CThostFtdcRspUserLoginField* pRspUserLogin, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///错误应答
	virtual void OnRspError(CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///订阅行情应答
	void OnRspSubMarketData(CThostFtdcSpecificInstrumentField* pSpecificInstrument, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///深度行情通知
	virtual void OnRtnDepthMarketData(CThostFtdcDepthMarketDataField* pDepthMarketData);
};

