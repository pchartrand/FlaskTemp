#!/bin/bash
export MEMCACHED_HOST=192.168.1.27:11211
export ARDUINO_NUMBER_OF_INPUTS=5
cd ~/Arduino/FlaskTemp
. ~/.virtualenvs/flask-temp/bin/activate
nohup ./tempreport.py &
