# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, flash, jsonify, Response, g

from pyquery import PyQuery as pq
import datetime, re

from models import *

app = Flask(__name__)


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


def getData(start, end, mode="minutes"):
    researchData = ResearchData.select().where(
        (ResearchData.datetime >= start) &
        (ResearchData.datetime <= end)
    )

    hoge = {}
    for temp in researchData:
        d = temp.datetime.strftime("%Y-%m-%d %H:%M:%S")
        if mode == 'hours' and temp.datetime.minute != 0:
            continue
        if d not in hoge:
            hoge[d] = {}
        hoge[d][temp.name] = temp.data
        hoge[d]["datetime"] = temp.datetime

    data = []
    for key in hoge:
        obj = hoge[key]
        t0 = obj.get('temperature-jma')
        t1 = obj.get('temperature-1')
        t2 = obj.get('temperature-2')
        if 'temperature-jma' not in obj:
            x  = obj['datetime'].minute%10
            m1 = obj['datetime'].minute/10 *10
            d1 = obj['datetime'].strftime("%Y-%m-%d %H:") + str(m1).zfill(2) + ":00"
            dt2 = obj['datetime']+datetime.timedelta(minutes=+10)
            m2 = dt2.minute/10 *10
            d2 = dt2.strftime("%Y-%m-%d %H:") + str(m2).zfill(2) + ":00"
            try:
                t0 = round( (hoge[d1].get('temperature-jma') * (10-x) + hoge[d2].get('temperature-jma') * x)/10 ,1)
            except:
                t0 = hoge[d1].get('temperature-jma')

        data.append([key, t0, t1, t2])

    data.sort(key=lambda x:x[0])
    return data


@app.route("/json")
def json_mix():
    start = datetime.datetime.strptime(request.args.get('start'), "%Y-%m-%d")
    end   = datetime.datetime.strptime(request.args.get('end'), "%Y-%m-%d")
    mode = 'minutes'
    if (end - start).days > 8:
        mode = 'hours'
    data = getData(start,end, mode)
    return jsonify(data=data)


@app.route('/output.csv')
def generate_csv():
    start = datetime.datetime.strptime(request.args.get('start'), "%Y-%m-%d")
    end   = datetime.datetime.strptime(request.args.get('end'), "%Y-%m-%d")

    data = getData(start,end)

    data[:0] = [['Datetime', 'JMA temperature',"Temp1","Temp2"]]

    import csv,cStringIO
    csv_file = cStringIO.StringIO()
    writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerows(data)
    csv_data = csv_file.getvalue()

    return Response(csv_data, mimetype='text/csv')


@app.route('/output2.csv')
def generate_csv2():
    start = datetime.datetime.strptime(request.args.get('start'), "%Y-%m-%d")
    end   = datetime.datetime.strptime(request.args.get('end'), "%Y-%m-%d")

    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + datetime.timedelta(days=+n)

    times = [
        ["08:35", "09:05"],
        ["10:00", "10:30"],
        ["12:20", "13:00"],
        ["13:40", "14:20"],
        ["16:00", "16:30"],
        ["17:20", "17:50"]
    ]

    data = []

    for single_date in daterange(start, end):
        day = single_date.strftime("%Y-%m-%d ")
        day_data = [day,]

        for time in times:
            start_time = datetime.datetime.strptime(day+time[0], "%Y-%m-%d %H:%M")
            end_time   = datetime.datetime.strptime(day+time[1], "%Y-%m-%d %H:%M")
            researchData = ResearchData.select().where(
                (ResearchData.name == 'temperature-1') &
                (ResearchData.datetime >= start_time) &
                (ResearchData.datetime <= end_time)
            )
            if researchData.count() == 0:
                average = 0
            else:
                sum_data = reduce(lambda x, y: x + y.data, researchData,0)
                average = sum_data/researchData.count()
            day_data.append(average)
        data.append(day_data)

    import csv,cStringIO
    csv_file = cStringIO.StringIO()
    writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerows(data)
    csv_data = csv_file.getvalue()

    return Response(csv_data, mimetype='text/csv')



@app.route('/set/jma')
def setJma():
    g.db.set_autocommit(False)
    now = datetime.datetime.now()
    try:
        d = ResearchData.select().order_by(ResearchData.datetime.desc()).limit(1).get().datetime
    except ResearchData.DoesNotExist:
        #初期化
        d = datetime.datetime.now() + datetime.timedelta(days=-365)
    while d < now:
        inputJmaTemp(d.year,d.month,d.day)
        d += datetime.timedelta(days=+1)
    g.db.commit()
    return "ok"


@app.route('/set/data', methods=['POST'])
def setData():
    g.db.set_autocommit(False)
    data = request.json['json']

    for obj in data:
        timedata = datetime.datetime.strptime(obj[0], "%Y/%m/%d %H:%M:%S")
        researchData1 = ResearchData(datetime=timedata, name="temperature-1", data=float(obj[1]), data_type="raw-1min")
        researchData2 = ResearchData(datetime=timedata, name="temperature-2", data=float(obj[2]), data_type="raw-1min")
        try:
            researchData1.save()
            researchData2.save()
        except:
            pass
    g.db.commit()
    return "ok"


@app.route("/")
def home():
    return render_template('graph.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.before_request
def before_request():
    g.db = sqlite_db
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response


if __name__ == '__main__':
    app.run(debug=True)
