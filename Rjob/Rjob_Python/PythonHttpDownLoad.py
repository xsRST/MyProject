# -*- coding: UTF-8 -*-
import optparse
import os

import requests

if __name__ == '__main__':
    p = optparse.OptionParser(description="DownLoad Hist File")
    p.add_option("-u", "--url", dest="url", help="remote url like 'http://192.168.2.59:8080/'")
    p.add_option("-o", "--outPath", dest="outPath", help="outPath like 'D:/''")
    p.add_option("-f", "--fileNames", dest="fileNames",
                 help="fileName like 'GenusHistFile.tar.gz^GenusHistFile.tar.gz.md5 '")
    options, arguments = p.parse_args()
    if not options.url:
        print ("invalid url ")
        os._exit(0)
    elif not options.fileNames:
        print ("invalid fileName")
        os._exit(0)
    elif not options.outPath:
        print ("invalid outPath")
        os._exit(0)
    url = options.url
    fileNames = options.fileNames
    outPath = options.outPath
    for fileName in str(fileNames).split(","):
        try:
            downLoadUrl = url + "/" + fileName
            r = requests.get(downLoadUrl)
            with open(os.path.join(outPath, fileName), "wb") as f:
                f.write(r.content)
        except Exception, e:
            print("Fail " + str(e))
            pass
