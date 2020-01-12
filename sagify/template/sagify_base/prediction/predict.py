from __future__ import absolute_import

# Do not remove the following line
import sys;sys.path.append(".")  # NOQA
from sagify_base.prediction.prediction import predict as predict_function


def predict(json_input):
    """
    Prediction given the request input
    :param json_input: [dict], request input
    :return: [dict], prediction
    """
    return predict_function(json_input=json_input)
