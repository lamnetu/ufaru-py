from pydantic import BaseModel

class RewriteRequest(BaseModel):
    text: str

class RewriteResponse(BaseModel):
    original: str
    rewritten: str