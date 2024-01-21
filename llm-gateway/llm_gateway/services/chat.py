from llm_gateway.models.chat import CreateCompletionDTO
from llm_gateway.providers.client_factory import LLMClientFactory


async def completions(message: CreateCompletionDTO):
    llm_client = await LLMClientFactory().create_client(message.provider)

    return await llm_client.completions(message)
