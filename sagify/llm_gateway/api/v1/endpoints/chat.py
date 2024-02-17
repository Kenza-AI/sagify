from fastapi import APIRouter

from sagify.llm_gateway.schemas.chat import CreateCompletionDTO, RoleItem, MessageItem, ResponseCompletionDTO
from sagify.llm_gateway.services import chat


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
        ],
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        top_p=request.top_p,
        seed=request.seed
    )

    response = await chat.completions(parsed_message)

    return response
