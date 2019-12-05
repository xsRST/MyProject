#!/bin/sh

date

if [ -f $HOME/.clientrc ];then
    . $HOME/.clientrc
fi

. $HOME/.bashrc



export WORKDIR=$HOME/hist_data

DATETODAY=${1:-`date +\%Y\%m\%d`}

export MDLevel=L2; 


sleep 3

cd ${WORKDIR}

CMD="python ${WORKDIR}/start_make_file.py  -d ${DATETODAY}"
echo "------------------------------------------------------------------------------------------------------------------"
echo "Running $CMD"
echo "------------------------------------------------------------------------------------------------------------------"
$CMD
#
#sleep 3
#export Today=${DATETODAY2};
#CMD="/home/genusdev01/EOD/Hist_Data_Upload/bin/sendHistDataToPlayback.sh "
#echo "------------------------------------------------------------------------------------------------------------------"
#echo "Running $CMD"
#$CMD
#
#
#sleep 3
#
#CMD="python $HOME/Python/misc/resetvolume.py -d ${DATETODAY}"
#echo "------------------------------------------------------------------------------------------------------------------"
#echo "Running $CMD"
#echo "------------------------------------------------------------------------------------------------------------------"
#$CMD

