#!/usr/bin/env python
#- coding: utf-8 -#

import os
import json
import datetime
from time import sleep
import matplotlib

matplotlib.use('Agg')  #graphical backend not requiring X11
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, make_response, url_for, redirect
from pylab import savefig
from temperature_monitor.lib.constants import ARDUINO_NUMBER_OF_INPUTS
from temperature_monitor.lib.store import Store
from temperature_monitor.lib.storeseriesfetcher import StoreSeriesFetcher
from temperature_monitor.lib.tempseriesplot import plot_temperatures
from temperature_monitor.lib.templib import get_time
from storecache import StoreCache

labels = [ u'Extérieur', u'Sous-sol', u'C. à coucher', u'Bureau', u'Grenier',  u'Abeilles']
REFERENCE_SERIE = 3
DATETIME_SECONDS = '%Y-%m-%d %H:%M:%S'
DATETIME_MINUTES = '%Y-%m-%d %H:%M'
store = Store()
weekly_cache = StoreCache()
monthly_cache = StoreCache()

app = Flask(__name__)

NUMBER_OF_MEASUREMENTS_IN_GRAPH = 240
USE_WEB_FONTS = False
USE_JQUERY = False
USE_MG_DEV_VERSION = False
REFRESH_INTERVAL = 300
KEPT_MINUTE = '0'
KEPT_HOUR = '00'

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


def series_to_json(series, store=True):
    as_json = []
    for n, serie  in enumerate(series):
        serie_as_json = []
        for point in serie:
            date_value = point[0].strftime(DATETIME_MINUTES)
            value = round(point[1], 1)
            serie_as_json.append(
                dict(
                    date=date_value,
                    value=value
                )
            )
            if store:
                store_if_kept_minute(n, date_value, value)
                store_if_kept_hour(n, date_value, value)
        as_json.append(serie_as_json)
    return as_json


def store_if_kept_minute(serie, date_value, value):
    if date_value.endswith(KEPT_MINUTE):
        weekly_cache.add_to_cache(serie, date_value, value)

def store_if_kept_hour(serie, date_value, value):
    if date_value.endswith(KEPT_HOUR):
        monthly_cache.add_to_cache(serie, date_value, value)


@app.route('/temperatures', methods=['GET'])
def temperatures():
    results = get_temperatures()
    if request.args.get('format') == u'html':
        return render_template("temperatures.html", results=results)
    return json.dumps(results)


@app.route('/temperatures/<line>', methods=['GET'])
def temperature(line):
    results = get_one_temperature(line).values()[0]
    if request.args.get('format') == u'html':
        return render_template("temperature.html", **results)

    return json.dumps(results)

def preload():
    fetcher = StoreSeriesFetcher(store)
    fetcher.fetch(60 * ARDUINO_NUMBER_OF_INPUTS)

@app.route('/weekly-temperature-data.json', methods=['GET'])
def send_weekly_data():
    preload()
    too_old = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime(DATETIME_SECONDS)
    weekly_cache.delete_everything_older_than(too_old)

    store_as_lol = []
    for serie in weekly_cache.get_series():
        serie_as_list = weekly_cache.get_measurements(serie)
        store_as_lol.append(serie_as_list)
    return app.response_class(
        response=json.dumps(store_as_lol),
        status=200,
        mimetype='application/json'
    )

@app.route('/monthly-temperature-data.json', methods=['GET'])
def send_monthly_data():
    preload()

    store_as_lol = []
    too_old = (datetime.datetime.now()- datetime.timedelta(days=32)).strftime(DATETIME_SECONDS)
    monthly_cache.delete_everything_older_than(too_old)

    for serie in monthly_cache.get_series():
        serie_as_list = monthly_cache.get_measurements(serie)
        store_as_lol.append(serie_as_list)
    return app.response_class(
        response=json.dumps(store_as_lol),
        status=200,
        mimetype='application/json'
    )


@app.route('/temperature-data.json', methods=['GET'])
def send_data():
    n = int(request.args.get('n', NUMBER_OF_MEASUREMENTS_IN_GRAPH))
    fetcher = StoreSeriesFetcher(store)
    series = fetcher.fetch(n * ARDUINO_NUMBER_OF_INPUTS)
    series_as_json = series_to_json(series)

    return app.response_class(
        response=json.dumps(series_as_json),
        status=200,
        mimetype='application/json'
    )


