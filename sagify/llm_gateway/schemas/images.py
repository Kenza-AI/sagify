from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class ResponseFormat(str, Enum):
    URL = "url"
    B64_JSON = "b64_json"


class CreateImageDTO(BaseModel):
    provider: str
    model: Optional[str]
    prompt: str
    n: int
    width: int
    height: int
    seed: Optional[int]
    response_format: Optional[ResponseFormat] = 'url'


class DataItem(BaseModel):
    url: Optional[str]
    b64_json: Optional[str]

    def dict(self, *args, **kwargs):
        _ = kwargs.pop("exclude_none")
        return super().dict(*args, exclude_none=True, **kwargs)


class ResponseImageDTO(BaseModel):
    provider: str
    model: str
    created: int
    data: List[DataItem]
