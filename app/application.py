# -*- coding: utf-8 -*-

from flask import request, render_template, flash, url_for, redirect, jsonify, session, json, Response, g


from pyquery import PyQuery as pq
import urllib, urllib2
import re, datetime
import time

from models import *
import unicodedata
import re


from flask import Flask
import copy

app = Flask(__name__)



def test():
    pass

def getData(start, end):
    researchData = ResearchTemp.select().where(
        (ResearchTemp.datetime >= start) & 
        (ResearchTemp.datetime <= end)
    )

    jmaData = JmaTemp.select().where(
        (ResearchTemp.datetime >= start) & 
        (ResearchTemp.datetime <= end)
    )

    hoge = {}
    for temp in jmaData:
        d = temp.datetime.strftime("%Y-%m-%d %H:%M:%S")
        hoge[d] = [temp.temperature]

    for temp in researchData:
        d = temp.datetime.strftime("%Y-%m-%d %H:%M:%S")
        m = temp.datetime.minute/10 *10
        d2 = temp.datetime.strftime("%Y-%m-%d %H:") + str(m).zfill(2) + ":00"
        if d not in hoge:
            if d2 in hoge:
                hoge[d] = [hoge[d2][0]]
            else:
                hoge[d] = [None]
        hoge[d].extend([temp.temperature1,temp.temperature2])

    data = []
    for temp in hoge:
        if not len(hoge[temp]) == 3:
            hoge[temp].extend([None,None])
        n = [temp]
        n.extend(hoge[temp])
        data.append(n)

    data.sort(key=lambda x:x[0])
    return data


@app.route("/json/mix")
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
    print data[:5]

    import csv,cStringIO
    csv_file = cStringIO.StringIO()
    writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerows(data)
    csv_data = csv_file.getvalue()

    return Response(csv_data, mimetype='text/csv')


@app.route("/")
def home():
    #programs = Program.query().order(Program.cate, Program.time_s)
    #return render_template('program_list.html', programs=programs)
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