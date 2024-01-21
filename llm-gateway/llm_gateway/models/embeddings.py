from typing import List
from pydantic import BaseModel

from llm_gateway.models import Usage


class CreateEmbeddingDTO(BaseModel):
    provider: str
    model: str
    input: str


class EmbeddingItem(BaseModel):
    embedding: List[float]
    index: int
    object: str


class DataItem(BaseModel):
    data: List[EmbeddingItem]
    model: str
    object: str
    usage: Usage


class ResponseEmbeddingDTO(BaseModel):
    data: List[DataItem]
    provider: str
    model: str
    object: str
    usage: Usage
