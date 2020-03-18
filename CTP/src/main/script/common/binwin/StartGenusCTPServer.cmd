@echo off
Title=GenusCTPServer

SET DATE=%date:~0,4%%date:~5,2%%date:~8,2%
	
REM  ==========================================================
REM  TTF start up script
REM  ==========================================================

REM  -----------------------------------------------------------------------------
REM  set java options
REM  -----------------------------------------------------------------------------

set JAVA_OPTS=

REM  -----------------------------------------------------------------------------
REM  set system parameters
REM  -----------------------------------------------------------------------------
set ROOTDIR=..

REM  -----------------------------------------------------------------------------
REM  set classpath
REM  -----------------------------------------------------------------------------
set CLASSPATH=%ROOTDIR%\lib\*;%ROOTDIR%\3rd\*

REM  -----------------------------------------------------------------------------
REM  set main class
REM  -----------------------------------------------------------------------------
set APP_MAIN=com.genus.ctp.Application

REM  -----------------------------------------------------------------------------
REM  set application arguments
REM  -----------------------------------------------------------------------------
set APP_ARGS=

REM  -----------------------------------------------------------------------------
REM  set logging file
REM  -----------------------------------------------------------------------------
set LOGFILE="%ROOTDIR%\log\%DATE%.GenusCTPServer.log"

REM  -----------------------------------------------------------------------------
REM  run the command
REM  -----------------------------------------------------------------------------

set COMMAND=java %JAVA_OPTS%
set COMMAND=%COMMAND% -DROOTDIR=%ROOTDIR%
set COMMAND=%COMMAND% -DLOGFILE=%LOGFILE%
set COMMAND=%COMMAND% -classpath "%CLASSPATH%"
set COMMAND=%COMMAND% %APP_MAIN%
set COMMAND=%COMMAND% %APP_ARGS%

echo %COMMAND%
  %COMMAND% > %LOGFILE%
REM  %COMMAND% 


