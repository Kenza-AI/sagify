import json
import os
import pickle

import joblib
import xgboost as xgb


def model_fn(model_dir):
    print("loading XGBoost model from: {}".format(model_dir))

    files = [f for f in os.listdir(model_dir) if os.path.isfile(os.path.join(model_dir, f))]
    model_file_name = files[0]

    print("Files: {}".format(files))

    try:
        loaded_model = xgb.Booster()
        loaded_model.load_model(os.path.join(model_dir, model_file_name))
    except:
        print("XGBoost's load_model didn't work. Trying with joblib now")

        try:
            loaded_model = joblib.load(model_file_name)
        except:
            print("XGBoost's joblib.load didn't work. Trying with pickle now")
            loaded_model = pickle.load(open(model_file_name, 'rb'))

    return loaded_model


def input_fn(request_body, request_content_type):
    if request_content_type == "application/json":
        print(json.loads(request_body))
        return xgb.DMatrix(json.loads(request_body))
    else:
        raise Exception("Not supported content type")
