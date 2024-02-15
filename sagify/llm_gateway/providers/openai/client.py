import structlog
from openai import OpenAI

from sagify.llm_gateway.api.v1.exceptions import InternalServerError
from sagify.llm_gateway.schemas.chat import CreateCompletionDTO, ResponseCompletionDTO
from sagify.llm_gateway.schemas.embeddings import CreateEmbeddingDTO, ResponseEmbeddingDTO
from sagify.llm_gateway.schemas.images import CreateImageDTO, ResponseImageDTO


logger = structlog.get_logger()


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()

    async def completions(self, message: CreateCompletionDTO):
        request = {
            "model": message.model,
            "messages": message.messages,
            "temperature": message.temperature,
            "max_tokens": message.max_tokens,
            "stream": False
        }
        try:
            response = self.client.chat.completions.create(**request)
            response_dict = response.model_dump()
            response_dict["provider"] = message.provider
            return ResponseCompletionDTO(**response_dict)
        except Exception as e:
            logger.error(e)
            raise InternalServerError()

    async def embeddings(self, embedding_input: CreateEmbeddingDTO):
        request = {
            "model": embedding_input.model,
            "input": embedding_input.input,
        }
        try:
            response = self.client.embeddings.create(**request)
            response_dict = response.model_dump()
            response_dict["provider"] = embedding_input.provider
            return ResponseEmbeddingDTO(**response_dict)
        except Exception as e:
            logger.error(e)
            raise InternalServerError()

    async def generations(self, image_input: CreateImageDTO):
        request = {
            "model": image_input.model,
            "prompt": image_input.prompt,
            "n": image_input.n,
            "size": '{}x{}'.format(image_input.width, image_input.height)
        }
        try:
            response = self.client.images.generate(**request)
            response_dict = response.model_dump()
            response_dict["provider"] = image_input.provider
            response_dict["model"] = image_input.model
            return ResponseImageDTO(**response_dict)
        except Exception as e:
            logger.error(e)
            raise InternalServerError()
