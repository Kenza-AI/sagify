![Sagify](docs/sagify@2x.png)

<p align="center">
    <em>Machine Learning Engineering done easily.</em>
</p>
<p align="center">
<a href="https://github.com/cortisolai/cortisol/actions?query=workflow%3ACI" target="_blank">
    <img src="https://github.com/cortisolai/cortisol/workflows/CI/badge.svg" alt="Test">
</a>
</p>

# sagify

A command-line utility to train and deploy Machine Learning/Deep Learning models on [AWS SageMaker](https://aws.amazon.com/sagemaker/) in a few simple steps! It hides all the details of Sagemaker so that you can focus 100% on Machine Learning, and not in low level engineering tasks.

For detailed reference to Sagify commands please go to: [Read the Docs](https://Kenza-AI.github.io/sagify/)

## Installation

### Prerequisites

sagify requires the following:

1. Python (3.7, 3.8, 3.9, 3.10, 3.11)
2. [Docker](https://www.docker.com/) installed and running
3. Configured [awscli](https://pypi.python.org/pypi/awscli)

### Install sagify

At the command line:

    pip install sagify


## Getting started -  No code deployment

1. Create a file with name `huggingface_config.json` with the following content:

        {
          "transformers_version": "4.6.1",
          "pytorch_version": "1.7.1",
          "hub": {
            "HF_MODEL_ID": "gpt2",
            "HF_TASK": "text-generation"
          }
        }
                
2. Then, make sure to configure your AWS account by following the instructions at section [Configure AWS Account](#configure-aws-account)
  
3. Finally, run the following command:

        sagify cloud lightning-deploy --framework huggingface -n 1 -e ml.c4.2xlarge --extra-config-file huggingface_config.json --aws-region us-east-1 --aws-profile sagemaker-dev
        
You can change the values for ec2 type (-e), aws region and aws profile with your preferred ones.

4. Once the Hugging Face model is deployed, you can go to https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/endpoints (make sure you're on your preferred region) and find your deployed endpoint. For example:

![Sagemaker-Endpoints-List](docs/sagemaker_endpoints_list.png)

5. Then, you can click on your deployed endpoint and copy the endpoint url. For example:

![Sagemaker-Endpoint](docs/sagemaker_endpoint.png)

6. Postman is a good app to call the deployed endpoint. Here's an example on how to set up the AWS signature in order to call the endpoint:
 
![Postman-AWS-Signature](docs/postman_aws_signature.png)

7. Finally, you can call the endpoint from Postman:

![Postman-Call-Endpoint](docs/postman_call_endpoint.png)

## Getting started - Custom Training and Deployment

### Step 1: Clone Machine Learning demo repository

You're going to clone and train a Machine Learning codebase to train a classifier for the Iris data set.

Clone repository:

    git clone https://github.com/Kenza-AI/sagify-demo.git 
    
Create environment:
    
    mkvirtualenv -p python3.7 sagify-demo
    
or

    mkvirtualenv -p python3.8 sagify-demo

Don't forget to activate the virtualenv after the creation of environment by executing `workon sagify-demo`.

Install dependencies:

    make requirements


### Step 2: Initialize sagify

    sagify init

Type in `sagify-demo` for SageMaker app name, `N` in question `Are you starting a new project?`, `src` for question `Type in the directory where your code lives` and make sure to choose your preferred Python version, AWS profile and region. Finally, type `requirements.txt` in question `Type in the path to requirements.txt`.

A module called `sagify` is created under the directory you provided. The structure is:
 
    sagify_base/
        local_test/
            test_dir/
                input/
                    config/
                        hyperparameters.json
                    data/
                        training/
                model/
                output/
            deploy_local.sh
            train_local.sh
        prediction/
            __init__.py
            nginx.conf
            predict.py
            prediction.py
            predictor.py
            serve
            wsgi.py
        training/
            __init__.py
            train
            training.py
        __init__.py
        build.sh
        Dockerfile
        executor.sh
        push.sh

### Step 3: Integrate sagify

As a Data Scientist, you only need to conduct a few actions. Sagify takes care of the rest:

1. Copy a subset of training data under `sagify_base/local_test/test_dir/input/data/training/` to test that training works locally
2. Implement `train(...)` function in `sagify_base/training/training.py`
3. Implement `predict(...)` function in `sagify_base/prediction/prediction.py`
4. Optionally, specify hyperparameters in `sagify_base/local_test/test_dir/input/config/hyperparameters.json` 

Hence,

1. Copy `iris.data` files from `data` to `sagify_base/local_test/test_dir/input/data/training/`

2. Replace the `TODOs` in the `train(...)` function in `sagify_base/training/training.py` file with:

    ```python
    input_file_path = os.path.join(input_data_path, 'iris.data')
    clf, accuracy = training_logic(input_file_path=input_file_path)
    
    output_model_file_path = os.path.join(model_save_path, 'model.pkl')
    joblib.dump(clf, output_model_file_path)
    
    accuracy_report_file_path = os.path.join(model_save_path, 'report.txt')
    with open(accuracy_report_file_path, 'w') as _out:
        _out.write(str(accuracy))
    ```
                
    and at the top of the file, add:
     
    ```python
    import os
    
    import joblib
    
    from iris_training import train as training_logic
    ```

3. Replace the body of `predict(...)` function in `sagify_base/prediction/prediction.py` with:

    ```python
    model_input = json_input['features']
    prediction = ModelService.predict(model_input)

    return {
        "prediction": prediction.item()
    }
    ```
        
    and replace the body of `get_model()` function in `ModelService` class in the same file with:
    
    ```python
    if cls.model is None:
        import joblib
        cls.model = joblib.load(os.path.join(_MODEL_PATH, 'model.pkl'))
    return cls.model
    ```
    

### Step 4: Build Docker image

It's time to build the Docker image that will contain the Machine Learning codebase:

    sagify build

If you run `docker images | grep sagify-demo` in your terminal, you'll see the created Sagify-Demo image.

### Step 5: Train model

Time to train the model for the Iris data set in the newly built Docker image:

    sagify local train

Model file `model.pkl` and report file `report.txt` are now under `sagify_base/local_test/test_dir/model/`

### Step 6: Deploy model

Finally, serve the model as a REST Service:

    sagify local deploy

Run the following curl command on your terminal to verify that the REST Service works:

    ```bash
    curl -X POST \
    http://localhost:8080/invocations \
    -H 'Cache-Control: no-cache' \
    -H 'Content-Type: application/json' \
    -H 'Postman-Token: 41189b9a-40e2-abcf-b981-c31ae692072e' \
    -d '{
	    "features":[[0.34, 0.45, 0.45, 0.3]]
    }'
    ```

It will be slow in the first couple of calls as it loads the model in a lazy manner.

Voila! That's a proof that this Machine Learning model is going to be trained and deployed on AWS SageMaker successfully. Now, go to the *Usage* section in [Sagify Docs](https://Kenza-AI.github.io/sagify/) to see how to train and deploy this Machine Learning model to AWS SageMaker!


## Hyperparameter Optimization

Given that you have configured your AWS Account as described in the previous section, you're now ready to perform Bayesian Hyperparameter Optimization on AWS SageMaker! The process is similar to training step.

### Step 1: Define Hyperparameter Configuration File

Define the Hyperparameter Configuration File. More specifically, you need to specify in a local JSON file the ranges for the hyperparameters, the name of the objective metric and its type (i.e. `Maximize` or `Minimize`). For example:

```json
{
	"ParameterRanges": {
		"CategoricalParameterRanges": [
			{
				"Name": "kernel",
				"Values": ["linear", "rbf"]
			}
		],
		"ContinuousParameterRanges": [
		{
		  "MinValue": 0.001,
		  "MaxValue": 10,
		  "Name": "gamma"
		}
		],
		"IntegerParameterRanges": [
			{
				"Name": "C",
				"MinValue": 1,
				"MaxValue": 10
			}
		]
    },
    "ObjectiveMetric": {
    	"Name": "Precision",
        "Type": "Maximize"
    }
}
```

### Step 2: Implement Train function

Replace the `TODOs` in the `train(...)` function in `sagify_base/training/training.py` file with your logic. For example:

```python
    from sklearn import datasets
    iris = datasets.load_iris()

    # Read the hyperparameter config json file
    import json
    with open(hyperparams_path) as _in_file:
        hyperparams_dict = json.load(_in_file)

    from sklearn import svm
    clf = svm.SVC(
        gamma=float(hyperparams_dict['gamma']),  # Values will be read as strings, so make sure to convert them to the right data type
        C=float(hyperparams_dict['C']),
        kernel=hyperparams_dict['kernel']
    )

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.3, random_state=42)

    clf.fit(X_train, y_train)

    from sklearn.metrics import precision_score

    predictions = clf.predict(X_test)

    precision = precision_score(y_test, predictions, average='weighted')
    
    # Log the objective metric name with its calculated value. In tis example is Precision.
    # The objective name should be exactly the same with the one specified in the hyperparams congig json file.
    # The value must be a numeric (float or int).
    from sagify.api.hyperparameter_tuning import log_metric
    name = "Precision"
    log_metric(name, precision)

    from joblib import dump
    dump(clf, os.path.join(model_save_path, 'model.pkl'))

    print('Training complete.')
```
        
### Step 3: Build and Push Docker image

1. `sagify build` Make sure sagify is in your `requirements.txt` file.
2. `sagify push`

### Step 4: Call The CLI Command

And, finally, call the hyperparameter-optimization CLI command. For example:

     sagify cloud hyperparameter-optimization -i s3://my-bucket/training-data/ -o s3://my-bucket/output/ -e ml.m4.xlarge -h local/path/to/hyperparam_ranges.json 
    
### Step 5: Monitor Progress

You can monitor the progress via the SageMaker UI console. Here is an example of a finished Hyperparameter Optimization job:

![Hyperparameter Optimization Results](docs/hyperparam_monitor.png)


## Commands

### Initialize

#### Name

Initializes a sagify module

#### Synopsis

    sagify init
    
#### Description

This command initializes a sagify module in the directory you provide when asked after you invoke the `init` command.

### Example

    sagify init


### Configure

#### Description

Updates an existing configuration value e.g. `python version` or `AWS region`.

#### Synopsis

    sagify configure [--aws-region AWS_REGION] [--aws-profile AWS_PROFILE] [--image-name IMAGE_NAME] [--python-version PYTHON_VERSION]

#### Optional Flags

`--aws-region AWS_REGION`: _AWS_ region where _Docker_ images are pushed and _SageMaker_ operations (_train_, _deploy_) are performed.

`--aws-profile AWS_PROFILE`: _AWS_ profile to use when interacting with _AWS_.

`--image-name IMAGE_NAME`: _Docker_ image name used when building for use with _SageMaker_. This shows up as an _AWS ECR_ repository on your _AWS_ account.

`--python-version PYTHON_VERSION`: _Python_ version used when building _SageMaker's_ _Docker_ images. Currently supported versions: `3.6`.


### Example

    sagify configure --aws-region us-east-2 --aws-profile default --image-name sage-docker-image-name --python-version 3.6


### Build

#### Name

Builds a Docker image

#### Synopsis

    sagify build
    
#### Description

This command builds a Docker image from code under the directory sagify is installed in. A `REQUIREMENTS_FILE` needs to be specified during `sagify init` or later via `sagify configure --requirements-dir` for all required dependencies to be installed in the Docker image.

#### Example

    sagify build


### Local Train

#### Name

Executes a Docker image in train mode

#### Synopsis

    sagify local train
    
#### Description

This command executes a Docker image in train mode. More specifically, it executes the `train(...)` function in `sagify_base/training/training.py` inside an already built Docker image (see Build command section).

#### Example

    sagify local train
    

### Local Deploy

#### Name

Executes a Docker image in serve mode

#### Synopsis

    sagify local deploy
    
#### Description

This command executes a Docker image in serve mode. More specifically, it runs a Flask REST app in Docker image and directs HTTP requests to `/invocations` endpoint. Then, the `/invocations` endpoint calls the `predict(...)` function in `sagify_base/prediction/prediction.py` (see Build command section on how to build a Docker image).
 
#### Example

    sagify local deploy
    

### Push

#### Name

Pushes a Docker image to AWS Elastic Container Service

#### Synopsis

    sagify push [--aws-profile PROFILE_NAME] [--aws-region AWS_REGION] [--iam-role-arn IAM_ROLE] [--external-id EXTERNAL_ID]

#### Description

This command pushes an already built Docker image to AWS Elastic Container Service. Later on, AWS SageMaker will consume that image from AWS Elastic Container Service for train and serve mode.

> Only one of _iam-role-arn_ and _aws_profile_ can be provided. _external-id_ is ignored when no _iam-role-arn_ is provided.

#### Optional Flags

`--iam-role-arn IAM_ROLE` or `-i IAM_ROLE`: AWS IAM role to use for pushing to ECR

`--aws-region AWS_REGION` or `-r AWS_REGION`: The AWS region to push the image to

`--aws-profile PROFILE_NAME` or `-p PROFILE_NAME`: AWS profile to use for pushing to ECR

`--external-id EXTERNAL_ID` or `-e EXTERNAL_ID`: Optional external id used when using an IAM role

#### Example

    sagify push
    

### Cloud Upload Data

#### Name

Uploads data to AWS S3

#### Synopsis

    sagify cloud upload-data --input-dir LOCAL_INPUT_DATA_DIR --s3-dir S3_TARGET_DATA_LOCATION
    
#### Description
 
This command uploads content under `LOCAL_INPUT_DATA_DIR` to S3 under `S3_TARGET_DATA_LOCATION`

#### Required Flags

`--input-dir LOCAL_INPUT_DATA_DIR` or `-i LOCAL_INPUT_DATA_DIR`: Local input directory

`--s3-dir S3_TARGET_DATA_LOCATION` or `-s S3_TARGET_DATA_LOCATION`: S3 target location

#### Example

    sagify cloud upload-data -i ./training_data/ -s s3://my-bucket/training-data/


### Cloud Train

#### Name

Trains your ML/DL model using a Docker image on AWS SageMaker with input from S3

#### Synopsis

    sagify cloud train --input-s3-dir INPUT_DATA_S3_LOCATION --output-s3-dir S3_LOCATION_TO_SAVE_OUTPUT --ec2-type EC2_TYPE [--hyperparams-file HYPERPARAMS_JSON_FILE] [--volume-size EBS_SIZE_IN_GB] [--time-out TIME_OUT_IN_SECS] [--aws-tags TAGS] [--iam-role-arn IAM_ROLE] [--external-id EXTERNAL_ID] [--base-job-name BASE_JOB_NAME] [--job-name JOB_NAME] [--metric-names COMMA_SEPARATED_METRIC_NAMES] [--use-spot-instances FLAG_TO_USE_SPOT_INSTANCES]

#### Description

This command retrieves a Docker image from AWS Elastic Container Service and executes it on AWS SageMaker in train mode

#### Required Flags

`--input-s3-dir INPUT_DATA_S3_LOCATION` or `-i INPUT_DATA_S3_LOCATION`: S3 location to input data

`--output-s3-dir S3_LOCATION_TO_SAVE_OUTPUT` or `-o S3_LOCATION_TO_SAVE_OUTPUT`: S3 location to save output (models, reports, etc). Make sure that the output bucket already exists. Any not existing key prefix will be created by sagify.

`--ec2-type EC2_TYPE` or `-e EC2_TYPE`: ec2 type. Refer to <https://aws.amazon.com/sagemaker/pricing/instance-types/>

#### Optional Flags

`--hyperparams-file HYPERPARAMS_JSON_FILE` or `-h HYPERPARAMS_JSON_FILE`: Path to hyperparams JSON file
 
`--volume-size EBS_SIZE_IN_GB` or `-v EBS_SIZE_IN_GB`: Size in GB of the EBS volume (default: 30)

`--time-out TIME_OUT_IN_SECS` or `-s TIME_OUT_IN_SECS`: Time-out in seconds (default: 24 * 60 * 60)

`--aws-tags TAGS` or `-a TAGS`: Tags for labeling a training job of the form `tag1=value1;tag2=value2`. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.

`--iam-role-arn IAM_ROLE` or `-r IAM_ROLE`: AWS IAM role to use for training with *SageMaker*

`--external-id EXTERNAL_ID` or `-x EXTERNAL_ID`: Optional external id used when using an IAM role

`--base-job-name BASE_JOB_NAME` or `-n BASE_JOB_NAME`: Optional prefix for the SageMaker training job

`--job-name JOB_NAME`: Optional name for the SageMaker training job. NOTE: if a `--base-job-name` is passed along with this option, it will be ignored.

`--use-spot-instances FLAG_TO_USE_SPOT_INSTANCES`: Optional flag that specifies whether to use SageMaker Managed Spot instances for training. It should be used only for training jobs that take less than 1 hour. More information: https://docs.aws.amazon.com/sagemaker/latest/dg/model-managed-spot-training.html (default: False).

`--metric-names COMMA_SEPARATED_METRIC_NAMES`: Optional comma-separated metric names for tracking performance of training jobs. Example: `Precision,Recall,AUC`. Then, make sure you log these metric values using the `log_metric` function in the `train` function:

```python
...
from sagify.api.hyperparameter_tuning import log_metric
log_metric("Precision:, precision)
log_metric("Accuracy", accuracy)
...
```
    
   When the training jobs finishes, they will be stored in the CloudWatch algorithm metrics logs of the SageMaker training job:
   
   ![Algorithm Metrics](docs/cloud_watch_metrics.png)

#### Example

    sagify cloud train -i s3://my-bucket/training-data/ -o s3://my-bucket/output/ -e ml.m4.xlarge -h local/path/to/hyperparams.json -v 60 -t 86400 --metric-names Accuracy,Precision
    
    
### Cloud Hyperparameter Optimization

#### Name

Executes a Docker image in hyperparameter-optimization mode on AWS SageMaker

#### Synopsis

    sagify cloud hyperparameter-optimization --input-s3-dir INPUT_DATA_S3_LOCATION --output-s3-dir S3_LOCATION_TO_SAVE_MULTIPLE_TRAINED_MODELS --ec2-type EC2_TYPE [--hyperparams-config-file HYPERPARAM_RANGES_JSON_FILE] [--max-jobs MAX_NUMBER_OF_TRAINING_JOBS] [--max-parallel-jobs MAX_NUMBER_OF_PARALLEL_TRAINING_JOBS] [--volume-size EBS_SIZE_IN_GB] [--time-out TIME_OUT_IN_SECS] [--aws-tags TAGS] [--iam-role-arn IAM_ROLE] [--external-id EXTERNAL_ID] [--base-job-name BASE_JOB_NAME] [--job-name JOB_NAME] [--wait WAIT_UNTIL_HYPERPARAM_JOB_IS_FINISHED] [--use-spot-instances FLAG_TO_USE_SPOT_INSTANCES]

#### Description

This command retrieves a Docker image from AWS Elastic Container Service and executes it on AWS SageMaker in hyperparameter-optimization mode

#### Required Flags

`--input-s3-dir INPUT_DATA_S3_LOCATION` or `-i INPUT_DATA_S3_LOCATION`: S3 location to input data

`--output-s3-dir S3_LOCATION_TO_SAVE_OUTPUT` or `-o S3_LOCATION_TO_SAVE_OUTPUT`: S3 location to save output (models, reports, etc). Make sure that the output bucket already exists. Any not existing key prefix will be created by sagify.

`--ec2-type EC2_TYPE` or `-e EC2_TYPE`: ec2 type. Refer to <https://aws.amazon.com/sagemaker/pricing/instance-types/>

`--hyperparams-config-file HYPERPARAM_RANGES_JSON_FILE` or `-h HYPERPARAM_RANGES_JSON_FILE`: Local path to hyperparameters configuration file. Example:

```json
{
	"ParameterRanges": {
		"CategoricalParameterRanges": [
			{
				"Name": "kernel",
				"Values": ["linear", "rbf"]
			}
		],
		"ContinuousParameterRanges": [
		{
		  "MinValue": 0.001,
		  "MaxValue": 10,
		  "Name": "gamma"
		}
		],
		"IntegerParameterRanges": [
			{
				"Name": "C",
				"MinValue": 1,
				"MaxValue": 10
			}
		]
    },
    "ObjectiveMetric": {
    	"Name": "Precision",
        "Type": "Maximize"
    }
}
```

#### Optional Flags

`--max-jobs MAX_NUMBER_OF_TRAINING_JOBS` or `-m MAX_NUMBER_OF_TRAINING_JOBS`: Maximum total number of training jobs to start for the hyperparameter tuning job (default: 3)

`--max-parallel-jobs MAX_NUMBER_OF_PARALLEL_TRAINING_JOBS` or `-p MAX_NUMBER_OF_PARALLEL_TRAINING_JOBS`: Maximum number of parallel training jobs to start (default: 1)
 
`--volume-size EBS_SIZE_IN_GB` or `-v EBS_SIZE_IN_GB`: Size in GB of the EBS volume (default: 30)

`--time-out TIME_OUT_IN_SECS` or `-s TIME_OUT_IN_SECS`: Time-out in seconds (default: 24 * 60 * 60)

`--aws-tags TAGS` or `-a TAGS`: Tags for labeling a training job of the form `tag1=value1;tag2=value2`. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.

`--iam-role-arn IAM_ROLE` or `-r IAM_ROLE`: AWS IAM role to use for training with *SageMaker*

`--external-id EXTERNAL_ID` or `-x EXTERNAL_ID`: Optional external id used when using an IAM role

`--base-job-name BASE_JOB_NAME` or `-n BASE_JOB_NAME`: Optional prefix for the SageMaker training job

`--job-name JOB_NAME`: Optional name for the SageMaker training job. NOTE: if a `--base-job-name` is passed along with this option, it will be ignored. 

`--wait WAIT_UNTIL_HYPERPARAM_JOB_IS_FINISHED` or `-w WAIT_UNTIL_HYPERPARAM_JOB_IS_FINISHED`: Optional flag to wait until Hyperparameter Tuning is finished. (default: don't wait)
 
`--use-spot-instances FLAG_TO_USE_SPOT_INSTANCES`: Optional flag that specifies whether to use SageMaker Managed Spot instances for training. It should be used only for training jobs that take less than 1 hour. More information: https://docs.aws.amazon.com/sagemaker/latest/dg/model-managed-spot-training.html (default: False).

#### Example

    sagify cloud hyperparameter-optimization -i s3://my-bucket/training-data/ -o s3://my-bucket/output/ -e ml.m4.xlarge -h local/path/to/hyperparam_ranges.json -v 60 -t 86400


### Cloud Deploy

#### Name

Executes a Docker image in serve mode on AWS SageMaker

#### Synopsis

    sagify cloud deploy --s3-model-location S3_LOCATION_TO_MODEL_TAR_GZ --num-instance NUMBER_OF_EC2_INSTANCES --ec2-type EC2_TYPE [--aws-tags TAGS] [--iam-role-arn IAM_ROLE] [--external-id EXTERNAL_ID] [--endpoint-name ENDPOINT_NAME]

#### Description

This command retrieves a Docker image from AWS Elastic Container Service and executes it on AWS SageMaker in serve mode. You can update an endpoint (model or number of instances) by specifying the endpoint-name. 

#### Required Flags

`--s3-model-location S3_LOCATION_TO_MODEL_TAR_GZ` or `-m S3_LOCATION_TO_MODEL_TAR_GZ`: S3 location to to model tar.gz

`--num-instances NUMBER_OF_EC2_INSTANCES` or `n NUMBER_OF_EC2_INSTANCES`: Number of ec2 instances

`--ec2-type EC2_TYPE` or `e EC2_TYPE`: ec2 type. Refer to https://aws.amazon.com/sagemaker/pricing/instance-types/

#### Optional Flags

`--aws-tags TAGS` or `-a TAGS`: Tags for labeling a training job of the form `tag1=value1;tag2=value2`. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.

`--iam-role-arn IAM_ROLE` or `-r IAM_ROLE`: AWS IAM role to use for deploying with *SageMaker*

`--external-id EXTERNAL_ID` or `-x EXTERNAL_ID`: Optional external id used when using an IAM role

`--endpoint-name ENDPOINT_NAME`: Optional name for the SageMaker endpoint

#### Example

    sagify cloud deploy -m s3://my-bucket/output/model.tar.gz -n 3 -e ml.m4.xlarge

    
### Cloud Batch Transform

#### Name

Executes a Docker image in batch transform mode on AWS SageMaker, i.e. runs batch predictions on user defined S3 data

#### Synopsis

    sagify cloud batch-transform --s3-model-location S3_LOCATION_TO_MODEL_TAR_GZ --s3-input-location S3_INPUT_LOCATION --s3-output-location S3_OUTPUT_LOCATION --num-instance NUMBER_OF_EC2_INSTANCES --ec2-type EC2_TYPE [--aws-tags TAGS] [--iam-role-arn IAM_ROLE] [--external-id EXTERNAL_ID] [--wait WAIT_UNTIL_BATCH_TRANSFORM_JOB_IS_FINISHED] [--job-name JOB_NAME]

#### Description

This command retrieves a Docker image from AWS Elastic Container Service and executes it on AWS SageMaker in batch transform mode, i.e. runs batch predictions on user defined S3 data. SageMaker will spin up REST container(s) and call it/them with input data(features) from a user defined S3 path.

Things to do:

- You should implement the predict function that expects a JSON containing the required feature values. It's the same predict function used for deploying the model as a REST service. Example of a JSON:

```json
{
    "features": [5.1,3.5,1.4,0.2]
}
```
- The input S3 path should contain a file or multiple files where each line is a JSON, the same JSON format as the one expected in the predict function. Example of a file:

```json
{"features": [[5.1,3.5,1.4,0.2]]}
{"features": [[4.9,3.0,1.4,0.2]]}
{"features": [[4.7,3.2,1.3,0.2]]}
{"features": [[4.6,3.1,1.5,0.2]]}
```

#### Required Flags

`--s3-model-location S3_LOCATION_TO_MODEL_TAR_GZ` or `-m S3_LOCATION_TO_MODEL_TAR_GZ`: S3 location to to model tar.gz

`--s3-input-location S3_INPUT_LOCATION` or `-i S3_INPUT_LOCATION`: s3 input data location

`--s3-output-location S3_OUTPUT_LOCATION` or `-o S3_OUTPUT_LOCATION`: s3 location to save predictions

`--num-instances NUMBER_OF_EC2_INSTANCES` or `n NUMBER_OF_EC2_INSTANCES`: Number of ec2 instances

`--ec2-type EC2_TYPE` or `e EC2_TYPE`: ec2 type. Refer to https://aws.amazon.com/sagemaker/pricing/instance-types/

#### Optional Flags

`--aws-tags TAGS` or `-a TAGS`: Tags for labeling a training job of the form `tag1=value1;tag2=value2`. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.

`--iam-role-arn IAM_ROLE` or `-r IAM_ROLE`: AWS IAM role to use for deploying with *SageMaker*

`--external-id EXTERNAL_ID` or `-x EXTERNAL_ID`: Optional external id used when using an IAM role

`--wait WAIT_UNTIL_BATCH_TRANSFORM_JOB_IS_FINISHED` or `-w WAIT_UNTIL_BATCH_TRANSFORM_JOB_IS_FINISHED`: Optional flag to wait until Batch Transform is finished. (default: don't wait)

`--job-name JOB_NAME`: Optional name for the SageMaker batch transform job

#### Example

    sagify cloud batch-transform -m s3://my-bucket/output/model.tar.gz -i s3://my-bucket/input_features -o s3://my-bucket/predictions -n 3 -e ml.m4.xlarge


### Cloud Create Streaming Inference

NOTE: THIS IS AN EXPERIMENTAL FEATURE

Make sure that the following 2 policies are attached to the role you created in section "Configure AWS Account":

![lambda_full_access](docs/lambda_full_access.png)

![sqs_full_access](docs/sqs_full_access.png)

#### Name

Creates streaming inference pipelines

#### Synopsis

    sagify cloud create-streaming-inference --name WORKER_NAME --endpoint-name ENDPOINT_NAME --input-topic-name FEATURES_INPUT_TOPIC_NAME --output-topic-name PREDICTIONS_OUTPUT_TOPIC_NAME --type STREAMING_INFERENCE_TYPE

#### Description

This command creates a worker as a Lambda function that listens to features in the `FEATURES_INPUT_TOPIC_NAME`, calls the the endpoint `ENDPOINT_NAME` and, finally, forwards predictions to `PREDICTIONS_OUTPUT_TOPIC_NAME`.

#### Required Flags

`--name WORKER_NAME`: The name of the Lambda function

`--endpoint-name ENDPOINT_NAME`: The name of the endpoint of the deployed model

`--input-topic-name FEATURES_INPUT_TOPIC_NAME`: Topic name where features will be landed

`--output-topic-name PREDICTIONS_OUTPUT_TOPIC_NAME`: Topic name where model predictions will be forwarded

`--type STREAMING_INFERENCE_TYPE`: The type of streaming inference. At the moment, only `SQS` is supported!

#### Example

    sagify cloud create-streaming-inference --name recommender-worker --endpoint-name my-recommender-endpoint-1 --input-topic-name features --output-topic-name model-predictions --type SQS


### Cloud Delete Streaming Inference

NOTE: THIS IS AN EXPERIMENTAL FEATURE

Make sure that the following 2 policies are attached to the role you created in section "Configure AWS Account":

![lambda_full_access](lambda_full_access.png)

![sqs_full_access](sqs_full_access.png)

#### Name

Deletes streaming inference pipelines

#### Synopsis

    sagify cloud delete-streaming-inference --name WORKER_NAME --input-topic-name FEATURES_INPUT_TOPIC_NAME --output-topic-name PREDICTIONS_OUTPUT_TOPIC_NAME --type STREAMING_INFERENCE_TYPE

#### Description

This command deletes the worker (i.e. Lambda function), input topic `FEATURES_INPUT_TOPIC_NAME` and output topic `PREDICTIONS_OUTPUT_TOPIC_NAME`.

#### Required Flags

`--name WORKER_NAME`: The name of the Lambda function

`--input-topic-name FEATURES_INPUT_TOPIC_NAME`: Topic name where features will be landed

`--output-topic-name PREDICTIONS_OUTPUT_TOPIC_NAME`: Topic name where model predictions will be forwarded

`--type STREAMING_INFERENCE_TYPE`: The type of streaming inference. At the moment, only `SQS` is supported!

#### Example

    sagify cloud delete-streaming-inference --name recommender-worker --input-topic-name features --output-topic-name model-predictions --type SQS


### Cloud Lightning Deploy

#### Name

Command for lightning deployment of pre-trained ML model(s) on AWS SageMaker without code

#### Synopsis

    sagify cloud lightning-deploy --framework FRAMEWORK --num-instances NUMBER_OF_EC2_INSTANCES --ec2-type EC2_TYPE --aws-profile AWS_PROFILE --aws-region AWS_REGION --extra-config-file EXTRA_CONFIG_FILE [--model-server-workers MODEL_SERVER_WORKERS] [--s3-model-location S3_LOCATION_TO_MODEL_TAR_GZ] [--aws-tags TAGS] [--iam-role-arn IAM_ROLE] [--external-id EXTERNAL_ID] [--endpoint-name ENDPOINT_NAME]

#### Description

This command deploys a pre-trained ML model without code. 

#### Required Flags

`--framework FRAMEWORK`: Name of the ML framework. Valid values: `sklearn`, `huggingface`, `xgboost`

`--num-instances NUMBER_OF_EC2_INSTANCES` or `n NUMBER_OF_EC2_INSTANCES`: Number of ec2 instances

`--ec2-type EC2_TYPE` or `e EC2_TYPE`: ec2 type. Refer to https://aws.amazon.com/sagemaker/pricing/instance-types/

`--aws-profile AWS_PROFILE`: The AWS profile to use for the lightning deploy command

`--aws-region AWS_REGION`: The AWS region to use for the lightning deploy command

`--extra-config-file EXTRA_CONFIG_FILE`: Json file with ML framework specific arguments

For SKLearn, you have to specify the `framework_version` in the EXTRA_CONFIG_FILE and specify the S3 location to model tar.gz (i.e. tar gzip your sklearn pickled file

#### Optional Flags

`--s3-model-location S3_LOCATION_TO_MODEL_TAR_GZ` or `-m S3_LOCATION_TO_MODEL_TAR_GZ`: Optional S3 location to model tar.gz

`--aws-tags TAGS` or `-a TAGS`: Tags for labeling a training job of the form `tag1=value1;tag2=value2`. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.

`--iam-role-arn IAM_ROLE` or `-r IAM_ROLE`: AWS IAM role to use for deploying with *SageMaker*

`--external-id EXTERNAL_ID` or `-x EXTERNAL_ID`: Optional external id used when using an IAM role

`--endpoint-name ENDPOINT_NAME`: Optional name for the SageMaker endpoint

#### Example for SKLearn

Compress your pre-trained sklearn model to a GZIP tar archive with command `!tar czvf model.tar.gz $your_sklearn_model_name`.

    sagify cloud lightning-deploy --framework sklearn -n 1 -e ml.c4.2xlarge --extra-config-file sklearn_config.json --aws-region us-east-1 --aws-profile sagemaker-dev -m s3://my-bucket/output/model.tar.gz

The `sklearn_config.json` must contain the following flag `framework_version`. Supported sklearn version(s): 0.20.0, 0.23-1.
 
Example of `sklearn_config.json`:

        {
          "framework_version": "0.23-1"
        }

#### Example for HuggingFace by specifying the `S3_LOCATION_TO_MODEL_TAR_GZ`

Compress your pre-trained HuggingFace model to a GZIP tar archive with command `!tar czvf model.tar.gz $your_hg_model_name`.

    sagify cloud lightning-deploy --framework huggingface -n 1 -e ml.c4.2xlarge --extra-config-file huggingface_config.json --aws-region us-east-1 --aws-profile sagemaker-dev -m s3://my-bucket/output/model.tar.gz

The `huggingface_config.json` must contain the following flags  `pytorch_version` or `tensorflow_version` (not both), and `transformers_version`. For more info: https://sagemaker.readthedocs.io/en/stable/frameworks/huggingface/sagemaker.huggingface.html#hugging-face-model.
 
Example of `huggingface_config.json`:

        {
          "transformers_version": "4.6.1",
          "pytorch_version": "1.7.1"
        }

#### Example for HuggingFace without specifying the `S3_LOCATION_TO_MODEL_TAR_GZ`

    sagify cloud lightning-deploy --framework huggingface -n 1 -e ml.c4.2xlarge --extra-config-file huggingface_config.json --aws-region us-east-1 --aws-profile sagemaker-dev


The `huggingface_config.json` must contain the following flags  `pytorch_version` or `tensorflow_version` (not both), `transformers_version` and `hub`. For more info: https://sagemaker.readthedocs.io/en/stable/frameworks/huggingface/sagemaker.huggingface.html#hugging-face-model.
 
Example of `huggingface_config.json`:

        {
          "transformers_version": "4.6.1",
          "pytorch_version": "1.7.1",
          "hub": {
            "HF_MODEL_ID": "gpt2",
            "HF_TASK": "text-generation"
          }
        }
        
#### Example for XGBoost

Compress your pre-trained XGBoost model to a GZIP tar archive with command `!tar czvf model.tar.gz $your_xgboost_model_name`.

    sagify cloud lightning-deploy --framework xgboost -n 1 -e ml.c4.2xlarge --extra-config-file xgboost_config.json --aws-region us-east-1 --aws-profile sagemaker-dev -m s3://my-bucket/output/model.tar.gz

The `xgboost_config.json` must contain the following flag `framework_version`. Supported xgboost version(s): 0.90-2, 1.0-1, and later.
 
Example of `xgboost_config.json`:

        {
          "framework_version": "0.23-1"
        }
