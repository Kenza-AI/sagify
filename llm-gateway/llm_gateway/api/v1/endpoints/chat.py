from fastapi import APIRouter
from fastapi.responses import JSONResponse

from llm_gateway.models.chat import CreateCompletionDTO, RoleItem, MessageItem, ResponseCompletionDTO
from llm_gateway.services import chat


router = APIRouter()


@router.post("/completions", tags=["completions"], response_model=ResponseCompletionDTO)
async def create(request: CreateCompletionDTO):
    parsed_message = CreateCompletionDTO(
        provider=request.provider,
        model=request.model,
        messages=[
            MessageItem(
                role=RoleItem(message.role),
                content=message.content
            ) for message in request.messages
        ]
    )

    response = await chat.completions(parsed_message)

    response_dto = {
        "id": response["id"],
        "provider": request["provider"],
        "object": response["object"],
        "created": response["created"],
        "model": response["model"],
        "choices": response["choices"],
        "usage": response["usage"]
    }

    return JSONResponse(content=response_dto)

