from llm_gateway.schemas.embeddings import CreateEmbeddingDTO
from llm_gateway.providers.client_factory import LLMClientFactory


async def embeddings(embedding_input: CreateEmbeddingDTO):
    llm_client = await LLMClientFactory().create_client(embedding_input.provider)

    return await llm_client.embeddings(embedding_input)
