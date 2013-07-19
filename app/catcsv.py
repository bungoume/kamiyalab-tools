# -*- coding: utf-8 -*-
import os
import csv
import datetime
from pyquery import PyQuery as pq
from peewee import SqliteDatabase
from models import *
import re

sqlite_db.connect()
sqlite_db.set_autocommit(False)

def create_tables():
    JmaTemp.create_table()
    ResearchTemp.create_table()

def inputCSV(directory = u"./csv_files/"):
    files = filter(lambda x: x[-4:]==".csv", os.listdir(directory))
    files.sort()

    for filename in files:
        incsv = csv.reader(open(directory + filename, 'rb'))

        cells = []
        for row in incsv:
            cells.append(row)

        for row in cells[202:262]:
            timedata = datetime.datetime.strptime(row[0], "%Y/%m/%d %H:%M:%S")

            if timedata.second == 0:
                researchTemp = ResearchTemp(datetime=timedata, temperature1=float(row[2]), temperature2=float(row[3]), data_type="average-1min")
                try:
                    researchTemp.save()
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
        if temperature == u"×":
            continue
        temperature = re.sub(r'[\]\)\ ]', '', temperature)

        jmaTemp = JmaTemp(datetime=timedata, temperature=float(temperature), data_type="10min")
        try:
            jmaTemp.save()
        except:
            pass


def calcAverage(year, month, day, hour):
    timedata = datetime.datetime(year, month, day, hour)
    data = JmaTemp.select().where(
        (JmaTemp.datetime >= timedata) &
        (JmaTemp.datetime < timedata+datetime.timedelta(hours=+1))
    )
    average = reduce(lambda a,b: a+b.temperature, data, 0) / data.count()
    jmaTemp = JmaTemp(datetime=timedata, temperature=float(average), data_type='1hour')
    try:
        jmaTemp.save()
    except:
        pass


def main():
    #inputCSV()
    #create_tables()
    d = datetime.datetime(2012,1,1)
    for a in range(366):
        inputJmaTemp(d.year,d.month,d.day)
        d += datetime.timedelta(days=+1)
    sqlite_db.commit()


if __name__ == '__main__':
    main()
