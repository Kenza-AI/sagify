# This is the file that implements a flask server to do inferences. It's the file that you will
#  modify to implement the scoring for your own algorithm.

from __future__ import print_function

import json

import flask

from . import predict


app = flask.Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy"""
    return flask.Response(response='\n', status=200, mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def transformation():
    """Do an inference on a single batch of data. In this sample server, we take data as JSON"""
    if flask.request.content_type == 'application/json':
        data = flask.request.get_json()
    else:
        return flask.Response(
            response=json.dumps({'message': 'This predictor only supports JSON data'}),
            status=415,
            mimetype='application/json'
        )

    result = predict.predict(data)

    return flask.Response(response=json.dumps(result), status=200, mimetype='application/json')
