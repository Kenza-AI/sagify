from sagify.llm_gateway.schemas.embeddings import CreateEmbeddingDTO
from sagify.llm_gateway.providers.client_factory import LLMClientFactory


async def embeddings(embedding_input: CreateEmbeddingDTO):
    llm_client = await LLMClientFactory(embedding_input.provider).create_client()

    return await llm_client.embeddings(embedding_input)
