# encoding=utf-8
import optparse
import os
import time

import jobs.logger
from jobs.GenusHistManager import GenusHistManager

if __name__ == '__main__':
    start_time = time.time()
    jobs.logger.write("start Time .....  ")
    p = optparse.OptionParser(description="Check running mode")
    p.add_option("-d", "--date", dest="date", help="find resource files refer to this date,should be like '20160727' ")

    options, arguments = p.parse_args()
    date = options.date if options.date else time.strftime("%Y%m%d")

    try:
        managet = GenusHistManager(date)
        managet.start()
    except Exception as e:
        jobs.logger.write(e)
        os._exit(0)
        pass
    end_time = time.time()
    jobs.logger.write("end  cost  {0:.2f} 秒".format(end_time - start_time))
    os._exit(0)
    pass
