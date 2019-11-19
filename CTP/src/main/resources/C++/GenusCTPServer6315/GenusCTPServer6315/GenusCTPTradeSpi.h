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

	///客户端认证请求
	virtual int ReqAuthenticate(CThostFtdcReqAuthenticateField* pReqAuthenticateField, int nRequestID) ;
	///用户登录请求
	virtual int ReqUserLogin(CThostFtdcReqUserLoginField* pReqUserLoginField, int nRequestID) ;
	///登出请求
	virtual int ReqUserLogout(CThostFtdcUserLogoutField* pUserLogout, int nRequestID);
	///请求查询合约
	virtual int ReqQryInstrument(CThostFtdcQryInstrumentField* pQryInstrument, int nRequestID) ;
	///请求查询行情
	virtual int ReqQryDepthMarketData(CThostFtdcQryDepthMarketDataField* pQryDepthMarketData, int nRequestID) ;

	///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
	virtual void OnFrontConnected();
	///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
	///@param nReason 错误原因
	///        0x1001 网络读失败
	///        0x1002 网络写失败
	///        0x2001 接收心跳超时
	///        0x2002 发送心跳失败
	///        0x2003 收到错误报文
	virtual void OnFrontDisconnected(int nReason);
	///心跳超时警告。当长时间未收到报文时，该方法被调用。
	///@param nTimeLapse 距离上次接收报文的时间
	virtual void OnHeartBeatWarning(int nTimeLapse);
	///客户端认证响应
	virtual void OnRspAuthenticate(CThostFtdcRspAuthenticateField* pRspAuthenticateField, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///登录请求响应
	virtual void OnRspUserLogin(CThostFtdcRspUserLoginField* pRspUserLogin, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///错误应答
	virtual void OnRspError(CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

	///请求查询合约响应
	virtual void OnRspQryInstrument(CThostFtdcInstrumentField* pInstrument, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);
	///请求查询行情响应
	virtual void OnRspQryDepthMarketData(CThostFtdcDepthMarketDataField* pDepthMarketData, CThostFtdcRspInfoField* pRspInfo, int nRequestID, bool bIsLast);

};
