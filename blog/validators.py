from pydantic import BaseModel, Field


class PydanticPost(BaseModel):
    title: str = Field(..., max_length=100, title="Title")
    content: str = Field(..., title="Content")
