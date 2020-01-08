#!/usr/bin/env python
# coding=utf-8
import os

import pandas as pd

outDir = "D:\\project\\Genus\\hist_data\\output"
files = os.listdir(outDir)
for file in files:
    print(file)

    file_path = os.path.join(outDir, file)
    if os.path.isfile(file_path) and file.find("Raw") > -1:
        if file.find("China-RawIntervalStats") > -1:
            df = pd.read_csv(file_path)
            df["SpreadSize"] = df["SpreadSize"] * 10
            df.to_csv(file_path, encoding="utf-8", index=False, )

            pass
        pass
    pass
