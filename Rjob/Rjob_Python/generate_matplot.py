# coding=utf-8
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

import jobs.ConfigChina

matplotlib.style.use('ggplot')
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
mpl.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
mpl.rc('xtick', labelsize=10)  # 设置坐标轴刻度显示大小
mpl.rc('ytick', labelsize=10)
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.dpi'] = 300

out_path = "C:\JINNA\\trunk/"
filname = out_path + "GenusHistIntervalStats20191127.csv"
data = pd.read_csv(filname, names=jobs.ConfigChina.GenusHistIntervalStats_header, encoding="utf-8", engine='c')
new_data = data[data["Symbol"] == "00005.HK"]
new_data.reset_index(drop=True, inplace=True)
ax1 = new_data.plot(color="blue", x="StartTime", y=["Volume"], kind="bar", sharex=True, grid=True)
new_data["VolumeSD"].plot(color="r", secondary_y=["VolumeSD"])

image_path = out_path + "volume.png"
plt.xticks(rotation=60)
plt.tight_layout()
plt.grid()
plt.savefig(image_path)
plt.show()
