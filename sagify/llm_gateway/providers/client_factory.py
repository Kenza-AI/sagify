from sagify.llm_gateway.providers.openai.client import OpenAIClient
from sagify.llm_gateway.providers.aws.sagemaker import SageMakerClient
from sagify.llm_gateway.providers.anthropic.client import AnthropicClient


class LLMClientFactory:
    def __init__(self, provider):
        self._providers = ["openai", "sagemaker", "anthropic"]
        if provider not in self._providers:
            raise ValueError(f"Invalid provider name {provider}")
        self.provider = provider

    async def create_client(self):
        if self.provider == "openai":
            return OpenAIClient()
        if self.provider == "sagemaker":
            return SageMakerClient()
        if self.provider == "anthropic":
            return AnthropicClient()
