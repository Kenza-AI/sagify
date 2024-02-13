import json
import os
import time
import uuid

import boto3
import structlog

from sagify.llm_gateway.api.v1.exceptions import InternalServerError
from sagify.llm_gateway.schemas.chat import CreateCompletionDTO, ResponseCompletionDTO
from sagify.llm_gateway.schemas.embeddings import CreateEmbeddingDTO
from sagify.llm_gateway.schemas.images import CreateImageDTO
from sagify.llm_gateway.schemas.chat import ChoiceItem, MessageItem

logger = structlog.get_logger()


class SageMakerClient:
    def __init__(self):
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        aws_region_name = os.environ.get("AWS_REGION_NAME")
        self.boto_session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region_name
        )
        self.sagemaker_runtime_client = self.boto_session.client('sagemaker-runtime')

    async def completions(self, message: CreateCompletionDTO):
        request = {
            "model": message.model,
            "messages": message.messages,
            "temperature": message.temperature,
            "max_tokens": message.max_tokens,
            "stream": False
        }
        try:
            return self._invoke_chat_completions_endpoint(**request)
        except Exception as e:
            logger.error(e)
            raise InternalServerError()

    async def embeddings(self, embedding_input: CreateEmbeddingDTO):
        pass

    async def generations(self, image_input: CreateImageDTO):
        pass

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
