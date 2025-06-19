from Database.mongo import db
from pymongo import ASCENDING
import math

rules_db = db["ruleinput"]

class RuleService:
    @staticmethod
    async def get_rules_by_project(data: dict, page_size: int = 10):
        query = {"ProjectId": data["projectId"]}

        if data.get("search"):
            query["RuleName"] = {"$regex": data["search"], "$options": "i"}

        total_docs = await rules_db.count_documents(query)  
        total_pages = math.ceil(total_docs / page_size)
        current_page = data["page"]

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
