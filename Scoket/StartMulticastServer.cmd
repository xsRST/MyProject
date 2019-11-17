@echo off
Title=MulticastServer

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
set ROOTDIR=.

REM  -----------------------------------------------------------------------------
REM  set classpath
REM  -----------------------------------------------------------------------------
set CLASSPATH=%ROOTDIR%\Scoket-1.0-SNAPSHOT.jar;%ROOTDIR%\3rd\*

REM  -----------------------------------------------------------------------------
REM  set main class
REM  -----------------------------------------------------------------------------
set APP_MAIN=com.genus.xs.multicast.server.MulticastServer

REM  -----------------------------------------------------------------------------
REM  set application arguments
REM  -----------------------------------------------------------------------------
set APP_ARGS=192.168.2.131 233.36.26.128 6628 

REM  -----------------------------------------------------------------------------
REM  set logging file
REM  -----------------------------------------------------------------------------
set LOGFILE="%ROOTDIR%\%DATE%.MulticastServer.log"

REM  -----------------------------------------------------------------------------
REM  run the command
REM  -----------------------------------------------------------------------------

set COMMAND=java %JAVA_OPTS%
set COMMAND=%COMMAND% -DROOTDIR=%ROOTDIR%
set COMMAND=%COMMAND% -classpath "%CLASSPATH%"
set COMMAND=%COMMAND% %APP_MAIN%
set COMMAND=%COMMAND% %APP_ARGS%

echo %COMMAND%
%COMMAND% > %LOGFILE%
REM  %COMMAND% 


