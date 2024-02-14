from fastapi import APIRouter

from sagify.llm_gateway.services import images
from sagify.llm_gateway.schemas.images import CreateImageDTO, ResponseImageDTO


router = APIRouter()


@router.post("/generations", tags=["generations"], response_model=ResponseImageDTO)
async def create(request: CreateImageDTO):
    parsed_message = CreateImageDTO(
        provider=request.provider,
        model=request.model,
        prompt=request.prompt,
        n=request.n,
        width=request.width,
        height=request.height,
        seed=request.seed,
        response_format=request.response_format
    )

    response = await images.generations(parsed_message)

    return response
