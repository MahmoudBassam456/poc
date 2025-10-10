from motor.motor_asyncio import AsyncIOMotorClient
from ..db_model.db_model_base import db_model_base

from ..db_schames.project import project 

class ProjectDB(db_model_base):
    def __init__(self, db_client: AsyncIOMotorClient):
        super().__init__(db_client=db_client)
        self.collection = self.db_client["projects"]

    async def create_project(self, project_id: str,file_name:str="",file_path:str="",file_extension:str=""):
        project_data=project(project_id=project_id,file_name=file_name,file_path=file_path,file_extension=file_extension)
        result = await self.collection.insert_one(project_data.dict())
        project_data._id = result.inserted_id  # already ObjectId
        return project_data

    async def get_project_or_create_newone(self, project_id: str,file_name:str="",file_path:str="",file_extension:str=""):
        existing = await self.collection.find_one({"project_id": project_id})
        if existing:
            return project(**existing)
        
        created_project = await self.create_project(project_id=project_id,file_name=file_name,file_path=file_path,file_extension=file_extension)
        return created_project
    async def get_all_projects(self,page: int = 1, page_size: int = 10):
        projects = []
        
        total_docs= await self.collection.count_documents({})#count total documents
        total_pages = (total_docs ) // page_size  #calculate total pages
        if total_docs % page_size > 0:
            total_pages += 1

        cursor = self.collection.find({}).strip((page-1)*page_size).limit(page_size)#get documents with pagination
        
        async for document in cursor:
            projects.append(project(**document))
        return projects
