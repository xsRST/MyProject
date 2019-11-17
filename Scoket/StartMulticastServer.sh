#!/bin/bash
. $HOME/.bashrc

date

DATE=`date +"%Y%m%d"`
	
#  ==========================================================
#  TTF start up script
#  ==========================================================

#  -----------------------------------------------------------------------------
#   java options
#  -----------------------------------------------------------------------------

JAVA_OPTS=

#  -----------------------------------------------------------------------------
#   system parameters
#  -----------------------------------------------------------------------------
 ROOTDIR=.

#  -----------------------------------------------------------------------------
#   classpath
#  -----------------------------------------------------------------------------
 CLASSPATH=${ROOTDIR}\Scoket-1.0-SNAPSHOT.jar;${ROOTDIR}\3rd\*

#  -----------------------------------------------------------------------------
#   main class
#  -----------------------------------------------------------------------------
 APP_MAIN=com.genus.xs.multicast.server.MulticastServer

#  -----------------------------------------------------------------------------
#   application arguments
#  -----------------------------------------------------------------------------
 APP_ARGS="192.168.2.131 233.36.26.128 6628"

#  -----------------------------------------------------------------------------
#   logging file
#  -----------------------------------------------------------------------------
 LOGFILE="${ROOTDIR}\${DATE}.MulticastServer.log"

#  -----------------------------------------------------------------------------
#  run the command
#  -----------------------------------------------------------------------------

COMMAND="$JAVA_HOME/bin/java ${JAVA_OPTS}"
 COMMAND="${COMMAND} -classpath ${CLASSPATH}"
 COMMAND="${COMMAND} $APP_MAIN}"
 COMMAND="${COMMAND} ${APP_ARGS}"

echo ${COMMAND}
${COMMAND} > ${LOGFILE} &
#  ${COMMAND}


