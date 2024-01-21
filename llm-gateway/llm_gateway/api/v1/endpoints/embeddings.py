from fastapi import APIRouter
from fastapi.responses import JSONResponse

from llm_gateway.models.embeddings import CreateEmbeddingDTO, ResponseEmbeddingDTO
from llm_gateway.services import embeddings


router = APIRouter()


@router.post("/embeddings", tags=["embeddings"], response_model=ResponseEmbeddingDTO)
async def create(request: CreateEmbeddingDTO):
    parsed_message = CreateEmbeddingDTO(
        provider=request.provider,
        model=request.model,
        input=request.input
    )

    response = await embeddings.embeddings(parsed_message)

    response_dto = {
        "data": response["data"],
        "provider": request["provider"],
        "model": response["model"],
        "object": response["object"],
        "usage": response["usage"]
    }

    return JSONResponse(content=response_dto)

