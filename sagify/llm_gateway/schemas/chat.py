from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

from sagify.llm_gateway.schemas import Usage


class RoleItem(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageItem(BaseModel):
    role: RoleItem
    content: str


class CreateCompletionDTO(BaseModel):
    provider: str
    model: Optional[str]
    messages: List[MessageItem]
    temperature: Optional[float] = 1.0
    max_tokens: int
    top_p: Optional[float]
    seed: Optional[int]


class ChoiceItem(BaseModel):
    index: int
    message: MessageItem
    finish_reason: Optional[str]


class ResponseCompletionDTO(BaseModel):
    id: str
    object: str
    created: int
    provider: str
    model: str
    choices: List[ChoiceItem]
    usage: Optional[Usage]

    class Config:
        populate_by_name = True
