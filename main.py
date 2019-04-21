#!/usr/bin/env python

import os
import sys
import json
import signal
import requests
import websocket
from prometheus_client import start_http_server, Gauge, Counter

SENSE_EMAIL = os.getenv("SENSE_EMAIL")
SENSE_PASSWORD = os.getenv("SENSE_PASSWORD")
METRICS_PORT = int(os.getenv("METRICS_PORT"))

API_ENDPOINT = "https://api.sense.com/apiservice/api/v1"

grid_watts = Gauge("sense_grid_watts", "Grid watts")
solar_watts = Gauge("sense_solar_watts", "Solar watts")
measure_count = Counter("sense_measure_count", "Measure count")


def on_open(ws):
    print "### WS opened ###"


def on_message(ws, message):
    try:
        payload = json.loads(message)
        payload_type = payload["type"]
        if payload_type == "realtime_update":
            payload = payload["payload"]
            grid_watts.set(payload["w"])
            solar_watts.set(payload.get("solar_w", 0.0))
            measure_count.inc()
        else:
            print "Ignored WS message '%s'" % payload_type
    except:
        print sys.exc_info()


def on_error(ws, error):
    print "### WS error ###\n%s" % error


def on_close(ws):
    print "### WS closed ###"


def run():
    # Log-in
    data = {
        "email": SENSE_EMAIL,
        "password": SENSE_PASSWORD,
    }
    response = requests.post("%s/authenticate" % API_ENDPOINT, data=data)
    assert response.status_code == 200
    payload = response.json()
    assert payload["authorized"] == True
    access_token = payload["access_token"]
    assert access_token
    monitor = payload["monitors"][0]

    # Stream
    ws = websocket.WebSocketApp("wss://clientrt.sense.com/monitors/%d/realtimefeed?access_token=%s" % (monitor["id"], access_token), on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


def sighandler(signum, frame):
    print "<SIGTERM received>"
    exit(0)


if __name__ == "__main__":
    print "=== START ==="
    signal.signal(signal.SIGTERM, sighandler)
    try:
        start_http_server(METRICS_PORT)
        run()
    except KeyboardInterrupt:
        print " Interrupted"
        exit(0)
