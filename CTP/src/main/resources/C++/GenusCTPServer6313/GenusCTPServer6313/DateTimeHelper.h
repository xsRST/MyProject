#pragma once
#include "pch.h"
using namespace std;
class DateTimeHelper
{
public:
	DateTimeHelper(void);
	~DateTimeHelper(void);
public:
	std::string GetTime();
public:
	static DateTimeHelper* GetInstance();
};

