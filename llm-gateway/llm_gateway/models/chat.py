from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

from llm_gateway.models import Usage


class RoleItem(str, Enum):
    SYSTEM = "system"
    USER = "user"


class MessageItem(BaseModel):
    role: RoleItem
    content: str


class CreateCompletionDTO(BaseModel):
    provider: str
    model: str
    messages: List[MessageItem]


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
    usage: Usage

    class Config:
        populate_by_name = True
