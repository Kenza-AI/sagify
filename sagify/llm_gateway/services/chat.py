from sagify.llm_gateway.schemas.chat import CreateCompletionDTO
from sagify.llm_gateway.providers.client_factory import LLMClientFactory


async def completions(message: CreateCompletionDTO):
    llm_client = await LLMClientFactory().create_client(message.provider)

    return await llm_client.completions(message)
