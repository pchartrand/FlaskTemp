#!/usr/bin/env python
#- coding: utf-8 -#

import os
import json
import datetime

import matplotlib
matplotlib.use('Agg')  #graphical backend not requiring X11
import matplotlib.pyplot as plt

from flask import Flask, render_template, request
from pylab import savefig
from temperature_monitor.lib.constants import ARDUINO_NUMBER_OF_INPUTS
from temperature_monitor.lib.store import Store
from temperature_monitor.lib.storeseriesfetcher import StoreSeriesFetcher
from temperature_monitor.lib.tempseriesplot import plot_temperatures
from temperature_monitor.lib.templib import get_time

labels =[ u'Extérieur', u'Sous-sol', u'C. à coucher', u'Bureau', u'Grenier',  u'Abeilles']

store = Store()
app = Flask(__name__)

NUMBER_OF_MEASUREMENTS_IN_GRAPH = 360
USE_WEB_FONTS = False
USE_JQUERY = True
USE_MG_DEV_VERSION = False

def get_one_temperature(line):
    (line, temp, timestamp) = store.get_one(store.last() - int(line))
    if temp is None:
        return "Nothing found in memcached, or memcached is down."
    else:
        data = dict(temp="%.2f" %temp, timestamp=timestamp)
        return{'line_%s' % line: data}


def get_temperatures():
    results = {}
    for i in range(ARDUINO_NUMBER_OF_INPUTS):
        results.update(get_one_temperature(i))
    return results


@app.route('/temperatures', methods=['GET'])
def temperatures():
    results = get_temperatures()
    if request.args.get('format') == u'html':
        print results
        return render_template("temperatures.html", results=results)
    return json.dumps(results)


@app.route('/temperatures/<line>', methods=['GET'])
def temperature(line):
    results = get_one_temperature(line).values()[0]
    if request.args.get('format') == u'html':
        return render_template("temperature.html", **results)

    return json.dumps(results)

@app.route('/temperature-data.json', methods=['GET'])
def send_data():
    n = int(request.args.get('n',NUMBER_OF_MEASUREMENTS_IN_GRAPH))
    fetcher = StoreSeriesFetcher(store)
    series = fetcher.fetch(n * ARDUINO_NUMBER_OF_INPUTS)
    series_as_json = []
    for serie in series:
        serie_as_json = []
        for point in serie:
            serie_as_json.append(
                dict(
                    date=point[0].strftime('%Y-%m-%d %H:%M'),
                    value=round(point[1], 1)
                )
            )
        series_as_json.append(serie_as_json)

    return app.response_class(
        response=json.dumps(series_as_json),
        status=200,
        mimetype='application/json'
    )


@app.route('/temperature-graph', methods=['GET'])
def graph():
    n = int(request.args.get('n',NUMBER_OF_MEASUREMENTS_IN_GRAPH))
    return render_template(
        'graph.html',
        datetime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        n=n,
        more=n * 2,
        less=n / 2,
        use_web_fonts=USE_WEB_FONTS,
        use_jquery=USE_JQUERY,
        dev_version=USE_MG_DEV_VERSION
    )


@app.route('/temperature-plots', methods=['GET'])
def show_variations():
    plt.clf()
    fetcher = StoreSeriesFetcher(store)
    series = fetcher.fetch()
    filename = 'temperatures_%s.png' % series[0][0][0]
    file_path = os.path.join('static/', filename)

    for s in series:
        s.reverse()
    
    plot_temperatures(plt, series, labels, [ 'green', 'royalblue', 'crimson', 'purple','blue','orange'])
    if not os.path.exists(file_path):
        savefig(file_path, dpi=300)

    return render_template('variations.html', file_path=file_path, date_time=get_time())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
