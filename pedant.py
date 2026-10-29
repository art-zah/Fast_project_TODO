from pydantic import BaseModel, Field

class Tasks(BaseModel):
    task_header: str = Field(min_length=1, max_length=100)
    task_description: str = Field(max_length=255)
    status: str = Field(max_length=255)