@app.route('/weekly-temperatures-graph', methods=['GET'])
def weekly_graph():
    resp = make_response(
        render_template(
            'weekly-graph.html',
            datetime=datetime.datetime.now().strftime(DATETIME_SECONDS),
            use_web_fonts=USE_WEB_FONTS,
            use_jquery=USE_JQUERY,
            dev_version=USE_MG_DEV_VERSION,
            labels=labels,
            show_reload=weekly_cache.measurements_count() == 0
        )
    )
    resp.headers['REFRESH'] = REFRESH_INTERVAL
    return resp

@app.route('/monthly-temperatures-graph', methods=['GET'])
def monthly_graph():
    resp = make_response(
        render_template(
            'monthly-graph.html',
            datetime=datetime.datetime.now().strftime(DATETIME_SECONDS),
            use_web_fonts=USE_WEB_FONTS,
            use_jquery=USE_JQUERY,
            dev_version=USE_MG_DEV_VERSION,
            labels=labels,
            show_reload=monthly_cache.measurements_count() == 0
        )
    )
    resp.headers['REFRESH'] = REFRESH_INTERVAL
    return resp

@app.route('/temperature-graph', methods=['GET'])
def graph():
    n = int(request.args.get('n',NUMBER_OF_MEASUREMENTS_IN_GRAPH))
    duration = "{} h".format(n / 60) if n > 60 else "{} min".format(n)
    resp = make_response(
        render_template(
            'graph.html',
            datetime=datetime.datetime.now().strftime(DATETIME_SECONDS),
            n=n,
            more=n * 2,
            less=n / 2,
            use_web_fonts=USE_WEB_FONTS,
            use_jquery=USE_JQUERY,
            dev_version=USE_MG_DEV_VERSION,
            duration=duration,
            labels=labels
        )
    )
    resp.headers['REFRESH'] = REFRESH_INTERVAL
    return resp


@app.route('/temperature-plots', methods=['GET'])
def show_variations():
    plt.clf()
    fetcher = StoreSeriesFetcher(store)
    series = fetcher.fetch()
    filename = 'temperatures_%s.png' % series[0][0][0]
    file_path = os.path.join('static/', filename)

    for s in series:
        s.reverse()
    
    plot_temperatures(plt, series, labels, [ 'green', 'royalblue', 'crimson', 'purple', 'blue', 'orange'])
    if not os.path.exists(file_path):
        savefig(file_path, dpi=300)

    return render_template('variations.html', file_path=file_path, date_time=get_time())


def dump_serie(serie_cache, file_name):
    store_as_lol = []
    for serie in serie_cache.get_series():
        serie_as_list = serie_cache.get_measurements(serie)
        store_as_lol.append(serie_as_list)
    with open("{} {}.json".format(file_name, datetime.datetime.now().strftime(DATETIME_SECONDS) ), 'w') as outfile:
        json.dump(store_as_lol, outfile)


@app.route('/temperatures-dump', methods=['GET'])
def temperatures_dump():
    dump_serie(monthly_cache, 'monthly')
    dump_serie(weekly_cache, 'weekly')
    return "done {}".format(datetime.datetime.now().strftime(DATETIME_SECONDS))


@app.route('/monthly-temperatures-load', methods=['GET'])
def load_monthly_serie():
    load_serie(monthly_cache, 'monthly')
    return redirect(url_for('monthly_graph'))


@app.route('/weekly-temperatures-load', methods=['GET'])
def load_weekly_serie():
    load_serie(weekly_cache, 'weekly')
    return redirect(url_for('weekly_graph'))


def load_serie(cache, period):
    file_path = os.path.join(os.path.dirname(__file__), "{}.json".format(period))
    with open(file_path) as jsonfile:
        data = json.load(jsonfile)
        for i, serie in enumerate(data):
            for point in serie:
                cache.add_to_cache(i, point['date'], point['value'])

def retry():
    try:
        app.run(host='0.0.0.0', debug=True)
    except:
        sleep(3)
        print("caught exception: will retry")
        retry()




if __name__ == '__main__':
    retry()
