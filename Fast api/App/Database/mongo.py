from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
from pymongo import ASCENDING
import math

MONGO_URI = "mongodb://gxbot:GlxBot%40321@GxbotApp01:27017/?authSource=gxbot" 

client = AsyncIOMotorClient(MONGO_URI)
db = client["AutomatedValidator"]  

users_db = db["user"]
domains_db = db["domains"]
projects_db = db["projects"]
rules_db = db["ruleinput"]

def get_unique_id():
    return str(uuid.uuid4())

async def login_user(username: str, password: str) -> dict:
    if not username or not password:
        return {
            "status": "fail",
            "message": "Username and password are required",
            "data": {}
        }

    user = await users_db.find_one({"username": username})

    if not user or user.get("password") != password:
        return {
            "status": "fail",
            "message": "Invalid username or password",
            "data": {}
        }

    return {
        "status": "success",
        "message": "Login successful",
        "data": {"username": username, "password": password}
    }

async def get_all_domains() -> list:
    domains = []
    async for doc in domains_db.find():
        domains.append({
            'DomainId': doc.get('DomainId'),
            'Name': doc.get('Name')
        })
    return domains

async def add_project(Name: str, Description: str, Owner: str, CreatedBy: str) -> dict:
    project = {
        "ProjectId": get_unique_id(),
        "Name": Name,
        "Description": Description,
        "Status": "Active",
        "Owner": Owner,
        "CreatedBy": CreatedBy,
        "CreatedAt": datetime.utcnow()
    }
    result = await projects_db.insert_one(project)
    return {"message": "Project added successfully", "project_id": str(result.inserted_id)}

async def get_all_projects() -> list:
    projects = []
    async for doc in projects_db.find({"Status": "Active"}):
        projects.append({
            "id": str(doc.get("_id")),
            "projectName": doc.get("Name")
        })
    return projects

async def get_rules_by_project(projectId: str, page: int, search: str, page_size: int = 10) -> dict:
    query = {"ProjectId": projectId}
    if search:
        query["RuleName"] = {"$regex": search, "$options": "i"}

    total_docs = await rules_db.count_documents(query)
    total_pages = math.ceil(total_docs / page_size)
    current_page = page

    cursor = rules_db.find(query).sort("UploadedAt", ASCENDING).skip((current_page - 1) * page_size).limit(page_size)

    rules = []
    async for doc in cursor:
        rules.append({
            "ruleId": doc.get("RuleInputId"),
            "ruleName": doc.get("RuleName"),
            "domainName": doc.get("DomainId"),
            "headersFileName": doc.get("HeaderFile", {}).get("FileName"),
            "sampleDataFileName": doc.get("SampleDataFile", {}).get("FileName"),
            "metadata": [doc.get("MetaDataFile", {}).get("FileName")],
            "additionalInfo": doc.get("AdditionalInfo")
        })

    return {
        "success": True,
        "data": {
            "totalPages": total_pages,
            "currentPage": current_page,
            "rules": rules
        },
        "message": "Rules fetched successfully"
    }