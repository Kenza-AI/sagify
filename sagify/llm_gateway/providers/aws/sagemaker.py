from PIL import Image
import base64
import json
from io import BytesIO
import os
import time
import uuid

import boto3
import structlog

from sagify.llm_gateway.api.v1.exceptions import InternalServerError
from sagify.llm_gateway.schemas.chat import CreateCompletionDTO, ResponseCompletionDTO
from sagify.llm_gateway.schemas.embeddings import CreateEmbeddingDTO, ResponseEmbeddingDTO
from sagify.llm_gateway.schemas.images import CreateImageDTO, ResponseImageDTO, ResponseFormat
from sagify.llm_gateway.schemas.chat import ChoiceItem, MessageItem

logger = structlog.get_logger()


class SageMakerClient:
    def __init__(self):
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        aws_region_name = os.environ.get("AWS_REGION_NAME", "us-east-1")
        self._bucket_name = os.environ.get("S3_BUCKET_NAME")
        self._image_url_ttl = os.environ.get("IMAGE_URL_TTL_IN_SECONDS", 3600)
        self._chat_completions_model = os.environ.get("SM_CHAT_COMPLETIONS_MODEL")
        self._embeddings_model = os.environ.get("SM_EMBEDDINGS_MODEL")
        self._image_creation_model = os.environ.get("SM_IMAGE_CREATION_MODEL")
        self.boto_session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region_name
        )
        self.sagemaker_runtime_client = self.boto_session.client('sagemaker-runtime')
        self.s3_client = self.boto_session.client('s3')

    async def completions(self, message: CreateCompletionDTO):
        request = {
            "model": message.model if message.model else self._chat_completions_model,
            "messages": message.messages,
            "temperature": message.temperature,
            "max_tokens": message.max_tokens,
            "stream": False
        }
        try:
            return self._invoke_chat_completions_endpoint(**request)
        except Exception as e:
            logger.error(e)
            raise InternalServerError(str(e))

    async def embeddings(self, embedding_input: CreateEmbeddingDTO):
        request = {
            "model": embedding_input.model if embedding_input.model else self._embeddings_model,
            "input": embedding_input.input,
        }
        try:
            return self._invoke_embeddings_endpoint(**request)
        except Exception as e:
            logger.error(e)
            raise InternalServerError(str(e))

    async def generations(self, image_input: CreateImageDTO):
        request = {
            "model": image_input.model if image_input.model else self._image_creation_model,
            "prompt": image_input.prompt,
            "n": image_input.n,
            "width": image_input.width,
            "height": image_input.height,
            "seed": image_input.seed,
            "response_format": image_input.response_format
        }
        try:
            return self._invoke_image_creation_endpoint(**request)
        except Exception as e:
            logger.error(e)
            raise InternalServerError(str(e))

    def _invoke_image_creation_endpoint(
            self,
            model,
            prompt,
            n,
            width,
            height,
            seed,
            response_format
    ):
        """
        Invoke SageMaker endpoint for image creations

        :param model: [str], name of the endpoint
        :param prompt: [Union[List[str], str]], prompt text
        :param n: [int], number of images to generate
        :param width: [int], width of the image
        :param height: [int], height of the image
        :param seed: [Optional[int]], seed for random number generation
        :param response_format: [ResponseFormat], response format

        :return: [ResponseImageDTO], response from the endpoint
        """
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_images_per_prompt": n,
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "seed": seed,
        }
        response = self.sagemaker_runtime_client.invoke_endpoint(
            EndpointName=model,
            Body=json.dumps(payload),
            ContentType="application/json",
            CustomAttributes='accept_eula=true',
            Accept="application/json;jpeg"
        )
        response_dict = json.loads(response['Body'].read().decode('utf-8'))

        return ResponseImageDTO(
            provider='sagemaker',
            model=model,
            created=int(time.time()),
            data=[
                self._prepare_image_item_response(
                    response_format, _base64_string
                ) for _base64_string in response_dict['generated_images']
            ]
        )

    def _prepare_image_item_response(self, response_format, base64_string):
        if response_format == ResponseFormat.URL:
            return {
                'url': self._generated_image_url(base64_string),
            }
        else:
            return {
                'b64_json': base64_string
            }

    def _generated_image_url(self, base64_string):
        # Decode the base64 string
        img_data = base64.b64decode(base64_string)

        # Create a PIL Image object
        img = Image.open(BytesIO(img_data))

        # Save the image to a BytesIO object
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Upload the image to S3
        key = '{}.png'.format(str(uuid.uuid4()))
        self.s3_client.upload_fileobj(buffer, self._bucket_name, key)

        # Get the URL of the uploaded image
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self._bucket_name,
                'Key': key
            },
            ExpiresIn=self._image_url_ttl
        )

    def _invoke_embeddings_endpoint(self, model, input):
        """
        Invoke SageMaker endpoint for embeddings

        :param model: [str], name of the endpoint
        :param input: [List[str]], input text list

        :return: [ResponseEmbeddingDTO], response from the endpoint
        """
        response = self.sagemaker_runtime_client.invoke_endpoint(
            EndpointName=model,
            Body=json.dumps(input),
            ContentType="application/x-text",
            CustomAttributes='accept_eula=true'
        )
        response_dict = json.loads(response['Body'].read().decode('utf-8'))

        return ResponseEmbeddingDTO(
            object='list',
            provider='sagemaker',
            model=model,
            data=[
                {
                    'object': 'embedding',
                    'embedding': _embedding,
                    'index': _index
                } for _index, _embedding in enumerate(response_dict['embedding'])
            ]
        )

    def _invoke_chat_completions_endpoint(
            self,
            model,
            messages,
            temperature=None,
            max_tokens=None,
            top_p=None,
            stream=False
    ):
        """
        Invoke SageMaker endpoint for chat completions

        :param model: [str], name of the endpoint
        :param messages: [list[MessageItem]], list of messages
        :param temperature: [float, default=None], Controls the randomness in the output. Higher temperature results
        in output sequence with low-probability words and lower temperature results
        in output sequence with high-probability words. If temperature -> 0, it results in greedy decoding.
        If specified, it must be a positive float.
        :param max_tokens: [int, default=None], Model generates text until the output length
        (excluding the input context length) reaches max_new_tokens. If specified,
        it must be a positive integer.
        :param top_p: [float, default=None], In each step of text generation, sample from the smallest possible
        set of words with cumulative probability top_p. If specified, it must be a float between 0 and 1.
        :param stream: [bool, default=False], Whether to stream the response or not

        :return: [ResponseCompletionDTO], response from the endpoint
        """
        parameters = {}
        if temperature:
            parameters["temperature"] = temperature

        if max_tokens:
            parameters["max_new_tokens"] = max_tokens

        if top_p:
            parameters["top_p"] = top_p

        payload = {
            "inputs": [
                [
                    {
                        'role': _message_item.role.value,
                        'content': _message_item.content
                    } for _message_item in messages
                ]
            ],
        }

        if parameters:
            payload['parameters'] = parameters

        response = self.sagemaker_runtime_client.invoke_endpoint(
            EndpointName=model,
            Body=json.dumps(payload),
            ContentType="application/json",
            CustomAttributes='accept_eula=true'
        )

        response_dict = json.loads(response['Body'].read().decode('utf-8'))

        return ResponseCompletionDTO(
            id='chatcmpl-{}'.format(str(uuid.uuid4())),
            object='chat.completion',
            created=int(time.time()),
            model=model,
            choices=[
                ChoiceItem(
                    index=_index,
                    message=MessageItem(
                        role=_choice['generation']['role'],
                        content=_choice['generation']['content'],
                    )
                ) for _index, _choice in enumerate(response_dict)
            ],
            provider='sagemaker'
        )
