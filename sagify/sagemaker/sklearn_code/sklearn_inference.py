import os
import joblib


def model_fn(model_dir):
    print("loading SKLearn model from: {}".format(model_dir))

    files = [f for f in os.listdir(model_dir) if os.path.isfile(os.path.join(model_dir, f))]
    model_file_name = files[0]

    return joblib.load(os.path.join(model_dir, model_file_name))
