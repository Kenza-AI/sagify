from fastapi import APIRouter
from fastapi.responses import JSONResponse

from llm_gateway.services import images
from llm_gateway.models.images import CreateImageDTO, ResponseImageDTO


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

    response_dto = {
        "provider": request["provider"],
        "created": response["created"],
        "data": response["data"]
    }

    return JSONResponse(content=response_dto)

