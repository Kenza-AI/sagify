from sagify.llm_gateway.providers.openai.client import OpenAIClient
from sagify.llm_gateway.providers.aws.sagemaker import SageMakerClient


class LLMClientFactory:
    def __init__(self):
        self._clients = {
            "openai": OpenAIClient(),
            "sagemaker": SageMakerClient(),
        }

    async def create_client(self, provider):
        client = self._clients.get(provider)
        if not client:
            raise ValueError(f"Invalid provider name {provider}")
        return client
