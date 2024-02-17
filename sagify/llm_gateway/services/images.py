from sagify.llm_gateway.schemas.images import CreateImageDTO
from sagify.llm_gateway.providers.client_factory import LLMClientFactory


async def generations(image_input: CreateImageDTO):
    llm_client = await LLMClientFactory(image_input.provider).create_client()

    return await llm_client.generations(image_input)
