from pydantic import BaseModel, Field
from typing import Optional

from app.core.enums import RewriteMode


class RewriteRequest(BaseModel):
    text: str
    mode: RewriteMode = RewriteMode.REWRITE_STRONG
    custom_prompt: Optional[str] = Field(
        None,
        description="Кастомный промпт (только для mode=custom)",
    )


class RewriteResponse(BaseModel):
    original: str
    rewritten: str
    mode: RewriteMode
