from Database.mongo import db
from datetime import datetime
import uuid
from fastapi import Form

project_db = db["projects"]

def get_unique_id():
    return str(uuid.uuid4())

class ProjectService:
    @staticmethod
    async def add_project(
        Name: str = Form(...),
        Description: str = Form(...),
        Owner: str = Form(...),
        CreatedBy: str = Form(...)
    ):
        project = {
            "ProjectId": get_unique_id(),
            "Name": Name,
            "Description": Description,
            "Status": "Active",
            "Owner": Owner,
            "CreatedBy": CreatedBy,
            "CreatedAt": datetime.utcnow()
        }

        result = await project_db.insert_one(project)
        return {"message": "Project added successfully", "project_id": str(result.inserted_id)}

    @staticmethod
    async def get_all_projects():
        projects = []
        async for doc in project_db.find({"Status": "Active"}):
            projects.append({
                "id": str(doc.get("_id")),
                "projectName": doc.get("Name")
            })
        return projects