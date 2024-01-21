from typing import List
from pydantic import BaseModel


class CreateImageDTO(BaseModel):
    provider: str
    model: str
    prompt: str
    n: int
    size: str


class DataItem(BaseModel):
    url: str


class ResponseImageDTO(BaseModel):
    provider: str
    model: str
    created: int
    data: List[DataItem]
