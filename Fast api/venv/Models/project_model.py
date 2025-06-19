from pydantic import BaseModel

class ProjectCreate(BaseModel):
    ProjectId: str
    Name: str
    DomainId: str
    Description: str
    Owner: str
    CreatedBy: str
