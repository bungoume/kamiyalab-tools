# -*- coding: utf-8 -*-
import os
import csv
import datetime
from pyquery import PyQuery as pq
from models import *
import re

sqlite_db.connect()
sqlite_db.set_autocommit(False)


def inputCSV(directory = u"./csv_files/"):
    files = filter(lambda x: x[-4:]==".csv", os.listdir(directory))
    files.sort()

    for filename in files:
        incsv = csv.reader(open(directory + filename, 'rb'))
        print filename
        
        cells = []
        for row in incsv:
            cells.append(row)

        for row in cells[202:262]:
            if raw[0] == '#BeginMark':
                break
            timedata = datetime.datetime.strptime(row[0], "%Y/%m/%d %H:%M:%S")

            if timedata.second == 0:
                researchData1 = ResearchData(datetime=timedata, name="temperature-1", data=float(row[2]), data_type="raw-1min")
                researchData2 = ResearchData(datetime=timedata, name="temperature-2", data=float(row[3]), data_type="raw-1min")
                try:
                    researchData1.save()
                    researchData2.save()
                except:
                    pass


def inputJmaTemp(year, month, day):

    y = str(year)
    m = str(month).zfill(2)
    d = str(day).zfill(2)
    url = "http://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=48&block_no=47610"
    url += "&year=" + y + "&month=" + m + "&day=" + d

    print url
    for a in pq(url=url)("table.data2_s tr"):
        line = pq(a)("td")
        time_text = line.eq(0).html()
        if not time_text:
            continue

        if time_text =="24:00":
            timedata = datetime.datetime.strptime(y+"/"+m+"/"+d+" 00:00", "%Y/%m/%d %H:%M") + datetime.timedelta(days=+1)
        else:
            timedata = datetime.datetime.strptime(y+"/"+m+"/"+d+" "+time_text, "%Y/%m/%d %H:%M")

        #前10分に適用
        timedata = timedata + datetime.timedelta(minutes=-10)
        temperature = line.eq(4).html()
        #データ不備時はパス
        if temperature == u"×":
            continue
        #精度不足時につく文字除去
        temperature = re.sub(r'[\]\)\ ]', '', temperature)

        researchData = ResearchData(datetime=timedata, name="temperature-jma", data=float(temperature), data_type="raw-10min")
        try:
            researchData.save()
        except:
            pass


def main():
    inputCSV()
    d = datetime.datetime.now()
    for a in range(10):
        d += datetime.timedelta(days=-1)
        inputJmaTemp(d.year,d.month,d.day)
    sqlite_db.commit()


if __name__ == '__main__':
    main()
