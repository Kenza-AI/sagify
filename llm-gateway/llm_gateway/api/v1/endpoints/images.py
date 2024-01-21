from fastapi import APIRouter

from llm_gateway.services import images
from llm_gateway.schemas.images import CreateImageDTO, ResponseImageDTO


router = APIRouter()


@router.post("/generations", tags=["generations"], response_model=ResponseImageDTO)
async def create(request: CreateImageDTO):
    parsed_message = CreateImageDTO(
        provider=request.provider,
        model=request.model,
        prompt=request.prompt,
        n=request.n,
        size=request.size
    )

    response = await images.generations(parsed_message)

    return response
