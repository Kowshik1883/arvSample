import math
from typing import Optional
from fastapi import FastAPI, File, HTTPException, UploadFile, Form
from fastapi.responses import JSONResponse
import pandas as pd
from io import BytesIO
import docx
from PyPDF2 import PdfReader
import mimetypes
from pydantic import BaseModel
from Database.mongo import db
from Services.domainService import DomainService
from Models.project_model import ProjectCreate
from Services.projectService import ProjectService
from Models.GenericResponse import GenericResponse

app = FastAPI()

users_db = db["user"]

# Pydantic model for login request
class LoginRequest(BaseModel):
    username: str
    password: str


def read_file(file: UploadFile, excel_only: bool = False):
    content_type = file.content_type
    if excel_only:
        if content_type not in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/csv", 
        ]:
            raise ValueError("Unsupported file type. Please upload an Excel or CSV file.")
        if content_type.startswith("text"):
            return pd.read_csv(file.file)
        else:
            return pd.read_excel(file.file)
    else:
        if content_type in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/csv",
        ]:
            if content_type.startswith("text"):
                return pd.read_csv(file.file)
            else:
                return pd.read_excel(file.file)
        else:
            raise ValueError("Unsupported file type. Please upload an Excel or CSV file.")

def read_metadata_file(file: UploadFile):
    content_type = file.content_type
    filename = file.filename.lower()
    
    if content_type == "text/plain" or filename.endswith(".txt"):
        content = file.file.read().decode("utf-8")
        return content.replace("\r\n", " ").replace("\n", " ")
    
    elif content_type in [
        "application/pdf",
        "application/x-pdf",
    ] or filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        content = ""
        for page in reader.pages:
            content += page.extract_text() or ""
        return content.replace("\r\n", " ").replace("\n", " ")
    
    elif content_type in [
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ] or filename.endswith((".doc", ".docx")):
        doc = docx.Document(file.file)
        content = " ".join([para.text for para in doc.paragraphs])
        return content.replace("\r\n", " ").replace("\n", " ")
    
    else:
        raise ValueError(f"Unsupported metadata file type: {content_type}")

@app.post("/upload/")
async def upload_file(
    sample_data:UploadFile = File(None),
    rule_name: str = Form(...),
    domain: str = Form(...),
    file_headers: UploadFile = File(...),
    metadata_files: list[UploadFile] = [],
    additional_info: str = Form(None),
):
    try:
        # Process the main file (CSV/Excel) for headers
        if file_headers.content_type not in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/csv",
        ]:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid file type for main file. Please upload Excel or CSV."}
            )
        
        df = read_file(file_headers, excel_only=False)
        headers = df.columns.tolist()
        # Process the sample data file (Excel or CSV) if provided
        print("sample data", sample_data)
        sample_data_content = None
        if sample_data:
            if sample_data.content_type not in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel",
                "text/csv",
            ]:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid file type for sample data. Please upload an Excel or CSV file."}
                )
            
            sample_df = read_file(sample_data, excel_only=True)
            print("sample_df", sample_df)
            # Replace NaN values with None
            sample_df = sample_df.applymap(lambda x: None if pd.isna(x) else x)
            sample_data_content = sample_df.to_dict(orient="records")
        print("metadata", metadata_files)
        # Process multiple metadata files
        metadata_contents = []
        for metadata_file in metadata_files:
            content = read_metadata_file(metadata_file)
            metadata_contents.append({
                "filename": metadata_file.filename,
                "content": content
            })
            print("metadata:",metadata_contents)
        print(type(sample_data_content))
        return {
            "rule_name": rule_name,
            "domain": domain,
            "headers": headers,
            "metadata": metadata_contents,
            "sample_data": sample_data_content,
            "additional_info": additional_info
        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing file: {str(e)}"}
        )




@app.post("/login/")
async def login(login_request: LoginRequest):
    user = await users_db.find_one({"username": login_request.username})

    if not user or user["password"] != login_request.password:
        response = GenericResponse(
            status="fail",
            message="Invalid username or password",
            data={}
        )
        return response.to_dict()

    response = GenericResponse(
        status="success",
        message="Login successful",
        data={"username": login_request.username,"password": login_request.password}
    )
    return response.to_dict()


@app.get("/domains/")
async def get_all_domains():
    try:
        domains = await DomainService.get_all_domains()
        response = GenericResponse(status="success", message="Domains fetched successfully", data={"domains": domains})
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/")
async def add_project(project: ProjectCreate):
    try:
        result = await ProjectService.add_project(project.dict())
        response = GenericResponse(
            status="success",
            message="Project added successfully",
            data={"project_id": result["project_id"]}
        )
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/getAllProjects")
async def get_all_projects():
    try:
        projects = await ProjectService.get_all_projects()
        response = GenericResponse(
            status="success",
            message="Projects fetched successfully",
            data=projects
        )
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))