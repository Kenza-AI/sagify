from llm_gateway.providers.openai.client import OpenAIClient


class LLMClientFactory:
    def __init__(self):
        self._clients = {"openai": OpenAIClient()}

    async def create_client(self, provider):
        client = self._clients.get(provider)
        if not client:
            raise ValueError(f"Invalid provider name {provider}")
        return client
