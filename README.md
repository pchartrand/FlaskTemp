## FlaskTemp : a site to see current temperature readings and 24h trends.

Flask is a python web micro-framework.

[temperature-monitor](https://github.com/pchartrand/temperature-monitor) is a python library that captures time series of temperature data from an arduino (using pyserial), 
stores it in a memcached store for 24 hours and allows to graph the data using mathplotlib.

It contains:

### tempreport.py

The flask app. Requires temperature-monitor, json, matplotlib, pylab and flask.

### start_reporter.sh

A script that launches the flask app and sets it's environment

### sample_crontab.txt

A crontab entry that generates graphs at fixed intervals.
