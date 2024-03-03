![Sagify](docs/sagify@2x.png)

<p align="center">
    <em>LLMs and Machine Learning done easily.</em>
</p>
<p align="center">
<a href="https://github.com/kenza-ai/sagify/actions?query=workflow%3ACI" target="_blank">
    <img src="https://github.com/kenza-ai/sagify/workflows/CI/badge.svg" alt="Test">
</a>
</p>

# sagify

Sagify provides a simplified interface to manage machine learning workflows on [AWS SageMaker](https://aws.amazon.com/sagemaker/), helping you focus on building ML models rather than infrastructure. Its modular architecture includes an LLM Gateway module to provide a unified interface for leveraging both open source and proprietary large language models. The LLM Gateway gives access to various LLMs through a simple API, letting you easily incorporate them into your workflows.

For detailed reference to Sagify please go to: [Read the Docs](https://Kenza-AI.github.io/sagify/)

## Installation

### Prerequisites

sagify requires the following:

1. Python (3.7, 3.8, 3.9, 3.10, 3.11)
2. [Docker](https://www.docker.com/) installed and running
3. Configured [awscli](https://pypi.python.org/pypi/awscli)

### Install sagify

At the command line:

    pip install sagify


## Getting started -  LLM Deployment with no code
                
1. Make sure to configure your AWS account by following the instructions at section [Configure AWS Account](#configure-aws-account)
  
2. Finally, run the following command:

```sh
sagify cloud foundation-model-deploy --model-id model-txt2img-stabilityai-stable-diffusion-v2-1-base --model-version 1.* -n 1 -e ml.p3.2xlarge --aws-region us-east-1 --aws-profile sagemaker-dev
```
        
You can change the values for ec2 type (-e), aws region and aws profile with your preferred ones.

Once the Stable Diffusion model is deployed, you can use the generated code snippet to query it. Enjoy!

## Backend Platforms

### OpenAI

The following models are offered for chat completions:

| Model Name | URL |
|:------------:|:-----:|
|gpt-4|https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo|
|gpt-4-32k|https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo|
|gpt-3.5-turbo|https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo|

For image creation you can rely on the following models:

| Model Name | URL |
|:------------:|:-----:|
|dall-e-3|https://platform.openai.com/docs/models/dall-e|
|dall-e-2|https://platform.openai.com/docs/models/dall-e|

And for embeddings:

| Model Name | URL |
|:------------:|:-----:|
|text-embedding-3-large|https://platform.openai.com/docs/models/embeddings|
|text-embedding-3-small|https://platform.openai.com/docs/models/embeddings|
|text-embedding-ada-002|https://platform.openai.com/docs/models/embeddings|

All these lists of supported models on Openai can be retrieved by running the command `sagify llm models --all --provider openai`. If you want to focus only on chat completions models, then run `sagify llm models --chat-completions --provider openai`. For image creations and embeddings, `sagify llm models --image-creations --provider openai` and `sagify llm models --embeddings --provider openai`, respectively.

### Open-Source

The following open-source models are offered for chat completions:

| Model Name | URL |
|:------------:|:-----:|
|llama-2-7b|https://huggingface.co/meta-llama/Llama-2-7b|
|llama-2-13b|https://huggingface.co/meta-llama/Llama-2-13b|
|llama-2-70b|https://huggingface.co/meta-llama/Llama-2-70b|

For image creation you can rely on the following open-source models:

| Model Name | URL |
|:------------:|:-----:|
|stabilityai-stable-diffusion-v2|https://huggingface.co/stabilityai/stable-diffusion-2|
|stabilityai-stable-diffusion-v2-1-base|https://huggingface.co/stabilityai/stable-diffusion-2-1-base|
|stabilityai-stable-diffusion-v2-fp16|https://huggingface.co/stabilityai/stable-diffusion-2/tree/fp16|

And for embeddings:

| Model Name | URL |
|:------------:|:-----:|
|bge-large-en|https://huggingface.co/BAAI/bge-large-en|
|bge-base-en|https://huggingface.co/BAAI/bge-base-en|
|gte-large|https://huggingface.co/thenlper/gte-large|
|gte-base|https://huggingface.co/thenlper/gte-base|
|e5-large-v2|https://huggingface.co/intfloat/e5-large-v2|
|bge-small-en|https://huggingface.co/BAAI/bge-small-en|
|e5-base-v2|https://huggingface.co/intfloat/e5-base-v2|
|multilingual-e5-large|https://huggingface.co/intfloat/multilingual-e5-large|
|e5-large|https://huggingface.co/intfloat/e5-large|
|gte-small|https://huggingface.co/thenlper/gte-small|
|e5-base|https://huggingface.co/intfloat/e5-base|
|e5-small-v2|https://huggingface.co/intfloat/e5-small-v2|
|multilingual-e5-base|https://huggingface.co/intfloat/multilingual-e5-base|
|all-MiniLM-L6-v2|https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2|

All these lists of supported open-source models are supported on AWS Sagemaker and can be retrieved by running the command `sagify llm models --all --provider sagemaker`. If you want to focus only on chat completions models, then run `sagify llm models --chat-completions --provider sagemaker`. For image creations and embeddings, `sagify llm models --image-creations --provider sagemaker` and `sagify llm models --embeddings --provider sagemaker`, respectively.

## Set up OpenAI

You need to define the following env variables before you start the LLM Gateway server:

- `OPENAI_API_KEY`: Your OpenAI API key. Example: `export OPENAI_API_KEY=...`.
- `OPENAI_CHAT_COMPLETIONS_MODEL`: It should have one of values [here](https://platform.openai.com/docs/models/gpt-3-5-turbo) or [here](https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo).
- `OPENAI_EMBEDDINGS_MODEL`: It should have one of values [here](https://platform.openai.com/docs/models/embeddings).
- `OPENAI_IMAGE_CREATION_MODEL`: It should have one of values [here](https://platform.openai.com/docs/models/dall-e).

## Set up open-source LLMs

First step is to deploy the LLM model(s). You can choose to deploy all backend services (chat completions, image creations, embeddings) or some of them. 

If you want to deploy all of them, then run `sagify llm start --all`. This command will deploy all backend services (chat completions, image creations, embeddings) with the following configuration:

```json
{
    "chat_completions": {
        "model": "llama-2-7b",
        "instance_type": "ml.g5.2xlarge",
        "num_instances": 1,
    },
    "image_creations": {
        "model": "stabilityai-stable-diffusion-v2-1-base",
        "instance_type": "ml.p3.2xlarge",
        "num_instances": 1,
    },
    "embeddings": {
        "model": "gte-small",
        "instance_type": "ml.g5.2xlarge",
        "num_instances": 1,
    },
}
```

You can change this configuration by suppling your own config file, then you can run `sagify llm start -all --config YOUR_CONFIG_FILE.json`.

It takes 15 to 30 minutes to deploy all the backend services as Sagemaker endpoints.

The deployed model names, which are the Sagemaker endpoint names, are printed out and stored in the hidden file `.sagify_llm_infra.json`. You can also access them from the AWS Sagemaker web console.

## Deploy FastAPI LLM Gateway - Docker

Once you have set up your backend platform, you can deploy the FastAPI LLM Gateway locally. 

In case of using the AWS Sagemaker platform, you need to define the following env variables before you start the LLM Gateway server:

- `AWS_ACCESS_KEY_ID`: It can be the same one you use locally for Sagify. It should have access to Sagemaker and S3. Example: `export AWS_ACCESS_KEY_ID=...`.
- `AWS_SECRET_ACCESS_KEY`:  It can be the same one you use locally for Sagify. It should have access to Sagemaker and S3. Example: `export AWS_ACCESS_KEY_ID=...`.
- `AWS_REGION_NAME`: AWS region where the LLM backend services (Sagemaker endpoints) are deployed.
- `S3_BUCKET_NAME`: S3 bucket name where the created images by the image creation backend service are stored.
- `IMAGE_URL_TTL_IN_SECONDS`: TTL in seconds of the temporary url to the created images. Default value: 3600.
- `SM_CHAT_COMPLETIONS_MODEL`: The Sagemaker endpoint name where the chat completions model is deployed.
- `SM_EMBEDDINGS_MODEL`: The Sagemaker endpoint name where the embeddings model is deployed.
- `SM_IMAGE_CREATION_MODEL`: The Sagemaker endpoint name where the image creation model is deployed.

In case of using the OpenAI platform, you need to define the following env variables before you start the LLM Gateway server:

- `OPENAI_API_KEY`: Your OpenAI API key. Example: `export OPENAI_API_KEY=...`.
- `OPENAI_CHAT_COMPLETIONS_MODEL`: It should have one of values [here](https://platform.openai.com/docs/models/gpt-3-5-turbo) or [here](https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo).
- `OPENAI_EMBEDDINGS_MODEL`: It should have one of values [here](https://platform.openai.com/docs/models/embeddings).
- `OPENAI_IMAGE_CREATION_MODEL`: It should have one of values [here](https://platform.openai.com/docs/models/dall-e).

Now, you can run the command `sagify llm gateway --image sagify-llm-gateway:v0.1.0 --start-local` to start the LLM Gateway locally. You can change the name of the image via the `--image` argument.

This command will output the Docker container id. You can stop the container by executing `docker stop <CONTAINER_ID>`.

**Examples**

(*Remember to export first all the environment variables you need*)

In the case you want to create a docker image and then run it
```{bash}
sagify llm gateway --image sagify-llm-gateway:v0.1.0 --start-local
 ```

 If you want to use just build the image
 ```{bash}
 sagify llm gateway --image sagify-llm-gateway:v0.1.0
 ```

If you want to support both platforms (OpenAI and AWS Sagemaker), then pass all the env variables for both platforms.

## Deploy FastAPI LLM Gateway - AWS Fargate

In case you want to deploy the LLM Gateway to AWS Fargate, then you can follow these general steps:

1. Containerize the FastAPI LLM Gateway: See previous section.
2. Push Docker image to Amazon ECR.
3. Define Task Definition: Define a task definition that describes how to run your containerized FastAPI application on Fargate. Specify the Docker image, container port, CPU and memory requirements, and environment variables.
4. Create ECS Service: Create a Fargate service using the task definition. Configure the desired number of tasks, networking options, load balancing, and auto-scaling settings.
4. Set Environment Variables: Ensure that your FastAPI application retrieves the environment variables correctly at runtime.

Here's an example CloudFormation template to deploy a FastAPI service to AWS Fargate with 5 environment variables:

```yaml
Resources:
  MyFargateTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: my-fargate-task
      ContainerDefinitions:
        - Name: fastapi-container
          Image: <YOUR_ECR_REPOSITORY_URI>
          Memory: 512
          PortMappings:
            - ContainerPort: 80
          Environment:
            - Name: AWS_ACCESS_KEY_ID
              Value: "value1"
            - Name: AWS_SECRET_ACCESS_KEY
              Value: "value2"
            - Name: AWS_REGION_NAME
              Value: "value3"
            - Name: S3_BUCKET_NAME
              Value: "value4"
            - Name: IMAGE_URL_TTL_IN_SECONDS
              Value: "value5"
            - Name: SM_CHAT_COMPLETIONS_MODEL
              Value: "value6"
            - Name: SM_EMBEDDINGS_MODEL
              Value: "value7"
            - Name: SM_IMAGE_CREATION_MODEL
              Value: "value8"
            - Name: OPENAI_CHAT_COMPLETIONS_MODEL
              Value: "value9"
            - Name: OPENAI_EMBEDDINGS_MODEL
              Value: "value10"
            - Name: OPENAI_IMAGE_CREATION_MODEL
              Value: "value11"

  MyFargateService:
    Type: AWS::ECS::Service
    Properties:
      Cluster: default
      TaskDefinition: !Ref MyFargateTaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets:
            - <YOUR_SUBNET_ID>
          SecurityGroups:
            - <YOUR_SECURITY_GROUP_ID>
```

## LLM Gateway API

Once the LLM Gateway is deployed, you can access it on `HOST_NAME/docs`.

### Completions

```shell
curl --location --request POST '/v1/chat/completions' \
--header 'Content-Type: application/json' \
--data-raw '{
    "provider": "sagemaker",
     "messages": [
      {
        "role": "system",
        "content": "you are a cook"
      },
      {
        "role": "user",
        "content": "what is the recipe of mayonnaise"
      }
    ],
    "temperature": 0,
    "max_tokens": 600,
    "top_p": 0.9,
    "seed": 32
}'
```

> Example responses

> 200 Response

```json
{
    "id": "chatcmpl-8167b99c-f22b-4e04-8e26-4ca06d58dc86",
    "object": "chat.completion",
    "created": 1708765682,
    "provider": "sagemaker",
    "model": "meta-textgeneration-llama-2-7b-f-2024-02-24-08-49-32-123",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": " Ah, a fellow foodie! Mayonnaise is a classic condiment that's easy to make and can elevate any dish. Here's my trusty recipe for homemade mayonnaise:\n\nIngredients:\n\n* 2 egg yolks\n* 1/2 cup (120 ml) neutral-tasting oil, such as canola or grapeseed\n* 1 tablespoon lemon juice or vinegar\n* Salt and pepper to taste\n\nInstructions:\n\n1. In a small bowl, whisk together the egg yolks and lemon juice or vinegar until well combined.\n2. Slowly pour in the oil while continuously whisking the mixture. You can do this by hand with a whisk or use an electric mixer on low speed.\n3. Continue whisking until the mixture thickens and emulsifies, which should take about 5-7 minutes. You'll know it's ready when it reaches a thick, creamy consistency.\n4. Taste and adjust the seasoning as needed. You can add more salt, pepper, or lemon juice to taste.\n5. Transfer the mayonnaise to a jar or airtight container and store it in the fridge for up to 1 week.\n\nThat's it! Homemade mayonnaise is a great way to control the ingredients and flavor, and it's also a fun kitchen experiment. Enjoy!"
            }
        }
    ]
}
```

### Embeddings

```shell
curl --location --request POST '/v1/embeddings' \
--header 'Content-Type: application/json' \
--data-raw '{
  "provider": "sagemaker",
  "input": [
    "The mayonnaise was delicious"
  ]
}'
```

> Example responses

> 200 Response

```json
{
    "data": [
        {
            "object": "embedding",
            "embedding": [
                -0.04274585098028183,
                0.021814687177538872,
                -0.004705613013356924,
                ...
                -0.07548460364341736,
                0.036427777260541916,
                0.016453085467219353,
                0.004641987383365631,
                -0.0072729517705738544,
                0.02343473769724369,
                -0.002924458822235465,
                0.0339619480073452,
                0.005262510851025581,
                -0.06709178537130356,
                -0.015170316211879253,
                -0.04612169787287712,
                -0.012380547821521759,
                -0.006663458421826363,
                -0.0573800653219223,
                0.007938326336443424,
                0.03486081212759018,
                0.021514462307095528
            ],
            "index": 0
        }
    ],
    "provider": "sagemaker",
    "model": "hf-sentencesimilarity-gte-small-2024-02-24-09-24-27-341",
    "object": "list"
}
```

### Image Generations

```shell
curl --location --request POST '/v1/images/generations' \
--header 'Content-Type: application/json' \
--data-raw '{
  "provider": "sagemaker",
  "prompt": 
    "A baby sea otter"
  ,
  "n": 1,
  "width": 512,
  "height": 512,
  "seed": 32,
  "response_format": "url"
}'
```

> Example responses

> 200 Response

```json
{
    "provider": "sagemaker",
    "model": "stable-diffusion-v2-1-base-2024-02-24-11-43-32-177",
    "created": 1708775601,
    "data": [
        {
            "url": "https://your-bucket.s3.amazonaws.com/31cedd17-ccd7-4cba-8dea-cb7e8b915782.png?AWSAccessKeyId=AKIAUKEQBDHITP26MLXH&Signature=%2Fd1J%2FUjOWbRnP5cwtkSzYUVoEoo%3D&Expires=1708779204"
        }
    ]
}
```

## Talk with the team

Email: pavlos@sagify.ai

## Why did we build this

We realized that there is not a single LLM to rule them all!
