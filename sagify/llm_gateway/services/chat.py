from sagify.llm_gateway.schemas.chat import CreateCompletionDTO
from sagify.llm_gateway.providers.client_factory import LLMClientFactory


async def completions(message: CreateCompletionDTO):
    llm_client = await LLMClientFactory(message.provider).create_client()

    return await llm_client.completions(message)
