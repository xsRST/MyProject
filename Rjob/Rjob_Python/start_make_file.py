# encoding=utf-8
import optparse
import os
import time

from jobs.genusHistManager import GenusHistManager
from util import logger

if __name__ == '__main__':
    start_time = time.time()
    logger.write("start Time .....  ")
    p = optparse.OptionParser(description="Check running mode")
    p.add_option("-d", "--date", dest="date", help="find resource files refer to this date,should be like '20160727' ")

    options, arguments = p.parse_args()
    date = options.date if options.date else time.strftime("%Y%m%d")

    try:
        managet = GenusHistManager(date)
        managet.start()
    except Exception as e:
        logger.write(e)
        os._exit(0)
        pass
    end_time = time.time()
    logger.write("end  cost  {0:.2f} 秒".format(end_time - start_time))
    os._exit(0)
    pass
