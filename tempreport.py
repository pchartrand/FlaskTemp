import os
import json
import matplotlib
matplotlib.use('Agg')  #graphical backend not requiring X11
import matplotlib.pyplot as plt

from flask import Flask, render_template, request
from pylab import savefig

from temperature_monitor.lib.store import Store
from temperature_monitor.lib.storeseriesfetcher import StoreSeriesFetcher
from temperature_monitor.lib.tempseriesplot import plot_temperatures
from temperature_monitor.lib.templib import get_time

store = Store()
app = Flask(__name__)


def get_one_temperature(line):
    (line, temp, timestamp) = store.get_one(store.last() - int(line))
    if temp is None:
        return "Nothing found in memcached, or memcached is down."
    else:
        data = dict(temp="%.2f" %temp, timestamp=timestamp)
        return{'line_%s' % line: data}


def get_temperatures():
    results = {}
    for i in range(2):
        results.update(get_one_temperature(i))
    return results


@app.route('/temperatures', methods=['GET'])
def temperatures():
    results = get_temperatures()
    return json.dumps(results)


@app.route('/temperatures/<line>', methods=['GET'])
def temperature(line):
    results = get_one_temperature(line)
    if request.args.get('format') == u'html':
        return render_template("temperature.html",**results['line_0'])

    return json.dumps(results)

@app.route('/temperature-plots', methods=['GET'])
def show_variations():
    plt.clf()
    fetcher = StoreSeriesFetcher(store)
    s0, s1 = fetcher.fetch()
    for s in (s0, s1):
        s.reverse()
    plot_temperatures(plt, s0, s1)
    filename = 'temperatures_%s.png' % s0[0][0]
    file_path = os.path.join('static/', filename)
    if not os.path.exists(file_path):
        savefig(file_path, dpi=300)

    return render_template('variations.html', file_path=file_path, date_time=get_time())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
