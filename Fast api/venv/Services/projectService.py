from Database.mongo import db
from datetime import datetime

project_db = db["projects"]

class ProjectService:
    @staticmethod
    async def add_project(data: dict):
        project = {
            "ProjectId": data.get("ProjectId"),
            "Name": data.get("Name"),
            "DomainId": data.get("DomainId"),
            "Description": data.get("Description"),
            "Status": "Active",
            "Owner": data.get("Owner"),
            "CreatedBy": data.get("CreatedBy"),
            "CreatedAt": datetime.utcnow()
        }

        result = await project_db.insert_one(project)
        return {"message": "Project added successfully", "project_id": str(result.inserted_id)}
