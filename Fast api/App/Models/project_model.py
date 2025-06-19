from pydantic import BaseModel

class ProjectCreate(BaseModel):
    Name: str
    Description: str
    Owner: str
    CreatedBy: str
