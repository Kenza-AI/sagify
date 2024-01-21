from pydantic import BaseModel


class Usage(BaseModel):
    prompt_tokens: int
    total_tokens: int
