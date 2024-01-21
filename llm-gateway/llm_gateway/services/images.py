from llm_gateway.schemas.images import CreateImageDTO
from llm_gateway.providers.client_factory import LLMClientFactory


async def generations(image_input: CreateImageDTO):
    llm_client = await LLMClientFactory().create_client(image_input.provider)

    return await llm_client.generations(image_input)
