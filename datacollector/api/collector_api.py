# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Datacollector API resources."""
import json
from datetime import datetime
from flask import Flask, Response, jsonify, request

from datacollector.api.api_collector_handler import CollectorHandler

app = Flask(__name__)
collector_handler = CollectorHandler()


class InvalidParameterException(Exception):
    """Raised in case of invalid request body parameters."""


@app.route('/api/start', methods=['POST'])
def start_collector():
    """Endpoint for starting the collector. Route command to CollectorHandler object."""
    run_id = None

    try:
        data = request.get_json()
        start_delta = data['start']
        stop_delta = data['stop']
        interval = data['interval']
        if ("id" in data) is True:
            run_id = data['id']
        if start_delta < 0 or stop_delta <= 0 or interval <= 0:
            raise InvalidParameterException
    except Exception as e:
        return Response(json.dumps({"ret": "fail",
                                    "message": 'Invalid request body. Example of a request: {"start": 60, '
                                               '"stop": 120, "interval": 60}.'}), status=400)

    if run_id is None:
        run_id = collector_handler.create_run_id()
    else:
        date = datetime.utcnow()
        run_id = run_id + "_" + datetime.strftime(date, "%Y-%m-%dT%H-%M-%S")

    collector_handler.start_agent(start_delta, stop_delta, interval, run_id)
    return Response(json.dumps({"ret": "ok", "message": "Parameters for starting the collector received.", "id": run_id}))


@app.route('/api/stop', methods=['POST'])
def stop_collector():
    """Endpoint for stopping the collector. Route command to CollectorHandler-object."""
    try:
        data = request.get_json()
        run_id = data['id']
        message = collector_handler.stop_agent(run_id)
        return jsonify(message)
    except Exception as e:
        return jsonify(str(e))


@app.route('/api/results/collections', methods=['GET'])
def retrieve_collections():
    """Return names of existing collection runs."""
    data = collector_handler.get_collection_names()
    return Response(json.dumps({"ret": "ok", "message": "Names of collections retrieved successfully.", "data": data}))


@app.route('/api/results/collections/<run_id>/<host>', methods=['GET'])
def retrieve_collection_results(run_id, host):
    """Return results of a collection run using collection name and filename."""
    data = collector_handler.get_collection_results(run_id, host)
    return Response(json.dumps({"ret": "ok", "message": "Results for collection retrieved successfully.", "data": data}))


@app.route('/', methods=['GET'])
def default_get():
    """Entry point for the API."""
    return Response('Datacollector API', 200)


def run():
    """Deploy the API."""
    app.run(host='127.0.0.1', port=5000)
