# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, flash, url_for, redirect, jsonify, session, Response, g

from pyquery import PyQuery as pq
import urllib, urllib2
import re
import datetime
import copy

from models import *

app = Flask(__name__)


def getData(start, end):
    researchData = ResearchData.select().where(
        (ResearchData.datetime >= start) & 
        (ResearchData.datetime <= end)
    )

    hoge = {}
    for temp in researchData:
        d = temp.datetime.strftime("%Y-%m-%d %H:%M:%S")
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
            m = obj['datetime'].minute/10 *10
            d2 = obj['datetime'].strftime("%Y-%m-%d %H:") + str(m).zfill(2) + ":00"
            t0 = hoge[d2].get('temperature-jma')
        data.append([key, t0, t1, t2])

    data.sort(key=lambda x:x[0])
    return data


@app.route("/json")
def json_mix():
    start = datetime.datetime.strptime(request.args.get('start'), "%Y-%m-%d")
    end   = datetime.datetime.strptime(request.args.get('end'), "%Y-%m-%d")

    data = getData(start,end)

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