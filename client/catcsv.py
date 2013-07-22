# -*- coding: utf-8 -*-
import os
import csv
import datetime
import urllib2
import json

SERVER_URL = "http://localhost:5000"

def inputCSV(directory = u"./csv_files/"):
    files = filter(lambda x: x[-4:]==".csv", os.listdir(directory))
    files.sort()

    data = []
    for filename in files:
        incsv = csv.reader(open(directory + filename, 'rb'))
        print filename
        
        cells = []
        for row in incsv:
            cells.append(row)

        for row in cells[202:262]:
            if row[0] == '#BeginMark':
                break
            timedata = datetime.datetime.strptime(row[0], "%Y/%m/%d %H:%M:%S")

            if timedata.second == 0:
                data.append([row[0], row[2], row[3]])

    jdata = json.dumps({'json':data})
    print "size:" + str(len(jdata))
    req = urllib2.Request(SERVER_URL + "/set/data", jdata, {'Content-Type':'application/json'})
    res = urllib2.urlopen(req)
    print res.read()
    f = open('cache.txt', 'w')
    f.write(jdata)
    f.close()


def main():
    inputCSV()
    raw_input('END --> ')


if __name__ == '__main__':
    main()
