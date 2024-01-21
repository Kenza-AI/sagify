import openai
import structlog
from openai import OpenAI
from fastapi import HTTPException

from llm_gateway.models.chat import CreateCompletionDTO, ResponseCompletionDTO
from llm_gateway.models.embeddings import CreateEmbeddingDTO, ResponseEmbeddingDTO
from llm_gateway.models.images import CreateImageDTO, ResponseImageDTO


logger = structlog.get_logger()


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()

    async def completions(self, message: CreateCompletionDTO):
        request = {
            "model": message.model,
            "messages": message.messages,
            "max_tokens": 10
        }
        try:
            response = self.client.chat.completions.create(**request)
            return ResponseCompletionDTO(**response.to_dict())
        except openai.OpenAIError as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=str(e))

    async def embeddings(self, embedding_input: CreateEmbeddingDTO):
        request = {
            "model": embedding_input.model,
            "input": embedding_input.input,
        }
        try:
            response = self.client.embeddings.create(**request)
            return ResponseEmbeddingDTO(**response.to_dict())
        except openai.OpenAIError as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=str(e))

    async def generations(self, image_input: CreateImageDTO):
        request = {
            "model": image_input.model,
            "prompt": image_input.prompt,
            "n": image_input.n,
            "size": image_input.size
        }
        try:
            response = self.client.images.generate(**request)
            return ResponseImageDTO(**response.to_dict())
        except openai.OpenAIError as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=str(e))


