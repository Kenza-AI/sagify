from typing import List, Optional
from pydantic import BaseModel

from sagify.llm_gateway.schemas import Usage


class CreateEmbeddingDTO(BaseModel):
    provider: str
    model: str
    input: List[str]


class EmbeddingItem(BaseModel):
    embedding: List[float]
    index: int
    object: str


class DataItem(BaseModel):
    object: str
    embedding: List[float]
    index: int


class ResponseEmbeddingDTO(BaseModel):
    data: List[DataItem]
    provider: str
    model: str
    object: str
    usage: Optional[Usage]
