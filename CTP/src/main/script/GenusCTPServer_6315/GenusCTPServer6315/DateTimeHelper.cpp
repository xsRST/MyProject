#include "pch.h"
#include "DateTimeHelper.h"
using namespace std;

DateTimeHelper* g_pDateTimeHelper = NULL;
DateTimeHelper::DateTimeHelper(void)
{
}


DateTimeHelper::~DateTimeHelper(void)
{
}

DateTimeHelper* DateTimeHelper::GetInstance()
{
	if (NULL == g_pDateTimeHelper)
	{
		g_pDateTimeHelper = new DateTimeHelper();
	}
	return g_pDateTimeHelper;
}

string DateTimeHelper::GetTime()
{
	time_t time_seconds = time(0);
	struct tm now_time;

	localtime_s(&now_time, &time_seconds);

	char szCurrentDateTime[50] = "";
	sprintf_s(szCurrentDateTime, "%d-%02d-%02d %02d:%02d:%02d", now_time.tm_year + 1900, now_time.tm_mon + 1,
		now_time.tm_mday, now_time.tm_hour, now_time.tm_min, now_time.tm_sec);
	return szCurrentDateTime;
}
