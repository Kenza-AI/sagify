from fastapi import APIRouter

from sagify.llm_gateway.schemas.embeddings import CreateEmbeddingDTO, ResponseEmbeddingDTO
from sagify.llm_gateway.services import embeddings


router = APIRouter()


@router.post("/embeddings", tags=["embeddings"], response_model=ResponseEmbeddingDTO)
async def create(request: CreateEmbeddingDTO):
    parsed_message = CreateEmbeddingDTO(
        provider=request.provider,
        model=request.model,
        input=request.input
    )

    response = await embeddings.embeddings(parsed_message)

    return response
