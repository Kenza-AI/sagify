import structlog
import anthropic
import os
import time

from sagify.llm_gateway.api.v1.exceptions import InternalServerError
from sagify.llm_gateway.schemas.chat import CreateCompletionDTO, ResponseCompletionDTO
from sagify.llm_gateway.schemas.embeddings import CreateEmbeddingDTO
from sagify.llm_gateway.schemas.images import CreateImageDTO


logger = structlog.get_logger()


class AnthropicClient:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self._chat_completions_model = os.environ.get("ANTHROPIC_CHAT_COMPLETIONS_MODEL")

    async def completions(self, message: CreateCompletionDTO):
        request = {
            "model": message.model if message.model else self._chat_completions_model,
            "messages": message.messages,
            "temperature": message.temperature,
            "max_tokens": message.max_tokens,
            "top_p": message.top_p,
            "stream": False
        }
        try:
            response = self.client.messages.create(**request)
            response_dict = response.model_dump()
            response_dict["provider"] = message.provider
            response_dict["created"] = int(time.time())
            response_dict["usage"] = {
                 "prompt_tokens": response_dict["usage"]["input_tokens"],
                 "total_tokens": response_dict["usage"]["input_tokens"] + response_dict["usage"]["output_tokens"]
            }
            response_dict["object"] = response_dict["type"]
            response_dict["choices"] = []
            for i, message in enumerate(response_dict["content"]):
                response_dict["choices"].append(
                    {
                        "index": i,
                        "message": {
                            "role": response_dict["role"],
                            "content": message["text"]
                        },
                        "finish_reason": response_dict["stop_reason"]
                    }
                )
            return ResponseCompletionDTO(**response_dict)
        except Exception as e:
            logger.error(e)
            raise InternalServerError(str(e))

    async def embeddings(self, embedding_input: CreateEmbeddingDTO):
        raise InternalServerError("Not supported")

    async def generations(self, image_input: CreateImageDTO):
        raise InternalServerError("Not supported")
