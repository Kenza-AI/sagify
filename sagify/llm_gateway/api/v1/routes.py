from fastapi import APIRouter

from sagify.llm_gateway.api.v1.endpoints import chat, embeddings, images


api_router = APIRouter(prefix="/v1")
api_router.include_router(chat.router, prefix="/chat")
api_router.include_router(embeddings.router, prefix="")
api_router.include_router(images.router, prefix="/images")
